# Architecture Document

# KnowIT

Version: 1.0

---

# 1. Overview

KnowIT is a production-inspired Retrieval Augmented Generation (RAG) application that allows users to upload documents, organize them into collections, and interact with them using AI.

The architecture follows a modular, service-oriented design with clear separation of concerns to improve maintainability, extensibility, and testability.

Primary goals:

- Clean Architecture
- Modular Services
- Provider Abstractions
- Async-first Backend
- Production-style Logging
- Easy AI Provider Switching
- Easy Future Scaling

---

# 2. High-Level Architecture

                        React Frontend
                              │
                     HTTPS (Traefik)
                              │
                     FastAPI Application
                              │
 ┌──────────────┬─────────────┬──────────────┐
 │              │             │              │
Auth       Collection     Document      Chat Service
Service      Service       Service         Service
 │              │             │              │
 └──────────────┴─────────────┴──────────────┘
                    │
              RAG Service
                    │
     ┌──────────────┴───────────────┐
     │                              │
Embedding Provider          LLM Provider
     │                              │
     └──────────────┬───────────────┘
                    │
          PostgreSQL + PGVector
                    │
                  AWS S3

Logging Flow

FastAPI
   │
structlog
   │
Promtail
   │
Loki
   │
Grafana

---

# 3. Technology Stack

## Frontend

- React
- TypeScript
- Tailwind CSS
- shadcn/ui
- TanStack Query
- React Hook Form
- Zod

Responsibilities

- Authentication
- Collection Management
- Document Upload
- Chat Interface
- Settings

---

## Backend

FastAPI

Package & Environment Manager

- uv (MUST be used instead of pip)

Responsibilities

- Business Logic
- Authentication
- RAG
- Storage
- API Layer

---

## Database

PostgreSQL

Extensions

- PGVector

Responsibilities

- Users
- Collections
- Documents
- Chunks
- Chats
- Messages

---

## Object Storage

AWS S3

Stores

- Original files

Database stores only metadata.

---

# 4. Backend Folder Structure

app/

    api/
    core/
    config/
    middleware/
    models/
    schemas/
    repositories/
    services/
    providers/
        llm/
        embedding/
        storage/
    rag/
    background/
    db/
    utils/
    dependencies/
    main.py

Purpose

api/
HTTP Routes

services/
Business Logic

repositories/
Database Layer

providers/
External Services

rag/
Retrieval Pipeline

background/
Async Document Processing

middleware/
Logging
Timing
Correlation IDs

---

# 5. Frontend Structure

src/

    pages/
    layouts/
    components/
    hooks/
    services/
    api/
    features/
    types/
    utils/

Feature-first organization should be preferred.

---

# 6. Authentication Architecture

Authentication uses

- JWT Access Token
- Refresh Token

Flow

Register

↓

Verify Email

↓

Login

↓

Access Token

↓

Refresh Token

↓

Protected APIs

Passwords

- bcrypt hashing

Tokens

Access Token

Short-lived

Refresh Token

Long-lived

---

# 7. Collection Architecture

Each user owns multiple collections.

User

↓

Collection

↓

Documents

↓

Chats

↓

Messages

Collections isolate

- Documents
- Chat History
- Retrieval Scope

---

# 8. Document Upload Pipeline

Upload Request

↓

Authentication

↓

Validate File

↓

Store File in S3

↓

Save Metadata

↓

Return 202 Accepted

↓

Background Processing Starts

↓

Extract Text

↓

Clean Text

↓

Chunk Text

↓

Generate Embeddings

↓

Store Chunks

↓

Ready

The API should never wait for embedding generation.

---

# 9. Background Processing

V1

FastAPI BackgroundTasks

Responsibilities

- Text Extraction
- Chunking
- Embeddings
- Save Chunks

Future

BackgroundTasks implementation can later be replaced by

- Celery
- Redis

without changing business logic.

---

# 10. RAG Pipeline

Question

↓

Determine Collection

↓

Generate Query Embedding

↓

Semantic Search

↓

Top K Chunks

↓

Prompt Construction

↓

LLM

↓

Response

Only documents belonging to the selected collection participate in retrieval.

---

# 11. Chunking Pipeline

Document

↓

Extract Text

↓

Normalize

↓

Chunk

↓

Generate Metadata

↓

Embedding

↓

Store

Each chunk contains

- text
- embedding
- document id
- collection id
- page number (if applicable)
- chunk index

---

# 12. Provider Architecture

LLM Provider

Abstract Interface

generate()

stream()

health_check()

Providers

- Groq
- OpenAI
- Gemini
- Anthropic

Business logic must never directly call provider SDKs.

---

# 13. Embedding Provider

Abstract Interface

embed()

Providers

Initial provider selected during implementation.

Future providers

- OpenAI
- Voyage
- Jina
- Nomic

Embedding implementation should be swappable.

---

# 14. Storage Provider

Abstract Interface

upload()

delete()

get_url()

Initial Provider

AWS S3

Future

- Local Storage
- MinIO
- Cloudflare R2

---

# 15. Logging Architecture

Application logging uses

structlog

Every request should receive

- Correlation ID
- Request ID

Captured Information

- User ID
- Endpoint
- Status Code
- Latency
- Exception
- Collection ID
- LLM Provider
- Retrieval Time
- Generation Time

Logs

↓

Promtail

↓

Loki

↓

Grafana

Logs must remain structured JSON.

---

# 16. Middleware Stack

Request

↓

Correlation ID Middleware

↓

Request Timing Middleware

↓

Authentication Middleware

↓

Business Logic

↓

Exception Middleware

↓

Response

---

# 17. Deployment Architecture

Developer

↓

Git Push

↓

GitHub Actions

↓

SSH

↓

EC2

↓

Docker Compose

↓

Traefik

↓

FastAPI

↓

PostgreSQL

↓

Promtail

↓

Loki

↓

Grafana

↓

AWS S3

Docker services

- frontend
- backend
- postgres
- traefik
- promtail
- loki
- grafana

---

# 18. Observability

Metrics

- Request Count
- Error Count
- Upload Count
- Average Latency
- RAG Latency
- Embedding Time
- LLM Time

Log Search

Grafana + Loki should allow searching by

- Correlation ID
- User ID
- Collection ID
- Endpoint

---

# 19. Security Principles

- JWT Authentication
- Refresh Tokens
- Password Hashing
- Input Validation
- File Validation
- Authorization Checks
- Secure Environment Variables

Secrets should never be committed.

---

# 20. Scalability Strategy

Current

Single EC2

Single FastAPI Instance

Single PostgreSQL

Future

Multiple API Instances

↓

Load Balancer

↓

Dedicated Worker Queue

↓

Redis

↓

Celery

↓

Read Replicas

↓

Horizontal Scaling

The architecture should evolve without requiring major redesigns.

---

# 21. Architectural Principles

- Business logic belongs in services.
- API routes should remain thin.
- Providers should be replaceable.
- Repository layer should isolate database logic.
- Keep dependencies one-directional.
- Prefer composition over inheritance.
- Keep modules cohesive and loosely coupled.
- Every abstraction should solve a real problem.
- Simplicity is preferred over unnecessary flexibility.
