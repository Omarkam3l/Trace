"""JSONL (newline-delimited JSON) storage adapter.

Appends one span per line to a file, suitable for local debugging,
log-shipping pipelines, or offline analysis. File I/O is offloaded to a
thread via ``asyncio.to_thread`` so it never blocks the event loop, and
writes are serialized by an ``asyncio.Lock`` to keep lines from interleaving.
"""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from pathlib import Path

from traceforge.models.span import SpanModel
from traceforge.storage.base import StorageAdapter
from traceforge.utils.serialization import dumps


class JSONLStorage(StorageAdapter):
    """Append-only JSONL file storage."""

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()

    async def write_spans(self, spans: Sequence[SpanModel]) -> None:
        if not spans:
            return
        lines = "\n".join(dumps(span) for span in spans) + "\n"
        async with self._lock:
            await asyncio.to_thread(self._append, lines)

    def _append(self, lines: str) -> None:
        with self._path.open("a", encoding="utf-8") as f:
            f.write(lines)

    async def query_spans(
        self,
        *,
        trace_id: str | None = None,
        correlation_id: str | None = None,
        limit: int = 100,
    ) -> list[SpanModel]:
        async with self._lock:
            rows = await asyncio.to_thread(self._read_all)
        results = [
            row
            for row in rows
            if (trace_id is None or row.trace_id == trace_id)
            and (correlation_id is None or row.correlation_id == correlation_id)
        ]
        return results[-limit:]

    def _read_all(self) -> list[SpanModel]:
        if not self._path.exists():
            return []
        spans: list[SpanModel] = []
        with self._path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    spans.append(SpanModel.model_validate_json(line))
        return spans

    async def close(self) -> None:
        return None
