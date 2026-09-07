"""
===============================================================================
Module
===============================================================================

Filename:
Core_Kernel_Foundation.py

Purpose:
Provides the immutable foundational contract layer for the Mini Kernel
Framework. This module defines shared types, enumerations, protocol contracts,
exception models, and validated configuration objects used by all framework
components.

This module contains no runtime loading, external dependencies, business logic,
or execution behavior.

It establishes the stable "laws" of the framework.

Responsibilities:
- Define framework-wide type aliases.
- Define canonical enumerations.
- Define immutable metadata contracts.
- Define kernel interface protocols.
- Define canonical exception hierarchy.
- Define immutable framework configuration models.
- Provide dependency-stable contracts for all kernels.

Public Types:
- KernelId
- ComponentName
- SignalName
- Timestamp
- ConfidenceScore
- Probability

Public Classes:
- SignalType
- AssumptionLevel
- ExpertVote
- KernelMetadata
- ErrorContext
- KernelError
- ValidationError
- ConfigurationError
- InitializationError
- ProcessingError
- DependencyError
- GraphError
- GovernanceError
- SecurityError
- KernelComponent
- ObservationEngine
- DecisionEngine
- AttentionConfiguration
- TemporalConfiguration
- RelationshipConfiguration
- PropagationConfiguration
- ConsensusConfiguration
- FrameworkConfiguration

Dependencies:
- Python Standard Library
    - dataclasses
    - enum
    - typing

===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import (
    Any,
    Mapping,
    Protocol,
    TypeAlias,
    runtime_checkable,
)


# =============================================================================
# TYPE ALIASES
# =============================================================================

KernelId: TypeAlias = str
ComponentName: TypeAlias = str
SignalName: TypeAlias = str
Timestamp: TypeAlias = float
ConfidenceScore: TypeAlias = float
Probability: TypeAlias = float


# =============================================================================
# ENUMERATIONS
# =============================================================================


class SignalType(Enum):
    """
    Classification of observed signal state.
    """

    OBSERVED = auto()
    MISSING = auto()


class AssumptionLevel(Enum):
    """
    Risk classification for inferred assumptions.
    """

    NORMAL = auto()
    INVESTIGATE = auto()
    POTENTIAL_HAZARD = auto()


class ExpertVote(Enum):
    """
    Standardized decision voting outcomes.
    """

    SUPPORT = auto()
    OPPOSE = auto()
    NEUTRAL = auto()


# =============================================================================
# METADATA CONTRACTS
# =============================================================================


@dataclass(frozen=True, slots=True)
class KernelMetadata:
    """
    Immutable metadata describing a framework component.
    """

    name: str
    version: str
    description: str


# =============================================================================
# EXCEPTION MODEL
# =============================================================================


@dataclass(frozen=True, slots=True)
class ErrorContext:
    """
    Immutable diagnostic context attached to framework errors.
    """

    component: str
    operation: str
    details: Mapping[str, Any] | None = None


class KernelError(Exception):
    """
    Root exception for all framework errors.
    """

    def __init__(
        self,
        message: str,
        context: ErrorContext | None = None,
    ) -> None:

        super().__init__(message)

        self.message = message
        self.context = context

    def __str__(self) -> str:

        if self.context is None:
            return self.message

        return (
            f"{self.message} "
            f"[component={self.context.component}, "
            f"operation={self.context.operation}]"
        )


class ValidationError(KernelError):
    """Raised when validation fails."""


class ConfigurationError(KernelError):
    """Raised when configuration is invalid."""


class InitializationError(KernelError):
    """Raised when initialization fails."""


class ProcessingError(KernelError):
    """Raised during processing failures."""


class DependencyError(KernelError):
    """Raised when required dependencies are unavailable."""


class GraphError(KernelError):
    """Raised during graph operations."""


class GovernanceError(KernelError):
    """Raised when governance constraints fail."""


class SecurityError(KernelError):
    """Raised when security policies fail."""


# =============================================================================
# PROTOCOL CONTRACTS
# =============================================================================


@runtime_checkable
class KernelComponent(Protocol):
    """
    Base contract implemented by framework components.
    """

    @property
    def metadata(self) -> KernelMetadata:
        """
        Return immutable component metadata.
        """
        ...


@runtime_checkable
class ObservationEngine(Protocol):
    """
    Contract for observation-based engines.
    """

    def evaluate(
        self,
        value: Any,
    ) -> float:
        """
        Evaluate an observation.

        Returns:
            Normalized score.
        """
        ...


@runtime_checkable
class DecisionEngine(Protocol):
    """
    Contract for deterministic decision engines.
    """

    def decide(
        self,
        context: Mapping[str, Any],
    ) -> str:
        """
        Produce a decision identifier.
        """
        ...


# =============================================================================
# IMMUTABLE CONFIGURATION MODELS
# =============================================================================


@dataclass(frozen=True, slots=True)
class AttentionConfiguration:
    """
    Configuration for attention analysis.
    """

    missing_signal_score: float = 0.95


@dataclass(frozen=True, slots=True)
class TemporalConfiguration:
    """
    Configuration for temporal analysis.
    """

    history_limit: int = 100


@dataclass(frozen=True, slots=True)
class RelationshipConfiguration:
    """
    Configuration for relationship analysis.
    """

    window_size: int = 10


@dataclass(frozen=True, slots=True)
class PropagationConfiguration:
    """
    Configuration for forecasting propagation.
    """

    max_depth: int = 3
    probability_decay: float = 0.60


@dataclass(frozen=True, slots=True)
class ConsensusConfiguration:
    """
    Configuration for consensus evaluation.
    """

    engineer_threshold: float = 0.70
    adversary_threshold: float = 0.30
    operator_threshold: float = 0.50


@dataclass(frozen=True, slots=True)
class FrameworkConfiguration:
    """
    Root immutable framework configuration.
    """

    metadata: KernelMetadata = field(
        default_factory=lambda: KernelMetadata(
            name="Mini Kernel Framework",
            version="1.0.0",
            description=(
                "Production-grade modular cognitive kernel framework."
            ),
        )
    )

    attention: AttentionConfiguration = field(
        default_factory=AttentionConfiguration
    )

    temporal: TemporalConfiguration = field(
        default_factory=TemporalConfiguration
    )

    relationship: RelationshipConfiguration = field(
        default_factory=RelationshipConfiguration
    )

    propagation: PropagationConfiguration = field(
        default_factory=PropagationConfiguration
    )

    consensus: ConsensusConfiguration = field(
        default_factory=ConsensusConfiguration
    )