"""Unit tests for GraphRepository read operations."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from traceforge.query.exceptions import NotFoundError
from traceforge.query.repositories.graph_repository import GraphRepository
from traceforge.storage.drivers.sqlite import SQLiteStorageDriver
from traceforge.storage.records.activity_record import ActivityRecord
from traceforge.storage.records.graph_record import GraphRecord
from traceforge.storage.records.session_record import SessionRecord


def test_graph_read_repository():
    driver = SQLiteStorageDriver(":memory:")
    conn = driver.connection_manager.get_connection()

    now = datetime.now(timezone.utc)
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
    g1 = GraphRecord(graph_id="g1", activity_id="act1", node_ids=["n1", "n2"], relationship_ids=["r1"])

    driver.begin_transaction()
    driver.write_batch([s1, a1, g1])
    driver.commit()

    repo = GraphRepository(conn)

    graph = repo.get_by_id("g1")
    assert graph.graph_id == "g1"
    assert graph.node_ids == ["n1", "n2"]

    with pytest.raises(NotFoundError):
        repo.get_by_id("missing")

    graphs = repo.list_by_activity("act1")
    assert len(graphs) == 1

    driver.close()
