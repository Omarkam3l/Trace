"""Unit tests for PipelineDispatcher deterministic order delivery."""

from __future__ import annotations

from datetime import datetime, timezone

from traceforge.domain.activity import Activity
from traceforge.domain.enums import ActivityStatus, NodeStatus, NodeType, SessionStatus
from traceforge.domain.environment import Environment
from traceforge.domain.graph import ExecutionGraph
from traceforge.domain.node import ExecutionNode
from traceforge.domain.profile import RecordingProfile
from traceforge.domain.session import RecordingSession
from traceforge.pipeline.consumer import ExecutionConsumer
from traceforge.pipeline.pipeline import ExecutionPipeline


class OrderedCollectorConsumer(ExecutionConsumer):
    def __init__(self, name: str, global_log: list[str]) -> None:
        super().__init__(name=name)
        self.global_log = global_log

    def on_session_completed(self, session: RecordingSession) -> None:
        self.global_log.append(f"{self.name}:session:{session.id}")

    def on_activity_completed(self, activity: Activity) -> None:
        self.global_log.append(f"{self.name}:activity:{activity.id}")

    def on_graph_completed(self, graph: ExecutionGraph) -> None:
        self.global_log.append(f"{self.name}:graph:{graph.id}")


def test_deterministic_dispatch_ordering():
    dispatch_log: list[str] = []
    pipeline = ExecutionPipeline()

    c1 = OrderedCollectorConsumer("c1", dispatch_log)
    c2 = OrderedCollectorConsumer("c2", dispatch_log)
    c3 = OrderedCollectorConsumer("c3", dispatch_log)

    pipeline.register_consumer(c1)
    pipeline.register_consumer(c2)
    pipeline.register_consumer(c3)

    now = datetime.now(timezone.utc)
    node = ExecutionNode(
        node_id="n1",
        graph_id="g1",
        type=NodeType.FUNCTION_CALL,
        name="test_fn",
        started_at=now,
        status=NodeStatus.COMPLETED,
    )

    graph = ExecutionGraph(graph_id="g1", activity_id="act1", nodes={"n1": node}, relationships=[])
    activity = Activity(activity_id="act1", session_id="sess1", name="Act1", started_at=now, status=ActivityStatus.COMPLETED, graph=graph)
    session = RecordingSession(session_id="sess1", started_at=now, status=SessionStatus.COMPLETED, environment=Environment(os="win32", python_version="3.13"), profile=RecordingProfile(), activities=[activity])

    pipeline.publish_graph(graph)
    pipeline.publish_activity(activity)
    pipeline.publish_session(session)

    expected = [
        "c1:graph:g1", "c2:graph:g1", "c3:graph:g1",
        "c1:activity:act1", "c2:activity:act1", "c3:activity:act1",
        "c1:session:sess1", "c2:session:sess1", "c3:session:sess1",
    ]
    assert dispatch_log == expected
