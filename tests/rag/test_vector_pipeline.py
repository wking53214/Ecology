import pytest

# These tests import src.rag.*, which pulls in lancedb and sentence_transformers
# -- a multi-gigabyte ML stack not needed to work on the rest of this repo.
# Without this guard the failure lands at COLLECTION, which takes the whole
# suite down: 116 passing tests reported as "8 errors during collection"
# because an optional dependency was absent. A skip says "not exercised"; a
# collection error says nothing about the code and hides everything else.
#   pip install lancedb sentence-transformers pypdf google-genai
pytest.importorskip("lancedb", reason="RAG extras not installed")
pytest.importorskip("sentence_transformers", reason="RAG extras not installed")

import os
import shutil
import pytest
from src.rag.ingestion import MarkdownIngestionHandler
from src.rag.storage import StorageManager

def test_end_to_end_pipeline():
    """Validates data flow from raw dictionary chunks to LanceDB storage and search."""
    test_db_dir = "./data/test_vector_store"
    
    # Clean up any lingering test artifacts
    if os.path.exists(test_db_dir):
        shutil.rmtree(test_db_dir)

    try:
        # Initialize components
        handler = MarkdownIngestionHandler(model_name="all-MiniLM-L6-v2")
        manager = StorageManager(uri=test_db_dir)

        # Structure mock input matching parser payloads
        mock_chunks = [
            {
                "content": "The ContentPolishPipeline manages core governance frameworks and telemetry auditing.",
                "metadata": {"source": "governance.md", "section": "integrity"}
            },
            {
                "content": "Star Trek: The Next Generation features Commander Data exploring human emotional states.",
                "metadata": {"source": "star_trek.md", "section": "narrative"}
            }
        ]

        # Step 1: Execute transformation and vector generation
        cells = handler.parse_and_transform(mock_chunks)
        assert len(cells) == 2
        assert cells[0].raw_content == mock_chunks[0]["content"]
        assert len(cells[0].embedding) == 384  # Dimension size for all-MiniLM-L6-v2

        # Step 2: Persist data cells to LanceDB
        manager.ingest(cells)

        # Step 3: Execute vector search query validation
        query_vec = handler.embedding_model.encode("Who is Commander Data?").tolist()
        results = manager.search(query_vec, top_k=1)

        # Assertions to confirm retrieval precision
        assert len(results) == 1
        assert "Commander Data" in results[0]["raw_content"]
        assert results[0]["provenance"]["source"] == "star_trek.md"

    finally:
        # Ensure environment cleanup post-execution
        if os.path.exists(test_db_dir):
            shutil.rmtree(test_db_dir)
