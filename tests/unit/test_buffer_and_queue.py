"""Unit tests for recorder.buffer.BatchBuffer and recorder.queue.SpanQueue."""

from __future__ import annotations

import queue as _queue
import time

import pytest

from traceforge.recorder.buffer import BatchBuffer
from traceforge.recorder.queue import SpanQueue


def test_buffer_flushes_at_batch_size():
    buf = BatchBuffer(batch_size=3, flush_interval=1000)
    buf.add(1)
    buf.add(2)
    assert not buf.should_flush()
    buf.add(3)
    assert buf.should_flush()


def test_buffer_flushes_after_interval():
    buf = BatchBuffer(batch_size=1000, flush_interval=0.05)
    buf.add(1)
    assert not buf.should_flush()
    time.sleep(0.12)
    assert buf.should_flush()


def test_buffer_drain_resets_state():
    buf = BatchBuffer(batch_size=2, flush_interval=1000)
    buf.add(1)
    buf.add(2)
    items = buf.drain()
    assert items == [1, 2]
    assert len(buf) == 0
    assert not buf.should_flush()


def test_empty_buffer_never_flushes():
    buf = BatchBuffer(batch_size=1, flush_interval=0.0)
    assert not buf.should_flush()


def test_span_queue_put_get_roundtrip():
    q: SpanQueue[int] = SpanQueue()
    q.put(1)
    q.put(2)
    assert q.get(timeout=1) == 1
    assert q.get(timeout=1) == 2


def test_span_queue_get_times_out_when_empty():
    q: SpanQueue[int] = SpanQueue()
    with pytest.raises(_queue.Empty):
        q.get(timeout=0.05)


def test_span_queue_empty_and_qsize():
    q: SpanQueue[int] = SpanQueue()
    assert q.empty()
    q.put(1)
    assert not q.empty()
    assert q.qsize() == 1
