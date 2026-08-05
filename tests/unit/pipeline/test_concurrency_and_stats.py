"""Unit tests for multi-threaded pipeline publishing, statistics, and shutdown."""

from __future__ import annotations

import concurrent.futures
from datetime import UTC, datetime

from traceforge.domain.activity import Activity
from traceforge.domain.enums import SessionStatus
from traceforge.domain.environment import Environment
from traceforge.domain.graph import ExecutionGraph
from traceforge.domain.profile import RecordingProfile
from traceforge.domain.session import RecordingSession
from traceforge.pipeline.consumer import ExecutionConsumer
from traceforge.pipeline.pipeline import ExecutionPipeline


class ThreadStatsConsumer(ExecutionConsumer):
    def __init__(self, name: str) -> None:
        super().__init__(name=name)
        self.count = 0

    def on_session_completed(self, session: RecordingSession) -> None:
        self.count += 1

    def on_activity_completed(self, activity: Activity) -> None:
        pass

    def on_graph_completed(self, graph: ExecutionGraph) -> None:
        pass


def test_concurrent_pipeline_publication_and_stats():
    pipeline = ExecutionPipeline()
    consumer = ThreadStatsConsumer("thread_consumer")
    pipeline.register_consumer(consumer)

    now = datetime.now(UTC)
    session = RecordingSession(
        session_id="sess_thread",
        started_at=now,
        status=SessionStatus.COMPLETED,
        environment=Environment(os="win32", python_version="3.13"),
        profile=RecordingProfile(),
        activities=[],
    )

    def publish_worker(worker_id: int):
        for _ in range(10):
            pipeline.publish_session(session)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(publish_worker, i) for i in range(5)]
        concurrent.futures.wait(futures)

    stats = pipeline.get_statistics()
    assert stats.sessions_dispatched == 50

    pipeline.shutdown()
    assert pipeline.is_shutdown
    assert pipeline.get_statistics().active_consumers_count == 0
