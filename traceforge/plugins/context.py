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
