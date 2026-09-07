===============================================================================
Module
===============================================================================

Filename:
Arnold_Mini_Cognitive_Kernel.py

Purpose:
Implements the primary cognitive orchestration kernel that coordinates signal
processing across perception, observation, governance, memory, relationship,
forecasting, and decision subsystems. Arnold acts as the central reasoning
coordinator while maintaining strict separation between individual kernel
responsibilities.

Responsibilities:
- Coordinate multiple specialized kernels.
- Process incoming signals through the cognitive pipeline.
- Aggregate analytical outputs.
- Produce structured reasoning results.
- Maintain dependency-injected architecture.

Public Classes:
- ArnoldEngine
- CognitiveResult

Public Interfaces:
- ArnoldEngine.process()

Dependencies:
- Python Standard Library
    - dataclasses
    - typing

- Local
    - Signal_Mini_Data_Kernel.py
    - Attention_Mini_Perception_Kernel.py
    - PresenceAbsence_Mini_Observation_Kernel.py
    - Assumption_Mini_Governance_Kernel.py
    - Temporal_Mini_Memory_Kernel.py
    - Relationship_Mini_Graph_Kernel.py
    - Propagation_Mini_Forecasting_Kernel.py
    - Consensus_Mini_Decision_Kernel.py
    - Types_Mini_Core_Kernel.py
    - Exceptions_Mini_Core_Kernel.py

===============================================================================
Python Source
===============================================================================

"""
Arnold_Mini_Cognitive_Kernel.py

Central cognitive orchestration kernel.

Coordinates specialized mini kernels into a unified reasoning pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from Assumption_Mini_Governance_Kernel import AssumptionEngine
from Attention_Mini_Perception_Kernel import AttentionEngine
from Consensus_Mini_Decision_Kernel import ConsensusEngine
from Exceptions_Mini_Core_Kernel import ValidationError
from PresenceAbsence_Mini_Observation_Kernel import PresenceAbsenceEngine
from Propagation_Mini_Forecasting_Kernel import PropagationEngine
from Relationship_Mini_Graph_Kernel import RelationshipEngine
from Signal_Mini_Data_Kernel import Signal
from Temporal_Mini_Memory_Kernel import TemporalEngine
from Types_Mini_Core_Kernel import (
    KernelComponent,
    KernelMetadata,
)


@dataclass(frozen=True, slots=True)
class CognitiveResult:
    """
    Immutable cognitive pipeline result.
    """

    signal: str
    attention: float
    absence: float
    assumption: str
    momentum: float
    forecast: Any
    decision: str


@dataclass(slots=True)
class ArnoldEngine(KernelComponent):
    """
    Primary cognitive orchestration engine.
    """

    attention: AttentionEngine
    absence: PresenceAbsenceEngine
    assumption: AssumptionEngine
    temporal: TemporalEngine
    relationship: RelationshipEngine
    propagation: PropagationEngine
    consensus: ConsensusEngine

    @property
    def metadata(self) -> KernelMetadata:
        return KernelMetadata(
            name="Arnold Mini Cognitive Kernel",
            version="1.0.0",
            description=(
                "Coordinates modular reasoning kernels into a unified "
                "cognitive processing pipeline."
            ),
        )

    def process(
        self,
        signal: Signal,
    ) -> CognitiveResult:
        """
        Execute the complete cognitive pipeline.
        """

        if not isinstance(signal, Signal):
            raise ValidationError(
                "ArnoldEngine.process() requires a Signal instance."
            )

        self.temporal.update(signal)

        self.relationship.observe(signal)

        attention_score = self.attention.score(signal)

        absence_score = self.absence.evaluate(signal)

        assumption = self.assumption.classify(signal)

        momentum = self.temporal.momentum(
            signal.name
        )

        forecasts = self.propagation.forecast_paths(
            signal.name,
            self.relationship,
        )

        risk = (
            forecasts[0][1]
            if forecasts
            else 0.0
        )

        decision = self.consensus.decide(
            attention_score,
            risk,
        )

        return CognitiveResult(
            signal=signal.name,
            attention=round(
                attention_score,
                4,
            ),
            absence=round(
                absence_score,
                4,
            ),
            assumption=assumption.label,
            momentum=round(
                momentum,
                4,
            ),
            forecast=(
                forecasts[0]
                if forecasts
                else None
            ),
            decision=decision.decision,
        )