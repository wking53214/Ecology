import json

from history_loader import (
    cells_from_history_repo,
    cells_from_transcript,
    history_repo_summary,
)

CLAUDE_TX = """---
id: conv-claude-1
start_time: 2026-05-16T14:26:54.757306Z
message_count: 3
---

# Governance ledger triage

**human_anon** (2026-05-16T14:26:55.100000Z):

Here is the plan. **via docker compose** we deploy the ledger and then
verify the hash chain end to end.

**assistant_anon** (2026-05-16T14:28:10.000000Z):

Understood. I will triage the four items and build the small ones.

**issuer** (2026-05-16T14:29:00.000000Z):

approved
"""

CHATGPT_TX = """---
id: conv-gpt-1
title: "SQL OUTER JOINs for NULL"
create_time: 2023-09-20T13:48:42.426135+00:00
message_count: 2
models: [gpt-4o]
---

# SQL OUTER JOINs for NULL

**user** · 2023-09-20T13:48:42.647026+00:00

What sql join do I use to get all rows even with a null on one side?

---

**assistant** · 2023-09-20T13:48:45.963636+00:00 · gpt-4o

Use a LEFT OUTER JOIN. It keeps every row from the left table and fills
NULLs where the right side has no match.

---
"""


def test_claude_format_yields_one_cell_per_message_with_real_time_and_speaker():
    cells = list(cells_from_transcript(
        "Claude_History", "conv-claude-1", "Governance ledger triage",
        CLAUDE_TX, "2026-05-16T14:26:54.757306Z",
    ))
    assert [c.speaker for c in cells] == ["human", "assistant", "other"]  # issuer -> other
    assert cells[0].content.startswith("Here is the plan.")
    # the "**via docker compose**" span in the body is NOT read as a new message
    assert "**via docker compose**" in cells[0].content
    assert len(cells) == 3
    # real per-message time, not a file mtime
    assert cells[1].occurred_at.startswith("2026-05-16T14:28:10")
    assert cells[0].timestamp < cells[1].timestamp < cells[2].timestamp
    assert cells[0].source == "Claude_History/transcripts/conv-claude-1.md"
    assert cells[0].date_str == "2026-05-16"


def test_chatgpt_format_is_parsed_by_its_own_shape():
    cells = list(cells_from_transcript(
        "ChatGPT_History", "conv-gpt-1", "SQL OUTER JOINs for NULL",
        CHATGPT_TX, "2023-09-20T13:48:42.426135+00:00",
    ))
    assert [c.speaker for c in cells] == ["human", "assistant"]
    assert "LEFT OUTER JOIN" in cells[1].content
    assert cells[1].content.rstrip().endswith("no match.")  # trailing "---" stripped
    assert cells[0].occurred_at.startswith("2023-09-20T13:48:42")


def test_a_message_over_the_size_cap_splits_but_keeps_speaker_and_time():
    big = "para one.\n\n" + ("x" * 200 + "\n\n") * 60  # well over the default cap
    tx = f"---\nid: c\n---\n\n**human_anon** (2026-01-01T00:00:00Z):\n\n{big}\n"
    cells = list(cells_from_transcript("Claude_History", "c", "", tx, "2026-01-01T00:00:00Z",
                                       max_cell_chars=2000))
    assert len(cells) > 1
    assert all(c.speaker == "human" for c in cells)
    assert len({c.timestamp for c in cells}) == 1
    assert all(len(c.content) <= 2000 for c in cells)
    assert {c.identity for c in cells} == {f"Claude_History/c#0.{i}" for i in range(len(cells))}


def test_a_content_stripped_transcript_yields_nothing_not_a_crash():
    tx = "---\nid: c\n---\n\n# Title only\n\n**human_anon** (2026-01-01T00:00:00Z):\n\n\n\n---\n"
    assert list(cells_from_transcript("Claude_History", "c", "", tx, "2026-01-01T00:00:00Z")) == []


def test_non_iso_message_timestamp_falls_back_to_conversation_start():
    tx = "---\nid: c\n---\n\n**human_anon** (not-a-timestamp):\n\nhello there\n"
    cell = next(iter(cells_from_transcript("Claude_History", "c", "", tx, "2026-03-01T12:00:00Z")))
    assert cell.occurred_at.startswith("2026-03-01T12:00:00")


def _write_repo(tmp_path, name, transcripts):
    repo = tmp_path / name
    (repo / "index").mkdir(parents=True)
    (repo / "transcripts").mkdir()
    conv = []
    for cid, (start, text) in transcripts.items():
        (repo / "transcripts" / f"{cid}.md").write_text(text)
        conv.append({"id": cid, "start_time": start, "transcript": f"transcripts/{cid}.md"})
    (repo / "index" / "manifest.json").write_text(json.dumps({"conversations": conv}))
    return repo


def test_repo_reader_orders_conversations_oldest_first(tmp_path):
    repo = _write_repo(tmp_path, "Claude_History", {
        "newer": ("2026-06-01T00:00:00Z", CLAUDE_TX),
        "older": ("2026-01-01T00:00:00Z", CLAUDE_TX),
    })
    ids = [c.conversation_id for c in cells_from_history_repo(repo)]
    assert ids[0] == "older" and ids[-1] == "newer"


def test_summary_counts_stripped_conversations_separately(tmp_path):
    repo = _write_repo(tmp_path, "ChatGPT_History", {
        "good": ("2024-01-01T00:00:00+00:00", CHATGPT_TX),
        "stripped": ("2024-02-01T00:00:00+00:00",
                     "---\nid: stripped\n---\n\n**user** · 2024-02-01T00:00:00+00:00\n\n\n\n---\n"),
    })
    s = history_repo_summary(repo)
    assert s["conversations_in_manifest"] == 2
    assert s["conversations_with_cells"] == 1
    # headers present, text gone -- counted as content_stripped, not "empty"
    assert s["conversations_content_stripped"] == 1
    assert s["conversations_empty"] == 0
    assert s["speakers"] == {"human": 1, "assistant": 1}
