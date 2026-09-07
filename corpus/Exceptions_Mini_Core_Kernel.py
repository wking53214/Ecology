===============================================================================
Module
===============================================================================

Filename:
Exceptions_Mini_Core_Kernel.py

Purpose:
Provides the canonical exception hierarchy for the framework. Every kernel
raises strongly typed exceptions derived from a common base class, enabling
consistent error handling, deterministic failure modes, and clear diagnostic
reporting across the architecture.

Responsibilities:
- Define the framework's root exception.
- Define specialized exception types.
- Support deterministic error categorization.
- Provide immutable error metadata.
- Establish a common error contract for all kernels.

Public Classes:
- KernelError
- ValidationError
- ConfigurationError
- InitializationError
- ProcessingError
- DependencyError
- GraphError
- GovernanceError
- SecurityError
- ErrorContext

Dependencies:
- Python Standard Library
    - dataclasses
    - typing

===============================================================================
Python Source
===============================================================================

"""
Exceptions_Mini_Core_Kernel.py

Canonical exception hierarchy shared by every kernel.

All framework exceptions inherit from KernelError to provide
consistent error handling and structured diagnostics.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class ErrorContext:
    """
    Immutable metadata describing an exception.
    """

    component: str
    operation: str
    details: Mapping[str, Any] | None = None


class KernelError(Exception):
    """
    Base exception for the framework.
    """

    def __init__(
        self,
        message: str,
        context: ErrorContext | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.context = context

    def __str__(self) -> str:
        if self.context is None:
            return self.message

        return (
            f"{self.message} "
            f"[component={self.context.component}, "
            f"operation={self.context.operation}]"
        )


class ValidationError(KernelError):
    """
    Raised when validation fails.
    """


class ConfigurationError(KernelError):
    """
    Raised when configuration is invalid.
    """


class InitializationError(KernelError):
    """
    Raised when a kernel cannot initialize.
    """


class ProcessingError(KernelError):
    """
    Raised during runtime processing failures.
    """


class DependencyError(KernelError):
    """
    Raised when a required dependency is unavailable.
    """


class GraphError(KernelError):
    """
    Raised during graph construction or traversal.
    """


class GovernanceError(KernelError):
    """
    Raised when governance policy validation fails.
    """


class SecurityError(KernelError):
    """
    Raised when a security policy is violated.
    """