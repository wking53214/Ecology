"""Build corpus/ORIGIN.tsv: one row per file under corpus/ with whatever
origin evidence can be established mechanically.

Evidence, strongest first:

  history:<repo>[,<repo>]   the file's exact bytes exist as a blob in that
                            sibling repository's git history (any commit).
                            This is the author's own material.
  basename:<repo>/<path>    a tracked file of the same name exists in a
                            sibling repository but the bytes differ (a
                            diverged copy; origin likely, content unverified).
                            Names are compared after stripping the export
                            suffixes seen here (-<16 hex>, " (1)"), and a
                            .md whose body is Python is also tried as .py.
  marker:physionet          the file names the PhysioNet Challenge (BSD-3).
  marker:author-mit         the file carries the author's MIT notice.
  archive                   a zip or git bundle; contents are not indexed
                            here and must be assessed separately.
  none                      nothing determinable from the bytes or from the
                            sibling repositories available when this ran.

The batch column is the 16-hex export suffix many files carry; files sharing
one arrived together. It is context for a human, not evidence by itself.

Run from the repository root:

    python scripts/corpus_origin.py --siblings /path/to/dir/containing/repos

Sibling repositories are the author's other checkouts. The ledger records
which ones were consulted so a later run can widen the search.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

CORPUS = Path("corpus")
LEDGER = CORPUS / "ORIGIN.tsv"
SKIP = {"ORIGIN.tsv", "PROVENANCE.md"}
ARCHIVE_SUFFIXES = {".zip", ".bundle"}
PHYSIONET_TOKENS = (b"PhysioNet", b"physionet")
AUTHOR_MIT_TOKENS = (b"MIT License", b"William N King")


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def sibling_repos(root: Path) -> list[Path]:
    here = Path.cwd().resolve()
    return sorted(
        d for d in root.iterdir()
        if (d / ".git").exists() and d.resolve() != here
    )


def blob_in_history(repo: Path, sha: str) -> bool:
    return subprocess.run(
        ["git", "-C", str(repo), "cat-file", "-e", sha],
        capture_output=True,
    ).returncode == 0


def tracked_basenames(repo: Path) -> dict[str, str]:
    out = subprocess.run(
        ["git", "-C", str(repo), "ls-files"], capture_output=True, text=True
    ).stdout.split("\n")
    index: dict[str, str] = {}
    for path in out:
        if path:
            index.setdefault(Path(path).name, path)
    return index


EXPORT_SUFFIX = re.compile(r"(-[0-9a-f]{16})?( \(\d+\))?$")
BATCH_SUFFIX = re.compile(r"-([0-9a-f]{16})(?: \(\d+\))?$")


def candidate_names(path: Path, data: bytes) -> list[str]:
    stem = EXPORT_SUFFIX.sub("", path.stem)
    names = [stem + path.suffix]
    if path.suffix == ".md" and data.lstrip().startswith((b'"""', b"import ", b"from ", b"class ", b"def ", b"#!")):
        names.append(stem + ".py")
    return names


def classify(path: Path, data: bytes, repos: list[Path], names: dict[Path, dict[str, str]]) -> str:
    sha = git_blob_sha(data)
    hits = [r.name for r in repos if blob_in_history(r, sha)]
    if hits:
        return "history:" + ",".join(hits)
    if path.suffix in ARCHIVE_SUFFIXES:
        return "archive"
    if any(t in data for t in PHYSIONET_TOKENS):
        return "marker:physionet"
    if all(t in data for t in AUTHOR_MIT_TOKENS):
        return "marker:author-mit"
    for cand in candidate_names(path, data):
        for r in repos:
            if cand in names[r]:
                return f"basename:{r.name}/{names[r][cand]}"
    return "none"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--siblings", type=Path, default=Path("..").resolve())
    args = ap.parse_args(argv)

    repos = sibling_repos(args.siblings)
    names = {r: tracked_basenames(r) for r in repos}
    rows = []
    for p in sorted(x for x in CORPUS.iterdir() if x.is_file() and x.name not in SKIP):
        data = p.read_bytes()
        m = BATCH_SUFFIX.search(p.stem)
        batch = m.group(1) if m else "-"
        rows.append((p.name, len(data), hashlib.sha256(data).hexdigest(), batch, classify(p, data, repos, names)))

    consulted = ",".join(r.name for r in repos) or "none"
    with LEDGER.open("w") as f:
        f.write(f"# siblings consulted: {consulted}\n")
        f.write("file\tbytes\tsha256\tbatch\tevidence\n")
        for name, size, sha, batch, ev in rows:
            f.write(f"{name}\t{size}\t{sha}\t{batch}\t{ev}\n")

    kinds: dict[str, int] = {}
    for _, _, _, _, ev in rows:
        kinds[ev.split(":")[0]] = kinds.get(ev.split(":")[0], 0) + 1
    print(f"{len(rows)} files -> {LEDGER}")
    for k, v in sorted(kinds.items(), key=lambda kv: -kv[1]):
        print(f"  {k:10s} {v}")

    # Per-batch view: files sharing an export suffix arrived together, so a
    # batch whose other members trace to one repository suggests, without
    # proving, where its unresolved members came from.
    batches: dict[str, dict[str, int]] = {}
    for _, _, _, batch, ev in rows:
        key = ev.split("/")[0] if ev.startswith("basename:") else ev
        batches.setdefault(batch, {}).setdefault(key, 0)
        batches[batch][key] += 1
    print("batches (export suffix -> evidence counts):")
    for batch, counts in sorted(batches.items(), key=lambda kv: -sum(kv[1].values())):
        summary = ", ".join(f"{k} x{v}" for k, v in sorted(counts.items(), key=lambda kv: -kv[1]))
        print(f"  {batch:18s} {summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
