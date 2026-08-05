"""RelationshipRecord storage model."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class RelationshipRecord(BaseModel):
    """Immutable persistent storage record for a Relationship."""

    model_config = ConfigDict(frozen=True)

    relationship_id: str
    graph_id: str
    source_node_id: str
    target_node_id: str
    type: str
    record_timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
