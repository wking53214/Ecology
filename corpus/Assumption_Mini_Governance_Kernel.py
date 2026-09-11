"""
===============================================================================
Module
===============================================================================

Filename:
Assumption_Mini_Governance_Kernel.py

Purpose:
Implements the framework's defensive assumption engine. This kernel transforms
incomplete, ambiguous, or high-risk observations into deterministic,
policy-driven assumptions that downstream reasoning kernels can evaluate. The
kernel follows a fail-safe philosophy by assigning the least-risky reasonable
interpretation when evidence is incomplete while remaining fully explainable
and configurable.

Responsibilities:
- Classify observations into assumption categories.
- Assign standardized assumption severity levels.
- Apply deterministic governance rules.
- Validate incoming signals.
- Produce immutable assumption objects for downstream kernels.

Public Classes:
- Assumption
- AssumptionEngine

Public Interfaces:
- AssumptionEngine.classify()

Dependencies:
- Python Standard Library
    - dataclasses
    - typing

- Local
    - Signal_Mini_Data_Kernel.py
    - Types_Mini_Core_Kernel.py
    - Exceptions_Mini_Core_Kernel.py

===============================================================================
Python Source
===============================================================================

"""
"""
Assumption_Mini_Governance_Kernel.py

Production implementation of the defensive assumption engine.

This kernel converts ambiguous observations into deterministic,
governance-aligned assumptions using a configurable rule set.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from Exceptions_Mini_Core_Kernel import ValidationError
from Signal_Mini_Data_Kernel import Signal
from Types_Mini_Core_Kernel import (
    AssumptionLevel,
    KernelComponent,
    KernelMetadata,
)


@dataclass(frozen=True, slots=True)
class Assumption:
    """
    Immutable assumption generated from a signal.
    """

    label: str
    level: AssumptionLevel

    def __post_init__(self) -> None:
        if not self.label.strip():
            raise ValidationError(
                "Assumption label cannot be empty."
            )


@dataclass(slots=True)
class AssumptionEngine(KernelComponent):
    """
    Deterministic governance assumption engine.
    """

    rules: Mapping[str, AssumptionLevel] = field(
        default_factory=lambda: {
            "unknown_liquid": AssumptionLevel.POTENTIAL_HAZARD,
            "unknown_login": AssumptionLevel.INVESTIGATE,
            "unexpected_process": AssumptionLevel.INVESTIGATE,
            "privilege_escalation": AssumptionLevel.POTENTIAL_HAZARD,
        }
    )

    labels: Mapping[str, str] = field(
        default_factory=lambda: {
            "unknown_liquid": "potential_fuel_spill",
            "unknown_login": "potential_account_compromise",
            "unexpected_process": "unexpected_runtime_behavior",
            "privilege_escalation": "potential_privilege_abuse",
        }
    )

    @property
    def metadata(self) -> KernelMetadata:
        return KernelMetadata(
            name="Assumption Mini Governance Kernel",
            version="1.0.0",
            description=(
                "Generates deterministic governance assumptions from "
                "runtime observations."
            ),
        )

    def classify(self, signal: Signal) -> Assumption:
        """
        Produce a governance assumption from an incoming signal.

        Unknown signals default to NORMAL to maintain deterministic
        behavior while avoiding speculative classification.
        """
        if not isinstance(signal, Signal):
            raise ValidationError(
                "AssumptionEngine.classify() requires a Signal instance."
            )

        level = self.rules.get(
            signal.name,
            AssumptionLevel.NORMAL,
        )

        label = self.labels.get(
            signal.name,
            "normal",
        )

        return Assumption(
            label=label,
            level=level,
        )