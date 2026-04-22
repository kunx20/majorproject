from sentence_transformers import SentenceTransformer
import numpy as np

_model = None

def _get_model():
    """Lazy load the model only when needed"""
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def generate_embeddings(texts: list[str]) -> np.ndarray:
    model = _get_model()
    embeddings = model.encode(texts)
    return np.array(embeddings, dtype="float32")
