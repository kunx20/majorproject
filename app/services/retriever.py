import json
import re
import hashlib
import numpy as np
from rank_bm25 import BM25Okapi
from app.core.paths import data_path

# Global caches for performance
_model = None
_embeddings = None
_bm25_cache = None
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

    def encode(self, texts, *_args, **_kwargs):
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
    metadata_path = EMBEDDINGS_DIR / metadata_filename

    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    documents = [item["text"] for item in metadata]
    bm25 = _build_bm25_index(documents)
    query_tokens = tokenize(query)
    query_token_set = set(query_tokens)
    bm25_scores = bm25.get_scores(query_tokens)
    ranked_indices = sorted(
        range(len(metadata)),
        key=lambda idx: float(bm25_scores[idx]),
        reverse=True,
    )[:top_k]
    results = []
    for rank, idx in enumerate(ranked_indices, start=1):
        idx = int(idx)
        if idx >= len(metadata):
            continue
        item = metadata[idx]
        document_tokens = set(tokenize(item["text"]))
        exact_coverage = (
            len(query_token_set & document_tokens) / len(query_token_set)
            if query_token_set
            else 0.0
        )
        keyword_score = float(bm25_scores[idx])
        results.append({
            "rank": rank,
            "chunk_id": item["chunk_id"],
            "text": item["text"],
            "start_word": item["start_word"],
            "end_word": item["end_word"],
            "semantic_score": 0.0,
            "keyword_score": keyword_score,
            "exact_coverage": exact_coverage,
            "hybrid_score": keyword_score,
            "score": keyword_score,
        })

    return results[:top_k]


class GuidelineRetriever:
    """LangChain-based retriever for clinical guidelines using FAISS"""
    def __init__(self):
        self.vectorstore = None

    def build_index(self, chunks):
        """Build FAISS index from text chunks"""
        from langchain_community.vectorstores import FAISS as LangChainFAISS

        embeddings = _get_embeddings()
        self.vectorstore = LangChainFAISS.from_texts(chunks, embeddings)

    def search(self, query, top_k=3):
        """Search for similar chunks using similarity search"""
        if self.vectorstore is None:
            raise ValueError("Vectorstore not initialized. Call build_index first.")
        return self.vectorstore.similarity_search(query, k=top_k)
