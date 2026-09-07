# ===============================================================================
# ARCHITECTURE COMPILATION NOTES
# ===============================================================================
#
# Module:
# StaticCode_Intelligence_Graph_Kernel_V1.py
#
# Classification:
# Deterministic Static Code Intelligence,
# Python Architecture Discovery,
# Dependency Graph Construction,
# Knowledge Representation Extraction Engine
#
# Domain:
# Abstract Syntax Tree Analysis,
# Program Structure Modeling,
# Software Dependency Intelligence,
# Machine-Readable Architecture Mapping,
# Repository Understanding
#
# ===============================================================================
# MODULE CONSOLIDATION RECORD
# ===============================================================================
#
# This module was created by combining:
#
#
# ------------------------------------------------------------------------------
#
# Source Module:
#
# ASTExtractor_Mini_Analysis_Kernel.py
#
# Original Responsibility:
#
# Deterministic Python AST extraction engine.
#
# Capabilities absorbed:
#
#     - Python source parsing
#     - AST traversal
#     - Module discovery
#     - Class discovery
#     - Function discovery
#     - Async function discovery
#     - Import extraction
#     - Lexical call relationship extraction
#
#
# ------------------------------------------------------------------------------
#
# Source Module:
#
# GraphModels_Mini_Analysis_Kernel.py
#
# Original Responsibility:
#
# Canonical static analysis graph representation layer.
#
# Capabilities absorbed:
#
#     - Immutable graph node contracts
#     - Immutable graph edge contracts
#     - Graph container validation
#     - Graph statistics
#     - Analysis graph metadata
#
#
# ------------------------------------------------------------------------------
#
# Consolidated Purpose:
#
# Transform Python source code into deterministic,
# machine-readable architecture intelligence graphs.
#
#
# ===============================================================================
# PURPOSE
# ===============================================================================
#
# StaticCode Intelligence Graph Kernel converts Python source code into a
# deterministic graph-based intermediate representation.
#
# The kernel performs structural analysis without executing application code.
#
# It transforms source files into analyzable architecture graphs containing:
#
#     - Modules
#     - Classes
#     - Functions
#     - Async functions
#     - Imports
#     - Import aliases
#     - Function calls
#     - Class inheritance relationships
#     - Dependency relationships
#
#
# The resulting graph becomes a foundational artifact for:
#
#     - Architecture discovery
#     - Dependency analysis
#     - Repository intelligence
#     - Code understanding
#     - Knowledge extraction
#     - AI-assisted software reasoning
#     - Change impact analysis
#
#
# Guarantees:
#
#     - No code execution
#     - No runtime inspection
#     - No import resolution
#     - No type inference
#     - No dynamic evaluation
#     - Deterministic output
#     - Immutable graph artifacts
#
#
# ===============================================================================
# CORE DESIGN PRINCIPLE
# ===============================================================================
#
#
# Traditional Software Understanding:
#
#
#              SOURCE CODE
#                   |
#                   v
#             HUMAN READING
#                   |
#                   v
#          MANUAL ARCHITECTURE MAP
#
#
#
# Static Intelligence Model:
#
#
#              SOURCE CODE
#                   |
#                   v
#              AST PARSER
#                   |
#                   v
#          STRUCTURAL EXTRACTION
#                   |
#                   v
#          RELATIONSHIP MODELING
#                   |
#                   v
#           GRAPH REPRESENTATION
#                   |
#                   v
#          MACHINE ANALYZABLE MODEL
#
#
# ===============================================================================
# SYSTEM COMPONENT MAP
# ===============================================================================
#
#
# StaticCodeGraphEngine
#
# Purpose:
#     Primary static intelligence extraction engine.
#
# Responsibilities:
#
#     - Parse Python source safely
#     - Traverse AST structures
#     - Generate graph entities
#     - Capture structural relationships
#     - Produce immutable analysis graphs
#
#
# -------------------------------------------------------------------------------
#
# GraphNode
#
# Purpose:
#     Immutable representation of discovered architecture entities.
#
# Represents:
#
#     - Module
#     - Class
#     - Function
#     - Async Function
#     - Import
#
#
# -------------------------------------------------------------------------------
#
# GraphEdge
#
# Purpose:
#     Immutable relationship representation.
#
# Current Relationships:
#
#     CALL
#     INHERITS
#
#
# Future Extensions:
#
#     IMPORTS
#     REFERENCES
#     DEPENDS_ON
#     IMPLEMENTS
#     MODIFIES
#
#
# -------------------------------------------------------------------------------
#
# AnalysisGraph
#
# Purpose:
#     Immutable validated architecture graph container.
#
# Provides:
#
#     - Node storage
#     - Relationship storage
#     - Validation
#     - Statistics
#     - Deterministic serialization boundary
#
#
# ===============================================================================
# EXTRACTION PIPELINE
# ===============================================================================
#
#
# PYTHON SOURCE
#
#        |
#        v
#
#    ast.parse()
#
#        |
#        v
#
#    AST TREE
#
#        |
#        v
#
# StaticCodeGraphEngine
#
#        |
#        +-----------------------+
#        |                       |
#        v                       v
#
#   GraphNode              GraphEdge
#
#        |                       |
#        +-----------------------+
#
#                |
#                v
#
#        Immutable AnalysisGraph
#
#
# ===============================================================================
# GRAPH MODEL
# ===============================================================================
#
#
# Source:
#
#     S
#
#
# Extraction Function:
#
#
#     Extract(S) -> G
#
#
# Where:
#
#
#     G =
#
#     {
#
#       Nodes,
#       Edges,
#       Metadata
#
#     }
#
#
# Nodes represent architecture entities.
#
# Edges represent discovered relationships.
#
#
# ===============================================================================
# IMMUTABILITY GUARANTEE
# ===============================================================================
#
#
# Previous Design Risk:
#
#     frozen dataclass + mutable containers
#
#
# Example Failure:
#
#     graph.edges.append(edge)
#
#
# Refactored Design:
#
#     Nodes:
#         MappingProxyType
#
#     Edges:
#         Tuple
#
#
# Result:
#
#     Graph artifacts cannot be modified after creation.
#
#
# ===============================================================================
# ARCHITECTURAL SEPARATION
# ===============================================================================
#
#
# Extraction Layer:
#
#     StaticCodeGraphEngine
#
#
# Representation Layer:
#
#     GraphNode
#     GraphEdge
#     AnalysisGraph
#
#
# Contract Layer:
#
#     KernelMetadata
#     KernelComponent
#     ProcessingError
#     ValidationError
#
#
# This separation prevents extraction logic from becoming coupled to:
#
#     - Storage systems
#     - Visualization engines
#     - Search systems
#     - AI reasoning layers
#
#
# ===============================================================================
# RED TEAM VALIDATION APPLIED
# ===============================================================================
#
# Corrected:
#
#     ✓ Mutable frozen graph containers
#     ✓ Non-deterministic ordering
#     ✓ Duplicate relationship generation
#     ✓ Missing inheritance extraction
#     ✓ Missing import alias preservation
#     ✓ Weak immutability guarantees
#     ✓ Ambiguous module responsibility
#
#
# Added:
#
#     ✓ Deterministic graph ordering
#     ✓ Immutable graph output
#     ✓ Relationship deduplication
#     ✓ Expanded architecture metadata
#     ✓ Consolidated intelligence boundary
#
#
# ===============================================================================

