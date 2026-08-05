"""SnapshotRecord storage model."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class SnapshotRecord(BaseModel):
    """Immutable persistent storage record for a SessionSnapshot."""

    model_config = ConfigDict(frozen=True)

    snapshot_id: str
    session_id: str
    timestamp: datetime
    active_activity_id: str | None = None
    nodes_count: int = 0
    relationships_count: int = 0
    record_timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
