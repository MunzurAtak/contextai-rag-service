# ContextAI RAG Service

A Retrieval-Augmented Generation (RAG) service for context-aware AI applications.

## Overview

This service provides a complete RAG pipeline including document ingestion, embedding generation, vector storage, and LLM-based retrieval and generation.

## Project Structure

- `app/` - Core application modules
  - `main.py` - FastAPI application entry point
  - `rag.py` - RAG pipeline orchestration
  - `embeddings.py` - Embedding generation
  - `retrieval.py` - Document retrieval logic
  - `llm.py` - LLM integration
  - `schemas.py` - Pydantic models
  - `config.py` - Configuration management
- `data/` - Data storage directory
  - `uploads/` - Uploaded documents
- `vectorstore/` - Vector database storage
- `models/` - Pre-trained models
- `tests/` - Test suite

## Getting Started

### Installation

```bash
pip install -r requirements.txt
```

### Running the Service

```bash
uvicorn app.main:app --reload
```

The service will be available at `http://localhost:8000`

### Docker

```bash
docker build -t contextai-rag .
docker run -p 8000:8000 contextai-rag
```

## API Endpoints

(To be documented)

## Configuration

Configuration is managed through environment variables and `app/config.py`.

## License

MIT
