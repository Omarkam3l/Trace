"""Flush policies for determining when BufferManager should flush."""

from __future__ import annotations

import abc
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from traceforge.storage.buffer import BufferManager


class FlushPolicy(abc.ABC):
    """Abstract Base Class for flush policies."""

    @abc.abstractmethod
    def should_flush(self, buffer: BufferManager) -> bool:
        """Return True if the buffer should be flushed."""


class SizeFlushPolicy(FlushPolicy):
    """Flush policy triggered when buffer size reaches or exceeds max_records."""

    def __init__(self, max_records: int = 100) -> None:
        self.max_records = max_records

    def should_flush(self, buffer: BufferManager) -> bool:
        return buffer.size() >= self.max_records


class TimeFlushPolicy(FlushPolicy):
    """Flush policy triggered when elapsed time since last flush exceeds interval_seconds."""

    def __init__(self, interval_seconds: float = 5.0) -> None:
        self.interval_seconds = interval_seconds
        self._last_flush_time = time.monotonic()

    def should_flush(self, buffer: BufferManager) -> bool:
        if buffer.is_empty():
            return False
        elapsed = time.monotonic() - self._last_flush_time
        return elapsed >= self.interval_seconds

    def notify_flushed(self) -> None:
        """Update last flush timestamp after a flush completes."""
        self._last_flush_time = time.monotonic()


class HybridFlushPolicy(FlushPolicy):
    """Default flush policy combining size and time flush conditions with OR logic."""

    def __init__(self, max_records: int = 100, interval_seconds: float = 5.0) -> None:
        self.size_policy = SizeFlushPolicy(max_records=max_records)
        self.time_policy = TimeFlushPolicy(interval_seconds=interval_seconds)

    def should_flush(self, buffer: BufferManager) -> bool:
        return self.size_policy.should_flush(buffer) or self.time_policy.should_flush(buffer)

    def notify_flushed(self) -> None:
        self.time_policy.notify_flushed()
