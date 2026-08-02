"""Graph view models for UI graph libraries (Cytoscape/D3/Vis.js)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class NodeViewModel(BaseModel):
    """Frontend-ready node representation."""

    model_config = ConfigDict(frozen=True)

    id: str
    label: str
    type: str
    status: str
    duration_ms: float | None = None


class EdgeViewModel(BaseModel):
    """Frontend-ready edge representation."""

    model_config = ConfigDict(frozen=True)

    id: str
    source: str
    target: str
    label: str


class GraphViewModel(BaseModel):
    """Complete frontend graph visualization model."""

    model_config = ConfigDict(frozen=True)

    nodes: list[NodeViewModel] = Field(default_factory=list)
    edges: list[EdgeViewModel] = Field(default_factory=list)
