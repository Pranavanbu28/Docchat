from docchat.chunking import Chunk
from docchat.store import add_chunks, add_document, get_collection, search

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

def test_search_returns_distance(tmp_path):
    result = search(_toy(tmp_path), "feline pets", k=1)[0]
    assert result.distance is not None and result.distance >= 0

def test_chunk_pages_carries_page_numbers():
    from docchat.loaders import Page
    from docchat.chunking import chunk_pages
    chunks = chunk_pages([Page("x" * 1000, "f.pdf", 1), Page("y" * 100, "f.pdf", 2)])
    pages = [c.page for c in chunks]
    assert pages == sorted(pages)
    assert pages.count(1) > 1       # a long page gives several chunks
    assert pages.count(2) == 1      # a short page gives one

def test_chunk_pages_skips_blank_pages():
    from docchat.loaders import Page
    from docchat.chunking import chunk_pages
    assert chunk_pages([Page("", "f.pdf", 1), Page("  \n ", "f.pdf", 2)]) == []


def _doc(name, *texts):
    return [Chunk(t, name, i + 1) for i, t in enumerate(texts)]

def test_same_file_twice_is_skipped(tmp_path):
    col = get_collection(tmp_path)
    data = b"version one"
    assert add_document(col, "a.txt", data, _doc("a.txt", "one")) == "added"
    assert add_document(col, "a.txt", data, _doc("a.txt", "one")) == "skipped"
    assert col.count() == 1

def test_edited_file_replaces_old_content(tmp_path):
    col = get_collection(tmp_path)
    add_document(col, "a.txt", b"v1", _doc("a.txt", "old cats text"))
    assert add_document(col, "a.txt", b"v2", _doc("a.txt", "new dogs text")) == "replaced"
    assert col.get()["documents"] == ["new dogs text"]

def test_removed_page_does_not_linger(tmp_path):
    col = get_collection(tmp_path)
    add_document(col, "a.pdf", b"v1", _doc("a.pdf", "page one", "page two"))
    add_document(col, "a.pdf", b"v2", _doc("a.pdf", "page one"))
    assert col.count() == 1

def test_other_files_are_untouched_by_replacement(tmp_path):
    col = get_collection(tmp_path)
    add_document(col, "a.txt", b"a1", _doc("a.txt", "from a"))
    add_document(col, "b.txt", b"b1", _doc("b.txt", "from b"))
    add_document(col, "a.txt", b"a2", _doc("a.txt", "from a again"))
    assert sorted(col.get()["documents"]) == ["from a again", "from b"]
