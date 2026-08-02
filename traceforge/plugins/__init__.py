"""TraceForge Plugin SDK (Phase 4)."""

from traceforge.plugins.base import Plugin
from traceforge.plugins.context import PluginContext
from traceforge.plugins.manager import PluginManager
from traceforge.plugins.metadata import PluginMetadata
from traceforge.plugins.patching import patch_attribute, restore_attribute
from traceforge.plugins.registry import PluginRegistry

__all__ = [
    "Plugin",
    "PluginContext",
    "PluginManager",
    "PluginMetadata",
    "PluginRegistry",
    "patch_attribute",
    "restore_attribute",
]
