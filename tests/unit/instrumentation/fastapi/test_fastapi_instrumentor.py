"""Integration tests for FastAPIInstrumentor.

Before this file, traceforge.instrumentation.fastapi was an empty stub --
these tests exercise it against a real FastAPI app via TestClient (real
ASGI request/response cycle), not mocks, and confirm it composes with the
rest of the tracing pipeline (SpanToSessionBridge -> QueryEngine) built
earlier this session.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

import traceforge
from traceforge.instrumentation.fastapi import FastAPIInstrumentor
from traceforge.models.span import SpanModel
from traceforge.storage.drivers.sqlite import SQLiteStorageDriver


class _CaptureHook:
    """Minimal SpanLifecycleHook that just records finished spans."""

    def __init__(self) -> None:
        self.spans: list[SpanModel] = []

    def on_span_start(self, span: SpanModel) -> None:
        pass

    def on_span_end(self, span: SpanModel) -> None:
        self.spans.append(span)


def _make_app() -> FastAPI:
    app = FastAPI()

    @app.get("/hello/{name}")
    def hello(name: str) -> dict[str, str]:
        return {"msg": f"hi {name}"}

    @app.get("/boom")
    def boom() -> None:
        raise ValueError("kaboom")

    return app


def test_successful_request_produces_a_server_span():
    traceforge.reset_default_tracer()
    tracer = traceforge.configure(service_name="fastapi-test")
    hook = _CaptureHook()
    tracer.add_hook(hook)

    app = _make_app()
    FastAPIInstrumentor(app).install(tracer)
    client = TestClient(app)

    response = client.get("/hello/omar")

    assert response.status_code == 200
    assert response.json() == {"msg": "hi omar"}
    assert len(hook.spans) == 1
    span = hook.spans[0]
    assert span.name in ("GET /hello/{name}".replace("{name}", "omar"), "GET /hello/omar")
    assert span.kind.value == "server" if hasattr(span.kind, "value") else span.kind == "server"
    assert span.status.value == "ok" if hasattr(span.status, "value") else span.status == "ok"
    assert span.attributes["http.method"] == "GET"
    assert span.attributes["http.status_code"] == 200


def test_exception_in_handler_is_captured_and_still_propagates():
    traceforge.reset_default_tracer()
    tracer = traceforge.configure(service_name="fastapi-test-exc")
    hook = _CaptureHook()
    tracer.add_hook(hook)

    app = _make_app()
    FastAPIInstrumentor(app).install(tracer)
    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/boom")

    assert response.status_code == 500
    assert len(hook.spans) == 1
    span = hook.spans[0]
    assert span.status.value == "error" if hasattr(span.status, "value") else span.status == "error"
    assert span.exception is not None
    assert span.exception.type == "ValueError"
    assert span.exception.message == "kaboom"


def test_uninstall_stops_recording_new_spans():
    traceforge.reset_default_tracer()
    tracer = traceforge.configure(service_name="fastapi-test-uninstall")
    hook = _CaptureHook()
    tracer.add_hook(hook)

    app = _make_app()
    instrumentor = FastAPIInstrumentor(app)
    instrumentor.install(tracer)
    client = TestClient(app)

    client.get("/hello/a")
    assert len(hook.spans) == 1

    instrumentor.uninstall()
    response = client.get("/hello/b")

    assert response.status_code == 200  # app still works, just not traced
    assert len(hook.spans) == 1  # no new span recorded


def test_double_install_raises():
    tracer = traceforge.configure(service_name="fastapi-test-double")
    app = _make_app()
    instrumentor = FastAPIInstrumentor(app)
    instrumentor.install(tracer)

    try:
        instrumentor.install(tracer)
        assert False, "expected RuntimeError"
    except RuntimeError:
        pass


def test_traced_requests_reach_query_engine_via_bridge():
    """The actual point of instrumentation: real HTTP requests must be

    queryable/replayable, not just captured as spans in isolation. Exercises
    the full pipeline: FastAPIInstrumentor -> Tracer -> SpanToSessionBridge ->
    SQLiteIngestConsumer -> QueryEngine.
    """
    traceforge.reset_default_tracer()
    tracer = traceforge.configure(service_name="fastapi-bridge-test")

    driver = SQLiteStorageDriver(":memory:")
    pipeline = traceforge.ExecutionPipeline()
    pipeline.register_consumer(traceforge.SQLiteIngestConsumer(driver))
    tracer.add_hook(traceforge.SpanToSessionBridge(pipeline))

    app = _make_app()
    FastAPIInstrumentor(app).install(tracer)
    client = TestClient(app)

    client.get("/hello/bridge-test")

    conn = driver.connection_manager.get_connection()
    qe = traceforge.QueryEngine(conn)
    sessions = qe.sessions.list()
    assert len(sessions) == 1
    assert sessions[0].status == "completed"
