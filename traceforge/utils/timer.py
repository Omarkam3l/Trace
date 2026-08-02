"""A tiny stopwatch helper, independent of the tracing engine's own clock."""

from __future__ import annotations

import time
from types import TracebackType


class Stopwatch:
    """Measures elapsed wall-clock time via a context manager.

    Example::

        with Stopwatch() as sw:
            do_work()
        print(sw.elapsed_ms)
    """

    def __init__(self) -> None:
        self._start = 0.0
        self.elapsed_ms: float = 0.0

    def __enter__(self) -> Stopwatch:
        self._start = time.perf_counter()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.elapsed_ms = (time.perf_counter() - self._start) * 1000.0
