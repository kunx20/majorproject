from pathlib import Path

def extract_text_from_pdf(pdf_path: str) -> str:
    file_path = Path(pdf_path)

    try:
        import fitz
    except Exception as exc:
        raise RuntimeError(
            "PDF parsing is unavailable because PyMuPDF could not be imported. "
            "Install a compatible PyMuPDF build for this Python version to enable ingestion."
        ) from exc

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {pdf_path}")

    doc = fitz.open(file_path)
    pages_text = []

    for page_number, page in enumerate(doc, start=1):
        text = page.get_text("text")
        cleaned_text = text.strip()
        pages_text.append(f"\n--- Page {page_number} ---\n{cleaned_text}")

    doc.close()

    return "\n".join(pages_text).strip()