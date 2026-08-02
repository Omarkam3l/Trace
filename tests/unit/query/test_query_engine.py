"""Unit tests for QueryEngine facade and query object execution."""

from __future__ import annotations

from datetime import datetime, timezone

from traceforge.query.engine import QueryEngine
from traceforge.query.queries import ActivityQuery, GraphQuery, NodeQuery, RawEventQuery, SessionQuery
from traceforge.storage.drivers.sqlite import SQLiteStorageDriver
from traceforge.storage.records import ActivityRecord, GraphRecord, NodeRecord, RawEventRecord, SessionRecord


def test_query_engine_facade_execution():
    driver = SQLiteStorageDriver(":memory:")
    conn = driver.connection_manager.get_connection()

    now = datetime.now(timezone.utc)
    s1 = SessionRecord(session_id="s1", started_at=now, status="completed", environment_os="win32", environment_python="3.13", profile_name="standard")
    a1 = ActivityRecord(activity_id="act1", session_id="s1", name="Checkout", started_at=now, status="completed", graph_id="g1")
    g1 = GraphRecord(graph_id="g1", activity_id="act1", node_ids=["n1"], relationship_ids=[])
    n1 = NodeRecord(node_id="n1", graph_id="g1", type="function", name="main", started_at=now, status="completed")
    e1 = RawEventRecord(event_id="e1", timestamp=now, sequence=1, type="FunctionEntered", source="python_sdk", context_id="s1")

    driver.begin_transaction()
    driver.write_batch([s1, a1, g1, n1, e1])
    driver.commit()

    engine = QueryEngine(conn)

    sessions = engine.execute_session_query(SessionQuery(session_id="s1"))
    assert len(sessions) == 1
    assert sessions[0].session_id == "s1"

    activities = engine.execute_activity_query(ActivityQuery(session_id="s1"))
    assert len(activities) == 1
    assert activities[0].activity_id == "act1"

    graphs = engine.execute_graph_query(GraphQuery(graph_id="g1"))
    assert len(graphs) == 1

    nodes = engine.execute_node_query(NodeQuery(graph_id="g1"))
    assert len(nodes) == 1

    events = engine.execute_raw_event_query(RawEventQuery(session_id="s1"))
    assert len(events) == 1

    driver.close()
