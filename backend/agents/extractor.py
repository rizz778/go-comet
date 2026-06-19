import os
import json
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from concurrent.futures import ThreadPoolExecutor
from graph.state import PipelineState
from config.settings import settings
from schemas.extractor_schemas import TradeDocumentExtraction
from prompts.extractor_prompts import EXTRACTOR_SYSTEM_PROMPT


def get_gemini_client():
    api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")
    genai.configure(api_key=api_key)
    return genai
def extract_single_file(file_path: str, filename: str, model, config) -> tuple[str, dict, str]:
    """Helper function to run extraction on a single file (executed in thread pool)"""
    try:
        with open(file_path, "rb") as f:
            file_bytes = f.read()
            
        mime_type = "application/pdf" if file_path.lower().endswith(".pdf") else "image/jpeg"
        if file_path.lower().endswith(".png"):
            mime_type = "image/png"
            
        response = model.generate_content(
            [
                {"mime_type": mime_type, "data": file_bytes},
                EXTRACTOR_SYSTEM_PROMPT
            ],
            generation_config=config
        )
        
        file_data = json.loads(response.text)
        return filename, file_data, f"Extractor Agent: Extraction completed for {filename}."
    except Exception as e:
        # Fallback values structure
        fields = [
            "consignee_name", "hs_code", "port_of_loading", "port_of_discharge",
            "incoterms", "description_of_goods", "gross_weight", "invoice_number"
        ]
        fallback = {
            f: {"value": None, "confidence": 0.0, "source_snippet": None}
            for f in fields
        }
        fallback["extraction_warnings"] = [f"Extraction failed: {str(e)}"]
        return filename, fallback, f"Extractor Agent: Extraction failed for {filename} ({str(e)})."
def extract_agent(state: PipelineState) -> PipelineState:
    logs = list(state.get("logs", []))
    logs.append("Extractor Agent: Initializing Gemini Client...")
    
    file_paths = state.get("file_paths", [])
    filenames = state.get("filenames", [])
    
    if not file_paths and "file_path" in state:
        file_paths = [state["file_path"]]
        filenames = [state.get("filename", "document.pdf")]
        
    extracted_data = {}
    
    try:
        ai = get_gemini_client()
        model = ai.GenerativeModel(settings.gemini_model)
        config = GenerationConfig(
            response_mime_type="application/json",
            response_schema=TradeDocumentExtraction,
            temperature=0.1
        )
        
        logs.append(f"Extractor Agent: Starting concurrent extraction of {len(file_paths)} files...")
        
        # Process files in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=len(file_paths)) as executor:
            futures = [
                executor.submit(extract_single_file, path, name, model, config)
                for path, name in zip(file_paths, filenames)
            ]
            
            for future in futures:
                name, file_data, log_msg = future.result()
                extracted_data[name] = file_data
                logs.append(log_msg)
                
    except Exception as e:
        logs.append(f"Extractor Agent: Client initialization error ({str(e)})")
        
    logs.append("Extractor Agent: Multi-document extraction finished.")
    
    return {
        **state,
        "extracted_data": extracted_data,
        "logs": logs
    }