"""Unit tests for SessionRepository and RawEventRepository append-only operation."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from traceforge.domain.activity import Activity
from traceforge.domain.enums import ActivityStatus, NodeStatus, NodeType, SessionStatus
from traceforge.domain.environment import Environment
from traceforge.domain.graph import ExecutionGraph
from traceforge.domain.node import ExecutionNode
from traceforge.domain.profile import RecordingProfile
from traceforge.domain.session import RecordingSession
from traceforge.engine.raw_event import RawEvent
from traceforge.storage.drivers.base import StorageDriver
from traceforge.storage.records.raw_event_record import RawEventRecord
from traceforge.storage.records.session_record import SessionRecord
from traceforge.storage.repositories.raw_event_repository import RawEventRepository
from traceforge.storage.repositories.session_repository import SessionRepository


class InMemoryTestDriver(StorageDriver):
    def __init__(self) -> None:
        self.written_records: list[Any] = []

    def begin_transaction(self) -> None:
        pass

    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass

    def write_batch(self, records: list[Any]) -> None:
        self.written_records.extend(records)

    def flush(self) -> None:
        pass

    def close(self) -> None:
        pass


def test_session_repository_append_only():
    driver = InMemoryTestDriver()
    repo = SessionRepository(driver=driver)

    now = datetime.now(timezone.utc)
    env = Environment(os="win32", python_version="3.13")
    prof = RecordingProfile(name="standard")

    node = ExecutionNode(
        node_id="n1",
        graph_id="g1",
        type=NodeType.FUNCTION_CALL,
        name="calculate",
        started_at=now,
        status=NodeStatus.COMPLETED,
    )
    graph = ExecutionGraph(graph_id="g1", activity_id="act1", nodes={"n1": node}, relationships=[])
    activity = Activity(activity_id="act1", session_id="sess1", name="Task", started_at=now, status=ActivityStatus.COMPLETED, graph=graph)
    session = RecordingSession(session_id="sess1", started_at=now, status=SessionStatus.COMPLETED, environment=env, profile=prof, activities=[activity])

    s_rec = repo.append_session(session)
    assert isinstance(s_rec, SessionRecord)

    repo.append_activity(activity)
    repo.append_graph(graph)
    repo.append_node(node)

    assert len(driver.written_records) == 4

    # Verify repositories do NOT expose update(), delete(), or replace() methods
    assert not hasattr(repo, "update")
    assert not hasattr(repo, "delete")
    assert not hasattr(repo, "replace")


def test_raw_event_repository_append_only():
    driver = InMemoryTestDriver()
    repo = RawEventRepository(driver=driver)

    now = datetime.now(timezone.utc)
    evt = RawEvent(event_id="e1", timestamp=now, sequence=1, type="HTTPRequest")

    records = repo.append_raw_events([evt])
    assert len(records) == 1
    assert isinstance(records[0], RawEventRecord)
    assert len(driver.written_records) == 1

    assert not hasattr(repo, "update")
    assert not hasattr(repo, "delete")
    assert not hasattr(repo, "replace")
