"""Unit tests for TraceForgeApiService exception handling."""

from __future__ import annotations

import pytest

from traceforge.service.exceptions import ServiceNotFoundError
from traceforge.service.service import TraceForgeApiService
from traceforge.storage.drivers.sqlite import SQLiteStorageDriver


def test_api_service_not_found_exception():
    driver = SQLiteStorageDriver(":memory:")
    conn = driver.connection_manager.get_connection()

    service = TraceForgeApiService(conn)

    with pytest.raises(ServiceNotFoundError):
        service.get_session("non_existent")

    with pytest.raises(ServiceNotFoundError):
        service.replay_session("non_existent")

    driver.close()
