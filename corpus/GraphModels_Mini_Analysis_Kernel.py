"""
===============================================================================
Module
===============================================================================

Filename:
GraphModels_Mini_Analysis_Kernel.py

Purpose:
Defines the canonical graph data structures used by the static analysis
subsystem. This kernel provides immutable representations of nodes and edges
while enabling higher-level graph extraction, analysis, and serialization
components to operate on a consistent contract.

Responsibilities:
- Define graph node structures.
- Define graph relationship structures.
- Maintain immutable graph records.
- Provide validated graph containers.
- Establish graph analysis data contracts.

Public Classes:
- GraphNode
- GraphEdge
- AnalysisGraph

Public Interfaces:
- AnalysisGraph.node_count()
- AnalysisGraph.edge_count()

Dependencies:
- Python Standard Library
    - dataclasses
    - typing

- Local
    - Exceptions_Mini_Core_Kernel.py
    - Types_Mini_Core_Kernel.py

===============================================================================
Python Source
===============================================================================

"""
"""
GraphModels_Mini_Analysis_Kernel.py

Canonical graph models for static analysis.

Provides immutable graph structures consumed by extraction
and serialization kernels.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Mapping

from Exceptions_Mini_Core_Kernel import ValidationError
from Types_Mini_Core_Kernel import KernelComponent, KernelMetadata


@dataclass(frozen=True, slots=True)
class GraphNode:
    """
    Immutable graph node representation.
    """

    identifier: str
    kind: str
    source_file: str

    def __post_init__(self) -> None:
        if not self.identifier.strip():
            raise ValidationError(
                "Graph node identifier cannot be empty."
            )


@dataclass(frozen=True, slots=True)
class GraphEdge:
    """
    Immutable graph edge representation.
    """

    source: str
    destination: str
    relationship: str
    evidence: str


@dataclass(frozen=True, slots=True)
class AnalysisGraph(KernelComponent):
    """
    Immutable static analysis graph.
    """

    nodes: Mapping[str, GraphNode]
    edges: List[GraphEdge]
    total_lines: int

    @property
    def metadata(self) -> KernelMetadata:
        return KernelMetadata(
            name="Graph Models Mini Analysis Kernel",
            version="1.0.0",
            description=(
                "Defines immutable graph structures for static analysis."
            ),
        )

    def __post_init__(self) -> None:
        if self.total_lines < 0:
            raise ValidationError(
                "Graph line count cannot be negative."
            )

        if self.nodes is None:
            raise ValidationError(
                "Graph nodes cannot be None."
            )

        if self.edges is None:
            raise ValidationError(
                "Graph edges cannot be None."
            )

    def node_count(self) -> int:
        """
        Return total graph nodes.
        """
        return len(self.nodes)

    def edge_count(self) -> int:
        """
        Return total graph edges.
        """
        return len(self.edges)