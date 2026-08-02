"""Activity domain entity model."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator

from traceforge.domain.enums import ActivityStatus
from traceforge.domain.graph import ExecutionGraph


class Activity(BaseModel):
    """Immutable representation of a single meaningful user action."""

    model_config = ConfigDict(frozen=True)

    activity_id: str
    session_id: str
    name: str
    started_at: datetime
    finished_at: datetime | None = None
    duration_ms: float | None = None
    status: ActivityStatus = ActivityStatus.ACTIVE
    graph: ExecutionGraph

    @property
    def id(self) -> str:
        return self.activity_id

    @model_validator(mode="after")
    def validate_activity_integrity(self) -> Activity:
        if self.graph.activity_id != self.activity_id:
            raise ValueError(
                f"ExecutionGraph activity_id {self.graph.activity_id!r} does not match Activity activity_id {self.activity_id!r}"
            )
        return self
