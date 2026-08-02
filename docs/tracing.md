# Tracing concepts

## Trace

A trace is the full tree of spans produced by one logical execution
(e.g. one incoming request, one background job run). All spans in a
trace share a `trace_id`, generated automatically the first time you
open a span with no active parent.

## Span

A span is a single unit of work with:

- a `name`
- a `start_time` / `end_time` and computed `duration_ms`
- a `status` (`unset` → `ok` or `error`)
- a `kind` (`internal`, `client`, `server`, `producer`, `consumer`)
- `attributes` — structured, JSON-safe key/value metadata
- `events` — timestamped occurrences within the span
- an optional captured `exception`

```python
with tracer.start_span("process-order", kind=SpanKind.INTERNAL) as span:
    span.set_attribute("order.id", order_id)
    ...
```

Nesting a `start_span` call inside another automatically creates a
parent-child relationship — no manual span-ID passing required, in
either sync or async code, across `await` boundaries.

## Event

A structured, timestamped fact attached to a span — for execution-flow
signals ("cache miss", "retry attempt 2"), not free-text logging:

```python
span.add_event("cache-miss", attributes={"key": cache_key})
```

## Context

The "where am I in the execution tree right now" state — current trace
ID, span ID, parent span ID, correlation ID, session ID — propagated
automatically via `contextvars`. This is what lets nested `start_span`
calls find their parent without any explicit wiring.

## Correlation ID

An identifier for correlating related executions across process or
service boundaries (e.g. attach it to an outgoing HTTP header and have
the downstream service continue the same correlation). Generated
automatically for a trace's root span if not already set; propagates to
all descendants.

## Session ID

Groups traces belonging to one user/runtime session. Not generated
automatically — set explicitly via `traceforge.new_session(...)` when
your application has the concept of a session.

## Exceptions

Raising inside a `start_span` block automatically:

- sets the span's `status` to `error`
- captures the exception's type, message, and stack trace
- adds an `"exception"` event
- re-raises the original exception (TraceForge never swallows errors)

```python
with tracer.start_span("risky-call"):
    raise ValueError("boom")  # captured, then re-raised
```
