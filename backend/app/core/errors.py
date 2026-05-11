"""
Custom exceptions and error handling.
"""


class RAGException(Exception):
    """Base exception for RAG system."""
    pass


class DatabaseError(RAGException):
    """Database connection or query error."""
    pass


class RetrievalError(RAGException):
    """Error during document retrieval."""
    pass


class GenerationError(RAGException):
    """Error during LLM generation."""
    pass
