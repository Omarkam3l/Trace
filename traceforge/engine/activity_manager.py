"""ActivityManager: manages activity lifecycle and nested activity execution graphs."""

from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone

from traceforge.domain.activity import Activity
from traceforge.domain.enums import ActivityStatus
from traceforge.engine.graph_builder import GraphBuilder


class ActivityRecord:
    def __init__(self, activity_id: str, session_id: str, name: str, started_at: datetime) -> None:
        self.activity_id = activity_id
        self.session_id = session_id
        self.name = name
        self.started_at = started_at
        self.finished_at: datetime | None = None
        self.duration_ms: float | None = None
        self.status: ActivityStatus = ActivityStatus.ACTIVE
        self.graph_builder = GraphBuilder(graph_id=f"g_{activity_id}", activity_id=activity_id)


class ActivityManager:
    """Manages activity lifecycle and active graph builders."""

    def __init__(self) -> None:
        self._activities: dict[str, ActivityRecord] = {}
        self._active_stack: list[str] = []
        self._lock = threading.RLock()

    def start_activity(
        self,
        session_id: str,
        name: str,
        activity_id: str | None = None,
        started_at: datetime | None = None,
    ) -> str:
        with self._lock:
            act_id = activity_id or f"act_{uuid.uuid4().hex[:16]}"
            start_time = started_at or datetime.now(timezone.utc)
            record = ActivityRecord(
                activity_id=act_id,
                session_id=session_id,
                name=name,
                started_at=start_time,
            )
            self._activities[act_id] = record
            self._active_stack.append(act_id)
            return act_id

    def finish_activity(
        self,
        activity_id: str | None = None,
        finished_at: datetime | None = None,
        status: ActivityStatus = ActivityStatus.COMPLETED,
    ) -> Activity:
        with self._lock:
            target_id = activity_id or (self._active_stack[-1] if self._active_stack else None)
            if target_id is None or target_id not in self._activities:
                raise RuntimeError("No active activity to finish")

            record = self._activities[target_id]
            end_time = finished_at or datetime.now(timezone.utc)
            duration_ms = max(0.0, (end_time - record.started_at).total_seconds() * 1000.0)

            final_graph = record.graph_builder.build_final_graph()

            activity = Activity(
                activity_id=record.activity_id,
                session_id=record.session_id,
                name=record.name,
                started_at=record.started_at,
                finished_at=end_time,
                duration_ms=duration_ms,
                status=status,
                graph=final_graph,
            )

            if target_id in self._active_stack:
                self._active_stack.remove(target_id)
            return activity

    def get_current_activity_record(self) -> ActivityRecord | None:
        with self._lock:
            if not self._active_stack:
                return None
            return self._activities.get(self._active_stack[-1])

    def get_graph_builder(self, activity_id: str | None = None) -> GraphBuilder | None:
        with self._lock:
            rec = self._activities.get(activity_id) if activity_id else self.get_current_activity_record()
            return rec.graph_builder if rec else None

    def clear(self) -> None:
        with self._lock:
            self._activities.clear()
            self._active_stack.clear()
