from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from uuid import uuid4

class KnowledgeCell(BaseModel):
    """
    Standardized data contract for all ingested knowledge objects.
    Ensures consistency between raw ingestion and vector storage.
    """
    cell_id: str = Field(default_factory=lambda: str(uuid4()))
    raw_content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[List[float]] = None
    provenance: Dict[str, Any]
