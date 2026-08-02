"""API Service Layer configuration definitions."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ServiceConfig(BaseModel):
    """Immutable configuration for TraceForgeApiService."""

    model_config = ConfigDict(frozen=True)

    enable_caching: bool = False
    max_diff_nodes: int = 1000
    default_export_format: str = "json"
