"""Unit tests for TimelineAdapter."""

from __future__ import annotations

from datetime import datetime, timezone

from traceforge.replay.session import ReplaySession
from traceforge.storage.records import RawEventRecord, SessionRecord
from traceforge.visualization.adapters.timeline_adapter import TimelineAdapter
from traceforge.visualization.config import VisualizationConfig


def test_timeline_adapter():
    now = datetime.now(timezone.utc)
    sess_rec = SessionRecord(session_id="s1", started_at=now, status="completed", environment_os="win32", environment_python="3.13", profile_name="standard")
    evt = RawEventRecord(event_id="e1", timestamp=now, sequence=1, type="Start", source="worker_1")

    session = ReplaySession(session=sess_rec, timeline=[evt])
    adapter = TimelineAdapter()
    vm = adapter.adapt(session, VisualizationConfig())

    assert len(vm.tracks) == 1
    assert vm.tracks[0].name == "worker_1"
    assert vm.tracks[0].events[0].id == "e1"
