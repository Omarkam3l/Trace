"""RawEventRepository read repository."""

from __future__ import annotations

import sqlite3
import threading
from datetime import datetime

from traceforge.query.exceptions import RepositoryError
from traceforge.query.pagination import Pagination
from traceforge.storage.records.raw_event_record import RawEventRecord


class RawEventRepository:
    """Read repository for RawEventRecord storage models."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection
        self._lock = threading.RLock()

    def list_by_session(self, session_id: str, pagination: Pagination | None = None) -> list[RawEventRecord]:
        """List RawEventRecords belonging to a session in deterministic order."""
        pag = pagination or Pagination()
        with self._lock:
            try:
                cursor = self._conn.cursor()
                cursor.execute(
                    """
                    SELECT event_id, timestamp, sequence, type, source, payload_json, context_id, activity_hint, metadata_json, record_timestamp
                    FROM raw_events WHERE context_id = ? OR activity_hint = ?
                    ORDER BY timestamp ASC, sequence ASC, event_id ASC
                    LIMIT ? OFFSET ?;
                """,
                    (session_id, session_id, pag.limit, pag.offset),
                )
                return [self._row_to_record(row) for row in cursor.fetchall()]
            except sqlite3.Error as err:
                raise RepositoryError(f"Failed to list raw events for session {session_id!r}: {err}") from err

    def list_by_activity(self, activity_id: str, pagination: Pagination | None = None) -> list[RawEventRecord]:
        """List RawEventRecords belonging to an activity_id in deterministic order."""
        pag = pagination or Pagination()
        with self._lock:
            try:
                cursor = self._conn.cursor()
                cursor.execute(
                    """
                    SELECT event_id, timestamp, sequence, type, source, payload_json, context_id, activity_hint, metadata_json, record_timestamp
                    FROM raw_events WHERE activity_hint = ?
                    ORDER BY timestamp ASC, sequence ASC, event_id ASC
                    LIMIT ? OFFSET ?;
                """,
                    (activity_id, pag.limit, pag.offset),
                )
                return [self._row_to_record(row) for row in cursor.fetchall()]
            except sqlite3.Error as err:
                raise RepositoryError(f"Failed to list raw events for activity {activity_id!r}: {err}") from err

    def list_all(self, pagination: Pagination | None = None) -> list[RawEventRecord]:
        """List all RawEventRecords in deterministic order."""
        pag = pagination or Pagination()
        with self._lock:
            try:
                cursor = self._conn.cursor()
                cursor.execute(
                    """
                    SELECT event_id, timestamp, sequence, type, source, payload_json, context_id, activity_hint, metadata_json, record_timestamp
                    FROM raw_events
                    ORDER BY timestamp ASC, sequence ASC, event_id ASC
                    LIMIT ? OFFSET ?;
                """,
                    (pag.limit, pag.offset),
                )
                return [self._row_to_record(row) for row in cursor.fetchall()]
            except sqlite3.Error as err:
                raise RepositoryError(f"Failed to list raw events: {err}") from err

    def _row_to_record(self, row: tuple) -> RawEventRecord:
        return RawEventRecord(
            event_id=row[0],
            timestamp=datetime.fromisoformat(row[1]),
            sequence=row[2],
            type=row[3],
            source=row[4],
            payload_json=row[5],
            context_id=row[6],
            activity_hint=row[7],
            metadata_json=row[8],
            record_timestamp=datetime.fromisoformat(row[9]),
        )
