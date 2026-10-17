"""Optional connector to CNS (``cns.gate``): make Ecology's outputs bindable.

Ecology is independent. It has no runtime dependency on CNS, imports nothing
from CNS when it loads, and its whole suite passes with CNS absent. This module
is the one place that knows CNS exists, and it asks for CNS only when a digest
is requested. The ``*_content`` functions are pure and work without CNS; the
digest and ``binds`` functions raise :class:`CnsNotInstalled`, with the install
command, when CNS is missing. Nothing else in Ecology is affected.

Binding only
------------
CNS's shared gate contract is ``cns.gate.GateResult``. A verdict carries a
``subject`` label and a ``subject_digest``, and ``GateResult.binds`` says
whether the verdict was issued against exactly that content. This module lets
a verdict about an Ecology output be checked against the output: nothing more.
It is not a gate, it maps nothing to a verdict, and it takes no position on
whether an answer is right. A bound verdict says which answer it was about, not
that the answer deserved to pass.

What is bound
-------------
* An answer record (:func:`answer_content`): a mapping with ``query``,
  ``answer`` and ``sources``, which is what ``rag_engine.generate_response``
  returns plus the question that was asked. It binds the question hash, the
  answer hash and each cited excerpt as ``(source, extract hash, date,
  speaker)``. An honest "not in corpus" result is the same record with no
  sources; ``verified`` says which it is.
* A finding record (:func:`finding_content`): a ``finding.FindingRecord``, the
  stable shape Ecology hands to governance consumers.

The corpus is personal and cannot ship, so no corpus text is copied into the
bound content: the question, the answer and every extract are bound as full
SHA-256 hex digests. A source path is an identifier and is kept as written,
because it is how a reader finds the evidence. Evidence keeps the order given
(retrieval rank); ``source_material`` is a set of sources and is sorted.

Install with: ``pip install -r requirements-cns.txt``.
"""
from __future__ import annotations

import hashlib
import importlib
from collections.abc import Mapping
from types import ModuleType
from typing import Any, Optional

from finding import FindingRecord

__all__ = [
    "ANSWER_SUBJECT",
    "FINDING_SUBJECT",
    "CnsNotInstalled",
    "answer_content",
    "answer_digest",
    "binds",
    "cns_available",
    "finding_content",
    "finding_digest",
]

INSTALL_HINT = "pip install -r requirements-cns.txt"

ANSWER_SUBJECT = "ecology.answer"
FINDING_SUBJECT = "ecology.finding"


class CnsNotInstalled(ImportError):
    """Raised by this module's digest functions when ``cns`` cannot be imported."""


def _cns_gate() -> ModuleType:
    """Import ``cns.gate`` on demand, or say exactly what is missing."""
    try:
        return importlib.import_module("cns.gate")
    except ImportError as exc:
        raise CnsNotInstalled(
            "ecology_cns_connector needs the CNS package (cns.gate), which is not "
            f"installed. Install it with: {INSTALL_HINT}. Ecology itself works "
            "without it."
        ) from exc


def cns_available() -> bool:
    """Whether the CNS gate contract can be imported in this environment."""
    try:
        _cns_gate()
    except CnsNotInstalled:
        return False
    return True


