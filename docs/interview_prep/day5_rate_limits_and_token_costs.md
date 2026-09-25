# Day 5: Rate Limiting, HTTP 429 & Token Cost Control ⏱️💰

## 1. The 10-Year-Old Explanation

### The Candy Shop Rule (Inbound Rate Limiting)
Imagine a candy shop that gives out free samples.
If one greedy kid sprints through the door 100 times in 1 minute, the store runs out of candy, and all the other polite kids in line get nothing!

So the shopkeeper puts a **Bouncer at the door**:
> *"Hey kid! You are only allowed 5 visits per minute. Come back later!"*

That is **Rate Limiting**.

### What is HTTP 429?
Now imagine you want to order 500 pizzas from the local pizzeria all at once.
The chef picks up the phone and yells:
> *"Slow down! My oven can only bake 2 pizzas at a time! Call me back in 30 seconds!"*

In computer language, that is **`HTTP 429: Too Many Requests`**.
The server tells you: `Retry-After: 30`.

### What is "Exponential Backoff"?
If you call the busy chef every single millisecond:
- You: *"Ready now?"*
- Chef: *"NO!"*
- You: *"Ready now?"*
- Chef: *"NO!"*

You are just making things worse!
Instead, you wait smartly:
1. Wait 1 second... try again.
2. If still busy, wait 2 seconds...
3. If still busy, wait 4 seconds...
4. If still busy, wait 8 seconds...

Doubling the wait time each time is called **Exponential Backoff**. It gives the busy server breathing room to catch up!

---

## 2. The Backend Engineering Reality

### Two Types of Limits:
1. **Inbound Limits (Protecting YOUR backend)**:
   - Implemented in FastAPI using Redis (Token Bucket / Sliding Window).
   - Prevents malicious users or runaway loops from DDOS-ing your database and bankrupting your company's LLM budget.
2. **Outbound Limits (Protecting THE PROVIDER'S servers)**:
   - LLM vendors enforce **RPM** (Requests Per Minute) and **TPM** (Tokens Per Minute).
   - If you exceed them, they return `HTTP 429`.

### How to Handle HTTP 429:
- Read the `Retry-After` header if present.
- If not present, apply exponential backoff with **jitter** (a tiny random delay like $\pm 0.5$s so thousands of waiting requests don't all slam the server at the exact same millisecond).

### Token Tracking & Quotas:
Every call to an LLM returns a usage object:
```json
"usage": {
  "prompt_tokens": 150,
  "completion_tokens": 80,
  "total_tokens": 230
}
```
In our database, we record `token_count` on the `Message` model. This allows calculating user usage per month and rejecting requests when a user hits their monthly quota.

---

## 3. Where is this in our Codebase?

- **Token Tracking**: Look at [`backend/app/providers/llm/groq_provider.py`](file:///c:/Users/kiran/Desktop/knowIT/backend/app/providers/llm/groq_provider.py#L56-L63):
  ```python
  usage = data.get("usage", {})
  return LLMResponse(
      content=choice,
      model=self.model,
      prompt_tokens=usage.get("prompt_tokens", 0),
      completion_tokens=usage.get("completion_tokens", 0),
      total_tokens=usage.get("total_tokens", 0),
  )
  ```
- **Recorded in Database**: Look at [`backend/app/models/chat.py`](file:///c:/Users/kiran/Desktop/knowIT/backend/app/models/chat.py):
  Each message stores `token_count` and `latency_ms`.
- **Exponential Backoff Pattern (Python snippet)**:
  ```python
  import asyncio
  import random

  async def call_with_retry(func, max_attempts=3):
      for attempt in range(max_attempts):
          try:
              return await func()
          except HTTPStatusError as exc:
              if exc.response.status_code == 429 and attempt < max_attempts - 1:
                  # Exponential backoff with jitter
                  wait_time = (2 ** attempt) + random.uniform(0.1, 0.5)
                  await asyncio.sleep(wait_time)
                  continue
              raise
  ```

---

## 4. How to Explain this in an Interview 🎙️

> **Interviewer**: *"How do you handle LLM rate limits and prevent API cost overruns?"*
>
> **You (Strong Answer)**:
> *"We manage LLM usage at both inbound and outbound levels.
> 
> On the **inbound side**, we place rate limiting at the API gateway or FastAPI middleware using a Redis-backed sliding window. This throttles aggressive users by tenant ID or IP before they can trigger expensive downstream tasks.
> 
> On the **outbound side**, LLM vendors enforce both Requests Per Minute (RPM) and Tokens Per Minute (TPM). When a provider responds with an `HTTP 429 Too Many Requests`, our client inspects the `Retry-After` header. If missing, we apply an exponential backoff algorithm with jitter (e.g. $2^{\text{attempt}} + \text{jitter}$) to prevent thundering herd retries.
> 
> Finally, for **cost control**, we parse and persist the `prompt_tokens` and `completion_tokens` returned by the LLM usage object into our PostgreSQL records. This allows our backend to maintain rolling tenant token balances and reject requests once a monthly budget cap is reached."*
