"""Unit tests for ExecutionConsumer registration, unregistration, and enable/disable states."""

from __future__ import annotations

import pytest

from traceforge.domain.activity import Activity
from traceforge.domain.graph import ExecutionGraph
from traceforge.domain.session import RecordingSession
from traceforge.pipeline.consumer import ExecutionConsumer
from traceforge.pipeline.exceptions import ConsumerRegistrationError
from traceforge.pipeline.pipeline import ExecutionPipeline


class MockConsumer(ExecutionConsumer):
    def __init__(self, name: str, consumer_id: str | None = None) -> None:
        super().__init__(name=name, consumer_id=consumer_id)
        self.sessions: list[RecordingSession] = []
        self.activities: list[Activity] = []
        self.graphs: list[ExecutionGraph] = []

    def on_session_completed(self, session: RecordingSession) -> None:
        self.sessions.append(session)

    def on_activity_completed(self, activity: Activity) -> None:
        self.activities.append(activity)

    def on_graph_completed(self, graph: ExecutionGraph) -> None:
        self.graphs.append(graph)


def test_consumer_registration_and_unregistration():
    pipeline = ExecutionPipeline()
    c1 = MockConsumer("consumer_1")
    c2 = MockConsumer("consumer_2")

    pipeline.register_consumer(c1)
    pipeline.register_consumer(c2)

    stats = pipeline.get_statistics()
    assert stats.active_consumers_count == 2

    # Duplicate registration raises ConsumerRegistrationError
    with pytest.raises(ConsumerRegistrationError):
        pipeline.register_consumer(MockConsumer("duplicate", consumer_id="consumer_1"))

    # Unregister consumer
    unregistered = pipeline.unregister_consumer("consumer_1")
    assert unregistered is c1
    assert pipeline.get_statistics().active_consumers_count == 1


def test_consumer_enable_disable_states():
    pipeline = ExecutionPipeline()
    c1 = MockConsumer("consumer_1")
    pipeline.register_consumer(c1)

    assert c1.is_enabled
    assert pipeline.get_statistics().active_consumers_count == 1

    pipeline.disable_consumer("consumer_1")
    assert not c1.is_enabled
    assert pipeline.get_statistics().active_consumers_count == 0

    pipeline.enable_consumer("consumer_1")
    assert c1.is_enabled
    assert pipeline.get_statistics().active_consumers_count == 1
