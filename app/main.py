from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.health import router as health_router
from app.api.ask import router as ask_router
from app.api.ingest import router as ingest_router
from app.api.process import router as process_router
from app.api.embed import router as embed_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, tags=["Health"])
app.include_router(ask_router, prefix="/api", tags=["Ask"])
app.include_router(ingest_router, prefix="/api", tags=["Ingest"])
app.include_router(process_router, prefix="/api", tags=["Process"])
app.include_router(embed_router, prefix="/api", tags=["Embed"])

@app.get("/")
def root():
    return {
        "project": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "message": "Welcome to the Clinical Guideline QA System API"
    }