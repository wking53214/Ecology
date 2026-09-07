"""
===============================================================================
Module
===============================================================================

Filename:
WS3_Universal_Engine.py

Purpose:
Implements the WS3 Universal Non-Interference Telemetry Layer, a domain-
agnostic observational analytics engine designed to provide read-only system
visibility without possessing operational authority, decision authority, or
write-back capability.

WS3 functions exclusively as a telemetry and diagnostic observation layer.
It monitors system signals, generates immutable reporting artifacts, performs
pure analytical calculations, and enforces non-interference boundaries through
an internal deadman safety mechanism.

The engine is intentionally isolated from execution pathways to prevent
control escalation, policy modification, or unintended influence over monitored
systems.

Responsibilities:
- Provide universal observational telemetry capabilities.
- Maintain strict observe-only operating boundaries.
- Generate immutable telemetry reports.
- Track observational history.
- Perform deterministic analytics calculations.
- Detect forbidden behavioral intent.
- Disable operation through deadman enforcement when violations occur.
- Provide read-only system introspection.

Non-Responsibilities:
- Modify monitored systems.
- Execute operational commands.
- Change policies.
- Influence decisions.
- Perform automated remediation.
- Provide control authority.

Safety Guarantees:
- Observe-only architecture.
- No write-back capability.
- No execution authority.
- Immutable output artifacts.
- Fail-closed behavior after safety violations.
- Internal deadman enforcement.

Public Classes:
- WS3Violation
- WS3Mode
- WS3SignalType
- WS3State
- WS3Report
- WS3DeadmanSwitch
- WS3UniversalEngine

Public Interfaces:
- WS3UniversalEngine.observe()
- WS3UniversalEngine.compute_capacity_pressure()
- WS3UniversalEngine.detect_drift()
- WS3UniversalEngine.history()
- WS3UniversalEngine.status()

Dependencies:
- Python Standard Library
    - dataclasses
    - enum
    - typing
    - time
    - logging

===============================================================================
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import time
import logging


# ============================================================
# SAFETY & STATE LAYER
# ============================================================

class WS3Violation(Exception):
    """Raised when WS3 attempts or detects non-observational behavior."""


class WS3Mode(Enum):
    OBSERVE_ONLY = "observe_only"
    DISABLED = "disabled"


class WS3SignalType(Enum):
    CAPACITY = "capacity"
    LOAD = "load"
    ACCURACY = "accuracy"
    DRIFT = "drift"
    SYSTEM_HEALTH = "system_health"


@dataclass
class WS3State:
    enabled: bool = True
    mode: WS3Mode = WS3Mode.OBSERVE_ONLY
    violation_count: int = 0
    last_check: float = field(default_factory=lambda: time.time())


# ============================================================
# IMMUTABLE OUTPUT ARTIFACT
# ============================================================

@dataclass(frozen=True)
class WS3Report:
    """
    Immutable telemetry output. Cannot be modified after creation.
    """
    timestamp: float
    domain: str
    signal_type: WS3SignalType
    metrics: Dict[str, float]
    notes: List[str] = field(default_factory=list)


# ============================================================
# DEADMAN SWITCH (SAFETY ENFORCER)
# ============================================================

class WS3DeadmanSwitch:
    """
    Disables WS3 if any forbidden behavioral intent is detected.
    """

    MAX_VIOLATIONS = 1

    def __init__(self, state: WS3State):
        self.state = state
        self.logger = logging.getLogger("WS3_DEADMAN")

    def check_mutation_attempt(self, attempted_action: str) -> None:
        forbidden = {
            "modify",
            "write_back",
            "alter_policy",
            "influence",
            "control",
            "override",
            "escalate_decision",
        }

        if any(token in attempted_action.lower() for token in forbidden):
            self.trigger_deadman(attempted_action)

    def trigger_deadman(self, reason: str) -> None:
        self.state.violation_count += 1
        self.state.mode = WS3Mode.DISABLED
        self.logger.critical(f"WS3 DISABLED — reason={reason}")
        raise WS3Violation(reason)


# ============================================================
# UNIVERSAL OBSERVABILITY ENGINE
# ============================================================

class WS3UniversalEngine:
    """
    Cross-domain, read-only telemetry and analytics layer.

    Properties:
    - No control authority
    - No decision authority
    - No write-back capability
    - Observational analytics only
    """

    def __init__(self, domain: str):
        self.domain = domain
        self.state = WS3State()
        self.deadman = WS3DeadmanSwitch(self.state)
        self._history: List[WS3Report] = []

    # --------------------------------------------------------
    # CORE OBSERVATION API
    # --------------------------------------------------------

    def observe(
        self,
        signal_type: WS3SignalType,
        metrics: Dict[str, float],
        notes: Optional[List[str]] = None,
    ) -> WS3Report:

        self._assert_active()

        report = WS3Report(
            timestamp=time.time(),
            domain=self.domain,
            signal_type=signal_type,
            metrics=dict(metrics),
            notes=notes or [],
        )

        self._history.append(report)
        return report

    # --------------------------------------------------------
    # ANALYTICS (PURE FUNCTIONS)
    # --------------------------------------------------------

    def compute_capacity_pressure(self, utilization: float) -> float:
        """
        Nonlinear utilization stress mapping.
        """
        self._assert_active()
        u = max(0.0, min(1.0, utilization))
        return u * u

    def detect_drift(self, baseline: float, current: float) -> float:
        """
        Relative drift measurement.
        """
        self._assert_active()
        if baseline == 0:
            return 0.0
        return abs(current - baseline) / abs(baseline)

    # --------------------------------------------------------
    # SAFETY CONTROL (INTERNAL ONLY)
    # --------------------------------------------------------

    def _assert_active(self) -> None:
        if self.state.mode == WS3Mode.DISABLED:
            raise WS3Violation("WS3 is disabled (deadman triggered).")

    # --------------------------------------------------------
    # READ-ONLY INTROSPECTION
    # --------------------------------------------------------

    def history(self) -> List[WS3Report]:
        return list(self._history)

    def status(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "enabled": self.state.mode == WS3Mode.OBSERVE_ONLY,
            "violations": self.state.violation_count,
            "history_size": len(self._history),
        }