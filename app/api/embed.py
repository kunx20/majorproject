import json
from fastapi import APIRouter, HTTPException
from app.core.paths import data_path, safe_filename

router = APIRouter()

CHUNKS_DIR = data_path("chunks")
EMBEDDINGS_DIR = data_path("embeddings")
FAISS_DIR = data_path("faiss_index")

@router.post("/embed/{filename}")
def embed_guideline(filename: str):
    return {
        "message": "Vector embeddings are disabled in serverless mode.",
        "status": "disabled",
    }