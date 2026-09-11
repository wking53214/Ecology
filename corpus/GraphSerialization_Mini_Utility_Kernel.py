"""
===============================================================================
Module
===============================================================================

Filename:
GraphSerialization_Mini_Utility_Kernel.py

Purpose:
Provides serialization and transformation utilities for analysis graph objects.
This kernel converts immutable graph structures into portable dictionary
representations suitable for storage, auditing, transmission, visualization,
and integration with external analysis systems.

Responsibilities:
- Serialize graph nodes.
- Serialize graph edges.
- Convert graph models into transport formats.
- Preserve graph integrity during transformation.
- Provide deterministic serialization output.

Public Classes:
- GraphSerializer

Public Interfaces:
- GraphSerializer.to_dict()
- GraphSerializer.to_json_ready()

Dependencies:
- Python Standard Library
    - dataclasses
    - typing

- Local
    - GraphModels_Mini_Analysis_Kernel.py
    - Types_Mini_Core_Kernel.py
    - Exceptions_Mini_Core_Kernel.py

===============================================================================
Python Source
===============================================================================

"""
"""
GraphSerialization_Mini_Utility_Kernel.py

Graph serialization utility kernel.

Transforms analysis graph models into deterministic transport structures.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from Exceptions_Mini_Core_Kernel import ValidationError
from GraphModels_Mini_Analysis_Kernel import AnalysisGraph
from Types_Mini_Core_Kernel import (
    KernelComponent,
    KernelMetadata,
)


class GraphSerializer(KernelComponent):
    """
    Production graph serialization utility.
    """

    @property
    def metadata(self) -> KernelMetadata:
        return KernelMetadata(
            name="Graph Serialization Mini Utility Kernel",
            version="1.0.0",
            description=(
                "Serializes analysis graph models into portable formats."
            ),
        )

    def to_dict(
        self,
        graph: AnalysisGraph,
    ) -> dict[str, Any]:
        """
        Convert an analysis graph into a dictionary representation.
        """

        if not isinstance(graph, AnalysisGraph):
            raise ValidationError(
                "GraphSerializer requires an AnalysisGraph instance."
            )

        return {
            "nodes": [
                asdict(node)
                for node in graph.nodes.values()
            ],
            "edges": [
                asdict(edge)
                for edge in graph.edges
            ],
            "metadata": {
                "total_lines": graph.total_lines,
                "node_count": graph.node_count(),
                "edge_count": graph.edge_count(),
            },
        }

    def to_json_ready(
        self,
        graph: AnalysisGraph,
    ) -> dict[str, Any]:
        """
        Produce a JSON-compatible representation.

        All returned values are composed only of primitive
        Python serialization types.
        """

        return self.to_dict(graph)