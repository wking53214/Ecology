import re
import time
import ollama
import chromadb
from chromadb.utils import embedding_functions

from containment import verify as verify_containment
from ecology import ingest_directory, ActiveKnowledgeObject

# Local, in-process embedder: ChromaDB's bundled all-MiniLM-L6-v2 as a
# quantized ONNX model (384-dim, ~80MB, onnxruntime -- no torch, no ollama
# server). Replaces nomic-embed-text via ollama, which on this CPU ran at
# ~0.28 cells/sec on real-length cells AND progressively wedged llama-server
# under batched load until a full-corpus index run failed. This one measures
# ~12 cells/sec on the same cells and holds up, and 384-dim halves the
# on-disk HNSW footprint. Synthesis still uses ollama.chat (llama3.2) --
# that's a separate concern from retrieval.
_EMBEDDER = None


def _embed(texts: list[str]) -> list[list[float]]:
    """Embed a list of strings with the local ONNX model (lazy-loaded on
    first use, so `import rag_engine` stays cheap for callers that mock this)."""
    global _EMBEDDER
    if _EMBEDDER is None:
        _EMBEDDER = embedding_functions.ONNXMiniLM_L6_V2()
    return _EMBEDDER(texts)

# Term-overlap floor for the synthesis-verification check below. Same idea
# as Resume_OS's validate.py MEANING DRIFT check (a reworded line has to
# keep a minimum share of its source's meaningful terms), ported here rather
# than imported -- this module stays free of a dependency on that repo, but
# the principle is the same: per-excerpt verification only proves each
# excerpt was real, not that the LLM's synthesis of them stayed faithful.
_SYNTHESIS_TERM = re.compile(r"[a-zA-Z][a-zA-Z0-9+/.-]*")
_SYNTHESIS_STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "to", "in", "on", "for", "with",
    "by", "at", "as", "from", "into", "that", "this", "it", "is", "are",
    "was", "were", "be", "been", "being", "has", "have", "had", "not",
    "which", "who", "what", "when", "where", "how", "query", "answer",
}
SYNTHESIS_OVERLAP_FLOOR = 0.35


def _terms(text: str) -> set:
    return {w.lower().strip(".-/") for w in _SYNTHESIS_TERM.findall(text)
            if len(w) > 2 and w.lower() not in _SYNTHESIS_STOPWORDS}


def _synthesis_matches_its_own_sources(answer: str, verified: list) -> bool:
    """Per-excerpt containment proves each excerpt was real. It says nothing
    about whether the LLM's synthesis of them stayed faithful once combined
    -- that's a separate check, and this is it.

    Direction matters: this checks how much of what the ANSWER says is
    grounded in the source terms, not how much of the sources the answer
    covers (a faithful answer can be far shorter than its sources; that's
    summarization, not drift). Catching an answer that introduces something
    the sources never said is the goal here, the same shape as Resume_OS's
    NUMBER DRIFT check -- new content in the output that isn't in the input.
    """
    combined = " ".join(item["extract"] for item in verified)
    source_terms = _terms(combined)
    answer_terms = _terms(answer)
    if not answer_terms:
        return False
    kept = len(answer_terms & source_terms) / len(answer_terms)
    return kept >= SYNTHESIS_OVERLAP_FLOOR

# Bump this whenever ingestion/chunking logic OR the embedding model
# changes, so a stale on-disk collection built under the old scheme
# (different vector space, different identities) doesn't get silently
# reused instead of re-indexed. v3: switched nomic-embed-text (768d, ollama)
# -> ONNXMiniLM_L6_V2 (384d, in-process).
DEFAULT_COLLECTION_NAME = "living_memory_v3"
HISTORY_COLLECTION_NAME = "conversation_history_v2"
COMMIT_COLLECTION_NAME = "commit_history_v1"


def _cell_metadata(cell) -> dict:
    """Chroma metadata for one cell. `source` always; `date` and `speaker`
    when the cell carries them (history_loader.ConversationCell does,
    ingest_directory's ActiveKnowledgeObject carries date only). Kept so
    the real conversation time and who-said-it survive indexing -- a
    memory system that reconstructs *when* cannot afford to drop them
    here, and re-deriving them means a full re-index."""
    meta = {"source": cell.source}
    date = getattr(cell, "date_str", None)
    if date:
        meta["date"] = date
    speaker = getattr(cell, "speaker", None)
    if speaker:
        meta["speaker"] = speaker
    return meta


def _open_or_load_collection(client, collection_name):
    """(collection, already_populated). A non-empty on-disk collection is
    returned as-is -- callers skip re-indexing."""
    try:
        collection = client.get_collection(name=collection_name)
        if collection.count() > 0:
            print(f"[System] Loaded existing vector store from disk with {collection.count()} chunks. Skipping re-indexing.")
            return collection, True
    except Exception:
        pass
    return client.get_or_create_collection(name=collection_name), False


