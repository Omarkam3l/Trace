# TraceForge Python SDK Reference

```python
import traceforge

tracer = traceforge.Tracer("my-service")
recorder = traceforge.Recorder(
    storage=traceforge.SQLiteStorage("traceforge.db")
).start()
tracer.add_hook(recorder)

with tracer.start_span("main-operation") as span:
    span.set_attribute("key", "val")
    with tracer.start_span("sub-step"):
        pass

recorder.stop()
```
