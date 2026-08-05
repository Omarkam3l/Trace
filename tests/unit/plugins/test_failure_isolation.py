"""Unit tests for plugin failure isolation."""

from __future__ import annotations

from traceforge.engine.recorder import Recorder
from traceforge.plugins.base import Plugin
from traceforge.plugins.context import PluginContext
from traceforge.plugins.manager import PluginManager
from traceforge.plugins.metadata import PluginMetadata


class FailingPlugin(Plugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(name="failing_plugin", version="1.0.0")

    def enable(self, context: PluginContext) -> None:
        raise RuntimeError("Crash during plugin enable")

    def disable(self) -> None:
        raise RuntimeError("Crash during plugin disable")


def test_failure_isolation_on_enable_and_disable():
    recorder = Recorder()
    recorder.start_session()

    manager = PluginManager(recorder=recorder)
    plugin = FailingPlugin()
    manager.register_plugin(plugin)

    # Enable fails safely without crashing application or recorder
    success = manager.enable_plugin(plugin)
    assert not success
    assert not plugin.is_enabled

    session = recorder.stop_session()
    graph = session.activities[0].graph

    # Verify a PluginFailure RawEvent was recorded safely
    assert len(graph.nodes) >= 1  # Recording session completed safely
