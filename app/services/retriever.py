from pathlib import Path
import json
import re
import faiss
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS as LangChainFAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

FAISS_DIR = Path("data/faiss_index")
EMBEDDINGS_DIR = Path("data/embeddings")

def tokenize(text: str):
    return re.findall(r"\b\w+\b", text.lower())

def normalize_scores(scores):
    scores = np.array(scores, dtype="float32")
    if len(scores) == 0:
        return scores
    min_v = float(scores.min())
    max_v = float(scores.max())
    if max_v - min_v == 0:
        return np.ones_like(scores)
    return (scores - min_v) / (max_v - min_v)

def retrieve_top_chunks(query: str, index_filename: str, metadata_filename: str, top_k: int = 5):
    index_path = FAISS_DIR / index_filename
    metadata_path = EMBEDDINGS_DIR / metadata_filename

    if not index_path.exists():
        raise FileNotFoundError(f"FAISS index file not found: {index_path}")

    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

    index = faiss.read_index(str(index_path))

    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    documents = [item["text"] for item in metadata]

    query_embedding = model.encode([query]).astype("float32")
    distances, indices = index.search(query_embedding, min(10, len(documents)))

    semantic_candidates = []
    for rank, idx in enumerate(indices[0]):
        if idx < len(metadata):
            semantic_candidates.append({
                "idx": int(idx),
                "distance": float(distances[0][rank]),
                "text": metadata[idx]["text"],
                "chunk_id": metadata[idx]["chunk_id"],
                "start_word": metadata[idx]["start_word"],
                "end_word": metadata[idx]["end_word"]
            })

    tokenized_docs = [tokenize(doc) for doc in documents]
    bm25 = BM25Okapi(tokenized_docs)
    query_tokens = tokenize(query)
    bm25_scores = bm25.get_scores(query_tokens)

    semantic_distances = [item["distance"] for item in semantic_candidates]
    semantic_similarity = 1 / (1 + np.array(semantic_distances, dtype="float32"))
    semantic_norm = normalize_scores(semantic_similarity)

    bm25_candidate_scores = [bm25_scores[item["idx"]] for item in semantic_candidates]
    bm25_norm = normalize_scores(bm25_candidate_scores)

    results = []
    for i, item in enumerate(semantic_candidates):
        hybrid_score = 0.7 * float(semantic_norm[i]) + 0.3 * float(bm25_norm[i])

        results.append({
            "rank": 0,
            "chunk_id": item["chunk_id"],
            "text": item["text"],
            "start_word": item["start_word"],
            "end_word": item["end_word"],
            "semantic_score": float(semantic_norm[i]),
            "keyword_score": float(bm25_norm[i]),
            "hybrid_score": hybrid_score,
            "score": hybrid_score
        })

    results.sort(key=lambda x: x["hybrid_score"], reverse=True)

    for i, item in enumerate(results):
        item["rank"] = i + 1

    return results[:top_k]


class GuidelineRetriever:
    """LangChain-based retriever for clinical guidelines using FAISS"""
    def __init__(self):
        self.vectorstore = None

    def build_index(self, chunks):
        """Build FAISS index from text chunks"""
        self.vectorstore = LangChainFAISS.from_texts(chunks, embeddings)

    def search(self, query, top_k=3):
        """Search for similar chunks using similarity search"""
        if self.vectorstore is None:
            raise ValueError("Vectorstore not initialized. Call build_index first.")
        return self.vectorstore.similarity_search(query, k=top_k)
