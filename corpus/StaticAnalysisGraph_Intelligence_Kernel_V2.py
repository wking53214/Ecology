# ===============================================================================
# ARCHITECTURE COMPILATION NOTES
# ===============================================================================
#
# Module:
# StaticAnalysisGraph_Intelligence_Kernel_V1.py
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
# Machine-Readable Architecture Mapping
#
# ===============================================================================
# PURPOSE
# ===============================================================================
#
# StaticAnalysisGraph Intelligence Kernel converts Python source code into a
# deterministic graph-based intermediate representation.
#
# The kernel performs structural analysis without executing application code.
#
# It transforms source files into analyzable architecture graphs containing:
#
#   - Modules
#   - Classes
#   - Functions
#   - Async functions
#   - Imports
#   - Lexical call relationships
#   - Dependency relationships
#
#
# The resulting graph becomes a foundational artifact for:
#
#   - Architecture discovery
#   - Dependency analysis
#   - Code intelligence
#   - Knowledge extraction
#   - Repository understanding
#   - AI-assisted software reasoning
#
#
# Guarantees:
#
#   - No code execution
#   - No runtime inspection
#   - No import resolution
#   - No type inference
#   - No dynamic evaluation
#   - Deterministic output
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
# ASTExtractorEngine
#
# Purpose:
#     Deterministic source analysis engine.
#
# Responsibilities:
#
#     - Parse Python source
#     - Traverse AST nodes
#     - Identify structural entities
#     - Capture imports
#     - Capture lexical call relationships
#     - Generate graph artifacts
#
#
# -------------------------------------------------------------------------------
#
# GraphNode
#
# Purpose:
#     Immutable representation of an analyzed entity.
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
#
# Future Extensions:
#
#     IMPORTS
#     INHERITS
#     REFERENCES
#     DEPENDS_ON
#
#
# -------------------------------------------------------------------------------
#
# AnalysisGraph
#
# Purpose:
#     Canonical validated graph container.
#
# Provides:
#
#     - Node storage
#     - Edge storage
#     - Graph validation
#     - Graph statistics
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
# ASTExtractorEngine
#
#        |
#        +-------------------+
#        |                   |
#        v                   v
#
#   GraphNode          GraphEdge
#
#        |                   |
#        +-------------------+
#
#                |
#                v
#
#          AnalysisGraph
#
#
# ===============================================================================
# MATHEMATICAL MODEL
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
#     G = {
#
#         Nodes,
#         Edges,
#         Metadata
#
#     }
#
#
# Nodes represent discovered entities.
#
# Edges represent discovered relationships.
#
#
# ===============================================================================
# ARCHITECTURAL SEPARATION
# ===============================================================================
#
#
# Discovery Layer:
#
#     ASTExtractorEngine
#
#
# Representation Layer:
#
#     GraphNode
#     GraphEdge
#     AnalysisGraph
#
#
# This separation prevents extraction logic from becoming coupled to:
#
#     - Storage
#     - Visualization
#     - Search
#     - AI reasoning layers
#
#
# ===============================================================================


from __future__ import annotations


import ast

from dataclasses import dataclass, field

from typing import (
    Dict,
    List,
    Mapping,
    Optional,
)


# ===============================================================================
# LOCAL CORE EXCEPTIONS
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
# KERNEL METADATA
# ===============================================================================


@dataclass(frozen=True, slots=True)
class KernelMetadata:

    name: str

    version: str

    description: str



class KernelComponent:
    """
    Base kernel contract.
    """

    @property
    def metadata(self) -> KernelMetadata:
        raise NotImplementedError



# ===============================================================================
# GRAPH DATA CONTRACTS
# ===============================================================================


@dataclass(frozen=True, slots=True)
class GraphNode:
    """
    Immutable graph node representation.
    """

    identifier: str

    kind: str

    source_file: str


    def __post_init__(self):

        if not self.identifier.strip():

            raise ValidationError(
                "Graph node identifier cannot be empty."
            )



@dataclass(frozen=True, slots=True)
class GraphEdge:
    """
    Immutable graph relationship.
    """

    source: str

    destination: str

    relationship: str

    evidence: str



@dataclass(frozen=True, slots=True)
class AnalysisGraph(
    KernelComponent
):
    """
    Immutable static analysis graph.
    """

    nodes: Mapping[str, GraphNode]

    edges: List[GraphEdge]

    total_lines: int



    @property
    def metadata(self):

        return KernelMetadata(

            name=
            "Static Analysis Graph Intelligence Kernel",

            version=
            "1.0.0",

            description=
            (
                "Canonical immutable graph representation "
                "for deterministic source analysis."
            )

        )



    def __post_init__(self):

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

        return len(self.nodes)



    def edge_count(self) -> int:

        return len(self.edges)
