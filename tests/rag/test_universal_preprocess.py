import os
import json
import csv
import pytest
from src.rag.preprocess import UniversalPreprocessor

def test_universal_factory_extraction(tmp_path):
    """Verifies parsing across text, tabular, and structural JSON document layouts."""
    preprocessor = UniversalPreprocessor(max_words=50)

    # 1. Plain Text Ingestion Verification
    txt_file = tmp_path / "log.txt"
    txt_file.write_text("Telemetry subsystem alpha online framework monitoring baseline execution parameter configurations.")
    txt_chunks = preprocessor.chunk_document(str(txt_file))
    assert len(txt_chunks) == 1
    assert "Telemetry subsystem" in txt_chunks[0]["content"]
    assert txt_chunks[0]["metadata"]["section"] == "Body"

    # 2. JSON Structure Processing Verification
    json_data = {"engine_id": "DIT_V2", "metrics": {"latency_ms": 12.4, "status": "nominal"}}
    json_file = tmp_path / "config.json"
    with open(json_file, "w") as f:
        json.dump(json_data, f)
    json_chunks = preprocessor.chunk_document(str(json_file))
    assert len(json_chunks) == 2
    assert "engine_id" in json_chunks[0]["content"] or "engine_id" in json_chunks[1]["content"]

    # 3. CSV Tabular Record Parsing Verification
    csv_file = tmp_path / "fleet.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["vehicle", "year", "trim"])
        writer.writerow(["Tacoma", "2021", "SR"])
        writer.writerow(["RAV4", "2022", "Ltd"])
    csv_chunks = preprocessor.chunk_document(str(csv_file))
    assert len(csv_chunks) == 2
    assert "vehicle: Tacoma" in csv_chunks[0]["content"]
    assert "vehicle: RAV4" in csv_chunks[1]["content"]
    assert csv_chunks[1]["metadata"]["row_index"] == 1
