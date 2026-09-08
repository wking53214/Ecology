# corpus/ provenance

**This directory is data, not code, and it is not covered by the repository's
LICENSE.**

`corpus/` holds 360 files harvested from other systems and conversations (199
Markdown, 91 Python, 49 text, 8 patches, 6 JSON, as of 2026-09-07). Several
are flattened, with their line breaks destroyed before they arrived; they are
excluded from pytest and ruff by `pytest.ini` and `ruff.toml` for that reason.

What is known about their licenses:

- `LICENSE-38ace9a314da6382.md` is a BSD 3-Clause license naming the George B.
  Moody PhysioNet Challenges. Files that came with it are redistributable under
  that license's conditions, but **which files those are is not recorded**.
- `LICENSE-8fdaa84c270b798e.md` is an MIT license naming William N King.
- Every other file has **no recorded origin or license**.

Consequences:

1. Do not redistribute `corpus/` as part of an ecology release, wheel, or
   demo dataset until each file's origin and license are recorded here.
2. The Apache-2.0 `LICENSE` at the repository root covers ecology's own code
   (`*.py` at the root, `src/`, `scripts/`, `tests/`) and nothing under
   `corpus/` or `raw_sources/`.
3. `raw_sources/` (PDF exports of chat transcripts) is the author's own
   material and is likewise not part of any release.

Recorded 2026-09-07 following an external audit that found no LICENSE file
and no provenance record for this directory.
