"""
===============================================================================
Module
===============================================================================

Filename:
Security_Mini_Governance_Kernel.py

Purpose:
Implements the security governance boundary responsible for enforcing runtime
access validation, integrity checks, and defensive controls across the Mini
Kernel Framework. The Security Kernel provides centralized protection policies
without coupling individual modules to security implementation details.

Responsibilities:
- Validate execution identities.
- Enforce security policy rules.
- Provide integrity verification.
- Support fail-closed security decisions.
- Maintain security isolation between kernels.

Public Classes:
- SecurityDecision
- SecurityEngine

Public Interfaces:
- SecurityEngine.authorize()
- SecurityEngine.verify_integrity()

Dependencies:
- Python Standard Library
    - dataclasses
    - hashlib

- Local
    - Types_Mini_Core_Kernel.py
    - Exceptions_Mini_Core_Kernel.py

===============================================================================
Python Source
===============================================================================

"""
"""
Security_Mini_Governance_Kernel.py

Security governance enforcement kernel.

Provides centralized authorization and integrity validation controls.
"""

from __future__ import annotations

import hashlib

from dataclasses import dataclass

from Exceptions_Mini_Core_Kernel import ValidationError

from Types_Mini_Core_Kernel import (
    KernelComponent,
    KernelMetadata,
)


@dataclass(frozen=True, slots=True)
class SecurityDecision:
    """
    Immutable security decision result.
    """

    allowed: bool
    reason: str


@dataclass(slots=True)
class SecurityEngine(KernelComponent):
    """
    Runtime security governance engine.
    """

    trusted_identity: str = "system"

    @property
    def metadata(self) -> KernelMetadata:
        return KernelMetadata(
            name="Security Mini Governance Kernel",
            version="1.0.0",
            description=(
                "Provides authorization and integrity governance controls."
            ),
        )

    def authorize(
        self,
        identity: str,
    ) -> SecurityDecision:
        """
        Validate execution identity.
        """

        if not isinstance(identity, str):
            raise ValidationError(
                "Identity must be a string."
            )

        if identity != self.trusted_identity:
            return SecurityDecision(
                allowed=False,
                reason="Unauthorized execution identity.",
            )

        return SecurityDecision(
            allowed=True,
            reason="Identity authorized.",
        )

    def verify_integrity(
        self,
        payload: str,
        expected_hash: str,
    ) -> SecurityDecision:
        """
        Verify payload integrity using SHA-256.
        """

        if not isinstance(payload, str):
            raise ValidationError(
                "Payload must be a string."
            )

        calculated_hash = hashlib.sha256(
            payload.encode("utf-8")
        ).hexdigest()

        if calculated_hash != expected_hash:
            return SecurityDecision(
                allowed=False,
                reason="Integrity verification failed.",
            )

        return SecurityDecision(
            allowed=True,
            reason="Integrity verification passed.",
        )