"""PythonRuntimePlugin: automatic CPython runtime observation plugin."""

from __future__ import annotations

import threading

from traceforge.plugins.base import Plugin
from traceforge.plugins.context import PluginContext
from traceforge.plugins.metadata import PluginMetadata
from traceforge.runtime.backends.base import InstrumentationBackend
from traceforge.runtime.backends.selector import BackendSelector
from traceforge.runtime.config import RuntimeConfig
from traceforge.runtime.filter import RuntimeFilter


class PythonRuntimePlugin(Plugin):
    """Automatic CPython execution observation plugin."""

    def __init__(self, config: RuntimeConfig | None = None) -> None:
        super().__init__()
        self._config = config or RuntimeConfig()
        self._backend: InstrumentationBackend | None = None
        self._lock = threading.RLock()

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="python_runtime",
            version="1.0.0",
            description="Automatic CPython execution observation plugin",
            author="TraceForge Team",
            supported_versions=[">=3.10"],
            capabilities={"tracing", "runtime_observation", "context_propagation"},
        )

    @property
    def config(self) -> RuntimeConfig:
        return self._config

    @property
    def active_backend(self) -> InstrumentationBackend | None:
        return self._backend

    def enable(self, context: PluginContext) -> None:
        with self._lock:
            if self.is_enabled:
                return

            filter_evaluator = RuntimeFilter(
                include=self._config.include,
                exclude=self._config.exclude,
            )

            self._backend = BackendSelector.select_backend(
                config=self._config,
                emit_callback=context.emit,
                filter_evaluator=filter_evaluator,
            )

            self._backend.start()

    def disable(self) -> None:
        with self._lock:
            if not self.is_enabled or self._backend is None:
                return

            try:
                self._backend.stop()
            finally:
                self._backend = None
