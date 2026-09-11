"""
===============================================================================
Module
===============================================================================

Filename:
Temporal_Mini_Memory_Kernel.py

Purpose:
Implements the temporal memory subsystem responsible for maintaining signal
history and calculating directional change over time. This kernel provides a
lightweight historical context layer for higher-level reasoning systems by
tracking previous observations while maintaining bounded memory usage.

Responsibilities:
- Store historical signal values.
- Maintain bounded temporal memory.
- Calculate signal momentum.
- Provide deterministic historical analysis.
- Prevent uncontrolled memory growth.

Public Classes:
- TemporalEngine

Public Interfaces:
- TemporalEngine.update()
- TemporalEngine.momentum()
- TemporalEngine.history()

Dependencies:
- Python Standard Library
    - collections
    - dataclasses
    - typing

- Local
    - Configuration_Mini_Core_Kernel.py
    - Signal_Mini_Data_Kernel.py
    - Types_Mini_Core_Kernel.py
    - Exceptions_Mini_Core_Kernel.py

===============================================================================
Python Source
===============================================================================

"""
"""
Temporal_Mini_Memory_Kernel.py

Bounded temporal memory engine.

Maintains historical signal observations and provides deterministic
momentum calculations for downstream reasoning kernels.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Deque, Dict, List

from Configuration_Mini_Core_Kernel import TemporalConfiguration
from Exceptions_Mini_Core_Kernel import ValidationError
from Signal_Mini_Data_Kernel import Signal
from Types_Mini_Core_Kernel import (
    KernelComponent,
    KernelMetadata,
    SignalName,
)


@dataclass(slots=True)
class TemporalEngine(KernelComponent):
    """
    Production temporal memory implementation.

    Memory is bounded by configuration to guarantee predictable resource use.
    """

    configuration: TemporalConfiguration

    _history: Dict[SignalName, Deque[float]] = field(
        init=False,
        default_factory=dict,
    )

    def __post_init__(self) -> None:
        self._history = defaultdict(
            lambda: deque(
                maxlen=self.configuration.history_limit
            )
        )

    @property
    def metadata(self) -> KernelMetadata:
        return KernelMetadata(
            name="Temporal Mini Memory Kernel",
            version="1.0.0",
            description=(
                "Maintains bounded historical signal memory and "
                "calculates directional movement."
            ),
        )

    def update(self, signal: Signal) -> None:
        """
        Add a signal observation to temporal memory.
        """
        if not isinstance(signal, Signal):
            raise ValidationError(
                "TemporalEngine.update() requires a Signal instance."
            )

        self._history[signal.name].append(
            float(signal.value)
        )

    def momentum(self, name: SignalName) -> float:
        """
        Calculate directional movement of a signal.

        Formula:
            latest_value - earliest_value

        Returns:
            Zero when insufficient history exists.
        """
        history = self._history.get(name)

        if history is None or len(history) < 2:
            return 0.0

        return history[-1] - history[0]

    def history(self, name: SignalName) -> List[float]:
        """
        Return a safe copy of stored history.
        """
        history = self._history.get(name)

        if history is None:
            return []

        return list(history)