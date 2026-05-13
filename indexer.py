"""Indexer skeleton: embeddings + FAISS build/save/load (placeholders)."""
from typing import List, Tuple
import numpy as np

try:
    import faiss
except Exception:
    faiss = None

from sentence_transformers import SentenceTransformer


class FaissIndexer:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", dim: int = 384):
        self.model = SentenceTransformer(model_name)
        self.dim = dim
        self.index = None

    def embed_texts(self, texts: List[str], batch_size: int = 64) -> np.ndarray:
        return self.model.encode(texts, batch_size=batch_size, show_progress_bar=False, convert_to_numpy=True)

    def build_index(self, embeddings: np.ndarray, use_hnsw: bool = True) -> None:
        if faiss is None:
            raise ImportError("faiss is required for indexing")
        d = embeddings.shape[1]
        if use_hnsw:
            index = faiss.IndexHNSWFlat(d, 32)
            index.hnsw.efConstruction = 200
        else:
            index = faiss.IndexFlatIP(d)
        index.add(embeddings)
        self.index = index

    def save_index(self, path: str) -> None:
        if faiss is None:
            raise ImportError("faiss is required for saving/loading index")
        if self.index is None:
            raise RuntimeError("No index to save")
        faiss.write_index(self.index, path)

    def load_index(self, path: str) -> None:
        if faiss is None:
            raise ImportError("faiss is required for saving/loading index")
        self.index = faiss.read_index(path)

    def search(self, query_embeddings: np.ndarray, k: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        if self.index is None:
            raise RuntimeError("Index not built")
        D, I = self.index.search(query_embeddings, k)
        return D, I
