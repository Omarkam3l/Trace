"""Unit tests for pipeline consumer failure isolation."""

from __future__ import annotations

from datetime import UTC, datetime

from traceforge.domain.activity import Activity
from traceforge.domain.enums import SessionStatus
from traceforge.domain.environment import Environment
from traceforge.domain.graph import ExecutionGraph
from traceforge.domain.profile import RecordingProfile
from traceforge.domain.session import RecordingSession
from traceforge.pipeline.consumer import ExecutionConsumer
from traceforge.pipeline.pipeline import ExecutionPipeline


class FailingConsumer(ExecutionConsumer):
    def on_session_completed(self, session: RecordingSession) -> None:
        raise RuntimeError("Consumer 1 crashed on session")

    def on_activity_completed(self, activity: Activity) -> None:
        raise RuntimeError("Consumer 1 crashed on activity")

    def on_graph_completed(self, graph: ExecutionGraph) -> None:
        raise RuntimeError("Consumer 1 crashed on graph")


class HealthyConsumer(ExecutionConsumer):
    def __init__(self, name: str) -> None:
        super().__init__(name=name)
        self.received_sessions: list[RecordingSession] = []

    def on_session_completed(self, session: RecordingSession) -> None:
        self.received_sessions.append(session)

    def on_activity_completed(self, activity: Activity) -> None:
        pass

    def on_graph_completed(self, graph: ExecutionGraph) -> None:
        pass


def test_failure_isolation_between_consumers():
    pipeline = ExecutionPipeline()

    failing = FailingConsumer("failing")
    healthy = HealthyConsumer("healthy")

    pipeline.register_consumer(failing)
    pipeline.register_consumer(healthy)

    now = datetime.now(UTC)
    session = RecordingSession(
        session_id="sess_fail_test",
        started_at=now,
        status=SessionStatus.COMPLETED,
        environment=Environment(os="linux", python_version="3.12"),
        profile=RecordingProfile(),
        activities=[],
    )

    # Publish session artifact - failing consumer error is isolated
    pipeline.publish_session(session)

    assert len(healthy.received_sessions) == 1
    assert healthy.received_sessions[0].id == "sess_fail_test"

    stats = pipeline.get_statistics()
    assert stats.failures_count == 1
    assert stats.sessions_dispatched == 1
