"""WebSocket exporter: streams finished spans to connected clients in
real time (e.g. a live trace-viewer dashboard).

The ``websockets`` package is an optional dependency — install with
``pip install traceforge[websocket]``. It's imported lazily so the rest
of TraceForge has zero hard dependency on it.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from traceforge.api.exceptions import ExporterError
from traceforge.models.span import SpanModel
from traceforge.utils.logger import get_logger
from traceforge.utils.serialization import dumps

if TYPE_CHECKING:
    from websockets.asyncio.server import ServerConnection

_logger = get_logger(__name__)


class WebSocketExporter:
    """Broadcasts finished spans as JSON to all connected WebSocket clients.

    Usage::

        exporter = WebSocketExporter(host="localhost", port=8765)
        await exporter.start()   # begin accepting connections
        ...
        await exporter.shutdown()
    """

    def __init__(self, host: str = "localhost", port: int = 8765) -> None:
        try:
            import websockets  # noqa: F401
        except ImportError as exc:  # pragma: no cover - exercised only without extra installed
            raise ExporterError(
                "WebSocketExporter requires the optional 'websockets' package. "
                "Install it with: pip install traceforge[websocket]"
            ) from exc

        self._host = host
        self._port = port
        self._clients: set[ServerConnection] = set()
        self._server: Any = None

    async def start(self) -> None:
        import websockets

        async def _handler(connection: ServerConnection) -> None:
            self._clients.add(connection)
            try:
                async for _ in connection:
                    pass  # this exporter is send-only; ignore client messages
            finally:
                self._clients.discard(connection)

        self._server = await websockets.serve(_handler, self._host, self._port)
        _logger.info("traceforge: websocket exporter listening on %s:%s", self._host, self._port)

    async def export(self, spans: Sequence[SpanModel]) -> None:
        if not self._clients or not spans:
            return
        payload = dumps(list(spans))
        stale = set()
        for client in list(self._clients):
            try:
                await client.send(payload)
            except Exception:  # noqa: BLE001
                stale.add(client)
        self._clients -= stale

    async def shutdown(self) -> None:
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
        self._clients.clear()
