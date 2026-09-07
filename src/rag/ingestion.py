from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from src.rag.schema import KnowledgeCell
from src.governance.registry import register_as_module

@register_as_module(system_auth="GSA_UNIVERSAL_ADAPTER", handshake_version="2.3")
class MarkdownIngestionHandler:
    """Transforms parsed Markdown structural blocks into vector-populated KnowledgeCell objects."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.embedding_model = SentenceTransformer(model_name)

    def parse_and_transform(self, raw_chunks: List[Dict[str, Any]]) -> List[KnowledgeCell]:
        """Processes raw text segments, computes vector fields, and returns validated schema objects."""
        knowledge_cells = []
        
        for chunk in raw_chunks:
            text_content = chunk.get("content", "")
            metadata = chunk.get("metadata", {})
            
            vector_embedding = self.embedding_model.encode(text_content).tolist()
            
            # Aligns explicitly with raw_content, embedding, and provenance field parameters
            cell = KnowledgeCell(
                raw_content=text_content,
                embedding=vector_embedding,
                provenance=metadata
            )
            knowledge_cells.append(cell)
            
        return knowledge_cells
