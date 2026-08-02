"""SQLite storage driver exception hierarchy."""

from __future__ import annotations

from traceforge.api.exceptions import StorageError


class SQLiteConnectionError(StorageError):
    """Raised when connection or reconnection to the SQLite database fails."""


class SQLiteConstraintError(StorageError):
    """Raised when a SQLite database constraint (primary key, foreign key, unique, check) is violated."""


class SQLiteTransactionError(StorageError):
    """Raised when begin, commit, or rollback transaction operations fail in SQLite."""


class SQLiteWriteError(StorageError):
    """Raised when writing or executing SQL statements fails."""
