"""Recording profile value object model."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from traceforge.domain.enums import NodeType


class RecordingProfile(BaseModel):
    """Immutable recording profile defining capture policies."""

    model_config = ConfigDict(frozen=True)

    name: str = "standard"
    captured_node_types: set[NodeType] | None = None
    max_payload_bytes: int = 100_000
    capture_variables: bool = True
    capture_stack: bool = True
    sampling_rate: float = 1.0
    privacy_rules: dict[str, Any] = Field(default_factory=dict)
