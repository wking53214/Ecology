"""
===============================================================================
Module
===============================================================================

Filename:
Logging_Mini_Observability_Kernel.py

Purpose:
Provides the centralized observability layer for the Mini Kernel Framework.
This kernel establishes structured logging primitives that allow every module
to emit consistent diagnostic events, operational metadata, and execution
telemetry while avoiding direct coupling to a specific logging backend.

Responsibilities:
- Provide structured framework logging.
- Standardize kernel event reporting.
- Support severity-based diagnostics.
- Maintain dependency injection compatibility.
- Enable operational observability across modules.

Public Classes:
- LogEvent
- ObservabilityLogger

Public Interfaces:
- ObservabilityLogger.emit()
- ObservabilityLogger.info()
- ObservabilityLogger.warning()
- ObservabilityLogger.error()

Dependencies:
- Python Standard Library
    - dataclasses
    - logging
    - datetime
    - typing

- Local
    - Types_Mini_Core_Kernel.py
    - Exceptions_Mini_Core_Kernel.py

===============================================================================
Python Source
===============================================================================

"""
"""
Logging_Mini_Observability_Kernel.py

Structured observability kernel.

Provides consistent logging behavior across all framework components.
"""

from __future__ import annotations

import logging

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping

from Types_Mini_Core_Kernel import (
    KernelComponent,
    KernelMetadata,
)


@dataclass(frozen=True, slots=True)
class LogEvent:
    """
    Immutable structured log event.
    """

    level: str
    component: str
    message: str
    timestamp: str
    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )


@dataclass(slots=True)
class ObservabilityLogger(KernelComponent):
    """
    Structured framework observability logger.
    """

    component_name: str
    logger: logging.Logger = field(
        default_factory=lambda: logging.getLogger(
            "MiniKernelFramework"
        )
    )

    @property
    def metadata(self) -> KernelMetadata:
        return KernelMetadata(
            name="Logging Mini Observability Kernel",
            version="1.0.0",
            description=(
                "Provides structured operational telemetry."
            ),
        )

    def emit(
        self,
        event: LogEvent,
    ) -> None:
        """
        Emit a structured logging event.
        """

        message = (
            f"[{event.component}] "
            f"{event.message} "
            f"| metadata={dict(event.metadata)}"
        )

        level = event.level.upper()

        if level == "ERROR":
            self.logger.error(message)

        elif level == "WARNING":
            self.logger.warning(message)

        else:
            self.logger.info(message)

    def info(
        self,
        message: str,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        """
        Emit informational telemetry.
        """

        self.emit(
            LogEvent(
                level="INFO",
                component=self.component_name,
                message=message,
                timestamp=self._timestamp(),
                metadata=metadata or {},
            )
        )

    def warning(
        self,
        message: str,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        """
        Emit warning telemetry.
        """

        self.emit(
            LogEvent(
                level="WARNING",
                component=self.component_name,
                message=message,
                timestamp=self._timestamp(),
                metadata=metadata or {},
            )
        )

    def error(
        self,
        message: str,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        """
        Emit error telemetry.
        """

        self.emit(
            LogEvent(
                level="ERROR",
                component=self.component_name,
                message=message,
                timestamp=self._timestamp(),
                metadata=metadata or {},
            )
        )

    @staticmethod
    def _timestamp() -> str:
        """
        Return UTC ISO-8601 timestamp.
        """

        return datetime.now(
            timezone.utc
        ).isoformat()