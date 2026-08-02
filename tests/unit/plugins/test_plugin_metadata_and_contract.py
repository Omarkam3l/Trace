"""Unit tests for PluginMetadata and Plugin ABC contract."""

from __future__ import annotations

import pytest

from traceforge.plugins.base import Plugin
from traceforge.plugins.context import PluginContext
from traceforge.plugins.metadata import PluginMetadata


class DummyPlugin(Plugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="dummy_plugin",
            version="1.0.0",
            description="Dummy test plugin",
            author="TraceForge Team",
            supported_versions=["1.0.0"],
            capabilities={"tracing"},
        )

    def enable(self, context: PluginContext) -> None:
        pass

    def disable(self) -> None:
        pass


def test_plugin_metadata_immutability():
    meta = PluginMetadata(name="test", version="0.1.0")
    assert meta.name == "test"
    assert meta.version == "0.1.0"

    with pytest.raises(Exception):
        meta.name = "mutated"  # Immutability enforcement


def test_dummy_plugin_instantiation():
    plugin = DummyPlugin()
    assert plugin.metadata.name == "dummy_plugin"
    assert not plugin.is_enabled
