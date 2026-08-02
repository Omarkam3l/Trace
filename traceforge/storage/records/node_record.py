"""NodeRecord storage model."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field


class NodeRecord(BaseModel):
    """Immutable persistent storage record for an ExecutionNode."""

    model_config = ConfigDict(frozen=True)

    node_id: str
    graph_id: str
    type: str
    name: str
    started_at: datetime
    finished_at: datetime | None = None
    duration_ms: float | None = None
    status: str
    parent_id: str | None = None
    child_ids: list[str] = Field(default_factory=list)
    inputs_json: str = "{}"
    outputs_json: str = "{}"
    metadata_json: str = "{}"
    tags: list[str] = Field(default_factory=list)
    source: str = "unknown"
    record_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
