"""
Embedding function: convert text to vector representation.
"""
from app.core.config import EMBEDDING_DIM


def create_embedding(text: str) -> str:
    """
    Create a simple embedding vector from text.
    
    This is a placeholder for demonstration. In production, use a proper embedding model
    (e.g., sentence-transformers, OpenAI embeddings).
    
    Returns: string representation of a float vector (PostgreSQL pgvector format).
    """
    embedding = [0.0] * EMBEDDING_DIM
    text = text.lower()

    # Use character codes and position to create a simple embedding
    for i, char in enumerate(text[:EMBEDDING_DIM]):
        embedding[i] = (ord(char) % 256) / 256.0

    # Add word-based features with deterministic hashing
    words = text.split()
    for i, word in enumerate(words[:192]):
        idx = (hash(word.encode('utf-8')) % 192) + 192
        embedding[idx] = min(embedding[idx] + 0.1, 1.0)

    return "[" + ",".join(map(str, embedding)) + "]"
