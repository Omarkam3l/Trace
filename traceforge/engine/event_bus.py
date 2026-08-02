"""EventBus for deterministic event publish/subscribe dispatch."""

from __future__ import annotations

import threading
from collections.abc import Callable
from typing import Any

from traceforge.engine.raw_event import RawEvent


class EventBus:
    """Thread-safe, deterministic pub/sub event dispatcher."""

    def __init__(self) -> None:
        self._handlers: list[Callable[[RawEvent], None]] = []
        self._lock = threading.RLock()

    def subscribe(self, handler: Callable[[RawEvent], None]) -> Callable[[], None]:
        """Subscribe a handler function and return an unsubscribe callback."""
        with self._lock:
            if handler not in self._handlers:
                self._handlers.append(handler)

        def unsubscribe() -> None:
            with self._lock:
                if handler in self._handlers:
                    self._handlers.remove(handler)

        return unsubscribe

    def unsubscribe(self, handler: Callable[[RawEvent], None]) -> None:
        with self._lock:
            if handler in self._handlers:
                self._handlers.remove(handler)

    def publish(self, event: RawEvent) -> None:
        """Publish a RawEvent to all subscribers deterministically."""
        with self._lock:
            subscribers = list(self._handlers)

        for handler in subscribers:
            handler(event)

    def clear(self) -> None:
        with self._lock:
            self._handlers.clear()
