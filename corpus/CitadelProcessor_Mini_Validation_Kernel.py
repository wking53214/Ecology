"""
===============================================================================
Module
===============================================================================

Filename:
CitadelProcessor_Mini_Validation_Kernel.py

Purpose:
Implements the governed execution validation pipeline responsible for
processing generated outputs through deterministic quality and policy checks.
The Citadel Processor Kernel manages retry behavior, duplicate detection, and
validation filtering before allowing results to continue through the system.

Responsibilities:
- Process generated outputs.
- Detect duplicate responses.
- Apply validation rules.
- Manage bounded retry execution.
- Provide deterministic failure states.

Public Classes:
- OutputValidationResult
- CitadelProcessorEngine

Public Interfaces:
- CitadelProcessorEngine.execute()
- CitadelProcessorEngine.validate_output()

Dependencies:
- Python Standard Library
    - dataclasses
    - typing
    - asyncio
    - re

- Local
    - Exceptions_Mini_Core_Kernel.py
    - Types_Mini_Core_Kernel.py

===============================================================================
Python Source
===============================================================================

"""
"""
CitadelProcessor_Mini_Validation_Kernel.py

Governed output validation pipeline.

Controls generated output acceptance using deterministic validation rules.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Awaitable, Callable, Set

from Exceptions_Mini_Core_Kernel import ValidationError
from Types_Mini_Core_Kernel import (
    KernelComponent,
    KernelMetadata,
)


GeneratorFunction = Callable[[str], Awaitable[str]]


@dataclass(frozen=True, slots=True)
class OutputValidationResult:
    """
    Immutable output validation result.
    """

    accepted: bool
    reason: str


@dataclass(slots=True)
class CitadelProcessorEngine(KernelComponent):
    """
    Output governance and validation processor.
    """

    generator: GeneratorFunction
    max_retries: int = 5

    _seen_outputs: Set[str] = field(
        init=False,
        default_factory=set,
    )

    blocked_patterns: tuple[str, ...] = (
        r"\b(i|me|my|mine|myself)\b",
        r"\b(may|might|could|possibly)\b",
    )

    def __post_init__(self) -> None:
        if self.max_retries <= 0:
            raise ValidationError(
                "max_retries must be greater than zero."
            )

    @property
    def metadata(self) -> KernelMetadata:
        return KernelMetadata(
            name="Citadel Processor Mini Validation Kernel",
            version="1.0.0",
            description=(
                "Validates generated outputs before system acceptance."
            ),
        )

    async def execute(
        self,
        prompt: str,
    ) -> str:
        """
        Execute generation with validation controls.
        """

        if not isinstance(prompt, str):
            raise ValidationError(
                "Prompt must be a string."
            )

        for _ in range(self.max_retries):

            output = await self.generator(prompt)

            if output in self._seen_outputs:
                continue

            self._seen_outputs.add(output)

            validation = self.validate_output(
                output
            )

            if validation.accepted:
                return output

        return (
            "SYSTEM_HALT: "
            "VALIDATION_THRESHOLD_EXCEEDED"
        )

    def validate_output(
        self,
        output: str,
    ) -> OutputValidationResult:
        """
        Validate generated output.
        """

        if not isinstance(output, str):
            raise ValidationError(
                "Output must be a string."
            )

        for pattern in self.blocked_patterns:

            if re.search(
                pattern,
                output,
                re.IGNORECASE,
            ):
                return OutputValidationResult(
                    accepted=False,
                    reason=(
                        "Blocked language pattern detected."
                    ),
                )

        return OutputValidationResult(
            accepted=True,
            reason="Output passed validation.",
        )