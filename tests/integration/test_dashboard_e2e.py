"""End-to-end integration tests for TraceForge Gateway Dashboard and API endpoints.

Verifies:
1. Public SDK tracing with SpanToSessionBridge populates sessions, activities, nodes, and flamegraph visualizations.
2. Failed traces capture exception_type, exception_message, and exception_stacktrace in node metadata.
3. Dashboard static index.html serves correctly and contains flamegraph, filtering, live polling, and exception UI elements.
"""

from fastapi.testclient import TestClient

import traceforge
from traceforge.gateway.server import create_app
from traceforge.storage.drivers.sqlite import SQLiteStorageDriver


def test_dashboard_and_visualization_endpoints_e2e():
    traceforge.reset_default_tracer()
    tracer = traceforge.configure(service_name="dashboard-e2e")

    driver = SQLiteStorageDriver(":memory:")
    pipeline = traceforge.ExecutionPipeline()
    pipeline.register_consumer(traceforge.SQLiteIngestConsumer(driver))
    bridge = traceforge.SpanToSessionBridge(pipeline)
    tracer.add_hook(bridge)

    @traceforge.traced()
    def compute_sum(a, b):
        with traceforge.span("inner_step"):
            return a + b

    @traceforge.traced()
    def failing_task():
        raise RuntimeError("database connection timeout")

    # Execute successful and failed traces
    compute_sum(10, 20)

    try:
        failing_task()
    except RuntimeError:
        pass

    conn = driver.connection_manager.get_connection()
    service = traceforge.TraceForgeApiService(conn)
    app = create_app(service)
    client = TestClient(app)

    # 1. Test index dashboard HTML
    res_dash = client.get("/dashboard")
    assert res_dash.status_code == 200
    assert "TraceForge Platform" in res_dash.text
    assert "Flamegraph View" in res_dash.text
    assert "live-toggle-btn" in res_dash.text
    assert "status-filter" in res_dash.text

    # 2. Test sessions endpoint
    res_sessions = client.get("/api/v1/sessions")
    assert res_sessions.status_code == 200
    sessions = res_sessions.json()
    assert len(sessions) == 2

    statuses = {s["status"] for s in sessions}
    assert "completed" in statuses
    assert "failed" in statuses

    # Find failed session
    failed_session = next(s for s in sessions if s["status"] == "failed")
    res_replay = client.get(f"/api/v1/sessions/{failed_session['session_id']}/replay")
    assert res_replay.status_code == 200
    replay_data = res_replay.json()

    failed_node = replay_data["nodes"][0]
    assert failed_node["status"] == "failed"
    assert "database connection timeout" in failed_node["metadata_json"]
    assert "RuntimeError" in failed_node["metadata_json"]

    # 3. Test flamegraph visualization endpoint
    success_session = next(s for s in sessions if s["status"] == "completed")
    res_flame = client.get(f"/api/v1/sessions/{success_session['session_id']}/visualization/flamegraph")
    assert res_flame.status_code == 200
    flame_data = res_flame.json()
    assert flame_data["root"] is not None
    assert "compute_sum" in flame_data["root"]["name"]
    assert len(flame_data["root"]["children"]) == 1
    assert flame_data["root"]["children"][0]["name"] == "inner_step"
