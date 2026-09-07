import os
import zipfile
import pytest
from unittest.mock import MagicMock
from src.rag.crawler import DirectoryIngestionScanner
from src.rag.pipeline import RAGOrchestrationPipeline

def test_zip_in_memory_extraction(tmp_path):
    """Confirms zip archives extract compliant documents into stream buffers while dropping unmapped blocks."""
    zip_file_path = tmp_path / "codebase.zip"
    
    # Pack various whitelisted and excluded file tracks into our test archive
    with zipfile.ZipFile(zip_file_path, 'w') as zf:
        zf.writestr("core.py", "def execute(): return True")
        zf.writestr("readme.txt", "Living Memory Platform Core")
        zf.writestr("icon.png", "binary_image_stream_data")

    scanner = DirectoryIngestionScanner()
    virtual_files = scanner.process_zip_in_memory(str(zip_file_path))
    
    # Assertions verify that only the whitelisted files were extracted
    assert len(virtual_files) == 2
    virtual_names = [v["virtual_path"] for v in virtual_files]
    assert any("core.py" in name for name in virtual_names)
    assert any("readme.txt" in name for name in virtual_names)
    assert not any("icon.png" in name for name in virtual_names)
