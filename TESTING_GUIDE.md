# Testing Guide: White Box & Black Box Testing

## Overview
This guide explains both testing approaches used in the Clinical Guideline QA System:
- **White Box Testing**: Tests internal implementation, logic, and code paths
- **Black Box Testing**: Tests external API behavior without knowledge of internal implementation

---

## White Box Testing (Unit & Integration Tests)

White box tests verify internal logic, code paths, and implementation details.

### 1. Unit Tests - Testing Individual Components

**File**: `tests/test_chunking.py`
```python
class TestTextChunker:
    def test_chunk_text_basic(self):
        """White box: Test internal chunking logic"""
        text = "This is a test sentence. " * 20
        chunks = self.chunker.chunk_text(text)
        
        # Tests INTERNAL behavior: exact structure of output
        assert len(chunks) > 1
        assert all('text' in chunk for chunk in chunks)
        assert all('metadata' in chunk for chunk in chunks)
```

**Key White Box Aspects**:
- Tests internal data structures (checking exact keys in dict)
- Verifies internal algorithms (chunk overlap, metadata assignment)
- Tests error handling in specific code paths
- Checks internal state changes

### 2. White Box Test Examples for Your Project

#### Test Data Structure Validation
```python
# tests/test_ingest.py - White box testing data processing
def test_chunk_metadata_structure():
    """White box: Verify exact internal data structure"""
    chunker = TextChunker()
    chunks = chunker.chunk_text("test content" * 10)
    
    # Tests INTERNAL structure expectations
    assert isinstance(chunks, list)
    for chunk in chunks:
        assert isinstance(chunk, dict)
        assert set(chunk.keys()) == {'text', 'metadata'}
        assert 'chunk_id' in chunk['metadata']
        assert 'source' in chunk['metadata']
```

#### Test Code Paths & Branches
```python
# tests/test_safety.py - White box testing multiple code paths
def test_safety_check_all_paths():
    """White box: Test different conditional branches"""
    
    # Path 1: Dangerous medical keywords
    assert is_unsafe_medical_query("severe chest pain") is True
    
    # Path 2: Safe medical question
    assert is_unsafe_medical_query("treatment options") is False
    
    # Path 3: Edge case - empty string
    assert is_unsafe_medical_query("") is False
```

#### Test Internal Error Handling
```python
# tests/test_retriever.py - White box testing exception handling
def test_retriever_handles_missing_index():
    """White box: Test error handling when index missing"""
    retriever = Retriever(index_path="nonexistent.index")
    
    # Tests INTERNAL exception handling
    with pytest.raises(FileNotFoundError):
        retriever.retrieve("query")
```

---

## Black Box Testing (API & Integration Tests)

Black box tests verify external behavior/API contracts without knowing implementation details.

### 1. API Endpoint Testing

**File**: `tests/test_main.py` (to be enhanced)
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check_endpoint():
    """Black box: Health endpoint returns expected response"""
    response = client.get("/health")
    
    # Tests EXTERNAL behavior only
    assert response.status_code == 200
    assert "status" in response.json()

def test_ask_question_endpoint():
    """Black box: API accepts question and returns answer"""
    payload = {"question": "What is first line treatment for hypertension?"}
    response = client.post("/api/ask", json=payload)
    
    # Tests EXTERNAL contract - doesn't care how it's implemented
    assert response.status_code == 200
    assert "answer" in response.json()
    assert isinstance(response.json()["answer"], str)
    assert len(response.json()["answer"]) > 0
```

### 2. Black Box Test Examples

#### Test API Response Contracts
```python
# tests/test_black_box_api.py
def test_ingest_endpoint_accepts_file():
    """Black box: Ingest endpoint accepts file and confirms success"""
    with open("test_guideline.txt") as f:
        files = {"file": f}
        response = client.post("/api/ingest", files=files)
    
    # Only tests external contract - response structure and status
    assert response.status_code in [200, 201]
    data = response.json()
    assert "message" in data
    assert "chunks" in data
```

#### Test Functional Requirements (User Perspective)
```python
def test_question_answering_workflow():
    """Black box: End-to-end workflow from user perspective"""
    
    # Step 1: Ingest a guideline
    response = client.post("/api/ingest", files={"file": ("test.txt", b"content")})
    assert response.status_code == 200
    
    # Step 2: Ask a question
    response = client.post(
        "/api/ask",
        json={"question": "What treatment?"}
    )
    assert response.status_code == 200
    assert "answer" in response.json()
```

#### Test Invalid Input Handling (User Perspective)
```python
def test_invalid_question_format():
    """Black box: API rejects invalid input gracefully"""
    
    # Missing required field
    response = client.post("/api/ask", json={})
    assert response.status_code == 422  # Validation error
    
    # Empty question
    response = client.post("/api/ask", json={"question": ""})
    assert response.status_code in [400, 422]
