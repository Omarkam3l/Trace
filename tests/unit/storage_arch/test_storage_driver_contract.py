"""Unit tests for StorageDriver abstract contract."""

from __future__ import annotations

from typing import Any

import pytest

from traceforge.storage.drivers.base import StorageDriver


class DummyDriver(StorageDriver):
    def __init__(self) -> None:
        self.batches: list[list[Any]] = []
        self.in_transaction: bool = False
        self.flushed: bool = False
        self.closed: bool = False

    def begin_transaction(self) -> None:
        self.in_transaction = True

    def commit(self) -> None:
        self.in_transaction = False

    def rollback(self) -> None:
        self.in_transaction = False

    def write_batch(self, records: list[Any]) -> None:
        self.batches.append(list(records))

    def flush(self) -> None:
        self.flushed = True

    def close(self) -> None:
        self.closed = True


def test_storage_driver_interface_implementation():
    driver = DummyDriver()
    driver.begin_transaction()
    assert driver.in_transaction

    driver.write_batch(["rec1", "rec2"])
    assert len(driver.batches) == 1

    driver.commit()
    assert not driver.in_transaction

    driver.flush()
    assert driver.flushed

    driver.close()
    assert driver.closed
