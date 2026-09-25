# Day 2: Embeddings & Vector Databases 🧭📍

## 1. The 10-Year-Old Explanation

Computers don't understand words. If you type *"puppy"*, the computer just sees the letters `p - u - p - p - y`. It has no idea that a puppy is a small, playful baby dog!

So how do we teach a computer what words **actually mean**?

### The GPS Map of Meanings (Embeddings)
Think of a giant 3D map:
- If a word is an **animal**, it goes towards the North.
- If a word is **friendly and soft**, it goes towards the East.
- If a word is **small**, it goes towards the Sky.

Where does **"Puppy"** land on the map?
`[North: 0.8, East: 0.9, Up: 0.7]`

Where does **"Dog"** land?
`[North: 0.85, East: 0.8, Up: 0.3]`

Where does **"Refrigerator"** land?
`[North: -0.9, East: -0.5, Up: 0.1]`

Notice that **"Puppy"** and **"Dog"** are practically sitting right next to each other on the map! But **"Refrigerator"** is miles away!

That list of numbers `[0.8, 0.9, 0.7]` is called an **Embedding** (or a **Vector**).
- **Text goes in $\to$ A list of numbers comes out.**
- Sentences with similar meanings have coordinates close together!

### What is a Vector Database?
If you have 100,000 flashcards, you need a smart toy box where all the animal flashcards sit in one corner, food in another, and spaceship cards in another.
A **Vector Database** is just a database that can quickly find: *"Which 5 flashcards are sitting closest to this GPS coordinate?"*

---

## 2. The Backend Engineering Reality

1. **Embedding Models**:
   - In production, models like `text-embedding-3-small` (OpenAI, 1536 dimensions) or `all-MiniLM-L6-v2` (FastEmbed / HuggingFace, 384 dimensions) turn text chunks into dense float arrays.
   - In this project's local dev mode, we had a `MockEmbeddingProvider` (deterministic SHA-256 vector) to allow testing without needing external ML libraries.
2. **Measuring Closeness (Distance Metrics)**:
   - **Cosine Distance / Similarity**: Measures the *angle* between two vectors. Does not care how long or short the text was, only its directional meaning. (Most common for text!).
   - **Euclidean (L2) Distance**: Measures straight-line distance.
3. **Why PostgreSQL + pgvector?**:
   - You don't always need a separate standalone vector database (like Pinecone, Milvus, or Qdrant).
   - PostgreSQL has an open-source extension called **`pgvector`**.
   - With `pgvector`, your relational tables (users, permissions, documents, timestamps) and your vectors live in the **same database**. You get ACID transactions, relational foreign keys, and vector search with zero extra infrastructure overhead!

---

## 3. Where is this in our Codebase?

- **Vector Column in PostgreSQL**: Look at [`backend/app/models/chunk.py`](file:///c:/Users/kiran/Desktop/knowIT/backend/app/models/chunk.py#L23):
  ```python
  from pgvector.sqlalchemy import Vector

  class Chunk(Base):
      __tablename__ = "chunks"
      ...
      embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(384), nullable=True)
  ```
- **Semantic Search Query**: Look at [`backend/app/repositories/document_repository.py`](file:///c:/Users/kiran/Desktop/knowIT/backend/app/repositories/document_repository.py#L51-L63):
  ```python
  async def semantic_search(self, collection_id: uuid.UUID, query_vector: List[float], top_k: int = 5):
      stmt = (
          select(Chunk, Chunk.embedding.cosine_distance(query_vector).label("distance"))
          .where(Chunk.collection_id == collection_id, Chunk.embedding.is_not(None))
          .order_by("distance")
          .limit(top_k)
      )
      result = await self.db.execute(stmt)
      return [(row.Chunk, float(row.distance)) for row in result.all()]
  ```

---

## 4. How to Explain this in an Interview 🎙️

> **Interviewer**: *"What are embeddings, and why did you choose PostgreSQL with pgvector instead of a dedicated vector database?"*
>
> **You (Strong Answer)**:
> *"An embedding is a dense numerical vector representing the semantic meaning of text in a high-dimensional vector space. Passages with similar semantic intent have smaller cosine distances between their vector representations, allowing us to perform conceptual search rather than relying purely on exact keyword matching.
> 
> In our architecture, we chose **PostgreSQL with the `pgvector` extension** over a standalone vector database like Pinecone or Qdrant for operational simplicity and data integrity.
> 
> With `pgvector`, our chunks, document metadata, tenant collection IDs, and embeddings reside in a single relational store. This allows us to enforce tenant access control, perform ACID transactions, and do relational filtering (e.g. `WHERE collection_id = :id`) and vector similarity ordering (`ORDER BY embedding <=> :query_vector LIMIT 5`) in a single query, avoiding the consistency headaches and synchronization lag of maintaining two disparate data stores."*
