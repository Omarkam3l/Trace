# Phase 5 — Python Runtime Plugin

## Goal

Implement the first production-grade runtime plugin for TraceForge.

The Python Runtime Plugin automatically observes Python program execution and emits structured `RawEvent` objects into the Recording Engine without requiring developers to manually instrument their code.

This phase transforms TraceForge from an infrastructure framework into a usable runtime analysis platform.

---

# Objectives

The plugin must:

- Observe Python execution automatically.
- Generate deterministic execution events.
- Produce hierarchical execution structures.
- Preserve runtime correctness.
- Remain framework agnostic.
- Never modify user source code.
- Never crash the application being observed.

---

# Architectural Principles

## 1. Zero Code Modification

The plugin must never rewrite source files.

No:

- AST rewriting
- Source generation
- Build steps
- Bytecode modification

The user should be able to start recording with:

```python
import traceforge

traceforge.start()

run_application()
```

or

```bash
traceforge run app.py
```

without changing application code.

---

## 2. Runtime Observation Only

Observation occurs entirely during runtime.

The plugin observes execution.

It never changes execution.

---

## 3. Adaptive Instrumentation Backend

The plugin abstracts the instrumentation backend behind a common interface.

Backends:

1. CPython Monitoring API (PEP 669)
2. sys.setprofile()
3. sys.settrace() (Deep Debug only)

Selection priority:

```
PEP669
    ↓
setprofile
    ↓
settrace
```

The plugin automatically selects the best available backend based on the current Python version and active recording profile.

Users may explicitly override the backend through configuration.

---

## 4. Hierarchical Execution Model

Execution must never be represented as a flat event stream.

Runtime hierarchy:

```
Recording Session
    ↓
Activity
    ↓
Execution Graph
    ↓
Execution Node
    ↓
Execution Event
    ↓
Execution Sequence
```

Every execution event may optionally expose its own nested execution sequence.

This enables progressive exploration of runtime behavior.

---

## 5. Progressive Execution Disclosure

Execution should be explored gradually.

Users first see high-level operations.

Each execution node may be expanded to reveal deeper runtime details.

Example:

```
Login()

▼

Validate User()

▶

Database Query()

▶

Generate JWT()

▶
```

Expanding Database Query:

```
Connect

↓

Prepare

↓

Execute

↓

Receive

↓

Deserialize

↓

Close
```

Expanding Execute:

```
Socket Write

↓

Kernel Wait

↓

TCP Receive

↓

Response
```

This hierarchy is a core architectural principle of TraceForge.

---

# Runtime Observation Scope

## Function Execution

Record:

- function call
- return
- exception

---

## Methods

Record:

- instance methods
- static methods
- class methods

---

## Classes

Record:

- construction
- destruction (when observable)
- inheritance metadata

---

## Module Loading

Record:

- imports
- reloads

---

## Async Runtime

Record:

- task creation
- await
- resume
- completion
- cancellation

---

## Thread Runtime

Record:

- thread creation
- thread start
- thread join
- thread completion

---

## Context Managers

Record:

- __enter__
- __exit__

---

## Generators

Record:

- yield
- resume
- completion

---

## Exceptions

Record:

- raise
- catch
- rethrow

---

# Recording Profiles

## Minimal

Capture:

- Function Calls
- Returns
- Exceptions
- Threads
- Async Tasks

Designed for production environments.

Target overhead:

< 5%

---

## Standard (Default)

Capture:

Everything from Minimal plus:

- Imports
- Classes
- Context Managers
- Generators
- Decorators

Target overhead:

< 15%

---

## Deep Debug

Capture:

Everything from Standard plus:

- Local variables
- Global variables
- Stack frames
- Line events
- Expression details (backend permitting)

Performance is secondary to diagnostic quality.

---

## Custom

Users define exactly which runtime events should be recorded.

---

# Runtime Filtering

Recording should support include/exclude filters.

Example:

```python
trace.configure(
    include=[
        "my_app.*"
    ],
    exclude=[
        "site-packages.*",
        "threading.*",
        "asyncio.*"
    ]
)
```

Filtering occurs before event creation whenever possible.

---

# Execution Node Types

Introduce runtime node classifications.

```
FUNCTION

METHOD

CLASS

MODULE

THREAD

ASYNC_TASK

GENERATOR

CONTEXT_MANAGER

IMPORT

EXCEPTION

VARIABLE

LINE

EXPRESSION
```

These node types will later power:

- analysis
- visualization
- AI reasoning
- filtering

---

# Backend Interface

Each instrumentation backend must expose the same interface.

Responsibilities:

- start observation
- stop observation
- emit runtime events
- propagate execution context

The Recording Engine must remain completely unaware of which backend is active.

---

# Plugin Responsibilities

The plugin is responsible for:

- runtime observation
- backend selection
- event creation
- context propagation

The plugin is NOT responsible for:

- graph construction
- execution analysis
- storage
- visualization
- exporting

---

# Failure Isolation

Instrumentation failures must never terminate user applications.

Any internal runtime plugin failure must:

1. Emit a PluginFailure RawEvent.
2. Disable only the failing plugin if necessary.
3. Allow application execution to continue.

---

# Performance Goals

Minimal Profile

< 5% runtime overhead

---

Standard Profile

< 15% runtime overhead

---

Deep Debug

No strict performance target.

Diagnostic completeness takes priority.

---

# Compatibility

Supported versions:

- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13+

The plugin automatically selects the optimal backend for each runtime.

---

# Non-Goals

This phase does NOT include:

- FastAPI integration
- Django integration
- Flask integration
- SQLAlchemy integration
- Requests instrumentation
- HTTP tracing
- OpenAI instrumentation
- LangGraph instrumentation
- Storage engines
- Dashboard UI
- AI analysis

Those belong to future phases.

---

# Acceptance Criteria

Phase 5 is complete only when:

- Python applications can be traced without modifying source code.
- Runtime backend selection is automatic and deterministic.
- Recording Profiles behave exactly as specified.
- Runtime Filtering correctly limits captured events.
- Threads and asyncio contexts remain isolated and deterministic.
- Hierarchical execution structures are produced.
- Every execution node can expose deeper execution sequences.
- Runtime overhead remains within the defined performance budgets.
- Plugin failures never terminate the host application.
- Long-running execution does not introduce memory leaks.
- Execution ordering remains deterministic across identical runs.
- The implementation satisfies production-grade engineering standards and is approved for API Freeze.