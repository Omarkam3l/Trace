"""Unit tests for concurrent plugin execution and event emission."""

from __future__ import annotations

import concurrent.futures
from datetime import datetime, timezone

from traceforge.engine.raw_event import RawEvent
from traceforge.engine.recorder import Recorder
from traceforge.plugins.base import Plugin
from traceforge.plugins.context import PluginContext
from traceforge.plugins.manager import PluginManager
from traceforge.plugins.metadata import PluginMetadata


class WorkerPlugin(Plugin):
    def __init__(self, worker_id: int) -> None:
        super().__init__()
        self.worker_id = worker_id

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(name=f"worker_plugin_{self.worker_id}", version="1.0.0")

    def enable(self, context: PluginContext) -> None:
        pass

    def disable(self) -> None:
        pass

    def emit_events(self, count: int) -> None:
        if self.is_enabled and self._context:
            t0 = datetime.now(timezone.utc)
            for i in range(count):
                evt = RawEvent(
                    event_id=f"evt_w{self.worker_id}_{i}",
                    timestamp=t0,
                    sequence=i,
                    type="FunctionEntered",
                    payload={"worker": self.worker_id, "step": i},
                )
                self._context.emit(evt)


def test_concurrent_plugin_event_emissions():
    recorder = Recorder()
    recorder.start_session()

    manager = PluginManager(recorder=recorder)
    plugins = [WorkerPlugin(i) for i in range(5)]

    for p in plugins:
        manager.register_plugin(p)
        manager.enable_plugin(p)

    def run_worker(plugin: WorkerPlugin):
        plugin.emit_events(10)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(run_worker, p) for p in plugins]
        concurrent.futures.wait(futures)

    session = recorder.stop_session()
    total_nodes = sum(len(act.graph.nodes) for act in session.activities)
    assert total_nodes == 50  # 5 plugins * 10 events
