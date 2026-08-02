# Phase 7 — Query Engine

## Overview

The Query Engine introduces the read-side architecture for TraceForge.

Previous phases established deterministic execution recording and durable append-only storage.

This phase adds a dedicated read model capable of retrieving historical execution data efficiently while remaining completely isolated from the write path.

The Query Engine follows CQRS principles.

The write model remains immutable.

The read model never mutates persisted execution data.

---

# Goals

Implement a production-grade read architecture capable of:

- loading sessions
- loading activities
- loading execution graphs
- loading nodes
- loading relationships
- loading raw events
- filtering
- searching
- pagination
- graph traversal
- timeline queries

---

# Non Goals

This phase does NOT implement

- replay execution
- visualization
- AI analysis
- exporters
- REST APIs
- GraphQL
- dashboards
- caching
- indexing optimizations
- distributed storage

---

# Architecture

```
                SQLite Driver

                      │

              Query Driver

                      │

           Query Repository Layer

      ┌──────────┬───────────┐

      ▼          ▼           ▼

 Session      Activity     Graph

 Repository   Repository   Repository

      ▼          ▼           ▼

         Query Engine

                ▼

          Public Read API
```

---

# Design Principles

The Query Engine

- is read-only
- never performs writes
- never mutates storage
- never owns transactions
- never knows about Recorder
- never knows about Runtime Plugin

---

# Components

## QueryEngine

Primary facade.

Responsibilities

- route queries
- coordinate repositories
- expose public API

---

## SessionRepository

Read sessions.

Supported queries

- get_by_id
- list
- exists

---

## ActivityRepository

Read activities.

Supported queries

- get_by_id
- list_by_session
- exists

---

## GraphRepository

Read graphs.

Supported queries

- get_by_id
- list_by_activity

---

## NodeRepository

Read nodes.

Supported queries

- get_by_id
- list_by_graph

---

## RelationshipRepository

Read relationships.

Supported queries

- list_by_graph

---

## RawEventRepository

Read raw runtime events.

Supported queries

- list_by_session
- list_by_activity

---

# Query Objects

Every query is immutable.

Example

```python
SessionQuery(
    session_id=...
)

ActivityQuery(
    session_id=...
)

NodeQuery(
    graph_id=...
)
```

---

# Filters

Support

- session_id
- activity_id
- graph_id
- node_type
- status
- timestamp range

---

# Pagination

Support

- limit
- offset

Deterministic ordering required.

---

# Ordering

Unless otherwise specified

Results are ordered by

timestamp

↓

sequence

↓

identifier

---

# Graph Traversal

Support

- incoming relationships
- outgoing relationships
- parent
- children

Traversal never mutates graphs.

---

# Thread Safety

Repositories must be thread-safe.

No shared mutable state.

---

# Transactions

Read operations never begin transactions.

They rely on SQLite snapshot isolation.

---

# Performance

Use prepared SELECT statements.

Avoid N+1 queries.

Batch fetch where appropriate.

---

# Error Handling

Introduce

QueryError

NotFoundError

InvalidQueryError

RepositoryError

Translate backend errors.

---

# Package Structure

traceforge/query/

    engine.py

    filters.py

    pagination.py

    queries.py

    exceptions.py

    repositories/

        session_repository.py

        activity_repository.py

        graph_repository.py

        node_repository.py

        relationship_repository.py

        raw_event_repository.py

---

# Tests

Create

tests/unit/query/

test_sessions.py

test_activities.py

test_graphs.py

test_nodes.py

test_relationships.py

test_raw_events.py

test_filters.py

test_pagination.py

test_thread_safety.py

test_query_engine.py

Verify

- lookup
- filtering
- pagination
- deterministic ordering
- graph traversal
- thread safety
- invalid queries
- not found behavior

All previous tests must continue passing.

---

# Deliverables

The Query Engine must provide

- production-ready read architecture
- immutable query objects
- repository abstraction
- deterministic query ordering
- CQRS compliance
- backend-independent API