"""Unit tests for SQLiteStorageDriver integration with BufferManager and FlushEngine."""

from __future__ import annotations

from datetime import datetime, timezone

from traceforge.storage.buffer import BufferManager
from traceforge.storage.drivers.sqlite import SQLiteStorageDriver
from traceforge.storage.flush_engine import FlushEngine
from traceforge.storage.records import RawEventRecord


def test_sqlite_driver_flush_engine_integration():
    driver = SQLiteStorageDriver(":memory:")
    buf = BufferManager()
    engine = FlushEngine(buffer=buf, driver=driver)

    now = datetime.now(timezone.utc)
    for i in range(10):
        rec = RawEventRecord(
            event_id=f"evt_{i}",
            timestamp=now,
            sequence=i,
            type="FunctionEntered",
            source="python_sdk",
        )
        buf.append(rec)

    assert buf.size() == 10

    batch = engine.flush()
    assert batch is not None
    assert batch.record_count == 10
    assert buf.is_empty()

    conn = driver.connection_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM raw_events;")
    assert cursor.fetchone()[0] == 10

    driver.close()
