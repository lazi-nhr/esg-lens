"""Hybrid BM25 + pgvector retrieval for PostgreSQL."""
from typing import List, Dict
from rank_bm25 import BM25Okapi
from app.db.repositories.documents_repo import DocumentRepository
from app.retrieval.embedder import create_embedding


class HybridRetriever:
    def __init__(self):
        self.bm25 = None
        self.all_docs = []
    
    def build_index(self):
        """Load all documents from PostgreSQL and build BM25."""
        self.all_docs = DocumentRepository.list_all()
        texts = [doc['content'] for doc in self.all_docs]
        tokenized = [t.split() for t in texts]
        self.bm25 = BM25Okapi(tokenized)
    
    def refresh_index(self):
        """Rebuild BM25 index (call after adding new documents)."""
        self.bm25 = None
        self.all_docs = []
        self.build_index()
    
    def bm25_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """BM25 keyword search."""
        if not self.bm25:
            self.build_index()
        
        scores = self.bm25.get_scores(query.split())
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
        # Return docs with scores
        return [(self.all_docs[idx], float(score)) for idx, score in ranked]
    
    def pgvector_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """pgvector semantic search."""
        embedding = create_embedding(query)
        return DocumentRepository.search_by_similarity(embedding, top_k)
    
    def hybrid_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Combine BM25 + pgvector results with proper score merging.
        
        Returns top_k documents ranked by combined semantic + keyword relevance.
        """
        # Get results from both methods (request more for merging)
        bm25_results = self.bm25_search(query, top_k * 2)
        pgvector_results = self.pgvector_search(query, top_k * 2)
        
        # Normalize BM25 scores to 0-1 range
        max_bm25 = max([score for _, score in bm25_results], default=1.0)
        bm25_normalized = {
            doc['id']: score / max_bm25 if max_bm25 > 0 else 0
            for doc, score in bm25_results
        }
        
        # pgvector already returns similarity scores (0-1)
        pgvector_scores = {
            doc['id']: doc.get('similarity', 0)
            for doc in pgvector_results
        }
        
        # Merge with combined scoring (average of both if present)
        merged = {}
        
        # Add pgvector results
        for doc in pgvector_results:
            doc_id = doc['id']
            pgvector_score = pgvector_scores[doc_id]
            bm25_score = bm25_normalized.get(doc_id, 0)
            
            # Average scores if both present, otherwise use individual score
            combined_score = (pgvector_score + bm25_score) / 2 if bm25_score > 0 else pgvector_score
            merged[doc_id] = {'doc': doc, 'score': combined_score}
        
        # Add BM25-only results
        for doc, bm25_score in bm25_results:
            doc_id = doc['id']
            if doc_id not in merged:
                merged[doc_id] = {'doc': doc, 'score': bm25_normalized[doc_id]}
        
        # Sort by combined score and return top_k
        sorted_results = sorted(merged.items(), key=lambda x: x[1]['score'], reverse=True)
        return [item[1]['doc'] for item in sorted_results[:top_k]]