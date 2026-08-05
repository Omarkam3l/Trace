"""Unit tests for multi-threaded concurrent QueryEngine reads."""

from __future__ import annotations

import concurrent.futures
from datetime import UTC, datetime

from traceforge.query.engine import QueryEngine
from traceforge.query.queries import SessionQuery
from traceforge.storage.drivers.sqlite import SQLiteStorageDriver
from traceforge.storage.records.session_record import SessionRecord


def test_concurrent_query_engine_reads():
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

    engine = QueryEngine(conn)

    def reader_worker(worker_id: int):
        res = engine.execute_session_query(SessionQuery(session_id="s1"))
        assert len(res) == 1
        assert res[0].session_id == "s1"

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(reader_worker, i) for i in range(10)]
        concurrent.futures.wait(futures)

    driver.close()
