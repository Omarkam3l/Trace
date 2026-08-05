"""Unit tests for TimelineBuilder deterministic event sorting."""

from __future__ import annotations

from datetime import UTC, datetime

from traceforge.replay.timeline import TimelineBuilder
from traceforge.storage.records import RawEventRecord


def test_timeline_builder_deterministic_sorting():
    now = datetime.now(UTC)
    e1 = RawEventRecord(event_id="b_evt", timestamp=now, sequence=2, type="FunctionReturned", source="python_sdk")
    e2 = RawEventRecord(event_id="a_evt", timestamp=now, sequence=1, type="FunctionEntered", source="python_sdk")
    e3 = RawEventRecord(event_id="c_evt", timestamp=now, sequence=1, type="FunctionEntered", source="python_sdk")

    sorted_timeline = TimelineBuilder.sort_timeline([e1, e2, e3])
    # Priority: timestamp ASC -> sequence ASC -> event_id ASC
    assert sorted_timeline[0].event_id == "a_evt"
    assert sorted_timeline[1].event_id == "c_evt"
    assert sorted_timeline[2].event_id == "b_evt"
