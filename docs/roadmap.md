# KnowIT - Roadmap

This document outlines the planned phases for KnowIT development.

## Phase 1: Foundation (Current)
- [x] Initial project scaffolding.
- [x] Monorepo structure setup (Backend / Frontend / Docs).
- [ ] Database integration with SQLAlchemy and Alembic setup.
- [ ] Implement JWT-based authentication and User management.

## Phase 2: Document Management
- [ ] Implement CRUD operations for Collections.
- [ ] Build document upload endpoints.
- [ ] Implement text extraction utilities (`loaders` for PDF and DOCX).

## Phase 3: Vectorization & RAG Engine
- [ ] Setup PostgreSQL with `pgvector`.
- [ ] Implement text chunking strategies.
- [ ] Integrate with embedding providers (OpenAI, Gemini).
- [ ] Implement vector search and retrieval logic.

## Phase 4: Conversational AI
- [ ] Integrate with LLM providers for response generation.
- [ ] Build Prompt Builder service.
- [ ] Implement Chat API with support for conversational memory.
- [ ] Add support for Server-Sent Events (SSE) / Streaming Chat.

## Phase 5: Frontend Development
- [ ] Scaffold frontend web application.
- [ ] Build Dashboard and Collection Management UI.
- [ ] Implement Chat Interface.

## Future Explorations
- Multi-modal support (images/charts in documents).
- Advanced RAG techniques (HyDE, Re-ranking, GraphRAG).
- Multi-tenant architecture.
