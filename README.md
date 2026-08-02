# TraceForge

A framework-agnostic **execution tracing SDK** for Python. TraceForge helps
you understand the complete runtime execution of any software project:
nested spans, parent-child relationships, durations, structured events,
exceptions, and context propagation — across sync and async code alike.

TraceForge is **not**:

- a logger — it captures execution *structure*, not free-text log messages
- an APM — no metrics dashboards, alerting, or SLOs
- business-logic aware — it knows nothing about your domain, only about
  the shape of your code's execution

## Core concepts

| Concept        | What it is                                                        |
|-----------------|--------------------------------------------------------------------|
| **Trace**       | The full tree of spans produced by one logical execution           |
| **Span**        | A single unit of work, with a start/end time and a parent          |
| **Event**       | A timestamped, structured occurrence inside a span                 |
| **Context**     | The ambient "where am I in the tree" state, propagated automatically |
| **Correlation ID** | Ties related executions together across process/service boundaries |
| **Session ID**  | Groups traces belonging to one user/runtime session                |

## Install

```bash
pip install -e ".[dev]"          # core + dev tooling
pip install -e ".[websocket]"    # + WebSocket exporter support
```

Requires Python 3.12+.

## Quickstart

```python
import traceforge

tracer = traceforge.Tracer("my-service")

recorder = traceforge.Recorder(
    storage=traceforge.MemoryStorage(),
    exporters=[traceforge.ConsoleExporter()],
).start()
tracer.add_hook(recorder)

with tracer.start_span("handle-request") as span:
    span.set_attribute("user.id", "abc123")
    with tracer.start_span("query-db") as db_span:
        db_span.add_event("cache-miss")
        ...  # nested span, automatically parented to "handle-request"

recorder.stop()
```

### Async

```python
async with tracer.start_span("fetch-user") as span:
    user = await fetch_user_from_db()
    span.set_attribute("user.found", user is not None)
```

### Decorators

```python
from traceforge import traced

@traced()
def sync_work(): ...

@traced(name="async-work")
async def async_work(): ...
```

### Exceptions are captured automatically

```python
with tracer.start_span("risky") as span:
    raise ValueError("boom")  # span status -> ERROR, exception recorded
```

## Architecture

See [`docs/architecture.md`](docs/architecture.md) for the full breakdown.
In short:

```
core/        domain engine: Tracer, Span, Trace, Context, Clock, IDs, Lifecycle
models/      Pydantic schemas: SpanModel, TraceModel, EventModel, enums
api/         ergonomics: decorators, context managers, module-level functions
storage/     pluggable persistence: memory, jsonl, sqlite (postgres: roadmap)
exporters/   pluggable sinks: console, json, websocket, otlp
recorder/    async batching bridge from the sync hot-path to storage/exporters
config/      typed settings, env/JSON loaders
middleware/  generic (framework-agnostic) correlation/timing helpers
```

`instrumentation/`, `dashboard/`, and `ai/` are reserved for future
releases (see [`docs/roadmap.md`](docs/roadmap.md)) and are intentionally
not implemented in this milestone — this release is the reusable SDK core.

## Design principles

- **Async-first, sync-compatible**: every span context manager works as
  both `with` and `async with`.
- **No global mutable state**: `Tracer` instances are explicit and
  independent; the one opt-in exception (a "default tracer" registry) is
  isolated to `traceforge.api.functions` and used by nothing in core.
- **Thread-safe**: context propagation uses `contextvars`; mutable domain
  objects (`Span`, `Trace`, `Recorder`) guard state with locks.
- **Pluggable by interface, not by inheritance tricks**: `StorageAdapter`
  and `Exporter` are the only contracts core code depends on.

## Testing

```bash
pytest
```

## License

MIT — see [`LICENSE`](LICENSE).
