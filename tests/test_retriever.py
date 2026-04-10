import json
import tempfile
from pathlib import Path

import faiss
import numpy as np
import pytest

from app.services import retriever


def test_retrieve_top_chunks_returns_ranked_results(monkeypatch):
    with tempfile.TemporaryDirectory() as temp_dir:
        base_dir = Path(temp_dir)
        faiss_dir = base_dir / "faiss_index"
        embeddings_dir = base_dir / "embeddings"
        faiss_dir.mkdir(parents=True, exist_ok=True)
        embeddings_dir.mkdir(parents=True, exist_ok=True)

        monkeypatch.setattr(retriever, "FAISS_DIR", faiss_dir)
        monkeypatch.setattr(retriever, "EMBEDDINGS_DIR", embeddings_dir)

        metadata = [
            {"chunk_id": 1, "text": "first chunk", "start_word": 0, "end_word": 2},
            {"chunk_id": 2, "text": "second chunk", "start_word": 3, "end_word": 5},
        ]
        metadata_path = embeddings_dir / "test_metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f)

        embeddings = np.array([[1.0, 0.0], [0.0, 1.0]], dtype="float32")
        index = faiss.IndexFlatL2(2)
        index.add(embeddings)
        index_path = faiss_dir / "test.index"
        faiss.write_index(index, str(index_path))

        monkeypatch.setattr(retriever.model, "encode", lambda texts: np.array([[1.0, 0.0]], dtype="float32"))

        results = retriever.retrieve_top_chunks(
            query="query text",
            index_filename="test.index",
            metadata_filename="test_metadata.json",
            top_k=1,
        )

        assert len(results) == 1
        assert results[0]["chunk_id"] == 1
        assert results[0]["text"] == "first chunk"
        assert results[0]["rank"] == 1
        assert isinstance(results[0]["score"], float)


def test_retrieve_top_chunks_raises_file_not_found(monkeypatch):
    with tempfile.TemporaryDirectory() as temp_dir:
        base_dir = Path(temp_dir)
        monkeypatch.setattr(retriever, "FAISS_DIR", base_dir / "faiss_index")
        monkeypatch.setattr(retriever, "EMBEDDINGS_DIR", base_dir / "embeddings")

        with pytest.raises(FileNotFoundError, match="FAISS index file not found"):
            retriever.retrieve_top_chunks(
                query="query text",
                index_filename="missing.index",
                metadata_filename="missing_metadata.json",
            )

def test_basic_truth():
    assert True