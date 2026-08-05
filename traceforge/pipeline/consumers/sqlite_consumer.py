"""SQLiteIngestConsumer: ExecutionConsumer persisting completed execution objects to SQLiteStorageDriver."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from traceforge.pipeline.consumer import ExecutionConsumer
from traceforge.storage.records.activity_record import ActivityRecord
from traceforge.storage.records.graph_record import GraphRecord
from traceforge.storage.records.node_record import NodeRecord
from traceforge.storage.records.relationship_record import RelationshipRecord
from traceforge.storage.records.session_record import SessionRecord

if TYPE_CHECKING:
    from traceforge.domain.activity import Activity
    from traceforge.domain.graph import ExecutionGraph
    from traceforge.domain.session import RecordingSession
    from traceforge.storage.drivers.sqlite import SQLiteStorageDriver


class SQLiteIngestConsumer(ExecutionConsumer):
    """Execution consumer that translates domain execution events into persistent SQLite records."""

    def __init__(self, driver: SQLiteStorageDriver, name: str = "sqlite_ingest_consumer") -> None:
        super().__init__(name=name)
        self._driver = driver

    @property
    def driver(self) -> SQLiteStorageDriver:
        return self._driver

    def on_session_completed(self, session: RecordingSession) -> None:
        if not self.is_enabled:
            return

        record = SessionRecord(
            session_id=session.session_id,
            started_at=session.started_at,
            finished_at=session.finished_at,
            duration_ms=session.duration_ms,
            status=str(session.status.value if hasattr(session.status, "value") else session.status),
            environment_os=session.environment.os,
            environment_python=session.environment.python_version,
            profile_name=session.profile.name,
        )
        self._driver.begin_transaction()
        self._driver.write_batch([record])
        self._driver.commit()

    def on_activity_completed(self, activity: Activity) -> None:
        if not self.is_enabled:
            return

        record = ActivityRecord(
            activity_id=activity.activity_id,
            session_id=activity.session_id,
            name=activity.name,
            started_at=activity.started_at,
            finished_at=activity.finished_at,
            duration_ms=activity.duration_ms,
            status=str(activity.status.value if hasattr(activity.status, "value") else activity.status),
            graph_id=activity.graph.graph_id,
        )
        self._driver.begin_transaction()
        self._driver.write_batch([record])
        self._driver.commit()

    def on_graph_completed(self, graph: ExecutionGraph) -> None:
        if not self.is_enabled:
            return

        records: list[Any] = []

        # 1. Graph Record
        graph_rec = GraphRecord(
            graph_id=graph.graph_id,
            activity_id=graph.activity_id,
            node_ids=list(graph.nodes.keys()),
            relationship_ids=[r.relationship_id for r in graph.relationships],
        )
        records.append(graph_rec)

        # 2. Node Records
        for node_id, node in graph.nodes.items():
            inputs_str = json.dumps(node.inputs) if isinstance(node.inputs, dict) else str(node.inputs)
            outputs_str = json.dumps(node.outputs) if isinstance(node.outputs, dict) else str(node.outputs)
            metadata_str = json.dumps(node.metadata) if isinstance(node.metadata, dict) else str(node.metadata)

            node_rec = NodeRecord(
                node_id=node.node_id,
                graph_id=node.graph_id,
                type=str(node.type.value if hasattr(node.type, "value") else node.type),
                name=node.name,
                started_at=node.started_at,
                finished_at=node.finished_at,
                duration_ms=node.duration_ms,
                status=str(node.status.value if hasattr(node.status, "value") else node.status),
                parent_id=node.parent_id,
                child_ids=node.child_ids,
                inputs_json=inputs_str,
                outputs_json=outputs_str,
                metadata_json=metadata_str,
                tags=node.tags,
                source=node.source,
            )
            records.append(node_rec)

        # 3. Relationship Records
        for rel in graph.relationships:
            rel_rec = RelationshipRecord(
                relationship_id=rel.relationship_id,
                graph_id=rel.graph_id,
                source_node_id=rel.source_node_id,
                target_node_id=rel.target_node_id,
                type=str(rel.type.value if hasattr(rel.type, "value") else rel.type),
            )
            records.append(rel_rec)

        self._driver.begin_transaction()
        self._driver.write_batch(records)
        self._driver.commit()
