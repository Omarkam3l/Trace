"""NodeRepository read repository with graph traversal support."""

from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime

from traceforge.query.exceptions import NotFoundError, RepositoryError
from traceforge.query.pagination import Pagination
from traceforge.storage.records.node_record import NodeRecord


class NodeRepository:
    """Read repository for NodeRecord storage models."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection
        self._lock = threading.RLock()

    def get_by_id(self, node_id: str) -> NodeRecord:
        """Fetch NodeRecord by ID or raise NotFoundError."""
        with self._lock:
            try:
                cursor = self._conn.cursor()
                cursor.execute("""
                    SELECT node_id, graph_id, node_type, name, started_at, finished_at, duration_ms, status, parent_id, child_ids_json, inputs_json, outputs_json, metadata_json, tags_json, source, record_timestamp
                    FROM nodes WHERE node_id = ?;
                """, (node_id,))
                row = cursor.fetchone()
                if not row:
                    raise NotFoundError(f"Node with ID {node_id!r} not found")
                return self._row_to_record(row)
            except sqlite3.Error as err:
                raise RepositoryError(f"Failed to fetch node {node_id!r}: {err}") from err

    def list_by_graph(self, graph_id: str, pagination: Pagination | None = None) -> list[NodeRecord]:
        """List NodeRecords belonging to graph_id in deterministic order."""
        pag = pagination or Pagination()
        with self._lock:
            try:
                cursor = self._conn.cursor()
                cursor.execute("""
                    SELECT node_id, graph_id, node_type, name, started_at, finished_at, duration_ms, status, parent_id, child_ids_json, inputs_json, outputs_json, metadata_json, tags_json, source, record_timestamp
                    FROM nodes WHERE graph_id = ?
                    ORDER BY started_at ASC, node_id ASC
                    LIMIT ? OFFSET ?;
                """, (graph_id, pag.limit, pag.offset))
                return [self._row_to_record(row) for row in cursor.fetchall()]
            except sqlite3.Error as err:
                raise RepositoryError(f"Failed to list nodes for graph {graph_id!r}: {err}") from err

    def get_parent(self, node_id: str) -> NodeRecord | None:
        """Fetch parent NodeRecord for node_id if it exists."""
        node = self.get_by_id(node_id)
        if not node.parent_id:
            return None
        return self.get_by_id(node.parent_id)

    def get_children(self, node_id: str) -> list[NodeRecord]:
        """Fetch child NodeRecords for node_id in deterministic order."""
        node = self.get_by_id(node_id)
        if not node.child_ids:
            return []
        with self._lock:
            try:
                placeholders = ",".join("?" for _ in node.child_ids)
                cursor = self._conn.cursor()
                cursor.execute(f"""
                    SELECT node_id, graph_id, node_type, name, started_at, finished_at, duration_ms, status, parent_id, child_ids_json, inputs_json, outputs_json, metadata_json, tags_json, source, record_timestamp
                    FROM nodes WHERE node_id IN ({placeholders})
                    ORDER BY started_at ASC, node_id ASC;
                """, node.child_ids)
                return [self._row_to_record(row) for row in cursor.fetchall()]
            except sqlite3.Error as err:
                raise RepositoryError(f"Failed to fetch children for node {node_id!r}: {err}") from err

    def _row_to_record(self, row: tuple) -> NodeRecord:
        return NodeRecord(
            node_id=row[0],
            graph_id=row[1],
            type=row[2],
            name=row[3],
            started_at=datetime.fromisoformat(row[4]),
            finished_at=datetime.fromisoformat(row[5]) if row[5] else None,
            duration_ms=row[6],
            status=row[7],
            parent_id=row[8],
            child_ids=json.loads(row[9]),
            inputs_json=row[10],
            outputs_json=row[11],
            metadata_json=row[12],
            tags=json.loads(row[13]),
            source=row[14],
            record_timestamp=datetime.fromisoformat(row[15]),
        )
