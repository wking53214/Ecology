from dataclasses import dataclass

from lexical_index import build_lexical_index, lexical_search


@dataclass
class _Cell:
    identity: str
    content: str
    source: str
    date_str: str | None = None
    speaker: str | None = None


def _cells():
    return [
        _Cell("c1", "We decided the VSA principle governs Citadel as its law.",
              "Claude_History/transcripts/a.md", "2026-05-10", "assistant"),
        _Cell("c2", "The mortgage IVR banking demo needs a real phone line.",
              "Claude_History/transcripts/b.md", "2026-06-01", "human"),
        _Cell("c3", "Event-time beats ingest-time for the recurrence tie-break.",
              "ChatGPT_History/transcripts/c.md", "2026-07-15", "assistant"),
        _Cell("c4", "unrelated chatter about lunch",
              "ChatGPT_History/transcripts/d.md", "2026-07-16", "human"),
    ]


def test_build_and_search_returns_the_matching_cell(tmp_path):
    db = tmp_path / "lex.sqlite3"
    n = build_lexical_index(_cells(), db_path=db)
    assert n == 4

    hits = lexical_search("VSA Citadel governing law", db_path=db, n_results=2)
    assert hits
    assert hits[0].identity == "c1"
    assert hits[0].date == "2026-05-10"
    assert hits[0].speaker == "assistant"


def test_date_range_filter(tmp_path):
    db = tmp_path / "lex.sqlite3"
    build_lexical_index(_cells(), db_path=db)

    # "demo" and "phone" only appear in the June cell
    hits = lexical_search("demo phone line", db_path=db, n_results=5,
                          date_from="2026-05-15", date_to="2026-06-30")
    assert [h.identity for h in hits] == ["c2"]

    # same query, a window that excludes June -> nothing
    hits = lexical_search("demo phone line", db_path=db, n_results=5,
                          date_from="2026-01-01", date_to="2026-03-01")
    assert hits == []


def test_speaker_filter(tmp_path):
    db = tmp_path / "lex.sqlite3"
    build_lexical_index(_cells(), db_path=db)
    hits = lexical_search("mortgage lunch demo chatter", db_path=db, n_results=5, speaker="human")
    assert {h.speaker for h in hits} == {"human"}


def test_punctuation_in_query_does_not_break_fts(tmp_path):
    db = tmp_path / "lex.sqlite3"
    build_lexical_index(_cells(), db_path=db)
    # bare FTS5 would choke on the unbalanced quote / colon
    hits = lexical_search('event-time vs. ingest-time: which "wins"?', db_path=db, n_results=3)
    assert hits[0].identity == "c3"


def test_rebuild_replaces_prior_contents(tmp_path):
    db = tmp_path / "lex.sqlite3"
    build_lexical_index(_cells(), db_path=db)
    build_lexical_index(_cells()[:1], db_path=db, rebuild=True)
    hits = lexical_search("the", db_path=db, n_results=50)
    assert len(hits) <= 1
