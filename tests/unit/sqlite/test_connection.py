"""Unit tests for SQLiteConnectionManager."""

from __future__ import annotations

import tempfile
from pathlib import Path

from traceforge.storage.drivers.sqlite_connection import SQLiteConnectionManager


def test_sqlite_connection_manager_lifecycle():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_file = Path(tmpdir) / "test.db"
        mgr = SQLiteConnectionManager(db_file)
        assert not mgr.is_closed

        conn = mgr.get_connection()
        assert conn is not None

        # Connection reopening
        reconnected = mgr.reconnect()
        assert reconnected is not None
        assert not mgr.is_closed

        mgr.close()
        assert mgr.is_closed
