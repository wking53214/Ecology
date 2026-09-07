"""Lexical (BM25) retrieval over conversation cells via SQLite FTS5.

A complement to the vector store, not a replacement. Two reasons it earns
its place here:

- It needs no embedding model, no GPU, and ~seconds to build over the whole
  archive -- where the vector index is a multi-GB, hour-plus operation that
  has already failed once on disk. When a reconstruction question is mostly
  proper nouns (VSA, Citadel, FORTRESS, GSA-815), BM25 over the raw text is
  a strong first pass on its own.
- It carries `date` and `speaker` straight through, and supports a date-range
  filter at query time -- the "what was I thinking in May" shape -- without
  re-embedding anything.

The FTS5 table is the index; `sqlite3` is stdlib. Query it directly here,
never through the ChromaDB client.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator

DEFAULT_DB = "./lexical_index.sqlite3"


@dataclass(frozen=True)
class LexicalHit:
    identity: str
    content: str
    source: str
    date: str | None
    speaker: str | None
    score: float  # bm25; lower is a better match in SQLite's convention


def _connect(db_path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def build_lexical_index(cells: Iterable, db_path: str | Path = DEFAULT_DB, *, rebuild: bool = True) -> int:
    """Build (or rebuild) the FTS5 index from an iterable of cells.

    A cell is anything with .identity / .content / .source and, ideally,
    .date_str / .speaker. Returns the row count.
    """
    db_path = Path(db_path)
    if rebuild and db_path.exists():
        db_path.unlink()
        for suffix in ("-wal", "-shm"):
            p = db_path.with_name(db_path.name + suffix)
            if p.exists():
                p.unlink()

    conn = _connect(db_path)
    try:
        conn.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS cells USING fts5("
            "identity UNINDEXED, content, source UNINDEXED, "
            "cell_date UNINDEXED, speaker UNINDEXED, "
            "tokenize='porter unicode61')"
        )
        rows = (
            (
                c.identity,
                c.content,
                c.source,
                getattr(c, "date_str", None),
                getattr(c, "speaker", None),
            )
            for c in cells
        )
        conn.executemany(
            "INSERT INTO cells (identity, content, source, cell_date, speaker) "
            "VALUES (?, ?, ?, ?, ?)",
            rows,
        )
        conn.commit()
        count = conn.execute("SELECT count(*) FROM cells").fetchone()[0]
        return count
    finally:
        conn.close()


def _fts_query(raw: str) -> str:
    """Turn a free-text query into a permissive FTS5 MATCH expression: the
    significant words OR'd together, quoted so punctuation can't break the
    parser. Precision comes from BM25 ranking and the downstream containment
    check, not from a strict AND here."""
    words = [w for w in _tokenize(raw) if len(w) > 2]
    if not words:
        words = _tokenize(raw) or [raw]
    return " OR ".join(f'"{w}"' for w in words)


def _tokenize(text: str) -> list[str]:
    out, cur = [], []
    for ch in text.lower():
        if ch.isalnum() or ch in "+-_/.":
            cur.append(ch)
        elif cur:
            out.append("".join(cur))
            cur = []
    if cur:
        out.append("".join(cur))
    return out


def lexical_search(
    query: str,
    db_path: str | Path = DEFAULT_DB,
    *,
    n_results: int = 5,
    date_from: str | None = None,
    date_to: str | None = None,
    speaker: str | None = None,
) -> list[LexicalHit]:
    """Top-n cells for `query` by BM25, with optional YYYY-MM-DD date-range
    and speaker filters."""
    conn = _connect(db_path)
    try:
        sql = [
            "SELECT identity, content, source, cell_date, speaker, bm25(cells) AS score",
            "FROM cells WHERE cells MATCH ?",
        ]
        params: list = [_fts_query(query)]
        if date_from is not None:
            sql.append("AND cell_date >= ?")
            params.append(date_from)
        if date_to is not None:
            sql.append("AND cell_date <= ?")
            params.append(date_to)
        if speaker is not None:
            sql.append("AND speaker = ?")
            params.append(speaker)
        sql.append("ORDER BY score LIMIT ?")
        params.append(n_results)
        cur = conn.execute(" ".join(sql), params)
        return [
            LexicalHit(identity=r[0], content=r[1], source=r[2], date=r[3], speaker=r[4], score=r[5])
            for r in cur.fetchall()
        ]
    finally:
        conn.close()


def iter_all_dates(db_path: str | Path = DEFAULT_DB) -> Iterator[str]:
    conn = _connect(db_path)
    try:
        for (d,) in conn.execute("SELECT DISTINCT cell_date FROM cells WHERE cell_date IS NOT NULL ORDER BY cell_date"):
            yield d
    finally:
        conn.close()
