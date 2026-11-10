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
