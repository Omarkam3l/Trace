# Phase 2 — Recording Engine

Version: 1.0

Status: Specification

---

# Goal

Implement the deterministic runtime responsible for transforming raw runtime events into immutable execution graphs.

The Recording Engine is the heart of TraceForge.

It owns runtime state.

It is the ONLY mutable component in the entire system.

Every other domain model remains immutable.

---

# Responsibilities

The Recording Engine is responsible for:

- Starting recording sessions
- Stopping recording sessions
- Creating activities
- Closing activities
- Managing execution contexts
- Receiving raw events
- Building execution nodes
- Building relationships
- Maintaining execution order
- Maintaining timestamps
- Producing immutable execution graphs

The Recording Engine never:

- Performs AI analysis
- Writes to storage
- Exports traces
- Displays dashboards
- Knows about frameworks
- Knows about databases

---

# High-Level Architecture

Plugins

↓

Raw Events

↓

Event Bus

↓

Recording Engine

↓

Execution Graph

---

# Components

The Recording Engine consists of the following components:

## Recorder

Public entry point.

Responsibilities:

- Start session
- Stop session
- Register plugins
- Receive raw events
- Dispatch events internally

---

## Session Manager

Responsible for:

- Creating RecordingSession
- Closing RecordingSession
- Session lifecycle
- Session metadata

Only one active session may exist.

---

## Activity Manager

Responsible for:

- Creating activities
- Closing activities
- Activity lifecycle
- Activity lookup

Activities always belong to one session.

---

## Context Manager

Responsible for runtime execution contexts.

Creates execution scopes.

Supports:

- Nested contexts
- Async contexts
- Thread-local contexts

Every execution node belongs to exactly one context.

---

## Event Bus

Receives raw events.

Provides publish/subscribe.

Maintains ordering.

No business logic.

No graph logic.

---

## Node Factory

Transforms Raw Events into immutable ExecutionNodes.

Performs:

- Validation
- Timestamp normalization
- Status assignment
- Metadata normalization

---

## Relationship Builder

Creates graph relationships.

Supported relationships:

- Parent → Child
- Previous → Next
- Dependency

Future relationship types must be backward compatible.

---

## Graph Builder

Responsible for:

- Graph creation
- Node insertion
- Relationship insertion
- DAG validation
- Ordering

Graph Builder is the only component allowed to mutate the graph during recording.

Once recording ends:

Graph becomes immutable.

---

# Raw Event

Plugins never create ExecutionNodes.

Plugins emit Raw Events.

RawEvent contains:

event_id

timestamp

type

source

payload

context_id

activity_hint

metadata

---

# Event Types

Two categories exist.

## Boundary Events

Examples

SessionStarted

SessionFinished

ActivityStarted

ActivityFinished

ContextStarted

ContextFinished

---

## Execution Events

Examples

FunctionEntered

FunctionReturned

HTTPRequest

HTTPResponse

SQLQuery

RedisCall

FilesystemRead

FilesystemWrite

LLMCall

CacheLookup

ExceptionThrown

BackgroundTask

Custom

---

# Runtime Flow

Plugin

↓

Raw Event

↓

Event Bus

↓

Recorder

↓

Node Factory

↓

Execution Node

↓

Relationship Builder

↓

Graph Builder

↓

Execution Graph

---

# State Ownership

Recorder owns runtime state.

No plugin owns state.

No plugin builds graphs.

No plugin builds relationships.

---

# Context Rules

Contexts may be nested.

Contexts must always close.

Orphan contexts are invalid.

Execution nodes inherit the active context automatically.

---

# Ordering Rules

Execution order must be deterministic.

Ordering priority:

1. Timestamp

2. Sequence Number

3. Event ID

Recorder must preserve ordering regardless of plugin source.

---

# Error Handling

Malformed Raw Events must never crash recording.

Errors become internal recorder events.

Recording continues whenever possible.

---

# Thread Safety

Recording Engine must support:

Multiple threads

Multiple async tasks

Thread-local execution contexts

No shared mutable graph state outside the Recorder.

---

# Performance Goals

Raw Event processing:

< 50 μs average

Node creation:

O(1)

Relationship insertion:

O(1)

Graph validation:

Incremental

Memory allocations minimized.

---

# Public API

Recorder

start_session()

stop_session()

emit(raw_event)

current_session()

current_activity()

---

# Testing Requirements

Implement unit tests for:

Session lifecycle

Activity lifecycle

Context nesting

Context cleanup

Event ordering

Node creation

Relationship creation

Graph construction

DAG validation

Thread safety

Async execution

Malformed events

Concurrent event emission

Nested activities

Empty sessions

Stress tests

---

# Acceptance Criteria

✓ Session lifecycle works

✓ Activities created correctly

✓ Context propagation works

✓ Raw Events converted into Execution Nodes

✓ Relationships built correctly

✓ Graph remains a valid DAG

✓ Recorder is deterministic

✓ Thread-safe

✓ Async-safe

✓ No framework dependencies

✓ No storage dependencies

✓ All tests pass

---

# Non Goals

No FastAPI

No Flask

No Django

No React

No Flutter

No Exporters

No SQLite

No Dashboard

No AI

No Visualization

No Plugins

Those belong to future phases.