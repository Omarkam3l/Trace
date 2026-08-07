"""Unit tests for traceforge top-level public API exports."""

from __future__ import annotations

import traceforge


def test_public_api_version_export():
    assert hasattr(traceforge, "__version__")
    assert isinstance(traceforge.__version__, str)
    assert traceforge.__version__ == "1.0.2"


def test_public_api_core_imports():
    assert hasattr(traceforge, "Tracer")
    assert hasattr(traceforge, "Span")
    assert hasattr(traceforge, "SpanContext")
    assert hasattr(traceforge, "Clock")
    assert hasattr(traceforge, "SystemClock")
    assert hasattr(traceforge, "FrozenClock")


def test_public_api_storage_imports():
    assert hasattr(traceforge, "MemoryStorage")
    assert hasattr(traceforge, "JSONLStorage")
    assert hasattr(traceforge, "SQLiteStorage")
    assert hasattr(traceforge, "StorageAdapter")


def test_public_api_exporter_imports():
    assert hasattr(traceforge, "ConsoleExporter")
    assert hasattr(traceforge, "JSONExporter")
    assert hasattr(traceforge, "WebSocketExporter")
    assert hasattr(traceforge, "OTLPExporter")


def test_public_api_api_functions():
    assert hasattr(traceforge, "configure")
    assert hasattr(traceforge, "traced")
    assert hasattr(traceforge, "span")
    assert hasattr(traceforge, "get_tracer")
    assert hasattr(traceforge, "is_configured")
    assert hasattr(traceforge, "reset_default_tracer")


def test_public_api_recorder_import():
    assert hasattr(traceforge, "Recorder")


def test_public_api_query_engine_import():
    assert hasattr(traceforge, "QueryEngine")


def test_public_api_all_attribute():
    assert isinstance(traceforge.__all__, list)
    for name in traceforge.__all__:
        assert hasattr(traceforge, name), f"Name '{name}' in __all__ but missing on top-level package"
