"""Visualization configuration definitions."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class VisualizationConfig(BaseModel):
    """Immutable configuration for VisualizationEngine data adapters."""

    model_config = ConfigDict(frozen=True)

    include_metadata: bool = True
    max_depth: int = 100
    color_palette: str = "default"
