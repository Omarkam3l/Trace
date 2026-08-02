"""Unit tests for SQLiteSchemaManager idempotent initialization."""

from __future__ import annotations

import sqlite3

from traceforge.storage.drivers.sqlite_schema import SQLiteSchemaManager


def test_sqlite_schema_manager_idempotent_creation():
    conn = sqlite3.connect(":memory:")
    mgr = SQLiteSchemaManager(conn)

    # Initial schema creation
    mgr.initialize_schema()

    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row[0] for row in cursor.fetchall()}

    expected_tables = {
        "sessions",
        "activities",
        "graphs",
        "nodes",
        "relationships",
        "snapshots",
        "raw_events",
    }
    assert expected_tables.issubset(tables)

    # Re-running schema creation is idempotent and does not fail
    mgr.initialize_schema()
    conn.close()
