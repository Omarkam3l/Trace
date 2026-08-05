"""RelationshipRepository read repository."""

from __future__ import annotations

import sqlite3
import threading
from datetime import datetime

from traceforge.query.exceptions import RepositoryError
from traceforge.storage.records.relationship_record import RelationshipRecord


class RelationshipRepository:
    """Read repository for RelationshipRecord storage models."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection
        self._lock = threading.RLock()

    def list_by_graph(self, graph_id: str) -> list[RelationshipRecord]:
        """List RelationshipRecords belonging to graph_id in deterministic order."""
        with self._lock:
            try:
                cursor = self._conn.cursor()
                cursor.execute(
                    """
                    SELECT relationship_id, graph_id, source_node_id, target_node_id, relationship_type, record_timestamp
                    FROM relationships WHERE graph_id = ?
                    ORDER BY relationship_id ASC;
                """,
                    (graph_id,),
                )
                return [self._row_to_record(row) for row in cursor.fetchall()]
            except sqlite3.Error as err:
                raise RepositoryError(f"Failed to list relationships for graph {graph_id!r}: {err}") from err

    def list_incoming(self, node_id: str, graph_id: str) -> list[RelationshipRecord]:
        """List incoming RelationshipRecords targeting node_id within graph_id."""
        with self._lock:
            try:
                cursor = self._conn.cursor()
                cursor.execute(
                    """
                    SELECT relationship_id, graph_id, source_node_id, target_node_id, relationship_type, record_timestamp
                    FROM relationships WHERE graph_id = ? AND target_node_id = ?
                    ORDER BY relationship_id ASC;
                """,
                    (graph_id, node_id),
                )
                return [self._row_to_record(row) for row in cursor.fetchall()]
            except sqlite3.Error as err:
                raise RepositoryError(f"Failed to list incoming relationships for node {node_id!r}: {err}") from err

    def list_outgoing(self, node_id: str, graph_id: str) -> list[RelationshipRecord]:
        """List outgoing RelationshipRecords originating from node_id within graph_id."""
        with self._lock:
            try:
                cursor = self._conn.cursor()
                cursor.execute(
                    """
                    SELECT relationship_id, graph_id, source_node_id, target_node_id, relationship_type, record_timestamp
                    FROM relationships WHERE graph_id = ? AND source_node_id = ?
                    ORDER BY relationship_id ASC;
                """,
                    (graph_id, node_id),
                )
                return [self._row_to_record(row) for row in cursor.fetchall()]
            except sqlite3.Error as err:
                raise RepositoryError(f"Failed to list outgoing relationships for node {node_id!r}: {err}") from err

    def _row_to_record(self, row: tuple) -> RelationshipRecord:
        return RelationshipRecord(
            relationship_id=row[0],
            graph_id=row[1],
            source_node_id=row[2],
            target_node_id=row[3],
            type=row[4],
            record_timestamp=datetime.fromisoformat(row[5]),
        )