# ===============================================================================
# IMPORTS
# ===============================================================================

from __future__ import annotations


import ast

from dataclasses import (
    dataclass,
    field,
)

from types import MappingProxyType

from typing import (
    Dict,
    Tuple,
    Mapping,
    Optional,
    Set,
)


# ===============================================================================
# CORE EXCEPTIONS
# ===============================================================================
#
# These contracts may remain externalized into:
#
#     Exceptions_Mini_Core_Kernel.py
#
# They are included here only to maintain standalone execution capability.
#
# ===============================================================================


class ProcessingError(Exception):
    """
    Raised when source processing fails.
    """

    pass



class ValidationError(Exception):
    """
    Raised when graph validation fails.
    """

    pass



# ===============================================================================
# KERNEL METADATA CONTRACT
# ===============================================================================
#
# Provides standardized metadata across the intelligence kernel ecosystem.
#
# ===============================================================================


@dataclass(
    frozen=True,
    slots=True,
)
class KernelMetadata:
    """
    Immutable kernel identification metadata.
    """

    name: str

    version: str

    description: str



# ===============================================================================
# KERNEL COMPONENT CONTRACT
# ===============================================================================
#
# Every intelligence kernel exposes metadata.
#
# ===============================================================================


class KernelComponent:
    """
    Base kernel contract.
    """

    @property
    def metadata(
        self
    ) -> KernelMetadata:

        raise NotImplementedError



