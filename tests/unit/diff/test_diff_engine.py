"""Unit tests for ExecutionDiffEngine workflow."""

from __future__ import annotations

from datetime import datetime, timezone

from traceforge.diff.engine import ExecutionDiffEngine
from traceforge.replay.session import ReplaySession
from traceforge.storage.records import NodeRecord, SessionRecord


def test_execution_diff_engine_comparison():
    now = datetime.now(timezone.utc)
    base_sess = SessionRecord(session_id="s1", started_at=now, duration_ms=100.0, status="completed", environment_os="win32", environment_python="3.13", profile_name="standard")
    target_sess = SessionRecord(session_id="s2", started_at=now, duration_ms=150.0, status="completed", environment_os="win32", environment_python="3.13", profile_name="standard")

    n1 = NodeRecord(node_id="n1", graph_id="g1", type="function", name="main", started_at=now, duration_ms=10.0, status="completed")
    n2 = NodeRecord(node_id="n2", graph_id="g1", type="function", name="helper", started_at=now, duration_ms=30.0, status="completed")

    baseline = ReplaySession(session=base_sess, nodes=[n1])
    target = ReplaySession(session=target_sess, nodes=[n1, n2])

    engine = ExecutionDiffEngine()
    report = engine.compare(baseline, target)

    assert report.baseline_session_id == "s1"
    assert report.target_session_id == "s2"
    assert report.graph_diff is not None
    assert report.graph_diff.added_nodes == ["helper"]
    assert report.performance_diff is not None
    assert report.performance_diff.duration_delta_ms == 50.0
