"""Unit tests for SizeFlushPolicy, TimeFlushPolicy, and HybridFlushPolicy."""

from __future__ import annotations

import time

from traceforge.storage.buffer import BufferManager
from traceforge.storage.policies import HybridFlushPolicy, SizeFlushPolicy, TimeFlushPolicy


def test_size_flush_policy():
    buf = BufferManager()
    policy = SizeFlushPolicy(max_records=3)

    buf.append("r1")
    assert not policy.should_flush(buf)
    buf.append("r2")
    assert not policy.should_flush(buf)
    buf.append("r3")
    assert policy.should_flush(buf)


def test_time_flush_policy():
    buf = BufferManager()
    policy = TimeFlushPolicy(interval_seconds=0.05)

    assert not policy.should_flush(buf)  # Empty buffer does not flush

    buf.append("r1")
    time.sleep(0.06)
    assert policy.should_flush(buf)


def test_hybrid_flush_policy():
    buf = BufferManager()
    policy = HybridFlushPolicy(max_records=2, interval_seconds=1.0)

    buf.append("r1")
    assert not policy.should_flush(buf)

    buf.append("r2")
    assert policy.should_flush(buf)  # Size trigger
