import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Clinical Guideline QA System")
    APP_VERSION: str = os.getenv("APP_VERSION", "0.1.0")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Ollama settings
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "neural-chat")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    USE_LLM: bool = os.getenv("USE_LLM", "true").lower() == "true"
    
    # GPU acceleration settings
    ENABLE_GPU: bool = os.getenv("ENABLE_GPU", "true").lower() == "true"
    NUM_GPU_LAYERS: int = int(os.getenv("NUM_GPU_LAYERS", "20"))  # Number of layers to offload to GPU
    NUM_THREADS: int = int(os.getenv("NUM_THREADS", "4"))  # CPU threads for parallel processing

settings = Settings()