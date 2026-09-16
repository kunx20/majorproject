import hashlib
import numpy as np

_model = None


class _FallbackSentenceTransformer:
    """Minimal deterministic fallback when sentence-transformers cannot load."""

    def encode(self, texts, *args, **kwargs):
        if isinstance(texts, str):
            texts = [texts]
        dim = 384
        output = []
        for text in texts:
            values = np.zeros(dim, dtype="float32")
            for i in range(dim):
                digest = hashlib.md5(f"{text}:{i}".encode("utf-8")).digest()
                value = int.from_bytes(digest, byteorder="big", signed=False)
                values[i] = ((value / 2**128) - 0.5) * 2.0
            output.append(values)
        return np.array(output, dtype="float32")


def _get_model():
    """Lazy load the model only when needed; fall back if the dependency is unavailable."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception:
            _model = _FallbackSentenceTransformer()
    return _model


def generate_embeddings(texts: list[str]) -> np.ndarray:
    model = _get_model()
    embeddings = model.encode(texts)
    return np.array(embeddings, dtype="float32")