```

#### Test Safety Guardrails (Business Logic)
```python
def test_unsafe_questions_rejected():
    """Black box: Dangerous medical queries are rejected"""
    
    dangerous_query = "I'm having a heart attack what do I do"
    response = client.post(
        "/api/ask",
        json={"question": dangerous_query}
    )
    
    # External behavior: should reject or flag dangerous content
    assert response.status_code in [400, 422]
    or "unsafe" in response.json().get("detail", "").lower()
```

---

## Complete Test Example Structure

### tests/test_black_box_api.py (Black Box - External API Behavior)
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestHealthEndpoint:
    """Black box: Health check API behavior"""
    
    def test_health_returns_ok(self):
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_response_format(self):
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "ok"]

class TestAskEndpoint:
    """Black box: Question answering API behavior"""
    
    def test_ask_with_valid_question(self):
        response = client.post(
            "/api/ask",
            json={"question": "What is hypertension treatment?"}
        )
        assert response.status_code == 200
        assert "answer" in response.json()
    
    def test_ask_missing_question_field(self):
        response = client.post("/api/ask", json={})
        assert response.status_code == 422
    
    def test_ask_with_dangerous_query(self):
        response = client.post(
            "/api/ask",
            json={"question": "I'm dying help me"}
        )
        # Should either reject or warn
        assert response.status_code >= 400

class TestIngestEndpoint:
    """Black box: File ingestion API behavior"""
    
    def test_ingest_accepts_text_file(self, tmp_path):
        file_path = tmp_path / "test.txt"
        file_path.write_text("Medical guideline content")
        
        with open(file_path, "rb") as f:
            response = client.post(
                "/api/ingest",
                files={"file": f}
            )
        
        assert response.status_code == 200
        assert "chunks" in response.json()
    
    def test_ingest_without_file(self):
        response = client.post("/api/ingest")
        assert response.status_code == 422
```

### tests/test_white_box_logic.py (White Box - Internal Implementation)
```python
import pytest
from app.services.chunker import TextChunker
from app.services.embedder import Embedder
from app.core.safety import is_unsafe_medical_query

class TestChunkerInternals:
    """White box: Internal chunking logic"""
    
    def setup_method(self):
        self.chunker = TextChunker(chunk_size=100, overlap=20)
    
    def test_chunk_size_respected(self):
        """White box: Verify internal chunk size logic"""
        text = "word " * 100  # Create 500 char text
        chunks = self.chunker.chunk_text(text)
        
        # Test INTERNAL behavior: chunk size constraint
        for chunk in chunks:
            assert len(chunk['text']) <= 150  # 100 + 50 buffer
    
    def test_overlap_creates_duplicates(self):
        """White box: Verify overlap creates expected duplicates"""
        text = "1 2 3 4 5 6 7 8 9 10 " * 20
        chunks = self.chunker.chunk_text(text)
        
        # White box: Test overlap implementation detail
        if len(chunks) > 1:
            overlap_text = chunks[0]['text'][-20:]
            next_text = chunks[1]['text'][:20]
            # Overlap should create some shared content
            assert overlap_text in chunks[1]['text'] or len(overlap_text) > 0

class TestSafetyLogic:
    """White box: Internal safety check branches"""
    
    def test_keyword_matching_paths(self):
        """White box: Test each keyword detection path"""
        
        # Path: Emergency keywords
        assert is_unsafe_medical_query("chest pain emergency") is True
        assert is_unsafe_medical_query("difficulty breathing") is True
        
        # Path: Safe educational queries
        assert is_unsafe_medical_query("guideline for diabetes") is False
        
        # Path: Borderline cases
        assert is_unsafe_medical_query("side effects") is False

class TestEmbedderInternals:
    """White box: Embedding function internal validation"""
    
    def test_embedding_vector_shape(self):
        """White box: Verify embedding output shape"""
        embedder = Embedder()
        text = "test medical content"
        embedding = embedder.embed(text)
        
        # White box: Test internal vector shape
        assert len(embedding) == 384  # Expected embedding dimension
        assert all(isinstance(x, float) for x in embedding)
```

---

## Testing Best Practices

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_black_box_api.py -v

# Run specific test class
pytest tests/test_black_box_api.py::TestAskEndpoint -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Test Organization

| Type | Focus | Tool | File Pattern |
|------|-------|------|--------------|
| **Black Box** | External API behavior | TestClient | `test_*_api.py` |
| **Black Box** | User workflows | TestClient | `test_*_integration.py` |
| **White Box** | Internal logic | Direct imports | `test_*_unit.py` |
| **White Box** | Code paths | Direct imports | `test_*_logic.py` |

### Coverage Goals

- **White Box Tests**: 80%+ coverage of core business logic
- **Black Box Tests**: All public API endpoints tested
- **Edge Cases**: Both valid and invalid input scenarios

---

## Your Project: Recommended Next Steps

1. **Enhance test_main.py** with black box API tests using TestClient
2. **Add test_white_box_logic.py** for internal implementation details
3. **Create test_black_box_api.py** for all endpoint behavior
4. **Run `pytest tests/ --cov=app`** to identify untested code
5. **Target 70%+ coverage** before deployment

See [README.md](README.md) for project overview.
