#!/usr/bin/env python3
"""
Query the ESG Evaluation RAG system with a specific evaluation request.

This script makes an HTTP request to the backend API's /evaluate endpoint
to retrieve and generate an ESG report for a company and criterion.

Example:
    python query_esg_evaluation.py \
        --company "Microsoft" \
        --criterion "Environment" \
        --query "Evaluate Microsoft's Environment (E) Summary. Provide a structured ESG report with key findings."
"""

import asyncio
import aiohttp
import argparse
import json
import sys
from typing import Dict, Any

# Default backend configuration
DEFAULT_BACKEND_HOST = "localhost"
DEFAULT_BACKEND_PORT = 8500
DEFAULT_TOP_K = 3
DEFAULT_FORMAT = "markdown"


async def query_esg_evaluation(
    company: str,
    criterion: str,
    query: str,
    top_k: int = DEFAULT_TOP_K,
    format_type: str = DEFAULT_FORMAT,
    backend_url: str = None,
) -> Dict[str, Any]:
    """
    Query the ESG evaluation endpoint.
    
    Args:
        company: Company name (e.g., "Microsoft")
        criterion: ESG criterion (e.g., "Environment", "Social", "Governance")
        query: The evaluation query
        top_k: Number of documents to retrieve (default: 3)
        format_type: Output format "markdown" or "text" (default: "markdown")
        backend_url: Full backend URL (if not provided, uses localhost:8500)
    
    Returns:
        Dict containing the evaluation response
    """
    if backend_url is None:
        backend_url = f"http://{DEFAULT_BACKEND_HOST}:{DEFAULT_BACKEND_PORT}"
    
    evaluate_endpoint = f"{backend_url}/evaluate"
    
    payload = {
        "company": company,
        "criterion": criterion,
        "query": query,
        "top_k": top_k,
        "format": format_type,
    }
    
    print(f"📊 Querying ESG Evaluation System...")
    print(f"   Company: {company}")
    print(f"   Criterion: {criterion}")
    print(f"   Backend: {backend_url}")
    print(f"   Top-K: {top_k}")
    print(f"   Format: {format_type}")
    print()
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                evaluate_endpoint,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60),
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    error_text = await response.text()
                    print(f"❌ Error: HTTP {response.status}")
                    print(f"   {error_text}")
                    return None
    except aiohttp.ClientConnectorError as e:
        print(f"❌ Connection Error: Could not connect to {evaluate_endpoint}")
        print(f"   Make sure the backend is running on {backend_url}")
        print(f"   Error: {str(e)}")
        return None
    except asyncio.TimeoutError:
        print(f"❌ Timeout Error: Request to {evaluate_endpoint} took too long")
        return None
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {str(e)}")
        return None


def print_report(result: Dict[str, Any]) -> None:
    """Pretty-print the evaluation report."""
    if result is None:
        return
    
    print("=" * 80)
    print("✅ ESG EVALUATION REPORT")
    print("=" * 80)
    print()
    
    print(f"Company:         {result.get('company', 'N/A')}")
    print(f"Criterion:       {result.get('criterion', 'N/A')}")
    print(f"Retrieved Docs:  {result.get('retrieved_count', 0)}")
    print(f"Format:          {result.get('format', 'N/A')}")
    print()
    
    print("-" * 80)
    print("REPORT:")
    print("-" * 80)
    print()
    print(result.get('report', 'No report generated'))
    print()
    print("=" * 80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Query the ESG Evaluation RAG system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Microsoft Environment Summary
  python query_esg_evaluation.py \\
    --company "Microsoft" \\
    --criterion "Environment" \\
    --query "Evaluate Microsoft's Environment (E) Summary. Provide a structured ESG report with key findings."

  # Apple Social Responsibility
  python query_esg_evaluation.py \\
    --company "Apple" \\
    --criterion "Social" \\
    --query "What are Apple's key social responsibility initiatives and impact?"

  # Tesla Governance
  python query_esg_evaluation.py \\
    --company "Tesla" \\
    --criterion "Governance" \\
    --query "Analyze Tesla's corporate governance structure and board composition."
        """
    )
    
    parser.add_argument(
        "--company",
        required=True,
        help="Company name to evaluate (e.g., 'Microsoft')"
    )
    parser.add_argument(
        "--criterion",
        required=True,
        help="ESG criterion: 'Environment', 'Social', or 'Governance'"
    )
    parser.add_argument(
        "--query",
        required=True,
        help="The evaluation query"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=DEFAULT_TOP_K,
        help=f"Number of documents to retrieve (default: {DEFAULT_TOP_K})"
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "text"],
        default=DEFAULT_FORMAT,
        help=f"Output format (default: {DEFAULT_FORMAT})"
    )
    parser.add_argument(
        "--backend",
        help=f"Backend URL (default: http://{DEFAULT_BACKEND_HOST}:{DEFAULT_BACKEND_PORT})"
    )
    parser.add_argument(
        "--output",
        help="Save report to file (optional)"
    )
    
    args = parser.parse_args()
    
    # Run the async query
    result = asyncio.run(
        query_esg_evaluation(
            company=args.company,
            criterion=args.criterion,
            query=args.query,
            top_k=args.top_k,
            format_type=args.format,
            backend_url=args.backend,
        )
    )
    
    # Print the report
    if result:
        print_report(result)
        
        # Save to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                f.write(result.get('report', ''))
            print(f"✅ Report saved to: {args.output}")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
