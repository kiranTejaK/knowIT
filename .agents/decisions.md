# decisions.md

# KnowIT - Architecture Decision Records (ADR)

Version: 1.0

---

# Introduction

This document records the major architectural decisions made during the design of KnowIT.

Each decision includes:

- Decision
- Context
- Alternatives
- Rationale
- Trade-offs

The purpose is to preserve architectural intent and prevent revisiting previously resolved decisions without a strong reason.

---

# ADR-001

## Use FastAPI as the Backend Framework

### Decision

Use FastAPI.

### Alternatives

- Django
- Flask
- Spring Boot
- Express.js

### Why

- Excellent async support
- Strong typing
- Automatic OpenAPI generation
- Dependency Injection
- High performance
- Familiar technology

### Trade-off

Smaller ecosystem than Django but significantly simpler for API-first development.

---

# ADR-002

## PostgreSQL as Primary Database

### Decision

Use PostgreSQL.

### Alternatives

- MySQL
- MongoDB
- SQL Server

### Why

- Mature relational database
- Excellent JSON support
- Native PGVector extension
- ACID compliance
- Strong indexing capabilities

### Trade-off

Slightly steeper learning curve than MySQL.

---

# ADR-003

## PGVector instead of Dedicated Vector Database

### Decision

Use PostgreSQL + PGVector.

### Alternatives

- Pinecone
- Weaviate
- Qdrant
- Milvus

### Why

- Single database
- Simpler deployment
- Lower operational complexity
- Suitable for MVP
- Good interview discussion point

### Trade-off

Not ideal for very large-scale vector workloads.

---

# ADR-004

## Semantic Search Only

### Decision

Implement semantic search.

### Alternatives

- Hybrid Search
- BM25 + Vector Search
- Keyword Search

### Why

- Simpler implementation
- Sufficient for MVP
- Demonstrates RAG concepts
- Faster development

### Trade-off

May miss exact keyword matches.

Hybrid search can be introduced later.

---

# ADR-005

## Collection-Based Organization

### Decision

Documents belong to Collections.

### Why

Collections provide

- Logical organization
- Retrieval isolation
- Better user experience
- Cleaner architecture

### Alternatives

- Flat document storage
- Folder hierarchy

### Trade-off

Adds an additional resource but significantly improves scalability.

---

# ADR-006

## Provider-Agnostic LLM Layer

### Decision

Abstract LLM providers behind a common interface.

### Providers

- Groq
- OpenAI
- Gemini
- Anthropic

### Why

Avoid vendor lock-in.

Support switching providers with minimal code changes.

### Trade-off

Requires an abstraction layer.

---

# ADR-007

## Provider-Agnostic Embeddings

### Decision

Use an Embedding Provider interface.

### Why

Embedding models evolve rapidly.

Changing providers should not affect business logic.

---

# ADR-008

## Background Document Processing

### Decision

Use FastAPI BackgroundTasks.

### Alternatives

- Celery
- RabbitMQ
- Redis Queue

### Why

Simple deployment.

Sufficient for expected workload.

Lower implementation complexity.

### Future

Can migrate to Celery without changing business logic.

---

# ADR-009

## AWS S3 for File Storage

### Decision

Store original documents in S3.

### Why

Database stores metadata only.

Improves scalability.

Reduces database size.

---

# ADR-010

## JWT Authentication

### Decision

JWT Access Token

+

Refresh Token

### Why

Industry standard.

Stateless authentication.

Supports mobile and web clients.

---

# ADR-011

## Refresh Token Rotation

### Decision

Persist hashed refresh tokens.

### Why

Supports

- Logout
- Device revocation
- Better security

---

# ADR-012

## UUID Primary Keys

### Decision

All entities use UUID.

### Why

Safer APIs.

No sequential IDs.

Future distributed compatibility.

---

# ADR-013

## Docker-Based Deployment

### Decision

Docker Compose

### Alternatives

- Kubernetes
- Bare Metal

### Why

Simple.

Production-inspired.

Easy local development.

---

# ADR-014

## Traefik Reverse Proxy

### Decision

Use Traefik.

### Why

Automatic routing.

Docker integration.

HTTPS support.

Future scalability.

---

# ADR-015

## GitHub Actions Deployment

### Decision

GitHub Actions

↓

SSH

↓

EC2

### Why

Simple CI/CD.

Easy to understand.

Suitable for portfolio project.

---

# ADR-016

## Structured Logging

### Decision

Use structlog.

### Why

Machine-readable logs.

JSON output.

Better debugging.

Supports observability.

---

# ADR-017

## Loki Logging Stack

### Decision

Promtail

↓

Loki

↓

Grafana

### Alternatives

ELK Stack

OpenSearch

CloudWatch

### Why

Lightweight.

Docker friendly.

Excellent Grafana integration.

### Trade-off

Less feature-rich than ELK but significantly simpler.

---

# ADR-018

## Thin Controllers

### Decision

Business logic belongs in services.

### Why

Improves

- Testability
- Reusability
- Maintainability

Routes should only coordinate requests.

---

# ADR-019

## Repository Layer

### Decision

Repositories own database queries.

### Why

Keep SQL away from services.

Improve separation of concerns.

---

# ADR-020

## Async-First Backend

### Decision

Prefer async throughout the application.

### Why

Better scalability.

Efficient I/O.

Matches FastAPI strengths.

---

# ADR-021

## LangChain Usage

### Decision

Use LangChain selectively.

### Use Cases

- Document loaders
- Text splitters
- PGVector integrations

### Avoid

Allowing LangChain to own application architecture.

### Why

Maintain architectural clarity.

Understand the RAG pipeline instead of hiding it.

---

# ADR-022

## Keep V1 Focused

### Decision

Exclude

- Hybrid Search
- Celery
- Redis Cache
- Kubernetes
- OCR
- Workspaces

### Why

Deliver a polished MVP.

Avoid unnecessary complexity.

---

# ADR-023

## Use uv as Package & Environment Manager

### Decision

Use `uv` as the python package installer and environment manager instead of `pip`.

### Why

- Extremely fast package resolution and installation speed.
- Deterministic, reproducible virtual environments.
- Drop-in compatibility for pip workflows (`uv pip install`).
- Standardized local and containerized dependency management.

### Rule

Do not use raw `pip` directly. All environment and package management must use `uv`.

---

# Guiding Philosophy

Every technology included in KnowIT must solve a real problem.

The project prioritizes:

- Clarity
- Maintainability
- Learning
- Production-inspired architecture

over technology accumulation.

The architecture should be easy to explain, easy to extend, and realistic to implement within the project's scope.
