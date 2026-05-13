#!/usr/bin/env python3
"""
Direct database query script for ESG documents using vector similarity search.

This script queries the PostgreSQL database directly with pgvector embeddings,
without requiring the FastAPI backend to be running.

It demonstrates:
  - Direct database connection
  - Vector similarity search using pgvector
  - Full-text search on ESG documents
  - Batch processing of queries
"""

import os
import sys
import argparse
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import psycopg2
from psycopg2.extras import RealDictCursor
from sentence_transformers import SentenceTransformer

from app.core.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
from app.core.config import EMBEDDING_DIM
from app.core.errors import DatabaseError


class ESGDatabaseQuerier:
    """Query ESG documents from the database using vector embeddings."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the querier.
        
        Args:
            model_name: Sentence transformer model for embeddings
        """
        self.model = SentenceTransformer(model_name)
        self.conn = None
    
    def connect(self) -> None:
        """Connect to the database."""
        try:
            self.conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                cursor_factory=RealDictCursor
            )
            print(f"✅ Connected to database: {DB_NAME} on {DB_HOST}:{DB_PORT}")
        except Exception as e:
            raise DatabaseError(f"Failed to connect to database: {str(e)}")
    
    def disconnect(self) -> None:
        """Disconnect from the database."""
        if self.conn:
            self.conn.close()
            print("✅ Disconnected from database")
    
    def get_document_count(self) -> int:
        """Get total number of documents in the database."""
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT COUNT(*) as count FROM documents;")
            result = cur.fetchone()
            cur.close()
            return result['count'] if result else 0
        except Exception as e:
            print(f"❌ Error getting document count: {e}")
            return 0
    
    def vector_search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search.
        
        Args:
            query: The search query
            top_k: Number of results to return
        
        Returns:
            List of matching documents with similarity scores
        """
        try:
            # Generate embedding for the query
            query_embedding = self.model.encode(query, convert_to_tensor=False)
            embedding_list = query_embedding.tolist()
            
            cur = self.conn.cursor()
            
            # Vector similarity search using cosine distance
            query_sql = """
                SELECT 
                    id,
                    content,
                    created_at,
                    (1 - (embedding <=> %s::vector)) as similarity
                FROM documents
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
            """
            
            cur.execute(query_sql, (embedding_list, embedding_list, top_k))
            results = cur.fetchall()
            cur.close()
            
            return [dict(row) for row in results]
        except Exception as e:
            print(f"❌ Vector search error: {e}")
            return []
    
    def full_text_search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Perform full-text search on document content.
        
        Args:
            query: The search query
            top_k: Number of results to return
        
        Returns:
            List of matching documents
        """
        try:
            cur = self.conn.cursor()
            
            # Full-text search using LIKE pattern matching
            search_pattern = f"%{query}%"
            query_sql = """
                SELECT 
                    id,
                    content,
                    created_at
                FROM documents
                WHERE content ILIKE %s
                LIMIT %s;
            """
            
            cur.execute(query_sql, (search_pattern, top_k))
            results = cur.fetchall()
            cur.close()
            
            return [dict(row) for row in results]
        except Exception as e:
            print(f"❌ Full-text search error: {e}")
            return []
    
    def hybrid_search(self, query: str, top_k: int = 3, vector_weight: float = 0.7) -> List[Dict[str, Any]]:
        """
        Perform hybrid search (vector + full-text).
        
        Args:
            query: The search query
            top_k: Number of results to return
            vector_weight: Weight for vector similarity (0-1)
        
        Returns:
            List of top-k documents ranked by hybrid score
        """
        vector_results = self.vector_search(query, top_k * 2)
        text_results = self.full_text_search(query, top_k * 2)
        
        # Combine and rank results
        combined = {}
        
        # Add vector results
        for i, doc in enumerate(vector_results):
            doc_id = doc['id']
            score = doc.get('similarity', 0) * vector_weight
            combined[doc_id] = doc.copy()
            combined[doc_id]['hybrid_score'] = score
        
        # Add text results
        text_weight = 1.0 - vector_weight
        for i, doc in enumerate(text_results):
            doc_id = doc['id']
            text_score = (1 - i / max(1, len(text_results))) * text_weight
            if doc_id in combined:
                combined[doc_id]['hybrid_score'] += text_score
            else:
                combined[doc_id] = doc.copy()
                combined[doc_id]['hybrid_score'] = text_score
        
        # Sort by hybrid score
        results = sorted(
            combined.values(),
            key=lambda x: x.get('hybrid_score', 0),
            reverse=True
        )[:top_k]
        
        return results
    
    def get_documents_by_company(self, company: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Get documents related to a specific company.
        
        Args:
            company: Company name
            top_k: Number of results
        
        Returns:
            List of documents mentioning the company
        """
        return self.full_text_search(company, top_k)
    
    def evaluate_esg_criterion(
        self,
        company: str,
        criterion: str,
        query: str,
        top_k: int = 3
    ) -> Dict[str, Any]:
        """
        Evaluate a specific ESG criterion for a company.
        
        Args:
            company: Company name
            criterion: ESG criterion (Environment, Social, Governance)
            query: Evaluation query
            top_k: Number of documents to retrieve
        
        Returns:
            Dict with evaluation results
        """
        # Build enriched search query
        search_query = f"{company} {criterion} {query}"
        
        # Perform hybrid search
        documents = self.hybrid_search(search_query, top_k)
        
        return {
            "company": company,
            "criterion": criterion,
            "query": query,
            "retrieved_count": len(documents),
            "documents": documents,
            "summary": self._generate_summary(company, criterion, documents)
        }
    
    def _generate_summary(
        self,
        company: str,
        criterion: str,
        documents: List[Dict[str, Any]]
    ) -> str:
        """Generate a simple text summary from retrieved documents."""
        if not documents:
            return f"No documents found for {company} {criterion}"
        
        summary = f"ESG Evaluation: {company} - {criterion}\n"
        summary += f"Retrieved {len(documents)} document(s):\n\n"
        
        for i, doc in enumerate(documents, 1):
            content_preview = doc['content'][:200] + "..." if len(doc['content']) > 200 else doc['content']
            similarity = doc.get('similarity', doc.get('hybrid_score', 'N/A'))
            summary += f"{i}. [ID: {doc['id']}] (Score: {similarity})\n"
            summary += f"   {content_preview}\n\n"
        
        return summary


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Query the ESG database directly using vector embeddings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Vector similarity search
  python query_database.py --vector "ABB climate change initiatives"

  # Full-text search
  python query_database.py --text "carbon emissions reduction"

  # Hybrid search (recommended)
  python query_database.py --hybrid "Apple sustainability goals"

  # ESG evaluation
  python query_database.py --evaluate \\
    --company "Microsoft" \\
    --criterion "Environment" \\
    --query "Evaluate Microsoft's Environment (E) Summary. Provide a structured ESG report with key findings."

  # Get company documents
  python query_database.py --company "Tesla"
        """
    )
    
    parser.add_argument(
        "--vector",
        help="Vector similarity search query"
    )
    parser.add_argument(
        "--text",
        help="Full-text search query"
    )
    parser.add_argument(
        "--hybrid",
        help="Hybrid search query (vector + full-text)"
    )
    parser.add_argument(
        "--company",
        help="Get documents by company name"
    )
    parser.add_argument(
        "--evaluate",
        action="store_true",
        help="Perform ESG evaluation (requires --company, --criterion, --query)"
    )
    parser.add_argument(
        "--criterion",
        help="ESG criterion for evaluation (Environment, Social, Governance)"
    )
    parser.add_argument(
        "--query",
        help="Query for evaluation"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of results to return (default: 3)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    parser.add_argument(
        "--output",
        help="Save results to file"
    )
    
    args = parser.parse_args()
    
    # Initialize querier
    try:
        querier = ESGDatabaseQuerier()
        querier.connect()
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        sys.exit(1)
    
    results = None
    
    try:
        # Get document count
        count = querier.get_document_count()
        print(f"📊 Database contains {count} documents\n")
        
        # Perform requested operation
        if args.vector:
            print(f"🔍 Vector search: '{args.vector}'")
            results = querier.vector_search(args.vector, args.top_k)
        
        elif args.text:
            print(f"🔍 Full-text search: '{args.text}'")
            results = querier.full_text_search(args.text, args.top_k)
        
        elif args.hybrid:
            print(f"🔍 Hybrid search: '{args.hybrid}'")
            results = querier.hybrid_search(args.hybrid, args.top_k)
        
        elif args.company:
            print(f"🔍 Company search: '{args.company}'")
            results = querier.get_documents_by_company(args.company, args.top_k)
        
        elif args.evaluate:
            if not all([args.company, args.criterion, args.query]):
                parser.error("--evaluate requires --company, --criterion, and --query")
            print(f"📋 ESG Evaluation:")
            print(f"   Company: {args.company}")
            print(f"   Criterion: {args.criterion}")
            print(f"   Query: {args.query}\n")
            results = querier.evaluate_esg_criterion(
                args.company,
                args.criterion,
                args.query,
                args.top_k
            )
        
        else:
            parser.print_help()
            sys.exit(0)
        
        # Output results
        if results:
            if args.json:
                output = json.dumps(results, indent=2, default=str)
            else:
                if isinstance(results, dict):
                    output = json.dumps(results, indent=2, default=str)
                else:
                    output = "\n".join([
                        f"📄 Document {doc['id']}: {doc['content'][:100]}..."
                        for doc in results
                    ])
            
            print("=" * 80)
            print("RESULTS:")
            print("=" * 80)
            print(output)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output)
                print(f"\n✅ Results saved to: {args.output}")
    
    finally:
        querier.disconnect()


if __name__ == "__main__":
    main()
