"""Unit tests for TraceForgeApiService workflows."""

from __future__ import annotations

from datetime import datetime, timezone

from traceforge.service.service import TraceForgeApiService
from traceforge.storage.drivers.sqlite import SQLiteStorageDriver
from traceforge.storage.records import ActivityRecord, GraphRecord, NodeRecord, SessionRecord


def test_api_service_full_workflow():
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
    s2 = SessionRecord(
        session_id="s2",
        started_at=now,
        status="completed",
        environment_os="win32",
        environment_python="3.13",
        profile_name="standard",
    )

    a1 = ActivityRecord(
        activity_id="act1", session_id="s1", name="Checkout", started_at=now, status="completed", graph_id="g1"
    )
    a2 = ActivityRecord(
        activity_id="act2", session_id="s2", name="Checkout", started_at=now, status="completed", graph_id="g2"
    )

    g1 = GraphRecord(graph_id="g1", activity_id="act1", node_ids=["n1"], relationship_ids=[])
    g2 = GraphRecord(graph_id="g2", activity_id="act2", node_ids=["n1", "n2"], relationship_ids=[])

    n1 = NodeRecord(
        node_id="n1", graph_id="g1", type="function", name="main", started_at=now, duration_ms=10.0, status="completed"
    )
    n2 = NodeRecord(
        node_id="n2",
        graph_id="g2",
        type="function",
        name="helper",
        started_at=now,
        duration_ms=20.0,
        status="completed",
    )

    driver.begin_transaction()
    driver.write_batch([s1, s2, a1, a2, g1, g2, n1, n2])
    driver.commit()

    service = TraceForgeApiService(conn)

    # 1. Session query
    sess = service.get_session("s1")
    assert sess.session_id == "s1"

    sessions = service.list_sessions()
    assert len(sessions) == 2

    # 2. Replay session
    replay = service.replay_session("s1")
    assert replay.session.session_id == "s1"
    assert len(replay.activities) == 1

    # 3. Compare sessions
    diff = service.compare_sessions("s1", "s2")
    assert diff.baseline_session_id == "s1"
    assert diff.target_session_id == "s2"

    # 4. Export session and diff
    json_export = service.export_session("s1")
    assert '"session_id": "s1"' in json_export

    diff_export = service.export_diff("s1", "s2")
    assert "Execution Diff Report" in diff_export or '"baseline_session_id": "s1"' in diff_export

    # 5. Visualizations
    graph_vm = service.get_graph_visualization("s1")
    assert len(graph_vm.nodes) == 1

    diff_vm = service.get_diff_visualization("s1", "s2")
    assert diff_vm.baseline_id == "s1"

    driver.close()
