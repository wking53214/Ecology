"""Reader for the *_History conversation archives (Claude_History,
ChatGPT_History, CoPilot_History, Gemini_History).

These repos share a manifest contract -- `index/manifest.json` lists the
conversations, each with an id, real ISO timestamps, and a transcript path
-- but NOT a transcript format: each repo's own `process.py` writes its own
message-block style (Claude: ``**human_anon** (<iso>):``; ChatGPT:
``**user** \u00b7 <iso>`` with ``---`` separators). So here the manifest is
the contract and the transcript parse is per-repo, auto-detected from the
frontmatter.

Why this exists instead of `ecology.ingest_directory()`:

- `ingest_directory` stamps every cell with the *file's* mtime, so an
  entire conversation corpus reads as "whenever it was last written." A
  system whose purpose is reconstructing *when* an inflection point
  happened cannot use that; the manifest and each message block carry the
  real time.
- `ingest_directory` splits on blank lines, which shreds a message
  containing a code block or a list into unattributed fragments. Here the
  cell is the message (large messages are split on paragraph boundaries
  but keep their speaker and timestamp).

Self-contained: standard library only, no import of `ecology` (which pulls
`ollama` at import time). Yields `ConversationCell` records, which are
duck-typed for Ecology's indexing path -- `initialize_vector_store` reads
`.identity` / `.content` / `.source` / `.date_str` / `.speaker`, all of
which `ConversationCell` carries. Usual use:
`list(cells_from_history_repo(repo))`.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Optional

# The archives this loader is for. Every one is private personal-conversation
# data -- CCC's PRIVATE_SOURCE_MARKERS refuses findings citing any of them by
# default, and `source` below is built to name the repo so that guard fires.
PRIVATE_HISTORY_REPOS = (
    "Claude_History",
    "ChatGPT_History",
    "CoPilot_History",
    "Gemini_History",
)

# A message longer than this is split on paragraph boundaries into parts
# that each keep the parent message's speaker and timestamp. nomic-embed-text
# tops out at 2048 tokens; 4000 chars stays under that even for code-dense
# content (~3 chars/token), so nothing is silently truncated at embed time.
# Locking this matters: a full corpus re-index is a ~38h operation.
DEFAULT_MAX_CELL_CHARS = 4000

# A message shorter than this carries no retrievable content ("Go", "Y",
# "continue", "Rewrite") -- ~1,400 such across the two real archives.
# Skipped: embedding them costs the same as any other cell and returns
# nothing recallable. The conversation's shape is still in the manifest.
DEFAULT_MIN_CELL_CHARS = 12

_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)

# Message headers are matched against a KNOWN speaker vocabulary, not any
# bold span -- real transcripts contain plenty of "**bold phrase** \u00b7 ..."
# inside message bodies (e.g. "**via docker compose** \u00b7 ...") that would
# otherwise be misread as a new message, truncating the real one and
# emitting a garbage cell.
_CLAUDE_SPEAKERS = r"human_anon|assistant_anon|issuer|human|assistant"
_CHATGPT_SPEAKERS = r"user|assistant|system|tool"

# Claude_History: **human_anon** (2026-07-22T16:59:37.779067Z):
_CLAUDE_HEADER = re.compile(
    rf"^\*\*({_CLAUDE_SPEAKERS})\*\*\s*\(([^)]*)\):[ \t]*$", re.M
)
# ChatGPT_History: **user** \u00b7 2024-08-06T15:49:12.647026+00:00 [\u00b7 gpt-4o]
_CHATGPT_HEADER = re.compile(
    rf"^\*\*({_CHATGPT_SPEAKERS})\*\*[ \t]*\u00b7[ \t]*([0-9T:\-.+Z]+)(?:[ \t]*\u00b7[ \t]*[^\n]*)?$",
    re.M,
)

_SPEAKER_NORMAL = {
    "human_anon": "human", "user": "human", "human": "human", "you": "human",
    "assistant_anon": "assistant", "assistant": "assistant", "ai": "assistant",
    "claude": "assistant", "chatgpt": "assistant", "copilot": "assistant",
}


@dataclass(frozen=True)
class ConversationCell:
    """One message (or one paragraph-slice of an oversized message) from a
    conversation archive, carrying its own real time and speaker."""

    identity: str            # "{repo}/{conv_id}#{seq}" (+ ".{part}" if split)
    content: str
    timestamp: float         # POSIX seconds -- the message's own time, or the
                             # conversation start_time when the message has none
    source: str              # "{repo}/transcripts/{conv_id}.md"
    speaker: str             # normalized: "human" | "assistant" | "other"
    conversation_id: str
    conversation_title: str
    occurred_at: str         # the ISO timestamp string, kept verbatim
    date_str: str            # "YYYY-MM-DD", to match ActiveKnowledgeObject


def _iso_to_posix(value: str, fallback: float) -> tuple[float, str]:
    """(posix_seconds, normalized_iso). Falls back to the conversation's
    own start time for the 2-in-10,721 message timestamps that aren't ISO."""
    raw = (value or "").strip()
    candidate = raw.replace("Z", "+00:00") if raw.endswith("Z") else raw
    try:
        dt = datetime.fromisoformat(candidate)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp(), dt.astimezone(timezone.utc).isoformat()
    except (ValueError, TypeError):
        dt = datetime.fromtimestamp(fallback, tz=timezone.utc)
        return fallback, dt.isoformat()


