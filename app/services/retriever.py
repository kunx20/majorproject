from pathlib import Path
import json
import re
import hashlib
import faiss
import numpy as np
from rank_bm25 import BM25Okapi
from langchain_community.vectorstores import FAISS as LangChainFAISS
from app.core.paths import data_path

# Global caches for performance
_model = None
_embeddings = None
_bm25_cache = None
_metadata_cache = None
_documents_cache = None

RETRIEVAL_STOPWORDS = {
    "what", "when", "where", "why", "how", "is", "are", "the", "a", "an",
    "for", "with", "without", "should", "can", "could", "would", "do", "does",
    "did", "first", "line", "treatment", "question", "answer", "main", "point",
    "guide", "guidelines", "general", "medical", "information", "patient", "health",
    "about", "this", "that", "there", "these", "those", "more", "most", "into",
    "from", "of", "on", "in", "to", "be", "it", "as", "or", "and", "not", "used",
    "provide", "provided", "signs", "symptoms", "common", "related", "condition",
    "conditions",
}


class _FallbackSentenceTransformer:
    """Deterministic fallback for environments where sentence-transformers cannot be imported."""

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
    """Lazy load SentenceTransformer model only when needed; fall back if unavailable."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception:
            _model = _FallbackSentenceTransformer()
    return _model


def _get_embeddings():
    """Lazy load HuggingFaceEmbeddings only when needed."""
    global _embeddings
    if _embeddings is None:
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            _embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        except Exception:
            _embeddings = None
    return _embeddings

def _build_bm25_index(documents):
    """Build BM25 index with caching"""
    global _bm25_cache, _documents_cache
    if _bm25_cache is None or _documents_cache != documents:
        tokenized_docs = [tokenize(doc) for doc in documents]
        _bm25_cache = BM25Okapi(tokenized_docs)
        _documents_cache = documents
    return _bm25_cache

FAISS_DIR = data_path("faiss_index")
EMBEDDINGS_DIR = data_path("embeddings")

def tokenize(text: str):
    return [
        token
        for token in re.findall(r"\b\w+\b", text.lower())
        if token not in RETRIEVAL_STOPWORDS
    ]

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
    bm25 = _build_bm25_index(documents)
    query_tokens = tokenize(query)
    query_token_set = set(query_tokens)
    bm25_scores = bm25.get_scores(query_tokens)

    results = []
    try:
        model = _get_model()
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

        # Keep exact keyword matches in the pool; semantic search can otherwise
        # discard clinically important chunks that contain the queried term.
        keyword_indices = np.argsort(bm25_scores)[::-1][: min(10, len(metadata))]
        candidate_by_index = {item["idx"]: item for item in semantic_candidates}
        for idx in keyword_indices:
            idx = int(idx)
            if idx in candidate_by_index:
                continue
            candidate_by_index[idx] = {
                "idx": idx,
                "distance": None,
                "text": metadata[idx]["text"],
                "chunk_id": metadata[idx]["chunk_id"],
                "start_word": metadata[idx]["start_word"],
                "end_word": metadata[idx]["end_word"],
            }
        semantic_candidates = list(candidate_by_index.values())

        semantic_distances = [
            item["distance"] for item in semantic_candidates if item["distance"] is not None
        ]
        semantic_similarity = 1 / (1 + np.array(semantic_distances, dtype="float32"))
        semantic_norm = normalize_scores(semantic_similarity)
        semantic_by_index = {
            item["idx"]: float(score)
            for item, score in zip(
                [item for item in semantic_candidates if item["distance"] is not None],
                semantic_norm,
            )
        }

        bm25_candidate_scores = [bm25_scores[item["idx"]] for item in semantic_candidates]
        bm25_norm = normalize_scores(bm25_candidate_scores)

        for i, item in enumerate(semantic_candidates):
            semantic_score = semantic_by_index.get(item["idx"], 0.0)
            document_tokens = set(tokenize(item["text"]))
            exact_coverage = (
                len(query_token_set & document_tokens) / len(query_token_set)
                if query_token_set
                else 0.0
            )
            if exact_coverage:
                hybrid_score = (
                    0.1 * semantic_score
                    + 0.4 * float(bm25_norm[i])
                    + 0.5 * exact_coverage
                )
            else:
                hybrid_score = 0.7 * semantic_score + 0.3 * float(bm25_norm[i])

            results.append({
                "rank": 0,
                "chunk_id": item["chunk_id"],
                "text": item["text"],
                "start_word": item["start_word"],
                "end_word": item["end_word"],
                "semantic_score": semantic_score,
                "keyword_score": float(bm25_norm[i]),
                "exact_coverage": exact_coverage,
                "hybrid_score": hybrid_score,
                "score": hybrid_score
            })
    except Exception as exc:
        print(f"✗ Warning: semantic retrieval unavailable, using BM25-only fallback: {exc}")
        ranked_indices = np.argsort(bm25_scores)[::-1][:top_k]

        for idx in ranked_indices:
            if idx >= len(metadata):
                continue
            keyword_score = float(bm25_scores[idx])
            item = metadata[idx]
            results.append({
                "rank": 0,
                "chunk_id": item["chunk_id"],
                "text": item["text"],
                "start_word": item["start_word"],
                "end_word": item["end_word"],
                "semantic_score": 0.0,
                "keyword_score": keyword_score,
                "hybrid_score": keyword_score,
                "score": keyword_score
            })

    if any(item.get("exact_coverage", 0.0) > 0 for item in results):
        results.sort(
            key=lambda x: (
                x.get("exact_coverage", 0.0),
                x.get("keyword_score", 0.0),
                x.get("semantic_score", 0.0),
            ),
            reverse=True,
        )
    else:
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
        embeddings = _get_embeddings()
        self.vectorstore = LangChainFAISS.from_texts(chunks, embeddings)

    def search(self, query, top_k=3):
        """Search for similar chunks using similarity search"""
        if self.vectorstore is None:
            raise ValueError("Vectorstore not initialized. Call build_index first.")
        return self.vectorstore.similarity_search(query, k=top_k)
