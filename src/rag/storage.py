from typing import List
import json
import lancedb
import pyarrow as pa
from src.rag.schema import KnowledgeCell
from src.governance.registry import register_as_module

@register_as_module(system_auth="GSA_UNIVERSAL_ADAPTER", handshake_version="2.3")
class StorageManager:
    """Handles the ingestion and persistence of KnowledgeCell objects."""

    def __init__(self, uri: str = "./data/vector_store"):
        self.db = lancedb.connect(uri)
        self.table_name = "knowledge_base"
        self._ensure_table()

    def _ensure_table(self):
        """Initializes the table safely using native idempotency flags."""
        schema = pa.schema([
            ("cell_id", pa.string()),
            ("raw_content", pa.string()),
            ("embedding", pa.list_(pa.float32(), 384)),
            ("provenance", pa.string()),
            ("metadata", pa.string())
        ])
        # Using exist_ok=True natively prevents existing table collisions
        self.db.create_table(self.table_name, schema=schema, exist_ok=True)

    def ingest(self, cells: List[KnowledgeCell]):
        """Ingests list of cells into the vector database after parsing structures to JSON strings."""
        data = []
        for cell in cells:
            cell_dict = cell.model_dump()
            cell_dict["provenance"] = json.dumps(cell_dict.get("provenance", {}))
            cell_dict["metadata"] = json.dumps(cell_dict.get("metadata", {}))
            data.append(cell_dict)
            
        table = self.db.open_table(self.table_name)
        table.add(data)

    def search(self, query_vector: List[float], top_k: int = 5):
        """Retrieves nearest neighbors using the custom embedding vector field name."""
        table = self.db.open_table(self.table_name)
        raw_results = table.search(query_vector, vector_column_name="embedding").limit(top_k).to_list()
        
        for result in raw_results:
            if "provenance" in result and isinstance(result["provenance"], str):
                try:
                    result["provenance"] = json.loads(result["provenance"])
                except Exception:
                    result["provenance"] = {}
            if "metadata" in result and isinstance(result["metadata"], str):
                try:
                    result["metadata"] = json.loads(result["metadata"])
                except Exception:
                    result["metadata"] = {}
                    
        return raw_results
