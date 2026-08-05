"""Execution diff report models."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NodeGraphDiff(BaseModel):
    """Structural graph comparison result."""

    model_config = ConfigDict(frozen=True)

    added_nodes: list[str] = Field(default_factory=list)
    removed_nodes: list[str] = Field(default_factory=list)
    modified_nodes: list[str] = Field(default_factory=list)
    added_relationships: list[str] = Field(default_factory=list)
    removed_relationships: list[str] = Field(default_factory=list)


class TimelineDiff(BaseModel):
    """Event stream timeline comparison result."""

    model_config = ConfigDict(frozen=True)

    added_events: list[str] = Field(default_factory=list)
    removed_events: list[str] = Field(default_factory=list)
    sequence_drift_count: int = 0


class PerformanceDiff(BaseModel):
    """Timing and performance comparison result."""

    model_config = ConfigDict(frozen=True)

    baseline_duration_ms: float | None = None
    target_duration_ms: float | None = None
    duration_delta_ms: float | None = None
    slow_nodes: list[tuple[str, float]] = Field(default_factory=list)


class ExceptionDiff(BaseModel):
    """Captured exception comparison result."""

    model_config = ConfigDict(frozen=True)

    added_exceptions: list[str] = Field(default_factory=list)
    removed_exceptions: list[str] = Field(default_factory=list)


class MetadataDiff(BaseModel):
    """Session environment and profile metadata comparison result."""

    model_config = ConfigDict(frozen=True)

    environment_os_changed: bool = False
    environment_python_changed: bool = False
    profile_name_changed: bool = False


class ExecutionDiffReport(BaseModel):
    """Immutable report capturing execution differences between baseline and target sessions."""

    model_config = ConfigDict(frozen=True)

    baseline_session_id: str
    target_session_id: str
    timestamp: datetime
    graph_diff: NodeGraphDiff | None = None
    timeline_diff: TimelineDiff | None = None
    performance_diff: PerformanceDiff | None = None
    exception_diff: ExceptionDiff | None = None
    metadata_diff: MetadataDiff | None = None
