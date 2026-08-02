"""The background writer: owns a private asyncio event loop running on a
dedicated thread, drains the span queue, batches spans, and flushes them
to storage + all configured exporters.

Running its own loop+thread (rather than relying on the host application's
event loop) is what lets :class:`Recorder` work identically whether the
host application is purely synchronous, purely asynchronous, or a mix —
the Recorder never assumes an event loop is already running on the calling
thread.
"""

from __future__ import annotations

import asyncio
import queue as _queue
import threading
from collections.abc import Sequence

from traceforge.core.lifecycle import Exporter
from traceforge.models.span import SpanModel
from traceforge.recorder.buffer import BatchBuffer
from traceforge.recorder.queue import SpanQueue
from traceforge.storage.base import StorageAdapter
from traceforge.utils.logger import get_logger

_logger = get_logger(__name__)

_POLL_TIMEOUT_SECONDS = 0.1


class RecorderWriter:
    """Runs the drain-batch-flush loop on a dedicated background thread."""

    def __init__(
        self,
        span_queue: SpanQueue[SpanModel],
        storage: StorageAdapter,
        exporters: Sequence[Exporter],
        *,
        batch_size: int,
        flush_interval: float,
    ) -> None:
        self._span_queue = span_queue
        self._storage = storage
        self._exporters = list(exporters)
        self._batch_size = batch_size
        self._flush_interval = flush_interval

        self._thread: threading.Thread | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._stop_event = threading.Event()
        self._stopped_cleanly = threading.Event()

    def start(self) -> None:
        self._thread = threading.Thread(
            target=self._run, name="traceforge-recorder-writer", daemon=True
        )
        self._thread.start()

    def stop(self, timeout: float | None) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout)

    # -- thread body ------------------------------------------------------
    def _run(self) -> None:
        loop = asyncio.new_event_loop()
        self._loop = loop
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._main())
        finally:
            loop.close()
            self._stopped_cleanly.set()

    async def _main(self) -> None:
        buffer: BatchBuffer[SpanModel] = BatchBuffer(self._batch_size, self._flush_interval)
        while True:
            stopping = self._stop_event.is_set()
            try:
                span = await asyncio.to_thread(self._span_queue.get, _POLL_TIMEOUT_SECONDS)
                buffer.add(span)
            except _queue.Empty:
                pass

            if buffer.should_flush() or (stopping and len(buffer)):
                await self._flush(buffer.drain())

            if stopping and self._span_queue.empty() and len(buffer) == 0:
                break

        for exporter in self._exporters:
            try:
                await exporter.shutdown()
            except Exception:  # noqa: BLE001
                _logger.exception("traceforge: exporter shutdown failed")

    async def _flush(self, batch: list[SpanModel]) -> None:
        if not batch:
            return
        try:
            await self._storage.write_spans(batch)
        except Exception:  # noqa: BLE001
            _logger.exception("traceforge: storage write failed for %d spans", len(batch))

        for exporter in self._exporters:
            try:
                await exporter.export(batch)
            except Exception:  # noqa: BLE001
                _logger.exception("traceforge: exporter %r failed", exporter)
