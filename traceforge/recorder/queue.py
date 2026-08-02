"""A thin, thread-safe queue wrapper used to hand finished spans from the
(sync, hot-path) Tracer over to the (async, background) Recorder.

Wraps ``queue.SimpleQueue`` because it's lock-free, safe to call from any
thread (or from inside a coroutine — put is non-blocking), and requires no
extra dependency.
"""

from __future__ import annotations

import queue
from typing import Generic, TypeVar

T = TypeVar("T")


class SpanQueue(Generic[T]):  # noqa: UP046
    """A non-blocking-put, blocking-with-timeout-get queue."""

    def __init__(self) -> None:
        self._queue: queue.SimpleQueue[T] = queue.SimpleQueue()

    def put(self, item: T) -> None:
        """Never blocks; safe to call from the traced application's hot path."""
        self._queue.put_nowait(item)

    def get(self, timeout: float) -> T:
        """Blocks up to ``timeout`` seconds; raises ``queue.Empty`` on timeout."""
        return self._queue.get(block=True, timeout=timeout)

    def empty(self) -> bool:
        return self._queue.empty()

    def qsize(self) -> int:
        return self._queue.qsize()
