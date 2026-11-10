from docchat.chunking import chunk_text
import pytest

# not periodic, so a wrong overlap can't pass by accident
TEXT = ",".join(str(i) for i in range(600))

def test_short_text_is_one_chunk():
    assert chunk_text("hello", size=800, overlap=100) == ["hello"]

def test_empty_text_gives_no_chunks():
    assert chunk_text("") == []

def test_no_chunk_exceeds_size():
    chunks = chunk_text(TEXT, size=800, overlap=100)
    assert len(chunks) > 1
    assert all(len(c) <= 800 for c in chunks)

def test_neighbours_overlap():
    chunks = chunk_text(TEXT, size=800, overlap=100)
    for a, b in zip(chunks, chunks[1:]):
        assert a[-100:] == b[:100]

def test_overlap_not_smaller_than_size_raises():
    with pytest.raises(ValueError):
        chunk_text("abc", size=10, overlap=10)