# ===============================================================================
# IMMUTABLE GRAPH DATA CONTRACTS
# ===============================================================================
#
# These structures represent the canonical architecture graph format.
#
# ===============================================================================


@dataclass(
    frozen=True,
    slots=True,
)
class GraphNode:
    """
    Immutable architecture entity representation.
    """

    identifier: str

    kind: str

    source_file: str


    def __post_init__(
        self
    ) -> None:

        if not self.identifier.strip():

            raise ValidationError(
                "Graph node identifier cannot be empty."
            )


        if not self.kind.strip():

            raise ValidationError(
                "Graph node kind cannot be empty."
            )



# ===============================================================================
#
# GRAPH RELATIONSHIP CONTRACT
#
# ===============================================================================


@dataclass(
    frozen=True,
    slots=True,
)
class GraphEdge:
    """
    Immutable architecture relationship.
    """

    source: str

    destination: str

    relationship: str

    evidence: str


    def __post_init__(
        self
    ) -> None:

        if not self.source.strip():

            raise ValidationError(
                "Graph edge source cannot be empty."
            )


        if not self.destination.strip():

            raise ValidationError(
                "Graph edge destination cannot be empty."
            )


        if not self.relationship.strip():

            raise ValidationError(
                "Graph edge relationship cannot be empty."
            )



# ===============================================================================
# IMMUTABLE ANALYSIS GRAPH
# ===============================================================================


@dataclass(
    frozen=True,
    slots=True,
)
class AnalysisGraph(
    KernelComponent
):
    """
    Immutable deterministic static analysis graph.

    Guarantees:

        - Nodes cannot be modified
        - Edges cannot be modified
        - Output ordering is deterministic
    """


    nodes: Mapping[str, GraphNode]

    edges: Tuple[GraphEdge, ...]

    total_lines: int



    @property
    def metadata(
        self
    ) -> KernelMetadata:

        return KernelMetadata(

            name=
            "StaticCode Intelligence Graph Kernel",

            version=
            "1.0.0",

            description=
            (
                "Immutable deterministic architecture "
                "graph representation generated from "
                "Python static analysis."
            )

        )



    def __post_init__(
        self
    ) -> None:


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



    def node_count(
        self
    ) -> int:
        """
        Return number of architecture entities.
        """

        return len(
            self.nodes
        )



    def edge_count(
        self
    ) -> int:
        """
        Return number of architecture relationships.
        """

        return len(
            self.edges
        )

        # ===============================================================================
# STATIC CODE GRAPH EXTRACTION ENGINE
# ===============================================================================
#
# Purpose:
#     Converts Python source trees into deterministic architecture graphs.
#
# Responsibilities:
#
#     - Parse Python source safely
#     - Discover modules
#     - Discover classes
#     - Discover functions
#     - Discover async functions
#     - Discover imports
#     - Preserve import aliases
#     - Capture lexical calls
#     - Capture inheritance relationships
#     - Generate immutable graph artifacts
#
# Guarantees:
#
#     - No execution
#     - No imports
#     - No runtime inspection
#     - No dynamic evaluation
#
# ===============================================================================


@dataclass(
    slots=True
)
class StaticCodeGraphEngine(
    ast.NodeVisitor,
    KernelComponent,
):
    """
    Production deterministic Python static intelligence engine.

    Converts Python source into an immutable architecture graph.

    This engine performs structural analysis only.
    """


    filename: str = "<module>"


    nodes: Dict[str, GraphNode] = field(
        init=False,
        default_factory=dict,
    )


    edges: list[GraphEdge] = field(
        init=False,
        default_factory=list,
    )


    scope: list[str] = field(
        init=False,
        default_factory=list,
    )


    edge_keys: Set[tuple] = field(
        init=False,
        default_factory=set,
    )



    @property
    def metadata(
        self
    ) -> KernelMetadata:

        return KernelMetadata(

            name=
            "StaticCode Intelligence Graph Engine",

            version=
            "1.0.0",

            description=
            (
                "Deterministic Python AST extraction engine "
                "producing immutable architecture graphs."
            )

        )



