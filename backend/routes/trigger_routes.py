from fastapi import APIRouter, UploadFile, File, Form
from controllers.trigger_controller import process_email_trigger

router = APIRouter()

@router.post("/trigger-email")
async def trigger_email(
    sender: str = Form(...),
    subject: str = Form(...),
    email_body: str = Form(...),
    file: list[UploadFile] = File(...)
):
    """Endpoint simulating an incoming supplier email.
    
    Accepts sender, subject, body, and attachment files.
    """
    return await process_email_trigger(sender, subject, email_body, file)
