"""Unit tests for SQLite foreign key constraints and primary key violation translation."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from traceforge.storage.drivers.sqlite import SQLiteStorageDriver
from traceforge.storage.drivers.sqlite_exceptions import SQLiteConstraintError
from traceforge.storage.records import ActivityRecord, SessionRecord


def test_sqlite_primary_key_and_foreign_key_constraints():
    driver = SQLiteStorageDriver(":memory:")
    now = datetime.now(UTC)

    s_rec = SessionRecord(
        session_id="s1",
        started_at=now,
        status="completed",
        environment_os="win32",
        environment_python="3.13",
        profile_name="standard",
    )

    driver.begin_transaction()
    driver.write_batch([s_rec])
    driver.commit()

    # Duplicate primary key raises SQLiteConstraintError
    driver.begin_transaction()
    with pytest.raises(SQLiteConstraintError):
        driver.write_batch([s_rec])
    driver.rollback()

    # Foreign key constraint failure (activity referencing non-existent session_id 'missing_sess')
    bad_activity = ActivityRecord(
        activity_id="act_bad",
        session_id="missing_sess",
        name="BadAct",
        started_at=now,
        status="completed",
        graph_id="g_bad",
    )

    driver.begin_transaction()
    with pytest.raises(SQLiteConstraintError):
        driver.write_batch([bad_activity])
    driver.rollback()

    driver.close()