def _normalize_speaker(label: str) -> str:
    return _SPEAKER_NORMAL.get(label.strip().lower(), "other")


def _load_manifest(repo_path: Path) -> list[dict]:
    raw = json.loads((repo_path / "index" / "manifest.json").read_text(encoding="utf-8"))
    convs = raw["conversations"] if isinstance(raw, dict) else raw
    if not isinstance(convs, list):
        raise ValueError(f"{repo_path}/index/manifest.json: no conversations list")
    return convs


def _conversation_start(entry: dict) -> str:
    for key in ("start_time", "create_time", "created_at", "first_message_time"):
        if entry.get(key):
            return entry[key]
    return ""


def _split_frontmatter(text: str) -> tuple[str, str]:
    m = _FRONTMATTER.match(text)
    return (m.group(1), text[m.end():]) if m else ("", text)


def _detect_headers(body: str):
    """Return the header regex that actually matches this transcript's
    message blocks, or None for a transcript with no recognizable blocks
    (14 of Claude_History's 265 -- empty or tool-only conversations)."""
    if _CLAUDE_HEADER.search(body):
        return _CLAUDE_HEADER
    if _CHATGPT_HEADER.search(body):
        return _CHATGPT_HEADER
    return None


def _iter_messages(body: str, header_re) -> Iterator[tuple[str, str, str]]:
    """(speaker_label, iso_timestamp, message_text) for each block."""
    matches = list(header_re.finditer(body))
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        chunk = body[start:end]
        # ChatGPT blocks are fenced by a trailing "---"; drop it and trim.
        chunk = re.sub(r"\n-{3,}\s*$", "", chunk).strip()
        if chunk:
            yield m.group(1), m.group(2), chunk


