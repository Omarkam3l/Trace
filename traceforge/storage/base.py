"""The pluggable storage interface.

Any storage backend (memory, JSONL, SQLite, Postgres, ...) implements this
ABC. TraceForge's core engine never imports a concrete storage class —
only this interface — which is what makes storage pluggable.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from traceforge.models.span import SpanModel


class StorageAdapter(ABC):
    """Async, pluggable persistence for finished spans."""

    @abstractmethod
    async def write_spans(self, spans: Sequence[SpanModel]) -> None:
        """Persist a batch of finished spans."""
        raise NotImplementedError

    @abstractmethod
    async def query_spans(
        self,
        *,
        trace_id: str | None = None,
        correlation_id: str | None = None,
        limit: int = 100,
    ) -> list[SpanModel]:
        """Retrieve spans, optionally filtered by trace or correlation ID."""
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        """Release any underlying resources (file handles, connections)."""
        raise NotImplementedError

    async def __aenter__(self) -> StorageAdapter:
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.close()
