import sys
from src.rag.pipeline import RAGOrchestrationPipeline
from src.rag.retrieval import RAGQueryEngine
from src.rag.generation import RAGGenerationEngine

class RAGTuningDashboard:
    def __init__(self):
        self.pipeline = RAGOrchestrationPipeline()
        # Initialize engine with dynamic dependencies
        self.query_engine = RAGQueryEngine(
            storage_manager=self.pipeline.storage_manager,
            embedding_model=self.pipeline.embedding_model
        )
        self.gen_engine = RAGGenerationEngine(query_engine=self.query_engine)
        
        self.top_k = 3
        self.max_distance = 1.2

    def display_menu(self):
        print("\n--- RAG TUNING DASHBOARD ---")
        print(f"1. Set Top-K ({self.top_k})")
        print(f"2. Set Max-Distance ({self.max_distance})")
        print("3. Execute Query & Visualize")
        print("4. Exit")
        return input("Selection: ")

    def run(self):
        while True:
            choice = self.display_menu()
            if choice == "1":
                self.top_k = int(input("Enter new Top-K: "))
            elif choice == "2":
                self.max_distance = float(input("Enter new Max-Distance: "))
            elif choice == "3":
                query = input("Enter Query: ")
                # Retrieval
                retrieval = self.query_engine.retrieve_context(
                    query=query, top_k=self.top_k, max_distance=self.max_distance
                )
                print("\n--- CONTEXT WINDOW VISUALIZER ---")
                print(retrieval["context_window"])
                print("\n--- COMPILED PROMPT ---")
                print(self.gen_engine.compile_prompt(query, retrieval["context_window"]))
            elif choice == "4":
                sys.exit(0)

if __name__ == "__main__":
    dashboard = RAGTuningDashboard()
    dashboard.run()
