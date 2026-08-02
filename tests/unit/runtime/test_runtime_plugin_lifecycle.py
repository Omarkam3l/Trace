"""Unit tests for PythonRuntimePlugin lifecycle, execution observation, and event emission."""

from __future__ import annotations

from traceforge.engine.recorder import Recorder
from traceforge.plugins.manager import PluginManager
from traceforge.runtime.config import RuntimeConfig
from traceforge.runtime.enums import BackendType
from traceforge.runtime.plugin import PythonRuntimePlugin


def test_python_runtime_plugin_lifecycle_and_observation():
    recorder = Recorder()
    recorder.start_session()

    cfg = RuntimeConfig(backend=BackendType.SETPROFILE, include=["test_runtime_plugin_lifecycle.*"])
    plugin = PythonRuntimePlugin(config=cfg)

    manager = PluginManager(recorder=recorder)
    manager.register_plugin(plugin)

    assert not plugin.is_enabled
    manager.enable_plugin(plugin)
    assert plugin.is_enabled
    assert plugin.active_backend is not None
    assert plugin.active_backend.is_active

    # Executed function observed by plugin
    def sample_monitored_function(a: int, b: int) -> int:
        return a + b

    result = sample_monitored_function(10, 20)
    assert result == 30

    manager.disable_plugin(plugin)
    assert not plugin.is_enabled
    assert plugin.active_backend is None

    session = recorder.stop_session()
    assert len(session.activities) >= 1
