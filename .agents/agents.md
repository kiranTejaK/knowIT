# agents.md

# KnowIT AI Development Guide

Version: 1.0

This document defines the engineering standards and architectural rules for the KnowIT project.

Every AI assistant contributing to this repository must follow these rules unless explicitly instructed otherwise.

---

# Project Mission

KnowIT is a production-inspired RAG application.

The primary objective is not simply to build a working application.

The objective is to build software that demonstrates good backend engineering practices while remaining understandable, maintainable and interview-ready.

Every implementation decision should prioritize

- Simplicity
- Maintainability
- Readability
- Extensibility

over unnecessary complexity.

---

# Technology Stack

Frontend

- React
- TypeScript
- Tailwind CSS
- shadcn/ui
- TanStack Query
- React Hook Form
- Zod

Backend

- FastAPI
- uv (Package & Environment Manager)

Database

- PostgreSQL

Vector Database

- PGVector

Storage

- AWS S3

Authentication

- JWT
- Refresh Tokens

Email

- Brevo SMTP

Logging

- structlog

Observability

- Promtail
- Loki
- Grafana

Deployment

- Docker
- Docker Compose
- Traefik
- GitHub Actions
- EC2

---

# Core Principles

Always write code that another developer can understand six months later.

Never optimize for cleverness.

Prefer explicit code over magic.

Prefer composition over inheritance.

Keep business logic independent from frameworks.

---

# Architecture Rules

Routes

Routes should

- validate input
- call services
- return responses

Routes must NOT

- contain business logic
- contain SQL
- call external SDKs directly

---

Services

Services own

- business logic
- workflows
- orchestration

Services must remain framework independent whenever possible.

---

Repositories

Repositories own

- database queries
- persistence logic

Repositories should never contain business logic.

---

Providers

Providers wrap external services.

Examples

- LLM
- Embeddings
- AWS S3
- SMTP

Business logic should never directly use provider SDKs.

---

# RAG Rules

The retrieval pipeline should always be

Question

↓

Embedding

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

Never bypass semantic retrieval.

Never send entire documents to the LLM.

Only retrieve chunks belonging to the active collection.

---

# LLM Rules

Always use the provider abstraction.

Never directly call

- Groq SDK
- OpenAI SDK
- Gemini SDK

inside business logic.

Provider switching should require minimal code changes.

---

# Embedding Rules

Use the embedding provider abstraction.

The embedding model must be configurable.

Do not hardcode providers.

---

# Background Processing

Use FastAPI BackgroundTasks.

Document processing should execute asynchronously.

The upload API must return immediately.

Document processing consists of

- Extract Text
- Clean Text
- Chunk
- Embed
- Store

Background processing should be isolated behind a service.

Future migration to Celery should require minimal code changes.

---

# Logging Rules

Every request must have

- Correlation ID
- Request ID

Every important event must be logged.

Never use print().

Always use structlog.

Logs must be JSON.

Log

- endpoint
- user
- latency
- collection
- document
- exceptions
- provider
- retrieval time
- generation time

---

# API Rules

REST APIs only.

Use nouns.

Examples

Good

/collections

/documents

/chats

Avoid

/getCollections

/createDocument

Return proper HTTP status codes.

---

# Database Rules

Use UUID primary keys.

Use timezone-aware timestamps.

Never store uploaded files inside PostgreSQL.

Store only metadata.

Store vectors in PGVector.

---

# Frontend Rules

Prefer feature-based organization.

Use TanStack Query for server state.

Use React Hook Form.

Validate forms with Zod.

Avoid unnecessary global state.

---

# Error Handling

Never expose internal exceptions.

Return consistent error responses.

Log exceptions with context.

Prefer domain-specific exceptions.

---

# Validation

Validate

- request body
- file type
- file size
- ownership
- authorization

Never trust client input.

---

# Security

Hash passwords.

Hash refresh tokens.

Validate JWTs.

Authorize every protected endpoint.

Use environment variables for secrets.

Never commit secrets.

---

# Documentation

Public functions should have meaningful docstrings.

Complex logic should include comments explaining WHY, not WHAT.

Keep documentation synchronized with implementation.

---

# Testing Philosophy

Test

- services
- repositories
- authentication
- RAG pipeline

Avoid excessive mocking.

Test business behavior rather than implementation details.

---

# Code Style

Write descriptive names.

Keep functions small.

Avoid deeply nested conditionals.

Prefer early returns.

Prefer readability over compact code.

---

# Dependency Rules

Allowed direction

API

↓

Services

↓

Repositories

↓

Database

Services

↓

Providers

Never reverse these dependencies.

Repositories should never call services.

Providers should never call repositories.

---

# Performance

Prefer async operations.

Avoid N+1 queries.

Select only required columns.

Paginate large datasets.

---

# AI Assistant Rules

Before implementing new functionality

1. Read the relevant documentation.
2. Reuse existing abstractions.
3. Avoid duplicate code.
4. Follow existing naming conventions.
5. Keep implementations simple.

Never introduce

- Redis
- Celery
- RabbitMQ
- Kubernetes
- Elasticsearch
- Microservices

unless explicitly requested.

Do not replace existing architecture without strong justification.

---

# Package Management Rules

`uv` MUST be used as the package and python environment manager instead of `pip`.

All dependency installations, environment setups, and Docker builds MUST use `uv`.

Do not use raw `pip` directly.

---

# Definition of Done

A feature is complete only if

✓ Business logic is implemented

✓ Validation exists

✓ Logging exists

✓ Error handling exists

✓ Database updated

✓ Documentation updated

✓ API consistent

✓ Code remains readable

---

# Project Philosophy

KnowIT is intentionally designed as a focused, production-inspired application.

The goal is to demonstrate excellent engineering decisions, not the largest possible technology stack.

Every dependency, abstraction, and architectural choice should provide clear value.

When in doubt, choose the simpler design that preserves maintainability.
