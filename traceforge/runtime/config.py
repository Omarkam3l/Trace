"""RuntimeConfig model for Phase 5 Python Runtime Plugin."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from traceforge.runtime.enums import BackendType, ProfileType


class RuntimeConfig(BaseModel):
    """Configuration settings for runtime observation and filtering."""

    model_config = ConfigDict(frozen=True)

    profile: ProfileType = ProfileType.STANDARD
    backend: BackendType | None = None
    include: list[str] = Field(default_factory=list)
    exclude: list[str] = Field(default_factory=list)
    capture_variables: bool = False
    capture_locals: bool = False