def _index_cells(collection, cells, batch_size):
    """Batched-embed and add a list of cells to a Chroma collection, skipping
    any whose identity is already present. Idempotent and safe to call
    repeatedly and with more than one source repo into the same collection
    (a re-run resumes; a second archive appends). A cell is anything with
    .identity / .content plus whatever _cell_metadata reads (.source, and
    .date_str / .speaker when present)."""
    cells = list(cells)
    if not cells:
        return collection

    # Drop cells already indexed (batched existence check).
    present = set()
    for i in range(0, len(cells), 512):
        ids = [c.identity for c in cells[i:i + 512]]
        present.update(collection.get(ids=ids, include=[])["ids"])
    if present:
        cells = [c for c in cells if c.identity not in present]
        print(f"[System] {len(present)} chunks already indexed; {len(cells)} new.")

    total = len(cells)
    if not total:
        print("[System] Nothing new to index.\n")
        return collection
    print(f"[System] Indexing {total} chunks with the local ONNX embedder...")
    start = time.perf_counter()
    for i in range(0, total, batch_size):
        batch = cells[i:i + batch_size]
        try:
            embeddings = _embed([c.content for c in batch])
            collection.add(
                ids=[c.identity for c in batch],
                embeddings=embeddings,
                documents=[c.content for c in batch],
                metadatas=[_cell_metadata(c) for c in batch],
            )
        except Exception as e:
            print(f"[Batch Error at index {i}]: {e}")
        if i and i % (batch_size * 50) == 0:
            rate = i / (time.perf_counter() - start)
            print(f"[System]   {i}/{total} ({rate:.0f} cells/s)")
    print(f"[System] Indexed {total} chunks in {time.perf_counter() - start:.4f}s.\n")
    return collection


def initialize_vector_store(directory_path="corpus", collection_name=DEFAULT_COLLECTION_NAME, batch_size=32, db_path="./chroma_db"):
    client = chromadb.PersistentClient(path=db_path)
    collection, populated = _open_or_load_collection(client, collection_name)
    if populated:
        return collection
    return _index_cells(collection, ingest_directory(directory_path), batch_size)


def index_history_repo(repo_path, collection_name=HISTORY_COLLECTION_NAME, batch_size=32,
                       db_path="./chroma_db", limit=None, max_cell_chars=None):
    """Index a *_History conversation archive (via history_loader) into its
    own Chroma collection. Separate collection from the code/docs corpus:
    conversation cells carry real message timestamps and a speaker, and
    mixing them with mtime-stamped file chunks would blur exactly the
    signal the archive is for. `limit` caps conversations (smoke runs)."""
    from history_loader import DEFAULT_MAX_CELL_CHARS, cells_from_history_repo

    client = chromadb.PersistentClient(path=db_path)
    # Not _open_or_load_collection's skip-if-populated path: more than one
    # archive lands in this one collection, so "already has rows" does not
    # mean "this repo is done". _index_cells skips per-identity instead.
    collection = client.get_or_create_collection(name=collection_name)
    cells = cells_from_history_repo(
        repo_path, limit=limit,
        max_cell_chars=max_cell_chars or DEFAULT_MAX_CELL_CHARS,
    )
    return _index_cells(collection, cells, batch_size)


def index_commit_history(repo_path, collection_name=COMMIT_COLLECTION_NAME, batch_size=32,
                         db_path="./chroma_db", limit=None, max_cell_chars=None,
                         include_merges=False):
    """Index a git repository's commit history (via commit_loader) into its
    own Chroma collection. Separate from both the code/docs corpus and the
    conversation history: commits carry the real author time and author,
    and keeping "what changed" apart from "why it was discussed" lets a
    query ask each on its own terms. More than one repository can land in
    the same collection; a re-run adds only commits not yet indexed.
    `limit` caps commits (smoke runs)."""
    from commit_loader import cells_from_git_repo
    from history_loader import DEFAULT_MAX_CELL_CHARS

    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection(name=collection_name)
    cells = cells_from_git_repo(
        repo_path, limit=limit, include_merges=include_merges,
        max_cell_chars=max_cell_chars or DEFAULT_MAX_CELL_CHARS,
    )
    return _index_cells(collection, cells, batch_size)


