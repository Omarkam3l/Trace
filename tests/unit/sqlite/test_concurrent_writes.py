"""Unit tests for multi-threaded concurrent SQLiteStorageDriver batch writes."""

from __future__ import annotations

import concurrent.futures
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from traceforge.storage.drivers.sqlite import SQLiteStorageDriver
from traceforge.storage.records import RawEventRecord


def test_concurrent_sqlite_batch_writes():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_file = Path(tmpdir) / "concurrent.db"
        driver = SQLiteStorageDriver(db_file)

        now = datetime.now(UTC)

        def worker_write(worker_id: int):
            driver.begin_transaction()
            records = [
                RawEventRecord(
                    event_id=f"w{worker_id}_e{i}",
                    timestamp=now,
                    sequence=i,
                    type="ConcurrentTest",
                    source="thread_pool",
                )
                for i in range(20)
            ]
            driver.write_batch(records)
            driver.commit()

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(worker_write, w) for w in range(5)]
            concurrent.futures.wait(futures)

        conn = driver.connection_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM raw_events;")
        total_rows = cursor.fetchone()[0]
        assert total_rows == 100

        driver.close()
