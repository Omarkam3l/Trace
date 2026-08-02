"""Batch immutable container for Phase 6.2 Buffer Manager & Flush Engine."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Batch(BaseModel):
    """Immutable batch of storage records ready for persistent writing."""

    model_config = ConfigDict(frozen=True)

    batch_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    records: tuple[Any, ...] = Field(default_factory=tuple)
    record_count: int = 0
