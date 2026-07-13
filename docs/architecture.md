# KnowIT - Architecture Overview

## High-Level Design
KnowIT is a modular Retrieval-Augmented Generation (RAG) platform. It follows a decoupled architecture separating the frontend client from the backend API.

### Components
1. **Frontend (Client)**: A web-based UI for users to upload documents, manage collections, and interact with the RAG chat interface.
2. **Backend (API)**: A FastAPI-based service handling business logic, authentication, document processing, and interactions with LLMs and Vector Databases.
3. **Database Layer**:
   - **Relational Data**: PostgreSQL for structured data (users, document metadata, collections, chat history).
   - **Vector Data**: pgvector (integrated within PostgreSQL) for storing and querying text embeddings.

## Backend Architecture
The backend is structured around a modular monolith pattern, ensuring clear boundaries between concerns:
- `api/`: Route handlers and controllers.
- `core/`: Application-wide configurations, security, and database connections.
- `models/`: SQLAlchemy ORM definitions mapping to database tables.
- `schemas/`: Pydantic models for request/response validation.
- `services/`: Core business logic bridging API and database.
- `loaders/`: Document parsing utilities (PDF, DOCX).
- `rag/`: Core logic for Chunking, Embeddings generation, Retrieval, and Prompt Building.

## Data Flow
1. **Document Ingestion**: User uploads a file -> `loaders/` extracts text -> `rag/chunking.py` splits text -> `rag/embeddings.py` generates vectors -> Stored in pgvector.
2. **Retrieval & Chat**: User asks a question -> `rag/embeddings.py` vectorizes query -> `rag/retriever.py` searches pgvector -> `rag/prompt_builder.py` constructs context -> LLM generates response -> Streamed to user via `api/chat.py`.
