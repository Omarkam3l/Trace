"""Unit tests for SQLiteStorageDriver transaction commit and rollback."""

from __future__ import annotations

from traceforge.storage.drivers.sqlite import SQLiteStorageDriver


def test_sqlite_transaction_commit_and_rollback():
    driver = SQLiteStorageDriver(":memory:")
    conn = driver.connection_manager.get_connection()

    driver.begin_transaction()
    conn.execute(
        "INSERT INTO sessions (session_id, started_at, status, environment_os, environment_python, profile_name, record_timestamp) VALUES ('s1', '2026-01-01', 'completed', 'win32', '3.13', 'std', '2026-01-01');"
    )
    driver.commit()

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sessions WHERE session_id = 's1';")
    assert cursor.fetchone()[0] == 1

    # Rollback verification
    driver.begin_transaction()
    conn.execute(
        "INSERT INTO sessions (session_id, started_at, status, environment_os, environment_python, profile_name, record_timestamp) VALUES ('s2', '2026-01-01', 'completed', 'win32', '3.13', 'std', '2026-01-01');"
    )
    driver.rollback()

    cursor.execute("SELECT COUNT(*) FROM sessions WHERE session_id = 's2';")
    assert cursor.fetchone()[0] == 0

    driver.close()
