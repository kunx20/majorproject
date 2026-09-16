import json
import numpy as np
import faiss
from fastapi import APIRouter, HTTPException
from app.core.paths import data_path, safe_filename
from app.services.embedder import generate_embeddings

router = APIRouter()

CHUNKS_DIR = data_path("chunks")
EMBEDDINGS_DIR = data_path("embeddings")
FAISS_DIR = data_path("faiss_index")

@router.post("/embed/{filename}")
def embed_guideline(filename: str):
    filename = safe_filename(filename, ".json")
    input_path = CHUNKS_DIR / filename

    if not input_path.exists():
        raise HTTPException(status_code=404, detail="Chunks JSON file not found.")

    with open(input_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    texts = [chunk["text"] for chunk in chunks]

    if not texts:
        raise HTTPException(status_code=400, detail="No chunk texts found.")

    embeddings = generate_embeddings(texts)

    npy_filename = f"{input_path.stem}_embeddings.npy"
    npy_path = EMBEDDINGS_DIR / npy_filename
    np.save(npy_path, embeddings)

    metadata_filename = f"{input_path.stem}_metadata.json"
    metadata_path = EMBEDDINGS_DIR / metadata_filename
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=4, ensure_ascii=False)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    faiss_filename = f"{input_path.stem}.index"
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