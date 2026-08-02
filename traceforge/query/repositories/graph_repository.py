"""GraphRepository read repository."""

from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime

from traceforge.query.exceptions import NotFoundError, RepositoryError
from traceforge.storage.records.graph_record import GraphRecord


class GraphRepository:
    """Read repository for GraphRecord storage models."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection
        self._lock = threading.RLock()

    def get_by_id(self, graph_id: str) -> GraphRecord:
        """Fetch GraphRecord by ID or raise NotFoundError."""
        with self._lock:
            try:
                cursor = self._conn.cursor()
                cursor.execute("""
                    SELECT graph_id, activity_id, node_ids_json, relationship_ids_json, record_timestamp
                    FROM graphs WHERE graph_id = ?;
                """, (graph_id,))
                row = cursor.fetchone()
                if not row:
                    raise NotFoundError(f"Graph with ID {graph_id!r} not found")
                return self._row_to_record(row)
            except sqlite3.Error as err:
                raise RepositoryError(f"Failed to fetch graph {graph_id!r}: {err}") from err

    def list_by_activity(self, activity_id: str) -> list[GraphRecord]:
        """List GraphRecords belonging to an activity_id."""
        with self._lock:
            try:
                cursor = self._conn.cursor()
                cursor.execute("""
                    SELECT graph_id, activity_id, node_ids_json, relationship_ids_json, record_timestamp
                    FROM graphs WHERE activity_id = ? ORDER BY graph_id ASC;
                """, (activity_id,))
                return [self._row_to_record(row) for row in cursor.fetchall()]
            except sqlite3.Error as err:
                raise RepositoryError(f"Failed to list graphs for activity {activity_id!r}: {err}") from err

    def _row_to_record(self, row: tuple) -> GraphRecord:
        return GraphRecord(
            graph_id=row[0],
            activity_id=row[1],
            node_ids=json.loads(row[2]),
            relationship_ids=json.loads(row[3]),
            record_timestamp=datetime.fromisoformat(row[4]),
        )
