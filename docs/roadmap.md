# Roadmap

## Shipped in this milestone (SDK core)

- Core engine: `Tracer`, `Span`, `Trace`, `Context`, `Clock`, `Lifecycle`
- Pydantic models: `SpanModel`, `TraceModel`, `EventModel`, enums
- Ergonomic API: decorators, context managers, module-level functions
- Storage: `MemoryStorage`, `JSONLStorage`, `SQLiteStorage`
- Exporters: `ConsoleExporter`, `JSONExporter`, `WebSocketExporter`, `OTLPExporter`
- Recorder: async, batched delivery decoupled from the tracing hot path
- Config: typed settings + env/JSON loaders
- Generic (framework-agnostic) correlation/timing middleware helpers
- Extensive unit + integration + performance-sanity test suite

## Planned (not yet implemented)

- **Storage**: `PostgresStorage`
- **Exporters**: full binary OTLP/gRPC transport (current `OTLPExporter`
  uses a simplified OTLP/HTTP+JSON encoding)
- **Instrumentation**: concrete adapters for FastAPI, Flask, Django,
  Express, Next.js, React, Flutter, LangGraph
- **Dashboard**: a live trace-viewer web app (FastAPI + React), building
  on the `WebSocketExporter`
- **AI layer**: optional trace summarization / root-cause suggestion
  tooling built on top of captured traces (kept strictly separate from
  the business-logic-agnostic core)
- **Sampling**: head-based and tail-based sampling strategies driven by
  `TraceForgeSettings.sampling_rate`
- **Benchmarks**: expanded throughput/latency suite in `benchmarks/`

Contributions welcome — see the reserved package stubs
(`traceforge/instrumentation/*`, `traceforge/dashboard/`, `traceforge/ai/`)
for where these land.
