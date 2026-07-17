import pytest
import os
import json
from plant import ContentPolishPipeline

async def mock_gateway(prompt: str):
    return "Valid response."

@pytest.mark.asyncio
async def test_audit_log_creation():
    audit_file = "execution_audit.jsonl"
    if os.path.exists(audit_file):
        os.remove(audit_file)
        
    pipeline = ContentPolishPipeline(execution_gateway=mock_gateway)
    await pipeline.execute("This is a valid test prompt.")
    
    assert os.path.exists(audit_file), "Audit log file not created."
    with open(audit_file, "r") as f:
        log_entry = json.loads(f.readline())
        assert log_entry["status"] == "SUCCESS"
