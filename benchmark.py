import time
from ecology import ingest_directory
from rag_engine import initialize_vector_store, generate_response

def run_benchmark():
    start_init = time.perf_counter()
    cells = ingest_directory("corpus")
    init_time = time.perf_counter() - start_init

    if not cells:
        print("[Benchmark] No cells ingested; add content to 'corpus' and try again.")
        return

    start_index = time.perf_counter()
    collection = initialize_vector_store(directory_path="corpus")
    index_time = time.perf_counter() - start_index

    test_query = "What is the operational status of the telemetry aggregator?"
    print(f"\n[Benchmark] Executing test query against {collection.count()} indexed chunks...")

    start_query = time.perf_counter()
    generate_response(collection, test_query, n_results=5)
    query_time = time.perf_counter() - start_query

    print(f"\n[Performance Summary]")
    print(f"- Ingestion Time: {init_time:.4f} seconds ({len(cells)} cells)")
    print(f"- Indexing Time: {index_time:.4f} seconds")
    print(f"- Query Latency: {query_time:.4f} seconds")

if __name__ == "__main__":
    run_benchmark()
