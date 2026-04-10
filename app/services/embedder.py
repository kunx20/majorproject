from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def generate_embeddings(texts: list[str]) -> np.ndarray:
    embeddings = model.encode(texts)
    return np.array(embeddings, dtype="float32")
