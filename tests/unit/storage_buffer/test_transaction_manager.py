"""Unit tests for TransactionManager lifecycle and nested transaction rejection."""

from __future__ import annotations

import pytest

from traceforge.storage.drivers.base import StorageDriver
from traceforge.storage.exceptions import TransactionError
from traceforge.storage.transaction_manager import TransactionManager


class DummyDriver(StorageDriver):
    def __init__(self) -> None:
        self.in_tx = False

    def begin_transaction(self) -> None:
        self.in_tx = True

    def commit(self) -> None:
        self.in_tx = False

    def rollback(self) -> None:
        self.in_tx = False

    def write_batch(self, records: list) -> None:
        pass

    def flush(self) -> None:
        pass

    def close(self) -> None:
        pass


def test_transaction_manager_lifecycle_and_nested_rejection():
    driver = DummyDriver()
    tx_mgr = TransactionManager(driver)

    assert not tx_mgr.is_in_transaction

    tx_mgr.begin_transaction()
    assert tx_mgr.is_in_transaction
    assert driver.in_tx

    # Rejects nested transaction
    with pytest.raises(TransactionError):
        tx_mgr.begin_transaction()

    tx_mgr.commit()
    assert not tx_mgr.is_in_transaction
    assert not driver.in_tx

    # Rejects commit without active transaction
    with pytest.raises(TransactionError):
        tx_mgr.commit()
