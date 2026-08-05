"""Unit tests for ReplayMode scope filtering (GRAPH_ONLY, TIMELINE_ONLY, SNAPSHOT_ONLY)."""

from __future__ import annotations

from datetime import datetime, timezone

from traceforge.query.engine import QueryEngine
from traceforge.replay.config import ReplayConfig, ReplayMode
from traceforge.replay.engine import ReplayEngine
from traceforge.storage.drivers.sqlite import SQLiteStorageDriver
from traceforge.storage.records import (
    ActivityRecord,
    GraphRecord,
    NodeRecord,
    RawEventRecord,
    SessionRecord,
    SnapshotRecord,
)


def test_replay_mode_filtering():
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
    g1 = GraphRecord(graph_id="g1", activity_id="act1", node_ids=["n1"], relationship_ids=[])
    n1 = NodeRecord(node_id="n1", graph_id="g1", type="function", name="main", started_at=now, status="completed")
    e1 = RawEventRecord(
        event_id="e1", timestamp=now, sequence=1, type="FunctionEntered", source="python_sdk", context_id="s1"
    )
    snap1 = SnapshotRecord(snapshot_id="snap1", session_id="s1", timestamp=now, nodes_count=1)

    driver.begin_transaction()
    driver.write_batch([s1, a1, g1, n1, e1, snap1])
    driver.commit()

    query_engine = QueryEngine(conn)
    replay_engine = ReplayEngine(query_engine)

    # GRAPH_ONLY mode
    res_graph = replay_engine.replay_session("s1", config=ReplayConfig(mode=ReplayMode.GRAPH_ONLY))
    assert len(res_graph.graphs) == 1
    assert len(res_graph.timeline) == 0

    # TIMELINE_ONLY mode
    res_time = replay_engine.replay_session("s1", config=ReplayConfig(mode=ReplayMode.TIMELINE_ONLY))
    assert len(res_time.graphs) == 0
    assert len(res_time.timeline) == 1

    driver.close()
