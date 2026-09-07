import os
import sys
import logging
from src.rag.crawler import DirectoryIngestionScanner
from src.rag.pipeline import RAGOrchestrationPipeline
from src.rag.retrieval import RAGQueryEngine
from src.rag.generation import RAGGenerationEngine

# Suppress verbose background warnings during standalone shell execution
logging.basicConfig(level=logging.ERROR)

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_rag.py \"<query>\" [--mock] [target_directory]")
        sys.exit(1)

    query = sys.argv[1]
    is_mock = "--mock" in sys.argv
    
    # Filter remaining arguments to capture the target directory path
    remaining_args = [arg for arg in sys.argv[2:] if arg != "--mock"]
    target_dir = remaining_args[0] if remaining_args else "/home/wking53214/living-memory/src"

    pipeline = RAGOrchestrationPipeline()
    scanner = DirectoryIngestionScanner()

    print(f"[*] Initializing filesystem tree crawl on: {target_dir}")
    scan_results = scanner.execute_batch_ingestion(target_directory=target_dir, pipeline=pipeline)
    print(f"[*] Ingestion sequence complete. Vectorized target files: {scan_results['files_found']}")

    print(f"[*] Running semantic lookup query: \"{query}\"")
    query_engine = RAGQueryEngine()
    
    if is_mock:
        print("[*] Localized simulation mode activated. Bypassing network connection.")
        simulated_response = (
            "SUCCESS: The GSA Universal Adapter module registry confirms that the following "
            "components utilize the @register_as_module decorator for governance authentication:\n"
            "1. UniversalPreprocessor (src/rag/preprocess.py)\n"
            "2. DirectoryIngestionScanner (src/rag/crawler.py)\n"
            "3. GeminiProductionClient (src/rag/generation.py)\n"
            "4. RAGGenerationEngine (src/rag/generation.py)\n"
            "All registered modules conform to the handshake_version='2.3' configuration criteria."
        )
        generation_engine = RAGGenerationEngine(query_engine=query_engine, llm_callable=lambda prompt: simulated_response)
    else:
        if not os.environ.get("GEMINI_API_KEY"):
            print("ERROR: The GEMINI_API_KEY environment variable is not defined.")
            sys.exit(1)
        generation_engine = RAGGenerationEngine(query_engine=query_engine)
    
    synthesis_output = generation_engine.execute_synthesis(query=query, top_k=3)

    print("\n=== GENERATED EVIDENCE-BASED ANALYSIS RESPONSE ===")
    print(synthesis_output["generated_response"])
    print("===================================================\n")

if __name__ == "__main__":
    main()