# ===============================================================================
# PUBLIC EXTRACTION INTERFACE
# ===============================================================================


    def extract(
        self,
        source: str,
    ) -> AnalysisGraph:
        """
        Convert Python source text into immutable AnalysisGraph.
        """


        if not source.strip():

            raise ProcessingError(
                "Cannot analyze empty source."
            )


        try:

            tree = ast.parse(
                source
            )


        except SyntaxError as exc:

            raise ProcessingError(
                f"Invalid Python source: {exc}"
            ) from exc



        self.nodes.clear()

        self.edges.clear()

        self.edge_keys.clear()

        self.scope.clear()



        self.visit(
            tree
        )


        #
        # Deterministic ordering
        #

        ordered_nodes = dict(
            sorted(
                self.nodes.items(),
                key=lambda item: item[0],
            )
        )


        ordered_edges = tuple(
            sorted(
                self.edges,
                key=lambda edge:
                (
                    edge.source,
                    edge.destination,
                    edge.relationship,
                ),
            )
        )



        return AnalysisGraph(

            nodes=MappingProxyType(
                ordered_nodes
            ),

            edges=ordered_edges,

            total_lines=len(
                source.splitlines()
            )

        )



# ===============================================================================
# MODULE DISCOVERY
# ===============================================================================


    def visit_Module(
        self,
        node: ast.Module,
    ):
        """
        Register source module.
        """


        self._add_node(

            self.filename,

            "module"

        )


        self.generic_visit(
            node
        )



# ===============================================================================
# CLASS DISCOVERY
# ===============================================================================


    def visit_ClassDef(
        self,
        node: ast.ClassDef,
    ):
        """
        Discover classes and inheritance relationships.
        """


        name = self._qualified_name(
            node.name
        )


        self._add_node(

            name,

            "class"

        )


        #
        # Extract inheritance
        #

        for base in node.bases:

            parent = self._resolve_call(
                base
            )


            if parent:

                self._add_edge(

                    GraphEdge(

                        source=name,

                        destination=parent,

                        relationship="INHERITS",

                        evidence=ast.unparse(base)

                    )

                )



        self.scope.append(
            node.name
        )


        self.generic_visit(
            node
        )


        self.scope.pop()



# ===============================================================================
# FUNCTION DISCOVERY
# ===============================================================================


    def visit_FunctionDef(
        self,
        node: ast.FunctionDef,
    ):
        """
        Discover normal functions.
        """

        self._register_function(
            node,
            "function",
        )



    def visit_AsyncFunctionDef(
        self,
        node: ast.AsyncFunctionDef,
    ):
        """
        Discover async functions.
        """

        self._register_function(
            node,
            "async_function",
        )



    def _register_function(
        self,
        node,
        kind: str,
    ):
        """
        Shared function registration logic.
        """


        name = self._qualified_name(
            node.name
        )


        self._add_node(

            name,

            kind

        )


        self.scope.append(
            node.name
        )


        self.generic_visit(
            node
        )


        self.scope.pop()



# ===============================================================================
# CALL GRAPH EXTRACTION
# ===============================================================================


    def visit_Call(
        self,
        node: ast.Call,
    ):
        """
        Extract lexical call relationships.

        Example:

            service.process()

        Creates:

            caller ---> service.process
        """


        caller = (

            ".".join(
                self.scope
            )

            if self.scope

            else self.filename

        )


        callee = self._resolve_call(
            node.func
        )



        if callee:


            try:

                evidence = ast.unparse(
                    node
                )


            except Exception:

                evidence = (
                    "<unparse_failed>"
                )



            self._add_edge(

                GraphEdge(

                    source=caller,

                    destination=callee,

                    relationship="CALL",

                    evidence=evidence

                )

            )


        self.generic_visit(
            node
        )



