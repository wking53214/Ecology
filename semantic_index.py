"""Ecology's implementation of CCC's SemanticIndex protocol.

CCC declares the interface and owns the policy; this owns the model. The
dependency arrow points at CCC and never away from it, which is why this file
lives here and not there:

    CCC  ──defines──►  SemanticIndex (Protocol)
                              ▲
                              │ implements
                        this module
                              │
                    ONNX MiniLM + Chroma

Nothing in `ccc/` imports this. Application wiring constructs it and hands it
in; CCC never learns that the vectors are 384-dimensional, that MiniLM
produced them, or that Chroma stores them. It receives similarities and
applies its own threshold.

Structural conformance, not inheritance
---------------------------------------
`SemanticIndex` is a Protocol, so this class satisfies it by having the two
methods. It deliberately does **not** import from CCC -- an adapter that has
to import the thing it plugs into is not decoupled from it, and Ecology
should remain usable with no CCC checkout present. `SemanticMatch` is
duck-typed the same way `FindingRecord` already is at the other seam.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence

DEFAULT_COLLECTION = "ccc_findings_v1"


@dataclass(frozen=True)
class SemanticMatch:
    """Structurally CCC's `SemanticMatch`, built here rather than imported.

    Two fields, and no vector among them: the contract is a similarity, not
    an embedding.
    """
    finding_id: str
    similarity: float


class SemanticUnavailable(Exception):
    """Raised when the model or store cannot answer.

    Named to match CCC's own `SemanticUnavailable` so its handler recognises
    a declared unavailability rather than an unanticipated crash -- the two
    degrade identically but are recorded differently, and only one is worth
    investigating.
    """


class EcologySemanticIndex:
    """Semantic recurrence provider backed by the local ONNX embedder.

    Uses the same in-process all-MiniLM-L6-v2 that `rag_engine` uses for the
    conversation corpus -- no ollama server, no torch. Findings are indexed
    into their own collection, separate from the conversation cells: a
    finding is a conclusion drawn *about* the corpus, and mixing the two
    would let a raw conversation cell surface as a semantically similar
    prior *finding*, which it is not.
    """

    provider_name = "ecology-minilm-onnx"

    def __init__(self, collection_name: str = DEFAULT_COLLECTION,
                 db_path: str = "./chroma_db", embedder=None):
        self._collection_name = collection_name
        self._db_path = db_path
        self._embedder = embedder
        self._collection = None

    # -- lazy wiring ---------------------------------------------------------

    def _embed(self, text: str) -> List[float]:
        if self._embedder is None:
            try:
                from rag_engine import _embed as engine_embed
            except Exception as exc:  # noqa: BLE001
                raise SemanticUnavailable(f"embedder unavailable: {exc}") from exc
            self._embedder = engine_embed
        try:
            return self._embedder([text])[0]
        except Exception as exc:  # noqa: BLE001
            raise SemanticUnavailable(f"embedding failed: {exc}") from exc

    def _get_collection(self):
        if self._collection is None:
            try:
                import chromadb
                client = chromadb.PersistentClient(path=self._db_path)
                self._collection = client.get_or_create_collection(
                    name=self._collection_name)
            except Exception as exc:  # noqa: BLE001
                raise SemanticUnavailable(f"vector store unavailable: {exc}") from exc
        return self._collection

    # -- the protocol --------------------------------------------------------

    def add(self, finding_id: str, text: str) -> None:
        """Index a finding for future semantic recurrence queries.

        Upserts rather than adds: re-recording the same finding id must not
        raise, because CCC replaying its own store on load would otherwise
        fail on the second pass.
        """
        collection = self._get_collection()
        vector = self._embed(text)
        try:
            collection.upsert(ids=[finding_id], embeddings=[vector], documents=[text])
        except Exception as exc:  # noqa: BLE001
            raise SemanticUnavailable(f"index write failed: {exc}") from exc

    def query(self, text: str, *, limit: int = 10) -> Sequence[SemanticMatch]:
        """Semantically similar prior findings, strongest first."""
        collection = self._get_collection()
        try:
            if collection.count() == 0:
                return []
        except Exception as exc:  # noqa: BLE001
            raise SemanticUnavailable(f"index unreadable: {exc}") from exc

        vector = self._embed(text)
        try:
            result = collection.query(query_embeddings=[vector],
                                      n_results=min(limit, collection.count()))
        except Exception as exc:  # noqa: BLE001
            raise SemanticUnavailable(f"query failed: {exc}") from exc

        ids = (result.get("ids") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]
        matches = [
            SemanticMatch(finding_id=fid, similarity=_similarity_from_distance(d))
            for fid, d in zip(ids, distances)
        ]
        matches.sort(key=lambda m: m.similarity, reverse=True)
        return matches


# Observed range for this embedder, measured rather than assumed. A
# genuinely-related paraphrase sharing almost no vocabulary scores ~0.33; an
# unrelated pair from the same domain scores ~0.18. Published so a threshold
# can be set against evidence instead of intuition -- see
# `expected_similarity_range()` and the note in CCC's semantic module.
OBSERVED_PARAPHRASE_SIMILARITY = 0.33
OBSERVED_UNRELATED_SIMILARITY = 0.18


def expected_similarity_range() -> dict:
    """What this provider's similarities actually look like.

    Exists because a threshold that no similarity can ever reach turns
    semantic recurrence into a silent no-op: everything imports, everything
    runs, and the feature never fires. A consumer can compare its declared
    threshold against these numbers and notice.
    """
    return {
        "provider": EcologySemanticIndex.provider_name,
        "metric": "cosine, floored at 0",
        "paraphrase": OBSERVED_PARAPHRASE_SIMILARITY,
        "unrelated": OBSERVED_UNRELATED_SIMILARITY,
        "note": (
            "all-MiniLM-L6-v2 scores a real paraphrase near 0.33, not near "
            "0.9. A threshold above ~0.5 will never fire on this provider."
        ),
    }


def _similarity_from_distance(distance: Optional[float]) -> float:
    """Chroma reports squared L2 distance; CCC's threshold is a similarity.

    Converted here rather than in CCC, because which distance metric the
    store uses is exactly the implementation detail the boundary exists to
    hide.

    This model emits unit-normalised vectors (measured: norm 1.0000), and for
    unit vectors squared-L2 and cosine are exactly related by
    ``cos = 1 - d/2``. So the conversion is not an approximation.

    An earlier version used ``1/(1+d)``, which is monotonic and therefore
    ranked correctly -- and destroyed most of the discrimination anyway,
    compressing a related pair to 0.428 and an unrelated one to 0.379.
    Separation went from 1.84x under cosine to 1.13x. A ranking that is right
    while the scale is meaningless is the worst case for a fixed threshold:
    the ordering looks fine in a spot check and the gate behaves arbitrarily.

    Floored at 0 -- a negative cosine means "pointing the other way", which
    for recurrence purposes is simply unrelated, and letting it go negative
    would make the value harder to reason about at no benefit.
    """
    if distance is None:
        return 0.0
    cosine = 1.0 - (float(distance) / 2.0)
    return max(0.0, min(1.0, cosine))
