# Phase 3 — Instrumentation API

**Status:** Draft  
**Version:** v0.4.0  
**Depends On:** Phase 1, Phase 1.5, Phase 2  
**API Stability:** Experimental (Frozen after completion)

---

# 1. Goal

The Instrumentation API provides the primary public interface of TraceForge.

Its purpose is to expose a simple, beautiful, and production-ready developer experience while hiding the complexity of the Recording Engine.

Developers should be able to instrument applications without understanding:

- Recorder
- GraphBuilder
- EventBus
- SessionManager
- ActivityManager
- ExecutionGraph

The Instrumentation API acts purely as a facade.

---

# 2. Motivation

The Recording Engine already provides deterministic runtime recording.

However, it is too low-level for everyday application development.

A developer should never need to emit RawEvents manually.

Instead, TraceForge should feel natural.

Example:

```python
from traceforge import trace

@trace
def login():
    ...
```

or

```python
with trace.session("Login"):

    with trace.activity("Database"):

        ...
```

The API should prioritize readability over flexibility.

---

# 3. Design Principles

## 3.1 Zero Business Logic

The Instrumentation layer contains no recording logic.

Every public method simply delegates to the Recording Engine.

Example

trace.activity()

↓

Recorder.start_activity()

---

## 3.2 Framework Agnostic

The Instrumentation API must not contain knowledge about:

- FastAPI
- Django
- Flask
- SQLAlchemy
- Celery
- LangGraph

Framework support belongs exclusively to Plugins.

---

## 3.3 Hybrid API

TraceForge supports two developer experiences.

### Simple API

```python
from traceforge import trace
```

Global singleton instance.

Suitable for most users.

---

### Advanced API

```python
from traceforge import Tracer

tracer = Tracer(...)
```

Suitable for

- embedded runtimes
- IDE integrations
- testing
- multiple isolated recorders
- enterprise environments

---

## 3.4 Beautiful API

Instrumentation should require minimal code.

Target:

3 lines or fewer.

---

# 4. Public API

The public package exports only:

```python
trace

Tracer
```

No engine components are publicly exposed.

---

## 4.1 Sessions

```python
trace.start_session(name)

trace.stop_session()

with trace.session(name):
    ...
```

---

## 4.2 Activities

```python
trace.start_activity(name)

trace.stop_activity()

with trace.activity(name):
    ...
```

---

## 4.3 Events

```python
trace.event(
    name,
    metadata=None
)
```

Events are lightweight execution markers.

---

## 4.4 Decorators

```python
@trace
def function():
    ...
```

Equivalent to

```python
with trace.activity(function_name):
    function()
```

---

Additional decorators

```python
@trace.activity()

@trace.session()
```

---

## 4.5 Runtime Information

```python
trace.current_session()

trace.current_activity()

trace.is_recording()
```

---

# 5. Plugin SDK

Plugins are intentionally low-level.

They never construct:

- ExecutionNode
- ExecutionGraph
- Activity
- Session

Plugins only emit RawEvents.

Example

```python
plugin.emit(raw_event)
```

Recorder owns graph construction.

---

# 6. Internal Flow

Developer

↓

Instrumentation API

↓

Recorder

↓

Recording Engine

↓

Execution Domain

No public API bypasses this flow.

---

# 7. Decorator Rules

Decorators define execution boundaries.

They DO NOT

- inspect Python AST
- use sys.settrace
- profile bytecode
- inspect local variables
- monitor function internals

They simply start and stop activities.

Detailed execution recording belongs to Plugins.

---

# 8. Context Managers

Context managers are first-class APIs.

Example

```python
with trace.session("Checkout"):

    with trace.activity("Payment"):

        ...
```

Nested contexts automatically produce nested activities.

---

# 9. Error Handling

Instrumentation never crashes the application.

If recording fails

- execution continues
- recorder captures the failure internally
- application behavior remains unchanged

TraceForge must always fail safely.

---

# 10. Thread Safety

Instrumentation API must remain

- thread-safe

- asyncio-safe

- reentrant

No shared mutable state outside Recorder.

---

# 11. Performance Requirements

Instrumentation overhead should remain negligible.

Target

Session creation:

< 50 µs

Activity creation:

< 20 µs

Event creation:

< 10 µs

Decorator overhead:

< 5% for typical business functions

---

# 12. Non Goals

This phase does NOT implement

- storage
- exporters
- dashboard
- AI analysis
- framework integrations
- plugin discovery
- visualization

---

# 13. Acceptance Criteria

The phase is complete when

✓ Users can instrument applications without accessing Recorder.

✓ Decorators behave identically to context managers.

✓ All APIs delegate to the Recording Engine.

✓ Public package exposes only trace and Tracer.

✓ Plugin SDK emits RawEvents only.

✓ Context propagation works for nested sync execution.

✓ Context propagation works for asyncio.

✓ Context propagation works across threads.

✓ Error handling never affects application execution.

✓ Complete unit and integration tests pass.

---

# 14. Testing Strategy

Unit Tests

- decorator lifecycle

- context managers

- nested sessions

- nested activities

- runtime queries

- exception handling

- concurrent instrumentation

- async instrumentation

Integration Tests

- decorator → recorder

- activity → recorder

- session → recorder

- plugin → recorder

Stress Tests

- 1000 nested activities

- concurrent threads

- concurrent asyncio tasks

Performance Tests

- instrumentation overhead

- decorator latency

- event throughput

---

# 15. Future Extensions

Future phases may introduce

- hierarchical execution expansion

- lazy-loaded execution details

- plugin auto-discovery

- storage adapters

- exporters

- OpenTelemetry bridge

- AI execution analysis

These capabilities are intentionally excluded from Phase 3.