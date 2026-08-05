"""Unit tests for PluginManager lifecycle management and event emission."""

from __future__ import annotations

from datetime import UTC, datetime

from traceforge.engine.raw_event import RawEvent
from traceforge.engine.recorder import Recorder
from traceforge.plugins.base import Plugin
from traceforge.plugins.context import PluginContext
from traceforge.plugins.manager import PluginManager
from traceforge.plugins.metadata import PluginMetadata


class EmissionTestPlugin(Plugin):
    def __init__(self) -> None:
        super().__init__()
        self.enabled_count = 0
        self.disabled_count = 0

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(name="emitter_plugin", version="1.0.0")

    def enable(self, context: PluginContext) -> None:
        self.enabled_count += 1

    def disable(self) -> None:
        self.disabled_count += 1

    def emit_custom_event(self) -> None:
        if self.is_enabled and self._context:
            evt = RawEvent(
                event_id="evt_plugin_1",
                timestamp=datetime.now(UTC),
                type="HTTPRequest",
                payload={"url": "https://api.traceforge.dev"},
            )
            self._context.emit(evt)


def test_plugin_manager_enable_disable_lifecycle():
    recorder = Recorder()
    recorder.start_session()

    manager = PluginManager(recorder=recorder)
    plugin = EmissionTestPlugin()
    manager.register_plugin(plugin)

    assert not plugin.is_enabled

    manager.enable_plugin("emitter_plugin")
    assert plugin.is_enabled
    assert plugin.enabled_count == 1

    # Emit event through plugin context
    plugin.emit_custom_event()

    manager.disable_plugin("emitter_plugin")
    assert not plugin.is_enabled
    assert plugin.disabled_count == 1

    session = recorder.stop_session()
    graph = session.activities[0].graph
    assert "evt_plugin_1" in graph.nodes
