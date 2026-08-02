"""Unit tests for RelationshipRepository read operations and incoming/outgoing traversal."""

from __future__ import annotations

from datetime import datetime, timezone

from traceforge.query.repositories.relationship_repository import RelationshipRepository
from traceforge.storage.drivers.sqlite import SQLiteStorageDriver
from traceforge.storage.records.activity_record import ActivityRecord
from traceforge.storage.records.graph_record import GraphRecord
from traceforge.storage.records.relationship_record import RelationshipRecord
from traceforge.storage.records.session_record import SessionRecord


def test_relationship_read_repository_and_traversal():
    driver = SQLiteStorageDriver(":memory:")
    conn = driver.connection_manager.get_connection()

    now = datetime.now(timezone.utc)
    s1 = SessionRecord(session_id="s1", started_at=now, status="completed", environment_os="win32", environment_python="3.13", profile_name="standard")
    a1 = ActivityRecord(activity_id="act1", session_id="s1", name="Checkout", started_at=now, status="completed", graph_id="g1")
    g1 = GraphRecord(graph_id="g1", activity_id="act1", node_ids=["n1", "n2"], relationship_ids=["r1"])

    rel = RelationshipRecord(relationship_id="r1", graph_id="g1", source_node_id="n1", target_node_id="n2", type="parent_child")

    driver.begin_transaction()
    driver.write_batch([s1, a1, g1, rel])
    driver.commit()

    repo = RelationshipRepository(conn)

    rels = repo.list_by_graph("g1")
    assert len(rels) == 1

    outgoing = repo.list_outgoing(node_id="n1", graph_id="g1")
    assert len(outgoing) == 1
    assert outgoing[0].target_node_id == "n2"

    incoming = repo.list_incoming(node_id="n2", graph_id="g1")
    assert len(incoming) == 1
    assert incoming[0].source_node_id == "n1"

    driver.close()
