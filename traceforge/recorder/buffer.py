"""Size/time-based batching buffer.

Decides *when* to flush accumulated spans: once ``batch_size`` items have
accumulated, or ``flush_interval`` seconds have elapsed since the last
flush — whichever comes first. This keeps storage/exporter I/O calls
batched (efficient) without letting spans sit unflushed indefinitely.
"""

from __future__ import annotations

import time
from typing import Generic, TypeVar

T = TypeVar("T")


class BatchBuffer(Generic[T]):  # noqa: UP046 - kept for clarity/consistency with SpanQueue
    """Accumulates items and reports when they should be flushed."""

    def __init__(self, batch_size: int, flush_interval: float) -> None:
        self._batch_size = batch_size
        self._flush_interval = flush_interval
        self._items: list[T] = []
        self._last_flush = time.monotonic()

    def add(self, item: T) -> None:
        self._items.append(item)

    def should_flush(self) -> bool:
        if not self._items:
            return False
        if len(self._items) >= self._batch_size:
            return True
        return (time.monotonic() - self._last_flush) >= self._flush_interval

    def drain(self) -> list[T]:
        items, self._items = self._items, []
        self._last_flush = time.monotonic()
        return items

    def __len__(self) -> int:
        return len(self._items)
