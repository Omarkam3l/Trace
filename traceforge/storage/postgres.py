"""PostgreSQL storage adapter — reserved for a future release.

Not part of the current SDK-core milestone (Memory / JSONL / SQLite only).
The interface below documents the intended shape so implementers have a
clear contract to fill in; it deliberately raises rather than pretending
to work.
"""

from __future__ import annotations

from collections.abc import Sequence

from traceforge.models.span import SpanModel
from traceforge.storage.base import StorageAdapter


class PostgresStorage(StorageAdapter):
    """Not yet implemented. Tracked on the roadmap (see docs/roadmap.md)."""

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    async def write_spans(self, spans: Sequence[SpanModel]) -> None:
        raise NotImplementedError(
            "PostgresStorage is not implemented yet; use MemoryStorage, "
            "JSONLStorage, or SQLiteStorage, or contribute this adapter."
        )

    async def query_spans(
        self,
        *,
        trace_id: str | None = None,
        correlation_id: str | None = None,
        limit: int = 100,
    ) -> list[SpanModel]:
        raise NotImplementedError

    async def close(self) -> None:
        return None
