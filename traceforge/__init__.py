"""TraceForge: a framework-agnostic execution-tracing SDK.

TraceForge captures the *structure and timing* of your code's execution —
nested spans, parent-child relationships, durations, structured events,
and captured exceptions — with pluggable storage and exporters.

It is explicitly **not**:
  - a logger (no free-text log levels/messages as a primary concept)
  - an APM (no metrics dashboards, alerting, or SLOs baked in)
  - business-logic aware (it knows nothing about your domain)

Quickstart
----------
::

    import traceforge

    tracer = traceforge.Tracer("my-service")
    recorder = traceforge.Recorder(
        storage=traceforge.MemoryStorage(),
        exporters=[traceforge.ConsoleExporter()],
    ).start()
    tracer.add_hook(recorder)

    with tracer.start_span("handle-request") as span:
        span.set_attribute("user.id", "abc123")
        with tracer.start_span("query-db"):
            ...  # nested span, automatically parented

    recorder.stop()
"""

from __future__ import annotations

from traceforge.api import (
    ConfigurationError,
    ExporterError,
    SpanNotActiveError,
    StorageError,
    TraceForgeError,
    TracerNotConfiguredError,
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
    span,
    traced,
)
from traceforge.core import (
    Clock,
    ContextManager,
    ExecutionContext,
    FrozenClock,
    Span,
    SpanContext,
    SystemClock,
    Trace,
    Tracer,
)
from traceforge.exporters import ConsoleExporter, JSONExporter, OTLPExporter, WebSocketExporter
from traceforge.models import (
    Attributes,
    EventLevel,
    EventModel,
    ExceptionInfo,
    SpanKind,
    SpanModel,
    SpanStatus,
    TraceModel,
)
from traceforge.recorder import Recorder
from traceforge.storage import JSONLStorage, MemoryStorage, SQLiteStorage, StorageAdapter

from traceforge.instrumentation import InstrumentationConfig, Tracer, trace
from traceforge.plugins import (
    Plugin,
    PluginContext,
    PluginManager,
    PluginMetadata,
    PluginRegistry,
)
from traceforge.diff import (
    DiffCategory,
    DiffConfig,
    ExecutionDiffEngine,
    ExecutionDiffReport,
)
from traceforge.export import (
    ExportConfig,
    ExportEngine,
    ExportFormat,
    HtmlExporter,
    JsonExporter,
    MarkdownExporter,
    MermaidExporter,
)
from traceforge.visualization import (
    DiffViewModel,
    FlamegraphViewModel,
    GraphViewModel,
    TimelineViewModel,
    VisualizationConfig,
    VisualizationEngine,
)
from traceforge.pipeline import ExecutionConsumer, ExecutionPipeline
from traceforge.query import (
    ActivityQuery,
    GraphQuery,
    NodeQuery,
    Pagination,
    QueryEngine,
    QueryFilter,
    RawEventQuery,
    RelationshipQuery,
    SessionQuery,
)
from traceforge.replay import (
    ReplayConfig,
    ReplayEngine,
    ReplayMode,
    ReplaySession,
)
from traceforge.runtime import (
    BackendType,
    ProfileType,
    PythonRuntimePlugin,
    RuntimeConfig,
)

__all__ = [
    "__version__",
    # Phase 3 Instrumentation API
    "InstrumentationConfig",
    "Tracer",
    "trace",
    # Phase 4 Plugin SDK
    "Plugin",
    "PluginMetadata",
    "PluginContext",
    "PluginManager",
    "PluginRegistry",
    # Phase 5 Python Runtime Plugin
    "PythonRuntimePlugin",
    "RuntimeConfig",
    "ProfileType",
    "BackendType",
    # Phase 5.5 Execution Pipeline
    "ExecutionConsumer",
    "ExecutionPipeline",
    # Phase 7 Query Engine
    "QueryEngine",
    "QueryFilter",
    "Pagination",
    "SessionQuery",
    "ActivityQuery",
    "GraphQuery",
    "NodeQuery",
    "RelationshipQuery",
    "RawEventQuery",
    # Phase 8 Replay Engine
    "ReplayEngine",
    "ReplayConfig",
    "ReplayMode",
    "ReplaySession",
    # Phase 9 Execution Diff Engine
    "ExecutionDiffEngine",
    "ExecutionDiffReport",
    "DiffConfig",
    "DiffCategory",
    # Phase 10 Export & Artifact System
    "ExportEngine",
    "ExportConfig",
    "ExportFormat",
    "JsonExporter",
    "MermaidExporter",
    "HtmlExporter",
    "MarkdownExporter",
    # Phase 11 Visualization Data Adapter Layer
    "VisualizationEngine",
    "VisualizationConfig",
    "GraphViewModel",
    "TimelineViewModel",
    "FlamegraphViewModel",
    "DiffViewModel",
    # core
    "Clock",
    "ContextManager",
    "ExecutionContext",
    "FrozenClock",
    "Span",
    "SpanContext",
    "SystemClock",
    "Trace",
    # models
    "Attributes",
    "EventLevel",
    "EventModel",
    "ExceptionInfo",
    "SpanKind",
    "SpanModel",
    "SpanStatus",
    "TraceModel",
    # storage
    "JSONLStorage",
    "MemoryStorage",
    "SQLiteStorage",
    "StorageAdapter",
    # exporters
    "ConsoleExporter",
    "JSONExporter",
    "OTLPExporter",
    "WebSocketExporter",
    # recorder
    "Recorder",
    # api / ergonomics
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
