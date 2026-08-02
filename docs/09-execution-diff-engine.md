# Phase 9 — Execution Diff Engine

## Overview

The Execution Diff Engine provides a deterministic, read-only comparison framework between two reconstructed `ReplaySession` objects (e.g., a baseline execution vs. a target execution).

Previous phases established deterministic recording (Phases 1-5.5), durable storage (Phase 6), read querying (Phase 7), and execution replay reconstruction (Phase 8).

Phase 9 introduces structural, temporal, performance, and exception diffing to pinpoint regressions, anomalies, runtime structural changes, and behavioral differences across executions.

The Diff Engine follows strict CQRS principles: it is 100% read-only, operates purely on immutable `ReplaySession` data, and produces immutable `ExecutionDiffReport` artifacts.

---

# Goals

Implement a production-grade comparison engine capable of:

- Structural Graph Comparison (added/removed/modified nodes, hierarchy shifts, relationship changes)
- Timeline Event Comparison (sequence divergence, missing events, payload/type changes)
- Performance & Timing Comparison (duration delta, latency regressions, node timing variance)
- Exception & Error Comparison (new/resolved exceptions, stack trace divergence)
- Environment & Metadata Comparison (Python/OS version changes, profile variances)
- Deterministic Diff Reports (identical inputs $\rightarrow$ byte-for-byte identical diff output)

---

# Non Goals

This phase does NOT implement:

- live runtime diffing during execution
- visual UI rendering or side-by-side diff viewers
- automated root-cause AI reasoning (belonging to Phase 10+)
- database writes or storage mutations
- exporters or REST/GraphQL endpoints

---

# Architecture

```
                 ReplayEngine (Phase 8)
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
      Baseline Replay             Target Replay
          Session                     Session
             │                           │
             └─────────────┬─────────────┘
                           ▼
                 ExecutionDiffEngine (Facade)
                           │
       ┌───────────────────┼───────────────────┬───────────────────┐
       ▼                   ▼                   ▼                   ▼
  GraphDiff       TimelineDiff         PerformanceDiff      ExceptionDiff
  Comparator       Comparator            Comparator          Comparator
       │                   │                   │                   │
       └───────────────────┼───────────────────┴───────────────────┘
                           ▼
                 ExecutionDiffReport (Immutable)
                           │
                           ▼
                    Public Diff API
```

---

# Design Principles

The Execution Diff Engine:

- is 100% read-only and free of side effects
- depends exclusively on immutable `ReplaySession` models from Phase 8
- never accesses storage drivers, database connections, or Live Recorders
- guarantees deterministic comparison order and reproducible reports
- enforces thread safety with zero shared mutable state

---

# Package Structure

```
traceforge/diff/

    engine.py

    config.py

    report.py

    comparators/

        base.py

        graph.py

        timeline.py

        performance.py

        exception.py

        metadata.py

    exceptions.py

tests/unit/diff/

    test_engine.py

    test_graph_diff.py

    test_timeline_diff.py

    test_performance_diff.py

    test_exception_diff.py

    test_config.py

    test_thread_safety.py
```

---

# Components & Responsibilities

## 1. ExecutionDiffEngine (`engine.py`)

Primary public facade.

Responsibilities:
- Accept baseline and target `ReplaySession` objects.
- Coordinate individual comparators according to `DiffConfig`.
- Assemble and return an immutable `ExecutionDiffReport`.

## 2. GraphDiffComparator (`comparators/graph.py`)

Compares execution node hierarchies and relationships.

Responsibilities:
- Detect added, removed, or modified nodes by node name/signature.
- Identify parent-child hierarchy structural shifts.
- Compare incoming and outgoing relationship graphs.

## 3. TimelineDiffComparator (`comparators/timeline.py`)

Compares event stream timelines.

Responsibilities:
- Align events by sequence and timestamp.
- Detect event sequence drift, event insertion/omission, and payload changes.

## 4. PerformanceDiffComparator (`comparators/performance.py`)

Compares timing metrics and execution overhead.

Responsibilities:
- Calculate total session duration delta and percentage variance.
- Identify bottleneck nodes with significant latency regressions.

## 5. ExceptionDiffComparator (`comparators/exception.py`)

Compares error states and captured exceptions.

Responsibilities:
- Identify newly introduced exceptions or resolved exceptions.
- Highlight stack trace and exception attribute differences.

---

# Public API Design & Models

## DiffConfig (`config.py`)

```python
class DiffCategory(StrEnum):
    GRAPH = "graph"
    TIMELINE = "timeline"
    PERFORMANCE = "performance"
    EXCEPTION = "exception"
    METADATA = "metadata"

class DiffConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    categories: set[DiffCategory] = Field(default_factory=lambda: set(DiffCategory))
    duration_threshold_ms: float = 10.0
    strict_sequence_matching: bool = True
```

## ExecutionDiffReport (`report.py`)

```python
class ExecutionDiffReport(BaseModel):
    model_config = ConfigDict(frozen=True)

    baseline_session_id: str
    target_session_id: str
    timestamp: datetime
    graph_diff: NodeGraphDiff | None = None
    timeline_diff: TimelineDiff | None = None
    performance_diff: PerformanceDiff | None = None
    exception_diff: ExceptionDiff | None = None
    metadata_diff: MetadataDiff | None = None
```

---

# Deterministic Comparison Strategy

1. **Node Matching**: Nodes are matched by `(node_type, name)` signature or logical node identifier.
2. **Deterministic Ordering**: All diff collections (added nodes, removed nodes, modified events) are ordered deterministically by `name ASC` or `timestamp ASC, sequence ASC`.
3. **Thresholding**: Performance regressions are flagged only when exceeding `duration_threshold_ms` to avoid micro-benchmark noise.

---

# Error Handling (`exceptions.py`)

```python
class DiffError(TraceForgeError):
    """Base exception for Execution Diff Engine failures."""

class DiffValidationError(DiffError):
    """Raised when comparing incompatible or un-replayable sessions."""

class DiffConfigurationError(DiffError):
    """Raised when invalid DiffConfig parameters are provided."""
```

---

# Thread Safety & Performance

- **Thread Safety**: All comparators operate on frozen, immutable models (`ReplaySession`). Comparison functions are pure, stateless, and thread-safe.
- **Performance**: Algorithmic node and timeline matching executes in $O(N \log N)$ using hash-indexed lookups and single-pass sequence alignments.

---

# Future AI Analysis Integration Points

The immutable `ExecutionDiffReport` serves as the structured input contract for Phase 10 AI Root-Cause Analysis:
- LLM prompt builders consume structured `graph_diff` and `performance_diff` blocks directly.
- AI reasoning engines evaluate structural divergences without parsing raw log streams.
