"""Public, ergonomic API surface: decorators, context managers, exceptions."""

from traceforge.api.context_manager import span
from traceforge.api.decorators import traced
from traceforge.api.exceptions import (
    ConfigurationError,
    ExporterError,
    SpanNotActiveError,
    StorageError,
    TraceForgeError,
    TracerNotConfiguredError,
)
from traceforge.api.functions import (
    configure,
    current_correlation_id,
    current_session_id,
    current_span_id,
    current_trace_id,
    get_tracer,
    is_configured,
    new_session,
    reset_default_tracer,
    set_correlation_id,
)

__all__ = [
    "ConfigurationError",
    "ExporterError",
    "SpanNotActiveError",
    "StorageError",
    "TraceForgeError",
    "TracerNotConfiguredError",
    "configure",
    "current_correlation_id",
    "current_session_id",
    "current_span_id",
    "current_trace_id",
    "get_tracer",
    "is_configured",
    "new_session",
    "reset_default_tracer",
    "set_correlation_id",
    "span",
    "traced",
]
