"""JSON exporter: appends each batch of finished spans to a JSON-lines file
or an in-memory sink, for downstream tooling to consume.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Sequence
from pathlib import Path

from traceforge.models.span import SpanModel
from traceforge.utils.serialization import dumps


class JSONExporter:
    """Exports spans as JSON.

    If ``path`` is given, appends one JSON array per batch (one line per
    batch) to that file. If ``sink`` is given instead, calls ``sink(json_str)``
    for each batch — useful for wiring into custom transports in tests.
    """

    def __init__(
        self,
        path: str | Path | None = None,
        *,
        sink: Callable[[str], None] | None = None,
    ) -> None:
        if (path is None) == (sink is None):
            raise ValueError("JSONExporter requires exactly one of `path` or `sink`")
        self._path = Path(path) if path else None
        if self._path:
            self._path.parent.mkdir(parents=True, exist_ok=True)
        self._sink = sink
        self._lock = asyncio.Lock()

    async def export(self, spans: Sequence[SpanModel]) -> None:
        if not spans:
            return
        payload = dumps(list(spans)) + "\n"
        if self._sink is not None:
            self._sink(payload)
            return
        async with self._lock:
            await asyncio.to_thread(self._append, payload)

    def _append(self, payload: str) -> None:
        assert self._path is not None
        with self._path.open("a", encoding="utf-8") as f:
            f.write(payload)

    async def shutdown(self) -> None:
        return None
