import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
    APP_NAME: str = os.getenv("APP_NAME", "Clinical Guideline QA System")
    APP_VERSION: str = os.getenv("APP_VERSION", "0.1.0")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Ollama settings
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "tinyllama")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    USE_LLM: bool = os.getenv("USE_LLM", "true").lower() == "true"
    
    # GPU acceleration settings
    ENABLE_GPU: bool = os.getenv("ENABLE_GPU", "true").lower() == "true"
    NUM_GPU_LAYERS: int = int(os.getenv("NUM_GPU_LAYERS", "20"))  # Number of layers to offload to GPU
    NUM_THREADS: int = int(os.getenv("NUM_THREADS", "4"))  # CPU threads for parallel processing
    MAX_UPLOAD_BYTES: int = int(os.getenv("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS", "http://127.0.0.1:8001,http://localhost:8001"
        ).split(",")
        if origin.strip()
    ]

settings = Settings()