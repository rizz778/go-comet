from fastapi import APIRouter, UploadFile, File
from controllers.pipeline_controller import process_upload

router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    return await process_upload(file)
