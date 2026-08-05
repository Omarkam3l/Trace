"""Unit tests for GraphDiffComparator."""

from __future__ import annotations

from datetime import UTC, datetime

from traceforge.diff.comparators.graph import GraphDiffComparator
from traceforge.replay.session import ReplaySession
from traceforge.storage.records import NodeRecord, RelationshipRecord, SessionRecord


def test_graph_diff_comparator():
    now = datetime.now(UTC)
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
    n2_base = NodeRecord(
        node_id="n2", graph_id="g1", type="function", name="old_fn", started_at=now, status="completed"
    )
    n3_targ = NodeRecord(
        node_id="n3", graph_id="g1", type="function", name="new_fn", started_at=now, status="completed"
    )

    r1 = RelationshipRecord(
        relationship_id="r1", graph_id="g1", source_node_id="n1", target_node_id="n2", type="parent_child"
    )

    baseline = ReplaySession(session=b_sess, nodes=[n1, n2_base], relationships=[r1])
    target = ReplaySession(session=t_sess, nodes=[n1, n3_targ], relationships=[])

    comp = GraphDiffComparator()
    diff = comp.compare(baseline, target)

    assert diff.added_nodes == ["new_fn"]
    assert diff.removed_nodes == ["old_fn"]
    assert len(diff.removed_relationships) == 1
