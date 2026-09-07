===============================================================================
Module
===============================================================================

Filename:
Utilities_Mini_Core_Kernel.py

Purpose:
Provides shared utility primitives used throughout the Mini Kernel Framework.
This kernel contains reusable deterministic helpers that reduce duplication
across modules while preserving strict separation between business logic and
framework support functions.

Responsibilities:
- Provide common validation utilities.
- Provide deterministic hashing utilities.
- Provide safe dictionary transformation helpers.
- Support framework-wide consistency.
- Reduce duplicate implementation patterns.

Public Classes:
- UtilityEngine

Public Interfaces:
- UtilityEngine.require_non_empty()
- UtilityEngine.safe_hash()
- UtilityEngine.normalize_mapping()

Dependencies:
- Python Standard Library
    - hashlib
    - typing

- Local
    - Types_Mini_Core_Kernel.py
    - Exceptions_Mini_Core_Kernel.py

===============================================================================
Python Source
===============================================================================

"""
Utilities_Mini_Core_Kernel.py

Shared deterministic framework utilities.
"""

from __future__ import annotations

import hashlib

from typing import Any, Mapping

from Exceptions_Mini_Core_Kernel import ValidationError
from Types_Mini_Core_Kernel import (
    KernelComponent,
    KernelMetadata,
)


class UtilityEngine(KernelComponent):
    """
    General framework utility provider.
    """

    @property
    def metadata(self) -> KernelMetadata:
        return KernelMetadata(
            name="Utilities Mini Core Kernel",
            version="1.0.0",
            description=(
                "Provides reusable deterministic framework utilities."
            ),
        )

    @staticmethod
    def require_non_empty(
        value: str,
        field_name: str,
    ) -> str:
        """
        Validate a required string value.
        """

        if not isinstance(value, str):
            raise ValidationError(
                f"{field_name} must be a string."
            )

        normalized = value.strip()

        if not normalized:
            raise ValidationError(
                f"{field_name} cannot be empty."
            )

        return normalized

    @staticmethod
    def safe_hash(
        value: str,
    ) -> str:
        """
        Produce deterministic SHA-256 hash.
        """

        if not isinstance(value, str):
            raise ValidationError(
                "Hash input must be a string."
            )

        return hashlib.sha256(
            value.encode(
                "utf-8"
            )
        ).hexdigest()

    @staticmethod
    def normalize_mapping(
        value: Mapping[str, Any],
    ) -> dict[str, Any]:
        """
        Convert mapping input into a safe dictionary copy.
        """

        if not isinstance(value, Mapping):
            raise ValidationError(
                "Value must implement Mapping."
            )

        return dict(value)