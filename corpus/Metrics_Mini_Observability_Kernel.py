"""
===============================================================================
Module
===============================================================================

Filename:
Metrics_Mini_Observability_Kernel.py

Purpose:
Implements the runtime metrics collection layer responsible for capturing
quantitative system behavior across Mini Kernels. The Metrics Kernel provides
a lightweight observability interface for counters, measurements, and
operational health indicators while maintaining independence from external
monitoring platforms.

Responsibilities:
- Collect runtime measurements.
- Maintain operational counters.
- Provide metric snapshots.
- Support health monitoring.
- Enable external telemetry integration.

Public Classes:
- MetricSnapshot
- MetricsEngine

Public Interfaces:
- MetricsEngine.increment()
- MetricsEngine.record()
- MetricsEngine.snapshot()

Dependencies:
- Python Standard Library
    - dataclasses
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
Metrics_Mini_Observability_Kernel.py

Runtime metrics collection kernel.

Provides deterministic internal telemetry aggregation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict

from Exceptions_Mini_Core_Kernel import ValidationError

from Types_Mini_Core_Kernel import (
    KernelComponent,
    KernelMetadata,
)


@dataclass(frozen=True, slots=True)
class MetricSnapshot:
    """
    Immutable metrics snapshot.
    """

    metrics: dict[str, float]
    timestamp: str


@dataclass(slots=True)
class MetricsEngine(KernelComponent):
    """
    Runtime metrics aggregation engine.
    """

    _metrics: Dict[str, float] = field(
        init=False,
        default_factory=dict,
    )

    @property
    def metadata(self) -> KernelMetadata:
        return KernelMetadata(
            name="Metrics Mini Observability Kernel",
            version="1.0.0",
            description=(
                "Collects and exposes runtime system measurements."
            ),
        )

    def increment(
        self,
        name: str,
        amount: float = 1.0,
    ) -> None:
        """
        Increment a metric counter.
        """

        self._validate_name(name)

        self._metrics[name] = (
            self._metrics.get(name, 0.0)
            + amount
        )

    def record(
        self,
        name: str,
        value: float,
    ) -> None:
        """
        Record a metric value.
        """

        self._validate_name(name)

        self._metrics[name] = value

    def snapshot(
        self,
    ) -> MetricSnapshot:
        """
        Return current metrics state.
        """

        return MetricSnapshot(
            metrics=dict(self._metrics),
            timestamp=datetime.now(
                timezone.utc
            ).isoformat(),
        )

    @staticmethod
    def _validate_name(
        name: str,
    ) -> None:
        """
        Validate metric names.
        """

        if not isinstance(name, str):
            raise ValidationError(
                "Metric name must be a string."
            )

        if not name.strip():
            raise ValidationError(
                "Metric name cannot be empty."
            )