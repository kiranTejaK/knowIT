# Day 3: Retrieval, Context Assembly & Citations 🔍📋

## 1. The 10-Year-Old Explanation

Imagine you are in a super tough science exam. The teacher allows you to bring a **Robot helper**, but the robot has amnesia—it only knows what you write down on a single piece of paper right in front of it!

When the test asks: *"What is the boiling point of milk?"*

Here is how you and your robot solve it:
1. **Find the clue (Retrieval)**: You search through your index card box and find the **Top 3 flashcards** that mention milk and heating.
2. **Make the cheat sheet (Context Assembly)**: You tape those 3 flashcards onto a sheet of paper. Above them, you write strict rules for your robot:
   > *"Robot: You are an honest helper. Read ONLY these 3 flashcards. Do NOT invent facts from your imagination. If the answer is not on these cards, say 'I do not know'."*
3. **The Robot Answers (Generation)**: The robot reads the 3 cards, sees *"Milk boils at 100.5°C"*, and writes the answer.
4. **Showing Proof (Citations)**: Next to its answer, the robot points to the card: *"Found on Card #12, Page 4!"*

That is **RAG** (Retrieval-Augmented Generation) in a nutshell!
- **R**etrieval: Finding the relevant flashcards.
- **A**ugmentation: Gluing them into the robot's prompt.
- **G**eneration: The robot writing the grounded answer with citations.

---

## 2. The Backend Engineering Reality

### Why RAG? Why not just fine-tune an LLM?
1. **Knowledge Cutoffs**: Base LLMs don't know what happened yesterday, nor do they know your private company documents.
2. **Hallucinations**: Without context, LLMs make up plausible-sounding nonsense.
3. **Citations & Verifiability**: A business needs to know *where* an answer came from. RAG provides exact page numbers and document IDs.
4. **Instant Updates**: When a document is updated or deleted, you just update the rows in PostgreSQL. In fine-tuning, you would have to spend thousands of dollars retraining the model!

### What is "Top-K"?
- `top_k` (usually 3 to 5) is how many chunks we retrieve.
- If $K=1$, you might miss key context that spans two chunks.
- If $K=50$, you flood the prompt with junk, increase cost, and make the LLM slow and confused.

---

## 3. Where is this in our Codebase?

Look at [`backend/app/services/rag_service.py`](file:///c:/Users/kiran/Desktop/knowIT/backend/app/services/rag_service.py#L70-L138):

```python
async def execute_rag_pipeline(self, user_id, collection_id, question, top_k=5) -> RAGResult:
    # 1. Embed user question
    query_vector = await self.embedding_provider.embed_query(question)

    # 2. Semantic Search (Top-K Chunks)
    search_results = await self.document_repo.semantic_search(collection_id, query_vector, top_k=top_k)

    # 3. Construct Context & Citations
    context_blocks = []
    citations = []
    for chunk, distance in search_results:
        context_blocks.append(f"[Page {chunk.page_number}]: {chunk.content}")
        citations.append(Citation(...))

    # 4. Assemble Grounded System Prompt
    system_prompt = (
        f"You are KnowIT AI, an intelligent assistant answering questions based on knowledge collection '{collection.name}'. "
        "Use ONLY the retrieved context below to answer accurately. If context is insufficient, state that clearly."
    )
    user_prompt = f"Retrieved Context:\n{context_str}\n\nUser Question:\n{question}"

    # 5. Call LLM
    llm_response = await self.llm_provider.generate(user_prompt, system_prompt=system_prompt)
```

---

## 4. How to Explain this in an Interview 🎙️

> **Interviewer**: *"Explain how your RAG pipeline constructs the prompt and prevents hallucinations."*
>
> **You (Strong Answer)**:
> *"Our RAG pipeline operates in two distinct phases: retrieval and synthesis.
> 
> During retrieval, the user's query is embedded and matched against our `pgvector` chunk embeddings using cosine similarity. We select the top-$K$ passages (typically $K=3$ to $5$) bounded by tenant collection permissions.
> 
> During synthesis, we construct a structured prompt with two layers:
> 1. A strict **system prompt** that establishes grounding boundaries: we instruct the model to behave as an objective assistant, use only the supplied context, and explicitly say 'I do not know' if the context lacks the answer.
> 2. An **augmented user prompt** that pairs the formatted context snippets—tagged with metadata like `[Page X]`—with the user's query.
> 
> Finally, we attach source citations (including chunk ID, page number, and similarity score) to the API response. This allows the frontend to show the exact source references so end-users can verify every claim."*
