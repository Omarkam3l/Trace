"""Unit tests for VisualizationEngine workflow."""

from __future__ import annotations

from datetime import datetime, timezone

from traceforge.diff.report import ExecutionDiffReport, NodeGraphDiff
from traceforge.replay.session import ReplaySession
from traceforge.storage.records import NodeRecord, RawEventRecord, RelationshipRecord, SessionRecord
from traceforge.visualization.engine import VisualizationEngine


def test_visualization_engine_transformations():
    now = datetime.now(timezone.utc)
    sess_rec = SessionRecord(
        session_id="s1",
        started_at=now,
        status="completed",
        environment_os="win32",
        environment_python="3.13",
        profile_name="standard",
    )

    n1 = NodeRecord(
        node_id="n1",
        graph_id="g1",
        type="function",
        name="main",
        started_at=now,
        duration_ms=10.0,
        status="completed",
        child_ids=["n2"],
    )
    n2 = NodeRecord(
        node_id="n2",
        graph_id="g1",
        type="function",
        name="helper",
        started_at=now,
        duration_ms=5.0,
        status="completed",
        parent_id="n1",
    )
    rel = RelationshipRecord(
        relationship_id="r1", graph_id="g1", source_node_id="n1", target_node_id="n2", type="parent_child"
    )
    evt = RawEventRecord(event_id="e1", timestamp=now, sequence=1, type="Start", source="test")

    session = ReplaySession(session=sess_rec, nodes=[n1, n2], relationships=[rel], timeline=[evt])
    engine = VisualizationEngine()

    graph_vm = engine.to_graph_model(session)
    assert len(graph_vm.nodes) == 2
    assert len(graph_vm.edges) == 1

    timeline_vm = engine.to_timeline_model(session)
    assert len(timeline_vm.tracks) == 1
    assert timeline_vm.tracks[0].name == "test"

    flamegraph_vm = engine.to_flamegraph_model(session)
    assert flamegraph_vm.root is not None
    assert flamegraph_vm.root.name == "main"
    assert len(flamegraph_vm.root.children) == 1

    diff_report = ExecutionDiffReport(
        baseline_session_id="s1",
        target_session_id="s2",
        timestamp=now,
        graph_diff=NodeGraphDiff(added_nodes=["extra"]),
    )
    diff_vm = engine.to_diff_model(diff_report)
    assert diff_vm.baseline_id == "s1"
    assert diff_vm.summary["added_nodes_count"] == 1
