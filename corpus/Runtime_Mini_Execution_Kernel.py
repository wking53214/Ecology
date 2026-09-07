===============================================================================
Module
===============================================================================

Filename:
Runtime_Mini_Execution_Kernel.py

Purpose:
Implements the runtime execution coordinator responsible for managing the
operational lifecycle of the Mini Kernel Framework. The Runtime Kernel
initializes registered components, validates system readiness, and coordinates
controlled execution while maintaining separation between orchestration and
individual kernel logic.

Responsibilities:
- Manage framework startup lifecycle.
- Validate registered components.
- Coordinate runtime execution.
- Provide system readiness status.
- Maintain execution boundaries.

Public Classes:
- RuntimeState
- RuntimeEngine

Public Interfaces:
- RuntimeEngine.initialize()
- RuntimeEngine.execute()
- RuntimeEngine.status()

Dependencies:
- Python Standard Library
    - dataclasses
    - enum
    - typing

- Local
    - Registry_Mini_Registry_Kernel.py
    - Types_Mini_Core_Kernel.py
    - Exceptions_Mini_Core_Kernel.py

===============================================================================
Python Source
===============================================================================

"""
Runtime_Mini_Execution_Kernel.py

Framework runtime execution coordinator.

Controls lifecycle and operational readiness.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable

from Exceptions_Mini_Core_Kernel import (
    DependencyError,
    ValidationError,
)

from Registry_Mini_Registry_Kernel import (
    ModuleRegistryEngine,
)

from Types_Mini_Core_Kernel import (
    KernelComponent,
    KernelMetadata,
)


class RuntimeState(Enum):
    """
    Runtime lifecycle states.
    """

    CREATED = auto()
    INITIALIZED = auto()
    RUNNING = auto()
    FAILED = auto()
    STOPPED = auto()


@dataclass(slots=True)
class RuntimeEngine(KernelComponent):
    """
    Framework runtime lifecycle manager.
    """

    registry: ModuleRegistryEngine

    state: RuntimeState = RuntimeState.CREATED

    @property
    def metadata(self) -> KernelMetadata:
        return KernelMetadata(
            name="Runtime Mini Execution Kernel",
            version="1.0.0",
            description=(
                "Controls framework lifecycle and execution state."
            ),
        )

    def initialize(
        self,
    ) -> None:
        """
        Validate runtime readiness.
        """

        components = self.registry.list()

        if not components:
            raise DependencyError(
                "Runtime requires registered kernels."
            )

        self.state = RuntimeState.INITIALIZED

    async def execute(
        self,
        operation: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a controlled runtime operation.
        """

        if self.state != RuntimeState.INITIALIZED:
            raise ValidationError(
                "Runtime must be initialized before execution."
            )

        self.state = RuntimeState.RUNNING

        try:
            result = operation(
                *args,
                **kwargs,
            )

            self.state = RuntimeState.INITIALIZED

            return result

        except Exception:
            self.state = RuntimeState.FAILED
            raise

    def status(
        self,
    ) -> RuntimeState:
        """
        Return current runtime state.
        """

        return self.state