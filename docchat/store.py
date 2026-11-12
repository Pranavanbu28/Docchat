import chromadb
from docchat.chunking import Chunk

def get_collection(db_path):
    client = chromadb.PersistentClient(path=str(db_path))
    return client.get_or_create_collection("docs")

def add_chunks(collection, chunks):
    if not chunks:
        return
    collection.add(
        ids=[f"{c.source}-p{c.page}-c{i}" for i, c in enumerate(chunks)],
        documents=[c.text for c in chunks],
        metadatas=[{"source": c.source, "page": c.page} for c in chunks],
    )

def search(collection, query, k=4):
    r = collection.query(query_texts=[query], n_results=k, include=["documents", "metadatas", "distances"])
    return [
        Chunk(text=doc, source=meta["source"], page=meta["page"])
        for doc, meta in zip(r["documents"][0], r["metadatas"][0])
    ]
