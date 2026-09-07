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
from src.rag.pipeline import RAGOrchestrationPipeline

def test_full_pipeline_orchestration(tmp_path):
    """Validates structural ingestion parsing through vector database persistence layers."""
    test_db_dir = os.path.join(tmp_path, "vector_store")
    doc_dir = os.path.join(tmp_path, "docs")
    os.makedirs(doc_dir, exist_ok=True)

    # 1. Establish localized mock documents mimicking system guides
    doc_a = os.path.join(doc_dir, "governance_spec.md")
    with open(doc_a, "w", encoding="utf-8") as f:
        f.write(
            "---\nmodule: Kernel\nstatus: Hardened\n---\n"
            "## GAPS Module Authentication\n"
            "The registry wrapper validates handshake operations for security isolation.\n"
        )

    doc_b = os.path.join(doc_dir, "fleet_spec.md")
    with open(doc_b, "w", encoding="utf-8") as f:
        f.write(
            "---\ntype: Transport\n---\n"
            "## Vehicle Log\n"
            "The 2021 Toyota Tacoma SR forms a primary transportation node within the local infrastructure.\n"
        )

    # 2. Instantiate and fire the automated production orchestrator
    pipeline = RAGOrchestrationPipeline(db_uri=test_db_dir, max_words=150)
    result = pipeline.orchestrate([doc_a, doc_b])

    # 3. Assert full operational execution counts
    assert result["status"] == "success"
    assert result["cells_ingested"] == 2
    assert len(result["skipped_files"]) == 0

    # 4. Verify cross-layer text retrieval accuracy via semantic query matching
    query_vec = pipeline.ingestion_handler.embedding_model.encode("Tell me about the truck").tolist()
    search_hits = pipeline.storage_manager.search(query_vec, top_k=1)

    assert len(search_hits) == 1
    assert "Toyota Tacoma" in search_hits[0]["raw_content"]
    assert search_hits[0]["provenance"]["source"] == "fleet_spec.md"
