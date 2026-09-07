import os
import json
import pytest
from unittest.mock import MagicMock
from src.rag.crawler import DirectoryIngestionScanner
from src.rag.pipeline import RAGOrchestrationPipeline

def test_incremental_scanner_skips_unmodified_files(tmp_path):
    """Verifies that files with matching checksums are skipped on consecutive crawl runs."""
    state_db = tmp_path / "state.json"
    workspace = tmp_path / "workspace"
    os.makedirs(workspace, exist_ok=True)
    
    target_doc = workspace / "logic.py"
    target_doc.write_text("print('core integrity functional')")

    mock_pipeline = MagicMock(spec=RAGOrchestrationPipeline)
    mock_pipeline.orchestrate.return_value = {"cells_ingested": 2, "skipped_files": []}
    
    # Explicitly wire internal attributes expected by the ingestion logic
    mock_pipeline.preprocessor = MagicMock()
    mock_pipeline.preprocessor._parsers = {}
    mock_pipeline.storage_manager = MagicMock()
    
    # Run 1: Index fresh document tracking states
    scanner_first = DirectoryIngestionScanner(state_file=str(state_db))
    result_first = scanner_first.execute_batch_ingestion(str(workspace), mock_pipeline)
    
    assert result_first["files_vectorized"] == 1
    assert os.path.exists(str(state_db))
    mock_pipeline.orchestrate.assert_called_once()
    
    # Run 2: Verify the document is skipped because it remains unmodified
    mock_pipeline.reset_mock()
    # Ensure preprocessor/storage_manager are re-added after reset_mock()
    mock_pipeline.preprocessor = MagicMock()
    mock_pipeline.preprocessor._parsers = {}
    mock_pipeline.storage_manager = MagicMock()
    
    scanner_second = DirectoryIngestionScanner(state_file=str(state_db))
    result_second = scanner_second.execute_batch_ingestion(str(workspace), mock_pipeline)
    
    assert result_second["files_found"] == 1
    assert result_second["files_vectorized"] == 0
    mock_pipeline.orchestrate.assert_not_called()
