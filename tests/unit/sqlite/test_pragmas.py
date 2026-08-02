"""Unit tests for SQLite PRAGMA configuration verification."""

from __future__ import annotations

import tempfile
from pathlib import Path

from traceforge.storage.drivers.sqlite_connection import SQLiteConnectionManager


def test_sqlite_pragma_configuration():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_file = Path(tmpdir) / "pragma_test.db"
        mgr = SQLiteConnectionManager(db_file)
        conn = mgr.get_connection()
        cursor = conn.cursor()

        cursor.execute("PRAGMA foreign_keys;")
        fk_val = cursor.fetchone()[0]
        assert fk_val == 1

        cursor.execute("PRAGMA journal_mode;")
        jm_val = cursor.fetchone()[0].upper()
        assert jm_val == "WAL"

        mgr.close()
