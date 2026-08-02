"""PipelineDispatcher: deterministic artifact dispatch with failure isolation."""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from traceforge.domain.activity import Activity
    from traceforge.domain.graph import ExecutionGraph
    from traceforge.domain.session import RecordingSession
    from traceforge.pipeline.consumer import ExecutionConsumer
    from traceforge.pipeline.stats import PipelineStatistics


class PipelineDispatcher:
    """Delivers completed immutable execution artifacts to enabled consumers under failure isolation."""

    def __init__(self, stats: PipelineStatistics) -> None:
        self._stats = stats
        self._lock = threading.RLock()

    def dispatch_session(self, session: RecordingSession, consumers: list[ExecutionConsumer]) -> None:
        """Dispatch completed RecordingSession to enabled consumers in deterministic order."""
        with self._lock:
            active_list = [c for c in consumers if c.is_enabled]

        self._stats.record_session()
        for consumer in active_list:
            try:
                consumer.on_session_completed(session)
            except Exception:
                self._stats.record_failure()

    def dispatch_activity(self, activity: Activity, consumers: list[ExecutionConsumer]) -> None:
        """Dispatch completed Activity to enabled consumers in deterministic order."""
        with self._lock:
            active_list = [c for c in consumers if c.is_enabled]

        self._stats.record_activity()
        for consumer in active_list:
            try:
                consumer.on_activity_completed(activity)
            except Exception:
                self._stats.record_failure()

    def dispatch_graph(self, graph: ExecutionGraph, consumers: list[ExecutionConsumer]) -> None:
        """Dispatch completed ExecutionGraph to enabled consumers in deterministic order."""
        with self._lock:
            active_list = [c for c in consumers if c.is_enabled]

        self._stats.record_graph()
        for consumer in active_list:
            try:
                consumer.on_graph_completed(graph)
            except Exception:
                self._stats.record_failure()
