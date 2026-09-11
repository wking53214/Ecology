"""
===============================================================================
Module
===============================================================================

Filename:
Relationship_Mini_Graph_Kernel.py

Purpose:
Implements the relationship mapping subsystem responsible for learning and
tracking signal-to-signal transitions. The Relationship Kernel builds a bounded
directed transition graph from observed runtime behavior and provides
probabilistic relationship forecasts for downstream propagation and reasoning
kernels.

Responsibilities:
- Maintain signal relationship transitions.
- Track observed event sequences.
- Calculate transition probabilities.
- Provide ranked relationship predictions.
- Prevent invalid graph operations.

Public Classes:
- RelationshipEngine

Public Interfaces:
- RelationshipEngine.observe()
- RelationshipEngine.next_likely()
- RelationshipEngine.transitions()

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
Relationship_Mini_Graph_Kernel.py

Signal relationship graph engine.

Learns directional relationships between observed signals and exposes
probabilistic transition forecasts.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from Configuration_Mini_Core_Kernel import RelationshipConfiguration
from Exceptions_Mini_Core_Kernel import ValidationError
from Signal_Mini_Data_Kernel import Signal
from Types_Mini_Core_Kernel import (
    KernelComponent,
    KernelMetadata,
    SignalName,
)


@dataclass(slots=True)
class RelationshipEngine(KernelComponent):
    """
    Directed signal relationship graph.

    Uses observed sequences to construct transition probabilities.
    """

    configuration: RelationshipConfiguration

    _window: deque[SignalName] = field(
        init=False
    )

    _transitions: Dict[
        SignalName,
        Dict[SignalName, int]
    ] = field(
        init=False
    )

    def __post_init__(self) -> None:
        self._window = deque(
            maxlen=self.configuration.window_size
        )

        self._transitions = defaultdict(
            lambda: defaultdict(int)
        )

    @property
    def metadata(self) -> KernelMetadata:
        return KernelMetadata(
            name="Relationship Mini Graph Kernel",
            version="1.0.0",
            description=(
                "Learns probabilistic relationships between runtime signals."
            ),
        )

    def observe(
        self,
        signal: Signal,
    ) -> None:
        """
        Record a signal observation and update graph transitions.
        """
        if not isinstance(signal, Signal):
            raise ValidationError(
                "RelationshipEngine.observe() requires a Signal instance."
            )

        if self._window:
            previous = self._window[-1]

            self._transitions[previous][signal.name] += 1

        self._window.append(signal.name)

    def next_likely(
        self,
        node: SignalName,
        top_k: int = 3,
    ) -> List[Tuple[SignalName, float]]:
        """
        Return the most probable next relationships.

        Args:
            node:
                Source signal.

            top_k:
                Maximum number of returned relationships.

        Returns:
            Ordered list of signal and probability pairs.
        """
        if top_k <= 0:
            raise ValidationError(
                "top_k must be greater than zero."
            )

        if node not in self._transitions:
            return []

        transitions = self._transitions[node]

        total = sum(transitions.values())

        if total == 0:
            return []

        ranked = [
            (
                destination,
                count / total,
            )
            for destination, count in transitions.items()
        ]

        ranked.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        return ranked[:top_k]

    def transitions(
        self,
    ) -> Dict[SignalName, Dict[SignalName, int]]:
        """
        Return a defensive copy of the transition graph.
        """
        return {
            source: dict(targets)
            for source, targets in self._transitions.items()
        }