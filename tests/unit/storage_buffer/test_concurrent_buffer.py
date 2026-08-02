"""Unit tests for concurrent producers, thread-safe buffer operations, and flush engine stress testing."""

from __future__ import annotations

import concurrent.futures

from traceforge.storage.buffer import BufferManager
from traceforge.storage.drivers.base import StorageDriver
from traceforge.storage.flush_engine import FlushEngine


class ConcurrencyDriver(StorageDriver):
    def __init__(self) -> None:
        self.flushed_records: list = []

    def begin_transaction(self) -> None:
        pass

    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass

    def write_batch(self, records: list) -> None:
        self.flushed_records.extend(records)

    def flush(self) -> None:
        pass

    def close(self) -> None:
        pass


def test_concurrent_producers_and_flush_engine_stress():
    buf = BufferManager()
    driver = ConcurrencyDriver()
    engine = FlushEngine(buffer=buf, driver=driver)

    def producer(worker_id: int):
        for i in range(50):
            buf.append(f"w{worker_id}_{i}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(producer, w) for w in range(5)]
        concurrent.futures.wait(futures)

    assert buf.size() == 250

    batch = engine.flush()
    assert batch is not None
    assert batch.record_count == 250
    assert len(driver.flushed_records) == 250
    assert buf.is_empty()
