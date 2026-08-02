"""PipelineStatistics for pipeline metrics tracking."""

from __future__ import annotations

import threading
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PipelineStatsSnapshot:
    sessions_dispatched: int
    activities_dispatched: int
    graphs_dispatched: int
    failures_count: int
    active_consumers_count: int


class PipelineStatistics:
    """Thread-safe statistics metrics container for ExecutionPipeline."""

    def __init__(self) -> None:
        self._sessions_dispatched: int = 0
        self._activities_dispatched: int = 0
        self._graphs_dispatched: int = 0
        self._failures_count: int = 0
        self._active_consumers_count: int = 0
        self._lock = threading.RLock()

    def record_session(self) -> None:
        with self._lock:
            self._sessions_dispatched += 1

    def record_activity(self) -> None:
        with self._lock:
            self._activities_dispatched += 1

    def record_graph(self) -> None:
        with self._lock:
            self._graphs_dispatched += 1

    def record_failure(self) -> None:
        with self._lock:
            self._failures_count += 1

    def set_active_consumers_count(self, count: int) -> None:
        with self._lock:
            self._active_consumers_count = count

    def snapshot(self) -> PipelineStatsSnapshot:
        with self._lock:
            return PipelineStatsSnapshot(
                sessions_dispatched=self._sessions_dispatched,
                activities_dispatched=self._activities_dispatched,
                graphs_dispatched=self._graphs_dispatched,
                failures_count=self._failures_count,
                active_consumers_count=self._active_consumers_count,
            )

    def reset(self) -> None:
        with self._lock:
            self._sessions_dispatched = 0
            self._activities_dispatched = 0
            self._graphs_dispatched = 0
            self._failures_count = 0
            self._active_consumers_count = 0
