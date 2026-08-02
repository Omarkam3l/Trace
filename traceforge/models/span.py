"""The Span model: a single unit of traced execution."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from traceforge.models.enums import SpanKind, SpanStatus
from traceforge.models.event import EventModel
from traceforge.models.metadata import ExceptionInfo


class SpanModel(BaseModel):
    """An immutable snapshot of a span at a point in time.

    While a span is *in progress*, TraceForge mutates a live domain object
    (``traceforge.core.span.Span``); every time that object is observed
    (started, ended) it emits a frozen ``SpanModel`` snapshot like this one
    for storage/exporters to consume. This keeps the persistence layer free
    of hidden mutable state.
    """

    model_config = ConfigDict(frozen=True)

    id: str
    trace_id: str
    parent_span_id: str | None = None
    name: str
    kind: SpanKind = SpanKind.INTERNAL
    status: SpanStatus = SpanStatus.UNSET

    start_time: datetime
    end_time: datetime | None = None
    duration_ms: float | None = None

    attributes: dict[str, Any] = Field(default_factory=dict)
    events: list[EventModel] = Field(default_factory=list)
    children: list[SpanModel] = Field(default_factory=list)
    exception: ExceptionInfo | None = None

    correlation_id: str | None = None
    session_id: str | None = None

    @property
    def is_finished(self) -> bool:
        return self.end_time is not None

    @property
    def is_root(self) -> bool:
        return self.parent_span_id is None

    @property
    def parent_id(self) -> str | None:
        return self.parent_span_id

    @property
    def started_at(self) -> datetime:
        return self.start_time

    @property
    def finished_at(self) -> datetime | None:
        return self.end_time
