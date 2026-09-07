import json
import re

import pytest
import ollama

import rag_engine
from rag_engine import generate_response, index_history_repo, initialize_vector_store


def _keyword_embedding(text: str):
    """Deterministic 3-dim embedding: presence of alpha/beta/gamma keywords."""
    lowered = text.lower()
    return [
        1.0 if "alpha" in lowered else 0.0,
        1.0 if "beta" in lowered else 0.0,
        1.0 if "gamma" in lowered else 0.0,
    ]


def _fake_embed(texts):
    """Stands in for rag_engine._embed (the local ONNX embedder): a list of
    strings in, a list of deterministic keyword vectors out."""
    return [_keyword_embedding(t) for t in texts]


def _extract_data(user_content: str) -> str:
    match = re.search(r'Data: "(.*)"\nQuery:', user_content, re.S)
    return match.group(1) if match else ""


def _extract_verified_excerpts(user_content: str) -> str:
    """The final-synthesis call's prompt shape, not receive_message's --
    used to fake a synthesis that faithfully echoes what it was given,
    so the synthesis-verification check has real overlap to find."""
    match = re.search(r"Verified excerpts:\n(.*)\n\nQuery:", user_content, re.S)
    return match.group(1) if match else ""


def _fake_chat_relevance_matches_query(model, messages, options=None):
    """Simulates receive_message's two calls plus the final synthesis call,
    routed by which system prompt is active. Relevance/extraction always
    succeed for content that literally contains the query keyword, so the
    containment check has real, verifiable data to check against."""
    system_content = messages[0]["content"]
    user_content = messages[-1]["content"]

    if "binary classifier" in system_content:
        data = _extract_data(user_content)
        query = re.search(r'Query: "(.*)"', user_content).group(1)
        keyword = query.split()[0].lower()
        return {"message": {"content": "YES" if keyword in data.lower() else "NO"}}

    if "strict text-extraction robot" in system_content:
        data = _extract_data(user_content)
        return {"message": {"content": data}}

    return {"message": {"content": _extract_verified_excerpts(user_content)}}


@pytest.fixture(autouse=True)
def stub_ollama(monkeypatch):
    # retrieval no longer goes through ollama -- it's the local ONNX
    # embedder, reached via rag_engine._embed. Synthesis and the
    # receive_message verification calls still use ollama.chat.
    monkeypatch.setattr(rag_engine, "_embed", _fake_embed)
    monkeypatch.setattr(ollama, "chat", _fake_chat_relevance_matches_query)


def test_initialize_vector_store_indexes_corpus_chunks(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "doc.md").write_text("Alpha content here.\n\nBeta content here.\n")

    collection = initialize_vector_store(directory_path=str(corpus), collection_name="test_collection", db_path=str(tmp_path / "chroma_db"))

    assert collection.count() == 2


def test_generate_response_retrieves_and_verifies_matching_source(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "alpha_doc.md").write_text("alpha topics only in this document.\n")
    (corpus / "beta_doc.md").write_text("beta topics only in this document.\n")

    collection = initialize_vector_store(directory_path=str(corpus), collection_name="test_collection2", db_path=str(tmp_path / "chroma_db"))

    answer, sources = generate_response(collection, "alpha query", n_results=1, verifier="llm")

    assert "alpha topics" in answer
    assert sources[0]["source"] == "alpha_doc.md"
    assert sources[0]["extract"] == "alpha topics only in this document."


