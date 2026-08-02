"""TransactionManager for coordinating StorageDriver transactions."""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

from traceforge.storage.exceptions import TransactionError

if TYPE_CHECKING:
    from traceforge.storage.drivers.base import StorageDriver


class TransactionManager:
    """Coordinates transaction lifecycle over a StorageDriver backend."""

    def __init__(self, driver: StorageDriver) -> None:
        self._driver = driver
        self._in_transaction: bool = False
        self._lock = threading.RLock()

    @property
    def is_in_transaction(self) -> bool:
        with self._lock:
            return self._in_transaction

    def begin_transaction(self) -> None:
        """Begin a transaction block. Rejects nested transactions."""
        with self._lock:
            if self._in_transaction:
                raise TransactionError("Nested transactions are prohibited")
            self._driver.begin_transaction()
            self._in_transaction = True

    def commit(self) -> None:
        """Commit the current active transaction."""
        with self._lock:
            if not self._in_transaction:
                raise TransactionError("Cannot commit: No active transaction")
            try:
                self._driver.commit()
            finally:
                self._in_transaction = False

    def rollback(self) -> None:
        """Roll back the current active transaction."""
        with self._lock:
            if not self._in_transaction:
                return
            try:
                self._driver.rollback()
            finally:
                self._in_transaction = False
