"""In-memory storage adapter.

Useful for tests, local development, and short-lived processes. Not
durable — all data is lost when the process exits.
"""

from __future__ import annotations

import asyncio
from collections import deque
from collections.abc import Sequence

from traceforge.models.span import SpanModel
from traceforge.storage.base import StorageAdapter


class MemoryStorage(StorageAdapter):
    """Thread/task-safe, bounded, append-only in-memory span store."""

    def __init__(self, max_spans: int = 100_000) -> None:
        self._spans: deque[SpanModel] = deque(maxlen=max_spans)
        self._lock = asyncio.Lock()

    async def write_spans(self, spans: Sequence[SpanModel]) -> None:
        async with self._lock:
            self._spans.extend(spans)

    async def query_spans(
        self,
        *,
        trace_id: str | None = None,
        correlation_id: str | None = None,
        limit: int = 100,
    ) -> list[SpanModel]:
        async with self._lock:
            results = [
                s
                for s in self._spans
                if (trace_id is None or s.trace_id == trace_id)
                and (correlation_id is None or s.correlation_id == correlation_id)
            ]
        return results[-limit:]

    async def close(self) -> None:
        return None

    def __len__(self) -> int:
        return len(self._spans)
