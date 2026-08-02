"""OTLP (OpenTelemetry Protocol) exporter.

Ships spans to an OTLP-compatible collector over HTTP using a simplified
JSON encoding of the OTLP data model. A full binary-protobuf OTLP/gRPC
exporter is on the roadmap (see docs/roadmap.md); this HTTP/JSON transport
is enough to interoperate with collectors that accept OTLP/HTTP+JSON.
"""

from __future__ import annotations

import asyncio
import urllib.error
import urllib.request
from collections.abc import Sequence

from traceforge.models.span import SpanModel
from traceforge.utils.logger import get_logger
from traceforge.utils.serialization import dumps, to_jsonable

_logger = get_logger(__name__)


def _span_to_otlp_like(span: SpanModel) -> dict[str, object]:
    """A simplified OTLP-flavored representation of a TraceForge span."""
    return {
        "traceId": span.trace_id,
        "spanId": span.id,
        "parentSpanId": span.parent_span_id,
        "name": span.name,
        "kind": span.kind.value.upper(),
        "startTimeUnixNano": _to_unix_nanos(span.start_time.isoformat()),
        "endTimeUnixNano": _to_unix_nanos(span.end_time.isoformat()) if span.end_time else None,
        "attributes": to_jsonable(span.attributes),
        "status": {"code": span.status.value.upper()},
        "events": [to_jsonable(e) for e in span.events],
    }


def _to_unix_nanos(iso_timestamp: str) -> int:
    from datetime import datetime

    dt = datetime.fromisoformat(iso_timestamp)
    return int(dt.timestamp() * 1_000_000_000)


class OTLPExporter:
    """Posts batches of finished spans to an OTLP/HTTP collector endpoint."""

    def __init__(
        self,
        endpoint: str = "http://localhost:4318/v1/traces",
        *,
        service_name: str = "traceforge-service",
        timeout: float = 5.0,
    ) -> None:
        self._endpoint = endpoint
        self._service_name = service_name
        self._timeout = timeout

    async def export(self, spans: Sequence[SpanModel]) -> None:
        if not spans:
            return
        service_attr = {"key": "service.name", "value": self._service_name}
        body: dict[str, object] = {
            "resourceSpans": [
                {
                    "resource": {"attributes": [service_attr]},
                    "scopeSpans": [{"spans": [_span_to_otlp_like(s) for s in spans]}],
                }
            ]
        }
        await asyncio.to_thread(self._post, body)

    def _post(self, body: dict[str, object]) -> None:
        data = dumps(body).encode("utf-8")
        request = urllib.request.Request(
            self._endpoint,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout):
                pass
        except (urllib.error.URLError, OSError) as exc:
            _logger.warning("traceforge: OTLP export to %s failed: %s", self._endpoint, exc)

    async def shutdown(self) -> None:
        return None
