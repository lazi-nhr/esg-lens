#!/usr/bin/env python3
"""
Batch ESG Evaluation Script

Perform multiple ESG evaluations in batch mode, supporting both:
1. API-based queries (via FastAPI backend)
2. Direct database queries (using pgvector)

This script enables:
- Batch evaluation of multiple companies
- Multiple criteria per company
- CSV/JSON output
- Parallel processing
- Result aggregation and analysis
"""

import asyncio
import json
import csv
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import time

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import aiohttp
except ImportError:
    aiohttp = None

from app.core.config import EMBEDDING_DIM


@dataclass
class ESGEvaluationConfig:
    """Configuration for a single ESG evaluation."""
    company: str
    criterion: str
    query: str
    top_k: int = 3
    format: str = "markdown"


@dataclass
class ESGEvaluationResult:
    """Result of an ESG evaluation."""
    company: str
    criterion: str
    query: str
    status: str  # "success", "error", "pending"
    retrieved_count: int = 0
    report: str = ""
    error_message: str = ""
    timestamp: str = ""


class ESGBatchEvaluator:
    """Batch evaluate ESG criteria using the backend API."""
    
    def __init__(self, backend_url: str = "http://localhost:8500", max_concurrent: int = 3):
        """
        Initialize the batch evaluator.
        
        Args:
            backend_url: Backend API URL
            max_concurrent: Maximum concurrent requests
        """
        self.backend_url = backend_url
        self.max_concurrent = max_concurrent
        self.results: List[ESGEvaluationResult] = []
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def evaluate_single(
        self,
        config: ESGEvaluationConfig
    ) -> ESGEvaluationResult:
        """
        Evaluate a single ESG criterion.
        
        Args:
            config: Evaluation configuration
        
        Returns:
            Evaluation result
        """
        async with self.semaphore:
            result = ESGEvaluationResult(
                company=config.company,
                criterion=config.criterion,
                query=config.query,
                status="pending",
                timestamp=self._get_timestamp()
            )
            
            try:
                if aiohttp is None:
                    raise ImportError("aiohttp is required for API queries")
                
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "company": config.company,
                        "criterion": config.criterion,
                        "query": config.query,
                        "top_k": config.top_k,
                        "format": config.format,
                    }
                    
                    async with session.post(
                        f"{self.backend_url}/evaluate",
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=60),
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            result.status = "success"
                            result.retrieved_count = data.get("retrieved_count", 0)
                            result.report = data.get("report", "")
                        else:
                            error_text = await response.text()
                            result.status = "error"
                            result.error_message = f"HTTP {response.status}: {error_text}"
            
            except aiohttp.ClientConnectorError as e:
                result.status = "error"
                result.error_message = f"Connection failed: {str(e)}"
            except asyncio.TimeoutError:
                result.status = "error"
                result.error_message = "Request timeout"
            except Exception as e:
                result.status = "error"
                result.error_message = f"{type(e).__name__}: {str(e)}"
            
            return result
    
    async def evaluate_batch(
        self,
        configs: List[ESGEvaluationConfig]
    ) -> List[ESGEvaluationResult]:
        """
        Evaluate multiple configurations in batch.
        
        Args:
            configs: List of evaluation configurations
        
        Returns:
            List of evaluation results
        """
        print(f"📊 Starting batch evaluation of {len(configs)} configurations...")
        print(f"   Backend: {self.backend_url}")
        print(f"   Concurrent requests: {self.max_concurrent}\n")
        
        start_time = time.time()
        
        # Create tasks for all evaluations
        tasks = [self.evaluate_single(config) for config in configs]
        
        # Run all tasks concurrently
        results = await asyncio.gather(*tasks)
        
        elapsed = time.time() - start_time
        
        # Print summary
        successful = sum(1 for r in results if r.status == "success")
        failed = sum(1 for r in results if r.status == "error")
        
        print(f"✅ Batch evaluation complete ({elapsed:.2f}s)")
        print(f"   Successful: {successful}")
        print(f"   Failed: {failed}")
        print()
        
        self.results = results
        return results
    
    def save_results_json(self, output_path: str) -> None:
        """Save results as JSON."""
        data = [asdict(r) for r in self.results]
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Results saved to: {output_path}")
    
    def save_results_csv(self, output_path: str) -> None:
        """Save results as CSV."""
        if not self.results:
            print("❌ No results to save")
            return
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'company', 'criterion', 'query', 'status', 
                'retrieved_count', 'error_message', 'timestamp'
            ])
            writer.writeheader()
            for result in self.results:
                row = asdict(result)
                row.pop('report', None)  # Don't include full report in CSV
                writer.writerow(row)
        print(f"✅ Results saved to: {output_path}")
    
    def save_reports_separate(self, output_dir: str) -> None:
        """Save each report to a separate file."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        for result in self.results:
            if result.status == "success" and result.report:
                filename = f"{result.company}_{result.criterion}.txt"
                filepath = Path(output_dir) / filename
                with open(filepath, 'w') as f:
                    f.write(f"Company: {result.company}\n")
                    f.write(f"Criterion: {result.criterion}\n")
                    f.write(f"Retrieved Documents: {result.retrieved_count}\n")
                    f.write("=" * 80 + "\n\n")
                    f.write(result.report)
        
        print(f"✅ Reports saved to: {output_dir}")
    
    def print_summary(self) -> None:
        """Print summary of all results."""
        print("=" * 80)
        print("EVALUATION SUMMARY")
        print("=" * 80)
        print()
        
        for result in self.results:
            status_emoji = "✅" if result.status == "success" else "❌"
            print(f"{status_emoji} {result.company} - {result.criterion}")
            print(f"   Status: {result.status}")
            if result.status == "success":
                print(f"   Retrieved: {result.retrieved_count} documents")
            else:
                print(f"   Error: {result.error_message}")
            print()
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp."""
        import datetime
        return datetime.datetime.now().isoformat()


