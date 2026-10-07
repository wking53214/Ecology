"""Index one or more git repositories' commit histories into Ecology.

Thin wrapper around rag_engine.index_commit_history. Each commit becomes a
searchable cell with its real author time, author, message and changed
files, in the `commit_history_v1` collection (separate from the
conversation history). Re-running adds only commits not yet indexed.

The clones must hold full history; a shallow clone indexes only the commits
it fetched.

Usage:
  cd ~/ecology
  python3 scripts/run_commit_index.py ~/CCC ~/CNS ~/Conservation_Kernel
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag_engine import index_commit_history  # noqa: E402


def main(paths):
    for path in paths:
        t0 = time.time()
        print(f"[{time.strftime('%H:%M:%S')}] indexing commits of {path} ...", flush=True)
        col = index_commit_history(path)
        print(f"[{time.strftime('%H:%M:%S')}] done in {time.time() - t0:.0f}s; "
              f"collection now {col.count()} cells", flush=True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
