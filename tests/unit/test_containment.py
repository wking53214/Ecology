"""Deterministic containment verification.

The six numbered cases are the design's own examples, implemented verbatim.
They are worth being honest about: they were written from the same design as
the code, so they check that the design was *implemented*, not that it is
*correct*. Passing them is necessary and nowhere near sufficient — see
`scripts/calibrate_containment.py`, which scores the verifier against real
corpus passages it did not author.

The two reject cases (4, 5, 6) are the ones that matter. A verifier that
admits them contaminates the evidence path into CCC, where a falsely
corroborating passage can advance a pattern that does not exist.
"""

import pytest

from containment import (
    DEFAULT,
    Thresholds,
    extract_concepts,
    is_distinctive,
    split_sentences,
    stem,
    supports,
    verify,
    verify_detailed,
)


# ---------------------------------------------------------------------------
# The six design cases
# ---------------------------------------------------------------------------

def test_1_direct_match():
    """Exact anchor, exact phrase, decision equivalence, rationale marker."""
    query = "Why did we choose SQLite for the evidence store?"
    passage = (
        "We decided to use SQLite for the evidence store because it keeps the "
        "prototype dependency-free and is included with Python's standard library."
    )
    got = verify(query, passage)
    assert got is not None
    assert "SQLite" in got and "because" in got
    assert got in passage, "returned evidence must be a literal substring"


def test_2_paraphrase_with_no_literal_decision_verb():
    """The important test. There is no 'choose' anywhere in the passage --
    'the call was to go with' has to carry the decision through the controlled
    relationship, or conversational paraphrase is simply not recognised."""
    query = "Why did we choose Citadel?"
    passage = (
        "After comparing the alternatives, the call was to go with Citadel "
        "because it gave us a simpler integration boundary and avoided "
        "another dependency."
    )
    got = verify(query, passage)
    assert got is not None, "paraphrased decision was not recognised"
    assert "call was to go with" in got


def test_3_multi_sentence_window():
    """Evidence split across two sentences: one supplies the problem, the next
    the decision. The third is true but unnecessary, and the length penalty
    should leave it out."""
    query = "Why was the vector index added?"
    passage = (
        "The initial lexical search was useful but missed semantically similar "
        "conversation. We added the vector index to recover those paraphrased "
        "references. This also improved retrieval when terminology changed "
        "between conversations."
    )
    got = verify(query, passage)
    assert got is not None
    assert "vector index" in got
    assert "terminology changed" not in got, (
        "the unnecessary third sentence was included -- the length penalty "
        "is not doing its job"
    )


def test_4_reject_common_word_overlap():
    """'we', 'the', 'evidence', 'store' all overlap. There is no SQLite, no
    decision, no rationale attached to anything. The anchor gate exists for
    exactly this."""
    query = "Why did we choose SQLite for the evidence store?"
    passage = (
        "We discussed the evidence yesterday. The team said we should do this "
        "carefully and make sure the store remains reliable."
    )
    result = verify_detailed(query, passage)
    assert result.accepted is False
    assert verify(query, passage) is None


def test_5_reject_right_entity_wrong_proposition():
    """The adversarial case. The passage genuinely is about SQLite and a
    database — the anchor is present and real — but it never establishes that
    anyone chose SQLite. Exact entity matching is not evidence of the claim."""
    query = "Why did we choose SQLite for the evidence store?"
    passage = (
        "SQLite is already used by several tools in the repository. The current "
        "database contains approximately 40,000 records."
    )
    assert verify(query, passage) is None, (
        "admitted a passage that mentions the right thing and says nothing "
        "about the question asked"
    )


def test_6_reject_rationale_without_the_decision():
    """Excellent rationale vocabulary, no evidence a choice was ever made.
    The verifier must not infer the missing decision because the explanation
    sounds like a reason."""
    query = "Why did we choose Citadel?"
    passage = (
        "Because Citadel is easier to test and has fewer dependencies. The "
        "alternative would require additional infrastructure."
    )
    assert verify(query, passage) is None, (
        "inferred a decision from rationale alone"
    )


