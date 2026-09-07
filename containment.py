"""Deterministic containment verification.

Answers one narrow question about a retrieved passage:

    Does this passage contain evidence relevant to this query?

It does **not** claim the passage is true, that an inferred proposition is
correct, or that the answer is complete. Those are different questions, and
conflating them is how a retrieval layer starts manufacturing evidence.

Why deterministic
-----------------
The previous verifier made two LLM calls per candidate passage -- a relevance
classification and an extraction. Measured on this machine: a two-passage
query did not finish in 120 seconds, which meant the Ecology -> CCC path had
never once completed on real data. Retrieval itself takes 0.08s (lexical) to
2.1s (vector). Verification was the whole wall.

This runs in microseconds and is stdlib-only.

Precision over recall, deliberately
-----------------------------------
The asymmetry is not a preference, it follows from what sits downstream:

    retrieval -> containment -> FindingRecord -> CCC -> ANOMALY -> PATTERN

A missed passage costs one candidate. A falsely admitted passage becomes
apparently-corroborating evidence, and CCC's recurrence engine counts it
toward a pattern that may not exist. One failure loses information; the other
manufactures it. So every gate here is a hard reject, not a score penalty.

CALIBRATION STATUS: UNCALIBRATED
--------------------------------
The weights and thresholds below are reasoned defaults, not measured ones.
They have not been fitted against labelled data, and the tests that ship with
this module were written from the same design as the code -- they prove the
design was implemented, not that it is correct. Treat every constant in
`Thresholds` as a policy parameter awaiting evidence, and see
`scripts/calibrate_containment.py` for scoring against real corpus passages
rather than against examples this module's author invented.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Optional, Sequence

# ---------------------------------------------------------------------------
# Policy parameters
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Thresholds:
    """Every number the verifier's behaviour depends on, in one place.

    Grouped here rather than scattered as literals so that a calibration run
    can vary them, and so nobody has to grep for magic constants to find out
    what the verifier's policy actually is.
    """

    # Composite score weights. Must sum to 1.0.
    w_coverage: float = 0.40
    w_anchor: float = 0.25
    w_proximity: float = 0.15
    w_intent: float = 0.15
    w_phrase: float = 0.05

    # Hard gates. Each one is a reject, not a penalty.
    min_matched_weight: float = 0.40   # gate 1: content evidence
    min_anchor_score: float = 0.50     # gate 2: distinctive term present
    min_score: float = 0.68            # gate 3: final confidence

    # Match credit by how the token was recognised.
    exact_credit: float = 1.00
    morphological_credit: float = 0.85
    synonym_credit: float = 0.70

    # Token weighting.
    ordinary_weight: float = 1.0
    distinctive_weight: float = 3.0

    # Window search.
    max_window_sentences: int = 4
    window_length_penalty: float = 0.03

    def __post_init__(self) -> None:
        total = (self.w_coverage + self.w_anchor + self.w_proximity
                 + self.w_intent + self.w_phrase)
        if abs(total - 1.0) > 1e-9:
            raise ValueError(f"composite weights must sum to 1.0, got {total}")


DEFAULT = Thresholds()


# ---------------------------------------------------------------------------
# Normalisation
# ---------------------------------------------------------------------------

_TOKEN = re.compile(r"[a-z0-9]+(?:['\-][a-z0-9]+)?")

# Conversational stopwords. Question words are NOT here -- they carry intent
# and are classified separately below.
_STOPWORDS = frozenset("""
the a an is are was were be been being am
this that these those it its
we they them he she you i me my our your their his her
and or but if then than so
to of in on for with from at by about into over under
do did does done doing
can could would should will shall may might must
have has had having
not no nor
there here what's it's don't didn't
""".split())

# Question words -> the structural relationship the query is asking about.
_INTENT = {
    "why": "rationale",
    "how": "mechanism",
    "when": "temporal",
    "where": "location",
    "who": "actor",
    "whether": "decision",
    "which": "selection",
    "what": "identity",
}

# Small, curated, explainable. Deliberately not a thesaurus: every entry here
# is a claim that two words mean the same thing for verification purposes, and
# a wrong claim admits false evidence.
_SYNONYM_CLASSES = {
    "choose": {"choose", "chose", "chosen", "choosing", "select", "selects",
               "selected", "selecting", "pick", "picked", "picking",
               "decide", "decided", "deciding", "go", "went", "opt", "opted"},
    "decision": {"decision", "decide", "decided", "choice", "call", "verdict",
                 "chose", "chosen", "selected", "picked", "settled"},
    "reason": {"reason", "reasons", "because", "why", "rationale", "cause",
               "due", "since", "motivated", "motivation", "justification"},
    "reject": {"reject", "rejected", "rejecting", "discard", "discarded",
               "drop", "dropped", "dropping", "avoid", "avoided", "ruled",
               "abandon", "abandoned"},
    "implement": {"implement", "implemented", "implementing", "build", "built",
                  "building", "add", "added", "adding", "integrate",
                  "integrated", "wire", "wired", "create", "created"},
    "change": {"change", "changed", "changing", "switch", "switched", "move",
               "moved", "migrate", "migrated", "replace", "replaced"},
}

# Multi-word phrases that signal a decision was made. Checked as phrases
# because the individual words are unremarkable: "the call was to go with X"
# contains no decision verb at all.
_DECISION_PHRASES = (
    "call was to", "went with", "settled on", "decided on", "opted for",
    "we chose", "we picked", "we selected", "ended up using",
    "the decision was", "agreed to use", "landed on",
)

_RATIONALE_MARKERS = (
    "because", "since", "due to", "so that", "in order to", "the reason",
    "rationale", "which is why", "as a result of", "on the grounds",
)

# Reverse index: token -> the classes it belongs to.
_TOKEN_TO_CLASSES: dict[str, set[str]] = {}
for _cls, _members in _SYNONYM_CLASSES.items():
    for _m in _members:
        _TOKEN_TO_CLASSES.setdefault(_m, set()).add(_cls)


def normalize(text: str) -> str:
    """NFKC, lowercase, and unify the punctuation that varies by keyboard."""
    text = unicodedata.normalize("NFKC", text)
    text = (text.replace("’", "'").replace("‘", "'")
                .replace("“", '"').replace("”", '"')
                .replace("—", "-").replace("–", "-"))
    return text.lower()


def tokenize(text: str) -> list[str]:
    return _TOKEN.findall(normalize(text))


_SUFFIXES = ("ingly", "edly", "ing", "ed", "es", "s", "ly", "ion", "ions",
             "ment", "ments")


def stem(token: str) -> str:
    """A conservative suffix trim, not a full Porter stemmer.

    Aggressive stemming manufactures matches -- it is how "universal" and
    "universe" become the same concept. This only strips suffixes when a
    reasonable stem remains, and never below four characters.
    """
    for suffix in _SUFFIXES:
        if token.endswith(suffix) and len(token) - len(suffix) >= 4:
            return token[: -len(suffix)]
    return token


# ---------------------------------------------------------------------------
# Distinctiveness
# ---------------------------------------------------------------------------

_CAMEL = re.compile(r"[a-z][A-Z]")
_VERSION = re.compile(r"\bv?\d+\.\d+")


def is_distinctive(raw_token: str) -> bool:
    """Whether a token is specific enough to anchor a match.

    An anchor is the difference between "this passage is about the thing I
    asked about" and "this passage shares some English with my question".
    Deliberately conservative: over-marking tokens as distinctive makes the
    anchor gate easy to satisfy, which is the gate doing the most work.
    """
    if len(raw_token) < 2:
        return False
    if raw_token.isupper() and len(raw_token) >= 2:      # SQLITE, CCC, GSA
        return True
    if _CAMEL.search(raw_token):                          # CamelCase
        return True
    if "_" in raw_token or "-" in raw_token:              # snake_case, kebab
        return True
    if "/" in raw_token or "." in raw_token.strip("."):   # paths, modules
        return True
    if _VERSION.search(raw_token):                        # v1.2, 3.14
        return True
    if any(c.isdigit() for c in raw_token):
        return True
    if len(raw_token) >= 9:                               # long uncommon word
        return True
    return False


_SEPARATORS = re.compile(r"[_\-./]")


def compound_parts(token: str) -> tuple[str, ...]:
    """The components of a separator-joined technical term.

    Found by calibration against the real corpus, not by design: a query for
    `event-time` matched *nothing* in 10 retrieved passages, because the
    corpus writes the same concept as "event time", "event_time" and
    "eventTime" depending on who was typing. Treating `event-time` as one
    opaque token makes its own anchor unmatchable, which turns the gate meant
    to require evidence into a gate that refuses everything.

    Components are only credited when they appear *adjacently* in the passage
    (see `_adjacent_run`), so this recovers the real match without letting a
    passage that merely contains "event" somewhere and "time" elsewhere claim
    the anchor.
    """
    if not _SEPARATORS.search(token):
        return ()
    parts = tuple(p for p in _SEPARATORS.split(token) if len(p) >= 2)
    return parts if len(parts) >= 2 else ()


@dataclass(frozen=True)
class QueryConcepts:
    """What the query is actually asking, decomposed."""
    tokens: tuple[str, ...]
    stems: tuple[str, ...]
    weights: dict[str, float]
    anchors: frozenset[str]
    classes: frozenset[str]
    intents: frozenset[str]
    total_weight: float
    # token -> its separator-split components, for compound technical terms.
    compounds: dict[str, tuple[str, ...]] = field(default_factory=dict)


def extract_concepts(query: str, thresholds: Thresholds = DEFAULT) -> QueryConcepts:
    raw_tokens = re.findall(r"[A-Za-z0-9]+(?:[_\-./'][A-Za-z0-9]+)*", query)
    tokens, weights, anchors, classes, intents = [], {}, set(), set(), set()

    for raw in raw_tokens:
        lowered = normalize(raw)
        if lowered in _INTENT:
            intents.add(_INTENT[lowered])
            continue
        if lowered in _STOPWORDS:
            continue
        tokens.append(lowered)
        distinctive = is_distinctive(raw)
        weights[lowered] = (thresholds.distinctive_weight if distinctive
                            else thresholds.ordinary_weight)
        if distinctive:
            anchors.add(lowered)
        classes.update(_TOKEN_TO_CLASSES.get(lowered, ()))

    # A query naming a choice is asking about a decision even without "why".
    if classes & {"choose", "decision"}:
        intents.add("decision")

    return QueryConcepts(
        tokens=tuple(tokens),
        stems=tuple(stem(t) for t in tokens),
        weights=weights,
        anchors=frozenset(anchors),
        classes=frozenset(classes),
        intents=frozenset(intents),
        total_weight=sum(weights.values()) or 1.0,
        compounds={t: compound_parts(t) for t in tokens if compound_parts(t)},
    )


def _adjacent_run(parts: Sequence[str], tokens: Sequence[str],
                  max_gap: int = 1) -> bool:
    """Whether `parts` appear in order and close together in `tokens`.

    Adjacency is what keeps the compound relaxation honest. "event time" is
    the same concept as `event-time`; an "event" in one paragraph and a "time"
    in another is not, and crediting the latter would hand the anchor gate to
    any passage containing two common words.
    """
    part_stems = [stem(p) for p in parts]
    positions: list[list[int]] = []
    for want, want_stem in zip(parts, part_stems):
        hits = [i for i, tok in enumerate(tokens)
                if tok == want or stem(tok) == want_stem]
        if not hits:
            return False
        positions.append(hits)
    # Greedy forward walk: each part must follow the previous within max_gap.
    for start in positions[0]:
        cursor = start
        ok = True
        for hits in positions[1:]:
            nxt = next((h for h in hits if cursor < h <= cursor + max_gap + 1), None)
            if nxt is None:
                ok = False
                break
            cursor = nxt
        if ok:
            return True
    return False


# ---------------------------------------------------------------------------
# Sentence segmentation
# ---------------------------------------------------------------------------

_ABBREV = {"mr", "mrs", "ms", "dr", "prof", "sr", "jr", "st", "vs", "etc",
           "e.g", "i.e", "approx", "fig", "no", "vol", "inc", "ltd", "co"}


def split_sentences(passage: str) -> list[tuple[int, int]]:
    """(start, end) character spans. Protects abbreviations and decimals.

    Spans rather than strings so the returned evidence is a genuine substring
    of the passage -- a verifier that reconstructs its own quote is not
    verifying containment, it is paraphrasing.
    """
    spans, start, i, n = [], 0, 0, len(passage)
    while i < n:
        ch = passage[i]
        if ch in ".?!":
            # decimal number: 3.14
            if (ch == "." and 0 < i < n - 1
                    and passage[i - 1].isdigit() and passage[i + 1].isdigit()):
                i += 1
                continue
            # abbreviation
            if ch == ".":
                back = passage[max(0, i - 6):i]
                word = re.split(r"[^A-Za-z.]", back)[-1].lower().strip(".")
                if word in _ABBREV:
                    i += 1
                    continue
            j = i + 1
            while j < n and passage[j] in ".?!\"')]":
                j += 1
            if j >= n or passage[j].isspace():
                if passage[start:j].strip():
                    spans.append((start, j))
                while j < n and passage[j].isspace():
                    j += 1
                start = j
                i = j
                continue
        elif ch == "\n":
            # A blank line or a bullet/speaker label starts a new unit.
            j = i + 1
            while j < n and passage[j] in " \t":
                j += 1
            if (j < n and (passage[j] == "\n" or passage[j] in "-*•>"
                           or passage[j : j + 2] == "**")):
                if passage[start:i].strip():
                    spans.append((start, i))
                while j < n and passage[j].isspace():
                    j += 1
                start = j
                i = j
                continue
        i += 1
    if passage[start:].strip():
        spans.append((start, n))
    return spans


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class VerificationResult:
    """Why a passage was admitted or refused.

    The public interface returns `str | None`, but this object is the reason,
    and it is kept because a verifier that cannot explain itself is one more
    thing that has to be trusted. Every component is reproducible from the
    query and passage alone.
    """
    accepted: bool
    score: float = 0.0
    content_coverage: float = 0.0
    anchor_score: float = 0.0
    proximity_score: float = 0.0
    intent_score: float = 0.0
    phrase_score: float = 0.0
    matched_weight: float = 0.0
    matched_concepts: tuple[str, ...] = ()
    span: Optional[tuple[int, int]] = None
    sentence_start: int = -1
    sentence_end: int = -1
    rejected_by: str = ""


def _match_credit(token: str, token_stem: str, sentence_tokens: set[str],
                  sentence_stems: set[str], sentence_classes: set[str],
                  concepts: QueryConcepts, t: Thresholds,
                  ordered_tokens: Sequence[str] = ()) -> float:
    if token in sentence_tokens:
        return t.exact_credit
    if token_stem in sentence_stems:
        return t.morphological_credit
    # A compound technical term written the other way round: `event-time` in
    # the query against "event time" in the passage. Credited at the
    # morphological rate, and only when the components are adjacent -- see
    # compound_parts() for why this exists and _adjacent_run() for what stops
    # it becoming a free pass.
    parts = concepts.compounds.get(token)
    if parts and ordered_tokens and _adjacent_run(parts, ordered_tokens):
        return t.morphological_credit
    for cls in _TOKEN_TO_CLASSES.get(token, ()):
        if cls in sentence_classes:
            return t.synonym_credit
    return 0.0


def _proximity(positions: Sequence[int]) -> float:
    """How close together the matching terms are, in words.

    Terms scattered across 4,000 characters are much weaker evidence than the
    same terms in one clause, and without this a long passage wins by simply
    containing more words.
    """
    if len(positions) < 2:
        return 1.0
    spread = max(positions) - min(positions)
    if spread <= 8:
        return 1.0
    if spread <= 20:
        return 0.8
    if spread <= 50:
        return 0.5
    return 0.1


def _score_text(text: str, concepts: QueryConcepts, t: Thresholds) -> dict:
    lowered = normalize(text)
    tokens = _TOKEN.findall(lowered)
    token_set = set(tokens)
    stem_set = {stem(x) for x in tokens}
    classes: set[str] = set()
    for tok in token_set:
        classes.update(_TOKEN_TO_CLASSES.get(tok, ()))

    matched_weight = 0.0
    matched: list[str] = []
    positions: list[int] = []
    for token, token_stem in zip(concepts.tokens, concepts.stems):
        credit = _match_credit(token, token_stem, token_set, stem_set, classes,
                               concepts, t, tokens)
        if credit > 0:
            matched_weight += concepts.weights[token] * credit
            matched.append(token)
            for idx, tok in enumerate(tokens):
                if tok == token or stem(tok) == token_stem:
                    positions.append(idx)
                    break

    coverage = min(matched_weight / concepts.total_weight, 1.0)

    if concepts.anchors:
        def _anchor_present(a: str) -> bool:
            if a in token_set or stem(a) in stem_set:
                return True
            parts = concepts.compounds.get(a)
            return bool(parts) and _adjacent_run(parts, tokens)
        hit = sum(1 for a in concepts.anchors if _anchor_present(a))
        anchor = hit / len(concepts.anchors)
    else:
        anchor = 1.0  # no anchor to require

    has_decision = (any(p in lowered for p in _DECISION_PHRASES)
                    or bool(classes & {"choose", "decision"}))
    has_rationale = (any(m in lowered for m in _RATIONALE_MARKERS)
                     or "reason" in classes)

    # Intent is scored against what the query asked for. A query asking WHY
    # something was chosen needs BOTH the decision and its reason present --
    # rationale alone is Test 6, a reason for a choice nobody established was
    # made, and decision alone answers a different question than the one asked.
    wants_rationale = "rationale" in concepts.intents
    wants_decision = "decision" in concepts.intents
    if wants_rationale and wants_decision:
        intent = 1.0 if (has_decision and has_rationale) else (
            0.35 if (has_decision or has_rationale) else 0.0)
    elif wants_decision:
        intent = 1.0 if has_decision else 0.0
    elif wants_rationale:
        intent = 1.0 if has_rationale else 0.0
    elif concepts.intents:
        intent = 0.5           # an intent we do not model structurally
    else:
        intent = 0.5           # no interrogative: neutral

    phrase = 1.0 if any(p in lowered for p in _DECISION_PHRASES) else 0.0

    proximity = _proximity(positions)
    score = (t.w_coverage * coverage + t.w_anchor * anchor
             + t.w_proximity * proximity + t.w_intent * intent
             + t.w_phrase * phrase)

    return {
        "score": score, "coverage": coverage, "anchor": anchor,
        "proximity": proximity, "intent": intent, "phrase": phrase,
        "matched_weight": matched_weight, "matched": tuple(matched),
        "has_decision": has_decision, "has_rationale": has_rationale,
    }


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def verify_detailed(query: str, passage: str,
                    thresholds: Thresholds = DEFAULT) -> VerificationResult:
    """Full result, including why a passage was refused."""
    concepts = extract_concepts(query, thresholds)
    if not concepts.tokens:
        return VerificationResult(accepted=False, rejected_by="empty_query")

    spans = split_sentences(passage)
    if not spans:
        return VerificationResult(accepted=False, rejected_by="empty_passage")

    best = None
    for i in range(len(spans)):
        for size in range(1, thresholds.max_window_sentences + 1):
            j = i + size
            if j > len(spans):
                break
            start, end = spans[i][0], spans[j - 1][1]
            scored = _score_text(passage[start:end], concepts, thresholds)
            adjusted = scored["score"] - thresholds.window_length_penalty * (size - 1)
            key = (adjusted, scored["anchor"], -size, -i)
            if best is None or key > best[0]:
                best = (key, scored, adjusted, (start, end), i, j - 1)

    _key, scored, adjusted, span, s_start, s_end = best

    # Hard gates, in order of how cheaply they refuse. Each is a reject on its
    # own -- a high composite score does not buy past a missing anchor.
    if scored["matched_weight"] < thresholds.min_matched_weight * concepts.total_weight:
        return VerificationResult(accepted=False, score=adjusted,
                                  matched_weight=scored["matched_weight"],
                                  matched_concepts=scored["matched"],
                                  rejected_by="gate1_content_evidence")
    if concepts.anchors and scored["anchor"] < thresholds.min_anchor_score:
        return VerificationResult(accepted=False, score=adjusted,
                                  anchor_score=scored["anchor"],
                                  matched_concepts=scored["matched"],
                                  rejected_by="gate2_anchor")
    if adjusted < thresholds.min_score:
        return VerificationResult(accepted=False, score=adjusted,
                                  content_coverage=scored["coverage"],
                                  anchor_score=scored["anchor"],
                                  proximity_score=scored["proximity"],
                                  intent_score=scored["intent"],
                                  matched_concepts=scored["matched"],
                                  rejected_by="gate3_confidence")

    return VerificationResult(
        accepted=True, score=adjusted,
        content_coverage=scored["coverage"], anchor_score=scored["anchor"],
        proximity_score=scored["proximity"], intent_score=scored["intent"],
        phrase_score=scored["phrase"], matched_weight=scored["matched_weight"],
        matched_concepts=scored["matched"], span=span,
        sentence_start=s_start, sentence_end=s_end,
    )


def verify(query: str, passage: str,
           thresholds: Thresholds = DEFAULT) -> Optional[str]:
    """The supporting excerpt, or None.

    Drop-in replacement for the LLM-backed `ActiveKnowledgeObject.receive_message`.
    The returned string is always a literal substring of `passage`.
    """
    result = verify_detailed(query, passage, thresholds)
    if not result.accepted or result.span is None:
        return None
    return passage[result.span[0]:result.span[1]].strip()


def supports(query: str, passage: str,
             thresholds: Thresholds = DEFAULT) -> bool:
    return verify_detailed(query, passage, thresholds).accepted
