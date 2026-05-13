#!/usr/bin/env python3
"""
Examples: Using the refactored searcher classes.

Demonstrates different ways to use the modular search components.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.retrieval.searchers import (
    VectorSearcher,
    BM25Searcher,
    HybridSearcher,
)
from app.db.connection import init_db


def example_vector_search():
    """Example: Use only vector search."""
    print("=" * 80)
    print("📌 Example 1: Vector Search Only")
    print("=" * 80)
    print()
    
    searcher = VectorSearcher()
    query = "renewable energy climate"
    results = searcher.search(query, top_k=3)
    
    print(f"Query: '{query}'")
    print(f"Results: {len(results)} documents\n")
    
    for i, doc in enumerate(results, 1):
        similarity = doc.get('similarity', 'N/A')
        content = doc.get('content', '')[:60].replace('\n', ' ') + "..."
        print(f"{i}. Similarity: {similarity:.4f}")
        print(f"   {content}\n")


def example_keyword_search():
    """Example: Use only BM25 keyword search."""
    print("=" * 80)
    print("📌 Example 2: Keyword Search Only (BM25)")
    print("=" * 80)
    print()
    
    searcher = BM25Searcher()
    query = "renewable energy climate"
    results = searcher.search(query, top_k=3)
    
    print(f"Query: '{query}'")
    print(f"Results: {len(results)} documents\n")
    
    for i, doc in enumerate(results, 1):
        score = doc.get('bm25_score', 'N/A')
        content = doc.get('content', '')[:60].replace('\n', ' ') + "..."
        print(f"{i}. BM25 Score: {score:.4f}")
        print(f"   {content}\n")


def example_hybrid_search():
    """Example: Use hybrid search (default with reranking)."""
    print("=" * 80)
    print("📌 Example 3: Hybrid Search with Reranking")
    print("=" * 80)
    print()
    
    searcher = HybridSearcher(enable_reranking=True)
    query = "renewable energy climate"
    results = searcher.search(query, top_k=3)
    
    print(f"Query: '{query}'")
    print(f"Results: {len(results)} documents\n")
    
    for i, doc in enumerate(results, 1):
        rerank_score = doc.get('rerank_score', 'N/A')
        content = doc.get('content', '')[:60].replace('\n', ' ') + "..."
        print(f"{i}. Rerank Score: {rerank_score:.4f}")
        print(f"   {content}\n")


def example_detailed_scores():
    """Example: Get detailed scoring information."""
    print("=" * 80)
    print("📌 Example 4: Hybrid Search with Detailed Scores")
    print("=" * 80)
    print()
    
    searcher = HybridSearcher(enable_reranking=True)
    query = "renewable energy climate"
    results = searcher.search_with_details(query, top_k=3)
    
    print(f"Query: '{query}'")
    print(f"Results: {len(results)} documents\n")
    
    for i, doc in enumerate(results, 1):
        doc_id = doc.get('id', 'N/A')
        bm25 = doc.get('bm25_score', 0)
        vector = doc.get('vector_score', 0)
        hybrid = doc.get('hybrid_score', 0)
        rerank = doc.get('rerank_score', 0)
        
        print(f"{i}. Document {doc_id}")
        print(f"   BM25 Score:    {bm25:.4f}")
        print(f"   Vector Score:  {vector:.4f}")
        print(f"   Hybrid Score:  {hybrid:.4f}")
        print(f"   Rerank Score:  {rerank:.4f}")
        print()


def example_custom_configuration():
    """Example: Create searchers with custom configuration."""
    print("=" * 80)
    print("📌 Example 5: Custom Configuration")
    print("=" * 80)
    print()
    
    # Custom searchers
    vector = VectorSearcher()
    bm25 = BM25Searcher()
    
    # Compose into hybrid with custom model
    searcher = HybridSearcher(
        vector_searcher=vector,
        bm25_searcher=bm25,
        enable_reranking=True,
        reranker_model="cross-encoder/ms-marco-MiniLM-L-6-v2"  # Faster model
    )
    
    print("Created hybrid searcher with:")
    print("  - Custom VectorSearcher")
    print("  - Custom BM25Searcher")
    print("  - Reranking enabled")
    print("  - Fast reranker model (MiniLM-L-6-v2)\n")
    
    query = "renewable energy"
    results = searcher.search(query, top_k=5)
    print(f"Search for '{query}': {len(results)} results found")


def example_toggle_reranking():
    """Example: Toggle reranking on/off."""
    print("=" * 80)
    print("📌 Example 6: Toggle Reranking")
    print("=" * 80)
    print()
    
    searcher = HybridSearcher(enable_reranking=True)
    query = "renewable energy"
    
    print("With reranking enabled:")
    results = searcher.search(query, top_k=3)
    print(f"  Found {len(results)} results")
    print(f"  Top result has rerank_score: {results[0].get('rerank_score', 'N/A')}\n")
    
    print("Disabling reranking...")
    searcher.set_reranking(False)
    
    print("With reranking disabled:")
    results = searcher.search(query, top_k=3)
    print(f"  Found {len(results)} results")
    print(f"  Top result has hybrid_score: {results[0].get('hybrid_score', 'N/A')}")


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║  REFACTORED SEARCH ARCHITECTURE - EXAMPLES".ljust(79) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    # Initialize database
    init_db()
    print("✅ Database initialized\n")
    
    try:
        example_vector_search()
        print()
        example_keyword_search()
        print()
        example_hybrid_search()
        print()
        example_detailed_scores()
        print()
        example_custom_configuration()
        print()
        example_toggle_reranking()
        print()
        
        print("=" * 80)
        print("✅ All examples completed successfully!")
        print("=" * 80)
        print()
        print("📖 For more information, see:")
        print("   - app/retrieval/REFACTORING.md")
        print("   - app/retrieval/searchers/base.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
