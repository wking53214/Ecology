"""Detached, resumable full-corpus index for the memory-clone pipeline.

Runs history_loader -> nomic-embed-text -> one persistent Chroma collection
(`conversation_history_v1` in ecology/chroma_db, rag_engine's default).

Embeds ONE cell per ollama call. Batched embed requests (BATCH=64) were
sending ~64k tokens against a 2048-token context; llama-server degraded
under that load and eventually wedged (spinning at 300% CPU, no output).
Single-cell calls are ~3.5s each and stable.

Resumable: ids already in the collection are skipped (checked 256 at a
time), so a restart picks up where it stopped. A cell whose embed call
exceeds CELL_TIMEOUT is logged and skipped rather than hanging the run;
after STALL_LIMIT consecutive timeouts the llama-server is killed (ollama
respawns it) and the run continues.

Usage:  nohup python3 run_history_index.py Claude_History [ChatGPT_History] &
"""
import subprocess
import sys
import threading
import time

sys.path.insert(0, "/home/wking53214/ecology")

import chromadb  # noqa: E402
import ollama  # noqa: E402

from history_loader import cells_from_history_repo  # noqa: E402

DB_PATH = "/home/wking53214/ecology/chroma_db"
COLLECTION = "conversation_history_v1"
SCAN_CHUNK = 256          # ids per resume-skip lookup
CELL_TIMEOUT = 45.0       # seconds; a slower embed than this is treated as stuck
STALL_LIMIT = 3           # consecutive timeouts before bouncing llama-server
LOG = "/home/wking53214/ecology/history_index.log"
REPOS = {
    "Claude_History": "/home/wking53214/Claude_History",
    "ChatGPT_History": "/home/wking53214/ChatGPT_History",
}


def log(msg):
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def _bounce_llama_server():
    """Kill the llama-server runner; ollama serve respawns it on next call."""
    try:
        subprocess.run(["sudo", "pkill", "-9", "-f", "llama-server"], timeout=15)
        log("  bounced llama-server after repeated timeouts")
        time.sleep(5)
    except Exception as e:  # noqa: BLE001
        log(f"  llama-server bounce failed: {e!r}")


def embed_one(text, timeout=CELL_TIMEOUT):
    """Embed a single string with a wall-clock timeout. None on timeout/error."""
    result = {}

    def _call():
        try:
            result["emb"] = ollama.embed(model="nomic-embed-text", input=[text])["embeddings"][0]
        except Exception as e:  # noqa: BLE001
            result["err"] = e

    t = threading.Thread(target=_call, daemon=True)
    t.start()
    t.join(timeout)
    if t.is_alive():
        return None
    return result.get("emb")


def main(repo_names):
    client = chromadb.PersistentClient(path=DB_PATH)
    col = client.get_or_create_collection(name=COLLECTION)
    log(f"=== start === collection has {col.count()} cells; repos: {repo_names}")

    for name in repo_names:
        cells = list(cells_from_history_repo(REPOS[name]))
        log(f"{name}: {len(cells)} cells to consider")

        # Resume: drop cells already indexed (batched lookup).
        pending = []
        for i in range(0, len(cells), SCAN_CHUNK):
            chunk = cells[i:i + SCAN_CHUNK]
            have = set(col.get(ids=[c.identity for c in chunk])["ids"])
            pending.extend(c for c in chunk if c.identity not in have)
        log(f"{name}: {len(pending)} cells to embed ({len(cells) - len(pending)} already done)")

        done = 0
        skipped = 0
        stalls = 0
        t0 = time.time()
        for cell in pending:
            emb = embed_one(cell.content)
            if emb is None:
                skipped += 1
                stalls += 1
                log(f"  SKIP {cell.identity} (embed timeout/err, len {len(cell.content)})")
                if stalls >= STALL_LIMIT:
                    _bounce_llama_server()
                    stalls = 0
                continue
            stalls = 0
            col.add(
                ids=[cell.identity],
                embeddings=[emb],
                documents=[cell.content],
                metadatas=[{"source": cell.source, "date": cell.date_str, "speaker": cell.speaker}],
            )
            done += 1
            if done % 100 == 0:
                rate = done / max(time.time() - t0, 1e-9)
                eta_h = (len(pending) - done) / max(rate, 1e-9) / 3600
                log(f"  {name}: {done}/{len(pending)} ({rate:.2f} cells/s, ~{eta_h:.1f}h left, "
                    f"{skipped} skipped) | db {col.count()}")
        log(f"{name}: DONE. {done} embedded, {skipped} skipped. collection now {col.count()}.")

    log("=== all repos complete ===")


if __name__ == "__main__":
    args = sys.argv[1:] or ["Claude_History"]
    bad = [a for a in args if a not in REPOS]
    if bad:
        sys.exit(f"unknown repo(s): {bad}")
    main(args)
