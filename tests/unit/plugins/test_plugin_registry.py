"""Unit tests for PluginRegistry."""

from __future__ import annotations

import pytest

from traceforge.plugins.base import Plugin
from traceforge.plugins.context import PluginContext
from traceforge.plugins.metadata import PluginMetadata
from traceforge.plugins.registry import PluginRegistry


class MockPlugin(Plugin):
    def __init__(self, name: str) -> None:
        super().__init__()
        self._name = name

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(name=self._name, version="1.0.0")

    def enable(self, context: PluginContext) -> None:
        pass

    def disable(self) -> None:
        pass


def test_registry_registration_and_lookup():
    registry = PluginRegistry()
    p1 = MockPlugin("plugin_a")
    p2 = MockPlugin("plugin_b")

    registry.register(p1)
    registry.register(p2)

    assert registry.get("plugin_a") is p1
    assert registry.get("plugin_b") is p2
    assert len(registry.list_all()) == 2

    # Duplicate registration raises ValueError
    with pytest.raises(ValueError):
        registry.register(MockPlugin("plugin_a"))

    registry.unregister("plugin_a")
    assert registry.get("plugin_a") is None
    assert len(registry.list_all()) == 1
