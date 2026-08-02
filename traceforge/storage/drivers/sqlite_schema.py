"""SQLiteSchemaManager for idempotent schema creation and referential integrity."""

from __future__ import annotations

import sqlite3
import threading

from traceforge.storage.drivers.sqlite_exceptions import SQLiteWriteError


class SQLiteSchemaManager:
    """Manages idempotent table initialization in SQLite database."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection
        self._lock = threading.RLock()

    def initialize_schema(self) -> None:
        """Create all required tables idempotently if they do not exist."""
        with self._lock:
            try:
                cursor = self._conn.cursor()

                # 1. sessions
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY NOT NULL,
                    started_at TEXT NOT NULL,
                    finished_at TEXT,
                    duration_ms REAL,
                    status TEXT NOT NULL,
                    environment_os TEXT NOT NULL,
                    environment_python TEXT NOT NULL,
                    profile_name TEXT NOT NULL,
                    record_timestamp TEXT NOT NULL
                );
                """)

                # 2. activities
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS activities (
                    activity_id TEXT PRIMARY KEY NOT NULL,
                    session_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    finished_at TEXT,
                    duration_ms REAL,
                    status TEXT NOT NULL,
                    graph_id TEXT NOT NULL,
                    record_timestamp TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
                );
                """)

                # 3. graphs
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS graphs (
                    graph_id TEXT PRIMARY KEY NOT NULL,
                    activity_id TEXT NOT NULL,
                    node_ids_json TEXT NOT NULL DEFAULT '[]',
                    relationship_ids_json TEXT NOT NULL DEFAULT '[]',
                    record_timestamp TEXT NOT NULL,
                    FOREIGN KEY (activity_id) REFERENCES activities(activity_id) ON DELETE CASCADE
                );
                """)

                # 4. nodes
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS nodes (
                    node_id TEXT PRIMARY KEY NOT NULL,
                    graph_id TEXT NOT NULL,
                    node_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    finished_at TEXT,
                    duration_ms REAL,
                    status TEXT NOT NULL,
                    parent_id TEXT,
                    child_ids_json TEXT NOT NULL DEFAULT '[]',
                    inputs_json TEXT NOT NULL DEFAULT '{}',
                    outputs_json TEXT NOT NULL DEFAULT '{}',
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    tags_json TEXT NOT NULL DEFAULT '[]',
                    source TEXT NOT NULL,
                    record_timestamp TEXT NOT NULL,
                    FOREIGN KEY (graph_id) REFERENCES graphs(graph_id) ON DELETE CASCADE
                );
                """)

                # 5. relationships
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    relationship_id TEXT PRIMARY KEY NOT NULL,
                    graph_id TEXT NOT NULL,
                    source_node_id TEXT NOT NULL,
                    target_node_id TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    record_timestamp TEXT NOT NULL,
                    FOREIGN KEY (graph_id) REFERENCES graphs(graph_id) ON DELETE CASCADE
                );
                """)

                # 6. snapshots
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS snapshots (
                    snapshot_id TEXT PRIMARY KEY NOT NULL,
                    session_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    active_activity_id TEXT,
                    nodes_count INTEGER NOT NULL DEFAULT 0,
                    relationships_count INTEGER NOT NULL DEFAULT 0,
                    record_timestamp TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
                );
                """)

                # 7. raw_events
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS raw_events (
                    event_id TEXT PRIMARY KEY NOT NULL,
                    timestamp TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    payload_json TEXT NOT NULL DEFAULT '{}',
                    context_id TEXT,
                    activity_hint TEXT,
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    record_timestamp TEXT NOT NULL
                );
                """)

            except sqlite3.Error as err:
                raise SQLiteWriteError(f"Failed to initialize SQLite schema: {err}") from err
