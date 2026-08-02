"""SQLiteBatchWriter for converting Storage Records into parameterized executemany statements."""

from __future__ import annotations

import json
import sqlite3
import threading
from typing import Any

from traceforge.storage.drivers.sqlite_exceptions import SQLiteConstraintError, SQLiteWriteError
from traceforge.storage.records import (
    ActivityRecord,
    GraphRecord,
    NodeRecord,
    RawEventRecord,
    RelationshipRecord,
    SessionRecord,
    SnapshotRecord,
)


class SQLiteBatchWriter:
    """Writes batches of Storage Records into SQLite using prepared statements."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection
        self._lock = threading.RLock()

    def write_batch(self, records: list[Any]) -> None:
        """Write list of Storage Records into SQLite inside an existing transaction."""
        if not records:
            return

        with self._lock:
            try:
                cursor = self._conn.cursor()

                sessions_rows: list[tuple] = []
                activities_rows: list[tuple] = []
                graphs_rows: list[tuple] = []
                nodes_rows: list[tuple] = []
                relationships_rows: list[tuple] = []
                snapshots_rows: list[tuple] = []
                raw_events_rows: list[tuple] = []

                for rec in records:
                    if isinstance(rec, SessionRecord):
                        sessions_rows.append((
                            rec.session_id,
                            rec.started_at.isoformat(),
                            rec.finished_at.isoformat() if rec.finished_at else None,
                            rec.duration_ms,
                            rec.status,
                            rec.environment_os,
                            rec.environment_python,
                            rec.profile_name,
                            rec.record_timestamp.isoformat(),
                        ))

                    elif isinstance(rec, ActivityRecord):
                        activities_rows.append((
                            rec.activity_id,
                            rec.session_id,
                            rec.name,
                            rec.started_at.isoformat(),
                            rec.finished_at.isoformat() if rec.finished_at else None,
                            rec.duration_ms,
                            rec.status,
                            rec.graph_id,
                            rec.record_timestamp.isoformat(),
                        ))

                    elif isinstance(rec, GraphRecord):
                        graphs_rows.append((
                            rec.graph_id,
                            rec.activity_id,
                            json.dumps(rec.node_ids),
                            json.dumps(rec.relationship_ids),
                            rec.record_timestamp.isoformat(),
                        ))

                    elif isinstance(rec, NodeRecord):
                        nodes_rows.append((
                            rec.node_id,
                            rec.graph_id,
                            rec.type,
                            rec.name,
                            rec.started_at.isoformat(),
                            rec.finished_at.isoformat() if rec.finished_at else None,
                            rec.duration_ms,
                            rec.status,
                            rec.parent_id,
                            json.dumps(rec.child_ids),
                            rec.inputs_json,
                            rec.outputs_json,
                            rec.metadata_json,
                            json.dumps(rec.tags),
                            rec.source,
                            rec.record_timestamp.isoformat(),
                        ))

                    elif isinstance(rec, RelationshipRecord):
                        relationships_rows.append((
                            rec.relationship_id,
                            rec.graph_id,
                            rec.source_node_id,
                            rec.target_node_id,
                            rec.type,
                            rec.record_timestamp.isoformat(),
                        ))

                    elif isinstance(rec, SnapshotRecord):
                        snapshots_rows.append((
                            rec.snapshot_id,
                            rec.session_id,
                            rec.timestamp.isoformat(),
                            rec.active_activity_id,
                            rec.nodes_count,
                            rec.relationships_count,
                            rec.record_timestamp.isoformat(),
                        ))

                    elif isinstance(rec, RawEventRecord):
                        raw_events_rows.append((
                            rec.event_id,
                            rec.timestamp.isoformat(),
                            rec.sequence,
                            rec.type,
                            rec.source,
                            rec.payload_json,
                            rec.context_id,
                            rec.activity_hint,
                            rec.metadata_json,
                            rec.record_timestamp.isoformat(),
                        ))

                if sessions_rows:
                    cursor.executemany("""
                        INSERT INTO sessions (session_id, started_at, finished_at, duration_ms, status, environment_os, environment_python, profile_name, record_timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """, sessions_rows)

                if activities_rows:
                    cursor.executemany("""
                        INSERT INTO activities (activity_id, session_id, name, started_at, finished_at, duration_ms, status, graph_id, record_timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """, activities_rows)

                if graphs_rows:
                    cursor.executemany("""
                        INSERT INTO graphs (graph_id, activity_id, node_ids_json, relationship_ids_json, record_timestamp)
                        VALUES (?, ?, ?, ?, ?);
                    """, graphs_rows)

                if nodes_rows:
                    cursor.executemany("""
                        INSERT INTO nodes (node_id, graph_id, node_type, name, started_at, finished_at, duration_ms, status, parent_id, child_ids_json, inputs_json, outputs_json, metadata_json, tags_json, source, record_timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """, nodes_rows)

                if relationships_rows:
                    cursor.executemany("""
                        INSERT INTO relationships (relationship_id, graph_id, source_node_id, target_node_id, relationship_type, record_timestamp)
                        VALUES (?, ?, ?, ?, ?, ?);
                    """, relationships_rows)

                if snapshots_rows:
                    cursor.executemany("""
                        INSERT INTO snapshots (snapshot_id, session_id, timestamp, active_activity_id, nodes_count, relationships_count, record_timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?);
                    """, snapshots_rows)

                if raw_events_rows:
                    cursor.executemany("""
                        INSERT INTO raw_events (event_id, timestamp, sequence, type, source, payload_json, context_id, activity_hint, metadata_json, record_timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """, raw_events_rows)

            except sqlite3.IntegrityError as err:
                raise SQLiteConstraintError(f"SQLite constraint violation: {err}") from err
            except sqlite3.Error as err:
                raise SQLiteWriteError(f"SQLite write error: {err}") from err
