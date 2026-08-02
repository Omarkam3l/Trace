"""Execution Diff configuration and DiffCategory definitions."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class DiffCategory(StrEnum):
    """Execution diff comparison categories."""

    GRAPH = "graph"
    TIMELINE = "timeline"
    PERFORMANCE = "performance"
    EXCEPTION = "exception"
    METADATA = "metadata"


class DiffConfig(BaseModel):
    """Immutable configuration for ExecutionDiffEngine comparison."""

    model_config = ConfigDict(frozen=True)

    categories: set[DiffCategory] = Field(default_factory=lambda: set(DiffCategory))
    duration_threshold_ms: float = 10.0
    strict_sequence_matching: bool = True
