import re

import ollama

from rag_engine import initialize_vector_store, generate_response


def _keyword_embedding(text: str):
    lowered = text.lower()
    return [1.0 if "gamma" in lowered else 0.0, 0.0]


def _fake_embed(model, input):
    docs = input if isinstance(input, list) else [input]
    return {"embeddings": [_keyword_embedding(d) for d in docs]}


def _extract_data(user_content: str) -> str:
    match = re.search(r'Data: "(.*)"\nQuery:', user_content, re.S)
    return match.group(1) if match else ""


def _extract_verified_excerpts(user_content: str) -> str:
    """The final-synthesis call's prompt shape, not receive_message's --
    used to fake a synthesis that faithfully echoes what it was given,
    so the synthesis-verification check has real overlap to find."""
    match = re.search(r"Verified excerpts:\n(.*)\n\nQuery:", user_content, re.S)
    return match.group(1) if match else ""


def _fake_chat(model, messages, options=None):
    system_content = messages[0]["content"]
    user_content = messages[-1]["content"]

    if "binary classifier" in system_content:
        data = _extract_data(user_content)
        return {"message": {"content": "YES" if "gamma" in data.lower() else "NO"}}

    if "strict text-extraction robot" in system_content:
        return {"message": {"content": _extract_data(user_content)}}

    return {"message": {"content": _extract_verified_excerpts(user_content)}}


def test_knowledge_round_trip_preserves_source_content(tmp_path, monkeypatch):
    """Ingested content must come back through retrieval unchanged (no lossy
    transformation), and the answer must be traceable to a verified excerpt
    of that exact source content."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(ollama, "embed", _fake_embed)
    monkeypatch.setattr(ollama, "chat", _fake_chat)

    corpus = tmp_path / "corpus"
    corpus.mkdir()
    original_text = "The gamma subsystem is operational."
    (corpus / "status.md").write_text(original_text + "\n")

    collection = initialize_vector_store(directory_path=str(corpus), collection_name="roundtrip", db_path=str(tmp_path / "chroma_db"))
    _, sources = generate_response(collection, "gamma status", n_results=1)

    assert sources[0]["source"] == "status.md"

    results = collection.get(where={"source": "status.md"})
    assert results["documents"][0] == original_text
