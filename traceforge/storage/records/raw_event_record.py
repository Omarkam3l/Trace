"""RawEventRecord storage model."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class RawEventRecord(BaseModel):
    """Immutable persistent storage record for a RawEvent."""

    model_config = ConfigDict(frozen=True)

    event_id: str
    timestamp: datetime
    sequence: int
    type: str
    source: str
    payload_json: str = "{}"
    context_id: str | None = None
    activity_hint: str | None = None
    metadata_json: str = "{}"
    record_timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
