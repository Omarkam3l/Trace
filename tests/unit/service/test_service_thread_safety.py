"""Unit tests for multi-threaded concurrent TraceForgeApiService calls."""

from __future__ import annotations

import concurrent.futures
from datetime import UTC, datetime

from traceforge.service.service import TraceForgeApiService
from traceforge.storage.drivers.sqlite import SQLiteStorageDriver
from traceforge.storage.records import SessionRecord


def test_concurrent_api_service_calls():
    driver = SQLiteStorageDriver(":memory:")
    conn = driver.connection_manager.get_connection()

    now = datetime.now(UTC)
    s1 = SessionRecord(
        session_id="s1",
        started_at=now,
        status="completed",
        environment_os="win32",
        environment_python="3.13",
        profile_name="standard",
    )

    driver.begin_transaction()
    driver.write_batch([s1])
    driver.commit()

    service = TraceForgeApiService(conn)

    def worker_service(worker_id: int):
        sess = service.get_session("s1")
        assert sess.session_id == "s1"
        replay = service.replay_session("s1")
        assert replay.session.session_id == "s1"

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(worker_service, i) for i in range(10)]
        concurrent.futures.wait(futures)

    driver.close()
