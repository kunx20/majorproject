from fastapi import APIRouter, UploadFile, File, HTTPException
from app.core.config import settings
from app.core.paths import data_path, safe_filename
from app.schemas.ingest import IngestResponse
from app.services.parser import extract_text_from_pdf

router = APIRouter()

RAW_DIR = data_path("raw_guidelines")
PROCESSED_DIR = data_path("processed")

@router.post("/ingest", response_model=IngestResponse)
async def ingest_guideline(file: UploadFile = File(...)):
    filename = safe_filename(file.filename or "", ".pdf")
    file_path = RAW_DIR / filename

    total_bytes = 0
    try:
        with file_path.open("wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                total_bytes += len(chunk)
                if total_bytes > settings.MAX_UPLOAD_BYTES:
                    raise HTTPException(status_code=413, detail="Uploaded file is too large.")
                buffer.write(chunk)

        extracted_text = extract_text_from_pdf(str(file_path))
        output_path = PROCESSED_DIR / f"{file_path.stem}.txt"
        output_path.write_text(extracted_text, encoding="utf-8")
    except HTTPException:
        file_path.unlink(missing_ok=True)
        raise
    except Exception as error:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="Could not parse the PDF file.") from error

    return IngestResponse(
        filename=filename,
        saved_path=str(file_path),
        extracted_text_path=str(output_path),
        message="Guideline uploaded and text extracted successfully.",
        status="success"
    )