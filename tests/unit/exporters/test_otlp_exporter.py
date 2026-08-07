"""Integration tests for OTLPExporter.

Prior to this file, OTLPExporter had zero dedicated test coverage -- only
a bare `hasattr(traceforge, "OTLPExporter")` check in test_public_api.py.
Nothing confirmed it actually sent a well-formed request anywhere.

These tests spin up a real local HTTP server and point OTLPExporter at it,
so we're asserting against an actual received HTTP request/body -- not a
mocked urlopen call -- to catch things a mock could hide (wrong method,
wrong content-type, malformed JSON, connection handling).
"""

from __future__ import annotations

import json
import threading
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

import pytest

from traceforge.exporters.otlp import OTLPExporter
from traceforge.models.enums import SpanKind, SpanStatus
from traceforge.models.span import SpanModel


def make_span(**overrides: Any) -> SpanModel:
    defaults = dict(
        id="s1",
        trace_id="t1",
        name="handle-request",
        kind=SpanKind.INTERNAL,
        status=SpanStatus.OK,
        start_time=datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC),
        end_time=datetime(2026, 1, 1, 12, 0, 1, tzinfo=UTC),
        duration_ms=1000.0,
    )
    defaults.update(overrides)
    return SpanModel(**defaults)


class _CapturingHandler(BaseHTTPRequestHandler):
    """Records the last request it received onto the server instance."""

    def do_POST(self) -> None:  # noqa: N802 (stdlib naming convention)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        self.server.last_request = {  # type: ignore[attr-defined]
            "path": self.path,
            "method": "POST",
            "content_type": self.headers.get("Content-Type"),
            "body": body,
        }
        self.send_response(200)
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:  # silence stdlib access logs
        pass


@pytest.fixture
def capturing_server():
    server = HTTPServer(("127.0.0.1", 0), _CapturingHandler)
    server.last_request = None
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        thread.join(timeout=2)


async def test_export_sends_a_post_request_with_json_body(capturing_server):
    port = capturing_server.server_address[1]
    exporter = OTLPExporter(endpoint=f"http://127.0.0.1:{port}/v1/traces", service_name="my-service")

    await exporter.export([make_span()])

    assert capturing_server.last_request is not None
    assert capturing_server.last_request["method"] == "POST"
    assert capturing_server.last_request["path"] == "/v1/traces"
    assert capturing_server.last_request["content_type"] == "application/json"


async def test_export_body_matches_otlp_resource_spans_shape(capturing_server):
    port = capturing_server.server_address[1]
    exporter = OTLPExporter(endpoint=f"http://127.0.0.1:{port}/v1/traces", service_name="checkout-service")

    await exporter.export([make_span(id="span-abc", trace_id="trace-xyz", name="checkout")])

    body = json.loads(capturing_server.last_request["body"])
    resource_spans = body["resourceSpans"][0]

    # Service name propagates as a resource attribute.
    service_attrs = resource_spans["resource"]["attributes"]
    assert {"key": "service.name", "value": "checkout-service"} in service_attrs

    span = resource_spans["scopeSpans"][0]["spans"][0]
    assert span["traceId"] == "trace-xyz"
    assert span["spanId"] == "span-abc"
    assert span["name"] == "checkout"
    assert span["kind"] == "INTERNAL"
    assert span["status"]["code"] == "OK"
    assert isinstance(span["startTimeUnixNano"], int)
    assert isinstance(span["endTimeUnixNano"], int)
    assert span["endTimeUnixNano"] > span["startTimeUnixNano"]


async def test_export_batches_multiple_spans_in_one_request(capturing_server):
    port = capturing_server.server_address[1]
    exporter = OTLPExporter(endpoint=f"http://127.0.0.1:{port}/v1/traces")

    await exporter.export([make_span(id="a"), make_span(id="b"), make_span(id="c")])

    body = json.loads(capturing_server.last_request["body"])
    spans = body["resourceSpans"][0]["scopeSpans"][0]["spans"]
    assert len(spans) == 3
    assert {s["spanId"] for s in spans} == {"a", "b", "c"}


async def test_export_with_no_spans_sends_nothing(capturing_server):
    exporter = OTLPExporter(endpoint=f"http://127.0.0.1:{capturing_server.server_address[1]}/v1/traces")
    await exporter.export([])
    assert capturing_server.last_request is None


async def test_export_to_unreachable_endpoint_does_not_raise():
    """Fire-and-forget semantics: a dead collector must not crash the

    caller's tracing code path. It should log and swallow the error.
    """
    # Port 1 is a reserved, always-refused port on all platforms in a
    # sandboxed test environment -- guaranteed connection failure without
    # relying on external network state.
    exporter = OTLPExporter(endpoint="http://127.0.0.1:1/v1/traces", timeout=1.0)
    await exporter.export([make_span()])  # must not raise


async def test_shutdown_is_a_safe_noop():
    exporter = OTLPExporter(endpoint="http://127.0.0.1:9/v1/traces")
    await exporter.shutdown()  # must not raise
