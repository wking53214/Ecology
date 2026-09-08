"""corpus/ORIGIN.tsv is the per-file provenance ledger for corpus/.

These tests keep it honest: every file in corpus/ has a row, every row
describes the bytes actually on disk, and no row claims evidence that the
generator cannot produce. Regenerate with scripts/corpus_origin.py.
"""

import csv
import hashlib
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "corpus"
LEDGER = CORPUS / "ORIGIN.tsv"
SKIP = {"ORIGIN.tsv", "PROVENANCE.md"}
EVIDENCE = re.compile(r"^(history:[\w.,-]+|basename:[\w.-]+/.+|marker:(physionet|author-mit)|archive|none)$")


@pytest.fixture(scope="module")
def rows():
    with LEDGER.open() as f:
        lines = [ln for ln in f if not ln.startswith("#")]
    return {r["file"]: r for r in csv.DictReader(lines, delimiter="\t")}


def test_every_corpus_file_has_a_row(rows):
    on_disk = {p.name for p in CORPUS.iterdir() if p.is_file() and p.name not in SKIP}
    assert on_disk - set(rows) == set(), "files without a ledger row; rerun scripts/corpus_origin.py"
    assert set(rows) - on_disk == set(), "ledger rows for files no longer present"


def test_rows_describe_the_bytes_on_disk(rows):
    stale = [
        name for name, r in rows.items()
        if hashlib.sha256((CORPUS / name).read_bytes()).hexdigest() != r["sha256"]
        or int(r["bytes"]) != (CORPUS / name).stat().st_size
    ]
    assert stale == [], f"ledger is stale for {stale[:5]}; rerun scripts/corpus_origin.py"


def test_evidence_values_are_well_formed(rows):
    bad = {name: r["evidence"] for name, r in rows.items() if not EVIDENCE.match(r["evidence"])}
    assert bad == {}


def test_known_markers_are_recorded(rows):
    assert rows["LICENSE-38ace9a314da6382.md"]["evidence"] == "marker:physionet"
    # The author's MIT notice also carries the export suffix of files that
    # trace to observe-perceive; the marker match is recorded either way.
    assert rows["LICENSE-8fdaa84c270b798e.md"]["evidence"].startswith(("marker:author-mit", "history:"))


def test_ledger_names_the_repositories_it_consulted():
    first = LEDGER.open().readline()
    assert first.startswith("# siblings consulted: ")
    assert first.strip() != "# siblings consulted: none"
