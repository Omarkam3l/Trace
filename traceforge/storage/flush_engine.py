"""FlushEngine: orchestrates write buffer draining and transactional batch persistence."""

from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from traceforge.storage.batch import Batch
from traceforge.storage.exceptions import FlushError
from traceforge.storage.policies import FlushPolicy, HybridFlushPolicy
from traceforge.storage.transaction_manager import TransactionManager

if TYPE_CHECKING:
    from traceforge.storage.buffer import BufferManager
    from traceforge.storage.drivers.base import StorageDriver


class FlushEngine:
    """Coordinates draining BufferManager, constructing immutable Batch objects, and persisting them."""

    def __init__(
        self,
        buffer: BufferManager,
        driver: StorageDriver,
        policy: FlushPolicy | None = None,
        transaction_manager: TransactionManager | None = None,
    ) -> None:
        self._buffer = buffer
        self._driver = driver
        self._policy = policy or HybridFlushPolicy()
        self._tx_manager = transaction_manager or TransactionManager(driver)
        self._lock = threading.RLock()

    @property
    def buffer(self) -> BufferManager:
        return self._buffer

    @property
    def policy(self) -> FlushPolicy:
        return self._policy

    @property
    def transaction_manager(self) -> TransactionManager:
        return self._tx_manager

    def flush_if_needed(self) -> Batch | None:
        """Check flush policy and execute flush if condition is met."""
        with self._lock:
            if self._policy.should_flush(self._buffer):
                return self.flush()
            return None

    def flush(self) -> Batch | None:
        """Force flush all buffered records to persistence within a transaction block."""
        with self._lock:
            if self._buffer.is_empty():
                return None

            drained = self._buffer.drain()
            if not drained:
                return None

            now = datetime.now(timezone.utc)
            batch = Batch(
                batch_id=f"batch_{uuid.uuid4().hex[:16]}",
                created_at=now,
                records=tuple(drained),
                record_count=len(drained),
            )

            try:
                self._tx_manager.begin_transaction()
                self._driver.write_batch(list(batch.records))
                self._driver.flush()
                self._tx_manager.commit()

                if hasattr(self._policy, "notify_flushed"):
                    self._policy.notify_flushed()

                return batch

            except Exception as err:
                # Rollback transaction and re-append records back into buffer to preserve ordering
                try:
                    self._tx_manager.rollback()
                except Exception:
                    pass

                # Prepend records back into buffer to preserve insertion order
                self._buffer.append_many(drained)
                raise FlushError(f"Batch flush failed: {err}") from err
