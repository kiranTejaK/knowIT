# Product Requirements Document (PRD)

# KnowIT

Version: 1.0 (MVP)

Status: Planning

Author: Kiran Teja

---

# 1. Vision

KnowIT is a production-inspired SaaS knowledge management platform that enables users to upload documents, organize them into collections, and interact with them using AI-powered conversations.

The application uses Retrieval-Augmented Generation (RAG) to provide context-aware answers instead of relying solely on an LLM's pretrained knowledge.

The project aims to demonstrate modern backend engineering practices while showcasing practical experience in:

- LLM Integration
- Retrieval Augmented Generation (RAG)
- Vector Databases
- FastAPI
- PostgreSQL + PGVector
- AWS S3
- Production-style architecture
- Observability and structured logging

This project is intentionally designed to resemble a real-world SaaS application rather than a proof-of-concept AI demo.

---

# 2. Objectives

Primary objectives

• Learn practical LLM integration
• Learn complete RAG architecture
• Build a production-inspired backend
• Gain hands-on experience with vector databases
• Demonstrate clean architecture
• Demonstrate scalable project structure
• Build a portfolio-quality project suitable for technical interviews

---

# 3. Target Users

Primary Users

Individuals who want to organize personal knowledge.

Examples

- Study notes
- Technical documentation
- Company documentation
- Project documents
- Books
- Research papers

Future Users

Organizations that want internal AI-powered knowledge bases.

---

# 4. Core Features

## Authentication

- User Registration
- Email Verification
- Login
- JWT Authentication
- Refresh Tokens
- Logout
- Forgot Password
- Password Reset

---

## Collections

Users can organize documents into independent collections.

Examples

Backend Notes

Machine Learning

Spring Boot

AWS

Interview Preparation

Collections isolate documents and reduce retrieval scope.

---

## Document Management

Supported formats

- PDF
- DOCX
- TXT
- Markdown

Future Support

- CSV
- HTML
- PowerPoint
- Excel

Each uploaded document belongs to exactly one collection.

---

## AI Chat

Users can start multiple conversations inside a collection.

Each conversation maintains its own message history.

The AI only retrieves information from the current collection.

---

## Semantic Search

Questions are answered using semantic similarity search.

Workflow

Question

↓

Embedding Generation

↓

PGVector Similarity Search

↓

Relevant Chunks

↓

Prompt Construction

↓

LLM Response

---

## Provider Agnostic LLM

The application should support multiple LLM providers through a common abstraction.

Initial Provider

- Groq

Future Providers

- OpenAI
- Google Gemini
- Anthropic
- OpenRouter

The application should require minimal code changes when switching providers.

---

## Embedding Provider Abstraction

Embedding generation should also be abstracted.

Initial provider

(Open to final selection)

Future providers can be added without modifying business logic.

---

## Background Processing

Document processing should happen asynchronously.

Workflow

Upload

↓

Store in S3

↓

Return immediately

↓

Background Task

↓

Extract Text

↓

Chunk Document

↓

Generate Embeddings

↓

Store in PGVector

This keeps uploads responsive.

---

## AWS S3 Storage

Uploaded documents should be stored in AWS S3.

The application database stores only metadata.

---

## Email Notifications

Brevo SMTP will be used.

Initial Features

- Email Verification
- Password Reset

Future

- Workspace invitations
- Notification emails

---

# 5. Non Functional Requirements

## Performance

- Fast API responses
- Async database operations
- Async file uploads
- Efficient semantic retrieval

---

## Scalability

Architecture should allow

- Multiple LLM providers
- Multiple embedding providers
- Future workspace support
- Future Redis caching

---

## Security

- JWT Authentication
- Refresh Tokens
- Password hashing
- Input validation
- Secure file validation
- Role-ready authorization design

---

## Observability

Application logs must be fully structured.

Requirements

- JSON logs
- Correlation IDs
- Request IDs
- Request latency
- Exception logging
- LLM metrics
- Retrieval metrics

Logging Stack

structlog

↓

Promtail

↓

Loki

↓

Grafana

---

## Maintainability

Project should follow

- Clean Architecture
- Service Layer
- Repository Pattern (where applicable)
- Dependency Injection
- SOLID Principles

---

# 6. Technology Stack

Frontend

- React
- Tailwind CSS
- shadcn/ui
- TanStack Query
- React Hook Form
- Zod

Backend

- FastAPI
- SQLAlchemy
- Alembic
- uv (Package & Environment Manager)

Database

- PostgreSQL
- PGVector

Storage

- AWS S3

Authentication

- JWT
- Refresh Tokens

Email

- Brevo SMTP

LLM

- Groq

Vector Search

- PGVector Semantic Search

Deployment

- Docker
- Docker Compose
- Traefik
- GitHub Actions
- EC2

Observability

- structlog
- Promtail
- Loki
- Grafana

---

# 7. MVP Scope

Included

✅ Authentication

✅ Email Verification

✅ Password Reset

✅ Collections

✅ Document Upload

✅ PDF

✅ DOCX

✅ TXT

✅ Markdown

✅ S3 Storage

✅ Background Processing

✅ Chunking

✅ Embeddings

✅ PGVector

✅ Semantic Search

✅ AI Chat

✅ Chat History

✅ Provider Agnostic LLM

✅ Structured Logging

✅ Docker Deployment

✅ CI/CD

Excluded

❌ Multi-tenancy

❌ Teams

❌ Shared Collections

❌ OCR

❌ Hybrid Search

❌ Reranking

❌ Redis Cache

❌ Celery

❌ RabbitMQ

❌ Kubernetes

---

# 8. Future Enhancements

- Team Workspaces
- RBAC
- Collection Sharing
- Redis LLM Cache
- Celery Workers
- Hybrid Search
- Reranking
- OCR
- Image Understanding
- Audio Transcription
- Web Crawling
- Slack Integration
- Notion Integration
- Google Drive Integration
- Usage Analytics
- Admin Dashboard

---

# 9. Success Criteria

The MVP is considered complete when a user can

1. Register
2. Verify email
3. Login
4. Create collections
5. Upload supported documents
6. Documents are processed asynchronously
7. Embeddings are generated
8. Chunks are stored in PGVector
9. Ask AI questions
10. Receive context-aware responses
11. Continue conversations
12. View previous chats
13. Observe logs through Grafana
14. Deploy the application using Docker and GitHub Actions

---

# 10. Guiding Principles

- Keep the architecture simple.
- Prefer clean abstractions over unnecessary complexity.
- Build for maintainability.
- Optimize for learning and interview discussions.
- Every technology included should have a clear purpose.
- Avoid adding technologies solely to increase the project's complexity.
- Complete a polished MVP before considering advanced features.
