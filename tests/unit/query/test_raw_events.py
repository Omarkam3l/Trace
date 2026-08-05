"""Unit tests for RawEventRepository read operations."""

from __future__ import annotations

from datetime import UTC, datetime

from traceforge.query.repositories.raw_event_repository import RawEventRepository
from traceforge.storage.drivers.sqlite import SQLiteStorageDriver
from traceforge.storage.records.raw_event_record import RawEventRecord


def test_raw_event_read_repository():
    driver = SQLiteStorageDriver(":memory:")
    conn = driver.connection_manager.get_connection()

    now = datetime.now(UTC)
    e1 = RawEventRecord(
        event_id="e1", timestamp=now, sequence=1, type="FunctionEntered", source="python_sdk", context_id="s1"
    )
    e2 = RawEventRecord(
        event_id="e2", timestamp=now, sequence=2, type="FunctionReturned", source="python_sdk", activity_hint="act1"
    )

    driver.begin_transaction()
    driver.write_batch([e1, e2])
    driver.commit()

    repo = RawEventRepository(conn)

    s1_events = repo.list_by_session("s1")
    assert len(s1_events) == 1
    assert s1_events[0].event_id == "e1"

    act1_events = repo.list_by_activity("act1")
    assert len(act1_events) == 1
    assert act1_events[0].event_id == "e2"

    all_events = repo.list_all()
    assert len(all_events) == 2

    driver.close()
