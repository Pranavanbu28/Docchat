import hashlib

import chromadb
from docchat.chunking import Chunk

def get_collection(db_path):
    client = chromadb.PersistentClient(path=str(db_path))
    return client.get_or_create_collection("docs")

def file_hash(data):
    return hashlib.sha256(data).hexdigest()

def add_chunks(collection, chunks, digest=""):
    if not chunks:
        return
    prefix = digest[:12] or "nohash"
    collection.add(
        ids=[f"{c.source}-{prefix}-p{c.page}-c{i}" for i, c in enumerate(chunks)],
        documents=[c.text for c in chunks],
        metadatas=[
            {"source": c.source, "page": c.page, "file_hash": digest} for c in chunks
        ],
    )

def add_document(collection, name, data, chunks):
    """Store a file's chunks. Returns "added", "skipped" or "replaced"."""
    digest = file_hash(data)
    existing = collection.get(where={"source": name}, include=["metadatas"])
    if not existing["ids"]:
        add_chunks(collection, chunks, digest)
        return "added"
    if existing["metadatas"][0].get("file_hash") == digest:
        return "skipped"
    collection.delete(where={"source": name})
    add_chunks(collection, chunks, digest)
    return "replaced"

def search(collection, query, k=4):
    r = collection.query(
        query_texts=[query],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    return [
        Chunk(text=doc, source=meta["source"], page=meta["page"], distance=dist)
        for doc, meta, dist in zip(r["documents"][0], r["metadatas"][0], r["distances"][0])
    ]
