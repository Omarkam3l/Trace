"""Metadata value object model."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Metadata(BaseModel):
    """Immutable metadata container for execution node details."""

    model_config = ConfigDict(frozen=True)

    attributes: dict[str, Any] = Field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.attributes.get(key, default)

    def __contains__(self, key: str) -> bool:
        return key in self.attributes
