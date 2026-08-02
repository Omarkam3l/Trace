"""Generic timing middleware helper.

Not tied to any web framework: wraps any zero-arg (sync or async)
callable and reports elapsed time, for use inside a framework-specific
middleware shim.
"""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


def timed_call(call: Callable[[], T]) -> tuple[T, float]:  # noqa: UP047
    """Run ``call`` and return ``(result, elapsed_ms)``."""
    start = time.perf_counter()
    result = call()
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    return result, elapsed_ms


async def timed_call_async(call: Callable[[], Awaitable[T]]) -> tuple[T, float]:  # noqa: UP047
    """Async counterpart of :func:`timed_call`."""
    start = time.perf_counter()
    result = await call()
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    return result, elapsed_ms
