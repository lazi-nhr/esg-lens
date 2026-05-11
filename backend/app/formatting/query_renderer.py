"""
Query formatting: construct enriched queries for semantic search.
"""


def build_enriched_query(company: str = None, criterion: str = None, query: str = None) -> str:
    """
    Build an enriched query by prepending company and criterion context.
    
    Args:
        company: Company name (optional)
        criterion: ESG criterion (optional)
        query: Base query string
    
    Returns: Enriched query string suitable for embedding and vector search
    
    Example:
        build_enriched_query("Apple", "emissions", "sustainability report")
        → "emissions - Apple: sustainability report"
    """
    parts = []
    
    if criterion:
        parts.append(criterion.lower())
    
    if company:
        parts.append(company)
    
    if query:
        parts.append(query)
    
    return " - ".join(parts).strip() if parts else ""
