"""PluginManager: orchestrates plugin lifecycles and enforces failure isolation."""

from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone
from typing import Any

from traceforge.engine.raw_event import RawEvent
from traceforge.engine.recorder import Recorder
from traceforge.plugins.base import Plugin
from traceforge.plugins.context import PluginContext
from traceforge.plugins.registry import PluginRegistry


class PluginManager:
    """Orchestrates plugin registration, lifecycle, and failure isolation."""

    def __init__(self, recorder: Recorder) -> None:
        self._recorder = recorder
        self._registry = PluginRegistry()
        self._lock = threading.RLock()

    @property
    def registry(self) -> PluginRegistry:
        return self._registry

    def register_plugin(self, plugin: Plugin) -> None:
        """Register a plugin with the PluginManager."""
        self._registry.register(plugin)

    def unregister_plugin(self, name: str) -> None:
        """Unregister and disable a plugin."""
        with self._lock:
            plugin = self._registry.get(name)
            if plugin:
                if plugin.is_enabled:
                    self.disable_plugin(plugin)
                self._registry.unregister(name)

    def enable_plugin(self, name_or_plugin: str | Plugin, config: dict[str, Any] | None = None) -> bool:
        """Enable a registered plugin safely under failure isolation."""
        with self._lock:
            plugin = (
                self._registry.get(name_or_plugin)
                if isinstance(name_or_plugin, str)
                else name_or_plugin
            )
            if plugin is None:
                raise ValueError(f"Plugin {name_or_plugin!r} not found in registry")

            if plugin.is_enabled:
                return True

            context = PluginContext(recorder=self._recorder, config=config)

            try:
                plugin.enable(context)
                plugin._set_enabled(True, context)
                return True
            except Exception as exc:
                self._emit_plugin_failure(plugin.metadata.name, "enable", exc)
                return False

    def disable_plugin(self, name_or_plugin: str | Plugin) -> bool:
        """Disable a registered plugin safely under failure isolation."""
        with self._lock:
            plugin = (
                self._registry.get(name_or_plugin)
                if isinstance(name_or_plugin, str)
                else name_or_plugin
            )
            if plugin is None or not plugin.is_enabled:
                return False

            try:
                plugin.disable()
                plugin._set_enabled(False, None)
                return True
            except Exception as exc:
                plugin._set_enabled(False, None)
                self._emit_plugin_failure(plugin.metadata.name, "disable", exc)
                return False

    def enable_all(self) -> None:
        """Enable all registered plugins."""
        with self._lock:
            for plugin in self._registry.list_all():
                self.enable_plugin(plugin)

    def disable_all(self) -> None:
        """Disable all enabled plugins."""
        with self._lock:
            for plugin in self._registry.list_all():
                if plugin.is_enabled:
                    self.disable_plugin(plugin)

    def _emit_plugin_failure(self, plugin_name: str, phase: str, exception: Exception) -> None:
        """Emit a PluginFailure RawEvent to record isolated plugin failures."""
        try:
            event = RawEvent(
                event_id=f"fail_{uuid.uuid4().hex[:16]}",
                timestamp=datetime.now(timezone.utc),
                type="PluginFailure",
                payload={
                    "plugin_name": plugin_name,
                    "phase": phase,
                    "error_message": str(exception),
                    "exception_type": type(exception).__name__,
                },
            )
            self._recorder.emit(event)
        except Exception:
            pass  # Failure emission isolation guarantees no unhandled crash
