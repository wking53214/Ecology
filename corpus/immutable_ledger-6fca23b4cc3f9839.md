"""
Immutable Audit Ledger
======================

Append-only audit trail with SHA256 cryptographic chaining.
Detects tampering, enables forensic replay.
"""

logger = logging.getLogger("OBSERVE_AUDIT")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        "[OBSERVE_AUDIT] %(asctime)s %(levelname)s %(message)s"
    ))
    logger.addHandler(handler)

# ============================================================
# AUDIT ENTRY
# ============================================================

@dataclass
class ClinicalAuditEntry:
    """Single immutable entry in clinical audit trail."""
    audit_id: str
    timestamp: datetime
    patient_id: str
    vitals_snapshot: Dict
    selected_engines: List[str]
    engine_outputs: List[Dict]
    fused_verdict: Dict
    escalation_required: bool
    provisional_verdict: Optional[Dict] = None
    job_id: Optional[str] = None
    final_verdict: Optional[Dict] = None
    reconciliation_time: Optional[float] = None
    previous_hash: str = ""
    immutable_hash: str = ""

# ============================================================
# IMMUTABLE AUDIT LEDGER
# ============================================================

class ImmutableAuditLedger:
    """Append-only audit trail with SHA256 chaining."""

def __init__(self):
        self.entries: List[ClinicalAuditEntry] = []
        self.chain_head = hashlib.sha256(b"OBSERVE_GENESIS").hexdigest()
        logger.info("ImmutableAuditLedger initialized")

def append_clinical_assessment(
        self,
        patient_id: str,
        vitals_snapshot: Dict,
        selected_engines: List[str],
        engine_outputs: List[Dict],
        fused_verdict: Dict,
        escalation_required: bool,
        provisional_verdict: Optional[Dict] = None,
        job_id: Optional[str] = None,
    ) -> ClinicalAuditEntry:
        """
        Append clinical assessment to immutable ledger.
        
        Entry includes:
        - Provisional verdict (if async job queued)
        - Final verdict (when job completes)
        - Reconciliation status
        """

entry = ClinicalAuditEntry(
            audit_id=hashlib.sha256(
                f"{len(self.entries)}:{datetime.now(timezone.utc).isoformat()}:{patient_id}".encode()
            ).hexdigest()[:16],
            timestamp=datetime.now(timezone.utc),
            patient_id=patient_id,
            vitals_snapshot=vitals_snapshot,
            selected_engines=selected_engines,
            engine_outputs=engine_outputs,
            fused_verdict=fused_verdict,
            escalation_required=escalation_required,
            provisional_verdict=provisional_verdict,
            job_id=job_id,
            previous_hash=self.chain_head,
        )

# Compute immutable hash (SHA256 chain)
        entry_dict = {
            "audit_id": entry.audit_id,
            "timestamp": entry.timestamp.isoformat(),
            "patient_id": entry.patient_id,
            "fused_verdict": entry.fused_verdict,
            "escalation_required": entry.escalation_required,
        }

self.entries.append(entry)
        logger.info(
            f"Clinical assessment logged: patient={patient_id}, "
            f"hash={entry.immutable_hash[:16]}, "
            f"audit_id={entry.audit_id}"
        )

def reconcile_with_final_verdict(
        self,
        audit_id: str,
        final_verdict: Dict,
        reconciliation_time: float,
    ) -> bool:
        """
        Update audit entry with final verdict from async job.
        
        This modifies the entry's final_verdict field but does NOT
        change the immutable_hash (which was sealed when entry created).
        The hash includes only the provisional assessment.
        """

for entry in self.entries:
            if entry.audit_id == audit_id:
                entry.final_verdict = final_verdict
                entry.reconciliation_time = reconciliation_time
                logger.info(
                    f"Audit entry reconciled: {audit_id}, "
                    f"reconciliation_time={reconciliation_time:.2f}s"
                )
                return True

logger.warning(f"Audit entry not found: {audit_id}")
        return False

def verify_chain_integrity(self) -> bool:
        """
        Validate entire audit chain (detects tampering).
        
        Returns True if all hashes verify correctly.
        """

expected_hash = hashlib.sha256(b"OBSERVE_GENESIS").hexdigest()

for entry in self.entries:
            entry_dict = {
                "audit_id": entry.audit_id,
                "timestamp": entry.timestamp.isoformat(),
                "patient_id": entry.patient_id,
                "fused_verdict": entry.fused_verdict,
                "escalation_required": entry.escalation_required,
            }

logger.info(f"Chain integrity verified ({len(self.entries)} entries)")
        return True

def export_audit_trail(self) -> List[Dict]:
        """Export audit trail for compliance/export."""
        return [
            {
                "audit_id": e.audit_id,
                "timestamp": e.timestamp.isoformat(),
                "patient_id": e.patient_id,
                "escalation_required": e.escalation_required,
                "fused_verdict": e.fused_verdict,
                "provisional_verdict": e.provisional_verdict,
                "final_verdict": e.final_verdict,
                "reconciliation_time": e.reconciliation_time,
                "immutable_hash": e.immutable_hash,
            }
            for e in self.entries
        ]

def export_as_json(self, filepath: str) -> None:
        """Export audit trail to JSON file."""
        trail = self.export_audit_trail()
        with open(filepath, "w") as f:
            json.dump(trail, f, indent=2, default=str)
        logger.info(f"Audit trail exported to {filepath}")

def export_as_csv(self, filepath: str) -> None:
        """Export audit trail to CSV (HIPAA-safe format)."""
        import csv

with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "audit_id",
                    "timestamp",
                    "patient_id",
                    "escalation_required",
                    "risk_score",
                    "regime",
                    "immutable_hash",
                ],
            )
            writer.writeheader()

for entry in trail:
                writer.writerow({
                    "audit_id": entry["audit_id"],
                    "timestamp": entry["timestamp"],
                    "patient_id": entry["patient_id"],
                    "escalation_required": entry["escalation_required"],
                    "risk_score": entry["fused_verdict"].get("risk_score", ""),
                    "regime": entry["fused_verdict"].get("regime", ""),
                    "immutable_hash": entry["immutable_hash"],
                })

logger.info(f"Audit trail exported to CSV: {filepath}")

def query_patient(self, patient_id: str) -> List[ClinicalAuditEntry]:
        """Retrieve all audit entries for a patient."""
        return [e for e in self.entries if e.patient_id == patient_id]

def query_by_audit_id(self, audit_id: str) -> Optional[ClinicalAuditEntry]:
        """Retrieve single audit entry by ID."""
        for e in self.entries:
            if e.audit_id == audit_id:
                return e
        return None

def get_chain_stats(self) -> Dict:
        """Get statistics about audit chain."""
        return {
            "total_entries": len(self.entries),
            "unique_patients": len(set(e.patient_id for e in self.entries)),
            "escalations": sum(1 for e in self.entries if e.escalation_required),
            "reconciled_entries": sum(1 for e in self.entries if e.final_verdict is not None),
            "chain_head_hash": self.chain_head[:16],
            "chain_integrity_valid": self.verify_chain_integrity(),
        }
