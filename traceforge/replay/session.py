"""ReplaySession immutable result container."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from traceforge.storage.records import (
    ActivityRecord,
    GraphRecord,
    NodeRecord,
    RawEventRecord,
    RelationshipRecord,
    SessionRecord,
    SnapshotRecord,
)


class ReplaySession(BaseModel):
    """Immutable result container representing a reconstructed execution session."""

    model_config = ConfigDict(frozen=True)

    session: SessionRecord | None = None
    activities: list[ActivityRecord] = Field(default_factory=list)
    graphs: list[GraphRecord] = Field(default_factory=list)
    nodes: list[NodeRecord] = Field(default_factory=list)
    relationships: list[RelationshipRecord] = Field(default_factory=list)
    timeline: list[RawEventRecord] = Field(default_factory=list)
    snapshots: list[SnapshotRecord] = Field(default_factory=list)
