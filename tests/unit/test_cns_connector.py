"""Ecology's outputs as things a CNS verdict can be bound to.

These skip where ``cns`` is not installed. CI installs requirements-cns.txt and sets ECOLOGY_REQUIRE_CNS=1, so there
they cannot skip. Binding only: nothing here is a gate and nothing maps to a verdict.
"""
import copy
import dataclasses
import hashlib
import os

import pytest

if os.environ.get("ECOLOGY_REQUIRE_CNS") == "1":  # CI: a missing cns is a failure, not a skip
    import cns.gate as gate
else:
    gate = pytest.importorskip("cns.gate")

from ecology_cns_connector import (  # noqa: E402
    ANSWER_SUBJECT, FINDING_SUBJECT, answer_content, answer_digest, binds, cns_available, finding_content,
    finding_digest)
from finding import FindingRecord, to_finding_record  # noqa: E402

CANARY = "CANARY-7f3a91c2-private-corpus-text"
NOT_IN_CORPUS = "The retrieved corpus does not contain a verifiable answer to this query."


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def answer_record():
    return {
        "query": f"why did the pump fail {CANARY}",
        "answer": f"The seal cracked. {CANARY}",
        "sources": [
            {"source": "a.md", "extract": f"the seal cracked {CANARY}", "date": "2026-03-02", "speaker": "user"},
            {"source": "b.md", "extract": "the coolant leaked", "date": "2026-07-09"},
        ],
    }


def finding_record():
    return FindingRecord(
        conclusion=f"The seal cracked. {CANARY}",
        method="ecology.rag_engine.generate_response(model=llama3.2, n_results=5)",
        source_material=("a.md", "b.md"),
        confidence=0.4,
        verified=True,
        evidence=(("a.md", f"the seal cracked {CANARY}"), ("b.md", "the coolant leaked")),
        event_start_date="2026-03-02",
        event_end_date="2026-07-09",
    )


def issued_against(subject, digest):
    return gate.GateResult(gate="test.gate", position=gate.GatePosition.OMEGA, outcome=gate.GateOutcome.PASS,
                           reason="issued for the test", subject=subject, subject_digest=digest)


