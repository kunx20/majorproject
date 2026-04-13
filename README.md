# Clinical Guideline QA System

A FastAPI-based intelligent question-answering system that retrieves evidence-based answers from clinical guidelines using hybrid retrieval (semantic + BM25) with safety guardrails.

## Features

✨ **Evidence-Based Retrieval** - Uses FAISS vector database + BM25 hybrid search  
🔒 **Safety Guardrails** - Detects unsafe medical queries and emergency situations  
📄 **Smart Text Simplification** - Converts complex medical terminology to simple language  
🎯 **Citation Support** - Returns source chunks with relevant passages  
⚡ **Fast API** - Built with FastAPI for high-performance async endpoints  

## Project Structure

```
clinical_guideline_QA/
├── app/
│   ├── main.py                    # FastAPI application entry point
│   ├── api/
│   │   ├── ask.py                # Question answering endpoint
│   │   ├── health.py             # Health check endpoint
│   │   ├── ingest.py             # Guideline ingestion
│   │   ├── process.py            # Text processing
│   │   ├── embed.py              # Embedding generation
│   │   └── __init__.py
│   ├── core/
│   │   ├── config.py             # Configuration settings
│   │   ├── safety.py             # Safety checks & guardrails
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── ask.py                # Request/response models
│   │   ├── ingest.py             # Ingestion models
│   │   └── __init__.py
│   └── services/
│       ├── retriever.py          # Hybrid search & retrieval
│       ├── chunker.py            # Text chunking
│       ├── cleaner.py            # Text cleaning
│       ├── embedder.py           # Embedding generation
│       ├── parser.py             # Document parsing
│       └── __init__.py
├── data/
│   ├── raw_guidelines/           # Original documents
│   ├── processed/                # Cleaned text
│   ├── chunks/                   # Text chunks
│   ├── embeddings/               # Vector embeddings + metadata
│   └── faiss_index/              # FAISS vector indices
├── frontend/
│   └── index.html                # Interactive web UI
├── tests/                        # Test suite (19 tests)
│   ├── test_chunking.py
│   ├── test_embedding.py
│   ├── test_ingest.py
│   ├── test_main.py
│   ├── test_retriever.py
│   └── test_safety.py
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignore rules
├── .env.example                  # Environment template
└── README.md                     # This file
```

## Installation

### Prerequisites
- Python 3.10+
- pip or conda

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/YOUR_USERNAME/clinical-guideline-QA.git
cd clinical-guideline-QA
```

2. **Create a virtual environment:**
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your settings
```

## Usage

### Start the API Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Access the interactive API docs at: `http://localhost:8000/docs`

### Run Tests

```bash
pytest tests/ -v
```

All 19 tests passing ✅

### Access the Web Interface

Open `frontend/index.html` in your browser for the interactive Q&A interface.

## API Endpoints

### Health Check
```
GET /health/
```
Response: `{"status": "ok"}`

### Ask Question
```
POST /api/ask
Content-Type: application/json

{
  "question": "What is the first-line treatment for hypertension?"
}
```

Response:
```json
{
  "question": "What is the first-line treatment for hypertension?",
  "answer": "For high blood pressure treatment: [simplified answer]",
  "citations": [
    {
      "source": "standard-treatment-guidelines",
      "section": "Chunk 1",
      "text": "[relevant excerpt]"
    }
  ],
  "status": "success"
}
```

### Ingest Guideline
```
POST /api/ingest
Content-Type: multipart/form-data
```

### Generate Embeddings
```
POST /api/embed
```

## Technical Stack

- **Backend**: FastAPI, Uvicorn
- **Search**: FAISS (semantic) + BM25 (keyword)
- **Embeddings**: Sentence-Transformers (all-MiniLM-L6-v2)
- **Data Processing**: NumPy, scikit-learn
- **Safety**: Custom medical query detection
- **Testing**: pytest
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript

## Key Components

### Hybrid Retrieval System
- **Semantic Search**: FAISS vector similarity (70% weight)
- **Keyword Search**: BM25 ranking (30% weight)
- **Normalization**: Min-max scaling for score alignment

### Safety Guardrails
- Emergency detection (chest pain, choking, etc.)
- Unsupported diagnosis prevention
- Medical-only query validation

### Text Simplification
- Medical terminology → layman's terms
- Automatic abbreviation expansion
- Enhanced readability

## Testing

The project includes comprehensive tests:
- ✅ Text chunking and metadata
- ✅ Embedding generation
- ✅ Guideline ingestion
- ✅ API endpoints
- ✅ Retrieval ranking
- ✅ Safety checks

Run tests with coverage:
```bash
pytest tests/ -v --cov=app
```

## Environment Variables

Create a `.env` file:
```
APP_NAME=Clinical Guideline QA System
APP_VERSION=1.0.0
DEBUG=True
FAISS_INDEX_PATH=data/faiss_index
EMBEDDINGS_PATH=data/embeddings
```

## Deployment

### Docker (Optional)
```bash
docker build -t clinical-qa .
docker run -p 8000:8000 clinical-qa
```

### Production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Provide detailed reproduction steps

## Roadmap

- [ ] Multi-language support
- [ ] PDF upload support
- [ ] Advanced query understanding
- [ ] User feedback loop
- [ ] Analytics dashboard