def generate_response(collection, query_text, model_name="llama3.2", n_results=5,
                      verifier="deterministic"):
    """Retrieve the top-n_results chunks by embedding similarity, verify each
    one actually supports the query (the same containment check the old
    per-cell broadcast used), and only synthesize an answer from the chunks
    that pass. If nothing passes, say so rather than letting the model
    synthesize an answer from ungrounded context.
    """
    print(f"\n--- Synthesizing Response for: '{query_text}' (n_results={n_results}) ---")

    start_embed = time.perf_counter()
    query_embedding = _embed([query_text])[0]
    embed_time = time.perf_counter() - start_embed

    start_query = time.perf_counter()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    query_time = time.perf_counter() - start_query

    documents = results['documents'][0]
    metadatas = results['metadatas'][0]
    ids = results['ids'][0]

    # Containment verification. Deterministic by default.
    #
    # The LLM path made two model calls per candidate passage -- a relevance
    # classification and an extraction. Measured on this machine: a
    # two-passage query did not finish in 120 seconds, against retrieval that
    # takes 0.08s (lexical) to 2.1s (vector). Verification was the entire
    # wall, and it meant the Ecology -> CCC path had never completed once on
    # real data. containment.verify runs the same check at ~48 passages/sec.
    #
    # `verifier="llm"` keeps the original path available, because the two
    # answer slightly different questions and a disagreement between them is
    # worth being able to produce on demand: the deterministic one establishes
    # lexical and structural containment, the model one attempts paraphrase
    # judgement. Neither claims the passage is true.
    start_verify = time.perf_counter()
    verified = []
    for cell_id, doc, meta in zip(ids, documents, metadatas):
        if verifier == "deterministic":
            extract = verify_containment(query_text, doc)
        else:
            cell = ActiveKnowledgeObject(identity=cell_id, content=doc,
                                         timestamp=0, source=meta['source'])
            extract = cell.receive_message(query_text)
        if extract is not None:
            item = {"source": meta['source'], "extract": extract}
            if meta.get("date"):
                item["date"] = meta["date"]
            if meta.get("speaker"):
                item["speaker"] = meta["speaker"]
            verified.append(item)
    verify_time = time.perf_counter() - start_verify

    if not verified:
        total_latency = embed_time + query_time + verify_time
        print(f"[Telemetry] Embed: {embed_time:.4f}s | Search: {query_time:.4f}s | Verify: {verify_time:.4f}s | Total: {total_latency:.4f}s\n")
        return (
            "The retrieved corpus does not contain a verifiable answer to this query.",
            []
        )

    context_block = ""
    for i, item in enumerate(verified):
        context_block += f"\n[Verified excerpt {i+1} from {item['source']}]:\n{item['extract']}\n"

    system_prompt = (
        "You are an analytical executive assistant. Answer the user's query using "
        "only the verified excerpts provided below — each has already been confirmed "
        "to be a literal excerpt of its source. Do not introduce claims beyond what "
        "these excerpts state."
    )

    user_prompt = f"Verified excerpts:\n{context_block}\n\nQuery: {query_text}"

    start_gen = time.perf_counter()
    response = ollama.chat(
        model=model_name,
        options={
            "num_predict": 512,
            "temperature": 0.1,
            "num_thread": 4
        },
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    gen_time = time.perf_counter() - start_gen

    total_latency = embed_time + query_time + verify_time + gen_time
    print(f"[Telemetry] Embed: {embed_time:.4f}s | Search: {query_time:.4f}s | Verify: {verify_time:.4f}s | Generation: {gen_time:.4f}s | Total: {total_latency:.4f}s\n")

    answer = response['message']['content']

    # Per-excerpt containment proved each excerpt was real. This is the
    # separate check that the LLM's synthesis of them stayed faithful --
    # skip it, and a paraphrase drift in the combination step would still
    # come back tagged as "verified" on the strength of excerpts it no
    # longer accurately reflects.
    if not _synthesis_matches_its_own_sources(answer, verified):
        return (
            "The retrieved corpus does not contain a verifiable answer to this query.",
            []
        )

    # source_material carries the extract too now, not just the path --
    # a downstream governance consumer needs the actual verified text, not
    # just a citation to it (see finding.py). `date` / `speaker` ride along
    # when the collection carried them (the conversation-history path), so
    # the finding can be given a real event-time span.
    sources = [
        {k: v for k, v in item.items() if k in ("source", "extract", "date", "speaker")}
        for item in verified
    ]
    return answer, sources


if __name__ == "__main__":
    col = initialize_vector_store()

    if not col:
        exit()

    print("[System] Unified RAG engine ready. Type 'exit' or 'quit' to shut down.")

    while True:
        try:
            query = input("\nQuery > ")
            if query.strip().lower() in ['exit', 'quit']:
                print("[System] Shutting down. Goodbye.")
                break
            if not query.strip():
                continue

            answer, sources = generate_response(col, query, model_name="llama3.2", n_results=5)

            print("[Synthesized Response]:")
            print(answer)
            if sources:
                print("\n[Verified Sources]:")
                for src in {s['source'] for s in sources}:
                    print(f"- {src}")

        except KeyboardInterrupt:
            print("\n[System] Shutting down. Goodbye.")
            break
