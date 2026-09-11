"""
===============================================================================
Module
===============================================================================

Filename:
API_Mini_Interface_Kernel.py

Purpose:
Implements the external interface boundary for the Mini Kernel Framework. The
API Kernel provides a controlled communication layer between external callers
and internal framework services while preserving validation, governance, and
execution isolation. It converts external requests into structured internal
operations.

Responsibilities:
- Receive external framework requests.
- Validate request structures.
- Route requests into kernel execution flows.
- Provide standardized responses.
- Maintain interface isolation.

Public Classes:
- APIRequest
- APIResponse
- APIInterfaceEngine

Public Interfaces:
- APIInterfaceEngine.handle()

Dependencies:
- Python Standard Library
    - dataclasses
    - typing

- Local
    - Types_Mini_Core_Kernel.py
    - Exceptions_Mini_Core_Kernel.py
    - Runtime_Mini_Execution_Kernel.py

===============================================================================
Python Source
===============================================================================

"""
"""
API_Mini_Interface_Kernel.py

Framework external interface boundary.

Provides validated request and response handling.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from Exceptions_Mini_Core_Kernel import ValidationError

from Runtime_Mini_Execution_Kernel import RuntimeEngine

from Types_Mini_Core_Kernel import (
    KernelComponent,
    KernelMetadata,
)


@dataclass(frozen=True, slots=True)
class APIRequest:
    """
    Immutable API request envelope.
    """

    action: str
    payload: dict[str, Any]


@dataclass(frozen=True, slots=True)
class APIResponse:
    """
    Immutable API response envelope.
    """

    status: str
    result: Any


@dataclass(slots=True)
class APIInterfaceEngine(KernelComponent):
    """
    External communication gateway.
    """

    runtime: RuntimeEngine

    @property
    def metadata(self) -> KernelMetadata:
        return KernelMetadata(
            name="API Mini Interface Kernel",
            version="1.0.0",
            description=(
                "Provides controlled external framework interaction."
            ),
        )

    async def handle(
        self,
        request: APIRequest,
        operation: Callable[..., Any],
    ) -> APIResponse:
        """
        Process an external request.
        """

        if not isinstance(
            request,
            APIRequest,
        ):
            raise ValidationError(
                "Invalid API request."
            )

        if not request.action.strip():
            raise ValidationError(
                "API action cannot be empty."
            )

        result = await self.runtime.execute(
            operation,
            request.payload,
        )

        return APIResponse(
            status="SUCCESS",
            result=result,
        )