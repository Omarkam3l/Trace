"""TraceForge Plugin SDK (Phase 4)."""

from traceforge.plugins.base import Plugin
from traceforge.plugins.context import PluginContext
from traceforge.plugins.interfaces import TraceForgePluginInterface
from traceforge.plugins.loader import PluginLoader
from traceforge.plugins.manager import PluginManager
from traceforge.plugins.metadata import PluginMetadata
from traceforge.plugins.patching import patch_attribute, restore_attribute
from traceforge.plugins.registry import PluginRegistry

__all__ = [
    "Plugin",
    "PluginContext",
    "PluginLoader",
    "PluginManager",
    "PluginMetadata",
    "PluginRegistry",
    "TraceForgePluginInterface",
    "patch_attribute",
    "restore_attribute",
]
