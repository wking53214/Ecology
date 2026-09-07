"""Ecology's SemanticIndex adapter.

The adapter satisfies CCC's protocol structurally and never imports from CCC.
These tests run without a CCC checkout, which is the point: Ecology must stay
usable on its own, and an adapter that has to import the thing it plugs into
is not decoupled from it.
"""

import pytest

from semantic_index import (
    EcologySemanticIndex,
    SemanticMatch,
    SemanticUnavailable,
    _similarity_from_distance,
)


class _FakeCollection:
    def __init__(self, ids=(), distances=(), fail_on=None):
        self._ids, self._distances, self._fail_on = list(ids), list(distances), fail_on
        self.upserted = []

    def count(self):
        if self._fail_on == "count":
            raise RuntimeError("store gone")
        return len(self._ids)

    def upsert(self, ids, embeddings, documents):
        if self._fail_on == "upsert":
            raise RuntimeError("disk full")
        self.upserted.append(ids[0])

    def query(self, query_embeddings, n_results):
        if self._fail_on == "query":
            raise RuntimeError("index corrupt")
        return {"ids": [self._ids[:n_results]], "distances": [self._distances[:n_results]]}


def _index(collection, embedder=lambda texts: [[0.1, 0.2, 0.3]]):
    index = EcologySemanticIndex(embedder=embedder)
    index._collection = collection
    return index


# ---------------------------------------------------------------------------
# The contract
# ---------------------------------------------------------------------------

def test_query_returns_similarities_not_vectors():
    """CCC receives a similarity and never an embedding, so it never acquires
    an opinion about dimensionality or which model produced it."""
    index = _index(_FakeCollection(ids=["F-1", "F-2"], distances=[0.05, 0.9]))
    matches = index.query("some finding text")

    assert all(isinstance(m, SemanticMatch) for m in matches)
    assert all(set(vars(m)) == {"finding_id", "similarity"} for m in matches)


def test_matches_come_back_strongest_first():
    index = _index(_FakeCollection(ids=["far", "near"], distances=[2.0, 0.01]))
    matches = index.query("text")
    assert [m.finding_id for m in matches] == ["near", "far"]
    assert matches[0].similarity > matches[1].similarity


def test_an_empty_index_returns_nothing_rather_than_failing():
    assert list(_index(_FakeCollection()).query("text")) == []


def test_limit_is_respected():
    index = _index(_FakeCollection(ids=[f"F-{i}" for i in range(50)],
                                   distances=[0.1] * 50))
    assert len(index.query("text", limit=5)) == 5


def test_add_upserts_so_replaying_a_store_does_not_raise():
    """CCC replaying its own store on load would otherwise fail the second
    time it indexed the same finding id."""
    collection = _FakeCollection()
    index = _index(collection)
    index.add("F-1", "text")
    index.add("F-1", "text")
    assert collection.upserted == ["F-1", "F-1"]


# ---------------------------------------------------------------------------
# Distance -> similarity, converted on this side of the boundary
# ---------------------------------------------------------------------------

def test_distance_converts_to_a_bounded_similarity():
    """Which metric the store uses is exactly the implementation detail the
    boundary exists to hide, so the conversion happens here. Out-of-range
    values would silently break any threshold CCC declares."""
    assert _similarity_from_distance(0.0) == 1.0
    assert 0.0 < _similarity_from_distance(1.0) < 1.0
    assert _similarity_from_distance(1e9) >= 0.0
    assert _similarity_from_distance(None) == 0.0
    for d in (-5.0, 0.0, 0.5, 10.0, 1e6):
        assert 0.0 <= _similarity_from_distance(d) <= 1.0


def test_the_conversion_is_true_cosine_not_a_monotonic_stand_in():
    """This model emits unit-normalised vectors, so squared-L2 and cosine are
    related exactly by cos = 1 - d/2. An earlier version used 1/(1+d), which
    ranked correctly and compressed a related pair to 0.428 against an
    unrelated one at 0.379 -- separation 1.13x where cosine gives 1.84x. A
    ranking that is right while the scale is meaningless is the worst case
    for a fixed threshold: the ordering passes a spot check and the gate
    behaves arbitrarily."""
    # measured on real embeddings from this model
    related_distance, unrelated_distance = 1.3379, 1.6396
    related = _similarity_from_distance(related_distance)
    unrelated = _similarity_from_distance(unrelated_distance)

    assert related == pytest.approx(0.3311, abs=1e-3)
    assert unrelated == pytest.approx(0.1802, abs=1e-3)
    assert related / unrelated > 1.5, "discrimination collapsed"


def test_the_provider_publishes_the_range_its_scores_actually_occupy():
    """A threshold no similarity can reach turns semantic recurrence into a
    silent no-op -- everything imports, everything runs, the feature never
    fires. Publishing the observed range is what makes that detectable."""
    from semantic_index import expected_similarity_range
    observed = expected_similarity_range()

    assert observed["paraphrase"] > observed["unrelated"]
    assert observed["paraphrase"] < 0.5, (
        "a real paraphrase scores ~0.33 with this model; anything claiming "
        "otherwise has not been measured"
    )
    assert "provider" in observed and "metric" in observed


def test_closer_is_always_more_similar():
    values = [_similarity_from_distance(d) for d in (0.0, 0.1, 0.5, 1.0, 5.0)]
    assert values == sorted(values, reverse=True)


# ---------------------------------------------------------------------------
# Failure surfaces as SemanticUnavailable, which CCC degrades on
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fail_on", ["count", "query", "upsert"])
def test_store_failures_become_semantic_unavailable(fail_on):
    """CCC distinguishes a declared unavailability from an unanticipated
    crash. Letting a raw RuntimeError escape would land this in the wrong
    bucket and make a routine outage look like a defect."""
    index = _index(_FakeCollection(ids=["F-1"], distances=[0.1], fail_on=fail_on))
    with pytest.raises(SemanticUnavailable):
        if fail_on == "upsert":
            index.add("F-1", "text")
        else:
            index.query("text")


def test_an_embedder_failure_becomes_semantic_unavailable():
    def broken(texts):
        raise RuntimeError("onnx session died")

    index = _index(_FakeCollection(ids=["F-1"], distances=[0.1]), embedder=broken)
    with pytest.raises(SemanticUnavailable):
        index.query("text")


def test_findings_are_indexed_apart_from_conversation_cells():
    """A finding is a conclusion drawn *about* the corpus. Sharing a
    collection would let a raw conversation cell surface as a semantically
    similar prior finding, which it is not."""
    from rag_engine import HISTORY_COLLECTION_NAME
    from semantic_index import DEFAULT_COLLECTION

    assert DEFAULT_COLLECTION != HISTORY_COLLECTION_NAME


def test_the_adapter_does_not_import_ccc():
    """Structural conformance, not inheritance. Ecology stays usable with no
    CCC checkout present."""
    import ast
    import pathlib

    tree = ast.parse(pathlib.Path("semantic_index.py").read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [a.name.split(".")[0] for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [(node.module or "").split(".")[0]]
        else:
            continue
        assert "ccc" not in names, f"adapter imports CCC at line {node.lineno}"
