"""Unit tests for multi-threaded concurrent VisualizationEngine operations."""

from __future__ import annotations

import concurrent.futures
from datetime import datetime, timezone

from traceforge.replay.session import ReplaySession
from traceforge.storage.records import NodeRecord, SessionRecord
from traceforge.visualization.engine import VisualizationEngine


def test_concurrent_visualization_engine_transformations():
    now = datetime.now(timezone.utc)
    sess_rec = SessionRecord(session_id="s1", started_at=now, status="completed", environment_os="win32", environment_python="3.13", profile_name="standard")
    n1 = NodeRecord(node_id="n1", graph_id="g1", type="function", name="main", started_at=now, status="completed")

    session = ReplaySession(session=sess_rec, nodes=[n1])
    engine = VisualizationEngine()

    def worker_vis(worker_id: int):
        vm = engine.to_graph_model(session)
        assert len(vm.nodes) == 1

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(worker_vis, i) for i in range(10)]
        concurrent.futures.wait(futures)
