"""TimelineBuilder for deterministic event ordering reconstruction."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from traceforge.query.engine import QueryEngine
    from traceforge.storage.records.raw_event_record import RawEventRecord


class TimelineBuilder:
    """Reconstructs execution timeline in deterministic order."""

    def __init__(self, query_engine: QueryEngine) -> None:
        self._query_engine = query_engine

    def build_session_timeline(self, session_id: str) -> list[RawEventRecord]:
        """Fetch and reconstruct timeline for session_id in deterministic order."""
        events = self._query_engine.raw_events.list_by_session(session_id)
        return self.sort_timeline(events)

    def build_activity_timeline(self, activity_id: str) -> list[RawEventRecord]:
        """Fetch and reconstruct timeline for activity_id in deterministic order."""
        events = self._query_engine.raw_events.list_by_activity(activity_id)
        return self.sort_timeline(events)

    @staticmethod
    def sort_timeline(events: list[RawEventRecord]) -> list[RawEventRecord]:
        """Sort events deterministically by timestamp, sequence, and event_id."""
        return sorted(events, key=lambda e: (e.timestamp, e.sequence, e.event_id))
