"""Unit tests for GraphRebuilder execution graph reconstruction."""

from __future__ import annotations

from datetime import UTC, datetime

from traceforge.query.engine import QueryEngine
from traceforge.replay.graph_rebuilder import GraphRebuilder
from traceforge.storage.drivers.sqlite import SQLiteStorageDriver
from traceforge.storage.records import ActivityRecord, GraphRecord, NodeRecord, RelationshipRecord, SessionRecord


def test_graph_rebuilder_reconstruction():
    driver = SQLiteStorageDriver(":memory:")
    conn = driver.connection_manager.get_connection()

    now = datetime.now(UTC)
    s1 = SessionRecord(
        session_id="s1",
        started_at=now,
        status="completed",
        environment_os="win32",
        environment_python="3.13",
        profile_name="standard",
    )
    a1 = ActivityRecord(
        activity_id="act1", session_id="s1", name="Checkout", started_at=now, status="completed", graph_id="g1"
    )
    g1 = GraphRecord(graph_id="g1", activity_id="act1", node_ids=["n1"], relationship_ids=["r1"])
    n1 = NodeRecord(node_id="n1", graph_id="g1", type="function", name="main", started_at=now, status="completed")
    r1 = RelationshipRecord(
        relationship_id="r1", graph_id="g1", source_node_id="n1", target_node_id="n2", type="parent_child"
    )

    driver.begin_transaction()
    driver.write_batch([s1, a1, g1, n1, r1])
    driver.commit()

    query_engine = QueryEngine(conn)
    rebuilder = GraphRebuilder(query_engine)

    graphs, nodes, rels = rebuilder.rebuild_activity_graphs("act1")
    assert len(graphs) == 1
    assert len(nodes) == 1
    assert len(rels) == 1

    driver.close()
