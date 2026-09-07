===============================================================================
Module
===============================================================================

Filename:
Propagation_Mini_Forecasting_Kernel.py

Purpose:
Implements the predictive propagation subsystem responsible for exploring
possible future signal paths through the relationship graph. The Propagation
Kernel performs bounded graph traversal with probability decay, producing
ranked forecasts that can be consumed by decision and governance kernels.

Responsibilities:
- Traverse learned relationship paths.
- Calculate forecast probabilities.
- Apply configurable probability decay.
- Prevent uncontrolled recursion depth.
- Return ranked predictive paths.

Public Classes:
- PropagationEngine

Public Interfaces:
- PropagationEngine.forecast_paths()

Dependencies:
- Python Standard Library
    - dataclasses
    - typing

- Local
    - Configuration_Mini_Core_Kernel.py
    - Relationship_Mini_Graph_Kernel.py
    - Types_Mini_Core_Kernel.py
    - Exceptions_Mini_Core_Kernel.py

===============================================================================
Python Source
===============================================================================

"""
Propagation_Mini_Forecasting_Kernel.py

Bounded predictive propagation engine.

Uses relationship graphs to forecast possible future signal sequences.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from Configuration_Mini_Core_Kernel import PropagationConfiguration
from Exceptions_Mini_Core_Kernel import ValidationError
from Relationship_Mini_Graph_Kernel import RelationshipEngine
from Types_Mini_Core_Kernel import (
    KernelComponent,
    KernelMetadata,
    Probability,
    SignalName,
)


@dataclass(slots=True)
class PropagationEngine(KernelComponent):
    """
    Predictive relationship traversal engine.
    """

    configuration: PropagationConfiguration

    @property
    def metadata(self) -> KernelMetadata:
        return KernelMetadata(
            name="Propagation Mini Forecasting Kernel",
            version="1.0.0",
            description=(
                "Forecasts future signal paths through relationship graphs."
            ),
        )

    def forecast_paths(
        self,
        start: SignalName,
        relationship: RelationshipEngine,
    ) -> List[Tuple[List[SignalName], Probability]]:
        """
        Generate ranked future signal paths.

        Args:
            start:
                Initial signal node.

            relationship:
                Relationship graph provider.

        Returns:
            List of paths and calculated probabilities.
        """

        if not isinstance(start, str) or not start.strip():
            raise ValidationError(
                "Propagation start node must be a valid name."
            )

        if not isinstance(relationship, RelationshipEngine):
            raise ValidationError(
                "relationship must be RelationshipEngine."
            )

        results: List[
            Tuple[List[SignalName], Probability]
        ] = []

        def traverse(
            node: SignalName,
            path: List[SignalName],
            probability: float,
            depth: int,
            visited: set[str],
        ) -> None:

            if depth == 0:
                results.append(
                    (
                        list(path),
                        probability,
                    )
                )
                return

            if node in visited:
                results.append(
                    (
                        list(path),
                        probability,
                    )
                )
                return

            next_nodes = relationship.next_likely(node)

            if not next_nodes:
                results.append(
                    (
                        list(path),
                        probability,
                    )
                )
                return

            updated_visited = visited | {node}

            for destination, transition_probability in next_nodes:

                traverse(
                    destination,
                    path + [destination],
                    probability
                    * transition_probability
                    * self.configuration.probability_decay,
                    depth - 1,
                    updated_visited,
                )

        traverse(
            start,
            [start],
            1.0,
            self.configuration.max_depth,
            set(),
        )

        results.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        return results