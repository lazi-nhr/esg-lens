from typing import List, Dict
import logging
import os

from app.core.config import HF_MODEL, HF_API_KEY, HF_HOME

logger = logging.getLogger(__name__)

# 1. Update the model target
MODEL_NAME = HF_MODEL
CACHE_DIR = HF_HOME
_model = None
_tokenizer = None

def _get_model():
    global _model, _tokenizer
    if _model is None:
        # Changed to Auto classes for decoder-only architectures
        from transformers import AutoModelForCausalLM, AutoTokenizer
        logger.info(f"Loading {MODEL_NAME}...")
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)
        _model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME, 
            cache_dir=CACHE_DIR, 
            device_map="auto",  # automatically selects device (GPU or CPU)
            torch_dtype="auto"
        )
        
        # Log device information
        if hasattr(_model, 'device'):
            logger.info(f"Model loaded on device: {_model.device}")
        else:
            # For models with multiple devices
            devices = set()
            for param in _model.parameters():
                devices.add(str(param.device))
            logger.info(f"Model loaded on devices: {devices}")
        
        logger.info(f"Model ready. Parameters: {_model.num_parameters():,}")
    return _model, _tokenizer

async def generate_answer(query: str, retrieved_docs: List[Dict]) -> str:
    if not retrieved_docs:
        return "No relevant documents found in the database."
    try:
        return _run_local_inference(query, retrieved_docs)
    except Exception as e:
        logger.error(f"Local inference failed: {e}")
        return _placeholder_answer(retrieved_docs)

def _run_local_inference(query: str, retrieved_docs: List[Dict]) -> str:
    model, tokenizer = _get_model()
    
    # Format context
    context_parts = []
    for i, doc in enumerate(retrieved_docs[:3], start=1):
        content = doc.get("content", "").strip()[:800]
        context_parts.append(f"Excerpt {i}: {content}")
    context = "\n\n".join(context_parts)
    
    # Read template
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "esg_report.md")
    with open(prompt_path, "r") as f:
        template = f.read()
        
    # Extract company name dynamically out of the query string if possible, or leave a fallback
    company_name = "ABB" if "ABB" in query else ("Roche" if "Roche" in query else "Target Company")
    formatted_prompt = template.format(company=company_name, criterion="Environmental", context=context)

    # 2. Use modern Chat Templates for instruction alignment
    messages = [
        {"role": "system", "content": "You are a professional ESG assistant. Generate comprehensive structured reports."},
        {"role": "user", "content": formatted_prompt}
    ]
    
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
    
    # 3. Request a higher token count for long detailed paragraphs
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=800, 
        temperature=0.3,  # Lower temperature prevents hallucinating metrics
        do_sample=True
    )
    
    # Trim prompt tokens from output
    generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)]
    return tokenizer.decode(generated_ids[0], skip_special_tokens=True).strip()

def _placeholder_answer(retrieved_docs: List[Dict]) -> str:
    best = retrieved_docs[0]
    content = best.get("content", "").strip()
    snippet = content[:400] + "..." if len(content) > 400 else content
    return f"[Showing best matching document (id={best.get('id','?')})]\n\n{snippet}"