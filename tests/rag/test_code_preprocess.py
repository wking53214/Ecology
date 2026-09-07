import os
import pytest
from src.rag.preprocess import UniversalPreprocessor

def test_code_and_patch_extraction(tmp_path):
    """Verifies format execution parsing for python components and structural diff tables."""
    preprocessor = UniversalPreprocessor(max_words=20)

    # 1. Script Extraction Check
    py_file = tmp_path / "telemetry.py"
    py_file.write_text(
        "class TelemetryTower:\n"
        "    def __init__(self):\n"
        "        self.active = True\n"
        "\n"
        "def audit_logs():\n"
        "    return Clear\n"
    )
    py_chunks = preprocessor.chunk_document(str(py_file))
    assert len(py_chunks) >= 2
    assert "class TelemetryTower" in py_chunks[0]["content"]
    assert "audit_logs" in py_chunks[1]["content"]

    # 2. Patch Modification Check
    diff_file = tmp_path / "system.patch"
    diff_file.write_text(
        "diff --git a/src/main.py b/src/main.py\n"
        "--- a/src/main.py\n"
        "+++ b/src/main.py\n"
        "@@ -1,3 +1,4 @@\n"
        "-baseline_node = False\n"
        "+baseline_node = True\n"
    )
    diff_chunks = preprocessor.chunk_document(str(diff_file))
    assert len(diff_chunks) >= 1
    assert "diff --git" in diff_chunks[0]["content"]
    assert diff_chunks[0]["metadata"]["source"] == "system.patch"
