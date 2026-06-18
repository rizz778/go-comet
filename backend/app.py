from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from routes.chat_routes import router as chat_router
from routes.pipeline_routes import router as pipeline_router

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/chat", tags=["Chat"])
app.include_router(pipeline_router, prefix="/pipeline", tags=["Pipeline"])

@app.get("/")
def root():
    return {"status": "ok", "app": settings.app_name}