# Phase 8 — Replay Engine

## Overview

The Replay Engine reconstructs historical executions from persisted storage.

Unlike the Recorder, the Replay Engine never observes live execution.

Instead, it rebuilds immutable execution state from stored sessions, activities, graphs, nodes, relationships, snapshots, and raw events.

Replay is deterministic.

Given identical persisted data, replay must always produce identical reconstructed execution state.

---

# Goals

Implement a production-grade replay engine capable of:

- replaying complete sessions
- replaying activities
- replaying execution graphs
- replaying execution timelines
- replaying node execution order
- replaying raw event streams
- replaying snapshots
- deterministic reconstruction

---

# Non Goals

This phase does NOT implement

- visualization
- dashboards
- AI analysis
- distributed replay
- remote replay
- debugging UI
- exporters

---

# Architecture

                Query Engine

                     │

                     ▼

              Replay Engine

                     │

        ┌────────────┼────────────┐

        ▼            ▼            ▼

 Timeline Builder Graph Builder Snapshot Loader

        │            │            │

        └────────────┼────────────┘

                     ▼

             Replay Session

                     ▼

             Public Replay API

---

# Design Principles

Replay

- never writes
- never mutates storage
- never modifies graphs
- never depends on Recorder
- never depends on Runtime Plugin
- only reconstructs state

---

# Components

## ReplayEngine

Public facade.

Responsibilities

- load sessions
- coordinate replay
- expose replay API

---

## TimelineBuilder

Build deterministic execution timeline.

Responsibilities

- sort events
- reconstruct ordering
- validate sequence

---

## GraphRebuilder

Reconstruct execution graph from storage.

Responsibilities

- nodes
- relationships
- parent hierarchy

---

## SnapshotLoader

Load historical snapshots.

Support

- first snapshot
- latest snapshot
- snapshot by timestamp

---

## ReplaySession

Immutable replay result.

Contains

- session
- activities
- graph
- timeline
- snapshots

---

# Timeline

Timeline ordering

timestamp

↓

sequence

↓

identifier

No ambiguity allowed.

---

# Replay Modes

Support

FULL

Loads everything.

GRAPH_ONLY

Timeline omitted.

TIMELINE_ONLY

Graph omitted.

SNAPSHOT_ONLY

Loads snapshots only.

CUSTOM

Configurable.

---

# Replay Configuration

Immutable configuration model.

Fields

mode

validate_sequences

validate_relationships

strict

---

# Validation

Replay validates

missing nodes

broken relationships

duplicate identifiers

timeline ordering

parent hierarchy

invalid references

Strict mode raises exceptions.

Non-strict mode reports warnings.

---

# Exceptions

ReplayError

ReplayValidationError

ReplayConsistencyError

ReplayConfigurationError

---

# Package Structure

traceforge/replay/

    engine.py

    config.py

    session.py

    timeline.py

    graph_rebuilder.py

    snapshot_loader.py

    validator.py

    exceptions.py

---

# Thread Safety

Replay is read-only.

No shared mutable state.

---

# Performance

Use Query Engine only.

Never bypass repositories.

Batch loading required.

Avoid N+1 queries.

---

# Tests

tests/unit/replay/

test_engine.py

test_timeline.py

test_graph_rebuilder.py

test_snapshot_loader.py

test_validation.py

test_modes.py

test_thread_safety.py

Verify

- deterministic replay
- timeline ordering
- graph reconstruction
- replay modes
- validation
- malformed storage
- concurrent replay

---

# Deliverables

The Replay Engine must provide

- deterministic replay
- immutable replay session
- timeline reconstruction
- graph reconstruction
- snapshot loading
- replay validation
- production-ready API