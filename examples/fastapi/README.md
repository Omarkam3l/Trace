# fastapi example — reserved for a future release

This example is planned but not implemented in the current SDK-core
milestone (which ships the reusable tracing SDK only, without framework
instrumentation). See `../../docs/roadmap.md`.

In the meantime, you can wire TraceForge into any fastapi app manually:

```python
import traceforge

tracer = traceforge.Tracer("fastapi-example")
recorder = traceforge.Recorder(
    storage=traceforge.MemoryStorage(),
    exporters=[traceforge.ConsoleExporter()],
).start()
tracer.add_hook(recorder)

with tracer.start_span("handle-request"):
    ...
```
