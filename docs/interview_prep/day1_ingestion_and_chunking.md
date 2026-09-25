# Day 1: Document Ingestion & Chunking ✂️📄

## 1. The 10-Year-Old Explanation

Imagine you have a giant, heavy 800-page encyclopedia about animals.

If someone asks you: *"What color is a polar bear's skin?"*
You don't want to swallow the entire 800-page book at once to find out! Your brain would explode, and it would take way too long to read.

Instead, what if you:
1. Took a pair of safety scissors.
2. Cut the giant book into small, handy **index cards** (say, 2 paragraphs per card).
3. Put a little sticker on each card saying: *"From Page 42"*.

Now, whenever someone asks about polar bears, you only need to grab the **1 index card** about polar bears and read it in 2 seconds!

### But wait! Why do we need "Overlap"?
Imagine cutting a sentence right down the middle with your scissors:
- Card 1 ends with: *"Polar bears have white fur, but underneath, their skin is actually..."*
- Card 2 begins with: *"...jet black to absorb sunlight."*

If you only read Card 1, you don't know the answer! If you only read Card 2, you don't know whose skin is black!

**The Trick (Overlap):**
When cutting the cards, you make sure the end of Card 1 is repeated at the start of Card 2! Like a tape that overlaps:
- Card 1: *"...Polar bears have white fur, but underneath, their skin is actually jet black."*
- Card 2: *"underneath, their skin is actually jet black to absorb sunlight."*

Now, no matter which card you grab, the complete idea is safe!

---

## 2. The Backend Engineering Reality

In a real computer system, here is why we do this:

1. **LLMs have limited context windows**: If you pass a 100-page PDF to an LLM, it costs a ton of money (tokens), takes 10+ seconds to respond, and the LLM gets confused (the "needle in a haystack" problem).
2. **Text Extraction**: Different files come in different formats:
   - PDFs are tricky (they have streams of characters and font tables). We use `pypdf`.
   - Word docs (`.docx`) have XML paragraphs. We use `python-docx`.
   - `.txt` and `.md` are plain UTF-8 text.
3. **Background Processing**: Extracting and chunking a 50MB PDF takes several seconds. If the user clicks "Upload", your HTTP request should **NOT** freeze and timeout!
   - You upload the file to S3 immediately.
   - Return `202 Accepted` or `status: "PROCESSING"` to the user.
   - Run the heavy extraction and chunking in the background (using FastAPI `BackgroundTasks` or Celery).

---

## 3. Where is this in our Codebase?

- **Text Extraction**: Look at [`backend/app/loaders/text_extractors.py`](file:///c:/Users/kiran/Desktop/knowIT/backend/app/loaders/text_extractors.py):
  ```python
  class TextExtractor:
      @staticmethod
      def extract_pdf(file_bytes: bytes):
          reader = PdfReader(io.BytesIO(file_bytes))
          ...
  ```
- **Chunking with Overlap**: Look at [`backend/app/loaders/chunker.py`](file:///c:/Users/kiran/Desktop/knowIT/backend/app/loaders/chunker.py):
  ```python
  def chunk_text_pages(pages, chunk_size=1000, chunk_overlap=200):
      # Sliding window algorithm
      while start < text_len:
          end = start + chunk_size
          chunk_content = text[start:end].strip()
          extracted_chunks.append(...)
          start += (chunk_size - chunk_overlap) # <-- The overlap step!
  ```
- **Background Pipeline**: Look at [`backend/app/services/document_service.py`](file:///c:/Users/kiran/Desktop/knowIT/backend/app/services/document_service.py#L39-L77):
  ```python
  background_tasks.add_task(self.process_document_background, doc.id, file_bytes)
  ```

---

## 4. How to Explain this in an Interview 🎙️

> **Interviewer**: *"How do you handle document ingestion and chunking in a RAG system?"*
>
> **You (Strong Answer)**:
> *"In our ingestion pipeline, we treat document processing as an asynchronous workflow to keep our API fast and responsive. 
> 
> When a user uploads a file, we validate the MIME type and file size, store the raw binary in object storage (AWS S3), and return an immediate upload status. A background task then handles parsing using format-specific extractors—such as `pypdf` for PDFs or `python-docx` for Word documents.
> 
> Next, we apply a sliding-window chunking strategy. In our project, we use a 1000-character window with a 200-character overlap (approx. 20%). The reason chunking is critical is that vector search needs small, semantically cohesive passages to match user queries accurately without blowing up token budgets. The 20% overlap ensures we don't accidentally split critical sentences or entity relationships across chunk boundaries."*
