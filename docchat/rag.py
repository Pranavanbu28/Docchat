import ollama
from docchat.store import search

MODEL = "llama3.2:3b"
NO_ANSWER = "I couldn't find that in the uploaded documents."
# Chroma's default metric is squared L2. On our data, relevant questions had a
# best distance of 0.38-1.11 and off-topic ones 1.82-2.08.
MAX_DISTANCE = 1.5

def build_prompt(question, chunks):
    context = "\n\n".join(f"[{c.source}, p. {c.page}]\n{c.text}" for c in chunks)
    return (
        "You answer questions using ONLY the context below. "
        f"If the context does not contain the answer, reply exactly: {NO_ANSWER} "
        "Cite sources like [file, p. N].\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}"
    )

def answer(collection, question, k=4):
    chunks = search(collection, question, k)
    if not chunks or (chunks[0].distance is not None and chunks[0].distance > MAX_DISTANCE):
        return NO_ANSWER, []
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": build_prompt(question, chunks)}],
        # options={"temperature": 0}
    )
    return response.message.content, chunks
