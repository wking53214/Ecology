===============================================================================
Module
===============================================================================

Filename:
Consensus_Mini_Decision_Kernel.py

Purpose:
Implements the decision consensus subsystem responsible for combining multiple
independent evaluation perspectives into a deterministic operational decision.
The Consensus Kernel models engineering risk, adversarial risk, and operator
attention as separate voting inputs and converts those signals into a unified
decision state.

Responsibilities:
- Evaluate multi-perspective votes.
- Apply configurable decision thresholds.
- Produce deterministic outcomes.
- Separate risk evaluation from execution.
- Provide explainable decision results.

Public Classes:
- ConsensusEngine
- ConsensusResult

Public Interfaces:
- ConsensusEngine.decide()
- ConsensusEngine.engineer()
- ConsensusEngine.adversary()
- ConsensusEngine.operator()

Dependencies:
- Python Standard Library
    - dataclasses

- Local
    - Configuration_Mini_Core_Kernel.py
    - Types_Mini_Core_Kernel.py
    - Exceptions_Mini_Core_Kernel.py

===============================================================================
Python Source
===============================================================================

"""
Consensus_Mini_Decision_Kernel.py

Deterministic consensus decision engine.

Combines independent decision perspectives into an explainable
operational outcome.
"""

from __future__ import annotations

from dataclasses import dataclass

from Configuration_Mini_Core_Kernel import ConsensusConfiguration
from Exceptions_Mini_Core_Kernel import ValidationError
from Types_Mini_Core_Kernel import (
    ExpertVote,
    KernelComponent,
    KernelMetadata,
)


@dataclass(frozen=True, slots=True)
class ConsensusResult:
    """
    Immutable decision result.

    Attributes:
        decision:
            Final operational decision.

        votes:
            Individual expert votes.

        score:
            Net support score.
    """

    decision: str
    votes: tuple[ExpertVote, ...]
    score: int


@dataclass(slots=True)
class ConsensusEngine(KernelComponent):
    """
    Multi-perspective deterministic decision engine.
    """

    configuration: ConsensusConfiguration

    @property
    def metadata(self) -> KernelMetadata:
        return KernelMetadata(
            name="Consensus Mini Decision Kernel",
            version="1.0.0",
            description=(
                "Combines expert perspectives into deterministic decisions."
            ),
        )

    def engineer(
        self,
        risk: float,
    ) -> ExpertVote:
        """
        Engineering perspective.

        High risk produces opposition to continued execution.
        """
        self._validate_score(risk)

        if risk > self.configuration.engineer_threshold:
            return ExpertVote.OPPOSE

        return ExpertVote.SUPPORT

    def adversary(
        self,
        risk: float,
    ) -> ExpertVote:
        """
        Adversarial perspective.

        Low risk produces opposition to escalation.
        """
        self._validate_score(risk)

        if risk < self.configuration.adversary_threshold:
            return ExpertVote.OPPOSE

        return ExpertVote.SUPPORT

    def operator(
        self,
        attention: float,
    ) -> ExpertVote:
        """
        Operator attention perspective.
        """
        self._validate_score(attention)

        if attention > self.configuration.operator_threshold:
            return ExpertVote.SUPPORT

        return ExpertVote.NEUTRAL

    def decide(
        self,
        attention: float,
        risk: float,
    ) -> ConsensusResult:
        """
        Produce final consensus decision.
        """

        votes = (
            self.engineer(risk),
            self.adversary(risk),
            self.operator(attention),
        )

        score = (
            votes.count(ExpertVote.SUPPORT)
            -
            votes.count(ExpertVote.OPPOSE)
        )

        if score >= 1:
            decision = "ESCALATE"

        elif score == 0:
            decision = "INVESTIGATE"

        else:
            decision = "IGNORE"

        return ConsensusResult(
            decision=decision,
            votes=votes,
            score=score,
        )

    @staticmethod
    def _validate_score(
        value: float,
    ) -> None:
        """
        Validate normalized input scores.
        """

        if not 0.0 <= value <= 1.0:
            raise ValidationError(
                "Consensus values must be between 0.0 and 1.0."
            )