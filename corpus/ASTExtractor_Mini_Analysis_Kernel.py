# ===============================================================================
# ARCHITECTURE COMPILATION NOTES
# ===============================================================================
#
# Module:
# ASTExtractor_Mini_Analysis_Kernel.py
#
# Classification:
# Deterministic Static Analysis Engine,
# Python Abstract Syntax Tree Extraction Kernel,
# Software Intelligence Graph Construction Component
#
# Domain:
# Source Code Intelligence, Dependency Mapping,
# Architecture Discovery, Governance Evidence Collection,
# Static Program Analysis
#
# ===============================================================================
# PURPOSE
# ===============================================================================
#
# ASTExtractor is a deterministic source intelligence kernel designed to convert
# Python source code into structured analysis graphs without executing code.
#
# The architecture transforms raw source material into machine-readable
# structural intelligence by extracting:
#
#   - Modules
#   - Classes
#   - Functions
#   - Async functions
#   - Imports
#   - Lexical call relationships
#
# These extracted entities become graph representations that allow higher-level
# systems to perform:
#
#   - Dependency analysis
#   - Architecture discovery
#   - Code lineage tracking
#   - Governance validation
#   - Software intelligence analysis
#
# ASTExtractor intentionally analyzes what exists structurally rather than
# attempting to predict runtime behavior.
#
#
# ===============================================================================
# CORE DESIGN PRINCIPLE
# ===============================================================================
#
# Traditional Code Analysis Model:
#
#
#             PYTHON SOURCE
#                  |
#                  v
#          EXECUTE APPLICATION
#                  |
#                  v
#       OBSERVE RUNTIME BEHAVIOR
#
#
# ASTExtractor Model:
#
#
#             PYTHON SOURCE
#                  |
#                  v
#             AST PARSER
#                  |
#                  v
#        STRUCTURAL EXTRACTION
#                  |
#       +----------+----------+
#       |          |          |
#       v          v          v
#
#    MODULES    SYMBOLS    CALLS
#
#       |          |          |
#       v          v          v
#
#    GRAPH     ENTITIES   RELATIONSHIPS
#
#
# The kernel creates deterministic structural evidence without execution.
#
#
# ===============================================================================
# SECURITY GUARANTEES
# ===============================================================================
#
#
# No Code Execution
#
# The extractor never executes analyzed source code.
#
# Prevents:
#
#   - Arbitrary execution
#   - Side effects
#   - Runtime mutations
#   - External system interaction
#
#
# -------------------------------------------------------------------------------
#
# No Import Resolution
#
# Imports are recorded as structural references only.
#
# The kernel does not:
#
#   - Load external packages
#   - Resolve installed modules
#   - Execute initialization code
#
#
# -------------------------------------------------------------------------------
#
# No Type Inference
#
# The extractor does not attempt:
#
#   - Runtime type discovery
#   - Object prediction
#   - Data-flow assumptions
#
#
# -------------------------------------------------------------------------------
#
# Deterministic Output
#
# Identical source input produces identical graph output.
#
# Enables:
#
#   - Repeatable analysis
#   - Software comparison
#   - Change detection
#   - Audit evidence generation
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
#     Primary static analysis execution engine.
#
# Responsibilities:
#
#     - Parse Python source
#     - Traverse AST nodes
#     - Maintain lexical scope
#     - Create graph entities
#     - Generate relationship edges
#
#
# -------------------------------------------------------------------------------
#
# AnalysisGraph
#
# Purpose:
#     Intermediate representation of extracted software structure.
#
# Contains:
#
#     - Graph nodes
#     - Graph edges
#     - Source metadata
#     - Line information
#
#
# -------------------------------------------------------------------------------
#
# GraphNode
#
# Purpose:
#     Represents discovered structural entities.
#
# Node Types:
#
#     Module
#     Class
#     Function
#     Async Function
#     Import
#
#
# -------------------------------------------------------------------------------
#
# GraphEdge
#
# Purpose:
#     Represents relationships between software entities.
#
# Relationship Types:
#
#     CALL
#
# Captures:
#
#     - Calling scope
#     - Called target
#     - Source evidence
#
#
# -------------------------------------------------------------------------------
#
# Scope Tracker
#
# Purpose:
#     Maintains lexical context during AST traversal.
#
# Example:
#
#     Class.method.function
#
# becomes:
#
#     Qualified structural identity
#
#
# -------------------------------------------------------------------------------
#
# Import Extractor
#
# Purpose:
#     Records external references without loading dependencies.
#
# Captures:
#
#     - import statements
#     - from imports
#     - referenced modules
#
#
# ===============================================================================
# EXTRACTION PIPELINE
# ===============================================================================
#
#
# SOURCE INPUT
#
#        |
#        v
#
# VALIDATION
#
#        |
#        v
#
# PYTHON AST PARSING
#
#        |
#        v
#
# AST TREE WALK
#
#        |
#        |
# +------+----------------+
# |                       |
# v                       v
#
# STRUCTURAL NODES      RELATIONSHIPS
#
# |                       |
# v                       v
#
# MODULES               CALL EDGES
# CLASSES               IMPORT EDGES
# FUNCTIONS
# IMPORTS
#
#        |
#        v
#
# ANALYSIS GRAPH OUTPUT
#
#
# ===============================================================================
# GOVERNANCE STATE MODEL
# ===============================================================================
#
#
# SOURCE RECEIVED
#
#        |
#        v
#
# SAFETY VALIDATION
#
#        |
#        v
#
# SYNTAX VERIFICATION
#
#        |
#        v
#
# STATIC EXTRACTION
#
#        |
#        v
#
# GRAPH CONSTRUCTION
#
#        |
#        v
#
# SOFTWARE INTELLIGENCE OUTPUT
#
#
# ===============================================================================
# MATHEMATICAL MODEL
# ===============================================================================
#
# ASTExtractor models software structure as:
#
#
# Software System:
#
# S = {
#
#   Nodes,
#   Edges,
#   Metadata
#
# }
#
#
# Graph Representation:
#
#
# G = (V,E)
#
#
# where:
#
# V =
#
#     modules,
#     classes,
#     functions,
#     imports
#
#
# E =
#
#     CALL relationships
#
#
# Deterministic Constraint:
#
#
# Extract(Source) = Graph
#
#
# Same Source:
#
#     produces
#
# Same Graph
#
#
# ===============================================================================
# OPERATIONAL CONTROL MODEL
# ===============================================================================
#
#
#              AST EXTRACTION CONTROL PLANE
#
#                         |
#        +----------------+----------------+
#        |                |                |
#        v                v                v
#
#    Parser Layer    Visitor Layer    Graph Layer
#
#        |                |                |
#        +----------------+----------------+
#
#                         |
#                         v
#
#             Software Intelligence Graph
#
#                         |
#                         v
#
#          Architecture Analysis Pipeline
#
#
# ===============================================================================
# RELATIONSHIP TO GOVERNANCE STACK
# ===============================================================================
#
# ASTExtractor operates as an observation and evidence collection layer.
#
#
#                 Enterprise Governance System
#
#                           |
#                           v
#
#                 Software Intelligence Layer
#
#                           |
#                           v
#
#              ASTExtractor Analysis Kernel
#
#          +----------------+----------------+
#          |                |                |
#          v                v                v
#
#   Architecture Map   Dependency Graph   Risk Analysis
#
#          |
#          v
#
#   Governance Evidence
#
#
# ASTExtractor answers:
#
#     "What exists inside the software?"
#
#
# Governance systems answer:
#
#     "Does the software operate within approved constraints?"
#
#
# ===============================================================================
# RELATIONSHIP TO SENTINEL ARCHITECTURE
# ===============================================================================
#
# ASTExtractor is an observation primitive within a larger governance system.
#
#
#                 SENTINEL GOVERNANCE FABRIC
#
#                           |
#                           v
#
#                  OBSERVATION LAYER
#
#          +----------------+----------------+
#          |                |                |
#          v                v                v
#
#    ASTExtractor     File Scanner    Runtime Sensors
#
#          |
#          v
#
#    Software Structural Truth
#
#
# ASTExtractor is not the governance controller.
#
# It provides the evidence foundation required by governance controllers.
#
#
# ===============================================================================
# ARCHITECTURAL IMPROVEMENTS APPLIED
# ===============================================================================
#
# Original Static Analysis Approach:
#
# - Manual source inspection
# - Runtime-dependent discovery
# - Non-repeatable observations
# - Limited structural visibility
#
#
# Refactored Kernel:
#
# - Added deterministic AST traversal
# - Added graph-based intermediate representation
# - Added lexical scope tracking
# - Added call relationship extraction
# - Added safe parsing boundary
# - Added repeatable analysis output
#
# ===============================================================================
"""
ASTExtractor_Mini_Analysis_Kernel.py

Deterministic Python AST → Analysis Graph extraction kernel.

Responsibilities:
- Parse Python source safely.
- Extract structural entities.
- Build deterministic dependency graphs.
- Capture lexical call relationships.

Guarantees:
- No code execution.
- No import resolution.
- No type inference.
- Deterministic output.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Dict, Optional, List

from Exceptions_Mini_Core_Kernel import ProcessingError
from GraphModels_Mini_Analysis_Kernel import (
    AnalysisGraph,
    GraphEdge,
    GraphNode,
)
from Types_Mini_Core_Kernel import (
    KernelComponent,
    KernelMetadata,
)


@dataclass(slots=True)
class ASTExtractorEngine(
    KernelComponent,
    ast.NodeVisitor,
):
    """
    Production deterministic AST analysis engine.
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
            name="AST Extractor Mini Analysis Kernel",
            version="2.0.0",
            description=(
                "Deterministic AST to graph intermediate "
                "representation extractor."
            ),
        )


    def extract(
        self,
        source: str,
    ) -> AnalysisGraph:

        if not source.strip():
            raise ProcessingError(
                "Cannot analyze empty source."
            )

        try:
            tree = ast.parse(source)

        except SyntaxError as exc:
            raise ProcessingError(
                f"Invalid Python source: {exc}"
            ) from exc


        self.nodes.clear()
        self.edges.clear()
        self.scope.clear()


        self.visit(tree)


        return AnalysisGraph(
            nodes=dict(self.nodes),
            edges=list(self.edges),
            total_lines=len(
                source.splitlines()
            ),
        )


    # ---------------------------------------------------------
    # MODULE
    # ---------------------------------------------------------

    def visit_Module(
        self,
        node: ast.Module,
    ):

        self._add_node(
            self.filename,
            "module",
        )

        self.generic_visit(node)


    # ---------------------------------------------------------
    # DEFINITIONS
    # ---------------------------------------------------------

    def visit_ClassDef(
        self,
        node: ast.ClassDef,
    ):

        name = self._qualified_name(
            node.name
        )

        self._add_node(
            name,
            "class",
        )

        self.scope.append(node.name)

        self.generic_visit(node)

        self.scope.pop()


    def visit_FunctionDef(
        self,
        node: ast.FunctionDef,
    ):

        self._register_function(
            node,
            "function",
        )


    def visit_AsyncFunctionDef(
        self,
        node: ast.AsyncFunctionDef,
    ):

        self._register_function(
            node,
            "async_function",
        )


    def _register_function(
        self,
        node,
        kind: str,
    ):

        name = self._qualified_name(
            node.name
        )

        self._add_node(
            name,
            kind,
        )

        self.scope.append(node.name)

        self.generic_visit(node)

        self.scope.pop()


    # ---------------------------------------------------------
    # CALL GRAPH
    # ---------------------------------------------------------

    def visit_Call(
        self,
        node: ast.Call,
    ):

        caller = (
            ".".join(self.scope)
            if self.scope
            else self.filename
        )

        callee = self._resolve_call(
            node.func
        )

        if callee:

            try:
                evidence = ast.unparse(node)

            except Exception:
                evidence = "<unparse_failed>"


            self.edges.append(
                GraphEdge(
                    source=caller,
                    destination=callee,
                    relationship="CALL",
                    evidence=evidence,
                )
            )


        self.generic_visit(node)


    # ---------------------------------------------------------
    # IMPORTS
    # ---------------------------------------------------------

    def visit_Import(
        self,
        node: ast.Import,
    ):

        for alias in node.names:

            self._add_node(
                alias.name,
                "import",
            )


    def visit_ImportFrom(
        self,
        node: ast.ImportFrom,
    ):

        module = node.module or ""

        for alias in node.names:

            name = (
                f"{module}.{alias.name}"
                if module
                else alias.name
            )

            self._add_node(
                name,
                "import",
            )


    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    def _add_node(
        self,
        identifier: str,
        kind: str,
    ):

        if identifier not in self.nodes:

            self.nodes[identifier] = GraphNode(
                identifier=identifier,
                kind=kind,
                source_file=self.filename,
            )


    def _qualified_name(
        self,
        name: str,
    ) -> str:

        if self.scope:
            return ".".join(
                self.scope + [name]
            )

        return name


    def _resolve_call(
        self,
        node: ast.AST,
    ) -> Optional[str]:

        if isinstance(node, ast.Name):
            return node.id


        if isinstance(node, ast.Attribute):

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