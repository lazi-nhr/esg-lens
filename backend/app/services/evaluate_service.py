"""
Evaluate service: orchestrate retrieval + generation for ESG evaluation.
"""
from typing import Dict

from app.retrieval.vector_search import retrieve_similar
from app.llm.generator import generate_answer
from app.formatting.query_renderer import build_enriched_query
from app.formatting.report_renderer import format_report_markdown, format_report_text
from app.core.config import DEFAULT_TOP_K, DEFAULT_FORMAT


async def evaluate(
    company: str,
    criterion: str,
    query: str,
    top_k: int = DEFAULT_TOP_K,
    format: str = DEFAULT_FORMAT
) -> Dict:
    """
    Execute an ESG evaluation: retrieve documents, generate answer, format report.
    
    Args:
        company: Company name (e.g., "Microsoft")
        criterion: ESG criterion (e.g., "emissions", "governance", etc.)
        query: The evaluation query
        top_k: Number of documents to retrieve
        format: Output format ("markdown" or "text")
    
    Returns: Dict with company, criterion, query, retrieved_count, report, format
    """
    # Build enriched query for vector search
    enriched_query = build_enriched_query(company, criterion, query)

    # Retrieve similar documents
    retrieved_docs = await retrieve_similar(enriched_query, top_k)

    # Generate assessment
    assessment = await generate_answer(enriched_query, retrieved_docs)

    # Format the report
    if format == "markdown":
        report = format_report_markdown(company, criterion, enriched_query, retrieved_docs, assessment)
    else:
        report = format_report_text(company, criterion, enriched_query, retrieved_docs, assessment)

    return {
        "company": company,
        "criterion": criterion,
        "query": enriched_query,
        "retrieved_count": len(retrieved_docs),
        "report": report,
        "format": format,
    }
