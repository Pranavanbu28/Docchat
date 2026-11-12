from docchat.chunking import Chunk
from docchat.store import get_collection, add_chunks, search

def _toy(tmp_path):
    col = get_collection(tmp_path)
    add_chunks(col, [
        Chunk("Cats are small furry pets that purr.", "a.txt", 1),
        Chunk("Bananas are yellow fruit rich in potassium.", "b.txt", 1),
        Chunk("Python is a programming language.", "c.txt", 3),
    ])
    return col

def test_search_finds_by_meaning(tmp_path):
    results = search(_toy(tmp_path), "feline pets", k=1)
    print(results)
    assert "Cats" in results[0].text

def test_search_keeps_source_and_page(tmp_path):
    result = search(_toy(tmp_path), "programming", k=1)[0]
    assert (result.source, result.page) == ("c.txt", 3)

def test_chunk_pages_carries_page_numbers():
    from docchat.loaders import Page
    from docchat.chunking import chunk_pages
    chunks = chunk_pages([Page("x" * 1000, "f.pdf", 1), Page("y" * 100, "f.pdf", 2)])
    assert [c.page for c in chunks] == [1, 1, 2]
