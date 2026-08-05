"""Typed, validated TraceForge configuration."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from traceforge.config.defaults import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_ENABLED,
    DEFAULT_FLUSH_INTERVAL_SECONDS,
    DEFAULT_SAMPLING_RATE,
    DEFAULT_SERVICE_NAME,
    DEFAULT_STORAGE_BACKEND,
)

StorageBackend = Literal["memory", "jsonl", "sqlite", "postgres"]


class TraceForgeSettings(BaseModel):
    """Process-wide TraceForge configuration.

    Instantiate directly, or build one with
    :func:`traceforge.config.loader.load_settings`.
    """

    service_name: str = DEFAULT_SERVICE_NAME
    enabled: bool = DEFAULT_ENABLED

    storage_backend: StorageBackend = DEFAULT_STORAGE_BACKEND  # type: ignore[assignment]
    storage_path: str | None = None

    batch_size: int = Field(default=DEFAULT_BATCH_SIZE, gt=0)
    flush_interval: float = Field(default=DEFAULT_FLUSH_INTERVAL_SECONDS, gt=0)
    sampling_rate: float = Field(default=DEFAULT_SAMPLING_RATE, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def _validate_storage_path(self) -> TraceForgeSettings:
        if self.storage_backend in ("jsonl", "sqlite") and not self.storage_path:
            raise ValueError(f"storage_path is required when storage_backend={self.storage_backend!r}")
        return self
