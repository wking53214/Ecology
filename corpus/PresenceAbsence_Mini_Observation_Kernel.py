"""
===============================================================================
Module
===============================================================================

Filename:
PresenceAbsence_Mini_Observation_Kernel.py

Purpose:
Implements the framework's observation-state evaluation kernel. This module
determines whether a signal represents an observed or absent condition and
produces a normalized presence/absence score. The kernel is deterministic,
configuration-independent, and designed for seamless integration with higher-
level reasoning components.

Responsibilities:
- Evaluate observation state.
- Produce normalized presence/absence scores.
- Validate input signals.
- Provide a stable observation interface.
- Support downstream reasoning kernels.

Public Classes:
- PresenceAbsenceEngine

Public Interfaces:
- PresenceAbsenceEngine.evaluate()

Dependencies:
- Python Standard Library
    - dataclasses

- Local
    - Signal_Mini_Data_Kernel.py
    - Types_Mini_Core_Kernel.py
    - Exceptions_Mini_Core_Kernel.py

===============================================================================
Python Source
===============================================================================

"""
"""
PresenceAbsence_Mini_Observation_Kernel.py

Deterministic observation-state evaluation kernel.

This kernel evaluates whether an incoming signal represents an observed
or missing condition and returns a normalized score indicating the degree
of absence.
"""

from __future__ import annotations

from dataclasses import dataclass

from Exceptions_Mini_Core_Kernel import ValidationError
from Signal_Mini_Data_Kernel import Signal
from Types_Mini_Core_Kernel import (
    ConfidenceScore,
    KernelComponent,
    KernelMetadata,
    ObservationEngine,
    SignalType,
)


@dataclass(slots=True)
class PresenceAbsenceEngine(KernelComponent, ObservationEngine):
    """
    Production implementation of the Mini Observation Kernel.
    """

    @property
    def metadata(self) -> KernelMetadata:
        return KernelMetadata(
            name="Presence/Absence Mini Observation Kernel",
            version="1.0.0",
            description=(
                "Evaluates whether runtime signals represent observed or "
                "missing conditions."
            ),
        )

    def evaluate(self, value: Signal) -> ConfidenceScore:
        """
        Evaluate a Signal object and return its normalized absence score.

        Returns:
            1.0 if the signal is classified as missing.
            0.0 if the signal is classified as observed.
        """
        if not isinstance(value, Signal):
            raise ValidationError(
                "PresenceAbsenceEngine.evaluate() requires a Signal instance."
            )

        return 1.0 if value.signal_type is SignalType.MISSING else 0.0