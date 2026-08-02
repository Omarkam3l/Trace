"""Unit tests for traceforge.core.clock."""

from __future__ import annotations

from datetime import datetime, timezone

from traceforge.core.clock import FrozenClock, SystemClock


def test_system_clock_now_is_timezone_aware():
    clock = SystemClock()
    assert clock.now().tzinfo is not None


def test_system_clock_monotonic_increases():
    clock = SystemClock()
    a = clock.monotonic()
    b = clock.monotonic()
    assert b >= a


def test_frozen_clock_does_not_advance_on_its_own():
    clock = FrozenClock(start=datetime(2024, 6, 1, tzinfo=timezone.utc))
    assert clock.now() == clock.now()
    assert clock.monotonic() == 0.0


def test_frozen_clock_advance():
    clock = FrozenClock()
    clock.advance(5.0)
    assert clock.monotonic() == 5.0
    first = clock.now()
    clock.advance(1.0)
    assert clock.now() > first
