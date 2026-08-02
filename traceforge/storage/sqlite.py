"""SQLite storage adapter.

SQLite only supports one writer at a time, so all access is serialized
through a single connection guarded by a ``threading.Lock``, with the
actual (blocking) sqlite3 calls offloaded via ``asyncio.to_thread`` to
keep the event loop responsive.
"""

from __future__ import annotations

import asyncio
import sqlite3
import threading
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from traceforge.models.enums import SpanKind, SpanStatus
from traceforge.models.span import SpanModel
from traceforge.storage.base import StorageAdapter
from traceforge.utils.serialization import dumps

_SCHEMA = """
CREATE TABLE IF NOT EXISTS spans (
    id TEXT PRIMARY KEY,
    trace_id TEXT NOT NULL,
    parent_span_id TEXT,
    name TEXT NOT NULL,
    kind TEXT NOT NULL,
    status TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT,
    duration_ms REAL,
    attributes TEXT NOT NULL,
    events TEXT NOT NULL,
    exception TEXT,
    correlation_id TEXT,
    session_id TEXT
);
CREATE INDEX IF NOT EXISTS idx_spans_trace_id ON spans(trace_id);
CREATE INDEX IF NOT EXISTS idx_spans_correlation_id ON spans(correlation_id);
"""


class SQLiteStorage(StorageAdapter):
    """Durable, queryable local storage backed by SQLite."""

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(str(self._path), check_same_thread=False)
        with self._lock:
            self._conn.executescript(_SCHEMA)
            self._conn.commit()

    async def write_spans(self, spans: Sequence[SpanModel]) -> None:
        if not spans:
            return
        await asyncio.to_thread(self._write_spans_sync, spans)

    def _write_spans_sync(self, spans: Sequence[SpanModel]) -> None:
        rows = [
            (
                s.id,
                s.trace_id,
                s.parent_span_id,
                s.name,
                s.kind.value,
                s.status.value,
                s.start_time.isoformat(),
                s.end_time.isoformat() if s.end_time else None,
                s.duration_ms,
                dumps(s.attributes),
                dumps(s.events),
                dumps(s.exception) if s.exception else None,
                s.correlation_id,
                s.session_id,
            )
            for s in spans
        ]
        with self._lock:
            self._conn.executemany(
                """
                INSERT OR REPLACE INTO spans
                (id, trace_id, parent_span_id, name, kind, status, start_time,
                 end_time, duration_ms, attributes, events, exception,
                 correlation_id, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
            self._conn.commit()

    async def query_spans(
        self,
        *,
        trace_id: str | None = None,
        correlation_id: str | None = None,
        limit: int = 100,
    ) -> list[SpanModel]:
        return await asyncio.to_thread(self._query_spans_sync, trace_id, correlation_id, limit)

    def _query_spans_sync(
        self, trace_id: str | None, correlation_id: str | None, limit: int
    ) -> list[SpanModel]:
        clauses: list[str] = []
        params: list[str] = []
        if trace_id is not None:
            clauses.append("trace_id = ?")
            params.append(trace_id)
        if correlation_id is not None:
            clauses.append("correlation_id = ?")
            params.append(correlation_id)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        query = f"SELECT * FROM spans {where} ORDER BY start_time DESC LIMIT ?"
        params_with_limit = [*params, limit]
        with self._lock:
            cursor = self._conn.execute(query, params_with_limit)
            columns = [c[0] for c in cursor.description]
            rows = cursor.fetchall()
        return [self._row_to_model(dict(zip(columns, row, strict=True))) for row in rows]

    @staticmethod
    def _row_to_model(row: dict[str, Any]) -> SpanModel:
        import json

        return SpanModel(
            id=row["id"],
            trace_id=row["trace_id"],
            parent_span_id=row["parent_span_id"],
            name=row["name"],
            kind=SpanKind(row["kind"]),
            status=SpanStatus(row["status"]),
            start_time=row["start_time"],
            end_time=row["end_time"],
            duration_ms=row["duration_ms"],
            attributes=json.loads(row["attributes"]),
            events=json.loads(row["events"]),
            exception=json.loads(row["exception"]) if row["exception"] else None,
            correlation_id=row["correlation_id"],
            session_id=row["session_id"],
        )

    async def close(self) -> None:
        def _close() -> None:
            with self._lock:
                self._conn.close()

        await asyncio.to_thread(_close)
