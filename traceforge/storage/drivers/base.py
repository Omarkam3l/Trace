"""StorageDriver Abstract Base Class."""

from __future__ import annotations

import abc
from typing import Any


class StorageDriver(abc.ABC):
    """Abstract interface contract for all TraceForge storage driver backends."""

    @abc.abstractmethod
    def begin_transaction(self) -> None:
        """Begin a transaction block."""
        pass

    @abc.abstractmethod
    def commit(self) -> None:
        """Commit the active transaction."""
        pass

    @abc.abstractmethod
    def rollback(self) -> None:
        """Roll back the active transaction on error."""
        pass

    @abc.abstractmethod
    def write_batch(self, records: list[Any]) -> None:
        """Write a batch of Storage Record instances to persistence."""
        pass

    @abc.abstractmethod
    def flush(self) -> None:
        """Flush buffered writes to physical storage."""
        pass

    @abc.abstractmethod
    def close(self) -> None:
        """Close the storage driver and release underlying resources."""
        pass
