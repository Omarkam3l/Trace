"""Regression tests: PluginContext and PluginManager must fail fast, with a

clear message, when constructed with the public traceforge.Recorder instead
of the internal traceforge.engine.recorder.Recorder they actually need.

Before this fix:
- PluginContext(recorder=public_recorder).emit(...) raised a bare
  AttributeError three calls deep, with no indication of the two Recorder
  classes existing.
- PluginManager(recorder=public_recorder) didn't fail at all -- the mistake
  only surfaced later as *silently missing* plugin-failure diagnostics,
  since _emit_plugin_failure swallows exceptions from recorder.emit(...) by
  design (failure-isolation guarantee).
"""

from __future__ import annotations

import pytest

import traceforge
from traceforge.engine.recorder import Recorder as EngineRecorder
from traceforge.plugins.context import PluginContext
from traceforge.plugins.manager import PluginManager


def test_plugin_context_rejects_public_recorder():
    public_recorder = traceforge.Recorder(traceforge.MemoryStorage())
    with pytest.raises(TypeError, match="emit"):
        PluginContext(recorder=public_recorder)


def test_plugin_manager_rejects_public_recorder():
    public_recorder = traceforge.Recorder(traceforge.MemoryStorage())
    with pytest.raises(TypeError, match="emit"):
        PluginManager(recorder=public_recorder)


def test_plugin_context_accepts_engine_recorder():
    engine_recorder = EngineRecorder()
    # Should not raise.
    ctx = PluginContext(recorder=engine_recorder)
    assert ctx is not None


def test_plugin_manager_accepts_engine_recorder():
    engine_recorder = EngineRecorder()
    # Should not raise.
    manager = PluginManager(recorder=engine_recorder)
    assert manager is not None


def test_error_message_names_the_wrong_class():
    """The error should be actionable, not just 'no attribute emit'."""
    public_recorder = traceforge.Recorder(traceforge.MemoryStorage())
    with pytest.raises(TypeError) as exc_info:
        PluginContext(recorder=public_recorder)
    message = str(exc_info.value)
    assert "traceforge.engine.recorder" in message
    assert "Recorder" in message
