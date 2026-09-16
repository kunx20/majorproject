from pathlib import Path

from fastapi import HTTPException


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def data_path(directory: str) -> Path:
    path = PROJECT_ROOT / "data" / directory
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_filename(filename: str, suffix: str | None = None) -> str:
    candidate = Path(filename).name
    if not candidate or candidate in {".", ".."} or candidate != filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")
    if suffix and Path(candidate).suffix.lower() != suffix.lower():
        raise HTTPException(status_code=400, detail=f"Only {suffix.upper().lstrip('.')} files are allowed.")
    return candidate