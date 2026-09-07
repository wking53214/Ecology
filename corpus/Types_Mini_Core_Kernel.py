===============================================================================
Module
===============================================================================

Filename:
Types_Mini_Core_Kernel.py

Purpose:
Defines the foundational immutable data types, enumerations, protocols, and
type aliases shared across every kernel within the framework. This module
contains no business logic and serves as the canonical contract layer,
ensuring strong typing, interface consistency, and dependency stability
throughout the architecture.

Responsibilities:
- Define framework-wide enumerations.
- Define immutable protocol contracts.
- Define common type aliases.
- Provide canonical identifiers for kernel interoperability.
- Establish stable interfaces used by higher-level kernels.

Public Classes:
- SignalType
- AssumptionLevel
- ExpertVote
- KernelMetadata
- KernelComponent
- DecisionEngine
- ObservationEngine

Dependencies:
- Python Standard Library
    - dataclasses
    - enum
    - typing

===============================================================================
Python Source
===============================================================================

"""
Types_Mini_Core_Kernel.py

Core framework types and interface definitions.

This module intentionally contains no implementation logic.
It provides immutable contracts shared by every kernel.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import (
    Any,
    Mapping,
    Protocol,
    runtime_checkable,
    TypeAlias,
)

# ---------------------------------------------------------------------------
# Type Aliases
# ---------------------------------------------------------------------------

KernelId: TypeAlias = str
ComponentName: TypeAlias = str
SignalName: TypeAlias = str
Timestamp: TypeAlias = float
ConfidenceScore: TypeAlias = float
Probability: TypeAlias = float

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class SignalType(Enum):
    """Classification of observed signal state."""

    OBSERVED = auto()
    MISSING = auto()


class AssumptionLevel(Enum):
    """Risk classification for inferred assumptions."""

    NORMAL = auto()
    INVESTIGATE = auto()
    POTENTIAL_HAZARD = auto()


class ExpertVote(Enum):
    """Standardized voting outcomes."""

    SUPPORT = auto()
    OPPOSE = auto()
    NEUTRAL = auto()


# ---------------------------------------------------------------------------
# Immutable Metadata
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class KernelMetadata:
    """
    Immutable metadata describing a framework kernel.
    """

    name: str
    version: str
    description: str


# ---------------------------------------------------------------------------
# Framework Protocols
# ---------------------------------------------------------------------------


@runtime_checkable
class KernelComponent(Protocol):
    """
    Base protocol implemented by all kernels.
    """

    @property
    def metadata(self) -> KernelMetadata:
        """Return immutable kernel metadata."""


@runtime_checkable
class ObservationEngine(Protocol):
    """
    Interface for observation-based engines.
    """

    def evaluate(self, value: Any) -> float:
        """
        Evaluate an observation.

        Returns:
            float: Normalized score.
        """


@runtime_checkable
class DecisionEngine(Protocol):
    """
    Interface for decision-making engines.
    """

    def decide(
        self,
        context: Mapping[str, Any],
    ) -> str:
        """
        Produce a deterministic decision.

        Args:
            context:
                Immutable decision context.

        Returns:
            Decision identifier.
        """