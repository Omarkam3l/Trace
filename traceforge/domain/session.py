"""RecordingSession domain entity model."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from traceforge.domain.activity import Activity
from traceforge.domain.enums import SessionStatus
from traceforge.domain.environment import Environment
from traceforge.domain.profile import RecordingProfile


class RecordingSession(BaseModel):
    """Immutable developer recording session."""

    model_config = ConfigDict(frozen=True)

    session_id: str
    started_at: datetime
    finished_at: datetime | None = None
    duration_ms: float | None = None
    status: SessionStatus = SessionStatus.RECORDING
    environment: Environment
    profile: RecordingProfile
    activities: list[Activity] = Field(default_factory=list)

    @property
    def id(self) -> str:
        return self.session_id

    @model_validator(mode="after")
    def validate_session_integrity(self) -> RecordingSession:
        for act in self.activities:
            if act.session_id != self.session_id:
                raise ValueError(
                    f"Activity {act.activity_id!r} session_id {act.session_id!r} does not match RecordingSession session_id {self.session_id!r}"
                )
        return self
