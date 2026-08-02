"""Unit tests for multi-threaded concurrent ReplayEngine operations."""

from __future__ import annotations

import concurrent.futures
from datetime import datetime, timezone

from traceforge.query.engine import QueryEngine
from traceforge.replay.engine import ReplayEngine
from traceforge.storage.drivers.sqlite import SQLiteStorageDriver
from traceforge.storage.records import ActivityRecord, SessionRecord


def test_concurrent_replay_engine_reconstruction():
    driver = SQLiteStorageDriver(":memory:")
    conn = driver.connection_manager.get_connection()

    now = datetime.now(timezone.utc)
    s1 = SessionRecord(session_id="s1", started_at=now, status="completed", environment_os="win32", environment_python="3.13", profile_name="standard")
    a1 = ActivityRecord(activity_id="act1", session_id="s1", name="Checkout", started_at=now, status="completed", graph_id="g1")

    driver.begin_transaction()
    driver.write_batch([s1, a1])
    driver.commit()

    query_engine = QueryEngine(conn)
    replay_engine = ReplayEngine(query_engine)

    def worker_replay(worker_id: int):
        res = replay_engine.replay_session("s1")
        assert res.session is not None
        assert res.session.session_id == "s1"
        assert len(res.activities) == 1

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(worker_replay, i) for i in range(10)]
        concurrent.futures.wait(futures)

    driver.close()
