from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class ExtractedChunk:
    chunk_index: int
    page_number: int
    content: str
    token_count: int


def estimate_token_count(text: str) -> int:
    """Rough token estimation (approx ~4 chars per token)."""
    return max(1, len(text) // 4)


def chunk_text_pages(
    pages: List[Tuple[int, str]],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> List[ExtractedChunk]:
    """Splits pages of text into fixed-size overlapping chunks."""
    extracted_chunks = []
    global_index = 0

    for page_num, text in pages:
        if not text:
            continue

        # Single page text chunking
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + chunk_size
            chunk_content = text[start:end].strip()

            if chunk_content:
                tokens = estimate_token_count(chunk_content)
                extracted_chunks.append(
                    ExtractedChunk(
                        chunk_index=global_index,
                        page_number=page_num,
                        content=chunk_content,
                        token_count=tokens,
                    )
                )
                global_index += 1

            start += (chunk_size - chunk_overlap)
            if start >= text_len:
                break

    return extracted_chunks
