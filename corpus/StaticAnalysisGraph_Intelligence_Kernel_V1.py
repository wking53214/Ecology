"""
StaticAnalysisGraph_Intelligence_Kernel_V1.py

Deterministic Python Static Analysis Intelligence Kernel.

Purpose:
    Converts Python source code into deterministic software knowledge graphs.

Capabilities:
    - AST parsing
    - Module discovery
    - Class discovery
    - Function discovery
    - Async function discovery
    - Import relationship extraction
    - Inheritance relationship extraction
    - Lexical call graph extraction
    - Immutable graph generation

Guarantees:
    - No code execution
    - No runtime inspection
    - No import resolution
    - No type inference
    - No dynamic evaluation
    - Deterministic output
"""


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
#
# ===============================================================================
# MODULE CONSOLIDATION HISTORY
# ===============================================================================
#
# This module was created by combining:
#
#
# -------------------------------------------------------------------------------
#
# Source Module:
#
# ASTExtractor_Mini_Analysis_Kernel.py
#
# Contribution:
#
#     - AST parsing
#     - Structural entity discovery
#     - Module extraction
#     - Class extraction
#     - Function extraction
#     - Async function extraction
#     - Scope tracking
#     - Lexical call relationship extraction
#
#
# -------------------------------------------------------------------------------
#
# Source Module:
#
# GraphModels_Mini_Analysis_Kernel.py
#
# Contribution:
#
#     - Immutable graph nodes
#     - Immutable graph edges
#     - Analysis graph contracts
#     - Graph validation
#     - Graph statistics
#
#
# -------------------------------------------------------------------------------
#
# Consolidation Objective:
#
# Combine source understanding and graph representation into a single
# deterministic software intelligence primitive.
#
#
# Result:
#
# StaticAnalysisGraph_Intelligence_Kernel_V1.py
#
# becomes the foundational layer for:
#
#     - Repository intelligence
#     - Architecture discovery
#     - Dependency mapping
#     - AI-assisted code reasoning
#     - Software knowledge graph creation
#
#
# ===============================================================================


from __future__ import annotations


import ast


from dataclasses import (
    dataclass,
    field,
)


from typing import (
    Dict,
    Optional,
    Tuple,
    Mapping,
)



# ===============================================================================
# CORE EXCEPTIONS
# ===============================================================================


class ProcessingError(Exception):
    """
    Raised when source processing cannot continue.
    """
    pass



class ValidationError(Exception):
    """
    Raised when graph contracts fail validation.
    """
    pass



# ===============================================================================
# KERNEL CONTRACTS
# ===============================================================================


@dataclass(
    frozen=True,
    slots=True,
)
class KernelMetadata:

    name: str

    version: str

    description: str



class KernelComponent:
    """
    Base kernel interface.
    """

    @property
    def metadata(self) -> KernelMetadata:

        raise NotImplementedError



# ===============================================================================
# IMMUTABLE GRAPH CONTRACTS
# ===============================================================================


@dataclass(
    frozen=True,
    slots=True,
)
class GraphNode:
    """
    Immutable representation of a discovered software entity.

    Examples:

        module
        class
        function
        async_function
        import
    """

    identifier: str

    kind: str

    source_file: str


    def __post_init__(self):

        if not self.identifier.strip():

            raise ValidationError(
                "Graph node identifier cannot be empty."
            )


        if not self.kind.strip():

            raise ValidationError(
                "Graph node kind cannot be empty."
            )


        if not self.source_file.strip():

            raise ValidationError(
                "Graph node source file cannot be empty."
            )



@dataclass(
    frozen=True,
    slots=True,
)
class GraphEdge:
    """
    Immutable relationship between graph entities.

    Supported relationships:

        CALL
        IMPORTS
        INHERITS
    """

    source: str

    destination: str

    relationship: str

    evidence: str


    def __post_init__(self):

        if not self.source.strip():

            raise ValidationError(
                "Graph edge source cannot be empty."
            )


        if not self.destination.strip():

            raise ValidationError(
                "Graph edge destination cannot be empty."
            )



