"""SessionRepository: append-only repository for the Session aggregate."""

from __future__ import annotations

import json
import threading
from typing import TYPE_CHECKING

from traceforge.storage.records.activity_record import ActivityRecord
from traceforge.storage.records.graph_record import GraphRecord
from traceforge.storage.records.node_record import NodeRecord
from traceforge.storage.records.relationship_record import RelationshipRecord
from traceforge.storage.records.session_record import SessionRecord
from traceforge.storage.records.snapshot_record import SnapshotRecord

if TYPE_CHECKING:
    from traceforge.domain.activity import Activity
    from traceforge.domain.graph import ExecutionGraph
    from traceforge.domain.node import ExecutionNode, Relationship
    from traceforge.domain.session import RecordingSession
    from traceforge.storage.drivers.base import StorageDriver


class SessionRepository:
    """Thread-safe append-only repository for persisting Session aggregate artifacts."""

    def __init__(self, driver: StorageDriver) -> None:
        self._driver = driver
        self._lock = threading.RLock()

    def append_session(self, session: RecordingSession) -> SessionRecord:
        """Convert RecordingSession domain entity to SessionRecord and append to storage."""
        record = SessionRecord(
            session_id=session.id,
            started_at=session.started_at,
            finished_at=session.finished_at,
            duration_ms=session.duration_ms,
            status=str(session.status),
            environment_os=session.environment.os,
            environment_python=session.environment.python_version,
            profile_name=session.profile.name,
        )
        with self._lock:
            self._driver.write_batch([record])
        return record

    def append_activity(self, activity: Activity) -> ActivityRecord:
        """Convert Activity domain entity to ActivityRecord and append to storage."""
        record = ActivityRecord(
            activity_id=activity.id,
            session_id=activity.session_id,
            name=activity.name,
            started_at=activity.started_at,
            finished_at=activity.finished_at,
            duration_ms=activity.duration_ms,
            status=str(activity.status),
            graph_id=activity.graph.id,
        )
        with self._lock:
            self._driver.write_batch([record])
        return record

    def append_graph(self, graph: ExecutionGraph) -> GraphRecord:
        """Convert ExecutionGraph domain entity to GraphRecord and append to storage."""
        record = GraphRecord(
            graph_id=graph.id,
            activity_id=graph.activity_id,
            node_ids=list(graph.nodes.keys()),
            relationship_ids=[r.id for r in graph.relationships],
        )
        with self._lock:
            self._driver.write_batch([record])
        return record

    def append_node(self, node: ExecutionNode) -> NodeRecord:
        """Convert ExecutionNode domain entity to NodeRecord and append to storage."""
        record = NodeRecord(
            node_id=node.id,
            graph_id=node.graph_id,
            type=str(node.type),
            name=node.name,
            started_at=node.started_at,
            finished_at=node.finished_at,
            duration_ms=node.duration_ms,
            status=str(node.status),
            parent_id=node.parent_id,
            child_ids=list(node.child_ids),
            inputs_json=json.dumps(node.inputs),
            outputs_json=json.dumps(node.outputs),
            metadata_json=json.dumps(node.metadata.attributes),
            tags=list(node.tags),
            source=str(node.source),
        )
        with self._lock:
            self._driver.write_batch([record])
        return record

    def append_relationship(self, relationship: Relationship) -> RelationshipRecord:
        """Convert Relationship domain entity to RelationshipRecord and append to storage."""
        record = RelationshipRecord(
            relationship_id=relationship.id,
            graph_id=relationship.graph_id,
            source_node_id=relationship.source_node_id,
            target_node_id=relationship.target_node_id,
            type=str(relationship.type),
        )
        with self._lock:
            self._driver.write_batch([record])
        return record

    def append_snapshot(self, snapshot: SnapshotRecord) -> SnapshotRecord:
        """Append SnapshotRecord to storage."""
        with self._lock:
            self._driver.write_batch([snapshot])
        return snapshot
