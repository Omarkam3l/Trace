"""Clock abstraction.

Injecting a clock (rather than calling ``datetime.now()``/``time.monotonic()``
directly) keeps span-duration logic deterministic and unit-testable.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime
from typing import Protocol, runtime_checkable


@runtime_checkable
class Clock(Protocol):
    """A source of wall-clock and monotonic time."""

    def now(self) -> datetime:
        """Current wall-clock time, timezone-aware (UTC)."""
        ...

    def monotonic(self) -> float:
        """Current monotonic time in seconds, for duration measurement."""
        ...


class SystemClock:
    """The real clock, backed by the standard library."""

    def now(self) -> datetime:
        return datetime.now(UTC)

    def monotonic(self) -> float:
        return time.monotonic()


class FrozenClock:
    """A deterministic clock for tests.

    Advances only when ``advance()`` is called explicitly.
    """

    def __init__(self, start: datetime | None = None) -> None:
        self._now = start or datetime(2024, 1, 1, tzinfo=UTC)
        self._monotonic = 0.0

    def now(self) -> datetime:
        return self._now

    def monotonic(self) -> float:
        return self._monotonic

    def advance(self, seconds: float) -> None:
        from datetime import timedelta

        self._now += timedelta(seconds=seconds)
        self._monotonic += seconds
