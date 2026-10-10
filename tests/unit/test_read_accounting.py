"""Skipped input leaves a record.

Before this, short messages, manifest entries with no transcript, undecodable
bytes, unparsable Python files and malformed git records were all dropped
without a trace, so a count of cells could not be told apart from a count of
cells plus an unknown amount of silently lost input.
"""

import json

from code_scanner import extract_python_chunks
from commit_loader import parse_git_log
from ecology import ingest_directory
from history_loader import (
    cells_from_history_repo,
    cells_from_transcript,
    history_repo_summary,
)
from read_log import (
    CONVERSATION_TOO_SHORT,
    DECODE_LOSS,
    GIT_RECORD_MALFORMED,
    MANIFEST_ENTRY_NO_ID,
    MESSAGE_TOO_SHORT,
    PYTHON_UNPARSABLE,
    TRANSCRIPT_MISSING,
    ReadLog,
)

TX = """---
id: c1
---

**user** · 2024-01-01T00:00:00+00:00

ok

---

**assistant** · 2024-01-01T00:00:05+00:00

This answer is long enough to become a cell of its own.
"""


def _repo(tmp_path, entries, files):
    repo = tmp_path / "X_History"
    (repo / "index").mkdir(parents=True)
    (repo / "transcripts").mkdir()
    for name, data in files.items():
        (repo / "transcripts" / name).write_bytes(data)
    (repo / "index" / "manifest.json").write_text(json.dumps({"conversations": entries}))
    return repo


def test_a_short_message_is_recorded_and_the_cells_are_unchanged():
    log = ReadLog()
    with_log = list(cells_from_transcript("X", "c1", "t", TX, "2024-01-01T00:00:00+00:00", log=log))
    without = list(cells_from_transcript("X", "c1", "t", TX, "2024-01-01T00:00:00+00:00"))
    assert with_log == without and len(with_log) == 1
    assert log.counts() == {MESSAGE_TOO_SHORT: 1}
    assert log.skips[0].where == "X/c1#0"


def test_a_conversation_with_no_headers_and_too_little_text_is_recorded():
    log = ReadLog()
    list(cells_from_transcript("X", "c2", "t", "---\nid: c2\n---\n\nhi", "2024-01-01T00:00:00+00:00", log=log))
    assert log.counts() == {CONVERSATION_TOO_SHORT: 1}


def test_an_empty_transcript_is_not_a_skip():
    log = ReadLog()
    list(cells_from_transcript("X", "c3", "t", "---\nid: c3\n---\n\n", "2024-01-01T00:00:00+00:00", log=log))
    assert len(log) == 0


def test_manifest_entries_with_no_id_or_no_file_are_recorded(tmp_path):
    repo = _repo(
        tmp_path,
        [
            {"title": "no id here", "start_time": "2024-01-01T00:00:00Z"},
            {"id": "gone", "start_time": "2024-01-02T00:00:00Z", "transcript": "transcripts/gone.md"},
            {"id": "c1", "start_time": "2024-01-03T00:00:00Z", "transcript": "transcripts/c1.md"},
        ],
        {"c1.md": TX.encode()},
    )
    log = ReadLog()
    cells = list(cells_from_history_repo(repo, log=log))
    assert len(cells) == 1
    assert log.counts()[MANIFEST_ENTRY_NO_ID] == 1
    assert log.counts()[TRANSCRIPT_MISSING] == 1
    assert list(cells_from_history_repo(repo)) == cells


def test_undecodable_bytes_are_recorded_and_the_text_is_what_it_was(tmp_path):
    bad = TX.encode() + b"\xff\xfe tail"
    repo = _repo(tmp_path, [{"id": "c1", "start_time": "2024-01-01T00:00:00Z", "transcript": "transcripts/c1.md"}],
                 {"c1.md": bad})
    log = ReadLog()
    with_log = list(cells_from_history_repo(repo, log=log))
    assert log.counts()[DECODE_LOSS] == 1
    # Identical to the previous read_text(errors="ignore") behaviour.
    expected = (repo / "transcripts" / "c1.md").read_text(encoding="utf-8", errors="ignore")
    assert [c.content for c in with_log] == [c.content for c in cells_from_transcript(
        "X_History", "c1", "", expected, "2024-01-01T00:00:00Z")]


def test_crlf_transcripts_read_exactly_as_before(tmp_path):
    crlf = TX.replace("\n", "\r\n").encode()
    repo = _repo(tmp_path, [{"id": "c1", "start_time": "2024-01-01T00:00:00Z", "transcript": "transcripts/c1.md"}],
                 {"c1.md": crlf})
    expected = (repo / "transcripts" / "c1.md").read_text(encoding="utf-8", errors="ignore")
    assert "\r" not in expected
    got = [c.content for c in cells_from_history_repo(repo)]
    want = [c.content for c in cells_from_transcript("X_History", "c1", "", expected, "2024-01-01T00:00:00Z")]
    assert got == want


def test_summary_reports_what_was_left_out(tmp_path):
    repo = _repo(tmp_path, [{"id": "c1", "start_time": "2024-01-01T00:00:00Z", "transcript": "transcripts/c1.md"}],
                 {"c1.md": TX.encode()})
    assert history_repo_summary(repo)["skipped"] == {MESSAGE_TOO_SHORT: 1}


def test_an_unparsable_python_file_is_recorded(tmp_path):
    good, bad = tmp_path / "good.py", tmp_path / "bad.py"
    good.write_text("def f():\n    return 1\n")
    bad.write_text("def broken(:\n")
    log = ReadLog()
    assert [n for n, _ in extract_python_chunks(good, log)] == ["f"]
    assert extract_python_chunks(bad, log) == []
    assert log.counts() == {PYTHON_UNPARSABLE: 1}
    assert str(bad) == log.skips[0].where


def test_ingest_says_when_a_parent_contributed_nothing(tmp_path, capsys):
    (tmp_path / "ok.py").write_text("def f():\n    return 1\n")
    (tmp_path / "bad.py").write_text("def broken(:\n")
    log = ReadLog()
    cells = ingest_directory(str(tmp_path), log)
    out = capsys.readouterr().out
    assert len(cells) == 1
    assert "descended from 2 parent structures" in out  # the existing line, unchanged
    assert "1 input(s) were read but contributed nothing" in out
    # With no log the output is exactly what it was.
    ingest_directory(str(tmp_path))
    assert "contributed nothing" not in capsys.readouterr().out


def test_a_malformed_git_record_is_recorded():
    rs, us = "\x1e", "\x1f"
    text = f"{rs}abc{us}me{us}2024-01-01T00:00:00+00:00{us}msg{us}\n{rs}truncated{us}only"
    log = ReadLog()
    assert len(list(parse_git_log(text, log))) == 1
    assert log.counts() == {GIT_RECORD_MALFORMED: 1}
    assert len(list(parse_git_log(text))) == 1
