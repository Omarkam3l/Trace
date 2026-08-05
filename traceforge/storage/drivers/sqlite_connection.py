"""SQLiteConnectionManager for thread-safe SQLite connection management and PRAGMA configuration."""

from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

from traceforge.storage.drivers.sqlite_exceptions import SQLiteConnectionError


class SQLiteConnectionManager:
    """Manages SQLite database connections, automatic PRAGMA initialization, and thread safety."""

    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self._db_path = str(db_path)
        self._connection: sqlite3.Connection | None = None
        self._lock = threading.RLock()
        self._open_connection()

    @property
    def db_path(self) -> str:
        return self._db_path

    @property
    def is_closed(self) -> bool:
        with self._lock:
            return self._connection is None

    def get_connection(self) -> sqlite3.Connection:
        """Return the active SQLite connection."""
        with self._lock:
            if self._connection is None:
                self._open_connection()
            assert self._connection is not None
            return self._connection

    def reconnect(self) -> sqlite3.Connection:
        """Close current connection and reopen a fresh connection."""
        with self._lock:
            self.close()
            return self.get_connection()

    def close(self) -> None:
        """Close active SQLite connection."""
        with self._lock:
            if self._connection is not None:
                try:
                    self._connection.close()
                except sqlite3.Error:
                    pass
                finally:
                    self._connection = None

    def _open_connection(self) -> None:
        try:
            conn = sqlite3.connect(
                self._db_path,
                check_same_thread=False,
                isolation_level=None,
            )
            # Execute PRAGMA configurations outside transaction
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute("PRAGMA synchronous = NORMAL;")
            cursor.execute("PRAGMA temp_store = MEMORY;")
            cursor.execute("PRAGMA cache_size = -64000;")

            # journal_mode = WAL (only if not :memory:)
            if self._db_path != ":memory:":
                cursor.execute("PRAGMA journal_mode = WAL;")

            self._connection = conn
        except sqlite3.Error as err:
            raise SQLiteConnectionError(f"Failed to open SQLite database at {self._db_path!r}: {err}") from err
