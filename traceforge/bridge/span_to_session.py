"""Bridge from the public SDK's span-recording pipeline to the domain-object
execution pipeline that QueryEngine/ReplayEngine/DiffEngine/TraceForgeApiService
read from.

Background
----------
traceforge has two independent data pipelines:

1. Tracer -> Recorder -> StorageAdapter (MemoryStorage/JSONLStorage/
   SQLiteStorage) -- the public SDK surface, storing flat SpanModel objects.
2. ExecutionPipeline -> ExecutionConsumer (e.g. SQLiteIngestConsumer) ->
   StorageDriver (SQLiteStorageDriver) -- storing RecordingSession/Activity/
   ExecutionGraph/ExecutionNode/Relationship domain objects, which is what
   QueryEngine, ReplayEngine, ExecutionDiffEngine, and TraceForgeApiService
   all read from.

Nothing shipped previously converted (1) into (2): SpanModels captured via
@traced()/span() never reached the sessions/activities/graphs/nodes tables,
so replay/diff/the gateway API had no way to see anything recorded through
the public SDK. SpanToSessionBridge is that missing conversion step.

Usage
-----
    tracer = traceforge.configure(service_name="my-service")

    driver = SQLiteStorageDriver("traces.db")
    pipeline = traceforge.ExecutionPipeline()
    pipeline.register_consumer(traceforge.SQLiteIngestConsumer(driver))

    bridge = traceforge.SpanToSessionBridge(pipeline)
    tracer.add_hook(bridge)

    @traceforge.traced()
    def handle_request(...): ...

    # ... later ...
    conn = driver.connection_manager.get_connection()
    qe = traceforge.QueryEngine(conn)
    qe.sessions.list()  # now actually has rows

Mapping model
-------------
One *trace* (i.e. one root span and all its descendants) becomes exactly one
RecordingSession containing exactly one Activity containing exactly one
ExecutionGraph. Every SpanModel in the trace becomes one ExecutionNode; every
parent/child span relationship becomes one PARENT_CHILD Relationship.
"""

from __future__ import annotations

import platform
import threading
from typing import TYPE_CHECKING

from traceforge.domain.activity import Activity
from traceforge.domain.enums import (
    ActivityStatus,
    NodeStatus,
    NodeType,
    RelationshipType,
    SessionStatus,
    SourceType,
)
from traceforge.domain.environment import Environment
from traceforge.domain.graph import ExecutionGraph
from traceforge.domain.metadata import Metadata
from traceforge.domain.node import ExecutionNode, Relationship
from traceforge.domain.profile import RecordingProfile
from traceforge.domain.session import RecordingSession
from traceforge.models.enums import SpanStatus

if TYPE_CHECKING:
    from traceforge.models.span import SpanModel
    from traceforge.pipeline.pipeline import ExecutionPipeline


def _node_status_for(span: SpanModel) -> NodeStatus:
    if span.exception is not None or span.status == SpanStatus.ERROR:
        return NodeStatus.FAILED
    if span.is_finished:
        return NodeStatus.COMPLETED
    return NodeStatus.RUNNING


class SpanToSessionBridge:
    """SpanLifecycleHook that materializes completed traces into the

    RecordingSession/Activity/ExecutionGraph domain schema and publishes them
    via an ExecutionPipeline.

    Thread-safe: spans from concurrent traces (including concurrent async
    tasks) are tracked independently by trace_id.
    """

    def __init__(
        self,
        pipeline: ExecutionPipeline,
        environment_name: str = "development",
        profile_name: str = "traceforge-sdk-bridge",
    ) -> None:
        self._pipeline = pipeline
        self._environment_name = environment_name
        self._profile_name = profile_name
        self._lock = threading.Lock()
        # trace_id -> {span_id: SpanModel}, accumulated as spans end.
        self._in_progress: dict[str, dict[str, SpanModel]] = {}

    def on_span_start(self, span: SpanModel) -> None:
        # Nothing to do on start; a trace is only meaningful once its root
        # span has ended, at which point every descendant should already
        # have reported via on_span_end (children close before parents in
        # normal with-block usage).
        pass

    def on_span_end(self, span: SpanModel) -> None:
        with self._lock:
            trace_spans = self._in_progress.setdefault(span.trace_id, {})
            trace_spans[span.id] = span

            if span.parent_span_id is not None:
                # Not the root -- wait for the root span to close before
                # materializing anything.
                return

            # Root span just closed: the trace is complete. Pull it out and
            # release the lock before doing the (potentially slower) publish
            # work, so we don't hold the lock across pipeline dispatch.
            finished_trace = self._in_progress.pop(span.trace_id)

        self._publish_trace(span.trace_id, span, finished_trace)

    def _publish_trace(
        self,
        trace_id: str,
        root: SpanModel,
        spans_by_id: dict[str, SpanModel],
    ) -> None:
        nodes: dict[str, ExecutionNode] = {}
        relationships: list[Relationship] = []

        for span in spans_by_id.values():
            child_ids = [s.id for s in spans_by_id.values() if s.parent_span_id == span.id]
            nodes[span.id] = ExecutionNode(
                node_id=span.id,
                graph_id=trace_id,
                type=NodeType.FUNCTION_CALL,
                name=span.name,
                started_at=span.start_time,
                finished_at=span.end_time,
                duration_ms=span.duration_ms,
                status=_node_status_for(span),
                parent_id=span.parent_span_id,
                child_ids=child_ids,
                metadata=Metadata(attributes=dict(span.attributes)),
                source=SourceType.PYTHON_SDK,
            )
            if span.parent_span_id is not None:
                relationships.append(
                    Relationship(
                        relationship_id=f"rel_{span.parent_span_id}_{span.id}",
                        graph_id=trace_id,
                        source_node_id=span.parent_span_id,
                        target_node_id=span.id,
                        type=RelationshipType.PARENT_CHILD,
                    )
                )

        graph = ExecutionGraph(
            graph_id=trace_id,
            activity_id=trace_id,
            nodes=nodes,
            relationships=relationships,
        )

        activity_failed = any(s.exception is not None or s.status == SpanStatus.ERROR for s in spans_by_id.values())
        activity = Activity(
            activity_id=trace_id,
            session_id=trace_id,
            name=root.name,
            started_at=root.start_time,
            finished_at=root.end_time,
            duration_ms=root.duration_ms,
            status=ActivityStatus.FAILED if activity_failed else ActivityStatus.COMPLETED,
            graph=graph,
        )

        session = RecordingSession(
            session_id=trace_id,
            started_at=root.start_time,
            finished_at=root.end_time,
            duration_ms=root.duration_ms,
            status=SessionStatus.FAILED if activity_failed else SessionStatus.COMPLETED,
            environment=Environment(
                os=platform.system(),
                python_version=platform.python_version(),
                hostname=platform.node() or None,
                environment_name=self._environment_name,
            ),
            profile=RecordingProfile(name=self._profile_name),
        )

        # Publish order matters for consumers like SQLiteIngestConsumer that
        # write via foreign-key-adjacent tables: session and activity rows
        # exist before the graph/nodes/relationships that reference them.
        self._pipeline.publish_session(session)
        self._pipeline.publish_activity(activity)
        self._pipeline.publish_graph(graph)
