"""A minimal, framework-agnostic response context."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ResponseContext:
    status_code: int
    headers: dict[str, str] = field(default_factory=dict)
    duration_ms: float | None = None
