"""Unit tests for dynamic PluginLoader."""

from __future__ import annotations

import os
import tempfile

from traceforge.plugins.loader import PluginLoader


def test_plugin_loader_discover_empty():
    loader = PluginLoader()
    plugins = loader.discover_directory("non_existent_dir")
    assert len(plugins) == 0


def test_plugin_loader_discover_valid_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        plugin_file = os.path.join(tmpdir, "my_plugin.py")
        with open(plugin_file, "w", encoding="utf-8") as f:
            f.write("""
from traceforge.plugins.interfaces import TraceForgePluginInterface
from traceforge.plugins.metadata import PluginMetadata

class SamplePlugin(TraceForgePluginInterface):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(name="sample", version="1.0.0")
    def initialize(self, context=None) -> None:
        pass
    def shutdown(self) -> None:
        pass
""")
        loader = PluginLoader()
        loaded = loader.discover_directory(tmpdir)
        assert len(loaded) == 1
        assert loaded[0].metadata().name == "sample"