def conforms(value):
    """Only what cns.gate accepts: str, int, float, bool, None, list, and dicts with str keys."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return True
    if isinstance(value, list):
        return all(conforms(v) for v in value)
    if isinstance(value, dict):
        return all(isinstance(k, str) and conforms(v) for k, v in value.items())
    return False


def test_cns_is_reported_available():
    assert cns_available() is True


# ------------------------------------------------------------ determinism and shape

def test_the_same_answer_gives_the_same_content_and_digest():
    assert answer_content(answer_record()) == answer_content(copy.deepcopy(answer_record()))
    assert answer_digest(answer_record()) == answer_digest(copy.deepcopy(answer_record()))


def test_the_same_finding_gives_the_same_content_and_digest():
    assert finding_content(finding_record()) == finding_content(finding_record())
    assert finding_digest(finding_record()) == finding_digest(finding_record())


def test_the_digest_is_cns_subject_digest_over_the_content():
    assert answer_digest(answer_record()) == gate.subject_digest(answer_content(answer_record()))
    assert finding_digest(finding_record()) == gate.subject_digest(finding_content(finding_record()))


def test_content_holds_only_types_cns_accepts_and_cns_can_digest_it():
    non_answer = {"query": "q", "answer": NOT_IN_CORPUS, "sources": []}
    for content in (answer_content(answer_record()), answer_content(non_answer), finding_content(finding_record()),
                    finding_content(dataclasses.replace(finding_record(), confidence=None, evidence=()))):
        assert conforms(content), content
        assert len(gate.subject_digest(content)) == 64


def test_a_not_in_corpus_result_is_a_record_with_no_evidence():
    content = answer_content({"query": "q", "answer": NOT_IN_CORPUS, "sources": []})
    assert content["verified"] is False and content["evidence"] == []
    assert content["answer_sha256"] == sha(NOT_IN_CORPUS)
    assert answer_content(answer_record())["verified"] is True


def test_the_two_kinds_of_output_do_not_share_a_digest():
    assert answer_digest(answer_record()) != finding_digest(finding_record())


# ------------------------------------------------------------ every bound field is bound

def _set(path, value):
    def mutate(record):
        target = record
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        return record
    return mutate


ANSWER_CHANGES = {
    "query": _set(["query"], "a different question"),
    "answer": _set(["answer"], "A different answer."),
    "an answer that is only the non-answer": _set(["answer"], NOT_IN_CORPUS),
    "first source": _set(["sources", 0, "source"], "c.md"),
    "first extract": _set(["sources", 0, "extract"], "the seal held"),
    "first extract absent": lambda r: r["sources"][0].pop("extract") and r,
    "first date": _set(["sources", 0, "date"], "2026-03-03"),
    "first date absent": lambda r: r["sources"][0].pop("date") and r,
    "second speaker added": _set(["sources", 1, "speaker"], "assistant"),
    "first speaker": _set(["sources", 0, "speaker"], "assistant"),
    "first speaker absent": lambda r: r["sources"][0].pop("speaker") and r,
    "second source": _set(["sources", 1, "source"], "d.md"),
    "second extract": _set(["sources", 1, "extract"], "the coolant held"),
    "a source dropped": lambda r: r["sources"].pop() and r,
    "no sources at all": _set(["sources"], []),
    "a source added": lambda r: r["sources"].append({"source": "e.md", "extract": "x"}) or r,
    "a source repeated": lambda r: r["sources"].append(dict(r["sources"][0])) or r,
    "the order of the evidence": lambda r: r["sources"].reverse() or r,
}


@pytest.mark.parametrize("name", list(ANSWER_CHANGES))
def test_changing_any_bound_answer_field_changes_the_digest(name):
    changed = ANSWER_CHANGES[name](answer_record())
    assert answer_digest(changed) != answer_digest(answer_record())


FINDING_CHANGES = {
    "conclusion": {"conclusion": "A different conclusion."},
    "method": {"method": "ecology.rag_engine.generate_response(model=llama3.2, n_results=9)"},
    "a source dropped from source_material": {"source_material": ("a.md",)},
    "a source added to source_material": {"source_material": ("a.md", "b.md", "c.md")},
    "a source replaced in source_material": {"source_material": ("a.md", "z.md")},
    "confidence": {"confidence": 0.6},
    "confidence removed": {"confidence": None},
    "verified": {"verified": False},
    "evidence source": {"evidence": (("z.md", f"the seal cracked {CANARY}"), ("b.md", "the coolant leaked"))},
    "evidence extract": {"evidence": (("a.md", "the seal held"), ("b.md", "the coolant leaked"))},
    "evidence dropped": {"evidence": (("a.md", f"the seal cracked {CANARY}"),)},
    "evidence emptied": {"evidence": ()},
    "evidence order": {"evidence": (("b.md", "the coolant leaked"), ("a.md", f"the seal cracked {CANARY}"))},
    "event_start_date": {"event_start_date": "2026-03-03"},
    "event_start_date removed": {"event_start_date": None},
    "event_end_date": {"event_end_date": "2026-07-10"},
    "event_end_date removed": {"event_end_date": None},
}


@pytest.mark.parametrize("name", list(FINDING_CHANGES))
def test_changing_any_bound_finding_field_changes_the_digest(name):
    changed = dataclasses.replace(finding_record(), **FINDING_CHANGES[name])
    assert finding_digest(changed) != finding_digest(finding_record())


# ------------------------------------------------------------ what is claimed not to matter

def test_extra_keys_and_container_kinds_are_not_part_of_an_answer():
    base = answer_digest(answer_record())
    noisy = answer_record()
    noisy["latency_ms"] = 12.5
    noisy["sources"][0]["rank"] = 1
    assert answer_digest(noisy) == base
    as_tuple = answer_record()
    as_tuple["sources"] = tuple(as_tuple["sources"])
    assert answer_digest(as_tuple) == base
    reordered_keys = {k: answer_record()[k] for k in ("sources", "answer", "query")}
    assert answer_digest(reordered_keys) == base


def test_the_order_of_source_material_and_the_kind_of_number_are_not_part_of_a_finding():
    base = finding_digest(finding_record())
    assert finding_digest(dataclasses.replace(finding_record(), source_material=("b.md", "a.md"))) == base
    assert finding_digest(dataclasses.replace(finding_record(), source_material=["a.md", "b.md"])) == base
    as_list = dataclasses.replace(finding_record(), evidence=[list(p) for p in finding_record().evidence])
    assert finding_digest(as_list) == base
    one, one_float = (dataclasses.replace(finding_record(), confidence=c) for c in (1, 1.0))
    assert finding_digest(one) == finding_digest(one_float)
    zero, minus_zero = (dataclasses.replace(finding_record(), confidence=c) for c in (0.0, -0.0))
    assert finding_digest(zero) == finding_digest(minus_zero)


def test_a_lone_surrogate_in_a_chat_export_hashes_instead_of_raising():
    record = answer_record()
    record["answer"] = "broken \ud83d export"
    assert len(answer_digest(record)) == 64


# ------------------------------------------------------------ wrong types and missing keys

@pytest.mark.parametrize("bad", [None, "text", 7, ["query", "answer", "sources"], (NOT_IN_CORPUS, [])])
def test_an_answer_that_is_not_a_mapping_is_a_type_error(bad):
    with pytest.raises(TypeError, match="mapping"):
        answer_content(bad)


@pytest.mark.parametrize("field, value", [
    ("query", 7), ("query", None), ("answer", b"bytes"), ("answer", ["a"]), ("sources", "a.md"), ("sources", None),
    ("sources", {"source": "a.md"}), ("sources", ["a.md"]), ("sources", [("a.md", "x")])])
def test_an_answer_field_of_the_wrong_type_is_a_type_error(field, value):
    record = answer_record()
    record[field] = value
    with pytest.raises(TypeError):
        answer_content(record)


@pytest.mark.parametrize("key, value", [("source", 3), ("extract", 3), ("date", 20260302), ("speaker", ["user"])])
def test_a_source_field_of_the_wrong_type_is_a_type_error(key, value):
    record = answer_record()
    record["sources"][0][key] = value
    with pytest.raises(TypeError, match=key):
        answer_content(record)


@pytest.mark.parametrize("key", ["query", "answer", "sources"])
def test_an_answer_missing_a_required_key_is_a_value_error_naming_it(key):
    record = answer_record()
    del record[key]
    with pytest.raises(ValueError, match=key):
        answer_content(record)


def test_a_source_without_a_source_is_a_value_error_naming_it():
    record = answer_record()
    del record["sources"][1]["source"]
    with pytest.raises(ValueError, match=r"sources\[1\].*source"):
        answer_content(record)


@pytest.mark.parametrize("bad", [None, "text", 7, {"conclusion": "x"}, ("x", "m", (), None, True), object()])
def test_a_finding_that_is_not_a_finding_record_is_a_type_error(bad):
    with pytest.raises(TypeError, match="FindingRecord"):
        finding_content(bad)


@pytest.mark.parametrize("changes", [
    {"conclusion": 7}, {"method": None}, {"source_material": "a.md"}, {"source_material": (1, 2)},
    {"confidence": "0.4"}, {"confidence": True}, {"verified": 1}, {"verified": "yes"}, {"evidence": "a.md"},
    {"evidence": ("a.md",)}, {"evidence": (("a.md",),)}, {"evidence": (("a.md", 3),)}, {"event_start_date": 20260302},
    {"event_end_date": b"2026-07-09"}])
def test_a_finding_field_of_the_wrong_type_is_a_type_error(changes):
    with pytest.raises(TypeError):
        finding_content(dataclasses.replace(finding_record(), **changes))


# ------------------------------------------------------------ binds

def test_a_verdict_issued_against_exactly_this_answer_binds_to_it():
    result = issued_against(ANSWER_SUBJECT, answer_digest(answer_record()))
    assert binds(result, answer_record()) is True
    assert result.binds(ANSWER_SUBJECT, answer_digest(answer_record()))


def test_a_verdict_issued_against_exactly_this_finding_binds_to_it():
    result = issued_against(FINDING_SUBJECT, finding_digest(finding_record()))
    assert binds(result, finding_record()) is True


def test_a_verdict_does_not_bind_to_a_different_output():
    result = issued_against(ANSWER_SUBJECT, answer_digest(answer_record()))
    assert binds(result, ANSWER_CHANGES["answer"](answer_record())) is False
    finding = issued_against(FINDING_SUBJECT, finding_digest(finding_record()))
    assert binds(finding, dataclasses.replace(finding_record(), confidence=0.8)) is False


def test_a_verdict_does_not_bind_across_kinds_or_under_another_subject():
    answer = issued_against(ANSWER_SUBJECT, answer_digest(answer_record()))
    finding = issued_against(FINDING_SUBJECT, finding_digest(finding_record()))
    assert binds(answer, finding_record()) is False and binds(finding, answer_record()) is False
    assert binds(answer, answer_record(), subject="some.other.subject") is False
    assert binds(issued_against("some.other.subject", answer_digest(answer_record())), answer_record(),
                 subject="some.other.subject") is True


def test_the_default_subject_follows_the_kind_of_output():
    wrong_label = issued_against(FINDING_SUBJECT, answer_digest(answer_record()))
    assert binds(wrong_label, answer_record()) is False
    assert binds(wrong_label, answer_record(), subject=FINDING_SUBJECT) is True


def test_an_unbound_hand_built_verdict_binds_to_nothing():
    unbound = gate.GateResult(gate="test.gate", position=gate.GatePosition.OMEGA, outcome=gate.GateOutcome.PASS)
    assert not unbound.bound()
    assert binds(unbound, answer_record()) is False
    assert binds(unbound, finding_record()) is False
    no_digest = gate.GateResult(gate="g", position=gate.GatePosition.OMEGA, outcome=gate.GateOutcome.PASS,
                                subject=ANSWER_SUBJECT)
    assert binds(no_digest, answer_record()) is False


@pytest.mark.parametrize("bad", [None, "pass", {"subject": "x"}, True])
def test_binds_takes_a_gate_result(bad):
    with pytest.raises(TypeError, match="GateResult"):
        binds(bad, answer_record())


@pytest.mark.parametrize("bad", [None, "text", 3, [answer_record()]])
def test_binds_takes_an_answer_or_a_finding(bad):
    result = issued_against(ANSWER_SUBJECT, answer_digest(answer_record()))
    with pytest.raises(TypeError, match="FindingRecord or an answer-record mapping"):
        binds(result, bad)


# ------------------------------------------------------------ corpus text is never copied

def test_no_corpus_text_appears_in_any_content():
    for content in (answer_content(answer_record()), finding_content(finding_record())):
        assert CANARY not in repr(content)
        assert "seal cracked" not in repr(content) and "coolant" not in repr(content)
    answer = answer_content(answer_record())
    assert answer["question_sha256"] == sha(answer_record()["query"])
    assert answer["answer_sha256"] == sha(answer_record()["answer"])
    assert [e["extract_sha256"] for e in answer["evidence"]] == [sha(f"the seal cracked {CANARY}"), sha("the coolant leaked")]
    finding = finding_content(finding_record())
    assert finding["conclusion_sha256"] == sha(finding_record().conclusion)
    assert [e["source"] for e in finding["evidence"]] == ["a.md", "b.md"]


def test_the_identity_of_the_evidence_is_kept():
    answer = answer_content(answer_record())
    assert [(e["source"], e["date"], e["speaker"]) for e in answer["evidence"]] == [
        ("a.md", "2026-03-02", "user"), ("b.md", "2026-07-09", None)]
    assert finding_content(finding_record())["source_material"] == ["a.md", "b.md"]


# ------------------------------------------------------------ against Ecology's own code

@pytest.fixture
def engine(tmp_path, monkeypatch):
    """The real generate_response over a real Chroma collection of a throwaway corpus, with the embedder and the
    model stubbed the way the repo's own tests stub them."""
    import ollama
    import rag_engine

    def embed(texts):
        return [[1.0 if word in t.lower() else 0.0 for word in ("reactor", "kitchen", "garden")] for t in texts]

    def chat(model, messages, options=None, **kwargs):  # the synthesis simply restates the verified excerpts
        prompt = messages[-1]["content"]
        return {"message": {"content": prompt.split("Verified excerpts:")[1].split("Query:")[0].strip()}}

    monkeypatch.setattr(rag_engine, "_embed", embed)
    monkeypatch.setattr(ollama, "chat", chat)
    monkeypatch.chdir(tmp_path)
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "reactor_log.md").write_text(f"The reactor coolant pump failed because the seal cracked at {CANARY}.\n")
    (corpus / "kitchen.md").write_text("The kitchen schedule lists soup on Tuesday.\n")
    collection = rag_engine.initialize_vector_store(
        directory_path=str(corpus), collection_name="cns_connector_test", db_path=str(tmp_path / "chroma_db"))
    return rag_engine, collection


