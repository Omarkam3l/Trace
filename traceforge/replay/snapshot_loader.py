"""SnapshotLoader for retrieving historical session snapshots."""

from __future__ import annotations

import sqlite3
import threading
from datetime import datetime
from typing import TYPE_CHECKING

from traceforge.query.exceptions import RepositoryError

if TYPE_CHECKING:
    from traceforge.query.engine import QueryEngine
    from traceforge.storage.records.snapshot_record import SnapshotRecord


class SnapshotLoader:
    """Retrieves historical snapshots using QueryEngine."""

    def __init__(self, query_engine: QueryEngine) -> None:
        self._query_engine = query_engine
        self._lock = threading.RLock()

    def list_by_session(self, session_id: str) -> list[SnapshotRecord]:
        """Fetch all snapshots for a session_id ordered by timestamp."""
        with self._lock:
            try:
                conn = self._query_engine.sessions._conn
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT snapshot_id, session_id, timestamp, active_activity_id, nodes_count, relationships_count, record_timestamp
                    FROM snapshots WHERE session_id = ?
                    ORDER BY timestamp ASC;
                """, (session_id,))
                rows = cursor.fetchall()
                from traceforge.storage.records.snapshot_record import SnapshotRecord
                return [
                    SnapshotRecord(
                        snapshot_id=row[0],
                        session_id=row[1],
                        timestamp=datetime.fromisoformat(row[2]),
                        active_activity_id=row[3],
                        nodes_count=row[4],
                        relationships_count=row[5],
                        record_timestamp=datetime.fromisoformat(row[6]),
                    )
                    for row in rows
                ]
            except sqlite3.Error as err:
                raise RepositoryError(f"Failed to load snapshots for session {session_id!r}: {err}") from err
