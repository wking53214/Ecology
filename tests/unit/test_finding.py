from finding import to_finding_record


def test_verified_result_has_derived_confidence_from_pass_rate():
    """3 verified chunks, but 2 of them are the SAME document -- confidence
    must count 2 distinct sources, not 3 chunks. A flood-test finding:
    counting raw chunks let confidence claim stronger corroboration than
    source_material (already deduped) showed right next to it."""
    sources = [{"source": "a.md"}, {"source": "b.md"}, {"source": "a.md"}]
    record = to_finding_record(
        answer="The car is red.",
        sources=sources,
        n_results=5,
        model_name="llama3.2",
    )
    assert record.verified is True
    assert record.confidence == 2 / 5  # 2 distinct sources, not 3 chunks
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


def test_confidence_and_source_material_agree_on_how_many_sources_there_are():
    """The two fields must never tell a different-cardinality story about
    the same finding -- confidence's numerator and len(source_material)
    have to match, always, regardless of how many chunks came from each
    document."""
    sources = [
        {"source": "doc.md", "extract": "paragraph one"},
        {"source": "doc.md", "extract": "paragraph two"},
        {"source": "doc.md", "extract": "paragraph three"},
    ]
    record = to_finding_record(answer="x", sources=sources, n_results=5)
    implied_source_count = round(record.confidence * 5)
    assert implied_source_count == len(record.source_material) == 1


def test_finding_record_carries_event_dates():
    """Event dates can be set on a FindingRecord and carried through."""
    from finding import FindingRecord

    record = FindingRecord(
        conclusion="Evidence from May.",
        method="test_method",
        source_material=("conv.md",),
        confidence=0.8,
        verified=True,
        evidence=(("conv.md", "may evidence"),),
        event_start_date="2026-05-14",
        event_end_date="2026-05-14",
    )
    assert record.event_start_date == "2026-05-14"
    assert record.event_end_date == "2026-05-14"


def test_finding_record_defaults_event_dates_to_none():
    """A FindingRecord without event dates has them as None."""
    from finding import FindingRecord

    record = FindingRecord(
        conclusion="No event date info.",
        method="method",
        source_material=("source.md",),
        confidence=None,
        verified=False,
    )
    assert record.event_start_date is None
    assert record.event_end_date is None


def test_finding_record_event_dates_span_multiple_sources():
    """Event dates can span multiple sources with different dates."""
    from finding import FindingRecord

    record = FindingRecord(
        conclusion="Pattern across months.",
        method="method",
        source_material=("march.md", "may.md", "july.md"),
        confidence=0.7,
        verified=True,
        evidence=(
            ("march.md", "March evidence"),
            ("may.md", "May evidence"),
            ("july.md", "July evidence"),
        ),
        event_start_date="2026-03-01",
        event_end_date="2026-07-31",
    )
    assert record.event_start_date == "2026-03-01"
    assert record.event_end_date == "2026-07-31"