def _split_oversized(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    parts: list[str] = []
    current = ""
    for para in text.split("\n\n"):
        if current and len(current) + len(para) + 2 > max_chars:
            parts.append(current)
            current = para
        else:
            current = f"{current}\n\n{para}" if current else para
    if current:
        parts.append(current)
    # A single paragraph over the limit: hard-wrap it.
    wrapped: list[str] = []
    for p in parts:
        if len(p) <= max_chars:
            wrapped.append(p)
        else:
            wrapped.extend(p[i:i + max_chars] for i in range(0, len(p), max_chars))
    return wrapped


def cells_from_transcript(
    repo_name: str,
    conv_id: str,
    title: str,
    transcript_text: str,
    conversation_start_iso: str,
    *,
    max_cell_chars: int = DEFAULT_MAX_CELL_CHARS,
    min_cell_chars: int = DEFAULT_MIN_CELL_CHARS,
) -> Iterator[ConversationCell]:
    """Parse one transcript's text into cells. Exposed for callers that
    already hold the text; `cells_from_history_repo` is the usual entry."""
    _fm, body = _split_frontmatter(transcript_text)
    source = f"{repo_name}/transcripts/{conv_id}.md"
    start_posix, _ = _iso_to_posix(conversation_start_iso, datetime.now(tz=timezone.utc).timestamp())

    def _emit(seq, parts, posix, iso_str, speaker, date_str):
        kept = [p for p in parts if len(p.strip()) >= min_cell_chars]
        for part_no, part in enumerate(kept):
            suffix = "" if len(kept) == 1 else f".{part_no}"
            yield ConversationCell(
                identity=f"{repo_name}/{conv_id}#{seq}{suffix}",
                content=part, timestamp=posix, source=source, speaker=speaker,
                conversation_id=conv_id, conversation_title=title,
                occurred_at=iso_str, date_str=date_str,
            )

    header_re = _detect_headers(body)
    if header_re is None:
        text = body.strip()
        if len(text) < min_cell_chars:
            return
        date_str = datetime.fromtimestamp(start_posix, tz=timezone.utc).strftime("%Y-%m-%d")
        yield from _emit(0, _split_oversized(text, max_cell_chars),
                         start_posix, conversation_start_iso, "other", date_str)
        return

    for seq, (label, iso, text) in enumerate(_iter_messages(body, header_re)):
        if len(text.strip()) < min_cell_chars:
            continue
        posix, norm_iso = _iso_to_posix(iso, start_posix)
        date_str = datetime.fromtimestamp(posix, tz=timezone.utc).strftime("%Y-%m-%d")
        yield from _emit(seq, _split_oversized(text, max_cell_chars),
                         posix, norm_iso, _normalize_speaker(label), date_str)


def cells_from_history_repo(
    repo_path,
    *,
    max_cell_chars: int = DEFAULT_MAX_CELL_CHARS,
    min_cell_chars: int = DEFAULT_MIN_CELL_CHARS,
    limit: Optional[int] = None,
) -> Iterator[ConversationCell]:
    """Yield ConversationCells for every conversation in a *_History repo,
    oldest first. `limit` caps the number of conversations (for a smoke
    run against a 10k-message archive)."""
    repo_path = Path(repo_path)
    repo_name = repo_path.name
    entries = _load_manifest(repo_path)
    entries.sort(key=lambda e: _conversation_start(e) or "")
    if limit is not None:
        entries = entries[:limit]

    for entry in entries:
        conv_id = entry.get("id") or entry.get("safe_id")
        if not conv_id:
            continue
        rel = entry.get("transcript") or f"transcripts/{conv_id}.md"
        transcript = repo_path / rel
        if not transcript.is_file():
            continue
        yield from cells_from_transcript(
            repo_name, conv_id, entry.get("title", ""),
            transcript.read_text(encoding="utf-8", errors="ignore"),
            _conversation_start(entry),
            max_cell_chars=max_cell_chars, min_cell_chars=min_cell_chars,
        )


def history_repo_summary(repo_path, *, max_cell_chars: int = DEFAULT_MAX_CELL_CHARS) -> dict:
    """A one-look health check on a *_History repo: how many conversations
    the manifest lists, how many actually yielded cells, how many were
    empty or content-stripped in the export, the cell and speaker counts,
    and the real date span. The analogue of ingest_directory()'s print
    summary -- 'is this corpus wired correctly' before feeding it to the
    embedder."""
    repo_path = Path(repo_path)
    entries = _load_manifest(repo_path)
    total = len(entries)
    with_cells = 0
    missing = 0            # manifest entry with no id or no transcript file
    empty = 0             # transcript is frontmatter/title only
    content_stripped = 0  # message headers present, but the export captured
                          # no text -- an exchange provably happened at a
                          # known time and its content is gone (a fact about
                          # the archive, not about this reader)
    cell_count = 0
    speakers: dict[str, int] = {}
    earliest, latest = None, None
    for entry in entries:
        conv_id = entry.get("id") or entry.get("safe_id")
        transcript = repo_path / (entry.get("transcript") or f"transcripts/{conv_id}.md") if conv_id else None
        if not conv_id or not transcript.is_file():
            missing += 1
            continue
        text = transcript.read_text(encoding="utf-8", errors="ignore")
        produced = 0
        for cell in cells_from_transcript(
            repo_path.name, conv_id, entry.get("title", ""), text,
            _conversation_start(entry), max_cell_chars=max_cell_chars,
        ):
            produced += 1
            cell_count += 1
            speakers[cell.speaker] = speakers.get(cell.speaker, 0) + 1
            earliest = cell.occurred_at if earliest is None else min(earliest, cell.occurred_at)
            latest = cell.occurred_at if latest is None else max(latest, cell.occurred_at)
        if produced:
            with_cells += 1
        elif _detect_headers(_split_frontmatter(text)[1]) is not None:
            content_stripped += 1
        else:
            empty += 1
    return {
        "repo": repo_path.name,
        "conversations_in_manifest": total,
        "conversations_with_cells": with_cells,
        "conversations_empty": empty,
        "conversations_content_stripped": content_stripped,
        "conversations_missing_transcript": missing,
        "cells": cell_count,
        "speakers": speakers,
        "earliest": earliest,
        "latest": latest,
    }


