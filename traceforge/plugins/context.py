"""PluginContext for providing isolated runtime tools to plugins."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from traceforge.engine.raw_event import RawEvent
    from traceforge.engine.recorder import Recorder


class PluginContext:
    """Read-only gateway providing event emission and config utilities to plugins."""

    def __init__(
        self,
        recorder: Recorder,
        config: dict[str, Any] | None = None,
        logger: Any = None,
    ) -> None:
        if not hasattr(recorder, "emit"):
            # traceforge has two unrelated classes both named "Recorder":
            #   - traceforge.Recorder (public, documented in the README) --
            #     hooks into Tracer via on_span_start/on_span_end, has no
            #     .emit(). This is what most users reach for.
            #   - traceforge.engine.recorder.Recorder (internal, used by the
            #     plugin system) -- has .emit(raw_event) and is what
            #     PluginContext actually needs.
            # Passing the public one here used to fail three calls later,
            # deep inside a plugin, with a bare
            # "AttributeError: 'Recorder' object has no attribute 'emit'".
            # Fail here instead, with enough context to fix it immediately.
            raise TypeError(
                f"PluginContext requires a recorder with an .emit() method, "
                f"but got {type(recorder).__module__}.{type(recorder).__qualname__}, "
                "which has none. If you constructed this with `traceforge.Recorder(...)`, "
                "that is the public span-recording Recorder and is not compatible with "
                "the plugin system. Use `traceforge.engine.recorder.Recorder` instead "
                "when wiring up PluginContext/PluginManager."
            )
        self._recorder = recorder
        self._config = dict(config or {})
        self._logger = logger

    @property
    def config(self) -> dict[str, Any]:
        return dict(self._config)

    @property
    def logger(self) -> Any:
        return self._logger

    def emit(self, raw_event: RawEvent) -> None:
        """Emit a RawEvent to the underlying Recorder."""
        self._recorder.emit(raw_event)
