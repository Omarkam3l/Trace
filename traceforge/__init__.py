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

__version__ = "1.0.1"

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
from traceforge.bridge import SpanToSessionBridge
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
from traceforge.exporters import ConsoleExporter, JSONExporter, OTLPExporter, WebSocketExporter
from traceforge.gateway import create_app
from traceforge.instrumentation import InstrumentationConfig, trace
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
from traceforge.pipeline import ExecutionConsumer, ExecutionPipeline, SQLiteIngestConsumer
from traceforge.plugins import (
    Plugin,
    PluginContext,
    PluginManager,
    PluginMetadata,
    PluginRegistry,
)
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
from traceforge.recorder import Recorder
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
from traceforge.service import (
    ServiceConfig,
    TraceForgeApiService,
)
from traceforge.storage import JSONLStorage, MemoryStorage, SQLiteStorage, StorageAdapter
from traceforge.visualization import (
    DiffViewModel,
    FlamegraphViewModel,
    GraphViewModel,
    TimelineViewModel,
    VisualizationConfig,
    VisualizationEngine,
)

__all__ = [
    "ActivityQuery",
    # models
    "Attributes",
    "BackendType",
    # core
    "Clock",
    # api / ergonomics
    "ConfigurationError",
    # exporters
    "ConsoleExporter",
    "ContextManager",
    "DiffCategory",
    "DiffConfig",
    "DiffViewModel",
    "EventLevel",
    "EventModel",
    "ExceptionInfo",
    # Phase 5.5 Execution Pipeline
    "ExecutionConsumer",
    "ExecutionContext",
    # Phase 9 Execution Diff Engine
    "ExecutionDiffEngine",
    "ExecutionDiffReport",
    "ExecutionPipeline",
    "ExportConfig",
    # Phase 10 Export & Artifact System
    "ExportEngine",
    "ExportFormat",
    "ExporterError",
    "FlamegraphViewModel",
    "FrozenClock",
    "GraphQuery",
    "GraphViewModel",
    "HtmlExporter",
    # Phase 3 Instrumentation API
    "InstrumentationConfig",
    "JSONExporter",
    # storage
    "JSONLStorage",
    "JsonExporter",
    "MarkdownExporter",
    "MemoryStorage",
    "MermaidExporter",
    "NodeQuery",
    "OTLPExporter",
    "Pagination",
    # Phase 4 Plugin SDK
    "Plugin",
    "PluginContext",
    "PluginManager",
    "PluginMetadata",
    "PluginRegistry",
    "ProfileType",
    # Phase 5 Python Runtime Plugin
    "PythonRuntimePlugin",
    # Phase 7 Query Engine
    "QueryEngine",
    "QueryFilter",
    "RawEventQuery",
    # recorder
    "Recorder",
    "RelationshipQuery",
    "ReplayConfig",
    # Phase 8 Replay Engine
    "ReplayEngine",
    "ReplayMode",
    "ReplaySession",
    "RuntimeConfig",
    "SQLiteIngestConsumer",
    "SQLiteStorage",
    "ServiceConfig",
    "SessionQuery",
    "Span",
    "SpanContext",
    "SpanKind",
    "SpanModel",
    "SpanNotActiveError",
    "SpanStatus",
    "SpanToSessionBridge",
    "StorageAdapter",
    "StorageError",
    "SystemClock",
    "TimelineViewModel",
    "Trace",
    # Phase 12 API Service Layer
    "TraceForgeApiService",
    "TraceForgeError",
    "TraceModel",
    "Tracer",
    "TracerNotConfiguredError",
    "VisualizationConfig",
    # Phase 11 Visualization Data Adapter Layer
    "VisualizationEngine",
    "WebSocketExporter",
    "__version__",
    "configure",
    # Phase 13 HTTP Gateway Layer
    "create_app",
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
    "trace",
    "traced",
]
