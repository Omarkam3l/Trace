"""Replay configuration and ReplayMode definitions."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class ReplayMode(StrEnum):
    """Execution replay modes defining reconstruction scope."""

    FULL = "full"
    GRAPH_ONLY = "graph_only"
    TIMELINE_ONLY = "timeline_only"
    SNAPSHOT_ONLY = "snapshot_only"
    CUSTOM = "custom"


class ReplayConfig(BaseModel):
    """Immutable configuration for ReplayEngine execution."""

    model_config = ConfigDict(frozen=True)

    mode: ReplayMode = ReplayMode.FULL
    validate_sequences: bool = True
    validate_relationships: bool = True
    strict: bool = True
