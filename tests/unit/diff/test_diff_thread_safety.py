"""Unit tests for multi-threaded concurrent ExecutionDiffEngine comparisons."""

from __future__ import annotations

import concurrent.futures
from datetime import datetime, timezone

from traceforge.diff.engine import ExecutionDiffEngine
from traceforge.replay.session import ReplaySession
from traceforge.storage.records import NodeRecord, SessionRecord


def test_concurrent_execution_diff_comparisons():
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

    n1 = NodeRecord(node_id="n1", graph_id="g1", type="function", name="main", started_at=now, status="completed")

    baseline = ReplaySession(session=b_sess, nodes=[n1])
    target = ReplaySession(session=t_sess, nodes=[n1])

    engine = ExecutionDiffEngine()

    def worker_diff(worker_id: int):
        report = engine.compare(baseline, target)
        assert report.baseline_session_id == "s1"
        assert report.target_session_id == "s2"

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(worker_diff, i) for i in range(10)]
        concurrent.futures.wait(futures)
