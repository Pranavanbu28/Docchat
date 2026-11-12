import ollama
from docchat.store import search

MODEL = "llama3.2:3b"
NO_ANSWER = "I couldn't find that in the uploaded documents."

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
    if not chunks:
        return NO_ANSWER, []
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": build_prompt(question, chunks)}],
    )
    return response.message.content, chunks
