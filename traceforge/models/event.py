"""The Event model: a structured, timestamped occurrence within a span."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from traceforge.models.enums import EventLevel


class EventModel(BaseModel):
    """A point-in-time occurrence attached to a span.

    Events are for structured, execution-flow facts ("cache miss",
    "retrying request", "branch taken") — not for free-text application
    logging. TraceForge is not a logger.
    """

    model_config = ConfigDict(frozen=True)

    id: str
    span_id: str | None = None
    name: str
    timestamp: datetime
    level: EventLevel = EventLevel.INFO
    attributes: dict[str, Any] = Field(default_factory=dict)

    @property
    def metadata(self) -> dict[str, Any]:
        return self.attributes

    @property
    def created_at(self) -> datetime:
        return self.timestamp
