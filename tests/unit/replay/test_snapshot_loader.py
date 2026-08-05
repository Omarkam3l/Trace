"""Unit tests for SnapshotLoader snapshot retrieval."""

from __future__ import annotations

from datetime import datetime, timezone

from traceforge.query.engine import QueryEngine
from traceforge.replay.snapshot_loader import SnapshotLoader
from traceforge.storage.drivers.sqlite import SQLiteStorageDriver
from traceforge.storage.records import SessionRecord, SnapshotRecord


def test_snapshot_loader_retrieval():
    driver = SQLiteStorageDriver(":memory:")
    conn = driver.connection_manager.get_connection()

    now = datetime.now(timezone.utc)
    s1 = SessionRecord(
        session_id="s1",
        started_at=now,
        status="completed",
        environment_os="win32",
        environment_python="3.13",
        profile_name="standard",
    )
    snap1 = SnapshotRecord(snapshot_id="snap1", session_id="s1", timestamp=now, nodes_count=5)

    driver.begin_transaction()
    driver.write_batch([s1, snap1])
    driver.commit()

    query_engine = QueryEngine(conn)
    loader = SnapshotLoader(query_engine)

    snapshots = loader.list_by_session("s1")
    assert len(snapshots) == 1
    assert snapshots[0].snapshot_id == "snap1"
    assert snapshots[0].nodes_count == 5

    driver.close()