# ===============================================================================
# AST EXTRACTION ENGINE
# ===============================================================================
#
# Purpose:
#     Converts Python source trees into deterministic analysis graphs.
#
# Responsibilities:
#
#     - Parse source safely
#     - Discover modules
#     - Discover classes
#     - Discover functions
#     - Discover async functions
#     - Discover imports
#     - Capture lexical call relationships
#     - Produce immutable graph artifacts
#
# ===============================================================================


@dataclass(slots=True)
class ASTExtractorEngine(
    KernelComponent,
    ast.NodeVisitor,
):
    """
    Production deterministic AST analysis engine.

    This component performs static structural analysis only.

    It never:
        - Executes code
        - Imports modules
        - Resolves runtime objects
        - Performs type inference
    """


    filename: str = "<module>"


    nodes: Dict[str, GraphNode] = field(
        init=False,
        default_factory=dict,
    )


    edges: List[GraphEdge] = field(
        init=False,
        default_factory=list,
    )


    scope: List[str] = field(
        init=False,
        default_factory=list,
    )



    @property
    def metadata(self) -> KernelMetadata:

        return KernelMetadata(

            name=
            "AST Extractor Analysis Engine",

            version=
            "2.0.0",

            description=
            (
                "Deterministic Python AST to graph "
                "intermediate representation extractor."
            )

        )



    # ===========================================================================
    # PUBLIC EXTRACTION INTERFACE
    # ===========================================================================


    def extract(
        self,
        source: str,
    ) -> AnalysisGraph:
        """
        Convert Python source text into AnalysisGraph.
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

        self.scope.clear()



        self.visit(
            tree
        )


        return AnalysisGraph(

            nodes=dict(
                self.nodes
            ),

            edges=list(
                self.edges
            ),

            total_lines=len(
                source.splitlines()
            )

        )



    # ===========================================================================
    # MODULE DISCOVERY
    # ===========================================================================


    def visit_Module(
        self,
        node: ast.Module,
    ):
        """
        Register root source module.
        """


        self._add_node(

            self.filename,

            "module"

        )


        self.generic_visit(
            node
        )



    # ===========================================================================
    # CLASS DISCOVERY
    # ===========================================================================


    def visit_ClassDef(
        self,
        node: ast.ClassDef,
    ):
        """
        Register class definitions.
        """


        name = self._qualified_name(
            node.name
        )


        self._add_node(

            name,

            "class"

        )


        self.scope.append(
            node.name
        )


        self.generic_visit(
            node
        )


        self.scope.pop()



    # ===========================================================================
    # FUNCTION DISCOVERY
    # ===========================================================================


    def visit_FunctionDef(
        self,
        node: ast.FunctionDef,
    ):
        """
        Register standard functions.
        """


        self._register_function(

            node,

            "function"

        )



    def visit_AsyncFunctionDef(
        self,
        node: ast.AsyncFunctionDef,
    ):
        """
        Register asynchronous functions.
        """


        self._register_function(

            node,

            "async_function"

        )



    def _register_function(
        self,
        node,
        kind: str,
    ):
        """
        Common function registration logic.
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



    # ===========================================================================
    # CALL GRAPH EXTRACTION
    # ===========================================================================


    def visit_Call(
        self,
        node: ast.Call,
    ):
        """
        Capture lexical function calls.

        Example:

            service.process()

        becomes:

            caller --> service.process
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



            self.edges.append(

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



    # ===========================================================================
    # IMPORT EXTRACTION
    # ===========================================================================


    def visit_Import(
        self,
        node: ast.Import,
    ):
        """
        Capture standard imports.
        """


        for alias in node.names:


            self._add_node(

                alias.name,

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


            name = (

                f"{module}.{alias.name}"

                if module

                else alias.name

            )


            self._add_node(

                name,

                "import"

            )



    # ===========================================================================
    # INTERNAL GRAPH HELPERS
    # ===========================================================================


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



    def _qualified_name(
        self,
        name: str,
    ) -> str:
        """
        Build scoped entity name.
        """


        if self.scope:

            return ".".join(

                self.scope + [name]

            )


        return name



    def _resolve_call(
        self,
        node: ast.AST,
    ) -> Optional[str]:
        """
        Resolve lexical call target.

        Supports:

            function()

            object.method()

        Does not perform runtime resolution.
        """


        if isinstance(
            node,
            ast.Name
        ):

            return node.id



        if isinstance(
            node,
            ast.Attribute
        ):


            parts = []


            current = node



            while isinstance(

                current,

                ast.Attribute

            ):


                parts.append(

                    current.attr

                )


                current = current.value



            if isinstance(

                current,

                ast.Name

            ):


                parts.append(

                    current.id

                )



            return ".".join(

                reversed(parts)

            )



        return None