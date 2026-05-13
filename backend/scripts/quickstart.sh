#!/bin/bash
# Quick Start Guide for ESG Query Scripts
# This script demonstrates all three query approaches

set -e

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPTS_DIR")"

echo "🚀 ESG Evaluation Query Scripts - Quick Start Guide"
echo "=================================================="
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${BLUE}📋 Checking prerequisites...${NC}"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python 3 not found. Please install Python 3.8 or later.${NC}"
    exit 1
fi
echo "✅ Python $(python3 --version | cut -d' ' -f2) found"

# Check required packages
echo ""
echo "📦 Required Python packages:"
echo "   - aiohttp (for API queries)"
echo "   - sentence-transformers (for embeddings)"
echo "   - psycopg2 (for database access)"
echo "   - pydantic, fastapi, uvicorn (for backend)"
echo ""
echo "Install with: pip install -r ../requirements.txt"
echo ""

# Menu
show_menu() {
    echo -e "${BLUE}Choose a query approach:${NC}"
    echo ""
    echo "1. API-Based Query (requires backend running)"
    echo "2. Direct Database Query (queries PostgreSQL directly)"
    echo "3. Batch Evaluation (evaluate multiple companies)"
    echo "4. View example configuration"
    echo "5. Full workflow example"
    echo "0. Exit"
    echo ""
    read -p "Enter choice [0-5]: " choice
}

# Example queries
run_api_query() {
    echo ""
    echo -e "${BLUE}🌐 API-Based Query Example${NC}"
    echo "========================================"
    echo ""
    echo "This queries the FastAPI backend."
    echo "Make sure the backend is running:"
    echo "  cd .. && python start_backend.py"
    echo ""
    echo "Command:"
    echo "python query_esg_evaluation.py \\"
    echo "  --company \"Microsoft\" \\"
    echo "  --criterion \"Environment\" \\"
    echo "  --query \"Evaluate Microsoft's Environment (E) Summary. Provide a structured ESG report with key findings.\""
    echo ""
    read -p "Run this example? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python "$SCRIPTS_DIR/query_esg_evaluation.py" \
            --company "Microsoft" \
            --criterion "Environment" \
            --query "Evaluate Microsoft's Environment (E) Summary. Provide a structured ESG report with key findings."
    fi
}

run_database_query() {
    echo ""
    echo -e "${BLUE}🔍 Direct Database Query Example${NC}"
    echo "========================================"
    echo ""
    echo "This queries the database directly without needing the backend."
    echo ""
    echo "Command:"
    echo "python query_database.py --evaluate \\"
    echo "  --company \"Microsoft\" \\"
    echo "  --criterion \"Environment\" \\"
    echo "  --query \"Evaluate Microsoft's Environment (E) Summary. Provide a structured ESG report with key findings.\""
    echo ""
    read -p "Run this example? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python "$SCRIPTS_DIR/query_database.py" --evaluate \
            --company "Microsoft" \
            --criterion "Environment" \
            --query "Evaluate Microsoft's Environment (E) Summary. Provide a structured ESG report with key findings."
    fi
}

run_batch_query() {
    echo ""
    echo -e "${BLUE}📊 Batch Evaluation Example${NC}"
    echo "========================================"
    echo ""
    echo "This evaluates multiple companies in batch mode."
    echo ""
    echo "Command:"
    echo "python batch_evaluate.py \\"
    echo "  --company \"Microsoft\" \"Apple\" \\"
    echo "  --criteria \"Environment\" \"Social\" \\"
    echo "  --output-json results.json"
    echo ""
    read -p "Run this example? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python "$SCRIPTS_DIR/batch_evaluate.py" \
            --company "Microsoft" "Apple" \
            --criteria "Environment" "Social" \
            --output-json "/tmp/esg_results.json"
        echo ""
        echo "Results saved to /tmp/esg_results.json"
    fi
}

show_config() {
    echo ""
    echo -e "${BLUE}📄 Example Configuration File${NC}"
    echo "========================================"
    echo ""
    echo "File: evaluations_example.json"
    echo ""
    head -30 "$SCRIPTS_DIR/evaluations_example.json"
    echo "..."
    echo ""
    echo "Use with: python batch_evaluate.py --config evaluations_example.json"
}

full_workflow() {
    echo ""
    echo -e "${BLUE}🔄 Full Workflow Example${NC}"
    echo "========================================"
    echo ""
    echo "This demonstrates a complete evaluation workflow:"
    echo ""
    echo "Step 1: Check database documents"
    echo "  python query_database.py --company \"Microsoft\" --top-k 5"
    echo ""
    read -p "Run Step 1? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python "$SCRIPTS_DIR/query_database.py" --company "Microsoft" --top-k 5
    fi
    
    echo ""
    echo "Step 2: Vector search for environmental data"
    echo "  python query_database.py --vector \"Microsoft climate carbon\" --top-k 5 --json"
    echo ""
    read -p "Run Step 2? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python "$SCRIPTS_DIR/query_database.py" --vector "Microsoft climate carbon" --top-k 5 --json
    fi
    
    echo ""
    echo "Step 3: Full ESG evaluation"
    echo "  python batch_evaluate.py --company \"Microsoft\" --output-json /tmp/workflow_results.json"
    echo ""
    read -p "Run Step 3? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python "$SCRIPTS_DIR/batch_evaluate.py" \
            --company "Microsoft" \
            --output-json "/tmp/workflow_results.json"
        echo ""
        echo "Results saved to /tmp/workflow_results.json"
    fi
}

# Main loop
while true; do
    echo ""
    echo -e "${GREEN}ESG Evaluation Query Scripts${NC}"
    echo "Location: $SCRIPTS_DIR"
    echo ""
    show_menu
    
    case $choice in
        1) run_api_query ;;
        2) run_database_query ;;
        3) run_batch_query ;;
        4) show_config ;;
        5) full_workflow ;;
        0) echo "Goodbye!"; exit 0 ;;
        *) echo "Invalid option" ;;
    esac
done
