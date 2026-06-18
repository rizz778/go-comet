import os
import json
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from graph.state import PipelineState
from config.settings import settings
from schemas.extractor_schemas import TradeDocumentExtraction
from prompts.extractor_prompts import EXTRACTOR_SYSTEM_PROMPT

def get_gemini_client():
    """Initializes and returns the configured genai client module."""
    api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in your .env or system environment.")
    genai.configure(api_key=api_key)
    return genai

def extract_agent(state: PipelineState) -> PipelineState:
    logs = list(state.get("logs", []))
    logs.append("Extractor Agent: Initializing Gemini Client...")
    
    file_path = state["file_path"]
    
    try:
        # 1. Initialize Gemini Client
        ai = get_gemini_client()
        
        logs.append(f"Extractor Agent: Reading file bytes for {state['filename']}...")
        
        # 2. Read raw file bytes
        with open(file_path, "rb") as f:
            file_bytes = f.read()
            
        mime_type = "application/pdf" if file_path.lower().endswith(".pdf") else "image/jpeg"
        if file_path.lower().endswith(".png"):
            mime_type = "image/png"
            
        logs.append(f"Extractor Agent: Sending content inline to {settings.gemini_model}...")
        
        # 3. Configure Gemini Model with Pydantic Schema
        model = ai.GenerativeModel(settings.gemini_model)
        
        config = GenerationConfig(
            response_mime_type="application/json",
            response_schema=TradeDocumentExtraction,
            temperature=0.1
        )
        
        # 4. Invoke model with inline bytes and prompt
        response = model.generate_content(
            [
                {
                    "mime_type": mime_type,
                    "data": file_bytes
                },
                EXTRACTOR_SYSTEM_PROMPT
            ],
            generation_config=config
        )
        
        # 5. Parse structured output JSON
        extracted_data = json.loads(response.text)
        
    except Exception as e:
        logs.append(f"Extractor Agent: Vision call failed ({str(e)}). Falling back to empty state.")
        fields = [
            "consignee_name", "hs_code", "port_of_loading", "port_of_discharge",
            "incoterms", "description_of_goods", "gross_weight", "invoice_number"
        ]
        extracted_data = {
            f: {"value": None, "confidence": 0.0, "source_snippet": None}
            for f in fields
        }
        extracted_data["extraction_warnings"] = [f"Vision Extraction Failed: {str(e)}"]
        
    logs.append("Extractor Agent: Extraction step completed.")
    
    return {
        **state,
        "raw_text": "Processed directly via inline byte payload to Gemini API.",
        "extracted_data": extracted_data,
        "logs": logs
    }
