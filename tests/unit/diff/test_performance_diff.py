"""Unit tests for PerformanceDiffComparator."""

from __future__ import annotations

from datetime import datetime, timezone

from traceforge.diff.config import DiffConfig
from traceforge.diff.comparators.performance import PerformanceDiffComparator
from traceforge.replay.session import ReplaySession
from traceforge.storage.records import NodeRecord, SessionRecord


def test_performance_diff_comparator():
    now = datetime.now(timezone.utc)
    b_sess = SessionRecord(session_id="s1", started_at=now, duration_ms=100.0, status="completed", environment_os="win32", environment_python="3.13", profile_name="standard")
    t_sess = SessionRecord(session_id="s2", started_at=now, duration_ms=250.0, status="completed", environment_os="win32", environment_python="3.13", profile_name="standard")

    n1_base = NodeRecord(node_id="n1", graph_id="g1", type="function", name="query_db", started_at=now, duration_ms=10.0, status="completed")
    n1_targ = NodeRecord(node_id="n1", graph_id="g1", type="function", name="query_db", started_at=now, duration_ms=60.0, status="completed")  # +50ms regression

    baseline = ReplaySession(session=b_sess, nodes=[n1_base])
    target = ReplaySession(session=t_sess, nodes=[n1_targ])

    comp = PerformanceDiffComparator()
    diff = comp.compare(baseline, target, DiffConfig(duration_threshold_ms=20.0))

    assert diff.duration_delta_ms == 150.0
    assert len(diff.slow_nodes) == 1
    assert diff.slow_nodes[0] == ("query_db", 50.0)
