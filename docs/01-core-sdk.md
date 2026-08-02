# Phase 1 — Core SDK Foundation

Version: 1.0

Status: Approved for Implementation

---

# Goal

Build the reusable core of TraceForge.

This phase must NOT depend on any framework, language runtime integration,
or web framework.

It is a pure runtime tracing SDK.

The output of this phase is a working library that can create traces,
spans and events entirely in memory.

No files should be written yet.

No FastAPI.

No React.

No Next.js.

No Dashboard.

No AI.

Only the tracing engine.

---

# Problem

Developers need a consistent way to represent runtime execution.

Everything else in the project will depend on this layer.

If this layer is poorly designed,
every future integration will become difficult.

---

# Scope

Implement:

- Trace lifecycle
- Span lifecycle
- Event lifecycle
- Context propagation
- Correlation IDs
- Duration calculation
- Parent-child relationships
- In-memory storage

Do NOT implement:

- JSON export
- SQLite
- Dashboard
- CLI
- VSCode extension
- Framework plugins
- Network
- AI
- Logging

---

# Core Concepts

## Trace

Represents one execution session.

Examples:

- Login
- Checkout
- Search
- API Request

A Trace owns multiple spans.

---

## Span

Represents one logical operation.

Examples:

Validate User

Call Database

Create JWT

Return Response

Spans may contain child spans.

---

## Event

Represents a single point in time.

Examples:

Coupon Applied

Inventory Checked

Cache Hit

Token Generated

Events belong to spans.

---

## Context

Carries execution state.

Must contain:

Trace ID

Current Span ID

Parent Span ID

Correlation ID

Start Time

---

# Public API

The API must be extremely small.

Example:

trace = tracer.start_trace("Checkout")

span = trace.start_span("Validate User")

span.add_event("User Found")

span.finish()

trace.finish()

No additional complexity.

---

# IDs

Generate globally unique IDs.

Each object has:

Trace

Span

Event

Each must have its own ID.

---

# Time

Every object records:

Created At

Finished At

Duration

Duration is automatically calculated.

---

# Parent Relationships

Support nested spans.

Example:

Checkout
 ├── Validate User
 ├── Payment
 │     ├── Stripe Request
 │     └── Stripe Response
 └── Save Order

---

# Object Models

Trace

- id
- name
- started_at
- finished_at
- duration_ms
- status
- root_span

Span

- id
- parent_id
- trace_id
- name
- started_at
- finished_at
- duration_ms
- events
- children

Event

- id
- span_id
- timestamp
- name
- metadata

---

# Status

Objects support:

Running

Success

Error

Cancelled

---

# Error Handling

Exceptions inside spans should mark the span as Error.

The trace itself should continue until explicitly finished.

No exception should corrupt the tracing engine.

---

# Thread Safety

All context management must be thread-safe.

No global mutable state.

---

# Async Support

Architecture must support async execution.

Even if implementation is synchronous initially.

Future async support must not require redesign.

---

# Performance

The SDK must minimize allocations.

No unnecessary object copying.

No reflection.

No runtime inspection.

---

# Extensibility

Future storage engines should plug in without changing core code.

Future exporters should plug in without changing core code.

---

# Folder Structure

traceforge/

core/

models/

exceptions/

utils/

tests/

---

# Tests

Implement unit tests for:

Trace creation

Nested spans

Events

Duration calculation

Parent relationships

Status changes

Exception handling

Concurrent trace creation

---

# Acceptance Criteria

A developer can write:

trace = tracer.start_trace("Login")

span = trace.start_span("Database")

span.add_event("SELECT user")

span.finish()

trace.finish()

and obtain a complete in-memory execution tree.

No file writing.

No framework integration.

No external dependencies.

---

# Out of Scope

Everything else.

If a feature is not explicitly listed above,
it belongs to another phase.

Do not implement it.