# KnowIT - Backend

## Description
The backend for KnowIT, a modular Retrieval-Augmented Generation (RAG) platform.

## Vision
To create a scalable, multi-modal knowledge platform supporting diverse document types, multiple LLM providers, collections, semantic search, and conversational AI.

## Planned Features
- PDF Support
- DOCX Support
- Collections
- Multiple LLM providers
- Semantic Search
- RAG Pipeline
- Streaming Chat

## Tech Stack
- Python 3.12+
- FastAPI
- SQLAlchemy
- PostgreSQL (pgvector later)
- Pydantic Settings
- Alembic (placeholder only)
- JWT (later)

## Folder Structure
```text
backend/
├── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── loaders/
│   ├── rag/
│   ├── main.py
│   └── __init__.py
├── tests/
├── .env.example
├── README.md
└── requirements.txt
```