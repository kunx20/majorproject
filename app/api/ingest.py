from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.ingest import IngestResponse
from app.services.parser import extract_text_from_pdf

router = APIRouter()

RAW_DIR = Path("data/raw_guidelines")
PROCESSED_DIR = Path("data/processed")

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/ingest", response_model=IngestResponse)
async def ingest_guideline(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    file_path = RAW_DIR / file.filename

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    extracted_text = extract_text_from_pdf(str(file_path))

    output_filename = file.filename.replace(".pdf", ".txt")
    output_path = PROCESSED_DIR / output_filename

    with open(output_path, "w", encoding="utf-8") as txt_file:
        txt_file.write(extracted_text)

    return IngestResponse(
        filename=file.filename,
        saved_path=str(file_path),
        extracted_text_path=str(output_path),
        message="Guideline uploaded and text extracted successfully.",
        status="success"
    )