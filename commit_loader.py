"""Reader for a git repository's commit history, as indexable cells.

The *_History archives hold *why* a change was made (the conversations).
A repository's commit history holds *what* changed and *when*. With both in
Ecology, one question ("why did CCC split recurrence out?") can return the
commit that did it and the conversation where it was decided.

Each commit becomes one cell: its message, then the files it changed.
Like history_loader's ConversationCell, a CommitCell carries the commit's
real author time (not the time it was indexed) and who wrote it, so the
"when" survives indexing. A commit longer than `max_cell_chars` is split on
paragraph boundaries; every part keeps the commit's time and author.

Self-contained: standard library plus the `git` command, no import of
`ecology`. Reads only what the local clone holds, so a shallow clone yields
only the commits it fetched; that is a fact about the clone, not this reader.

Merge commits are skipped by default: their message is usually generated
("Merge pull request #12 ...") and the files they list repeat the commits
being merged.

Ported in spirit from innovation_os's repository/git_intelligence.py ahead
of that repository's retirement (2026-10-07). innovation_os listed commits
and changed files but never connected them to anything.
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional

from history_loader import DEFAULT_MAX_CELL_CHARS, _split_oversized
from read_log import GIT_RECORD_MALFORMED, ReadLog

# git log --name-status output is parsed from these separators, which do not
# occur in commit messages or paths: ASCII record separator before each
# commit, unit separator between its header fields.
_RS = "\x1e"
_US = "\x1f"
_FORMAT = f"{_RS}%H{_US}%an{_US}%aI{_US}%B{_US}"

_STATUS_WORDS = {
    "A": "added", "M": "modified", "D": "deleted", "R": "renamed",
    "C": "copied", "T": "type changed", "U": "unmerged",
}


@dataclass(frozen=True)
class CommitCell:
    """One commit (or one paragraph-slice of an oversized one)."""

    identity: str        # "{repo}@{sha}" (+ ".{part}" if split)
    content: str         # the commit message, then "Files changed:" lines
    timestamp: float     # POSIX seconds of the author time
    source: str          # "{repo}/commit/{sha}"
    speaker: str         # the commit author's name, as git records it
    repo: str
    sha: str
    occurred_at: str     # the ISO author time, kept verbatim
    date_str: str        # "YYYY-MM-DD", to match the other cell types


def _git_log(repo_path: Path, include_merges: bool) -> str:
    args = ["git", "-C", str(repo_path), "log", "--reverse",
            f"--format={_FORMAT}", "--name-status", "-M"]
    if not include_merges:
        args.append("--no-merges")
    try:
        result = subprocess.run(args, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", check=False)
    except FileNotFoundError as exc:
        raise RuntimeError("git is not installed or not on PATH") from exc
    if result.returncode != 0:
        raise ValueError(f"{repo_path} is not a readable git repository: {result.stderr.strip()}")
    return result.stdout


def _describe_change(line: str) -> Optional[str]:
    parts = line.split("\t")
    if len(parts) < 2 or not parts[0]:
        return None
    word = _STATUS_WORDS.get(parts[0][0], parts[0])
    if len(parts) >= 3:
        return f"{word}: {parts[1]} -> {parts[2]}"
    return f"{word}: {parts[1]}"


def parse_git_log(text: str, log: ReadLog | None = None):
    """(sha, author, iso_time, message, [change lines]) per commit, oldest
    first, from `git log` output in this module's format.

    A record with too few fields is skipped. Pass a ReadLog to have each one
    recorded."""
    for number, record in enumerate(text.split(_RS)):
        if not record.strip():
            continue
        fields = record.split(_US, 4)
        if len(fields) < 5:
            if log is not None:
                log.note(GIT_RECORD_MALFORMED, f"record {number}",
                         f"{len(fields)} of 5 fields: {record.strip()[:60]!r}")
            continue
        sha, author, iso_time, message, tail = fields
        changes = [c for c in (_describe_change(ln) for ln in tail.splitlines() if ln.strip()) if c]
        yield sha.strip(), author.strip(), iso_time.strip(), message.strip(), changes


def cells_from_git_repo(
    repo_path,
    *,
    max_cell_chars: int = DEFAULT_MAX_CELL_CHARS,
    limit: Optional[int] = None,
    include_merges: bool = False,
    repo_name: Optional[str] = None,
    log: ReadLog | None = None,
) -> Iterator[CommitCell]:
    """Yield CommitCells for a git repository, oldest commit first.

    `limit` caps the number of commits (the oldest `limit`). `repo_name`
    overrides the name used in identities and sources; by default it is the
    folder name, so the same repository cloned to two places indexes once.
    """
    repo_path = Path(repo_path)
    name = repo_name or repo_path.resolve().name
    for count, (sha, author, iso_time, message, changes) in enumerate(
            parse_git_log(_git_log(repo_path, include_merges), log)):
        if limit is not None and count >= limit:
            return
        when = datetime.fromisoformat(iso_time)
        body = message or "(no commit message)"
        if changes:
            body += "\n\nFiles changed:\n" + "\n".join(changes)
        parts = _split_oversized(body, max_cell_chars)
        for index, part in enumerate(parts):
            suffix = f".{index}" if len(parts) > 1 else ""
            yield CommitCell(
                identity=f"{name}@{sha}{suffix}",
                content=part,
                timestamp=when.timestamp(),
                source=f"{name}/commit/{sha}",
                speaker=author,
                repo=name,
                sha=sha,
                occurred_at=iso_time,
                date_str=when.date().isoformat(),
            )
