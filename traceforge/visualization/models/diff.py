"""Diff view models for side-by-side execution diff UI components."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DiffViewModel(BaseModel):
    """Frontend-ready execution diff representation."""

    model_config = ConfigDict(frozen=True)

    baseline_id: str
    target_id: str
    summary: dict[str, Any] = Field(default_factory=dict)
