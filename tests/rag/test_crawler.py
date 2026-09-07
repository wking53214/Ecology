import os
import pytest
from unittest.mock import MagicMock
from src.rag.crawler import DirectoryIngestionScanner
from src.rag.pipeline import RAGOrchestrationPipeline

def test_directory_scanner_recursive_discovery(tmp_path):
    """Verifies recursive collection of supported file extensions across subdirectories."""
    src_dir = tmp_path / "src"
    docs_dir = tmp_path / "docs"
    nested_dir = docs_dir / "nested"
    
    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(nested_dir, exist_ok=True)

    (src_dir / "main.py").write_text("def run(): pass")
    (docs_dir / "guide.md").write_text("# Documentation")
    (nested_dir / "patch_v1.patch").write_text("--- a/file")
    
    (docs_dir / "image.png").write_text("binary data")
    (src_dir / "cache.log").write_text("system output log data")

    scanner = DirectoryIngestionScanner(state_file=str(tmp_path / "state.json"))
    discovered_files = scanner.scan(str(tmp_path))
    
    assert len(discovered_files) == 3
    basenames = [os.path.basename(f) for f in discovered_files]
    assert "main.py" in basenames
    assert "guide.md" in basenames
    assert "patch_v1.patch" in basenames

def test_batch_ingestion_execution_flow(tmp_path):
    """Validates communication coordinates cleanly with the orchestrator pipeline layer."""
    test_file = tmp_path / "data.csv"
    test_file.write_text("col1,col2\nval1,val2")
    
    scanner = DirectoryIngestionScanner(state_file=str(tmp_path / "state.json"))
    mock_pipeline = MagicMock(spec=RAGOrchestrationPipeline)
    mock_pipeline.orchestrate.return_value = {"cells_ingested": 5, "skipped_files": []}
    
    mock_pipeline.preprocessor = MagicMock()
    mock_pipeline.preprocessor._parsers = {}
    mock_pipeline.storage_manager = MagicMock()
    
    result = scanner.execute_batch_ingestion(str(tmp_path), mock_pipeline)
    
    assert result["status"] == "success"
    assert result["files_found"] == 1
    assert result["pipeline_result"]["cells_ingested"] == 5
    mock_pipeline.orchestrate.assert_called_once_with([str(test_file)])
