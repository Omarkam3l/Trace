# SDK reference (quick guide)

## Creating a tracer

```python
import traceforge

tracer = traceforge.Tracer("my-service")
```

Optionally inject a custom `Clock` (see `traceforge.core.clock`) for
deterministic testing:

```python
from traceforge.core.clock import FrozenClock

tracer = traceforge.Tracer("my-service", clock=FrozenClock())
```

## Wiring up storage + exporters

```python
recorder = traceforge.Recorder(
    storage=traceforge.SQLiteStorage("./traces.db"),
    exporters=[traceforge.ConsoleExporter()],
    batch_size=50,
    flush_interval=1.0,
).start()

tracer.add_hook(recorder)

# ... application runs, spans flow to storage + exporters ...

recorder.stop()  # flushes remaining spans before returning
```

`Recorder` is also a context manager:

```python
with traceforge.Recorder(storage=traceforge.MemoryStorage()) as recorder:
    tracer.add_hook(recorder)
    ...
```

## Explicit tracer usage

```python
with tracer.start_span("step-1") as span:
    span.set_attribute("k", "v")
    span.add_event("something-happened")
```

```python
async with tracer.start_span("async-step") as span:
    await do_work()
```

## Default-tracer convenience layer (optional)

```python
traceforge.configure(tracer)

with traceforge.span("step-1"):
    ...

@traceforge.traced()
def my_function():
    ...

@traceforge.traced(name="custom-name")
async def my_async_function():
    ...
```

## Querying stored spans

```python
spans = await storage.query_spans(trace_id=some_trace_id, limit=100)
```

## Storage adapters

| Adapter          | Durable | Notes                                   |
|------------------|---------|------------------------------------------|
| `MemoryStorage`   | No      | Bounded ring buffer; tests/dev            |
| `JSONLStorage`    | Yes     | Append-only newline-delimited JSON file   |
| `SQLiteStorage`   | Yes     | Indexed by `trace_id` and `correlation_id`|
| `PostgresStorage` | —       | Reserved for a future release             |

## Exporters

| Exporter            | Notes                                              |
|---------------------|-----------------------------------------------------|
| `ConsoleExporter`    | Pretty-prints spans; zero configuration              |
| `JSONExporter`       | Writes/streams JSON batches to a file or callback     |
| `WebSocketExporter`  | Streams live spans to connected clients (optional dep)|
| `OTLPExporter`       | Posts OTLP/HTTP+JSON batches to a collector endpoint  |

## Configuration

```python
from traceforge.config import TraceForgeSettings, load_settings

settings = load_settings()  # reads TRACEFORGE_* environment variables
# or:
settings = TraceForgeSettings(service_name="my-service", storage_backend="sqlite", storage_path="./t.db")
```
