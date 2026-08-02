"""Unit tests for BufferManager memory buffer operations."""

from __future__ import annotations

import pytest

from traceforge.storage.buffer import BufferManager
from traceforge.storage.exceptions import BufferOverflowError


def test_buffer_manager_append_peek_drain_clear():
    buf = BufferManager(max_capacity=5)
    assert buf.is_empty()
    assert buf.size() == 0

    buf.append("r1")
    buf.append_many(["r2", "r3"])
    assert buf.size() == 3
    assert not buf.is_empty()

    # Peek preserves buffer state
    peeked = buf.peek()
    assert peeked == ["r1", "r2", "r3"]
    assert buf.size() == 3

    # Capacity overflow rejection
    with pytest.raises(BufferOverflowError):
        buf.append_many(["r4", "r5", "r6"])

    # Drain removes all items in insertion order
    drained = buf.drain()
    assert drained == ["r1", "r2", "r3"]
    assert buf.is_empty()

    buf.append("r4")
    buf.clear()
    assert buf.is_empty()
