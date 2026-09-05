from finding import to_finding_record


def test_verified_result_has_derived_confidence_from_pass_rate():
    """3 of 5 retrieved candidates passed verification -> confidence 0.6,
    not an invented number."""
    sources = [{"source": "a.md"}, {"source": "b.md"}, {"source": "a.md"}]
    record = to_finding_record(
        answer="The car is red.",
        sources=sources,
        n_results=5,
        model_name="llama3.2",
    )
    assert record.verified is True
    assert record.confidence == 3 / 5
    assert record.source_material == ("a.md", "b.md")  # deduped, sorted
    assert "generate_response" in record.method


def test_unverified_result_is_an_honest_non_answer():
    """Nothing passed verification: no fabricated confidence, no fabricated
    verification status."""
    record = to_finding_record(
        answer="The retrieved corpus does not contain a verifiable answer to this query.",
        sources=[],
        n_results=5,
    )
    assert record.verified is False
    assert record.confidence is None
    assert record.source_material == ()


def test_zero_n_results_does_not_divide_by_zero():
    record = to_finding_record(answer="", sources=[], n_results=0)
    assert record.verified is False
    assert record.confidence is None


def test_evidence_carries_each_excerpts_own_text_not_just_its_path():
    """A real consumer with per-item evidence-linking needs the actual
    verified text, not a path plus a collapsed confidence number."""
    sources = [
        {"source": "a.md", "extract": "alpha topics only in this document."},
        {"source": "b.md", "extract": "beta topics only in this document."},
    ]
    record = to_finding_record(answer="x", sources=sources, n_results=2)
    assert record.evidence == (
        ("a.md", "alpha topics only in this document."),
        ("b.md", "beta topics only in this document."),
    )


def test_evidence_is_empty_for_bare_source_only_dicts():
    """Older callers passing {"source": ...} with no "extract" still work,
    just without per-excerpt evidence -- not a hard failure."""
    record = to_finding_record(answer="x", sources=[{"source": "a.md"}], n_results=1)
    assert record.evidence == ()
    assert record.confidence == 1.0
