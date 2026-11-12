def chunk_text(text, size=800, overlap=100):
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")
    chunks = []
    step = size - overlap
    start = 0
    while start < len(text):
        chunks.append(text[start:start + size])
        if start + size >= len(text):
            break
        start += step
    return chunks

from dataclasses import dataclass

@dataclass
class Chunk:
    text: str
    source: str
    page: int

def chunk_pages(pages):
    chunks = []
    for page in pages:
        for text in chunk_text(page.text):
            chunks.append(Chunk(text=text, source=page.source, page=page.page))
    return chunks
