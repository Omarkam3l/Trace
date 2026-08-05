"""Dynamic plugin loader for discovering and instantiating plugins."""

from __future__ import annotations

import importlib
import importlib.util
import os
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from traceforge.plugins.interfaces import TraceForgePluginInterface


class PluginLoader:
    """Discovers and dynamically loads plugin classes from files and directories."""

    def discover_directory(self, plugins_dir: str) -> list[TraceForgePluginInterface]:
        """Scan directory for python plugin files and load plugin instances."""
        plugins: list[TraceForgePluginInterface] = []
        if not os.path.exists(plugins_dir):
            return plugins

        for filename in os.listdir(plugins_dir):
            if filename.endswith(".py") and not filename.startswith("_"):
                filepath = os.path.join(plugins_dir, filename)
                mod_name = f"traceforge_plugin_{os.path.splitext(filename)[0]}"
                spec = importlib.util.spec_from_file_location(mod_name, filepath)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[mod_name] = module
                    spec.loader.exec_module(module)
                    for attr in dir(module):
                        val = getattr(module, attr)
                        if isinstance(val, type) and hasattr(val, "metadata") and hasattr(val, "initialize"):
                            try:
                                inst = val()
                                plugins.append(inst)
                            except Exception:
                                pass
        return plugins
