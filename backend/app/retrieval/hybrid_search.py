"""
Hybrid search compatibility module.

This module provides backward compatibility by re-exporting the refactored
HybridRetriever class. New code should import from app.retrieval.searchers.

Migration guide:
  Old: from app.retrieval.hybrid_search import HybridRetriever
  New: from app.retrieval.searchers import HybridSearcher, VectorSearcher, BM25Searcher
"""

# Backward compatibility: re-export refactored classes
from app.retrieval.searchers import HybridSearcher

# Alias for backward compatibility
HybridRetriever = HybridSearcher

__all__ = ["HybridRetriever", "HybridSearcher"]
