import ollama

from rag_engine import initialize_vector_store, generate_response


def _keyword_embedding(text: str):
    lowered = text.lower()
    return [1.0 if "gamma" in lowered else 0.0, 0.0]


def _fake_embed(model, input):
    docs = input if isinstance(input, list) else [input]
    return {"embeddings": [_keyword_embedding(d) for d in docs]}


def test_knowledge_round_trip_preserves_source_content(tmp_path, monkeypatch):
    """Ingested content must come back through retrieval unchanged (no lossy transformation)."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(ollama, "embed", _fake_embed)
    monkeypatch.setattr(ollama, "chat", lambda **kwargs: {"message": {"content": "n/a"}})

    corpus = tmp_path / "corpus"
    corpus.mkdir()
    original_text = "The gamma subsystem is operational."
    (corpus / "status.md").write_text(original_text + "\n")

    collection = initialize_vector_store(directory_path=str(corpus), collection_name="roundtrip")
    _, sources = generate_response(collection, "gamma status", n_results=1)

    results = collection.get(where={"source": "status.md"})
    assert results["documents"][0] == original_text
