"""Unit tests for FastAPI HTTP Gateway Layer endpoints using TestClient."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from traceforge.gateway.server import create_app
from traceforge.service.service import TraceForgeApiService
from traceforge.storage.drivers.sqlite import SQLiteStorageDriver
from traceforge.storage.records import ActivityRecord, GraphRecord, NodeRecord, SessionRecord


def test_http_gateway_endpoints():
    driver = SQLiteStorageDriver(":memory:")
    conn = driver.connection_manager.get_connection()

    now = datetime.now(timezone.utc)
    s1 = SessionRecord(session_id="s1", started_at=now, status="completed", environment_os="win32", environment_python="3.13", profile_name="standard")
    s2 = SessionRecord(session_id="s2", started_at=now, status="completed", environment_os="win32", environment_python="3.13", profile_name="standard")

    a1 = ActivityRecord(activity_id="act1", session_id="s1", name="Checkout", started_at=now, status="completed", graph_id="g1")
    g1 = GraphRecord(graph_id="g1", activity_id="act1", node_ids=["n1"], relationship_ids=[])
    n1 = NodeRecord(node_id="n1", graph_id="g1", type="function", name="main", started_at=now, status="completed")

    driver.begin_transaction()
    driver.write_batch([s1, s2, a1, g1, n1])
    driver.commit()

    service = TraceForgeApiService(conn)
    app = create_app(service)
    client = TestClient(app)

    # 1. List sessions
    res = client.get("/api/v1/sessions")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2

    # 2. Get session by ID
    res = client.get("/api/v1/sessions/s1")
    assert res.status_code == 200
    assert res.json()["session_id"] == "s1"

    # 3. Replay session
    res = client.get("/api/v1/sessions/s1/replay")
    assert res.status_code == 200
    assert res.json()["session"]["session_id"] == "s1"

    # 4. Compare sessions
    res = client.post("/api/v1/diff", json={"baseline_id": "s1", "target_id": "s2"})
    assert res.status_code == 200
    assert res.json()["baseline_session_id"] == "s1"

    # 5. Export session
    res = client.get("/api/v1/sessions/s1/export?format=json")
    assert res.status_code == 200
    assert '"session_id": "s1"' in res.text

    # 6. Visualization graph
    res = client.get("/api/v1/sessions/s1/visualization/graph")
    assert res.status_code == 200
    assert len(res.json()["nodes"]) == 1

    driver.close()
