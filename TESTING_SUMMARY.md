# Testing Strategy Summary

## What Was Added

I've created a comprehensive testing framework with **both White Box and Black Box tests** for your Clinical Guideline QA System.

### New Test Files Created

1. **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Detailed documentation explaining:
   - White box vs black box testing concepts
   - Examples for each type
   - Best practices and patterns
   - How to organize tests

2. **[tests/test_black_box_api.py](tests/test_black_box_api.py)** - 21 Black Box Tests
   - API endpoint validation
   - Response contract verification
   - Error handling
   - End-to-end workflows

3. **[tests/test_white_box_logic.py](tests/test_white_box_logic.py)** - 20 White Box Tests
   - Internal algorithm verification
   - Data structure validation
   - Code path testing
   - State management

4. **[TEST_QUICK_REFERENCE.md](TEST_QUICK_REFERENCE.md)** - Quick reference for:
   - Running tests
   - Test patterns
   - Common assertions
   - Debugging tips

---

## Testing Overview

### Black Box Testing (21 tests)
**Tests external API behavior without knowing implementation**

```
TestRootEndpoint (2 tests)
├─ Root endpoint is accessible
└─ Returns project information

TestHealthEndpoint (2 tests)
├─ Returns 200 status
└─ Has expected response format

TestAskEndpoint (5 tests)
├─ Valid questions return answers
├─ Response format correct
├─ Missing fields rejected (422)
├─ Empty questions rejected
└─ Dangerous queries handled

TestIngestEndpoint (4 tests)
├─ Endpoint accessible
├─ Accepts file uploads
├─ Rejects missing files
└─ Returns metadata

TestProcessEndpoint (2 tests)
TestEmbedEndpoint (2 tests)

TestErrorHandling (3 tests)
├─ Invalid endpoints → 404
├─ Wrong methods → 405
└─ Malformed JSON → 422

TestWorkflows (1 test)
└─ Complete QA workflow (ingest → ask)
```

### White Box Testing (20 tests)
**Tests internal implementation, algorithms, and logic**

```
TestChunkerInternals (5 tests)
├─ Initialization state
├─ Output data structure
├─ Chunk size constraints
├─ Overlap algorithm
└─ Metadata attachment

TestCleanerInternals (4 tests)
├─ Page break removal
├─ Whitespace normalization
├─ Key term extraction
└─ Section splitting

TestSafetyLogicBranches (6 tests)
├─ Emergency keyword detection
├─ Safe query detection
├─ Borderline cases
├─ Empty string handling
├─ Query normalization
└─ Special character handling

TestDataValidation (3 tests)
├─ None metadata handling
├─ Unicode text handling
└─ Various newline styles

TestInternalStateManagement (2 tests)
├─ Chunker state isolation
└─ Cleaner instance independence
```

---

## Quick Start

### Run All Tests
```bash
pytest tests/ -v
```

### Run Black Box Tests Only
```bash
pytest tests/test_black_box_api.py -v
```

### Run White Box Tests Only
```bash
pytest tests/test_white_box_logic.py tests/test_chunking.py tests/test_safety.py -v
```

### Get Coverage Report
```bash
pytest tests/ --cov=app --cov-report=html
```

---

## Key Differences: Black Box vs White Box

| Aspect | Black Box | White Box |
|--------|-----------|-----------|
| **Perspective** | User/API consumer | Developer/implementation |
| **What Tests** | API behavior, contracts | Internal logic, algorithms |
| **Tools** | TestClient, HTTP requests | Direct imports, unit tests |
| **Focus** | Response status, format | Data structures, code paths |
| **Example** | "Does /api/ask return answer?" | "Do chunks respect size limit?" |
| **Files** | `test_black_box_api.py` | `test_white_box_logic.py` |

### Example Test Comparison

**Black Box** (What users see):
```python
def test_ask_with_valid_question():
    response = client.post(
        "/api/ask",
        json={"question": "What treatment?"}
    )
    assert response.status_code == 200
    assert "answer" in response.json()
```

**White Box** (Internal verification):
```python
def test_chunk_output_structure():
    chunks = chunker.chunk_text(text)
    assert set(chunks[0].keys()) == {'text', 'metadata'}
    assert isinstance(chunks[0]['metadata']['chunk_id'], (int, str))
```

---

## Test Coverage

### Black Box Coverage
✅ All public API endpoints
✅ Success cases (valid input)
✅ Error cases (invalid input)
✅ Dangerous input handling
✅ End-to-end workflows

### White Box Coverage
✅ Text chunking algorithm
✅ Text cleaning logic
✅ Safety checks
✅ Data structure validation
✅ Edge cases (unicode, empty strings)
✅ State management

---

## Next Steps

1. **Review the guides**:
   - [TESTING_GUIDE.md](TESTING_GUIDE.md) - Full explanation
   - [TEST_QUICK_REFERENCE.md](TEST_QUICK_REFERENCE.md) - Quick reference

2. **Run the tests**:
   ```bash
   pytest tests/ -v
   ```

3. **Add more tests as needed**:
   - For new endpoints, add black box tests
   - For new algorithms, add white box tests
   - Follow the patterns in the created files

4. **Check coverage**:
   ```bash
   pytest tests/ --cov=app
   ```
   - Goal: 70%+ coverage before production
   - Focus on critical paths first

---

## Test Organization Structure

```
tests/
├── test_black_box_api.py          ← NEW: API behavior tests (21 tests)
├── test_white_box_logic.py        ← NEW: Internal logic tests (20 tests)
├── test_chunking.py               (existing white box)
├── test_embedding.py              (existing white box)
├── test_safety.py                 (existing white box)
├── test_ingest.py                 (existing)
├── test_retriever.py              (existing)
└── test_main.py                   (existing - can enhance)

docs/
├── TESTING_GUIDE.md               ← NEW: Complete testing guide
├── TEST_QUICK_REFERENCE.md        ← NEW: Quick reference
└── (other guides)
```

---

## Testing Philosophy

**Comprehensive Coverage** = Black Box + White Box
- **Black Box**: Ensures API works correctly from user perspective
- **White Box**: Ensures internal logic is correct and efficient
- **Together**: Confident the system works correctly at all levels

---

For detailed explanations, see [TESTING_GUIDE.md](TESTING_GUIDE.md)
For quick commands, see [TEST_QUICK_REFERENCE.md](TEST_QUICK_REFERENCE.md)
