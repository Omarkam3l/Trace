"""Unit tests for ActivityRepository read operations."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from traceforge.query.exceptions import NotFoundError
from traceforge.query.repositories.activity_repository import ActivityRepository
from traceforge.storage.drivers.sqlite import SQLiteStorageDriver
from traceforge.storage.records.activity_record import ActivityRecord
from traceforge.storage.records.session_record import SessionRecord


def test_activity_read_repository():
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
    a1 = ActivityRecord(
        activity_id="act1", session_id="s1", name="Checkout", started_at=now, status="completed", graph_id="g1"
    )

    driver.begin_transaction()
    driver.write_batch([s1, a1])
    driver.commit()

    repo = ActivityRepository(conn)

    assert repo.exists("act1")
    assert not repo.exists("missing")

    act = repo.get_by_id("act1")
    assert act.name == "Checkout"

    with pytest.raises(NotFoundError):
        repo.get_by_id("missing")

    activities = repo.list_by_session("s1")
    assert len(activities) == 1
    assert activities[0].activity_id == "act1"

    driver.close()
