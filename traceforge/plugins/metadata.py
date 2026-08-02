"""PluginMetadata model for Phase 4 Plugin SDK."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PluginMetadata(BaseModel):
    """Immutable metadata container describing a TraceForge plugin."""

    model_config = ConfigDict(frozen=True)

    name: str
    version: str
    description: str = ""
    author: str = ""
    supported_versions: list[str] = Field(default_factory=list)
    capabilities: set[str] = Field(default_factory=set)
