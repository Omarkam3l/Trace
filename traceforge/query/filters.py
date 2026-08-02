"""QueryFilter model for Query Engine read operations."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class QueryFilter(BaseModel):
    """Immutable filter criteria for querying execution artifacts."""

    model_config = ConfigDict(frozen=True)

    session_id: str | None = None
    activity_id: str | None = None
    graph_id: str | None = None
    node_id: str | None = None
    node_type: str | None = None
    status: str | None = None
    timestamp_from: datetime | None = None
    timestamp_to: datetime | None = None
