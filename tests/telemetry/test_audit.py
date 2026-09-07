import pytest
import os
import json
from src.telemetry.audit import AuditLogger

def test_audit_log_creation(tmp_path):
    """Verifies that audit logs persist structured JSON events correctly."""
    log_file = tmp_path / "audit.log"
    auditor = AuditLogger(log_path=str(log_file))
    
    auditor.log_event("test_event", {"metric": 100})
    
    assert log_file.exists()
    with open(log_file, "r") as f:
        log_entry = json.loads(f.readline())
        assert log_entry["event"] == "test_event"
        assert log_entry["payload"]["metric"] == 100
