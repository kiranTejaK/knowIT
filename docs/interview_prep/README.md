# 7-Day AI Backend Crash Course: Explain Like I'm 10 🚀

Welcome to your 7-day, no-nonsense guide to mastering **AI-powered backend systems**. 

This guide is written specifically for **FastAPI & Python backend engineers** preparing for technical interviews. Every concept starts with a simple, everyday analogy that a 10-year-old would understand, connects directly to the actual code in this repository, and concludes with an **"Interview Script"** you can use when speaking to hiring managers.

---

## 🗺️ The 7-Day Roadmap

| Day | Topic | Fun Analogy | Core Code in this Repo |
|---|---|---|---|
| [**Day 1**](./day1_ingestion_and_chunking.md) | **Document Ingestion & Chunking** | *Cutting a 500-page encyclopedia into flashcards with overlapping edges.* | `app/loaders/chunker.py`, `app/loaders/text_extractors.py` |
| [**Day 2**](./day2_embeddings_and_vector_db.md) | **Embeddings & Vector Databases** | *Giving every idea a GPS coordinate on a giant 3D meaning-map.* | `app/models/chunk.py`, `pgvector` in PostgreSQL |
| [**Day 3**](./day3_retrieval_and_context_assembly.md) | **Retrieval, Context & Citations** | *Grabbing the top 3 best flashcards and making an open-book exam cheat sheet.* | `app/services/rag_service.py` |
| [**Day 4**](./day4_llm_provider_abstraction_and_fallback.md) | **Provider Abstraction & Fallbacks** | *Universal TV remote and a backup generator when the power goes out.* | `app/providers/llm/base.py`, `groq_provider.py` |
| [**Day 5**](./day5_rate_limits_and_token_costs.md) | **Rate Limiting, HTTP 429 & Costs** | *Bouncers at the candy shop door and coin allowances for the arcade.* | `Settings`, `tenacity` exponential backoff |
| [**Day 6**](./day6_keyword_vs_hybrid_search_and_langchain.md) | **Keyword vs. Semantic vs. Hybrid Search & LangChain** | *Finding exact serial numbers vs. ideas, and why you don't need a heavy 50-blade Swiss Army knife.* | SQL `LIKE` vs. `pgvector`, native Python RAG |
| [**Day 7**](./day7_end_to_end_mock_interview_and_architecture.md) | **The Master Blueprint & Mock Interview** | *Drawing the whole chocolate factory on the whiteboard and answering all questions.* | Full System Architecture & Interview Q&A |

---

## 🎯 How to Use These Notes
1. **Read one file per day** (about 10–15 minutes).
2. **Open the linked code files** in your editor to see where the concepts live.
3. **Practice saying the "Interview Script" out loud** in your own voice.