def load_configs_from_json(json_file: str) -> List[ESGEvaluationConfig]:
    """Load evaluation configurations from JSON file."""
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    configs = []
    for item in data:
        configs.append(ESGEvaluationConfig(
            company=item['company'],
            criterion=item['criterion'],
            query=item['query'],
            top_k=item.get('top_k', 3),
            format=item.get('format', 'markdown'),
        ))
    return configs


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Batch ESG Evaluation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Evaluate Microsoft E, S, G
  python batch_evaluate.py \\
    --company "Microsoft" \\
    --criteria "Environment" "Social" "Governance"

  # Load configurations from JSON
  python batch_evaluate.py --config evaluations.json

  # With output files
  python batch_evaluate.py \\
    --company "Apple" "Tesla" "Microsoft" \\
    --criteria "Environment" \\
    --output-json results.json \\
    --output-csv results.csv \\
    --reports-dir ./reports

evaluations.json format:
[
  {
    "company": "Microsoft",
    "criterion": "Environment",
    "query": "Evaluate Microsoft's Environment (E) Summary. Provide a structured ESG report with key findings.",
    "top_k": 3,
    "format": "markdown"
  },
  ...
]
        """
    )
    
    parser.add_argument(
        "--company",
        nargs="+",
        help="Company name(s) to evaluate"
    )
    parser.add_argument(
        "--criteria",
        nargs="+",
        default=["Environment", "Social", "Governance"],
        help="ESG criteria to evaluate (default: all three)"
    )
    parser.add_argument(
        "--config",
        help="Load configurations from JSON file"
    )
    parser.add_argument(
        "--backend",
        default="http://localhost:8500",
        help="Backend API URL (default: http://localhost:8500)"
    )
    parser.add_argument(
        "--concurrent",
        type=int,
        default=3,
        help="Maximum concurrent requests (default: 3)"
    )
    parser.add_argument(
        "--output-json",
        help="Save results to JSON file"
    )
    parser.add_argument(
        "--output-csv",
        help="Save results to CSV file"
    )
    parser.add_argument(
        "--reports-dir",
        help="Save individual reports to directory"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Documents to retrieve (default: 3)"
    )
    
    args = parser.parse_args()
    
    # Load or create configurations
    if args.config:
        configs = load_configs_from_json(args.config)
        print(f"📋 Loaded {len(configs)} configurations from {args.config}\n")
    elif args.company:
        configs = []
        for company in args.company:
            for criterion in args.criteria:
                query = f"Evaluate {company}'s {criterion} Summary. Provide a structured ESG report with key findings."
                configs.append(ESGEvaluationConfig(
                    company=company,
                    criterion=criterion,
                    query=query,
                    top_k=args.top_k,
                ))
        print(f"📋 Created {len(configs)} evaluation configurations\n")
    else:
        parser.print_help()
        sys.exit(0)
    
    # Run batch evaluation
    evaluator = ESGBatchEvaluator(args.backend, args.concurrent)
    
    try:
        results = asyncio.run(evaluator.evaluate_batch(configs))
        
        # Print summary
        evaluator.print_summary()
        
        # Save results
        if args.output_json:
            evaluator.save_results_json(args.output_json)
        if args.output_csv:
            evaluator.save_results_csv(args.output_csv)
        if args.reports_dir:
            evaluator.save_reports_separate(args.reports_dir)
    
    except KeyboardInterrupt:
        print("\n❌ Batch evaluation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
