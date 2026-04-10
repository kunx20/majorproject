from pydantic import BaseModel

class IngestResponse(BaseModel):
    filename: str
    saved_path: str
    extracted_text_path: str
    message: str
    status: str