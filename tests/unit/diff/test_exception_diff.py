"""Unit tests for ExceptionDiffComparator."""

from __future__ import annotations

from datetime import datetime, timezone

from traceforge.diff.comparators.exception import ExceptionDiffComparator
from traceforge.replay.session import ReplaySession
from traceforge.storage.records import NodeRecord, SessionRecord


def test_exception_diff_comparator():
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

    n1_base = NodeRecord(node_id="n1", graph_id="g1", type="function", name="main", started_at=now, status="completed")
    n1_targ = NodeRecord(node_id="n1", graph_id="g1", type="function", name="main", started_at=now, status="error")

    baseline = ReplaySession(session=b_sess, nodes=[n1_base])
    target = ReplaySession(session=t_sess, nodes=[n1_targ])

    comp = ExceptionDiffComparator()
    diff = comp.compare(baseline, target)

    assert diff.added_exceptions == ["main:error"]
    assert diff.removed_exceptions == []
