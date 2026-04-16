from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ExecutionResult:
    input: dict[str, Any]
    decision: str
    status: str
    valid: bool
    errors: list[str]
    timestamp: str
