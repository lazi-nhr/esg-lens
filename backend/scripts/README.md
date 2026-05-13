# ESG Evaluation Query Scripts

This directory contains scripts for querying the ESG Reporting RAG system database with specific queries.

## Overview

Three query approaches are provided:

### 1. `query_esg_evaluation.py` - API-Based Query
Make HTTP requests to the FastAPI backend's `/evaluate` endpoint.

**Prerequisites:**
- Backend server must be running (`python start_backend.py`)
- Network access to the backend

**Best for:**
- Production use
- Remote backend servers
- Integrated with other systems via API

**Usage:**
```bash
python query_esg_evaluation.py \
  --company "Microsoft" \
  --criterion "Environment" \
  --query "Evaluate Microsoft's Environment (E) Summary. Provide a structured ESG report with key findings."
```

**Options:**
- `--company`: Company name (required)
- `--criterion`: ESG criterion - Environment, Social, or Governance (required)
- `--query`: The evaluation query (required)
- `--top-k`: Number of documents to retrieve (default: 3)
- `--format`: Output format - markdown or text (default: markdown)
- `--backend`: Backend URL (default: http://localhost:8500)
- `--output`: Save report to file (optional)

**Examples:**

```bash
# Basic evaluation
python query_esg_evaluation.py \
  --company "Microsoft" \
  --criterion "Environment" \
  --query "Evaluate Microsoft's Environment (E) Summary. Provide a structured ESG report with key findings."

# Save to file
python query_esg_evaluation.py \
  --company "Apple" \
  --criterion "Social" \
  --query "What are Apple's key social responsibility initiatives?" \
  --output microsoft_env_report.txt

# Remote backend
python query_esg_evaluation.py \
  --company "Tesla" \
  --criterion "Governance" \
  --query "Analyze Tesla's corporate governance structure" \
  --backend "http://backend-server.example.com:8500"
```

---

### 2. `query_database.py` - Direct Database Query
Query the PostgreSQL database directly using vector embeddings without requiring the backend API.

**Prerequisites:**
- PostgreSQL with pgvector extension running
- Database credentials configured in `.env`
- Python dependencies installed (sentence-transformers, psycopg2)

**Best for:**
- Development and debugging
- Offline analysis
- Direct database access
- Custom query patterns

**Usage:**
```bash
# Vector similarity search
python query_database.py --vector "Microsoft climate change initiatives"

# Full-text search
python query_database.py --text "carbon emissions reduction"

# Hybrid search (recommended)
python query_database.py --hybrid "Apple sustainability goals"

# ESG evaluation
python query_database.py --evaluate \
  --company "Microsoft" \
  --criterion "Environment" \
  --query "Evaluate Microsoft's Environment (E) Summary. Provide a structured ESG report with key findings."

# Get company documents
python query_database.py --company "Tesla"
```

**Options:**
- `--vector QUERY`: Vector similarity search
- `--text QUERY`: Full-text keyword search
- `--hybrid QUERY`: Combined vector + full-text search
- `--company NAME`: Get all documents mentioning a company
- `--evaluate`: Perform ESG evaluation (requires --company, --criterion, --query)
- `--criterion`: ESG criterion for evaluation
- `--query`: Query string for evaluation
- `--top-k`: Number of results (default: 3)
- `--json`: Output as JSON
- `--output`: Save results to file

**Examples:**

```bash
# Vector search for Microsoft environmental data
python query_database.py --vector "Microsoft climate change initiatives" --top-k 5

# Full-text search for carbon reduction
python query_database.py --text "carbon emissions" --json --output results.json

# Hybrid search for Apple sustainability
python query_database.py --hybrid "Apple sustainability" --top-k 10

# ESG evaluation with direct database access
python query_database.py --evaluate \
  --company "Microsoft" \
  --criterion "Environment" \
  --query "Evaluate Microsoft's Environment (E) Summary. Provide a structured ESG report with key findings." \
  --json --output microsoft_e_eval.json

# Save company documents
python query_database.py --company "Tesla" --top-k 20 --output tesla_docs.json --json
```

---

### 3. `batch_evaluate.py` - Batch Processing
Evaluate multiple companies and criteria in batch mode with result aggregation.

**Prerequisites:**
- Backend server running (for API mode)
- Or database configured (for direct mode)

**Best for:**
- Evaluating multiple companies at once
- Generating reports for portfolios
- Batch processing workflows
- Parallel evaluation

**Usage:**
```bash
# Evaluate Microsoft across all ESG criteria
python batch_evaluate.py \
  --company "Microsoft" \
  --criteria "Environment" "Social" "Governance"

# Evaluate multiple companies
python batch_evaluate.py \
  --company "Microsoft" "Apple" "Tesla" \
  --criteria "Environment" "Governance"

# Load configuration from file
python batch_evaluate.py --config evaluations.json

# With output files
python batch_evaluate.py \
  --company "Microsoft" "Apple" \
  --criteria "Environment" \
  --output-json results.json \
  --output-csv results.csv \
  --reports-dir ./reports
```

**Options:**
- `--company`: Company name(s) to evaluate
- `--criteria`: ESG criteria (default: Environment, Social, Governance)
- `--config`: Load configurations from JSON file
- `--backend`: Backend API URL
- `--concurrent`: Max concurrent requests (default: 3)
- `--output-json`: Save results to JSON file
- `--output-csv`: Save results to CSV file
- `--reports-dir`: Save individual reports to directory
- `--top-k`: Documents to retrieve (default: 3)

**Examples:**

```bash
# Batch evaluate Microsoft
python batch_evaluate.py --company "Microsoft"

# Multiple companies
python batch_evaluate.py --company "Microsoft" "Apple" "Tesla" "Google"

# Specific criteria
python batch_evaluate.py \
  --company "Microsoft" "Apple" \
  --criteria "Environment" "Governance"

# Save all formats
python batch_evaluate.py \
  --company "Microsoft" "Apple" "Tesla" \
  --output-json results.json \
  --output-csv results.csv \
  --reports-dir ./esg_reports

# Load from configuration file
python batch_evaluate.py --config my_evaluations.json

# With custom concurrency
python batch_evaluate.py \
  --company "Microsoft" "Apple" \
  --concurrent 5 \
  --output-json results.json
```

---

## Configuration File Format

For batch evaluations, create a JSON file with evaluation configurations:

```json
[
  {
    "company": "Microsoft",
    "criterion": "Environment",
    "query": "Evaluate Microsoft's Environment (E) Summary. Provide a structured ESG report with key findings.",
    "top_k": 3,
    "format": "markdown"
  },
  {
    "company": "Microsoft",
    "criterion": "Social",
    "query": "Analyze Microsoft's social responsibility programs and employee practices",
    "top_k": 5,
    "format": "markdown"
  },
  {
    "company": "Microsoft",
    "criterion": "Governance",
    "query": "Evaluate Microsoft's governance structure and board composition",
    "top_k": 3,
    "format": "markdown"
  },
  {
    "company": "Apple",
    "criterion": "Environment",
    "query": "What are Apple's key environmental initiatives and carbon reduction targets?",
    "top_k": 4,
    "format": "markdown"
  }
]
```

Then use: `python batch_evaluate.py --config evaluations.json`

---

## Environment Setup

Ensure the following environment variables are configured in `.env`:

```bash
# Database
DB_HOST=nv-service-b48efcd4fbe8cf4a875a2ccb70e0e21b
DB_PORT=5432
DB_NAME=nuvolos
DB_USER=nuvolos
DB_PASSWORD=nuvolos

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8500

# LLM
HF_API_KEY=your_huggingface_api_key
```

---

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r ../requirements.txt
   ```

2. **Start the backend (for API queries):**
   ```bash
   cd ..
   python start_backend.py
   ```

3. **Run a query script:**
   ```bash
   python query_esg_evaluation.py --company "Microsoft" --criterion "Environment" --query "..."
   ```

---

## Output Formats

### Markdown Report
Default format for detailed, formatted reports with sections and formatting.

### Text Report
Plain text format suitable for logs and simple documentation.

### JSON Output
Structured JSON format for programmatic processing and integration.

### CSV Output
Spreadsheet-compatible format for bulk results and analysis.

---

## Examples

### Example 1: Quick Microsoft E Evaluation
```bash
python query_esg_evaluation.py \
  --company "Microsoft" \
  --criterion "Environment" \
  --query "Evaluate Microsoft's Environment (E) Summary. Provide a structured ESG report with key findings."
```

### Example 2: Direct Database Vector Search
```bash
python query_database.py \
  --vector "Microsoft sustainability goals climate change carbon neutral" \
  --top-k 10 \
  --json \
  --output microsoft_env_docs.json
```

### Example 3: Batch Evaluate Full Portfolio
```bash
python batch_evaluate.py \
  --company "Microsoft" "Apple" "Tesla" "Google" "Meta" \
  --criteria "Environment" "Social" "Governance" \
  --output-json portfolio_esg.json \
  --output-csv portfolio_esg.csv \
  --reports-dir ./company_reports
```

### Example 4: Evaluate from Configuration
```bash
# Create evaluations.json with your queries
python batch_evaluate.py --config evaluations.json \
  --output-csv results.csv \
  --reports-dir ./reports
```

---

## Troubleshooting

### Connection Refused (API queries)
- Ensure backend is running: `python start_backend.py`
- Check backend URL: default is `http://localhost:8500`
- Use `--backend` flag for custom URLs

### Database Connection Error (Direct queries)
- Check `.env` database credentials
- Ensure PostgreSQL is running
- Verify database exists and pgvector extension is enabled

### Timeout Errors
- Increase document retrieval with `--top-k`
- Check network connectivity
- Verify backend is responsive: `curl http://localhost:8500/`

### Out of Memory
- Reduce `--top-k` value
- Reduce `--concurrent` for batch operations
- Process in smaller batches

---

## Performance Notes

- **Vector search** is faster but requires embeddings
- **Full-text search** is good for keyword matching
- **Hybrid search** provides best balance of relevance
- **Batch processing** with `--concurrent 5` is optimal for most systems
- Each evaluation typically takes 5-15 seconds

---

## API Integration

These scripts can be integrated into larger systems:

```python
# Python example
import subprocess
import json

result = subprocess.run([
    'python', 'query_esg_evaluation.py',
    '--company', 'Microsoft',
    '--criterion', 'Environment',
    '--query', 'Evaluate...',
    '--output', 'output.json'
], capture_output=True)
```
