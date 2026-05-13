"""Retriever skeleton for BM25 + FAISS hybrid retrieval."""
from typing import List, Dict, Optional

from rank_bm25 import BM25Okapi
import numpy as np
from typing import Callable


class Retriever:
    def __init__(self, faiss_indexer=None, tokenizer: Callable[[str], List[str]] = lambda x: x.split()):
        self.faiss = faiss_indexer
        self.bm25 = None
        self.corpus_texts: List[str] = []
        self.chunk_ids: List[str] = []
        self.tokenizer: Callable[[str], List[str]] = tokenizer

    def build_bm25(self, texts: List[str], chunk_ids: List[str]):
        tokenized = [self.tokenizer(t) for t in texts]
        self.bm25 = BM25Okapi(tokenized)
        self.corpus_texts = texts
        self.chunk_ids = chunk_ids

    def bm25_query(self, query: str, top_n: int = 100):
        if self.bm25 is None:
            raise RuntimeError("BM25 not built")
        qtok = self.tokenizer(query)
        scores = self.bm25.get_scores(qtok)
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_n]
        # return list of (chunk_id, score)
        return [(self.chunk_ids[idx], float(score)) for idx, score in ranked]

    def hybrid_query(self, query: str, k: int = 10, bm25_top_n: int = 200):
        """Hybrid: merge BM25 and FAISS scores and return top-k chunk ids with provenance.

        If a FAISS index is available and `faiss_mapping` is provided (faiss_id -> chunk_id),
        this will search both and merge results giving precedence to FAISS semantic scores.

        Returns list of dicts: {chunk_id, score, source}
        """
        if self.bm25 is None:
            raise RuntimeError("BM25 not built")

        bm25_res = self.bm25_query(query, top_n=bm25_top_n)

        # If no faiss available, return bm25 top-k with source tag
        if self.faiss is None or self.faiss.index is None or not hasattr(self, "chunk_ids"):
            return [{"chunk_id": cid, "score": score, "source": "bm25"} for cid, score in bm25_res[:k]]

        # Embed query
        q_emb = self.faiss.model.encode([query], convert_to_numpy=True)

        # FAISS search across entire index
        D_all, I_all = self.faiss.search(q_emb, k=bm25_top_n)
        faiss_results = []
        for dist_row, idx_row in zip(D_all.tolist(), I_all.tolist()):
            for dist, idx in zip(dist_row, idx_row):
                faiss_results.append((int(idx), float(dist)))

        # Caller should provide mapping from faiss_id -> chunk_id via attribute if available
        faiss_mapping = getattr(self, "faiss_mapping", None)
        # Build dictionaries for quick lookup
        bm25_dict = {cid: score for cid, score in bm25_res}
        merged = {}

        # Add FAISS results (semantic)
        if faiss_mapping:
            for fid, score in faiss_results:
                cid = faiss_mapping.get(fid)
                if not cid:
                    continue
                merged[cid] = {"score": float(score), "source": "faiss"}

        # Add BM25 results if missing
        for cid, score in bm25_res:
            if cid in merged:
                # if both, keep faiss score but note both
                merged[cid]["source"] = "both"
            else:
                merged[cid] = {"score": float(score), "source": "bm25"}

        # Sort merged by score descending
        sorted_items = sorted(merged.items(), key=lambda x: x[1]["score"], reverse=True)
        results = []
        for cid, info in sorted_items[:k]:
            results.append({"chunk_id": cid, "score": info["score"], "source": info["source"]})

        return results
