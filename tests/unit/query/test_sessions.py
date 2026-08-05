"""Unit tests for SessionRepository read operations."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from traceforge.query.exceptions import NotFoundError
from traceforge.query.filters import QueryFilter
from traceforge.query.pagination import Pagination
from traceforge.storage.drivers.sqlite import SQLiteStorageDriver
from traceforge.storage.records.session_record import SessionRecord


def test_session_read_repository():
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
    s2 = SessionRecord(
        session_id="s2",
        started_at=now,
        status="active",
        environment_os="win32",
        environment_python="3.13",
        profile_name="standard",
    )

    driver.begin_transaction()
    driver.write_batch([s1, s2])
    driver.commit()

    from traceforge.query.repositories.session_repository import SessionRepository as ReadSessionRepo

    read_repo = ReadSessionRepo(conn)

    assert read_repo.exists("s1")
    assert not read_repo.exists("missing")

    s1_fetched = read_repo.get_by_id("s1")
    assert s1_fetched.session_id == "s1"
    assert s1_fetched.status == "completed"

    with pytest.raises(NotFoundError):
        read_repo.get_by_id("non_existent")

    sessions_all = read_repo.list()
    assert len(sessions_all) == 2

    # Filtering
    filtered = read_repo.list(filter=QueryFilter(status="completed"))
    assert len(filtered) == 1
    assert filtered[0].session_id == "s1"

    # Pagination
    paginated = read_repo.list(pagination=Pagination(limit=1, offset=0))
    assert len(paginated) == 1

    driver.close()
