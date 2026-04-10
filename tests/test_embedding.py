import pytest
import numpy as np
from app.services.embedder import generate_embeddings
import tempfile
import json
import os

def test_generate_embeddings():
    texts = ["This is a test sentence.", "Another test sentence."]
    embeddings = generate_embeddings(texts)
    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape[0] == len(texts)
    assert embeddings.dtype == np.float32

def test_numpy_array_creation():
    arr = np.array([[1.0, 2.0], [3.0, 4.0]], dtype="float32")
    assert arr.shape == (2, 2)
    assert arr.dtype == np.float32
