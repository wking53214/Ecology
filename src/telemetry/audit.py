import json
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class AuditLogger:
    """Logs structured telemetry data for pipeline performance analysis."""
    def __init__(self, log_path="telemetry/audit.log"):
        self.log_path = log_path
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def log_event(self, event_type: str, data: dict):
        """Records a timestamped telemetry event to the audit log."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event_type,
            "payload": data
        }
        try:
            with open(self.log_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.error(f"Telemetry write failure: {e}")
