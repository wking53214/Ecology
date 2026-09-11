"""
===============================================================================
Module
===============================================================================

Filename:
ConfigurationLoader_Mini_Core_Kernel.py

Purpose:
Implements the centralized configuration management layer responsible for
loading, validating, and distributing runtime configuration values across the
Mini Kernel Framework. The Configuration Loader Kernel provides a controlled
configuration boundary that prevents individual modules from directly managing
environmental settings or runtime parameters.

Responsibilities:
- Manage framework configuration values.
- Validate required configuration fields.
- Provide immutable configuration snapshots.
- Separate configuration from execution logic.
- Support dependency injection throughout the framework.

Public Classes:
- KernelConfiguration
- ConfigurationEngine

Public Interfaces:
- ConfigurationEngine.load()
- ConfigurationEngine.get()
- ConfigurationEngine.snapshot()

Dependencies:
- Python Standard Library
    - dataclasses
    - os
    - typing

- Local
    - Types_Mini_Core_Kernel.py
    - Exceptions_Mini_Core_Kernel.py

===============================================================================
Python Source
===============================================================================

"""
"""
ConfigurationLoader_Mini_Core_Kernel.py

Central configuration management kernel.

Provides validated runtime configuration access.
"""

from __future__ import annotations

import os

from dataclasses import dataclass, field
from typing import Dict, Mapping, Optional

from Exceptions_Mini_Core_Kernel import ValidationError

from Types_Mini_Core_Kernel import (
    KernelComponent,
    KernelMetadata,
)


@dataclass(frozen=True, slots=True)
class KernelConfiguration:
    """
    Immutable runtime configuration snapshot.
    """

    values: Mapping[str, str]


@dataclass(slots=True)
class ConfigurationEngine(KernelComponent):
    """
    Framework configuration manager.
    """

    environment: Optional[Mapping[str, str]] = None

    _values: Dict[str, str] = field(
        init=False,
        default_factory=dict,
    )

    @property
    def metadata(self) -> KernelMetadata:
        return KernelMetadata(
            name="Configuration Loader Mini Core Kernel",
            version="1.0.0",
            description=(
                "Provides validated runtime configuration management."
            ),
        )

    def load(
        self,
        required_keys: tuple[str, ...] = (),
    ) -> KernelConfiguration:
        """
        Load and validate configuration values.
        """

        source = (
            self.environment
            if self.environment is not None
            else os.environ
        )

        for key in required_keys:

            if key not in source:
                raise ValidationError(
                    f"Missing required configuration: {key}"
                )

        self._values = {
            key: str(value)
            for key, value in source.items()
        }

        return self.snapshot()

    def get(
        self,
        key: str,
        default: Optional[str] = None,
    ) -> Optional[str]:
        """
        Retrieve a configuration value.
        """

        if not isinstance(key, str):
            raise ValidationError(
                "Configuration key must be a string."
            )

        return self._values.get(
            key,
            default,
        )

    def snapshot(
        self,
    ) -> KernelConfiguration:
        """
        Return immutable configuration state.
        """

        return KernelConfiguration(
            values=dict(self._values)
        )