def test_generate_response_returns_no_answer_when_nothing_verifies(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    # gamma keyword embeds to [0,0,0], same as an unrelated query, so the
    # retrieved chunk won't actually contain the query keyword -> relevance
    # check fails -> nothing verifies -> honest "no answer" response.
    (corpus / "unrelated.md").write_text("Completely unrelated content.\n")

    collection = initialize_vector_store(directory_path=str(corpus), collection_name="test_collection3", db_path=str(tmp_path / "chroma_db"))

    answer, sources = generate_response(collection, "gamma query", n_results=1, verifier="llm")

    assert sources == []
    assert "does not contain a verifiable answer" in answer


def _history_repo(tmp_path):
    """A minimal Claude_History-shaped repo with two dated conversations."""
    repo = tmp_path / "Claude_History"
    (repo / "index").mkdir(parents=True)
    (repo / "transcripts").mkdir()
    convs = [
        ("older", "2026-01-05T10:00:00Z",
         "---\nid: older\n---\n\n**human_anon** (2026-01-05T10:00:00Z):\n\n"
         "alpha topics only in this message.\n\n"
         "**assistant_anon** (2026-01-05T10:01:00Z):\n\nunderstood, that is the key point here.\n"),
        ("newer", "2026-09-05T10:00:00Z",
         "---\nid: newer\n---\n\n**human_anon** (2026-09-05T10:00:00Z):\n\n"
         "beta topics only in this message.\n"),
    ]
    manifest = []
    for cid, start, text in convs:
        (repo / "transcripts" / f"{cid}.md").write_text(text)
        manifest.append({"id": cid, "start_time": start, "transcript": f"transcripts/{cid}.md"})
    (repo / "index" / "manifest.json").write_text(json.dumps({"conversations": manifest}))
    return repo


def test_index_history_repo_indexes_every_message_cell(tmp_path):
    repo = _history_repo(tmp_path)
    collection = index_history_repo(
        str(repo), collection_name="hist_test_1", db_path=str(tmp_path / "chroma_db"),
    )
    assert collection.count() == 3  # 2 messages in "older" + 1 in "newer"


def test_indexed_history_cells_carry_real_date_and_speaker_metadata(tmp_path):
    repo = _history_repo(tmp_path)
    collection = index_history_repo(
        str(repo), collection_name="hist_test_2", db_path=str(tmp_path / "chroma_db"),
    )
    got = collection.get(ids=["Claude_History/older#0"])
    meta = got["metadatas"][0]
    assert meta["source"] == "Claude_History/transcripts/older.md"
    assert meta["date"] == "2026-01-05"          # the message's real date, not today
    assert meta["speaker"] == "human"


def test_history_and_generate_response_flow_end_to_end(tmp_path):
    repo = _history_repo(tmp_path)
    collection = index_history_repo(
        str(repo), collection_name="hist_test_3", db_path=str(tmp_path / "chroma_db"),
    )
    answer, sources = generate_response(collection, "alpha query", n_results=1, verifier="llm")
    assert "alpha topics" in answer
    assert sources[0]["source"] == "Claude_History/transcripts/older.md"


def test_history_limit_caps_conversations(tmp_path):
    repo = _history_repo(tmp_path)
    collection = index_history_repo(
        str(repo), collection_name="hist_test_4", db_path=str(tmp_path / "chroma_db"), limit=1,
    )
    assert collection.count() == 2  # only the older conversation's 2 messages


def test_indexing_a_second_repo_appends_it_does_not_skip(tmp_path):
    """The bug: _open_or_load_collection saw a populated collection and
    skipped, so a second archive into the same collection never landed.
    Now _index_cells skips per-identity, so a second repo appends and a
    re-run of the same repo is a no-op."""
    db = str(tmp_path / "chroma_db")
    repo_a = _history_repo(tmp_path)

    repo_b = tmp_path / "ChatGPT_History"
    (repo_b / "index").mkdir(parents=True)
    (repo_b / "transcripts").mkdir()
    (repo_b / "transcripts" / "g.md").write_text(
        "---\nid: g\n---\n\n**user** · 2025-03-03T00:00:00+00:00\n\n"
        "gamma topics only in this message.\n"
    )
    (repo_b / "index" / "manifest.json").write_text(json.dumps(
        {"conversations": [{"id": "g", "start_time": "2025-03-03T00:00:00+00:00",
                            "transcript": "transcripts/g.md"}]}
    ))

    col = index_history_repo(str(repo_a), collection_name="multi", db_path=db)
    assert col.count() == 3
    col = index_history_repo(str(repo_b), collection_name="multi", db_path=db)
    assert col.count() == 4  # 3 from A + 1 from B, not skipped
    col = index_history_repo(str(repo_a), collection_name="multi", db_path=db)
    assert col.count() == 4  # re-run of A adds nothing


# ---------------------------------------------------------------------------
# The deterministic verifier, which is now the default
# ---------------------------------------------------------------------------

def test_the_default_verifier_is_deterministic_and_needs_no_model(tmp_path, monkeypatch):
    """The whole reason the default changed. The LLM path made two model calls
    per candidate passage; measured, a two-passage query did not finish in 120
    seconds against retrieval that takes under two. Verification was the
    entire wall, and the Ecology -> CCC path had never completed once on real
    data because of it.

    ollama.chat is left un-stubbed for retrieval+verification here on purpose:
    if the default path touched a model, this would hang rather than fail.
    """
    monkeypatch.chdir(tmp_path)
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "decision.md").write_text(
        "We decided to use SQLite for the evidence store because it keeps the "
        "prototype dependency-free and ships with Python.\n"
    )
    collection = initialize_vector_store("corpus", collection_name="det_v1",
                                         db_path=str(tmp_path / "db"))

    from containment import verify
    got = collection.get(include=["documents"])
    query = "Why did we choose SQLite for the evidence store?"
    assert any(verify(query, doc) for doc in got["documents"]), (
        "the deterministic verifier admitted nothing from a passage that "
        "directly answers the query"
    )


def test_both_verifiers_are_reachable_and_answer_different_questions():
    """The LLM path stays available deliberately. The two answer slightly
    different questions -- deterministic establishes lexical and structural
    containment, the model attempts paraphrase judgement -- and being able to
    produce a disagreement between them on demand is worth the branch."""
    import inspect

    signature = inspect.signature(generate_response)
    assert signature.parameters["verifier"].default == "deterministic"


def test_a_verified_extract_is_a_literal_substring_under_the_default(tmp_path, monkeypatch):
    """Same evidence boundary as before, enforced structurally rather than by
    asking a model to promise it."""
    from containment import verify

    passage = ("We evaluated three options. We decided to use SQLite because "
               "it ships with Python. That closed the question.")
    extract = verify("Why did we choose SQLite?", passage)
    assert extract is not None and extract in passage
