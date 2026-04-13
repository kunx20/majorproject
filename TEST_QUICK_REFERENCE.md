# Testing Quick Reference

## File Organization

| File | Type | Focus |
|------|------|-------|
| `tests/test_black_box_api.py` | **BLACK BOX** | API endpoints, response contracts, workflows |
| `tests/test_white_box_logic.py` | **WHITE BOX** | Internal logic, algorithms, data structures |
| `tests/test_chunking.py` | WHITE BOX | Text chunking algorithms |
| `tests/test_safety.py` | WHITE BOX | Safety logic paths |
| `tests/test_embedding.py` | WHITE BOX | Embedding logic |

---

## Running Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run Only Black Box Tests (API behavior)
```bash
pytest tests/test_black_box_api.py -v
```

### Run Only White Box Tests (Internal logic)
```bash
pytest tests/test_white_box_logic.py tests/test_chunking.py tests/test_safety.py -v
```

### Run Specific Test Class
```bash
pytest tests/test_black_box_api.py::TestAskEndpoint -v
pytest tests/test_white_box_logic.py::TestChunkerInternals -v
```

### Run with Coverage Report
```bash
pytest tests/ --cov=app --cov-report=html
# Opens coverage report in htmlcov/index.html
```

### Run with Short Output
```bash
pytest tests/ -v --tb=short
```

---

## Test Types Explained

### Black Box Testing (User Perspective)
**What it tests**: External API behavior without knowing implementation
- API endpoints return expected status codes
- Response structure matches contract
- Error handling works correctly
- End-to-end workflows function
- User-visible behavior is correct

**Example**:
```python
def test_ask_endpoint_returns_answer():
    response = client.post("/api/ask", json={"question": "What is treatment?"})
    assert response.status_code == 200
    assert "answer" in response.json()
```

### White Box Testing (Developer Perspective)
**What it tests**: Internal implementation details
- Algorithms work correctly
- Data structures are as expected
- Code paths execute properly
- Edge cases are handled
- State management is correct

**Example**:
```python
def test_chunker_size_constraint():
    chunker = TextChunker(chunk_size=100, overlap=20)
    chunks = chunker.chunk_text(large_text)
    
    for chunk in chunks:
        assert len(chunk['text']) <= 120  # Internal size limit
```

---

## Test Coverage Goals

1. **Black Box**: All public API endpoints
   - Success cases
   - Error cases (invalid input, missing fields)
   - Dangerous input handling

2. **White Box**: Core business logic
   - TextChunker algorithm
   - Safety checks
   - Data validation
   - Error handling

3. **Integration**: End-to-end workflows
   - Ingest → Ask flow
   - File processing pipeline
   - Embedding → Retrieval chain

---

## Common Test Patterns

### Testing API with Valid Input (Black Box)
```python
def test_ask_endpoint():
    response = client.post(
        "/api/ask",
        json={"question": "What is treatment?"}
    )
    assert response.status_code == 200
    assert "answer" in response.json()
```

### Testing API with Invalid Input (Black Box)
```python
def test_ask_missing_field():
    response = client.post("/api/ask", json={})
    assert response.status_code == 422  # Validation error
```

### Testing Internal Data Structure (White Box)
```python
def test_chunk_structure():
    chunks = chunker.chunk_text("text")
    assert set(chunks[0].keys()) == {'text', 'metadata'}
```

### Testing Algorithm Implementation (White Box)
```python
def test_overlap_behavior():
    chunks = chunker.chunk_text(text, overlap=20)
    # Verify overlap creates continuity
    assert chunks[0]['text'][-20:] in chunks[1]['text']
```

### Testing Error Handling (White Box)
```python
def test_safety_detects_emergency():
    assert is_unsafe_medical_query("severe chest pain") is True
    assert is_unsafe_medical_query("treatment options") is False
```

---

## Debugging Tests

### Run test with print output
```bash
pytest tests/test_black_box_api.py::TestAskEndpoint::test_ask_with_valid_question -v -s
```

### Run test and show local variables on failure
```bash
pytest tests/ -v --tb=long
```

### Run single test file with verbose output
```bash
pytest tests/test_white_box_logic.py::TestChunkerInternals::test_chunk_output_structure -vv
```

---

## Test Assertions Reference

### Black Box (API Testing)
```python
# Status codes
assert response.status_code == 200
assert response.status_code in [200, 201]

# Response structure
assert "answer" in response.json()
data = response.json()
assert isinstance(data["answer"], str)

# Error handling
assert response.status_code == 422  # Validation error
assert response.status_code == 404  # Not found
```

### White Box (Logic Testing)
```python
# Data structure validation
assert isinstance(chunks, list)
assert set(chunk.keys()) == {'text', 'metadata'}

# Algorithm verification
assert len(chunks) > 1
assert chunk['metadata']['chunk_id'] is not None

# Edge cases
assert is_unsafe_medical_query("") is False
assert all(isinstance(x, float) for x in embedding)
```

---

## Before Pushing Code

1. **Run all tests**:
   ```bash
   pytest tests/ -v
   ```

2. **Check coverage**:
   ```bash
   pytest tests/ --cov=app
   ```

3. **Fix any failures**:
   - Review failed test
   - Update code or test as appropriate
   - Re-run to verify fix

4. **Commit with tests passing**:
   ```bash
   git add tests/
   git commit -m "Add black box and white box tests"
   ```
