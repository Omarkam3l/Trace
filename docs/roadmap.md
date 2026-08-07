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
- **Instrumentation**: `FastAPIInstrumentor` (`traceforge/instrumentation/fastapi/`)
  -- auto-instruments a FastAPI app's requests as SERVER-kind spans,
  including automatic exception capture. See its docstring for the
  `install`/`uninstall` contract.
- **Gateway dashboard**: a working, lightweight trace viewer is already
  live at `GET /dashboard` on the HTTP gateway (`traceforge server`),
  served from `traceforge/gateway/static/index.html`. It lists recorded
  sessions with live polling, renders a flamegraph per session, and
  surfaces exception details for failed traces. This is separate from
  the planned standalone dashboard app described below -- see that
  section for the distinction.

## Planned (not yet implemented)

- **Storage**: `PostgresStorage`
- **Exporters**: full binary OTLP/gRPC transport (current `OTLPExporter`
  uses a simplified OTLP/HTTP+JSON encoding)
- **Instrumentation**: concrete adapters for Flask, Django, Express,
  Next.js, React, Flutter, LangGraph (FastAPI is done -- see "Shipped" above)
- **Standalone dashboard app**: a separate, richer live trace-viewer web
  app (FastAPI + React), building on the `WebSocketExporter` for
  real-time push. This is a different, more ambitious project than the
  gateway's existing `/dashboard` route (see "Shipped" above) -- the
  packages under `traceforge/dashboard/` (`api.py`, `server.py`,
  `websocket.py`) are reserved specifically for *this* standalone app,
  not the gateway route, which already works today without them.
- **AI layer**: optional trace summarization / root-cause suggestion
  tooling built on top of captured traces (kept strictly separate from
  the business-logic-agnostic core)
- **Sampling**: head-based and tail-based sampling strategies driven by
  `TraceForgeSettings.sampling_rate`
- **Benchmarks**: expanded throughput/latency suite in `benchmarks/`

Contributions welcome — see the reserved package stubs
(`traceforge/instrumentation/flask`, `traceforge/instrumentation/django`,
`traceforge/instrumentation/langgraph`, `traceforge/instrumentation/react`,
`traceforge/instrumentation/nextjs`, `traceforge/instrumentation/flutter`,
`traceforge/dashboard/`, `traceforge/ai/`) for where these land. Note that
`traceforge/dashboard/` is reserved for the standalone app described
above, not the already-working `/dashboard` gateway route.
