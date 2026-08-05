"""Unit tests for TimelineDiffComparator."""

from __future__ import annotations

from datetime import datetime, timezone

from traceforge.diff.comparators.timeline import TimelineDiffComparator
from traceforge.replay.session import ReplaySession
from traceforge.storage.records import RawEventRecord, SessionRecord


def test_timeline_diff_comparator():
    now = datetime.now(timezone.utc)
    b_sess = SessionRecord(
        session_id="s1",
        started_at=now,
        status="completed",
        environment_os="win32",
        environment_python="3.13",
        profile_name="standard",
    )
    t_sess = SessionRecord(
        session_id="s2",
        started_at=now,
        status="completed",
        environment_os="win32",
        environment_python="3.13",
        profile_name="standard",
    )

    e1 = RawEventRecord(event_id="e1", timestamp=now, sequence=1, type="Start", source="test")
    e2 = RawEventRecord(event_id="e2", timestamp=now, sequence=2, type="End", source="test")
    e3 = RawEventRecord(event_id="e3", timestamp=now, sequence=3, type="Extra", source="test")

    baseline = ReplaySession(session=b_sess, timeline=[e1, e2])
    target = ReplaySession(session=t_sess, timeline=[e1, e2, e3])

    comp = TimelineDiffComparator()
    diff = comp.compare(baseline, target)

    assert diff.added_events == ["e3"]
    assert diff.removed_events == []
    assert diff.sequence_drift_count == 1
