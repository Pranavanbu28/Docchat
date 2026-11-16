import tempfile
from pathlib import Path

import streamlit as st

from docchat.chunking import chunk_pages
from docchat.loaders import load_file
from docchat.store import add_chunks, get_collection
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

for f in uploaded:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / f.name
        path.write_bytes(f.getvalue())
        try:
            chunks = chunk_pages(load_file(path))
            add_chunks(col, chunks)
            st.sidebar.success(f"{f.name}: {len(chunks)} chunks")
        except ValueError as e:
            st.sidebar.error(f"{f.name}: {e}")

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

