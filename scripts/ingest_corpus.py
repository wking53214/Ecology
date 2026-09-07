import os
from pathlib import Path
from src.rag.pipeline import RAGOrchestrationPipeline

def run_recursive_ingestion(root_dir="./corpus"):
    pipeline = RAGOrchestrationPipeline()
    
    # Define valid text-based extensions
    valid_extensions = {'.md', '.txt', '.py', '.json', '.yaml', '.yml', '.c', '.cpp', '.sql'}
    
    # Exclusion filters to prevent indexing the database or environment
    exclude_dirs = {'.git', 'venv', '__pycache__', 'lancedb_data'}
    
    if not os.path.exists(root_dir):
        print(f"ERROR: Directory '{root_dir}' not found. Please verify the path.")
        return

    files_to_ingest = []
    print(f"Scanning directory: {os.path.abspath(root_dir)}")
    
    for path in Path(root_dir).rglob('*'):
        if path.is_file() and path.suffix in valid_extensions:
            # Check if any part of the path is in the exclusion list
            if not any(part in exclude_dirs for part in path.parts):
                files_to_ingest.append(str(path))
    
    print(f"Discovered {len(files_to_ingest)} files. Beginning ingestion...")
    result = pipeline.orchestrate(files_to_ingest)
    print(f"Ingestion complete: {result}")

if __name__ == "__main__":
    run_recursive_ingestion()
