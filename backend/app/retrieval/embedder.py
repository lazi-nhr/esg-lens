"""
Embedding function: convert text to vector representation using sentence-transformers.
"""
from app.core.config import EMBEDDING_DIM

# Lazy load model on first use
_model = None


def _get_model():
    """Load sentence-transformers model (lazy loading)."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model


def create_embedding(text: str) -> str:
    """
    Create embedding vector from text using sentence-transformers.
    
    Uses the 'all-MiniLM-L6-v2' model which produces 384-dimensional vectors.
    This is a lightweight, efficient model suitable for document retrieval tasks.
    
    Args:
        text: The input text to embed.
    
    Returns: String representation of embedding vector in PostgreSQL pgvector format.
    """
    # Ensure text is not empty
    if not text or not text.strip():
        return "[" + ",".join(["0.0"] * EMBEDDING_DIM) + "]"
    
    # Get model and encode
    model = _get_model()
    embedding = model.encode(text, convert_to_tensor=False)
    
    # Convert numpy array to list of floats
    embedding_list = embedding.tolist()
    
    # Format as PostgreSQL pgvector string: "[0.1, 0.2, ..., 0.384]"
    return "[" + ",".join(map(str, embedding_list)) + "]"
