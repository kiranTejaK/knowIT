# prompts.md

# KnowIT AI Development Workflows

Version: 1.0

---

# Purpose

This document contains reusable prompts for AI-assisted development.

Before using any prompt:

* Attach or provide the project documentation.
* Ensure the AI follows `agents.md`.
* Treat `architecture.md`, `schema.md`, and `api.md` as the source of truth.

Never allow the AI to redesign the architecture unless explicitly requested.

---

# Prompt 1 — Implement a Feature

You are a senior backend engineer working on the KnowIT project.

Before writing code:

* Follow agents.md.
* Follow architecture.md.
* Follow schema.md.
* Follow api.md.

Implement the following feature.

Requirements:

* Follow the existing architecture.
* Do not introduce unnecessary abstractions.
* Keep routes thin.
* Put business logic inside services.
* Use repositories for database access.
* Add structured logging.
* Add proper validation.
* Handle errors gracefully.
* Write production-quality code.

Feature:

<describe feature>

---

# Prompt 2 — Generate SQLAlchemy Models

Using schema.md,

Generate SQLAlchemy models.

Requirements

* SQLAlchemy 2.x style.
* Type annotations.
* Relationships.
* Constraints.
* UUID primary keys.
* Timezone-aware timestamps.
* Follow naming conventions.
* Do not generate unnecessary helper methods.

---

# Prompt 3 — Generate Alembic Migration

Generate the Alembic migration for the latest schema changes.

Requirements

* Safe migration.
* Reversible.
* PostgreSQL compatible.
* Enable pgvector where required.

---

# Prompt 4 — Implement Repository Layer

Implement repository classes.

Rules

* Database queries only.
* No business logic.
* Async SQLAlchemy.
* Proper transaction handling.
* Meaningful method names.

---

# Prompt 5 — Implement Service Layer

Implement the service.

Requirements

* Business logic only.
* Use repositories.
* Use providers.
* No SQL.
* No HTTP-specific logic.
* Add structured logging.

---

# Prompt 6 — Implement API Routes

Implement FastAPI routes.

Requirements

* Thin controllers.
* Dependency Injection.
* Validation.
* Authentication.
* Proper status codes.
* Response models.
* No business logic.

---

# Prompt 7 — Implement Authentication

Implement

* Register
* Login
* Refresh Token
* Logout
* Email Verification
* Forgot Password
* Password Reset

Requirements

* JWT
* Refresh Tokens
* Password hashing
* Secure validation
* Logging

---

# Prompt 8 — Implement Document Upload

Implement document upload.

Workflow

Validate

↓

Upload to S3

↓

Store metadata

↓

Return 202

↓

Start background processing

↓

Processing pipeline

↓

Ready

Supported

* PDF
* DOCX
* TXT
* Markdown

---

# Prompt 9 — Implement Background Processing

Implement asynchronous processing.

Workflow

Extract Text

↓

Clean

↓

Chunk

↓

Generate Embeddings

↓

Store Chunks

↓

Update Status

Use FastAPI BackgroundTasks.

Do not use Celery.

---

# Prompt 10 — Implement RAG Pipeline

Implement the complete retrieval pipeline.

Requirements

Generate embedding

↓

Semantic search

↓

Top-K retrieval

↓

Prompt construction

↓

LLM generation

↓

Save response

↓

Return answer

Use provider abstractions.

---

# Prompt 11 — Implement LLM Provider

Implement a new LLM provider.

Requirements

* Follow provider interface.
* Keep provider isolated.
* Support future providers.
* No business logic.
* Proper exception handling.

---

# Prompt 12 — Implement Embedding Provider

Implement an embedding provider.

Requirements

* Follow abstraction.
* Return vectors only.
* No database logic.
* Configurable model.

---

# Prompt 13 — Review Existing Code

Review the following code.

Focus on

* Architecture
* Readability
* Maintainability
* SOLID
* Performance
* Security
* Error handling
* Logging
* Best practices

Suggest improvements with explanations.

---

# Prompt 14 — Refactor Code

Refactor the following implementation.

Rules

* Preserve behavior.
* Improve readability.
* Reduce duplication.
* Keep architecture intact.
* Do not introduce unnecessary abstractions.

---

# Prompt 15 — Generate Unit Tests

Generate unit tests.

Requirements

* pytest
* Async support
* Cover happy path
* Validation
* Error cases
* Edge cases

---

# Prompt 16 — Generate Integration Tests

Generate integration tests for

* Authentication
* Collections
* Upload
* Chat
* RAG

Use realistic workflows.

---

# Prompt 17 — Debug Production Issue

Analyze the following issue.

Provide

* Root cause analysis
* Possible fixes
* Risks
* Recommended solution
* Prevention strategy

Do not guess without evidence.

---

# Prompt 18 — API Review

Review this API.

Check

* RESTfulness
* Naming
* Validation
* Security
* Status codes
* Pagination
* Error responses

---

# Prompt 19 — Database Review

Review the schema.

Check

* Normalization
* Relationships
* Indexes
* Constraints
* Performance
* Future scalability

---

# Prompt 20 — Pull Request Review

Act as a senior backend reviewer.

Review the pull request.

Check

* Architecture
* Maintainability
* Performance
* Security
* Logging
* Validation
* Naming
* Test coverage

Categorize comments into

* Critical
* Recommended
* Optional

---

# Prompt 21 — Explain the Code

Explain the implementation as if teaching a backend engineer with approximately three years of experience.

Cover

* High-level design
* Business flow
* Important decisions
* Possible improvements

---

# Prompt 22 — Interview Preparation

Act as a senior backend interviewer.

Ask questions specifically about the KnowIT project.

Focus on

* FastAPI
* PostgreSQL
* PGVector
* RAG
* LLM Integration
* AWS S3
* JWT
* Logging
* Deployment
* Design decisions

Challenge the implementation where appropriate.

---

# General Rules

Every prompt assumes:

* PRD.md has been read.
* architecture.md is authoritative.
* schema.md defines the database.
* api.md defines endpoints.
* decisions.md defines architectural choices.
* tasks.md defines implementation order.
* agents.md defines coding standards.

If there is a conflict between generated code and project documentation, the documentation takes precedence.
