import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    # Simple validation stub
    allowed_extensions = (".pdf", ".png", ".jpg", ".jpeg")
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(status_code=400, detail="Only PDF and Image files are allowed.")
        
    return {
        "status": "received",
        "filename": file.filename,
        "message": "File received. Next step: connect the Multi-Agent Extractor pipeline."
    }
