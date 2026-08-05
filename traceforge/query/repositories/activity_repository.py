"""ActivityRepository read repository."""

from __future__ import annotations

import sqlite3
import threading
from datetime import datetime

from traceforge.query.exceptions import NotFoundError, RepositoryError
from traceforge.query.pagination import Pagination
from traceforge.storage.records.activity_record import ActivityRecord


class ActivityRepository:
    """Read repository for ActivityRecord storage models."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection
        self._lock = threading.RLock()

    def get_by_id(self, activity_id: str) -> ActivityRecord:
        """Fetch ActivityRecord by ID or raise NotFoundError."""
        with self._lock:
            try:
                cursor = self._conn.cursor()
                cursor.execute(
                    """
                    SELECT activity_id, session_id, name, started_at, finished_at, duration_ms, status, graph_id, record_timestamp
                    FROM activities WHERE activity_id = ?;
                """,
                    (activity_id,),
                )
                row = cursor.fetchone()
                if not row:
                    raise NotFoundError(f"Activity with ID {activity_id!r} not found")
                return self._row_to_record(row)
            except sqlite3.Error as err:
                raise RepositoryError(f"Failed to fetch activity {activity_id!r}: {err}") from err

    def list_by_session(self, session_id: str, pagination: Pagination | None = None) -> list[ActivityRecord]:
        """List ActivityRecords belonging to a session_id in deterministic order."""
        pag = pagination or Pagination()
        with self._lock:
            try:
                cursor = self._conn.cursor()
                cursor.execute(
                    """
                    SELECT activity_id, session_id, name, started_at, finished_at, duration_ms, status, graph_id, record_timestamp
                    FROM activities WHERE session_id = ?
                    ORDER BY started_at ASC, activity_id ASC
                    LIMIT ? OFFSET ?;
                """,
                    (session_id, pag.limit, pag.offset),
                )
                return [self._row_to_record(row) for row in cursor.fetchall()]
            except sqlite3.Error as err:
                raise RepositoryError(f"Failed to list activities for session {session_id!r}: {err}") from err

    def exists(self, activity_id: str) -> bool:
        """Return True if activity_id exists."""
        with self._lock:
            try:
                cursor = self._conn.cursor()
                cursor.execute("SELECT 1 FROM activities WHERE activity_id = ?;", (activity_id,))
                return cursor.fetchone() is not None
            except sqlite3.Error as err:
                raise RepositoryError(f"Failed to check existence for activity {activity_id!r}: {err}") from err

    def _row_to_record(self, row: tuple) -> ActivityRecord:
        return ActivityRecord(
            activity_id=row[0],
            session_id=row[1],
            name=row[2],
            started_at=datetime.fromisoformat(row[3]),
            finished_at=datetime.fromisoformat(row[4]) if row[4] else None,
            duration_ms=row[5],
            status=row[6],
            graph_id=row[7],
            record_timestamp=datetime.fromisoformat(row[8]),
        )
