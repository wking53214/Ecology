"""
===============================================================================
Module
===============================================================================

Filename:
Audit_Mini_Governance_Kernel.py

Purpose:
Implements the immutable audit governance layer responsible for recording
system actions, validation decisions, and operational events. The Audit Kernel
provides traceability across the framework by creating structured audit
records that support compliance review, forensic analysis, and governance
verification.

Responsibilities:
- Capture operational events.
- Maintain audit history.
- Provide immutable records.
- Support compliance review.
- Enable forensic traceability.

Public Classes:
- AuditRecord
- AuditEngine

Public Interfaces:
- AuditEngine.record()
- AuditEngine.history()

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
Audit_Mini_Governance_Kernel.py

Immutable audit recording subsystem.

Provides governance traceability across framework operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from Exceptions_Mini_Core_Kernel import ValidationError

from Types_Mini_Core_Kernel import (
    KernelComponent,
    KernelMetadata,
)


@dataclass(frozen=True, slots=True)
class AuditRecord:
    """
    Immutable governance audit record.
    """

    event_type: str
    component: str
    details: dict[str, Any]
    timestamp: str


@dataclass(slots=True)
class AuditEngine(KernelComponent):
    """
    Framework audit trail manager.
    """

    _records: list[AuditRecord] = field(
        init=False,
        default_factory=list,
    )

    @property
    def metadata(self) -> KernelMetadata:
        return KernelMetadata(
            name="Audit Mini Governance Kernel",
            version="1.0.0",
            description=(
                "Maintains immutable operational audit records."
            ),
        )

    def record(
        self,
        event_type: str,
        component: str,
        details: dict[str, Any],
    ) -> AuditRecord:
        """
        Create an audit event.
        """

        if not event_type.strip():
            raise ValidationError(
                "Event type cannot be empty."
            )

        if not component.strip():
            raise ValidationError(
                "Component cannot be empty."
            )

        record = AuditRecord(
            event_type=event_type,
            component=component,
            details=dict(details),
            timestamp=datetime.now(
                timezone.utc
            ).isoformat(),
        )

        self._records.append(
            record
        )

        return record

    def history(
        self,
    ) -> tuple[AuditRecord, ...]:
        """
        Return immutable audit history.
        """

        return tuple(
            self._records
        )