#!/usr/bin/env python3
"""
Demo: Reranker comparison for hybrid search.

Shows the difference between:
1. Hybrid search without reranking (BM25 + pgvector average)
2. Hybrid search with reranking (cross-encoder final scoring)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.retrieval.hybrid_search import HybridRetriever
from app.db.connection import init_db


def print_result(doc: dict, rank: int):
    """Pretty print a single result."""
    doc_id = doc.get('id', 'N/A')
    score = doc.get('rerank_score', doc.get('hybrid_score', 'N/A'))
    content = doc.get('content', '')[:80].replace('\n', ' ') + "..."
    
    print(f"{rank}. [ID: {doc_id}] (Score: {score:.4f})")
    print(f"   {content}")


def demo_reranker():
    """Run demo comparison."""
    print("=" * 80)
    print("🔄 RERANKER DEMO: Hybrid Search Comparison")
    print("=" * 80)
    print()
    
    query = "ABB climate change initiatives"
    
    # Initialize database
    init_db()
    print(f"✅ Database initialized\n")
    
    # Create retriever WITH reranking
    print("Creating hybrid retriever WITH reranking...")
    retriever_with_rerank = HybridRetriever(enable_reranking=True)
    results_with_rerank = retriever_with_rerank.hybrid_search(query, top_k=5)
    print(f"✅ Loaded {len(results_with_rerank)} results with cross-encoder reranking\n")
    
    # Create retriever WITHOUT reranking
    print("Creating hybrid retriever WITHOUT reranking...")
    retriever_no_rerank = HybridRetriever(enable_reranking=False)
    results_no_rerank = retriever_no_rerank.hybrid_search(query, top_k=5)
    print(f"✅ Loaded {len(results_no_rerank)} results without reranking\n")
    
    # Display comparison
    print("=" * 80)
    print(f"Query: '{query}'")
    print("=" * 80)
    print()
    
    print("📊 WITHOUT RERANKING (BM25 + pgvector average):")
    print("-" * 80)
    for i, doc in enumerate(results_no_rerank, 1):
        print_result(doc, i)
    print()
    
    print("📊 WITH RERANKING (cross-encoder scoring):")
    print("-" * 80)
    for i, doc in enumerate(results_with_rerank, 1):
        print_result(doc, i)
    print()
    
    # Analysis
    print("=" * 80)
    print("📈 Analysis")
    print("=" * 80)
    print()
    print("The reranker uses a cross-encoder model to directly score")
    print("query-document relevance pairs, providing more accurate ranking.")
    print()
    print(f"Model: cross-encoder/ms-marco-MiniLM-L-12-v2")
    print("  - 12-layer BERT-based cross-encoder")
    print("  - Trained on MS-MARCO (1M+ Q&A pairs)")
    print("  - ~22M parameters (fast for real-time use)")
    print("  - Scores from 0-1 (higher = more relevant)")
    print()
    
    # Show detailed scores
    print("=" * 80)
    print("🔍 Detailed Scores (WITH RERANKING)")
    print("=" * 80)
    print()
    
    retriever_details = HybridRetriever(enable_reranking=True)
    results_detailed = retriever_details.hybrid_search_with_details(query, top_k=5)
    
    for i, doc in enumerate(results_detailed, 1):
        doc_id = doc.get('id', 'N/A')
        bm25 = doc.get('bm25_score', 0)
        pgvector = doc.get('pgvector_score', 0)
        hybrid = doc.get('hybrid_score', 0)
        rerank = doc.get('rerank_score', 0)
        method = doc.get('method', 'unknown')
        
        print(f"{i}. Document {doc_id}")
        print(f"   BM25 score:      {bm25:.4f}  (keyword relevance)")
        print(f"   PGVector score:  {pgvector:.4f}  (semantic similarity)")
        print(f"   Hybrid score:    {hybrid:.4f}  (average of BM25 + PGVector)")
        print(f"   Rerank score:    {rerank:.4f}  (cross-encoder final score)")
        print(f"   Ranking method:  {method}")
        print()


def demo_alternative_models():
    """Show other available cross-encoder models."""
    print("=" * 80)
    print("🎯 Alternative Cross-Encoder Models")
    print("=" * 80)
    print()
    print("You can change the model in HybridRetriever():")
    print()
    print("# QA-focused model (better for question-answering)")
    print("retriever = HybridRetriever(")
    print('    enable_reranking=True,')
    print('    reranker_model="cross-encoder/qnli-distilroberta-base"')
    print(")")
    print()
    print("# Fast model (for large-scale):")
    print("retriever = HybridRetriever(")
    print('    enable_reranking=True,')
    print('    reranker_model="cross-encoder/ms-marco-TinyBERT-L-2-v2"')
    print(")")
    print()
    print("# Disable reranking (faster, less accurate)")
    print("retriever = HybridRetriever(enable_reranking=False)")
    print()


if __name__ == "__main__":
    try:
        demo_reranker()
        print()
        demo_alternative_models()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