def _text(value: object, what: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{what} must be a str; got {type(value).__name__}")
    return value


def _hash(value: object, what: str) -> str:
    """Full SHA-256 of a text. Corpus text is bound by this and never copied."""
    # surrogatepass: exported chats can hold lone surrogates, which must hash rather than raise
    return hashlib.sha256(_text(value, what).encode("utf-8", "surrogatepass")).hexdigest()


def _optional_text(value: object, what: str) -> Optional[str]:
    return None if value is None else _text(value, what)


def _items(value: object, what: str) -> list:
    if not isinstance(value, (list, tuple)):
        raise TypeError(f"{what} must be a list or tuple; got {type(value).__name__}")
    return list(value)


def answer_content(record: Mapping) -> dict:
    """The content a verdict on an answer is bound to.

    ``record`` is a mapping with ``query`` (str), ``answer`` (str) and
    ``sources`` (the list ``generate_response`` returns: dicts with ``source``
    and optionally ``extract``, ``date`` and ``speaker``). Extra keys are not
    part of what is bound.
    """
    if not isinstance(record, Mapping):
        raise TypeError(f"an answer record is a mapping; got {type(record).__name__}")
    missing = [key for key in ("query", "answer", "sources") if key not in record]
    if missing:
        raise ValueError(f"answer record is missing required key(s): {', '.join(missing)}")
    evidence = []
    for i, item in enumerate(_items(record["sources"], "sources")):
        if not isinstance(item, Mapping):
            raise TypeError(f"sources[{i}] must be a mapping; got {type(item).__name__}")
        if "source" not in item:
            raise ValueError(f"sources[{i}] is missing required key: source")
        extract = item.get("extract")
        evidence.append({
            "source": _text(item["source"], f"sources[{i}]['source']"),
            "extract_sha256": None if extract is None else _hash(extract, f"sources[{i}]['extract']"),
            "date": _optional_text(item.get("date"), f"sources[{i}]['date']"),
            "speaker": _optional_text(item.get("speaker"), f"sources[{i}]['speaker']"),
        })
    return {
        "question_sha256": _hash(record["query"], "query"),
        "answer_sha256": _hash(record["answer"], "answer"),
        "verified": bool(evidence),
        "evidence": evidence,
    }


def finding_content(record: FindingRecord) -> dict:
    """The content a verdict on a ``FindingRecord`` is bound to."""
    if not isinstance(record, FindingRecord):
        raise TypeError(f"a finding record is a finding.FindingRecord; got {type(record).__name__}")
    confidence = record.confidence
    if confidence is not None and (isinstance(confidence, bool) or not isinstance(confidence, (int, float))):
        raise TypeError(f"confidence must be a number or None; got {type(confidence).__name__}")
    if not isinstance(record.verified, bool):
        raise TypeError(f"verified must be a bool; got {type(record.verified).__name__}")
    evidence = []
    for i, pair in enumerate(_items(record.evidence, "evidence")):
        pair = _items(pair, f"evidence[{i}]")
        if len(pair) != 2:
            raise TypeError(f"evidence[{i}] must be a (source, extract) pair")
        evidence.append({
            "source": _text(pair[0], f"evidence[{i}] source"),
            "extract_sha256": _hash(pair[1], f"evidence[{i}] extract"),
        })
    return {
        "conclusion_sha256": _hash(record.conclusion, "conclusion"),
        "method": _text(record.method, "method"),
        "source_material": sorted(_text(s, "source_material item") for s in _items(record.source_material, "source_material")),
        "confidence": None if confidence is None else float(confidence),
        "verified": record.verified,
        "evidence": evidence,
        "event_start_date": _optional_text(record.event_start_date, "event_start_date"),
        "event_end_date": _optional_text(record.event_end_date, "event_end_date"),
    }


def answer_digest(record: Mapping) -> str:
    """The digest a bound verdict on this answer record carries."""
    return _cns_gate().subject_digest(answer_content(record))


def finding_digest(record: FindingRecord) -> str:
    """The digest a bound verdict on this finding record carries."""
    return _cns_gate().subject_digest(finding_content(record))


def binds(result: Any, output: object, *, subject: Optional[str] = None) -> bool:
    """True iff ``result`` (a ``cns.gate.GateResult``) was issued against exactly this output.

    ``output`` is a ``FindingRecord`` or an answer-record mapping; ``subject``
    defaults to ``FINDING_SUBJECT`` or ``ANSWER_SUBJECT`` to match. A verdict
    that records nothing it judged (unbound) never binds.
    """
    gate = _cns_gate()
    if not isinstance(result, gate.GateResult):
        raise TypeError(f"binds takes a cns.gate.GateResult; got {type(result).__name__}")
    if isinstance(output, FindingRecord):
        default, digest = FINDING_SUBJECT, finding_digest(output)
    elif isinstance(output, Mapping):
        default, digest = ANSWER_SUBJECT, answer_digest(output)
    else:
        raise TypeError(f"binds takes a FindingRecord or an answer-record mapping; got {type(output).__name__}")
    return result.binds(default if subject is None else subject, digest)
