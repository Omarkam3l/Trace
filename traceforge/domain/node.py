"""ExecutionNode and Relationship domain entity models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from traceforge.domain.enums import NodeStatus, NodeType, RelationshipType, SourceType
from traceforge.domain.metadata import Metadata


class Relationship(BaseModel):
    """Immutable directional relationship between execution nodes."""

    model_config = ConfigDict(frozen=True)

    relationship_id: str
    graph_id: str
    source_node_id: str
    target_node_id: str
    type: RelationshipType = RelationshipType.PARENT_CHILD

    @property
    def id(self) -> str:
        return self.relationship_id

    @field_validator("target_node_id")
    @classmethod
    def validate_no_self_loop(cls, target: str, info: Any) -> str:
        if "source_node_id" in info.data and target == info.data["source_node_id"]:
            raise ValueError("Relationship source and target node cannot be identical (self-loop forbidden)")
        return target


class ExecutionNode(BaseModel):
    """Immutable atomic unit of execution."""

    model_config = ConfigDict(frozen=True)

    node_id: str
    graph_id: str
    type: NodeType
    name: str
    started_at: datetime
    finished_at: datetime | None = None
    duration_ms: float | None = None
    status: NodeStatus = NodeStatus.PENDING
    parent_id: str | None = None
    child_ids: list[str] = Field(default_factory=list)
    inputs: dict[str, Any] = Field(default_factory=dict)
    outputs: dict[str, Any] = Field(default_factory=dict)
    metadata: Metadata = Field(default_factory=Metadata)
    tags: set[str] = Field(default_factory=set)
    source: SourceType = SourceType.UNKNOWN

    @property
    def id(self) -> str:
        return self.node_id

    @property
    def parent(self) -> str | None:
        return self.parent_id

    @property
    def children(self) -> list[str]:
        return self.child_ids
