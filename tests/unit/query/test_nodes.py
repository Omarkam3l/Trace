"""Unit tests for NodeRepository read operations and parent/children traversal."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from traceforge.query.exceptions import NotFoundError
from traceforge.query.repositories.node_repository import NodeRepository
from traceforge.storage.drivers.sqlite import SQLiteStorageDriver
from traceforge.storage.records.activity_record import ActivityRecord
from traceforge.storage.records.graph_record import GraphRecord
from traceforge.storage.records.node_record import NodeRecord
from traceforge.storage.records.session_record import SessionRecord


def test_node_read_repository_and_traversal():
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
    g1 = GraphRecord(graph_id="g1", activity_id="act1", node_ids=["parent_node", "child_node"], relationship_ids=[])

    parent = NodeRecord(
        node_id="parent_node",
        graph_id="g1",
        type="function",
        name="main",
        started_at=now,
        status="completed",
        child_ids=["child_node"],
    )
    child = NodeRecord(
        node_id="child_node",
        graph_id="g1",
        type="function",
        name="helper",
        started_at=now,
        status="completed",
        parent_id="parent_node",
    )

    driver.begin_transaction()
    driver.write_batch([s1, a1, g1, parent, child])
    driver.commit()

    repo = NodeRepository(conn)

    node = repo.get_by_id("parent_node")
    assert node.name == "main"

    with pytest.raises(NotFoundError):
        repo.get_by_id("missing")

    nodes = repo.list_by_graph("g1")
    assert len(nodes) == 2

    # Graph Traversal
    fetched_parent = repo.get_parent("child_node")
    assert fetched_parent is not None
    assert fetched_parent.node_id == "parent_node"

    assert repo.get_parent("parent_node") is None

    children = repo.get_children("parent_node")
    assert len(children) == 1
    assert children[0].node_id == "child_node"

    driver.close()
