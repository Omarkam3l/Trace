"""Unit tests for GraphAdapter."""

from __future__ import annotations

from datetime import UTC, datetime

from traceforge.replay.session import ReplaySession
from traceforge.storage.records import NodeRecord, RelationshipRecord, SessionRecord
from traceforge.visualization.adapters.graph_adapter import GraphAdapter
from traceforge.visualization.config import VisualizationConfig


def test_graph_adapter():
    now = datetime.now(UTC)
    sess_rec = SessionRecord(
        session_id="s1",
        started_at=now,
        status="completed",
        environment_os="win32",
        environment_python="3.13",
        profile_name="standard",
    )
    n1 = NodeRecord(node_id="n1", graph_id="g1", type="function", name="main", started_at=now, status="completed")
    rel = RelationshipRecord(
        relationship_id="r1", graph_id="g1", source_node_id="n1", target_node_id="n2", type="parent_child"
    )

    session = ReplaySession(session=sess_rec, nodes=[n1], relationships=[rel])
    adapter = GraphAdapter()
    vm = adapter.adapt(session, VisualizationConfig())

    assert len(vm.nodes) == 1
    assert vm.nodes[0].id == "n1"
    assert len(vm.edges) == 1
    assert vm.edges[0].source == "n1"
