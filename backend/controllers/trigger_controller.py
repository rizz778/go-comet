import os
import json
import shutil
from datetime import datetime
from fastapi import UploadFile, HTTPException
from config.settings import settings

async def process_email_trigger(
    sender: str,
    subject: str,
    email_body: str,
    files: list[UploadFile]
) -> dict:
    """Saves email attachments and manifest to watched inbox folder to trigger watcher."""
    # 1. Validate file extensions
    allowed_extensions = (".pdf", ".png", ".jpg", ".jpeg")
    for file in files:
        if not file.filename.lower().endswith(allowed_extensions):
            raise HTTPException(
                status_code=400, 
                detail=f"File {file.filename} is not allowed. Only PDF and Image files are allowed."
            )
            
    # 2. Setup directory paths
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    inbox_dir = os.path.join(backend_dir, "inbox")
    
    # Create unique folder name using timestamp to prevent collisions
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    shipment_folder_name = f"shipment_{timestamp}"
    folder_path = os.path.join(inbox_dir, shipment_folder_name)
    
    os.makedirs(folder_path, exist_ok=True)
    
    try:
        # 3. Save attachment files first
        for file in files:
            file_path = os.path.join(folder_path, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                
        # 4. Write manifest.json last to ensure atomic watcher pickup
        manifest = {
            "sender": sender,
            "customer_name": "Nova Enterprise Customer",
            "subject": subject,
            "email_body": email_body,
            "received_at": datetime.utcnow().isoformat() + "Z"
        }
        
        manifest_path = os.path.join(folder_path, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
            
        return {
            "success": True,
            "message": f"Email queued successfully. Created inbox folder: {shipment_folder_name}"
        }
        
    except Exception as e:
        # Clean up directory if we failed mid-write
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        raise HTTPException(status_code=500, detail=f"Failed to trigger email queue: {str(e)}")
