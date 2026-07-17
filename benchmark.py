import time
from ecology import ingest_directory, broadcast_to_ether

def run_benchmark():
    start_init = time.perf_counter()
    ecology = ingest_directory("corpus")
    init_time = time.perf_counter() - start_init
    
    test_query = "What is the operational status of the telemetry aggregator?"
    print(f"\n[Benchmark] Executing test query against {len(ecology)} active cells...")
    
    start_broadcast = time.perf_counter()
    broadcast_to_ether(ecology, test_query)
    broadcast_time = time.perf_counter() - start_broadcast
    
    print(f"\n[Performance Summary]")
    print(f"- Initialization Time: {init_time:.4f} seconds")
    print(f"- Broadcast Latency: {broadcast_time:.4f} seconds")
    print(f"- Average Time per Cell: {(broadcast_time / len(ecology)):.6f} seconds")

if __name__ == "__main__":
    run_benchmark()
