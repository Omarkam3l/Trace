"""Immutable query objects for Phase 7 Query Engine."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from traceforge.query.filters import QueryFilter
from traceforge.query.pagination import Pagination


class SessionQuery(BaseModel):
    """Query parameters for fetching RecordingSession entities."""

    model_config = ConfigDict(frozen=True)

    session_id: str | None = None
    filter: QueryFilter | None = None
    pagination: Pagination = Field(default_factory=Pagination)


class ActivityQuery(BaseModel):
    """Query parameters for fetching Activity entities."""

    model_config = ConfigDict(frozen=True)

    activity_id: str | None = None
    session_id: str | None = None
    filter: QueryFilter | None = None
    pagination: Pagination = Field(default_factory=Pagination)


class GraphQuery(BaseModel):
    """Query parameters for fetching ExecutionGraph entities."""

    model_config = ConfigDict(frozen=True)

    graph_id: str | None = None
    activity_id: str | None = None


class NodeQuery(BaseModel):
    """Query parameters for fetching ExecutionNode entities."""

    model_config = ConfigDict(frozen=True)

    node_id: str | None = None
    graph_id: str | None = None
    node_type: str | None = None
    filter: QueryFilter | None = None
    pagination: Pagination = Field(default_factory=Pagination)


class RelationshipQuery(BaseModel):
    """Query parameters for fetching Relationship entities."""

    model_config = ConfigDict(frozen=True)

    graph_id: str | None = None
    source_node_id: str | None = None
    target_node_id: str | None = None


class RawEventQuery(BaseModel):
    """Query parameters for fetching RawEvent objects."""

    model_config = ConfigDict(frozen=True)

    session_id: str | None = None
    activity_id: str | None = None
    filter: QueryFilter | None = None
    pagination: Pagination = Field(default_factory=Pagination)
