"""TraceForge Instrumentation API (Phase 3)."""

from traceforge.instrumentation.config import InstrumentationConfig
from traceforge.instrumentation.tracer import Tracer

# Global default tracer instance for simple DX (`from traceforge import trace`)
trace = Tracer()

__all__ = [
    "InstrumentationConfig",
    "Tracer",
    "trace",
]
