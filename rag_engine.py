import time
import ollama
import chromadb

from ecology import ingest_directory, ActiveKnowledgeObject

# Bump this whenever ingestion/chunking logic changes, so a stale on-disk
# collection built under the old scheme (different identities, no .py
# chunks) doesn't get silently reused instead of re-indexed.
DEFAULT_COLLECTION_NAME = "living_memory_v2"


def initialize_vector_store(directory_path="corpus", collection_name=DEFAULT_COLLECTION_NAME, batch_size=32, db_path="./chroma_db"):
    client = chromadb.PersistentClient(path=db_path)

    try:
        collection = client.get_collection(name=collection_name)
        count = collection.count()
        if count > 0:
            print(f"[System] Loaded existing vector store from disk with {count} chunks. Skipping re-indexing.")
            return collection
    except Exception:
        pass

    collection = client.get_or_create_collection(name=collection_name)

    cells = ingest_directory(directory_path)
    if not cells:
        return collection

    total_chunks = len(cells)
    print(f"[System] Indexing {total_chunks} chunks using batched embeddings...")

    start_time = time.perf_counter()

    for i in range(0, total_chunks, batch_size):
        batch = cells[i:i + batch_size]
        batch_ids = [cell.identity for cell in batch]
        batch_docs = [cell.content for cell in batch]
        batch_metas = [{"source": cell.source} for cell in batch]

        try:
            response = ollama.embed(model='nomic-embed-text', input=batch_docs)
            batch_embeddings = response['embeddings']

            collection.add(
                ids=batch_ids,
                embeddings=batch_embeddings,
                documents=batch_docs,
                metadatas=batch_metas
            )
        except Exception as e:
            print(f"[Batch Error at index {i}]: {e}")

    elapsed = time.perf_counter() - start_time
    print(f"[System] Successfully indexed {total_chunks} chunks in {elapsed:.4f} seconds.\n")
    return collection


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

    sources = [{"source": item["source"]} for item in verified]
    return response['message']['content'], sources


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
