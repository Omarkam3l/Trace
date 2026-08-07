# Changelog

All notable changes to TraceForge will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.2] - 2026-08-07

### Added
- **Flamegraph Dashboard View**: Interactive stacked horizontal flamegraph visualization in HTTP Gateway Dashboard (`/dashboard`).
- **Live Session Auto-Refresh**: Auto-polling session list with toggleable live state and scroll preservation.
- **Exception Surface UI**: Red error diagnostic banners with collapsible stacktraces for failed execution nodes.
- **Fail-Fast Type Guards**: `PluginContext` & `PluginManager` validate `recorder.emit` attribute to distinguish `traceforge.Recorder` from `traceforge.engine.recorder.Recorder`.
- **Client-Side Search & Filter**: Instant filtering by session ID, activity name, and execution status.

## [1.0.1] - 2026-08-07

### Fixed
- **JWT Security Validation**: Enabled Pydantic `validate_default=True` across configuration schemas, enforcing $\ge 32$-byte secret key rules and raising warnings on default secret key usage.
- **Environment Configuration**: Fixed `EnvSource` to correctly parse `TRACEFORGE_JWT_SECRET` and `TRACEFORGE_SECURITY_ENABLED` from `os.environ`.
- **Relational Ingestion Bridge**: Added `SQLiteIngestConsumer` to bridge hot-path tracing events into the relational query/replay schema.
- **Package Imports**: Fixed missing `__version__` definition in `traceforge` package root.

## [1.0.0] - 2026-08-05

### Added
- **Python Tracing SDK**: Framework-agnostic async & sync span creation via `Tracer`, `with` context managers, and `@traced()` decorator.
- **Pluggable Storage Adapters**: `MemoryStorage`, `JSONLStorage`, and indexed `SQLiteStorage`.
- **Exporters**: `ConsoleExporter`, `JSONExporter`, `WebSocketExporter`, and `OTLPExporter`.
- **Query & Replay Engine**: Graph traversal, execution tree reconstruction, and session diff comparison (`ExecutionDiffEngine`).
- **HTTP Gateway & Web Dashboard**: Production-grade FastAPI server with JWT authentication, RBAC, Prometheus metrics (`/metrics`), and embedded dashboard (`/dashboard`).
- **Command-Line Interface (`traceforge`)**: Modular CLI for workspace initialization, server lifecycle, replay, visualization export, and session inspect.
- **Public API Guard & CI Automation**: Comprehensive unit test coverage and GitHub Actions workflow.
