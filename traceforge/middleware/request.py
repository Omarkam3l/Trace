"""A minimal, framework-agnostic request context.

Framework-specific instrumentation adapters (see ``traceforge.instrumentation``)
translate their framework's request object into this shape.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class RequestContext:
    method: str
    path: str
    headers: dict[str, str] = field(default_factory=dict)
    correlation_id: str | None = None