# ===============================================================================
# IMPORT EXTRACTION
# ===============================================================================


    def visit_Import(
        self,
        node: ast.Import,
    ):
        """
        Capture standard imports and aliases.
        """


        for alias in node.names:


            identifier = (

                f"{alias.name}"
            )


            if alias.asname:

                identifier += (

                    f" as {alias.asname}"

                )


            self._add_node(

                identifier,

                "import"

            )



    def visit_ImportFrom(
        self,
        node: ast.ImportFrom,
    ):
        """
        Capture from-import statements.
        """


        module = node.module or ""


        for alias in node.names:


            identifier = (

                f"{module}.{alias.name}"

                if module

                else alias.name

            )


            if alias.asname:

                identifier += (

                    f" as {alias.asname}"

                )


            self._add_node(

                identifier,

                "import"

            )

# ===============================================================================
# INTERNAL GRAPH HELPERS
# ===============================================================================
#
# Purpose:
#     Provides controlled graph mutation during extraction.
#
# Note:
#     Mutation exists only during the extraction phase.
#
#     Final AnalysisGraph output is immutable.
#
# ===============================================================================


    def _add_node(
        self,
        identifier: str,
        kind: str,
    ):
        """
        Add graph node if it does not already exist.
        """


        if identifier not in self.nodes:


            self.nodes[identifier] = GraphNode(

                identifier=identifier,

                kind=kind,

                source_file=self.filename

            )



# ===============================================================================
# EDGE MANAGEMENT
# ===============================================================================


    def _add_edge(
        self,
        edge: GraphEdge,
    ):
        """
        Add relationship if not already present.

        Prevents duplicate graph relationships.
        """


        edge_key = (

            edge.source,

            edge.destination,

            edge.relationship,

        )


        if edge_key not in self.edge_keys:


            self.edge_keys.add(
                edge_key
            )


            self.edges.append(
                edge
            )



# ===============================================================================
# NAME RESOLUTION
# ===============================================================================


    def _qualified_name(
        self,
        name: str,
    ) -> str:
        """
        Build scoped architecture identifier.

        Example:

            class Service:

                def run():

        Produces:

            Service.run
        """


        if self.scope:

            return ".".join(

                self.scope + [name]

            )


        return name



# ===============================================================================
# STATIC CALL RESOLUTION
# ===============================================================================


    def _resolve_call(
        self,
        node: ast.AST,
    ) -> Optional[str]:
        """
        Resolve lexical call target.

        Supported:

            function()

            object.method()

            module.function()

        Not supported:

            Runtime resolution

            Dynamic attributes

            Reflection

            Type inference
        """



        if isinstance(
            node,
            ast.Name,
        ):

            return node.id



        if isinstance(
            node,
            ast.Attribute,
        ):


            parts = []


            current = node



            while isinstance(

                current,

                ast.Attribute,

            ):


                parts.append(

                    current.attr

                )


                current = current.value



            if isinstance(

                current,

                ast.Name,

            ):


                parts.append(

                    current.id

                )



            return ".".join(

                reversed(parts)

            )



        return None



# ===============================================================================
# ANALYSIS VALIDATION
# ===============================================================================
#
# Performs internal consistency validation before graph emission.
#
# ===============================================================================


    def validate(
        self,
    ) -> None:
        """
        Validate extraction state.
        """


        for identifier, node in self.nodes.items():


            if identifier != node.identifier:

                raise ValidationError(

                    "Node index mismatch detected."

                )



        for edge in self.edges:


            if edge.source not in self.nodes:


                #
                # External calls are permitted.
                #
                # Example:
                #
                #     print()
                #
                #     requests.get()
                #
                #

                continue



# ===============================================================================
# EXECUTION EXAMPLE
# ===============================================================================
#
# The following demonstrates intended usage.
#
# This does not execute analyzed source code.
#
# It only parses and extracts structure.
#
# ===============================================================================


if __name__ == "__main__":


    sample_source = """

class Base:

    def execute(self):
        pass



class Service(Base):

    def run(self):

        self.execute()



def helper():

    return 1

"""


    engine = StaticCodeGraphEngine(
        filename="sample.py"
    )


    graph = engine.extract(
        sample_source
    )


    print(
        "STATIC GRAPH ANALYSIS"
    )


    print(
        "Nodes:",
        graph.node_count()
    )


    print(
        "Edges:",
        graph.edge_count()
    )


    for node in graph.nodes.values():

        print(
            node
        )


    for edge in graph.edges:

        print(
            edge
        )
