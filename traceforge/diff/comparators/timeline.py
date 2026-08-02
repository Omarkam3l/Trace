"""TimelineDiffComparator for comparing event stream timelines."""

from __future__ import annotations

from typing import TYPE_CHECKING

from traceforge.diff.report import TimelineDiff

if TYPE_CHECKING:
    from traceforge.replay.session import ReplaySession


class TimelineDiffComparator:
    """Compares event stream timelines and sequence order between baseline and target sessions."""

    def compare(self, baseline: ReplaySession, target: ReplaySession) -> TimelineDiff:
        """Compare timeline events deterministically."""
        base_event_ids = {e.event_id for e in baseline.timeline}
        target_event_ids = {e.event_id for e in target.timeline}

        added = sorted(list(target_event_ids - base_event_ids))
        removed = sorted(list(base_event_ids - target_event_ids))

        # Calculate sequence drift
        drift_count = 0
        min_len = min(len(baseline.timeline), len(target.timeline))
        for i in range(min_len):
            if baseline.timeline[i].sequence != target.timeline[i].sequence or baseline.timeline[i].type != target.timeline[i].type:
                drift_count += 1

        drift_count += abs(len(baseline.timeline) - len(target.timeline))

        return TimelineDiff(
            added_events=added,
            removed_events=removed,
            sequence_drift_count=drift_count,
        )
