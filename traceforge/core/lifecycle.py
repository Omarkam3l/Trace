"""Span lifecycle hooks and the interfaces storage/exporters plug into.

Hooks are intentionally *synchronous and cheap* (e.g. "push onto a
thread-safe queue"). Actual I/O (writing to storage, exporting) happens
asynchronously and out-of-band in :mod:`traceforge.recorder`, so that
recording a span never blocks the traced code path — sync or async.
"""

from __future__ import annotations

import threading
from collections.abc import Callable, Sequence
from typing import Protocol, runtime_checkable

from traceforge.models.span import SpanModel


@runtime_checkable
class SpanLifecycleHook(Protocol):
    """Observer notified when spans start and finish."""

    def on_span_start(self, span: SpanModel) -> None:
        """Called synchronously right after a span begins."""
        ...

    def on_span_end(self, span: SpanModel) -> None:
        """Called synchronously right after a span finishes."""
        ...


@runtime_checkable
class Exporter(Protocol):
    """A pluggable sink that ships finished spans somewhere (async I/O)."""

    async def export(self, spans: Sequence[SpanModel]) -> None:
        """Export a batch of finished spans."""
        ...

    async def shutdown(self) -> None:
        """Release any resources (connections, files, sockets)."""
        ...


class LifecycleManager:
    """Thread-safe registry/dispatcher for :class:`SpanLifecycleHook`."""

    def __init__(self) -> None:
        self._hooks: list[SpanLifecycleHook] = []
        self._lock = threading.Lock()

    def register(self, hook: SpanLifecycleHook) -> None:
        with self._lock:
            if hook not in self._hooks:
                self._hooks.append(hook)

    def unregister(self, hook: SpanLifecycleHook) -> None:
        with self._lock:
            if hook in self._hooks:
                self._hooks.remove(hook)

    def _snapshot(self) -> list[SpanLifecycleHook]:
        with self._lock:
            return list(self._hooks)

    def notify_start(self, span: SpanModel) -> None:
        for hook in self._snapshot():
            self._safe_call(hook.on_span_start, span)

    def notify_end(self, span: SpanModel) -> None:
        for hook in self._snapshot():
            self._safe_call(hook.on_span_end, span)

    @staticmethod
    def _safe_call(fn: Callable[[SpanModel], None], span: SpanModel) -> None:
        # A misbehaving hook (e.g. a buggy exporter) must never be allowed
        # to break the traced application code path.
        try:
            fn(span)
        except Exception:  # noqa: BLE001
            from traceforge.utils.logger import get_logger

            get_logger(__name__).exception(
                "traceforge: lifecycle hook %r raised while handling span %s",
                fn,
                span.id,
            )
