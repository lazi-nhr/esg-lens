"""
Configuration and environment variables.
"""
import os

# Load environment variables from .env file (if it exists)
from dotenv import load_dotenv
load_dotenv()

# Database
DB_HOST = os.getenv("DB_HOST", "nv-service-b48efcd4fbe8cf4a875a2ccb70e0e21b")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "nuvolos")
DB_USER = os.getenv("DB_USER", "nuvolos")
DB_PASSWORD = os.getenv("DB_PASSWORD", "nuvolos")

# Server
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8500"))
# BACKEND_HOST: address for server binding (0.0.0.0 = all interfaces)
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
# BACKEND_URL: address for client connections (what the frontend uses to call the backend)
BACKEND_URL = os.getenv("BACKEND_URL", "localhost")

# Retrieval
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "768"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5")
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "10"))
MAX_TOP_K = int(os.getenv("MAX_TOP_K", "100"))

# Chunking
SEMANTIC_SIMILARITY_THRESHOLD = float(os.getenv("SEMANTIC_SIMILARITY_THRESHOLD", "0.5"))
MIN_CHUNK_TOKENS = int(os.getenv("MIN_CHUNK_TOKENS", "100"))
MAX_CHUNK_TOKENS = int(os.getenv("MAX_CHUNK_TOKENS", "800"))

# LLM / Generation
DEFAULT_FORMAT = "markdown"  # "markdown" | "text"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "huggingface")

# Local model for inference (runs on Tesla T4)
HF_MODEL = os.getenv("HF_MODEL", "Qwen/Qwen2.5-7B")
# Fallback API model for inference (if local model fails)
HF_API_MODEL = os.getenv("HF_API_MODEL", "Qwen/Qwen2.5-7B-Instruct")
# Hugging Face API authentication (for embeddings and fallback inference)
HF_API_KEY = os.getenv("HF_API_KEY", "")
HF_HOME = os.getenv("HF_HOME", "/files/.hf_cache")

# Evaluation Criteria
# Structured definition of available ESG evaluation criteria
EVALUATION_CRITERIA = [
    {
        "id": "overall",
        "name": "Overall ESG Assessment",
        "description": "Comprehensive evaluation of Environmental, Social, and Governance practices",
        "category": "composite",
        "question": "Provide a comprehensive ESG assessment covering all three pillars: environmental, social, and governance performance. Include key achievements, gaps, and recommendations.",
        "context_instructions": "Synthesize insights from all three ESG dimensions. Focus on material issues and strategic importance.",
        "output_format": "narrative",
        "required_fields": ["environmental_score", "social_score", "governance_score", "overall_trends", "key_risks"],
        "retrieval_bias": ["ESG", "sustainability", "corporate responsibility", "material issues"]
    },
    {
        "id": "environment",
        "name": "Environment (E) Summary",
        "description": "Environmental sustainability initiatives, climate action, and resource management",
        "category": "pillar",
        "question": "What are the company's key environmental initiatives and climate commitments? Include emissions reduction targets, renewable energy use, waste management, and environmental compliance.",
        "context_instructions": "Emphasize quantifiable metrics, science-based targets, and progress against commitments. Highlight both achievements and areas needing improvement.",
        "output_format": "structured",
        "required_fields": ["emissions_targets", "renewable_energy_percent", "waste_reduction", "water_usage", "climate_risks"],
        "retrieval_bias": ["emissions", "carbon", "renewable energy", "climate change", "environmental risk", "sustainability"]
    },
    {
        "id": "social",
        "name": "Social (S) Summary",
        "description": "Social responsibility, employee welfare, community impact, and human rights",
        "category": "pillar",
        "question": "What is the company's approach to social responsibility including employee welfare, diversity and inclusion, community engagement, and human rights? Include key programs and their impact.",
        "context_instructions": "Focus on employee satisfaction, diversity metrics, community investment, and social impact measurement. Address labor practices and supply chain responsibility.",
        "output_format": "structured",
        "required_fields": ["employee_diversity", "compensation_equity", "community_investment", "labor_practices", "supply_chain_responsibility"],
        "retrieval_bias": ["diversity", "inclusion", "employee welfare", "community", "human rights", "labor practices", "supply chain"]
    },
    {
        "id": "governance",
        "name": "Governance (G) Summary",
        "description": "Board composition, executive compensation, ethics, and corporate transparency",
        "category": "pillar",
        "question": "What is the company's governance structure and approach to ethics? Include board composition, executive compensation philosophy, ethics programs, and transparency practices.",
        "context_instructions": "Evaluate board diversity, independence, compensation alignment with performance, and governance best practices. Address ethics and compliance frameworks.",
        "output_format": "structured",
        "required_fields": ["board_diversity", "board_independence", "ceo_pay_ratio", "ethics_program", "audit_committee"],
        "retrieval_bias": ["board composition", "executive compensation", "ethics", "compliance", "governance", "transparency", "audit"]
    },
]