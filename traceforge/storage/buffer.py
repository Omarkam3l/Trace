"""BufferManager for accumulating immutable storage records in memory."""

from __future__ import annotations

import threading
from collections import deque
from collections.abc import Sequence
from typing import Any

from traceforge.storage.exceptions import BufferOverflowError


class BufferManager:
    """Thread-safe memory buffer for storage records."""

    def __init__(self, max_capacity: int | None = None) -> None:
        self._max_capacity = max_capacity
        self._queue: deque[Any] = deque()
        self._lock = threading.RLock()

    @property
    def max_capacity(self) -> int | None:
        return self._max_capacity

    def append(self, record: Any) -> None:
        """Append a single record to the buffer."""
        with self._lock:
            if self._max_capacity is not None and len(self._queue) >= self._max_capacity:
                raise BufferOverflowError(f"Buffer exceeded maximum capacity of {self._max_capacity}")
            self._queue.append(record)

    def append_many(self, records: Sequence[Any]) -> None:
        """Append multiple records to the buffer in insertion order."""
        with self._lock:
            if self._max_capacity is not None and len(self._queue) + len(records) > self._max_capacity:
                raise BufferOverflowError(f"Buffer append_many exceeds max_capacity of {self._max_capacity}")
            self._queue.extend(records)

    def peek(self) -> list[Any]:
        """Return a copy of buffered records without removing them."""
        with self._lock:
            return list(self._queue)

    def drain(self) -> list[Any]:
        """Drain and return all buffered records, emptying the buffer."""
        with self._lock:
            drained = list(self._queue)
            self._queue.clear()
            return drained

    def clear(self) -> None:
        """Clear all buffered records."""
        with self._lock:
            self._queue.clear()

    def size(self) -> int:
        """Return current buffer size."""
        with self._lock:
            return len(self._queue)

    def is_empty(self) -> bool:
        """Return True if the buffer is empty."""
        with self._lock:
            return len(self._queue) == 0
