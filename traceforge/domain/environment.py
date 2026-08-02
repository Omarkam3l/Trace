"""Environment value object model."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Environment(BaseModel):
    """Immutable environment metadata recorded at session start."""

    model_config = ConfigDict(frozen=True)

    os: str
    python_version: str
    hostname: str | None = None
    environment_name: str = "development"
    variables: dict[str, str] = Field(default_factory=dict)
