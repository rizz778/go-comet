from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from config.settings import settings
from routes.pipeline_routes import router as pipeline_router
from services.storage import init_db

# Initialize SQLite database schema
init_db()

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pipeline_router, prefix="/pipeline", tags=["Pipeline"])

# Mount static files for the SPA frontend
client_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "client"))
if os.path.exists(client_dir):
    app.mount("/client", StaticFiles(directory=client_dir), name="client")

@app.get("/")
def root():
    index_path = os.path.join(client_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"status": "ok", "app": settings.app_name, "message": "Client UI build directory not found."}