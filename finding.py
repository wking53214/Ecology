"""Stable output contract for downstream governance consumers.

generate_response() returns a synthesized answer plus the sources that
passed containment verification. That's the right shape for a human reading
a terminal, but a governance system (CCC or otherwise) needs a stable,
generic record it can consume without depending on Ecology's internals --
and Ecology should not need to know CCC, or any other consumer, exists.
This is the seam between the two: owned here, on Ecology's side.
"""
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class FindingRecord:
    """A generic, consumer-agnostic shape for one retrieval result.

    `confidence` is derived, not asserted: the fraction of retrieved
    candidates that actually passed containment verification. It is not a
    claim about correctness, only about how much of what was retrieved held
    up under the one check Ecology actually performs.
    """
    conclusion: str
    method: str
    source_material: Tuple[str, ...]
    confidence: Optional[float]
    verified: bool


def to_finding_record(answer: str, sources: list, n_results: int,
                       model_name: str = "llama3.2") -> FindingRecord:
    """Package a generate_response() result into a stable FindingRecord.

    verified=False and confidence=None when nothing passed verification --
    an honest non-answer must not be dressed up as a low-confidence finding.
    """
    verified_count = len(sources)
    verified = verified_count > 0
    confidence = (verified_count / n_results) if verified and n_results else None
    return FindingRecord(
        conclusion=answer,
        method=f"ecology.rag_engine.generate_response(model={model_name}, n_results={n_results})",
        source_material=tuple(sorted({s["source"] for s in sources})),
        confidence=confidence,
        verified=verified,
    )
