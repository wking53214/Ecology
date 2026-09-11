"""
===============================================================================
Module
===============================================================================

Filename:
Signal_Mini_Data_Kernel.py

Purpose:
Defines the immutable signal data model used throughout the framework. Signals
represent the canonical unit of observation exchanged between kernels and
encapsulate validated metadata, values, timestamps, and state classifications.
This module establishes the framework's foundational data contract for runtime
processing.

Responsibilities:
- Define the immutable Signal data model.
- Validate signal construction.
- Provide deterministic serialization support.
- Expose convenience properties for downstream kernels.
- Maintain a stable data contract across the framework.

Public Classes:
- Signal

Public Interfaces:
- Signal.to_dict()
- Signal.from_dict()

Dependencies:
- Python Standard Library
    - dataclasses
    - typing
    - time

- Local
    - Types_Mini_Core_Kernel.py
    - Exceptions_Mini_Core_Kernel.py

===============================================================================
Python Source
===============================================================================

"""
"""
Signal_Mini_Data_Kernel.py

Canonical signal model shared by every kernel.

Signals are immutable and validated during construction to ensure
consistent behavior throughout the framework.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from time import time
from typing import Any, Mapping

from Exceptions_Mini_Core_Kernel import ValidationError
from Types_Mini_Core_Kernel import SignalName, SignalType, Timestamp


@dataclass(frozen=True, slots=True)
class Signal:
    """
    Immutable representation of an observed signal.

    Attributes:
        name:
            Logical identifier for the signal.

        value:
            Numeric observation.

        timestamp:
            Unix timestamp representing when the signal occurred.

        signal_type:
            Classification of the observation.
    """

    name: SignalName
    value: float
    timestamp: Timestamp
    signal_type: SignalType = SignalType.OBSERVED

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValidationError(
                "Signal name cannot be empty."
            )

        if not isinstance(self.value, (int, float)):
            raise ValidationError(
                "Signal value must be numeric."
            )

        if self.timestamp <= 0:
            raise ValidationError(
                "Timestamp must be greater than zero."
            )

    @property
    def is_missing(self) -> bool:
        """
        Returns True if the signal represents an absent observation.
        """
        return self.signal_type is SignalType.MISSING

    @property
    def is_observed(self) -> bool:
        """
        Returns True if the signal represents an observed value.
        """
        return self.signal_type is SignalType.OBSERVED

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the signal into a dictionary.
        """
        data = asdict(self)
        data["signal_type"] = self.signal_type.name
        return data

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "Signal":
        """
        Construct a Signal from a serialized mapping.
        """
        return cls(
            name=str(data["name"]),
            value=float(data["value"]),
            timestamp=float(data["timestamp"]),
            signal_type=SignalType[str(data["signal_type"])],
        )

    @classmethod
    def now(
        cls,
        name: str,
        value: float,
        signal_type: SignalType = SignalType.OBSERVED,
    ) -> "Signal":
        """
        Convenience factory that timestamps the signal using the current
        Unix epoch time.
        """
        return cls(
            name=name,
            value=value,
            timestamp=time(),
            signal_type=signal_type,
        )