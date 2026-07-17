import os
import time
import ollama
import chromadb

def initialize_vector_store(directory_path="corpus", collection_name="living_memory_vector", batch_size=32):
    client = chromadb.PersistentClient(path="./chroma_db")
    
    try:
        collection = client.get_collection(name=collection_name)
        count = collection.count()
        if count > 0:
            print(f"[System] Loaded existing vector store from disk with {count} chunks. Skipping re-indexing.")
            return collection
    except Exception:
        pass
        
    collection = client.get_or_create_collection(name=collection_name)
    
    if not os.path.exists(directory_path):
        print(f"[System] Directory '{directory_path}' not found.")
        return collection

    files = [f for f in os.listdir(directory_path) if f.endswith((".md", ".txt"))]
    all_ids = []
    all_documents = []
    all_metadatas = []
    
    print(f"[System] Scanning {len(files)} parent files...")
    
    for filename in files:
        filepath = os.path.join(directory_path, filename)
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().strip()
        except Exception:
            continue

        segments = [seg.strip() for seg in content.split('\n\n') if seg.strip()]
        for index, segment in enumerate(segments):
            chunk_id = f"{filename}_cell_{index}"
            all_ids.append(chunk_id)
            all_documents.append(segment)
            all_metadatas.append({"source": filename})

    total_chunks = len(all_documents)
    print(f"[System] Indexing {total_chunks} chunks using batched embeddings...")
    
    start_time = time.perf_counter()
    
    for i in range(0, total_chunks, batch_size):
        batch_ids = all_ids[i:i + batch_size]
        batch_docs = all_documents[i:i + batch_size]
        batch_metas = all_metadatas[i:i + batch_size]
        
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
    sources = results['metadatas'][0]
    
    context_block = ""
    for i, (doc, meta) in enumerate(zip(documents, sources)):
        context_block += f"\n[Context {i+1} from {meta['source']}]:\n{doc}\n"
        
    system_prompt = (
        "You are an analytical executive assistant. Answer the user's query strictly "
        "based on the provided context. If the answer cannot be determined from the "
        "context, state that the information is unavailable in the corpus."
    )
    
    user_prompt = f"Context:\n{context_block}\n\nQuery: {query_text}"
    
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
    
    total_latency = embed_time + query_time + gen_time
    print(f"[Telemetry] Embed: {embed_time:.4f}s | Search: {query_time:.4f}s | Generation: {gen_time:.4f}s | Total: {total_latency:.4f}s\n")
    
    return response['message']['content'], sources

if __name__ == "__main__":
    col = initialize_vector_store()
    
    if not col:
        exit()
        
    print("[System] Optimized RAG engine ready (num_predict=512). Type 'exit' or 'quit' to shut down.")
    
    while True:
        try:
            query = input("\nRAG Query > ")
            if query.strip().lower() in ['exit', 'quit']:
                print("[System] Shutting down RAG engine. Goodbye.")
                break
            if not query.strip():
                continue
                
            answer, sources = generate_response(col, query, model_name="llama3.2", n_results=5)
            
            print("[Synthesized Response]:")
            print(answer)
            print("\n[Referenced Sources]:")
            for src in set(s['source'] for s in sources):
                print(f"- {src}")
                
        except KeyboardInterrupt:
            print("\n[System] Shutting down RAG engine. Goodbye.")
            break
