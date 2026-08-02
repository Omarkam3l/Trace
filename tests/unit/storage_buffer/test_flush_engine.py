"""Unit tests for FlushEngine batch creation, successful flush, and rollback error isolation."""

from __future__ import annotations

import pytest

from traceforge.storage.buffer import BufferManager
from traceforge.storage.drivers.base import StorageDriver
from traceforge.storage.exceptions import FlushError
from traceforge.storage.flush_engine import FlushEngine
from traceforge.storage.policies import SizeFlushPolicy


class MockStorageDriver(StorageDriver):
    def __init__(self, should_fail: bool = False) -> None:
        self.written_batches: list[list] = []
        self.should_fail = should_fail
        self.in_transaction = False
        self.rolled_back = False

    def begin_transaction(self) -> None:
        self.in_transaction = True

    def commit(self) -> None:
        self.in_transaction = False

    def rollback(self) -> None:
        self.in_transaction = False
        self.rolled_back = True

    def write_batch(self, records: list) -> None:
        if self.should_fail:
            raise RuntimeError("Disk write failed")
        self.written_batches.append(list(records))

    def flush(self) -> None:
        pass

    def close(self) -> None:
        pass


def test_flush_engine_successful_flush():
    buf = BufferManager()
    driver = MockStorageDriver()
    engine = FlushEngine(buffer=buf, driver=driver, policy=SizeFlushPolicy(max_records=2))

    buf.append("item1")
    buf.append("item2")

    batch = engine.flush_if_needed()
    assert batch is not None
    assert batch.record_count == 2
    assert len(driver.written_batches) == 1
    assert driver.written_batches[0] == ["item1", "item2"]
    assert buf.is_empty()


def test_flush_engine_failed_write_rollback_and_preservation():
    buf = BufferManager()
    driver = MockStorageDriver(should_fail=True)
    engine = FlushEngine(buffer=buf, driver=driver)

    buf.append("item1")
    buf.append("item2")

    with pytest.raises(FlushError):
        engine.flush()

    assert driver.rolled_back
    # Verification: Failed records are restored back to buffer in original order
    assert buf.peek() == ["item1", "item2"]