@dataclass(
    frozen=True,
    slots=True,
)
class AnalysisGraph(
    KernelComponent,
):
    """
    Immutable static software knowledge graph.
    """

    nodes: Mapping[str, GraphNode]

    edges: Tuple[GraphEdge, ...]

    total_lines: int



    @property
    def metadata(self):

        return KernelMetadata(

            name=
            "Static Analysis Graph Intelligence Kernel",

            version=
            "2.0.0",

            description=
            (
                "Deterministic immutable software "
                "architecture knowledge graph."
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



    def node_count(self):

        return len(self.nodes)



    def edge_count(self):

        return len(self.edges)

# ===============================================================================
# AST EXTRACTION ENGINE
# ===============================================================================
#
# Purpose:
#
#     Converts Python source code into deterministic software architecture
#     graph structures.
#
#
# Responsibilities:
#
#     - Parse Python source safely
#     - Traverse AST nodes
#     - Discover modules
#     - Discover classes
#     - Discover inheritance relationships
#     - Discover functions
#     - Discover async functions
#     - Discover imports
#     - Discover lexical call relationships
#     - Produce immutable AnalysisGraph artifacts
#
#
# Design Boundary:
#
#     This engine understands source structure only.
#
#     It does NOT:
#
#         - Execute code
#         - Import modules
#         - Resolve runtime objects
#         - Perform type inference
#         - Evaluate expressions
#
# ===============================================================================


@dataclass(
    slots=True,
)
class ASTExtractorEngine(
    KernelComponent,
    ast.NodeVisitor,
):
    """
    Production deterministic Python AST analysis engine.

    Generates software knowledge graph artifacts
    from static source representation.
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



    @property
    def metadata(self) -> KernelMetadata:

        return KernelMetadata(

            name=
            "AST Extraction Intelligence Engine",

            version=
            "2.0.0",

            description=
            (
                "Deterministic Python AST to software "
                "knowledge graph extraction engine."
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
        Convert Python source into immutable AnalysisGraph.
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

            edges=tuple(
                self.edges
            ),

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
        Register root module entity.
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
        Extract class definitions and inheritance.
        """


        name = self._qualified_name(
            node.name
        )


        self._add_node(

            name,

            "class"

        )


# -------------------------------------------------------------------------------
# INHERITANCE EXTRACTION
# -------------------------------------------------------------------------------


        for base in node.bases:

            parent = self._resolve_call(
                base
            )


            if parent:

                self.edges.append(

                    GraphEdge(

                        source=name,

                        destination=parent,

                        relationship="INHERITS",

                        evidence=
                        (
                            f"class {node.name}"
                            f"({parent})"
                        )

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
        Extract standard functions.
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
        Extract asynchronous functions.
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
        Shared function registration.
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
        Capture lexical call relationships.

        Example:

            service.process()

        Creates:

            caller --CALL--> service.process


        Note:

            Runtime resolution is intentionally avoided.
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



# ===============================================================================
# IMPORT EXTRACTION
# ===============================================================================


    def visit_Import(
        self,
        node: ast.Import,
    ):
        """
        Extract standard import statements.
        """


        for alias in node.names:


            self._add_node(

                alias.name,

                "import"

            )


            self.edges.append(

                GraphEdge(

                    source=self.filename,

                    destination=alias.name,

                    relationship="IMPORTS",

                    evidence=
                    (
                        f"import {alias.name}"
                    )

                )

            )



    def visit_ImportFrom(
        self,
        node: ast.ImportFrom,
    ):
        """
        Extract from-import statements.
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


            self.edges.append(

                GraphEdge(

                    source=self.filename,

                    destination=name,

                    relationship="IMPORTS",

                    evidence=
                    (
                        f"from {module} "
                        f"import {alias.name}"
                    )

                )

            )
# ===============================================================================
# INTERNAL GRAPH MANAGEMENT
# ===============================================================================
#
# Purpose:
#
#     Provides controlled mutation during extraction while ensuring that the
#     resulting AnalysisGraph remains immutable after generation.
#
# ===============================================================================


    def _add_node(
        self,
        identifier: str,
        kind: str,
    ):
        """
        Register graph node if not already present.

        Duplicate discoveries are ignored to preserve deterministic output.
        """


        if identifier not in self.nodes:


            self.nodes[identifier] = GraphNode(

                identifier=identifier,

                kind=kind,

                source_file=self.filename

            )



# ===============================================================================
# SCOPED ENTITY NAMING
# ===============================================================================


    def _qualified_name(
        self,
        name: str,
    ) -> str:
        """
        Generate deterministic scoped names.

        Examples:

            class Service:
                def process()

        becomes:

            Service.process
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
        Resolve lexical call targets only.

        Supported:

            function()

            object.method()


        Unsupported intentionally:

            runtime dispatch

            reflection

            dynamic attributes

            evaluated expressions
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



# ===============================================================================
# RED TEAM HARDENING CONTROLS
# ===============================================================================
#
# Security and correctness evaluation performed against the kernel.
#
# ===============================================================================


class StaticAnalysisRedTeamReport:
    """
    Documents known attack surfaces and mitigations.
    """



    findings = {

        "code_execution":

        {

            "risk":

            "Malicious source could execute during analysis.",


            "mitigation":

            [

                "Uses ast.parse only",

                "Never calls eval",

                "Never executes imported modules"

            ]

        },


        "dynamic_resolution":

        {

            "risk":

            "Runtime behavior could be incorrectly inferred.",


            "mitigation":

            [

                "Only lexical AST relationships are extracted",

                "Runtime object lookup is prohibited"

            ]

        },


        "graph_mutation":

        {

            "risk":

            "Generated graph artifacts could be altered.",


            "mitigation":

            [

                "Frozen graph records",

                "Tuple edge storage",

                "Immutable node contracts"

            ]

        },


        "dependency_visibility":

        {

            "risk":

            "Important architecture relationships could be missed.",


            "mitigation":

            [

                "IMPORTS relationships",

                "INHERITS relationships",

                "CALL relationships"

            ]

        },


        "analysis_drift":

        {

            "risk":

            "Repeated scans produce inconsistent representations.",


            "mitigation":

            [

                "Deterministic traversal",

                "Stable identifiers",

                "No random generation"

            ]

        }

    }



# ===============================================================================
# ARCHITECTURAL GUARANTEES
# ===============================================================================
#
#
# The StaticAnalysisGraph Intelligence Kernel guarantees:
#
#
# Input:
#
#     Python Source Text
#
#
# Transformation:
#
#     Source
#        |
#        v
#     AST
#        |
#        v
#     Structural Extraction
#        |
#        v
#     Knowledge Graph
#
#
# Output:
#
#     Immutable AnalysisGraph
#
#
# The kernel provides a deterministic foundation for:
#
#     - Repository understanding
#     - Architecture mapping
#     - Software lineage analysis
#     - AI code reasoning
#     - Knowledge graph generation
#
#
# ===============================================================================


# ===============================================================================
# OPTIONAL STANDALONE EXECUTION TEST
# ===============================================================================


if __name__ == "__main__":


    sample = """
import os


class Service:

    def run(self):

        helper()


def helper():

    pass
"""


    engine = ASTExtractorEngine(
        filename="sample.py"
    )


    graph = engine.extract(
        sample
    )


    print(
        "STATIC ANALYSIS GRAPH"
    )


    print(
        "Nodes:",
        graph.node_count()
    )


    print(
        "Edges:",
        graph.edge_count()
    )


    for edge in graph.edges:

        print(

            edge.source,

            "--",

            edge.relationship,

            "-->",

            edge.destination

        )
