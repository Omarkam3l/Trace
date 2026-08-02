"""The Recorder: bridges the Tracer's synchronous lifecycle hooks to
asynchronous storage + exporters, via a background batching writer.

This is the piece that makes storage/exporters "pluggable" in practice:
construct a ``Recorder`` with whichever :class:`StorageAdapter` and
:class:`Exporter` list you want, attach it to a :class:`Tracer` with
``tracer.add_hook(recorder)``, and every finished span flows through it.
"""

from __future__ import annotations

import threading
from collections.abc import Sequence

from traceforge.core.lifecycle import Exporter, SpanLifecycleHook
from traceforge.models.span import SpanModel
from traceforge.recorder.queue import SpanQueue
from traceforge.recorder.writer import RecorderWriter
from traceforge.storage.base import StorageAdapter

DEFAULT_BATCH_SIZE = 50
DEFAULT_FLUSH_INTERVAL_SECONDS = 1.0


class Recorder(SpanLifecycleHook):
    """Buffers finished spans and flushes them to storage + exporters.

    ``on_span_start`` is a no-op by default (recording happens on
    completion); override/subclass if you need "span started" streaming.
    """

    def __init__(
        self,
        storage: StorageAdapter,
        exporters: Sequence[Exporter] = (),
        *,
        batch_size: int = DEFAULT_BATCH_SIZE,
        flush_interval: float = DEFAULT_FLUSH_INTERVAL_SECONDS,
    ) -> None:
        self._span_queue: SpanQueue[SpanModel] = SpanQueue()
        self._writer = RecorderWriter(
            self._span_queue,
            storage,
            exporters,
            batch_size=batch_size,
            flush_interval=flush_interval,
        )
        self._lock = threading.Lock()
        self._started = False

    def start(self) -> Recorder:
        with self._lock:
            if not self._started:
                self._writer.start()
                self._started = True
        return self

    def stop(self, timeout: float | None = 5.0) -> None:
        with self._lock:
            if self._started:
                self._writer.stop(timeout)
                self._started = False

    def __enter__(self) -> Recorder:
        return self.start()

    def __exit__(self, *exc_info: object) -> None:
        self.stop()

    # -- SpanLifecycleHook protocol --------------------------------------
    def on_span_start(self, span: SpanModel) -> None:
        return None

    def on_span_end(self, span: SpanModel) -> None:
        self._span_queue.put(span)

    @property
    def pending_count(self) -> int:
        return self._span_queue.qsize()
