"""PluginRegistry: catalog for plugin registration and lookup."""

from __future__ import annotations

import threading

from traceforge.plugins.base import Plugin


class PluginRegistry:
    """Lightweight thread-safe catalog storing registered plugins by name."""

    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}
        self._lock = threading.RLock()

    def register(self, plugin: Plugin) -> None:
        with self._lock:
            name = plugin.metadata.name
            if name in self._plugins:
                raise ValueError(f"Plugin with name {name!r} is already registered")
            self._plugins[name] = plugin

    def unregister(self, name: str) -> Plugin | None:
        with self._lock:
            return self._plugins.pop(name, None)

    def get(self, name: str) -> Plugin | None:
        with self._lock:
            return self._plugins.get(name)

    def list_all(self) -> list[Plugin]:
        with self._lock:
            return list(self._plugins.values())

    def clear(self) -> None:
        with self._lock:
            self._plugins.clear()
