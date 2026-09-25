# api.md

# KnowIT REST API

Version: 1.0

Base URL

/api/v1

Authentication

JWT Bearer Authentication

Content Type

application/json

---

# API Design Principles

- RESTful endpoints
- Resource-oriented URLs
- Stateless authentication
- JSON request/response
- Consistent error responses
- Pagination where required
- UUID identifiers
- Versioned APIs

---

# Health

GET

/health

Purpose

Health check.

Response

200 OK

{
    "status": "healthy"
}

---

# Authentication

## Register

POST

/auth/register

Purpose

Create new user account.

Request

{
    "full_name": "...",
    "email": "...",
    "password": "..."
}

Response

201 Created

---

## Verify Email

POST

/auth/verify-email

Purpose

Verify email address.

---

## Login

POST

/auth/login

Purpose

Authenticate user.

Response

Access Token

Refresh Token

User

---

## Refresh Token

POST

/auth/refresh

Purpose

Issue new access token.

---

## Logout

POST

/auth/logout

Purpose

Invalidate refresh token.

---

## Forgot Password

POST

/auth/forgot-password

---

## Reset Password

POST

/auth/reset-password

---

# User

## Get Profile

GET

/users/me

Returns

Current authenticated user.

---

## Update Profile

PATCH

/users/me

---

# Collections

## List Collections

GET

/collections

Returns

All collections owned by current user.

---

## Create Collection

POST

/collections

Request

{
    "name": "...",
    "description": "...",
    "color": "..."
}

---

## Get Collection

GET

/collections/{collection_id}

---

## Update Collection

PATCH

/collections/{collection_id}

---

## Delete Collection

DELETE

/collections/{collection_id}

---

# Documents

## Upload Document

POST

/collections/{collection_id}/documents

Multipart Form

file

Behavior

Upload

↓

Save to S3

↓

Create Metadata

↓

Return

↓

Background Processing Starts

Response

202 Accepted

{
    "document_id": "...",
    "status": "PROCESSING"
}

---

## List Documents

GET

/collections/{collection_id}/documents

---

## Get Document

GET

/documents/{document_id}

---

## Document Processing Status

GET

/documents/{document_id}/status

Purpose

Check document processing status and progress percentage during background parsing, chunking, and embedding.

Response

200 OK

{
    "status": "PROCESSING",
    "progress": 65,
    "current_step": "Generating Embeddings"
}

---

## Delete Document

DELETE

/documents/{document_id}

Deletes

- Metadata
- Chunks
- S3 Object

---

## Retry Processing

POST

/documents/{document_id}/retry

Only

FAILED documents.

---

# Chats

## Create Chat

POST

/collections/{collection_id}/chats

Request

{
    "title": "Optional"
}

---

## List Chats

GET

/collections/{collection_id}/chats

---

## Get Chat

GET

/chats/{chat_id}

---

## Rename Chat

PATCH

/chats/{chat_id}

---

## Delete Chat

DELETE

/chats/{chat_id}

---

# Messages

## Send Message

POST

/chats/{chat_id}/messages

Request

{
    "message": "Explain FastAPI middleware."
}

Workflow

Save User Message

↓

Generate Embedding

↓

Semantic Search

↓

Prompt

↓

LLM

↓

Save Assistant Message

↓

Return Response

Response

{
    "answer": "...",
    "citations": [...],
    "latency_ms": 950
}

---

## List Messages

GET

/chats/{chat_id}/messages

---

# Search

## Semantic Search

POST

/collections/{collection_id}/search

Request

{
    "query": "...",
    "top_k": 5
}

Response

Relevant Chunks

Purpose

Debugging

Future

Power Users

---

# Settings

## Available LLM Providers

GET

/settings/llm-providers

Example

[
    "groq",
    "openai",
    "gemini"
]

---

## Change Preferred LLM

PATCH

/settings/llm-provider

---

## Available Embedding Models

GET

/settings/embedding-models

---

# Admin (Future)

GET

/admin/users

GET

/admin/usage

GET

/admin/logs

Not included in MVP.

---

# Standard Response

Success

{
    "success": true,
    "data": {}
}

Error

{
    "success": false,
    "error": {
        "code": "...",
        "message": "..."
    }
}

---

# HTTP Status Codes

200 OK

201 Created

202 Accepted

204 No Content

400 Bad Request

401 Unauthorized

403 Forbidden

404 Not Found

409 Conflict

422 Validation Error

429 Too Many Requests

500 Internal Server Error

---

# Pagination

Request

?page=1

&page_size=20

Response

{
    "items": [],
    "pagination": {
        "page": 1,
        "page_size": 20,
        "total": 100
    }
}

---

# Correlation ID

Every request contains

X-Correlation-ID

If missing

Backend generates one.

Returned

Response Header

Purpose

Tracing

Logging

Debugging

---

# Authentication Header

Authorization

Bearer <access_token>

---

# File Upload Limits

Allowed

PDF

DOCX

TXT

MD

Maximum Size

Configurable

(Default implementation to define limit.)

---

# Future APIs

Workspace APIs

Invitation APIs

RBAC APIs

Billing APIs

Usage APIs

API Keys

Webhooks

Hybrid Search

Streaming Responses

Voice Chat

OCR

Image Search

Slack Sync

Google Drive Sync

Not part of MVP.
