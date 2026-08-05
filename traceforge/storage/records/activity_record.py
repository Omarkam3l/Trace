"""ActivityRecord storage model."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class ActivityRecord(BaseModel):
    """Immutable persistent storage record for an Activity."""

    model_config = ConfigDict(frozen=True)

    activity_id: str
    session_id: str
    name: str
    started_at: datetime
    finished_at: datetime | None = None
    duration_ms: float | None = None
    status: str
    graph_id: str
    record_timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
