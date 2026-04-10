from pathlib import Path
import json
from fastapi import APIRouter, HTTPException
from app.services.cleaner import clean_extracted_text
from app.services.chunker import chunk_text

router = APIRouter()

PROCESSED_DIR = Path("data/processed")
CHUNKS_DIR = Path("data/chunks")
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/process/{filename}")
def process_guideline(filename: str):
    input_path = PROCESSED_DIR / filename

    if not input_path.exists():
        raise HTTPException(status_code=404, detail="Processed text file not found.")

    with open(input_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    cleaned_text = clean_extracted_text(raw_text)
    chunks = chunk_text(cleaned_text, chunk_size=300, overlap=50)

    output_filename = filename.replace(".txt", "_chunks.json")
    output_path = CHUNKS_DIR / output_filename

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=4, ensure_ascii=False)

    return {
        "filename": filename,
        "chunks_file": str(output_path),
        "total_chunks": len(chunks),
        "message": "Text cleaned and chunked successfully.",
        "status": "success"
    }