"""Timeline view models for waterfall timeline components."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class EventViewModel(BaseModel):
    """Frontend-ready timeline event representation."""

    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    timestamp_iso: str
    sequence: int
    type: str


class TrackViewModel(BaseModel):
    """Timeline event track grouping."""

    model_config = ConfigDict(frozen=True)

    name: str
    events: list[EventViewModel] = Field(default_factory=list)


class TimelineViewModel(BaseModel):
    """Complete frontend timeline visualization model."""

    model_config = ConfigDict(frozen=True)

    tracks: list[TrackViewModel] = Field(default_factory=list)
