"""Plugin lifecycle interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from traceforge.plugins.metadata import PluginMetadata


class TraceForgePluginInterface(ABC):
    """Abstract interface for external TraceForge plugins."""

    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata descriptor."""

    @abstractmethod
    def initialize(self, context: Any = None) -> None:
        """Initialize the plugin."""

    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the plugin cleanly."""
