"""ExecutionConsumer Abstract Base Class."""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from traceforge.domain.activity import Activity
    from traceforge.domain.graph import ExecutionGraph
    from traceforge.domain.session import RecordingSession


class ExecutionConsumer(abc.ABC):
    """Abstract Base Class for decoupled execution pipeline consumers."""

    def __init__(self, name: str, consumer_id: str | None = None) -> None:
        self._name = name
        self._consumer_id = consumer_id or name
        self._enabled: bool = True

    @property
    def consumer_id(self) -> str:
        return self._consumer_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def enable(self) -> None:
        self._enabled = True

    def disable(self) -> None:
        self._enabled = False

    @abc.abstractmethod
    def on_session_completed(self, session: RecordingSession) -> None:
        """Invoked when a RecordingSession completes."""

    @abc.abstractmethod
    def on_activity_completed(self, activity: Activity) -> None:
        """Invoked when an Activity completes."""

    @abc.abstractmethod
    def on_graph_completed(self, graph: ExecutionGraph) -> None:
        """Invoked when an ExecutionGraph completes."""
