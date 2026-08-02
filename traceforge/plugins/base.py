"""Plugin Abstract Base Class (ABC)."""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from traceforge.plugins.context import PluginContext
    from traceforge.plugins.metadata import PluginMetadata


class Plugin(abc.ABC):
    """Abstract contract for all TraceForge plugins."""

    def __init__(self) -> None:
        self._enabled: bool = False
        self._context: PluginContext | None = None

    @property
    @abc.abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return immutable plugin metadata."""
        pass

    @property
    def is_enabled(self) -> bool:
        """Return True if the plugin is currently enabled."""
        return self._enabled

    @abc.abstractmethod
    def enable(self, context: PluginContext) -> None:
        """Enable the plugin with the provided PluginContext."""
        pass

    @abc.abstractmethod
    def disable(self) -> None:
        """Disable the plugin and restore original runtime state."""
        pass

    def _set_enabled(self, enabled: bool, context: PluginContext | None = None) -> None:
        self._enabled = enabled
        self._context = context
