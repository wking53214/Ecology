import re
import time
import ollama
import chromadb

from ecology import ingest_directory, ActiveKnowledgeObject

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

# Bump this whenever ingestion/chunking logic changes, so a stale on-disk
# collection built under the old scheme (different identities, no .py
# chunks) doesn't get silently reused instead of re-indexed.
DEFAULT_COLLECTION_NAME = "living_memory_v2"


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
    """Batched-embed and add a list of cells to a Chroma collection. A cell
    is anything with .identity / .content plus whatever _cell_metadata
    reads (.source, and .date_str / .speaker when present)."""
    total = len(cells)
    if not total:
        return collection
    print(f"[System] Indexing {total} chunks using batched embeddings...")
    start = time.perf_counter()
    for i in range(0, total, batch_size):
        batch = cells[i:i + batch_size]
        try:
            response = ollama.embed(model='nomic-embed-text', input=[c.content for c in batch])
            collection.add(
                ids=[c.identity for c in batch],
                embeddings=response['embeddings'],
                documents=[c.content for c in batch],
                metadatas=[_cell_metadata(c) for c in batch],
            )
        except Exception as e:
            print(f"[Batch Error at index {i}]: {e}")
    print(f"[System] Indexed {total} chunks in {time.perf_counter() - start:.4f}s.\n")
    return collection


def initialize_vector_store(directory_path="corpus", collection_name=DEFAULT_COLLECTION_NAME, batch_size=32, db_path="./chroma_db"):
    client = chromadb.PersistentClient(path=db_path)
    collection, populated = _open_or_load_collection(client, collection_name)
    if populated:
        return collection
    return _index_cells(collection, ingest_directory(directory_path), batch_size)


def index_history_repo(repo_path, collection_name="conversation_history_v1", batch_size=32,
                       db_path="./chroma_db", limit=None, max_cell_chars=None):
    """Index a *_History conversation archive (via history_loader) into its
    own Chroma collection. Separate collection from the code/docs corpus:
    conversation cells carry real message timestamps and a speaker, and
    mixing them with mtime-stamped file chunks would blur exactly the
    signal the archive is for. `limit` caps conversations (smoke runs)."""
    from history_loader import DEFAULT_MAX_CELL_CHARS, cells_from_history_repo

    client = chromadb.PersistentClient(path=db_path)
    collection, populated = _open_or_load_collection(client, collection_name)
    if populated:
        return collection
    cells = list(cells_from_history_repo(
        repo_path, limit=limit,
        max_cell_chars=max_cell_chars or DEFAULT_MAX_CELL_CHARS,
    ))
    return _index_cells(collection, cells, batch_size)


def generate_response(collection, query_text, model_name="llama3.2", n_results=5):
    """Retrieve the top-n_results chunks by embedding similarity, verify each
    one actually supports the query (the same containment check the old
    per-cell broadcast used), and only synthesize an answer from the chunks
    that pass. If nothing passes, say so rather than letting the model
    synthesize an answer from ungrounded context.
    """
    print(f"\n--- Synthesizing Response for: '{query_text}' (n_results={n_results}) ---")

    start_embed = time.perf_counter()
    query_response = ollama.embed(model='nomic-embed-text', input=query_text)
    query_embedding = query_response['embeddings'][0]
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

    start_verify = time.perf_counter()
    verified = []
    for cell_id, doc, meta in zip(ids, documents, metadatas):
        cell = ActiveKnowledgeObject(identity=cell_id, content=doc, timestamp=0, source=meta['source'])
        extract = cell.receive_message(query_text)
        if extract is not None:
            verified.append({"source": meta['source'], "extract": extract})
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
    # just a citation to it (see finding.py).
    sources = [{"source": item["source"], "extract": item["extract"]} for item in verified]
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
