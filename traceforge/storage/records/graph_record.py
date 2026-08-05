"""GraphRecord storage model."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class GraphRecord(BaseModel):
    """Immutable persistent storage record for an ExecutionGraph."""

    model_config = ConfigDict(frozen=True)

    graph_id: str
    activity_id: str
    node_ids: list[str] = Field(default_factory=list)
    relationship_ids: list[str] = Field(default_factory=list)
    record_timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