def test_a_real_answer_from_generate_response_binds_and_is_deterministic(engine):
    rag_engine, collection = engine
    query = "why did the reactor coolant pump fail"
    answer, sources = rag_engine.generate_response(collection, query, n_results=1)
    assert CANARY in answer and sources and sources[0]["source"] == "reactor_log.md"
    record = {"query": query, "answer": answer, "sources": sources}

    content = answer_content(record)
    assert content["verified"] is True and CANARY not in repr(content) and conforms(content)
    again = rag_engine.generate_response(collection, query, n_results=1)
    assert answer_digest({"query": query, "answer": again[0], "sources": again[1]}) == answer_digest(record)

    verdict = issued_against(ANSWER_SUBJECT, answer_digest(record))
    assert binds(verdict, record)
    assert not binds(verdict, {**record, "answer": answer + " (edited afterwards)"})
    assert not binds(verdict, {**record, "query": "why did the kitchen fail"})
    assert not binds(verdict, {**record, "sources": [dict(sources[0], extract="something else")]})


def test_a_real_not_in_corpus_result_binds_and_differs_from_an_answer(engine):
    rag_engine, collection = engine
    query = "what is growing in the garden"
    answer, sources = rag_engine.generate_response(collection, query, n_results=1)
    assert sources == [] and "does not contain a verifiable answer" in answer
    record = {"query": query, "answer": answer, "sources": sources}
    assert answer_content(record)["verified"] is False
    assert binds(issued_against(ANSWER_SUBJECT, answer_digest(record)), record)
    assert not binds(issued_against(ANSWER_SUBJECT, answer_digest(record)), {**record, "query": "what grows in the sea"})


def test_a_real_finding_record_binds(engine):
    rag_engine, collection = engine
    query = "why did the reactor coolant pump fail"
    answer, sources = rag_engine.generate_response(collection, query, n_results=1)
    finding = to_finding_record(answer, sources, n_results=1)
    content = finding_content(finding)
    assert content["verified"] is True and content["confidence"] == 1.0 and CANARY not in repr(content)
    verdict = issued_against(FINDING_SUBJECT, finding_digest(finding))
    assert binds(verdict, finding)
    assert not binds(verdict, dataclasses.replace(finding, conclusion=finding.conclusion + "!"))
    refused = to_finding_record(NOT_IN_CORPUS, [], n_results=1)
    assert finding_content(refused)["verified"] is False and not binds(verdict, refused)
