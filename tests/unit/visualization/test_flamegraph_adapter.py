"""Unit tests for FlamegraphAdapter."""

from __future__ import annotations

from datetime import datetime, timezone

from traceforge.replay.session import ReplaySession
from traceforge.storage.records import NodeRecord, SessionRecord
from traceforge.visualization.adapters.flamegraph_adapter import FlamegraphAdapter
from traceforge.visualization.config import VisualizationConfig


def test_flamegraph_adapter():
    now = datetime.now(timezone.utc)
    sess_rec = SessionRecord(session_id="s1", started_at=now, status="completed", environment_os="win32", environment_python="3.13", profile_name="standard")
    n1 = NodeRecord(node_id="n1", graph_id="g1", type="function", name="main", started_at=now, duration_ms=100.0, status="completed", child_ids=["n2"])
    n2 = NodeRecord(node_id="n2", graph_id="g1", type="function", name="child", started_at=now, duration_ms=40.0, status="completed", parent_id="n1")

    session = ReplaySession(session=sess_rec, nodes=[n1, n2])
    adapter = FlamegraphAdapter()
    vm = adapter.adapt(session, VisualizationConfig())

    assert vm.root is not None
    assert vm.root.name == "main"
    assert vm.root.value == 100.0
    assert len(vm.root.children) == 1
    assert vm.root.children[0].name == "child"
