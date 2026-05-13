"""Retrieval module for document search and ranking."""

# Searchers
from app.retrieval.searchers import (
    BaseSearcher,
    VectorSearcher,
    BM25Searcher,
    HybridSearcher,
)

# Reranker
from app.retrieval.reranker import DocumentReranker, get_reranker

# Backward compatibility
from app.retrieval.hybrid_search import HybridRetriever

__all__ = [
    # Base
    "BaseSearcher",
    # Individual searchers
    "VectorSearcher",
    "BM25Searcher",
    # Hybrid
    "HybridSearcher",
    "HybridRetriever",  # Backward compatibility alias
    # Reranking
    "DocumentReranker",
    "get_reranker",
]
