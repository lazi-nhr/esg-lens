"""
Document repository: CRUD and vector search operations.
"""
from typing import List, Dict

from app.db.connection import get_db_connection
from app.core.config import DEFAULT_TOP_K
from app.core.errors import DatabaseError


class DocumentRepository:
    """Handle all document database operations."""

    @staticmethod
    def add(content: str, embedding: str) -> int:
        """Add a document with its embedding. Returns document ID."""
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO documents (content, embedding) VALUES (%s, %s) RETURNING id;",
                (content, embedding)
            )
            doc_id = cur.fetchone()["id"]
            conn.commit()
            return doc_id
        except Exception as e:
            raise DatabaseError(f"Error adding document: {str(e)}")
        finally:
            if conn:
                cur.close()
                conn.close()

    @staticmethod
    def list_all() -> List[Dict]:
        """Retrieve all documents."""
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, content, created_at FROM documents ORDER BY id;")
            documents = cur.fetchall()
            return documents
        except Exception as e:
            raise DatabaseError(f"Error listing documents: {str(e)}")
        finally:
            if conn:
                cur.close()
                conn.close()

    @staticmethod
    def search_by_similarity(query_embedding: str, top_k: int = DEFAULT_TOP_K) -> List[Dict]:
        """Retrieve documents most similar to the query embedding."""
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, content,
                       1 - (embedding <=> %s::vector) as similarity
                FROM documents
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
                """,
                (query_embedding, query_embedding, top_k)
            )
            results = cur.fetchall()
            return results
        except Exception as e:
            raise DatabaseError(f"Error searching documents: {str(e)}")
        finally:
            if conn:
                cur.close()
                conn.close()
