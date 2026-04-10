# App API

A FastAPI-based application with health checks and question answering endpoints.

## Project Structure

```
app/
├── __init__.py
├── main.py                 # FastAPI application entry point
├── core/
│   ├── __init__.py
│   └── config.py          # Configuration management
├── api/
│   ├── __init__.py
│   ├── health.py          # Health check endpoints
│   └── ask.py             # Question answering endpoints
└── schemas/
    ├── __init__.py
    └── ask.py             # Pydantic models
tests/
└── test_main.py           # Unit tests
requirements.txt           # Project dependencies
.env                       # Environment variables
README.md                  # This file
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env`

3. Run the application:
```bash
uvicorn app.main:app --reload
```

4. Run tests:
```bash
pytest
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health/` - Health check
- `POST /ask/` - Ask a question
