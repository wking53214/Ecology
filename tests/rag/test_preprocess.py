import os
import pytest
from src.rag.preprocess import MarkdownPreprocessor

def test_markdown_preprocessing_pipeline(tmp_path):
    """Verifies metadata splitting, front-matter clearance, and header parsing precision."""
    # Write a temporary mock file containing standardized markdown elements
    mock_file = tmp_path / "test_doc.md"
    mock_file.write_text(
        "---\n"
        "author: Starfleet\n"
        "classification: Restricted\n"
        "---\n"
        "# Architecture Overview\n"
        "Core telemetry routing layer initialized.\n"
        "## Subsystem Alpha\n"
        "Asynchronous data processing boundaries hardened.\n"
    )

    preprocessor = MarkdownPreprocessor(max_words=100)
    chunks = preprocessor.chunk_document(str(mock_file))

    # General extraction diagnostics
    assert len(chunks) == 2
    
    # Section 1 validation (H1 block mapping)
    assert chunks[0]["metadata"]["author"] == "Starfleet"
    assert chunks[0]["metadata"]["section"] == "Architecture Overview"
    assert "Core telemetry routing" in chunks[0]["content"]

    # Section 2 validation (H2 nested block parsing)
    assert chunks[1]["metadata"]["classification"] == "Restricted"
    assert chunks[1]["metadata"]["section"] == "Subsystem Alpha"
    assert "Asynchronous data processing" in chunks[1]["content"]
