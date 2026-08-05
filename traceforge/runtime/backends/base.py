"""InstrumentationBackend Abstract Base Class."""

from __future__ import annotations

import abc
from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from traceforge.engine.raw_event import RawEvent
    from traceforge.runtime.config import RuntimeConfig
    from traceforge.runtime.enums import BackendType
    from traceforge.runtime.filter import RuntimeFilter


class InstrumentationBackend(abc.ABC):
    """Abstract interface for CPython instrumentation backends."""

    def __init__(
        self,
        emit_callback: Callable[[RawEvent], None],
        filter_evaluator: RuntimeFilter,
        config: RuntimeConfig,
    ) -> None:
        self._emit_callback = emit_callback
        self._filter = filter_evaluator
        self._config = config
        self._active: bool = False

    @property
    def is_active(self) -> bool:
        return self._active

    @property
    @abc.abstractmethod
    def backend_type(self) -> BackendType:
        pass

    @abc.abstractmethod
    def start(self) -> None:
        """Start runtime observation."""
        pass

    @abc.abstractmethod
    def stop(self) -> None:
        """Stop runtime observation."""
        pass
