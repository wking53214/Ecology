import json

from plant import AuditLogger


def test_audit_log_event_writes_valid_json_line(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    AuditLogger.log_event({"prompt": "test", "status": "SUCCESS"})

    with open("execution_audit.jsonl") as f:
        line = f.readline()
    entry = json.loads(line)

    assert entry == {"prompt": "test", "status": "SUCCESS"}


def test_audit_log_event_appends_rather_than_overwrites(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    AuditLogger.log_event({"prompt": "first", "status": "SUCCESS"})
    AuditLogger.log_event({"prompt": "second", "status": "REJECTED"})

    with open("execution_audit.jsonl") as f:
        lines = f.readlines()

    assert len(lines) == 2
    assert json.loads(lines[1])["prompt"] == "second"
