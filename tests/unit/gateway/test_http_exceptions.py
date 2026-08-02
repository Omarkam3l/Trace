"""Unit tests for HTTP Gateway Layer exception handling and status codes."""

from __future__ import annotations

from fastapi.testclient import TestClient

from traceforge.gateway.server import create_app
from traceforge.service.service import TraceForgeApiService
from traceforge.storage.drivers.sqlite import SQLiteStorageDriver


def test_http_gateway_not_found_handling():
    driver = SQLiteStorageDriver(":memory:")
    conn = driver.connection_manager.get_connection()

    service = TraceForgeApiService(conn)
    app = create_app(service)
    client = TestClient(app)

    res = client.get("/api/v1/sessions/non_existent")
    assert res.status_code == 404
    assert res.json()["error_type"] == "NotFoundError"

    driver.close()
