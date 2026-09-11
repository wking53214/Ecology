"""
===============================================================================
Module
===============================================================================

Filename:
Attention_Mini_Perception_Kernel.py

Purpose:
Implements the framework's perceptual attention model. The Attention Kernel
evaluates the significance of incoming signals and produces a normalized
attention score that downstream reasoning kernels use for prioritization. The
implementation is deterministic, configuration-driven, dependency-injected, and
fully independent of domain-specific business logic.

Responsibilities:
- Score incoming observations.
- Detect missing observations.
- Produce normalized attention values.
- Validate scoring inputs.
- Provide a stable perception interface for higher-level kernels.

Public Classes:
- AttentionEngine

Public Interfaces:
- AttentionEngine.evaluate()
- AttentionEngine.score()

Dependencies:
- Python Standard Library
    - dataclasses

- Local
    - Types_Mini_Core_Kernel.py
    - Signal_Mini_Data_Kernel.py
    - Configuration_Mini_Core_Kernel.py
    - Exceptions_Mini_Core_Kernel.py

===============================================================================
Python Source
===============================================================================

"""
"""
Attention_Mini_Perception_Kernel.py

Deterministic attention scoring engine.

The Attention Kernel evaluates the perceptual importance of a signal.
Missing observations receive configurable attention while observed
signals receive a baseline score.
"""

from __future__ import annotations

from dataclasses import dataclass

from Configuration_Mini_Core_Kernel import AttentionConfiguration
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
class AttentionEngine(KernelComponent, ObservationEngine):
    """
    Production implementation of the Mini Perception Kernel.
    """

    configuration: AttentionConfiguration

    @property
    def metadata(self) -> KernelMetadata:
        return KernelMetadata(
            name="Attention Mini Perception Kernel",
            version="1.0.0",
            description=(
                "Computes normalized attention scores for runtime signals."
            ),
        )

    def evaluate(self, value: Signal) -> float:
        """
        Evaluate a Signal object and return its normalized attention score.
        """
        if not isinstance(value, Signal):
            raise ValidationError(
                "AttentionEngine.evaluate() requires a Signal instance."
            )

        return self.score(value)

    def score(self, signal: Signal) -> ConfidenceScore:
        """
        Compute a normalized attention score.

        Rules
        -----
        • Missing signals receive the configured attention score.
        • Observed signals receive zero attention.
        """

        if signal.signal_type is SignalType.MISSING:
            return self.configuration.missing_signal_score

        return 0.0