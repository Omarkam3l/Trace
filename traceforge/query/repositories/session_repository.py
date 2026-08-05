"""SessionRepository read repository."""

from __future__ import annotations

import sqlite3
import threading
from datetime import datetime

from traceforge.query.exceptions import NotFoundError, RepositoryError
from traceforge.query.filters import QueryFilter
from traceforge.query.pagination import Pagination
from traceforge.storage.records.session_record import SessionRecord


class SessionRepository:
    """Read repository for SessionRecord storage models."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection
        self._lock = threading.RLock()

    def get_by_id(self, session_id: str) -> SessionRecord:
        """Fetch SessionRecord by ID or raise NotFoundError."""
        with self._lock:
            try:
                cursor = self._conn.cursor()
                cursor.execute(
                    """
                    SELECT session_id, started_at, finished_at, duration_ms, status, environment_os, environment_python, profile_name, record_timestamp
                    FROM sessions WHERE session_id = ?;
                """,
                    (session_id,),
                )
                row = cursor.fetchone()
                if not row:
                    raise NotFoundError(f"Session with ID {session_id!r} not found")
                return self._row_to_record(row)
            except sqlite3.Error as err:
                raise RepositoryError(f"Failed to fetch session {session_id!r}: {err}") from err

    def list(self, filter: QueryFilter | None = None, pagination: Pagination | None = None) -> list[SessionRecord]:
        """List SessionRecords matching optional filter and pagination in deterministic order."""
        pag = pagination or Pagination()
        with self._lock:
            try:
                query = "SELECT session_id, started_at, finished_at, duration_ms, status, environment_os, environment_python, profile_name, record_timestamp FROM sessions WHERE 1=1"
                params: list[str] = []

                if filter:
                    if filter.session_id:
                        query += " AND session_id = ?"
                        params.append(filter.session_id)
                    if filter.status:
                        query += " AND status = ?"
                        params.append(filter.status)

                query += " ORDER BY started_at ASC, session_id ASC LIMIT ? OFFSET ?;"
                params.extend([str(pag.limit), str(pag.offset)])

                cursor = self._conn.cursor()
                cursor.execute(query, params)
                return [self._row_to_record(row) for row in cursor.fetchall()]
            except sqlite3.Error as err:
                raise RepositoryError(f"Failed to list sessions: {err}") from err

    def exists(self, session_id: str) -> bool:
        """Return True if session_id exists."""
        with self._lock:
            try:
                cursor = self._conn.cursor()
                cursor.execute("SELECT 1 FROM sessions WHERE session_id = ?;", (session_id,))
                return cursor.fetchone() is not None
            except sqlite3.Error as err:
                raise RepositoryError(f"Failed to check existence for session {session_id!r}: {err}") from err

    def _row_to_record(self, row: tuple) -> SessionRecord:
        return SessionRecord(
            session_id=row[0],
            started_at=datetime.fromisoformat(row[1]),
            finished_at=datetime.fromisoformat(row[2]) if row[2] else None,
            duration_ms=row[3],
            status=row[4],
            environment_os=row[5],
            environment_python=row[6],
            profile_name=row[7],
            record_timestamp=datetime.fromisoformat(row[8]),
        )
