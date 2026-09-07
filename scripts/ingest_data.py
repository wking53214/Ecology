from src.rag.pipeline import RAGOrchestrationPipeline
import glob

def run_ingestion():
    pipeline = RAGOrchestrationPipeline()
    files = glob.glob("test_knowledge/*.md")
    print(f"Ingesting {len(files)} files...")
    result = pipeline.orchestrate(files)
    print(f"Ingestion result: {result}")

if __name__ == "__main__":
    run_ingestion()
