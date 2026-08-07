"""TraceForge Instrumentation API (Phase 3).

See traceforge.instrumentation.tracer.Tracer's docstring for an important
distinction from traceforge.Tracer -- they are two unrelated classes that
happen to share a name.
"""

from __future__ import annotations

import warnings

from traceforge.instrumentation.config import InstrumentationConfig
from traceforge.instrumentation.tracer import Tracer

# Global default instance for simple DX (`from traceforge import
# instrumentation_trace`). Named explicitly (not `trace`) so it doesn't sit
# unlabeled next to `traceforge.Tracer`/`traceforge.configure()`, which is a
# different class entirely -- see Tracer's docstring in
# traceforge/instrumentation/tracer.py.
instrumentation_trace = Tracer()

__all__ = [
    "InstrumentationConfig",
    "Tracer",
    "instrumentation_trace",
]


def __getattr__(name: str) -> object:
    # Backward-compatible deprecated alias for code written against the old
    # `from traceforge.instrumentation import trace` / `traceforge.trace`
    # name. Warns instead of breaking silently or breaking outright.
    if name == "trace":
        warnings.warn(
            "traceforge.instrumentation.trace (and traceforge.trace) is deprecated "
            "and will be removed in a future release. Use "
            "traceforge.instrumentation.instrumentation_trace (or "
            "traceforge.instrumentation_trace) instead. Also double-check you want "
            "this session/activity-based Tracer and not traceforge.Tracer "
            "(traceforge.configure()), which is a different, unrelated class -- "
            "see Tracer's docstring in traceforge/instrumentation/tracer.py.",
            DeprecationWarning,
            stacklevel=2,
        )
        return instrumentation_trace
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
