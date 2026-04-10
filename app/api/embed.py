from pathlib import Path
import json
import numpy as np
import faiss
from fastapi import APIRouter, HTTPException
from app.services.embedder import generate_embeddings

router = APIRouter()

CHUNKS_DIR = Path("data/chunks")
EMBEDDINGS_DIR = Path("data/embeddings")
FAISS_DIR = Path("data/faiss_index")

EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)
FAISS_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/embed/{filename}")
def embed_guideline(filename: str):
    input_path = CHUNKS_DIR / filename

    if not input_path.exists():
        raise HTTPException(status_code=404, detail="Chunks JSON file not found.")

    with open(input_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    texts = [chunk["text"] for chunk in chunks]

    if not texts:
        raise HTTPException(status_code=400, detail="No chunk texts found.")

    embeddings = generate_embeddings(texts)

    npy_filename = filename.replace(".json", "_embeddings.npy")
    npy_path = EMBEDDINGS_DIR / npy_filename
    np.save(npy_path, embeddings)

    metadata_filename = filename.replace(".json", "_metadata.json")
    metadata_path = EMBEDDINGS_DIR / metadata_filename
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=4, ensure_ascii=False)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    faiss_filename = filename.replace(".json", ".index")
    faiss_path = FAISS_DIR / faiss_filename
    faiss.write_index(index, str(faiss_path))

    return {
        "filename": filename,
        "embedding_file": str(npy_path),
        "metadata_file": str(metadata_path),
        "faiss_index_file": str(faiss_path),
        "total_chunks_embedded": len(texts),
        "embedding_dimension": dimension,
        "message": "Embeddings generated and FAISS index created successfully.",
        "status": "success"
    }