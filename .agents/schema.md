# schema.md

# KnowIT Database Schema

Version: 1.0

Database:
PostgreSQL 17+

Extension:
pgvector

---

# Overview

KnowIT stores

- Users
- Authentication
- Collections
- Documents
- Chunks
- Chats
- Messages

Vector embeddings are stored using PostgreSQL + PGVector.

Original documents are stored in AWS S3.

Only metadata exists inside PostgreSQL.

---

# Entity Relationship

User

↓

Collections

↓

Documents

↓

Chunks

↓

Embeddings (Vector)

Collections

↓

Chats

↓

Messages

---

# users

Stores application users.

Columns

id
UUID
Primary Key

email
VARCHAR(255)
Unique

password_hash
TEXT

full_name
VARCHAR(150)

is_email_verified
BOOLEAN

is_active
BOOLEAN

created_at

updated_at

last_login_at

Indexes

email UNIQUE

---

# refresh_tokens

Stores active refresh tokens.

Columns

id

user_id

token_hash

expires_at

revoked_at

created_at

Relationship

Many refresh tokens belong to one user.

Purpose

Allows logout from individual devices.

Supports refresh token rotation.

---

# email_verification_tokens

Columns

id

user_id

token_hash

expires_at

created_at

used_at

---

# password_reset_tokens

Columns

id

user_id

token_hash

expires_at

created_at

used_at

---

# collections

Represents a logical knowledge base.

Examples

Backend

AWS

Interview Notes

Python

Columns

id

user_id

name

description

color

created_at

updated_at

Indexes

user_id

Relationship

One User

↓

Many Collections

---

# documents

Stores uploaded document metadata.

Columns

id

collection_id

title

original_filename

extension

mime_type

file_size

storage_key

storage_provider

status

total_pages

total_chunks

created_at

updated_at

Status

UPLOADING

PROCESSING

READY

FAILED

Relationship

One Collection

↓

Many Documents

---

# chunks

Represents document chunks.

Columns

id

document_id

collection_id

content

chunk_index

page_number

token_count

embedding VECTOR

metadata JSONB

created_at

Embedding

VECTOR(768)

(The final dimension depends on the embedding model.)

Metadata

Example

{
  "section": "...",
  "heading": "...",
  "source_page": 8
}

Indexes

document_id

collection_id

HNSW Index

Purpose

Fast semantic similarity search.

---

# chats

Represents one conversation.

Columns

id

collection_id

title

created_at

updated_at

Relationship

One Collection

↓

Many Chats

---

# messages

Stores chat history.

Columns

id
UUID
Primary Key

chat_id
UUID
Foreign Key -> chats.id

role
VARCHAR(20)

content
TEXT

citations
JSONB

retrieved_chunk_ids
UUID[]

model
VARCHAR(100)

prompt_tokens
INTEGER

completion_tokens
INTEGER

total_tokens
INTEGER

latency_ms
INTEGER

created_at
TIMESTAMP WITH TIME ZONE

Role

USER

ASSISTANT

SYSTEM

Purpose

Conversation history.

Future

Streaming metadata.

---

# audit_logs (Optional)

Not required for MVP.

Future

Store security events.

Examples

Login

Password Reset

Collection Deleted

---

# Relationships

users

1

↓

N

collections

collections

1

↓

N

documents

documents

1

↓

N

chunks

collections

1

↓

N

chats

chats

1

↓

N

messages

users

1

↓

N

refresh_tokens

users

1

↓

N

email_verification_tokens

users

1

↓

N

password_reset_tokens

---

# File Storage Strategy

Database

Stores

Metadata

↓

S3

Stores

Original File

Storage Key Example

documents/

user-id/

collection-id/

document.pdf

---

# Document Lifecycle

Upload

↓

Database Entry

↓

Status

UPLOADING

↓

Upload to S3

↓

PROCESSING

↓

Background Task

↓

Chunk

↓

Embed

↓

Insert Chunks

↓

READY

---

# Chat Lifecycle

Create Chat

↓

Insert Chat

↓

User Message

↓

Retrieve Relevant Chunks

↓

Prompt Construction

↓

LLM Response

↓

Assistant Message Saved

---

# Soft Delete Strategy

Collections

Future

Documents

Future

Chats

Future

MVP

Hard Delete

Reason

Keep implementation simple.

---

# Index Strategy

users

email

UNIQUE

collections

user_id

documents

collection_id

chunks

document_id

chunks

collection_id

messages

chat_id

Vector

HNSW

embedding

Future

GIN index

metadata

---

# Constraints

Email

Unique

Collection Name

Unique Per User

Document

Belongs To One Collection

Chunk

Belongs To One Document

Message

Belongs To One Chat

Refresh Token

Belongs To One User

---

# UUID Strategy

Every table uses

UUID

Advantages

No sequential IDs

Safer APIs

Distributed-friendly

---

# Timestamps

Every major entity includes

created_at

updated_at

Timezone-aware

UTC

---

# Future Schema Extensions

Workspace

workspace_members

roles

permissions

collection_shares

api_keys

usage

billing

subscriptions

invitations

organizations

Redis cache metadata

Analytics

Embeddings Versioning

Multiple Vector Models

OCR Tables

Image Embeddings

---

# Design Principles

- Store files in S3, not PostgreSQL.
- Store vectors in PGVector.
- Normalize relational data.
- Keep collections as the primary isolation boundary.
- Keep chats independent from documents.
- Every document belongs to exactly one collection.
- Every chunk belongs to exactly one document.
- Every message belongs to exactly one chat.
- Prefer UUIDs over integer IDs.
- Design for future workspace support without implementing it in V1.
