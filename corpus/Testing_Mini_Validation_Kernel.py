"""
===============================================================================
Module
===============================================================================

Filename:
Testing_Mini_Validation_Kernel.py

Purpose:
Implements the framework validation harness responsible for verifying kernel
contracts, runtime readiness, and component integrity. The Testing Kernel
provides deterministic validation utilities that allow the Mini Kernel
Framework to evaluate whether individual modules conform to architectural
expectations before deployment.

Responsibilities:
- Validate kernel implementations.
- Verify required interfaces.
- Execute deterministic health checks.
- Produce validation reports.
- Support continuous integration testing.

Public Classes:
- ValidationReport
- KernelValidationEngine

Public Interfaces:
- KernelValidationEngine.validate_component()
- KernelValidationEngine.validate_registry()

Dependencies:
- Python Standard Library
    - dataclasses
    - typing

- Local
    - Registry_Mini_Registry_Kernel.py
    - Types_Mini_Core_Kernel.py
    - Exceptions_Mini_Core_Kernel.py

===============================================================================
Python Source
===============================================================================

"""
"""
Testing_Mini_Validation_Kernel.py

Framework validation and health testing subsystem.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from Exceptions_Mini_Core_Kernel import ValidationError

from Registry_Mini_Registry_Kernel import (
    ModuleRegistryEngine,
)

from Types_Mini_Core_Kernel import (
    KernelComponent,
    KernelMetadata,
)


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """
    Immutable validation result.
    """

    component: str
    passed: bool
    findings: tuple[str, ...]


class KernelValidationEngine(KernelComponent):
    """
    Validates framework kernel compliance.
    """

    @property
    def metadata(self) -> KernelMetadata:
        return KernelMetadata(
            name="Testing Mini Validation Kernel",
            version="1.0.0",
            description=(
                "Validates Mini Kernel Framework components."
            ),
        )

    def validate_component(
        self,
        component: KernelComponent,
    ) -> ValidationReport:
        """
        Validate a single kernel component.
        """

        if not isinstance(
            component,
            KernelComponent,
        ):
            raise ValidationError(
                "Component must implement KernelComponent."
            )

        findings: List[str] = []

        metadata = component.metadata

        if not metadata.name:
            findings.append(
                "Missing component name."
            )

        if not metadata.version:
            findings.append(
                "Missing component version."
            )

        return ValidationReport(
            component=metadata.name,
            passed=len(findings) == 0,
            findings=tuple(findings),
        )

    def validate_registry(
        self,
        registry: ModuleRegistryEngine,
    ) -> list[ValidationReport]:
        """
        Validate all registered kernels.
        """

        reports: list[ValidationReport] = []

        for identifier in registry.list():

            component = registry.get(
                identifier
            )

            reports.append(
                self.validate_component(
                    component
                )
            )

        return reports