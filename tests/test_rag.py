from types import SimpleNamespace

from docchat import rag
from docchat.chunking import Chunk
from docchat.rag import NO_ANSWER, answer, build_prompt

CHUNKS = [
    Chunk("Termination requires 60 days' notice.", "lease.pdf", 7),
    Chunk("Rent is due monthly.", "lease.pdf", 2),
]

def test_prompt_contains_question_and_chunk_text():
    p = build_prompt("How do I terminate?", CHUNKS)
    assert "How do I terminate?" in p
    assert "Termination requires 60 days' notice." in p
    assert "Rent is due monthly." in p

def test_prompt_labels_each_chunk_with_source_and_page():
    p = build_prompt("q", CHUNKS)
    assert "[lease.pdf, p. 7]" in p
    assert "[lease.pdf, p. 2]" in p

def test_prompt_tells_model_to_use_only_the_context():
    p = build_prompt("q", CHUNKS).lower()
    assert "only" in p
    assert "couldn't find" in p


def _fake_search(distance):
    return lambda collection, question, k: [
        Chunk("Rent is due monthly.", "lease.pdf", 2, distance=distance)
    ]

def test_far_match_is_refused_without_calling_the_model(monkeypatch):
    def boom(**kwargs):
        raise AssertionError("model should not be called")
    monkeypatch.setattr(rag, "search", _fake_search(rag.MAX_DISTANCE + 0.3))
    monkeypatch.setattr(rag.ollama, "chat", boom)
    assert answer(None, "who won the world cup?") == (NO_ANSWER, [])

def test_close_match_calls_the_model(monkeypatch):
    reply = SimpleNamespace(message=SimpleNamespace(content="Monthly. [lease.pdf, p. 2]"))
    monkeypatch.setattr(rag, "search", _fake_search(0.4))
    monkeypatch.setattr(rag.ollama, "chat", lambda **kwargs: reply)
    text, chunks = answer(None, "when is rent due?")
    assert text == "Monthly. [lease.pdf, p. 2]"
    assert chunks[0].source == "lease.pdf"
