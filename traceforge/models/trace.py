"""The Trace model: the full tree of spans sharing a trace ID."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from traceforge.models.enums import SpanStatus
from traceforge.models.span import SpanModel


class TraceModel(BaseModel):
    """A logical grouping of spans that share a trace ID.

    A ``TraceModel`` is an assembled *view* over spans that storage adapters
    can build on demand (spans are the unit of persistence); it is not
    itself the unit of storage.
    """

    model_config = ConfigDict(frozen=True)

    id: str
    name: str = "trace"
    correlation_id: str | None = None
    session_id: str | None = None
    root_span_id: str | None = None
    status: SpanStatus = SpanStatus.RUNNING
    start_time: datetime
    end_time: datetime | None = None
    duration_ms: float | None = None
    root_span: SpanModel | None = None
    spans: list[SpanModel] = Field(default_factory=list)

    @property
    def started_at(self) -> datetime:
        return self.start_time

    @property
    def finished_at(self) -> datetime | None:
        return self.end_time

    @classmethod
    def from_spans(
        cls,
        trace_id: str,
        spans: list[SpanModel],
        name: str | None = None,
        status: SpanStatus | None = None,
        duration_ms: float | None = None,
    ) -> TraceModel:
        if not spans:
            raise ValueError("cannot build a TraceModel from an empty span list")
        ordered = sorted(spans, key=lambda s: s.start_time)
        root = next((s for s in ordered if s.is_root), ordered[0])
        end_times = [s.end_time for s in ordered if s.end_time is not None]
        end_time = max(end_times) if len(end_times) == len(ordered) else None
        
        computed_duration: float | None = duration_ms
        if computed_duration is None and end_time is not None:
            computed_duration = max(0.0, (end_time - ordered[0].start_time).total_seconds() * 1000.0)

        # Build parent-child tree hierarchy among spans
        span_by_id: dict[str, SpanModel] = {}
        children_by_parent: dict[str, list[SpanModel]] = {}
        
        for s in ordered:
            span_by_id[s.id] = s
            if s.parent_span_id:
                children_by_parent.setdefault(s.parent_span_id, []).append(s)

        # Re-construct spans with populated children
        def attach_children(span_model: SpanModel) -> SpanModel:
            direct_children = children_by_parent.get(span_model.id, [])
            updated_children = [attach_children(child) for child in direct_children]
            return span_model.model_copy(update={"children": updated_children})

        structured_spans = [attach_children(s) for s in ordered]
        root_with_children = attach_children(root)

        trace_name = name or root.name or "trace"
        trace_status = status or root.status

        return cls(
            id=trace_id,
            name=trace_name,
            correlation_id=root.correlation_id,
            session_id=root.session_id,
            root_span_id=root.id,
            status=trace_status,
            start_time=ordered[0].start_time,
            end_time=end_time,
            duration_ms=computed_duration,
            root_span=root_with_children,
            spans=structured_spans,
        )
