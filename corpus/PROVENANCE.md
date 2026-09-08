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

## Per-file ledger (added 2026-09-08)

`ORIGIN.tsv` in this directory records, for every file here, its size, SHA-256,
export batch and the strongest origin evidence a script could establish.
Regenerate it with `python scripts/corpus_origin.py --siblings <dir of the
author's checkouts>`; `tests/unit/test_corpus_origin.py` fails if the ledger
and the directory drift apart.

Result of the first run, with 17 sibling repositories consulted:

| evidence | files | meaning |
|---|---|---|
| `history:<repo>` | 123 | exact bytes exist in that repository's git history: the author's own material (OBSERVE 79, GEMS/innovation_os 43, observe-perceive 1) |
| `basename:<repo>/<path>` | 23 | same name tracked in a sibling repository, bytes differ: a diverged copy, origin likely, content unverified |
| `marker:physionet` | 2 | the PhysioNet Challenge 2026 example README and its BSD-3 license |
| `archive` | 1 | `synapsis-master.zip`: an Apache-2.0 project snapshot that also contains its `.venv/` (4,137 third-party site-package files); not indexed here, and not redistributable as-is |
| `none` | 187 | no marker in the bytes and no match in any sibling repository |

The 187 unresolved files are 122 Markdown, 56 Python and 9 text files. Most
carry a 16-hex export suffix shared with files that do resolve, which says
where a batch was exported from but is not evidence about any single file.
They stay excluded from any release until someone who was there records
their origin. Nothing in this ledger changes the license position above.

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
