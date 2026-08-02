"""InstrumentationConfig model for Phase 3 Instrumentation API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from traceforge.domain.profile import RecordingProfile


class InstrumentationConfig(BaseModel):
    """Immutable configuration container for TraceForge instrumentation."""

    model_config = ConfigDict(frozen=True)

    profile: RecordingProfile = Field(default_factory=RecordingProfile)
    plugins: list[Any] = Field(default_factory=list)
    capture_exceptions: bool = True
    auto_activity_names: bool = True
    sampling_rate: float = 1.0
