"""Unit tests for SQLiteBatchWriter parameterized Storage Record insertion."""

from __future__ import annotations

from datetime import datetime, timezone

from traceforge.storage.drivers.sqlite import SQLiteStorageDriver
from traceforge.storage.records import ActivityRecord, SessionRecord


def test_sqlite_batch_writer_records_insertion():
    driver = SQLiteStorageDriver(":memory:")
    now = datetime.now(timezone.utc)

    s_rec = SessionRecord(
        session_id="s1",
        started_at=now,
        status="completed",
        environment_os="win32",
        environment_python="3.13",
        profile_name="standard",
    )
    a_rec = ActivityRecord(
        activity_id="act1",
        session_id="s1",
        name="Checkout",
        started_at=now,
        status="completed",
        graph_id="g1",
    )

    driver.begin_transaction()
    driver.write_batch([s_rec, a_rec])
    driver.commit()

    conn = driver.connection_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT session_id FROM sessions;")
    assert cursor.fetchone()[0] == "s1"

    cursor.execute("SELECT activity_id FROM activities;")
    assert cursor.fetchone()[0] == "act1"

    driver.close()
