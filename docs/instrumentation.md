# Instrumentation

`traceforge.instrumentation` defines the contract framework adapters
implement (`Instrumentor.install(tracer)` / `Instrumentor.uninstall()`),
so that in a future release, wiring TraceForge into a framework looks
like:

```python
# illustrative — not yet implemented
from traceforge.instrumentation.fastapi import FastAPIInstrumentor

FastAPIInstrumentor(app).install(tracer)
```

## Current status

Only the interface (`traceforge/instrumentation/base.py`) ships today.
The following subpackages are reserved, present as empty packages, and
intentionally **not implemented** in this SDK-core milestone:

- `fastapi/`, `flask/`, `django/`, `express/`, `nextjs/`, `react/`,
  `flutter/`, `langgraph/`

See [`roadmap.md`](roadmap.md) for planned scope.

## Framework-agnostic building blocks available today

While full auto-instrumentation isn't implemented yet, `traceforge.middleware`
ships generic, framework-agnostic helpers any adapter (or your own manual
integration) can use right now:

- `extract_correlation_id(headers)` / `inject_correlation_id(headers, id)`
- `RequestContext` / `ResponseContext` — minimal, framework-agnostic shapes
- `timed_call(...)` / `timed_call_async(...)`

Manual integration in the meantime is straightforward:

```python
def my_view(request):
    correlation_id = extract_correlation_id(request.headers)
    token = traceforge.set_correlation_id(correlation_id)
    try:
        with tracer.start_span(f"{request.method} {request.path}", kind=SpanKind.SERVER):
            return handle(request)
    finally:
        ContextManager.reset(token)
```
