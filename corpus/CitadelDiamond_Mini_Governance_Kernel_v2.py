===============================================================================
Module
===============================================================================

Filename:
CitadelRouter_Mini_Routing_Kernel.py

Purpose:
Implements the governed routing orchestration layer responsible for directing
incoming requests through integrity validation and output processing pipelines.
The Citadel Router Kernel coordinates governance checks and execution flow
while preserving modular separation between validation, generation, and
routing responsibilities.

Responsibilities:
- Route execution requests.
- Apply governance validation before processing.
- Coordinate processor execution.
- Maintain dependency injection boundaries.
- Provide deterministic routing outcomes.

Public Classes:
- RoutingResult
- CitadelRouterEngine

Public Interfaces:
- CitadelRouterEngine.route()

Dependencies:
- Python Standard Library
    - dataclasses
    - typing

- Local
    - CitadelDiamond_Mini_Governance_Kernel.py
    - CitadelProcessor_Mini_Validation_Kernel.py
    - Exceptions_Mini_Core_Kernel.py
    - Types_Mini_Core_Kernel.py

===============================================================================
Python Source
===============================================================================

"""
CitadelRouter_Mini_Routing_Kernel.py

Governed routing orchestration kernel.

Coordinates validation and execution pipelines.
"""

from __future__ import annotations

from dataclasses import dataclass

from CitadelDiamond_Mini_Governance_Kernel import (
    CitadelDiamondEngine,
)
from CitadelProcessor_Mini_Validation_Kernel import (
    CitadelProcessorEngine,
)
from Exceptions_Mini_Core_Kernel import ValidationError
from Types_Mini_Core_Kernel import (
    KernelComponent,
    KernelMetadata,
)


@dataclass(frozen=True, slots=True)
class RoutingResult:
    """
    Immutable routing response.
    """

    status: str
    output: str | None


@dataclass(slots=True)
class CitadelRouterEngine(KernelComponent):
    """
    Main governance-aware routing engine.
    """

    governance: CitadelDiamondEngine
    processor: CitadelProcessorEngine

    @property
    def metadata(self) -> KernelMetadata:
        return KernelMetadata(
            name="Citadel Router Mini Routing Kernel",
            version="1.0.0",
            description=(
                "Routes requests through governance and validation layers."
            ),
        )

    async def route(
        self,
        request: str,
    ) -> RoutingResult:
        """
        Route a request through the governed execution pipeline.
        """

        if not isinstance(request, str):
            raise ValidationError(
                "Router request must be a string."
            )

        validation = self.governance.validate(
            request
        )

        if not validation.accepted:
            return RoutingResult(
                status=validation.status,
                output=None,
            )

        output = await self.processor.execute(
            request
        )

        return RoutingResult(
            status="COMPLETED",
            output=output,
        )