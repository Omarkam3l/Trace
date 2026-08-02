"""SQLiteStorageDriver implementation of StorageDriver contract."""

from __future__ import annotations

import sqlite3
import threading
from pathlib import Path
from typing import Any

from traceforge.storage.drivers.base import StorageDriver
from traceforge.storage.drivers.sqlite_batch_writer import SQLiteBatchWriter
from traceforge.storage.drivers.sqlite_connection import SQLiteConnectionManager
from traceforge.storage.drivers.sqlite_exceptions import SQLiteTransactionError
from traceforge.storage.drivers.sqlite_schema import SQLiteSchemaManager


class SQLiteStorageDriver(StorageDriver):
    """Production-grade SQLite implementation of the StorageDriver contract."""

    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self._conn_mgr = SQLiteConnectionManager(db_path)
        self._schema_mgr = SQLiteSchemaManager(self._conn_mgr.get_connection())
        self._schema_mgr.initialize_schema()
        self._batch_writer = SQLiteBatchWriter(self._conn_mgr.get_connection())
        self._in_transaction: bool = False
        self._lock = threading.RLock()
        self._tx_lock = threading.RLock()

    @property
    def connection_manager(self) -> SQLiteConnectionManager:
        return self._conn_mgr

    def begin_transaction(self) -> None:
        """Begin explicit SQLite transaction safely serialized across threads."""
        self._tx_lock.acquire()
        with self._lock:
            if self._in_transaction:
                self._tx_lock.release()
                raise SQLiteTransactionError("Transaction already in progress")
            try:
                conn = self._conn_mgr.get_connection()
                conn.execute("BEGIN TRANSACTION;")
                self._in_transaction = True
            except sqlite3.Error as err:
                self._tx_lock.release()
                raise SQLiteTransactionError(f"Failed to begin transaction: {err}") from err

    def commit(self) -> None:
        """Commit active SQLite transaction."""
        with self._lock:
            if not self._in_transaction:
                return
            try:
                conn = self._conn_mgr.get_connection()
                conn.execute("COMMIT;")
            except sqlite3.Error as err:
                raise SQLiteTransactionError(f"Failed to commit transaction: {err}") from err
            finally:
                self._in_transaction = False
                self._tx_lock.release()

    def rollback(self) -> None:
        """Roll back active SQLite transaction."""
        with self._lock:
            if not self._in_transaction:
                return
            try:
                conn = self._conn_mgr.get_connection()
                conn.execute("ROLLBACK;")
            except sqlite3.Error as err:
                raise SQLiteTransactionError(f"Failed to rollback transaction: {err}") from err
            finally:
                self._in_transaction = False
                self._tx_lock.release()

    def write_batch(self, records: list[Any]) -> None:
        """Write list of Storage Records using SQLiteBatchWriter."""
        with self._lock:
            self._batch_writer.write_batch(records)

    def flush(self) -> None:
        """Flush active database writes."""
        pass

    def close(self) -> None:
        """Close SQLite database connection."""
        with self._lock:
            if self._in_transaction:
                try:
                    self.rollback()
                except Exception:
                    pass
            self._conn_mgr.close()
