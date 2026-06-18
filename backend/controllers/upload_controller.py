import os
import shutil
from fastapi import UploadFile, HTTPException
from config.settings import settings
from graph.graph import pipeline_graph

async def process_upload(file: UploadFile) -> dict:
    
    # 1. Validate file extension
    allowed_extensions = (".pdf", ".png", ".jpg", ".jpeg")
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(status_code=400, detail="Only PDF and Image files are allowed.")
        
    # 2. Save the file locally
    os.makedirs(settings.upload_dir, exist_ok=True)
    file_path = os.path.join(settings.upload_dir, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")
        
    # 3. Invoke LangGraph pipeline
    try:
        initial_state = {
            "filename": file.filename,
            "file_path": file_path,
            "raw_text": "",
            "extracted_data": {},
            "validation_results": {},
            "decision": "",
            "decision_reason": "",
            "amendment_draft": None,
            "logs": ["Upload Node: Document saved successfully."]
        }
        
        final_state = pipeline_graph.invoke(initial_state)
        
        # Parse the assigned SQLite database ID from logs to return to client
        db_log = [log for log in final_state["logs"] if "DB ID:" in log]
        run_id = None
        if db_log:
            try:
                run_id = int(db_log[0].split("DB ID:")[-1].strip())
            except Exception:
                pass
                
        return {
            "run_id": run_id,
            "filename": final_state["filename"],
            "extracted_data": final_state["extracted_data"],
            "validation_results": final_state["validation_results"],
            "decision": final_state["decision"],
            "decision_reason": final_state["decision_reason"],
            "amendment_draft": final_state["amendment_draft"],
            "logs": final_state["logs"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")