# ---------------------------------------------------------------------------
# The properties the six cases depend on
# ---------------------------------------------------------------------------

def test_returned_evidence_is_always_a_literal_substring():
    """A verifier that reconstructs its own quote is paraphrasing, not
    verifying containment. Checked structurally rather than by eye."""
    query = "Why did we choose SQLite?"
    passage = ("We evaluated three options. We decided to use SQLite because "
               "it ships with Python. That closed the question.")
    got = verify(query, passage)
    assert got is not None and got in passage


def test_rejection_names_which_gate_refused():
    """Each gate is a distinct reason, and a verifier that cannot say which
    one fired is one more thing that has to be trusted."""
    reasons = set()
    for q, p in [
        ("Why did we choose SQLite for the evidence store?",
         "We discussed the evidence yesterday. The store remains reliable."),
        ("Why did we choose Citadel?",
         "Because Citadel is easier to test and has fewer dependencies."),
    ]:
        reasons.add(verify_detailed(q, p).rejected_by)
    assert reasons, "no rejection reason recorded"
    assert all(r.startswith("gate") for r in reasons), reasons


@pytest.mark.parametrize("token,expected", [
    ("SQLITE", True), ("CamelCase", True), ("snake_case", True),
    ("kebab-case", True), ("v1.2", True), ("40000", True),
    ("conservation", True),          # long uncommon word
    ("the", False), ("store", False), ("choose", False),
])
def test_distinctiveness_is_conservative(token, expected):
    """The anchor gate does the most work of any gate, so over-marking tokens
    as distinctive makes it trivially satisfiable and quietly disables it."""
    assert is_distinctive(token) is expected


def test_stemming_does_not_manufacture_matches():
    """Aggressive stemming is how 'universal' and 'universe' become the same
    concept. Conservative trim, never below four characters."""
    assert stem("choosing") == stem("chooses") != ""
    assert stem("universal") != stem("universe")
    assert stem("was") == "was"      # too short to trim


def test_sentence_split_protects_abbreviations_and_decimals():
    text = "Dr. Smith measured 3.14 units. Then the run finished."
    spans = split_sentences(text)
    assert len(spans) == 2, [text[a:b] for a, b in spans]
    assert "Dr. Smith" in text[spans[0][0]:spans[0][1]]


def test_question_words_become_intent_not_content():
    """'why' is not a content token to be matched -- it says what kind of
    relationship the passage must contain."""
    concepts = extract_concepts("Why did we choose Citadel?")
    assert "why" not in concepts.tokens
    assert "rationale" in concepts.intents
    assert "decision" in concepts.intents      # 'choose' implies it
    assert "citadel" in concepts.tokens


def test_thresholds_are_a_single_policy_object():
    """Every number the verifier's behaviour depends on lives in one place, so
    calibration can vary it and nobody has to grep for magic constants."""
    strict = Thresholds(min_score=0.95)
    query = "Why did we choose SQLite for the evidence store?"
    passage = ("We decided to use SQLite for the evidence store because it "
               "keeps the prototype dependency-free.")
    assert verify(query, passage) is not None
    assert verify(query, passage, strict) is None


def test_composite_weights_must_sum_to_one():
    with pytest.raises(ValueError, match="sum to 1.0"):
        Thresholds(w_coverage=0.9)


def test_supports_agrees_with_verify():
    query = "Why did we choose SQLite?"
    for passage in [
        "We decided to use SQLite because it ships with Python.",
        "The weather was fine and nothing was decided.",
    ]:
        assert supports(query, passage) is (verify(query, passage) is not None)


def test_empty_and_degenerate_inputs_do_not_crash():
    assert verify("", "some passage") is None
    assert verify("why did we choose X", "") is None
    assert verify("the a an is", "the a an is") is None   # all stopwords
