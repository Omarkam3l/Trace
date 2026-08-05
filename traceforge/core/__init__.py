"""Core domain layer: Tracer, Span, Trace, Context, Clock, IDs, Lifecycle.

This package has zero dependencies on storage, exporters, or any specific
framework — it is the framework-agnostic execution-tracing engine itself.
"""

from traceforge.core.clock import Clock, FrozenClock, SystemClock
from traceforge.core.context import ContextManager, ExecutionContext
from traceforge.core.lifecycle import Exporter, LifecycleManager, SpanLifecycleHook
from traceforge.core.span import Span
from traceforge.core.trace import Trace
from traceforge.core.tracer import SpanContext, Tracer

__all__ = [
    "Clock",
    "ContextManager",
    "ExecutionContext",
    "Exporter",
    "FrozenClock",
    "LifecycleManager",
    "Span",
    "SpanContext",
    "SpanLifecycleHook",
    "SystemClock",
    "Trace",
    "Tracer",
]
