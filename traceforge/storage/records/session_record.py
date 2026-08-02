"""SessionRecord storage model for Phase 6.1 Storage Architecture."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field


class SessionRecord(BaseModel):
    """Immutable persistent storage record for a RecordingSession."""

    model_config = ConfigDict(frozen=True)

    session_id: str
    started_at: datetime
    finished_at: datetime | None = None
    duration_ms: float | None = None
    status: str
    environment_os: str
    environment_python: str
    profile_name: str
    record_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
