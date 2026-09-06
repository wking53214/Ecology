"""Index the *_History conversation archives into the vector store.

Thin wrapper around rag_engine.index_history_repo, which now uses the local
in-process ONNX embedder (all-MiniLM-L6-v2, 384-dim, ~10 cells/sec, no
ollama server). The whole ~40k-cell corpus indexes in roughly an hour.

The earlier version of this script fought nomic-embed-text via ollama:
batched embed calls of 64 cells (~64k tokens against a 2048-ctx runner)
progressively wedged llama-server, and a full run failed on a 100%-full
disk (HNSW footprint was ~2.2 GB at 25k cells, not the ~770 MB
extrapolated from a small sample). The ONNX embedder removes both problems
-- no server to wedge, half the vector width, and it is fast enough that
resumability and per-cell timeouts are no longer worth the complexity.

Usage (detached, survives the session):
  cd ~/ecology
  nohup python3 scripts/run_history_index.py > history_index.log 2>&1 &
"""
import sys
import time

sys.path.insert(0, "/home/wking53214/ecology")

from rag_engine import index_history_repo  # noqa: E402

REPOS = {
    "Claude_History": "/home/wking53214/Claude_History",
    "ChatGPT_History": "/home/wking53214/ChatGPT_History",
}


def main(names):
    for name in names:
        t0 = time.time()
        print(f"[{time.strftime('%H:%M:%S')}] indexing {name} ...", flush=True)
        col = index_history_repo(REPOS[name])
        print(f"[{time.strftime('%H:%M:%S')}] {name} done in {(time.time() - t0) / 60:.1f} min; "
              f"collection now {col.count()} cells", flush=True)


if __name__ == "__main__":
    args = sys.argv[1:] or list(REPOS)
    bad = [a for a in args if a not in REPOS]
    if bad:
        sys.exit(f"unknown repo(s): {bad}")
    main(args)
