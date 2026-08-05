"""End-to-end platform workflows test."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from traceforge.gateway.server import create_app
from traceforge.service.service import TraceForgeApiService
from traceforge.storage.drivers.sqlite import SQLiteStorageDriver
from traceforge.storage.records import ActivityRecord, GraphRecord, NodeRecord, SessionRecord


def test_e2e_session_lifecycle_replay_diff_export_vis():
    driver = SQLiteStorageDriver(":memory:")
    conn = driver.connection_manager.get_connection()

    now = datetime.now(UTC)
    s1 = SessionRecord(
        session_id="e2e_s1",
        started_at=now,
        status="completed",
        environment_os="win32",
        environment_python="3.12",
        profile_name="standard",
    )
    s2 = SessionRecord(
        session_id="e2e_s2",
        started_at=now,
        status="completed",
        environment_os="win32",
        environment_python="3.12",
        profile_name="standard",
    )

    a1 = ActivityRecord(
        activity_id="act1", session_id="e2e_s1", name="Checkout", started_at=now, status="completed", graph_id="g1"
    )
    g1 = GraphRecord(graph_id="g1", activity_id="act1", node_ids=["n1"], relationship_ids=[])
    n1 = NodeRecord(
        node_id="n1",
        graph_id="g1",
        type="function",
        name="process_payment",
        started_at=now,
        duration_ms=15.5,
        status="completed",
    )

    driver.begin_transaction()
    driver.write_batch([s1, s2, a1, g1, n1])
    driver.commit()

    service = TraceForgeApiService(conn)
    app = create_app(service)
    client = TestClient(app)

    # 1. Fetch Session List
    r_sessions = client.get("/api/v1/sessions")
    assert r_sessions.status_code == 200
    assert len(r_sessions.json()) == 2

    # 2. Replay Session
    r_replay = client.get("/api/v1/sessions/e2e_s1/replay")
    assert r_replay.status_code == 200
    assert r_replay.json()["session"]["session_id"] == "e2e_s1"

    # 3. Compare Sessions
    r_diff = client.post("/api/v1/diff", json={"baseline_id": "e2e_s1", "target_id": "e2e_s2"})
    assert r_diff.status_code == 200
    assert r_diff.json()["baseline_session_id"] == "e2e_s1"

    # 4. Export Artifacts
    r_export = client.get("/api/v1/sessions/e2e_s1/export?format=json")
    assert r_export.status_code == 200
    assert '"session_id": "e2e_s1"' in r_export.text

    # 5. Fetch Visualization Models
    r_graph = client.get("/api/v1/sessions/e2e_s1/visualization/graph")
    assert r_graph.status_code == 200
    assert len(r_graph.json()["nodes"]) == 1

    driver.close()
