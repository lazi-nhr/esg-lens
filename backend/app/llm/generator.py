"""
LLM generation: wrapper for language model calls.
For now, this is a placeholder that returns simple answers.
Later, hook in real LLM (OpenAI, Anthropic, open-source, etc.).
"""
from typing import List, Dict

from app.core.errors import GenerationError


async def generate_answer(query: str, retrieved_docs: List[Dict]) -> str:
    """
    Generate an answer based on the query and retrieved documents.
    
    This is a placeholder. In production, send to an LLM API.
    
    Args:
        query: The user's question.
        retrieved_docs: List of similar documents from the database.
    
    Returns: Generated answer string.
    """
    try:
        if not retrieved_docs:
            return "No relevant documents found in the database."

        # Simple placeholder: return truncated best match
        best_match = retrieved_docs[0]
        content = best_match["content"]

        if len(content) > 200:
            return f"Based on the documents, here's what I found: {content[:200]}..."
        else:
            return f"Based on the documents, here's what I found: {content}"
    except Exception as e:
        raise GenerationError(f"Error generating answer: {str(e)}")
