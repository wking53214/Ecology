import pytest
import ollama

from rag_engine import initialize_vector_store, generate_response


def _keyword_embedding(text: str):
    """Deterministic 3-dim embedding: presence of alpha/beta/gamma keywords."""
    lowered = text.lower()
    return [
        1.0 if "alpha" in lowered else 0.0,
        1.0 if "beta" in lowered else 0.0,
        1.0 if "gamma" in lowered else 0.0,
    ]


def _fake_embed(model, input):
    docs = input if isinstance(input, list) else [input]
    return {"embeddings": [_keyword_embedding(d) for d in docs]}


@pytest.fixture(autouse=True)
def stub_ollama_embed(monkeypatch):
    monkeypatch.setattr(ollama, "embed", _fake_embed)


def test_initialize_vector_store_indexes_corpus_chunks(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "doc.md").write_text("Alpha content here.\n\nBeta content here.\n")

    collection = initialize_vector_store(directory_path=str(corpus), collection_name="test_collection")

    assert collection.count() == 2


def test_generate_response_retrieves_matching_source(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "alpha_doc.md").write_text("This is about alpha topics only.\n")
    (corpus / "beta_doc.md").write_text("This is about beta topics only.\n")

    collection = initialize_vector_store(directory_path=str(corpus), collection_name="test_collection2")

    monkeypatch.setattr(ollama, "chat", lambda **kwargs: {"message": {"content": "synthesized answer"}})

    answer, sources = generate_response(collection, "alpha query", n_results=1)

    assert answer == "synthesized answer"
    assert sources[0]["source"] == "alpha_doc.md"
