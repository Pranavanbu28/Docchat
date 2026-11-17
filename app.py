import tempfile
from pathlib import Path

import streamlit as st

from docchat.chunking import chunk_pages
from docchat.loaders import load_file
from docchat.store import add_document, file_hash, get_collection
from docchat.rag import NO_ANSWER, answer

ROOT = Path(__file__).parent


@st.cache_resource
def get_col():
    return get_collection(ROOT / "data" / "chroma")


col = get_col()

st.title("DocChat")
st.write("Ask questions about your documents.")

st.sidebar.header("Library")
uploaded = st.sidebar.file_uploader(
    "Add documents",
    type=["pdf", "txt", "md", "docx"],
    accept_multiple_files=True,
)

def ingest(name, data):
    """Load, chunk and store one file. Returns (sidebar style, message)."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / name
        path.write_bytes(data)
        try:
            chunks = chunk_pages(load_file(path))
        except ValueError as e:
            return "error", f"{name}: {e}"
    if not chunks:
        return "warning", f"{name}: no text found (a scanned PDF needs OCR)"
    result = add_document(col, name, data, chunks)
    return "success", f"{name}: {result} ({len(chunks)} chunks)"


# Remember what each file produced, so reruns don't repeat the work.
if "ingested" not in st.session_state:
    st.session_state.ingested = {}

seen = set()
for f in uploaded:
    data = f.getvalue()
    digest = file_hash(data)
    if (f.name, digest) in seen:
        st.sidebar.info(f"{f.name}: duplicate upload ignored")
        continue
    seen.add((f.name, digest))
    prev = st.session_state.ingested.get(f.name)
    if prev is None or prev[0] != digest:
        st.session_state.ingested[f.name] = (digest, *ingest(f.name, data))
    _, style, message = st.session_state.ingested[f.name]
    getattr(st.sidebar, style)(message)

st.sidebar.write(f"Stored chunks: {col.count()}")

def render_content(m):
    st.write(m["content"])
    if m.get("sources"):
        with st.expander("Sources"):
            for s in m["sources"]:
                st.markdown(f"**{s['source']}, p. {s['page']}**")
                st.write(s["text"])


def show_message(m):
    with st.chat_message(m["role"]):
        render_content(m)


if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    show_message(m)

if question := st.chat_input("Ask about your documents"):
    user_msg = {"role": "user", "content": question}
    st.session_state.messages.append(user_msg)
    show_message(user_msg)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            text, chunks = answer(col, question)
        sources = [] if text == NO_ANSWER else [
            {"source": c.source, "page": c.page, "text": c.text} for c in chunks
        ]
        reply = {"role": "assistant", "content": text, "sources": sources}
        render_content(reply)
    st.session_state.messages.append(reply)

