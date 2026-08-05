"""Unit tests for SQLiteIngestConsumer."""

from __future__ import annotations

from datetime import UTC, datetime

from traceforge.domain.activity import Activity
from traceforge.domain.enums import ActivityStatus, SessionStatus
from traceforge.domain.environment import Environment
from traceforge.domain.graph import ExecutionGraph
from traceforge.domain.node import ExecutionNode, Relationship
from traceforge.domain.profile import RecordingProfile
from traceforge.domain.session import RecordingSession
from traceforge.pipeline.consumers.sqlite_consumer import SQLiteIngestConsumer
from traceforge.query.engine import QueryEngine
from traceforge.storage.drivers.sqlite import SQLiteStorageDriver


def test_sqlite_ingest_consumer_lifecycle():
    driver = SQLiteStorageDriver(":memory:")
    conn = driver.connection_manager.get_connection()
    consumer = SQLiteIngestConsumer(driver)

    now = datetime.now(UTC)
    env = Environment(os="win32", python_version="3.12")
    profile = RecordingProfile(name="standard")

    # 1. Create Domain Objects
    node1 = ExecutionNode(
        node_id="n1",
        graph_id="g1",
        type="function_call",
        name="test_func_1",
        started_at=now,
        finished_at=now,
        duration_ms=10.0,
        status="completed",
        child_ids=["n2"],
    )
    node2 = ExecutionNode(
        node_id="n2",
        graph_id="g1",
        type="function_call",
        name="test_func_2",
        started_at=now,
        finished_at=now,
        duration_ms=5.0,
        status="completed",
        parent_id="n1",
    )
    rel = Relationship(
        relationship_id="r1",
        graph_id="g1",
        source_node_id="n1",
        target_node_id="n2",
        type="parent_child",
    )
    graph = ExecutionGraph(
        graph_id="g1",
        activity_id="act1",
        nodes={"n1": node1, "n2": node2},
        relationships=[rel],
    )
    activity = Activity(
        activity_id="act1",
        session_id="s1",
        name="Test Activity",
        started_at=now,
        finished_at=now,
        duration_ms=10.0,
        status=ActivityStatus.COMPLETED,
        graph=graph,
    )
    session = RecordingSession(
        session_id="s1",
        started_at=now,
        finished_at=now,
        duration_ms=10.0,
        status=SessionStatus.COMPLETED,
        environment=env,
        profile=profile,
        activities=[activity],
    )

    # 2. Dispatch to Consumer (Order respects FK hierarchy: Session -> Activity -> Graph)
    consumer.on_session_completed(session)
    consumer.on_activity_completed(activity)
    consumer.on_graph_completed(graph)

    # 3. Verify in SQLite database via QueryEngine
    qe = QueryEngine(conn)
    sessions = qe.sessions.list()
    assert len(sessions) == 1
    assert sessions[0].session_id == "s1"

    activities = qe.activities.list_by_session("s1")
    assert len(activities) == 1
    assert activities[0].activity_id == "act1"

    nodes = qe.nodes.list_by_graph("g1")
    assert len(nodes) == 2
    assert {n.node_id for n in nodes} == {"n1", "n2"}

    rels = qe.relationships.list_by_graph("g1")
    assert len(rels) == 1
    assert rels[0].relationship_id == "r1"
