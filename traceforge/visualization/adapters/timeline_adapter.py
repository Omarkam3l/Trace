"""TimelineAdapter converting event streams to TimelineViewModel."""

from __future__ import annotations

from typing import TYPE_CHECKING

from traceforge.visualization.models.timeline import EventViewModel, TimelineViewModel, TrackViewModel

if TYPE_CHECKING:
    from traceforge.replay.session import ReplaySession
    from traceforge.visualization.config import VisualizationConfig


class TimelineAdapter:
    """Transforms ReplaySession event streams into waterfall timeline models."""

    def adapt(self, session: ReplaySession, config: VisualizationConfig) -> TimelineViewModel:
        """Convert session timeline events into TimelineViewModel tracks."""
        events_by_source: dict[str, list[EventViewModel]] = {}

        for evt in session.timeline:
            vm = EventViewModel(
                id=evt.event_id,
                name=evt.type,
                timestamp_iso=evt.timestamp.isoformat(),
                sequence=evt.sequence,
                type=evt.type,
            )
            src = evt.source or "default"
            if src not in events_by_source:
                events_by_source[src] = []
            events_by_source[src].append(vm)

        tracks = [TrackViewModel(name=src, events=evts) for src, evts in sorted(events_by_source.items())]

        return TimelineViewModel(tracks=tracks)
