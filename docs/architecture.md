# Architecture

TraceForge is organized as a small number of layers, each with a single
clear responsibility. Core code only ever depends on interfaces
(`StorageAdapter`, `Exporter`, `SpanLifecycleHook`), never on concrete
implementations — that's what makes storage and exporters pluggable.

```
┌─────────────────────────────────────────────────────────────────┐
│  api/            decorators, context managers, module functions  │
│                  (ergonomic layer on top of core)                │
├─────────────────────────────────────────────────────────────────┤
│  core/           Tracer, Span, Trace, Context, Clock, Lifecycle  │
│                  (the framework-agnostic tracing engine)         │
├─────────────────────────────────────────────────────────────────┤
│  models/         SpanModel, TraceModel, EventModel (Pydantic)    │
│                  (pure, immutable data — no behavior)             │
├───────────────────────────┬─────────────────────────────────────┤
│  recorder/                 │  storage/          exporters/       │
│  async batching bridge     │  Memory / JSONL /  Console / JSON / │
│  (sync hot path -> async)  │  SQLite            WebSocket / OTLP │
├─────────────────────────────────────────────────────────────────┤
│  config/         settings, defaults, env/file loaders             │
│  middleware/     generic correlation-ID / timing helpers          │
│  utils/          logging, serialization, small helpers            │
├─────────────────────────────────────────────────────────────────┤
│  instrumentation/  ai/  dashboard/   — reserved for future work   │
└─────────────────────────────────────────────────────────────────┘
```

## Data flow

1. Application code calls `tracer.start_span(...)`.
2. `Tracer._begin_span` reads the current `ExecutionContext` (via
   `contextvars`) to determine the parent span and trace ID, allocates a
   new `Span`, and pushes an updated context.
3. On exit, `Tracer._end_span` finalizes the span (status, duration via
   the injected `Clock`), restores the previous context, and calls
   `LifecycleManager.notify_end(span_model)` — synchronously and cheaply.
4. A `Recorder` (a `SpanLifecycleHook`) receives that call and pushes the
   finished `SpanModel` onto a thread-safe `SpanQueue`. This call never
   blocks the traced code path.
5. A background thread (`RecorderWriter`), running its own private
   asyncio event loop, drains the queue, batches spans (`BatchBuffer`),
   and flushes each batch to the configured `StorageAdapter` and all
   `Exporter`s — asynchronously.

## Why a dedicated background thread + loop?

The Recorder needs to work identically whether the host application is:

- purely synchronous (Flask, a script, a CLI tool),
- purely asynchronous (FastAPI, asyncio-based services), or
- a mix of both.

Relying on "the current event loop" would break the synchronous case.
Owning a private thread+loop means `Recorder.on_span_end` (the
lifecycle hook) is always a fast, synchronous, non-blocking call — no
matter what kind of code called `tracer.start_span`.

## Concurrency & thread-safety

- **Context propagation**: `contextvars.ContextVar`, correctly isolated
  per-thread and per-asyncio-task.
- **Span mutation**: guarded by a per-span `threading.Lock`.
- **Trace bookkeeping**: guarded by a per-tracer `threading.Lock`.
- **Recorder queue**: `queue.SimpleQueue`, safe for concurrent producers.
- **SQLite storage**: single connection, serialized via a `threading.Lock`
  (SQLite itself only supports one writer at a time); blocking calls are
  offloaded with `asyncio.to_thread`.

## No global mutable state

Every `Tracer` is an explicit, independent object — you can run multiple
tracers with different configurations in the same process. The one
intentional exception is `traceforge.api.functions`' optional "default
tracer" registry, used only by the ergonomic `traceforge.span(...)` /
`@traceforge.traced()` convenience layer. Nothing in `traceforge.core`
depends on it.
