===============================================================================
Module
===============================================================================

Filename:
Integration_Mini_Integration_Kernel.py

Purpose:
Provides the integration boundary between independent Mini Kernels. This module
coordinates kernel registration, lifecycle management, and controlled
communication between components while preserving architectural decoupling.
The Integration Kernel acts as the composition layer that assembles the
framework into an operational system.

Responsibilities:
- Register framework kernels.
- Resolve kernel dependencies.
- Provide controlled kernel access.
- Coordinate initialization order.
- Maintain integration boundaries.

Public Classes:
- KernelRegistration
- IntegrationEngine

Public Interfaces:
- IntegrationEngine.register()
- IntegrationEngine.resolve()
- IntegrationEngine.list_components()

Dependencies:
- Python Standard Library
    - dataclasses
    - typing

- Local
    - Types_Mini_Core_Kernel.py
    - Exceptions_Mini_Core_Kernel.py

===============================================================================
Python Source
===============================================================================

"""
Integration_Mini_Integration_Kernel.py

Framework integration and composition kernel.

Provides controlled assembly of independent mini kernels.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from Exceptions_Mini_Core_Kernel import (
    DependencyError,
    ValidationError,
)

from Types_Mini_Core_Kernel import (
    KernelComponent,
    KernelMetadata,
)


@dataclass(frozen=True, slots=True)
class KernelRegistration:
    """
    Immutable kernel registration record.
    """

    name: str
    instance: KernelComponent


@dataclass(slots=True)
class IntegrationEngine(KernelComponent):
    """
    Kernel composition manager.
    """

    _registry: Dict[str, KernelComponent] = field(
        init=False,
        default_factory=dict,
    )

    @property
    def metadata(self) -> KernelMetadata:
        return KernelMetadata(
            name="Integration Mini Integration Kernel",
            version="1.0.0",
            description=(
                "Coordinates registration and communication "
                "between framework kernels."
            ),
        )

    def register(
        self,
        registration: KernelRegistration,
    ) -> None:
        """
        Register a kernel component.
        """

        if not isinstance(
            registration,
            KernelRegistration,
        ):
            raise ValidationError(
                "Invalid kernel registration."
            )

        if registration.name in self._registry:
            raise DependencyError(
                f"Kernel already registered: {registration.name}"
            )

        self._registry[
            registration.name
        ] = registration.instance

    def resolve(
        self,
        name: str,
    ) -> KernelComponent:
        """
        Resolve a registered kernel.
        """

        if name not in self._registry:
            raise DependencyError(
                f"Kernel not found: {name}"
            )

        return self._registry[name]

    def list_components(
        self,
    ) -> list[str]:
        """
        Return registered kernel names.
        """

        return sorted(
            self._registry.keys()
        )