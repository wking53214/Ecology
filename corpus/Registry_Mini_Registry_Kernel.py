"""
===============================================================================
Module
===============================================================================

Filename:
Registry_Mini_Registry_Kernel.py

Purpose:
Implements the framework component registry responsible for maintaining
discoverable kernel metadata, lifecycle state, and dependency relationships.
The Registry Kernel provides a centralized catalog that allows runtime systems
to inspect available capabilities without coupling directly to implementation
details.

Responsibilities:
- Maintain kernel registrations.
- Track kernel metadata.
- Provide discovery capabilities.
- Support runtime inspection.
- Prevent duplicate registrations.

Public Classes:
- RegistryEntry
- ModuleRegistryEngine

Public Interfaces:
- ModuleRegistryEngine.register()
- ModuleRegistryEngine.get()
- ModuleRegistryEngine.describe()
- ModuleRegistryEngine.list()

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
"""
Registry_Mini_Registry_Kernel.py

Kernel discovery and registration subsystem.

Maintains runtime knowledge of available framework components.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from Exceptions_Mini_Core_Kernel import (
    DependencyError,
    ValidationError,
)

from Types_Mini_Core_Kernel import (
    KernelComponent,
    KernelMetadata,
)


@dataclass(frozen=True, slots=True)
class RegistryEntry:
    """
    Immutable registry record.
    """

    identifier: str
    component: KernelComponent
    metadata: KernelMetadata


@dataclass(slots=True)
class ModuleRegistryEngine(KernelComponent):
    """
    Runtime kernel registry.
    """

    _entries: Dict[str, RegistryEntry] = field(
        init=False,
        default_factory=dict,
    )

    @property
    def metadata(self) -> KernelMetadata:
        return KernelMetadata(
            name="Registry Mini Registry Kernel",
            version="1.0.0",
            description=(
                "Provides runtime kernel discovery and registration."
            ),
        )

    def register(
        self,
        component: KernelComponent,
        identifier: str | None = None,
    ) -> RegistryEntry:
        """
        Register a framework kernel.
        """

        if not isinstance(
            component,
            KernelComponent,
        ):
            raise ValidationError(
                "Component must implement KernelComponent."
            )

        key = identifier or component.metadata.name

        if not key.strip():
            raise ValidationError(
                "Registry identifier cannot be empty."
            )

        if key in self._entries:
            raise DependencyError(
                f"Duplicate kernel registration: {key}"
            )

        entry = RegistryEntry(
            identifier=key,
            component=component,
            metadata=component.metadata,
        )

        self._entries[key] = entry

        return entry

    def get(
        self,
        identifier: str,
    ) -> KernelComponent:
        """
        Retrieve a registered kernel.
        """

        if identifier not in self._entries:
            raise DependencyError(
                f"Unknown kernel: {identifier}"
            )

        return self._entries[
            identifier
        ].component

    def describe(
        self,
        identifier: str,
    ) -> KernelMetadata:
        """
        Return kernel metadata.
        """

        if identifier not in self._entries:
            raise DependencyError(
                f"Unknown kernel: {identifier}"
            )

        return self._entries[
            identifier
        ].metadata

    def list(
        self,
    ) -> list[str]:
        """
        List registered kernels.
        """

        return sorted(
            self._entries.keys()
        )