===============================================================================
Module
===============================================================================

Filename:
Configuration_Mini_Core_Kernel.py

Purpose:
Provides immutable, validated configuration objects for the framework. This
module centralizes runtime settings, threshold values, feature flags, and
kernel metadata while enforcing defensive validation. Configuration objects are
designed for dependency injection and remain immutable after construction,
ensuring deterministic behavior across all consuming kernels.

Responsibilities:
- Define immutable framework configuration.
- Validate configuration values during construction.
- Provide strongly typed configuration sections.
- Support dependency injection across kernels.
- Expose safe default production settings.

Public Classes:
- AttentionConfiguration
- TemporalConfiguration
- RelationshipConfiguration
- PropagationConfiguration
- ConsensusConfiguration
- FrameworkConfiguration

Dependencies:
- Python Standard Library
    - dataclasses
    - typing

- Local
    - Types_Mini_Core_Kernel.py
    - Exceptions_Mini_Core_Kernel.py

===============================================================================
Python Source
===============================================================================

"""
Configuration_Mini_Core_Kernel.py

Immutable configuration objects for the Mini Kernel Framework.

Configuration is validated during construction and is intended to be
shared safely across all framework components.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from Types_Mini_Core_Kernel import KernelMetadata
from Exceptions_Mini_Core_Kernel import ConfigurationError


@dataclass(frozen=True, slots=True)
class AttentionConfiguration:
    """Configuration for the Attention Kernel."""

    missing_signal_score: float = 0.95

    def __post_init__(self) -> None:
        if not 0.0 <= self.missing_signal_score <= 1.0:
            raise ConfigurationError(
                "missing_signal_score must be between 0.0 and 1.0"
            )


@dataclass(frozen=True, slots=True)
class TemporalConfiguration:
    """Configuration for the Temporal Kernel."""

    history_limit: int = 100

    def __post_init__(self) -> None:
        if self.history_limit < 2:
            raise ConfigurationError(
                "history_limit must be at least 2."
            )


@dataclass(frozen=True, slots=True)
class RelationshipConfiguration:
    """Configuration for the Relationship Kernel."""

    window_size: int = 10

    def __post_init__(self) -> None:
        if self.window_size < 2:
            raise ConfigurationError(
                "window_size must be at least 2."
            )


@dataclass(frozen=True, slots=True)
class PropagationConfiguration:
    """Configuration for the Forecasting Kernel."""

    max_depth: int = 3
    probability_decay: float = 0.60

    def __post_init__(self) -> None:
        if self.max_depth < 1:
            raise ConfigurationError(
                "max_depth must be greater than zero."
            )

        if not 0.0 < self.probability_decay <= 1.0:
            raise ConfigurationError(
                "probability_decay must be within (0.0, 1.0]."
            )


@dataclass(frozen=True, slots=True)
class ConsensusConfiguration:
    """Configuration for the Decision Kernel."""

    engineer_threshold: float = 0.70
    adversary_threshold: float = 0.30
    operator_threshold: float = 0.50

    def __post_init__(self) -> None:
        values = (
            self.engineer_threshold,
            self.adversary_threshold,
            self.operator_threshold,
        )

        if any(value < 0.0 or value > 1.0 for value in values):
            raise ConfigurationError(
                "Consensus thresholds must be between 0.0 and 1.0."
            )


@dataclass(frozen=True, slots=True)
class FrameworkConfiguration:
    """
    Root immutable configuration shared by the framework.
    """

    metadata: KernelMetadata = field(
        default_factory=lambda: KernelMetadata(
            name="Mini Kernel Framework",
            version="1.0.0",
            description="Production-grade modular cognitive kernel framework.",
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