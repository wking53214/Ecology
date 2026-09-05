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

    `confidence` is derived, not asserted: the fraction of the requested
    search width covered by *distinct* verified sources. Counted by
    distinct source, not by verified chunk -- three verified paragraphs
    from the same document are one source, not three, and a confidence
    number that counted them as three would tell a different, inflated
    story than `source_material` (which was already deduped) tells right
    next to it. It is not a claim about correctness, only about how much
    independent source material held up under the one check Ecology
    actually performs.

    `evidence` carries each individually-verified excerpt's own text, not
    just its source path. A consumer with real evidence-linking (attach
    each excerpt as its own item, not one collapsed number) needs the
    actual verified content to attach -- collapsing to a single float here
    would throw that structure away before it ever reached the consumer.
    """
    conclusion: str
    method: str
    source_material: Tuple[str, ...]
    confidence: Optional[float]
    verified: bool
    evidence: Tuple[Tuple[str, str], ...] = ()  # (source, extract) pairs


def to_finding_record(answer: str, sources: list, n_results: int,
                       model_name: str = "llama3.2") -> FindingRecord:
    """Package a generate_response() result into a stable FindingRecord.

    verified=False and confidence=None when nothing passed verification --
    an honest non-answer must not be dressed up as a low-confidence finding.
    `sources` items carrying an "extract" key (as generate_response() now
    returns) populate `evidence`; older callers passing bare {"source": ...}
    dicts still work, just without per-excerpt evidence.
    """
    verified = len(sources) > 0
    distinct_sources = tuple(sorted({s["source"] for s in sources}))
    confidence = (len(distinct_sources) / n_results) if verified and n_results else None
    return FindingRecord(
        conclusion=answer,
        method=f"ecology.rag_engine.generate_response(model={model_name}, n_results={n_results})",
        source_material=distinct_sources,
        confidence=confidence,
        verified=verified,
        evidence=tuple((s["source"], s["extract"]) for s in sources if "extract" in s),
    )
