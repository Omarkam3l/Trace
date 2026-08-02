"""Flamegraph view models for stack profile visualization."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class FlamegraphSpanModel(BaseModel):
    """Hierarchical node in a flamegraph stack tree."""

    model_config = ConfigDict(frozen=True)

    name: str
    value: float
    children: list[FlamegraphSpanModel] = Field(default_factory=list)


class FlamegraphViewModel(BaseModel):
    """Complete flamegraph visualization model."""

    model_config = ConfigDict(frozen=True)

    root: FlamegraphSpanModel | None = None
