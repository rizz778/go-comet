from google.generativeai.types import GenerationConfig
from concurrent.futures import ThreadPoolExecutor
from graph.state import PipelineState
from config.settings import settings
from schemas.extractor_schemas import TradeDocumentExtraction
from helpers.extractor_helper import extract_single_file
from helpers.common_helpers import get_gemini_client

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