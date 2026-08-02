"""RawEvent model for Phase 2 Recording Engine."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from traceforge.domain.enums import SourceType


class RawEvent(BaseModel):
    """Immutable raw event emitted by plugins and instrumentation hooks."""

    model_config = ConfigDict(frozen=True)

    event_id: str
    timestamp: datetime
    sequence: int = 0
    type: str
    source: SourceType | str = SourceType.UNKNOWN
    payload: dict[str, Any] = Field(default_factory=dict)
    context_id: str | None = None
    activity_hint: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
