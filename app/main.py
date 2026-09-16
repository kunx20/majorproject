from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from app.core.config import settings
from app.api.health import router as health_router
from app.api.ask import router as ask_router
from app.api.ingest import router as ingest_router
from app.api.process import router as process_router
from app.api.embed import router as embed_router

@asynccontextmanager
async def lifespan(_: FastAPI):
    """Pre-load the embedding model before serving requests."""
    try:
        from app.services.retriever import _get_model
        _get_model()
        print("Embedding model pre-loaded successfully")
    except Exception as error:
        print(f"Failed to pre-load embedding model: {error}")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, tags=["Health"])
app.include_router(ask_router, prefix="/api", tags=["Ask"])
app.include_router(ingest_router, prefix="/api", tags=["Ingest"])
app.include_router(process_router, prefix="/api", tags=["Process"])
app.include_router(embed_router, prefix="/api", tags=["Embed"])

FRONTEND_INDEX = Path(__file__).resolve().parents[1] / "frontend" / "index.html"

@app.get("/")
def root():
    return {
        "project": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "message": "Welcome to the Clinical Guideline QA System API"
    }


@app.get("/ui")
def ui():
    return FileResponse(FRONTEND_INDEX)