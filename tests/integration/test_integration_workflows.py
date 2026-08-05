"""Integration tests for TraceForge platform HTTP gateway endpoints & service."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from traceforge.gateway.server import create_app
from traceforge.service.service import TraceForgeApiService
from traceforge.storage.drivers.sqlite import SQLiteStorageDriver
from traceforge.storage.records import SessionRecord


def test_integration_health_and_metrics():
    driver = SQLiteStorageDriver(":memory:")
    conn = driver.connection_manager.get_connection()

    now = datetime.now(timezone.utc)
    s1 = SessionRecord(session_id="s1", started_at=now, status="completed", environment_os="win32", environment_python="3.12", profile_name="standard")
    driver.begin_transaction()
    driver.write_batch([s1])
    driver.commit()

    service = TraceForgeApiService(conn)
    app = create_app(service)
    client = TestClient(app)

    # 1. Check health
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

    # 2. Check ready
    res = client.get("/api/v1/ready")
    assert res.status_code == 200
    assert res.json()["status"] == "ready"

    # 3. Check status
    res = client.get("/api/v1/status")
    assert res.status_code == 200
    assert res.json()["status"] == "running"

    # 4. Check metrics
    res = client.get("/api/v1/metrics")
    assert res.status_code == 200
    assert "uptime" in res.json()

    # 5. Check dashboard root
    res = client.get("/")
    assert res.status_code == 200
    assert "TraceForge Platform" in res.text

    driver.close()
