"""RecordingContextManager for managing nested thread-local and asyncio contexts."""

from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ScopeFrame:
    context_id: str
    parent_node_id: str | None = None


@dataclass(frozen=True, slots=True)
class ContextStack:
    frames: tuple[ScopeFrame, ...] = field(default_factory=tuple)

    @property
    def current(self) -> ScopeFrame | None:
        return self.frames[-1] if self.frames else None

    def push(self, frame: ScopeFrame) -> ContextStack:
        return ContextStack(frames=(*self.frames, frame))

    def pop(self) -> ContextStack:
        return ContextStack(frames=self.frames[:-1])


_EMPTY_STACK = ContextStack()
_current_recording_context: ContextVar[ContextStack] = ContextVar("traceforge_recording_context", default=_EMPTY_STACK)


class RecordingContextScope:
    """Context manager scope representing a nested recording context."""

    def __init__(self, manager: RecordingContextManager, context_id: str, parent_node_id: str | None) -> None:
        self._manager = manager
        self._context_id = context_id
        self._parent_node_id = parent_node_id
        self._token: Token[ContextStack] | None = None

    @property
    def context_id(self) -> str:
        return self._context_id

    def __enter__(self) -> RecordingContextScope:
        stack = _current_recording_context.get()
        frame = ScopeFrame(context_id=self._context_id, parent_node_id=self._parent_node_id)
        self._token = _current_recording_context.set(stack.push(frame))
        return self

    def __exit__(self, *exc_info: object) -> None:
        if self._token is not None:
            try:
                _current_recording_context.reset(self._token)
            except RuntimeError:
                pass
            self._token = None

    async def __aenter__(self) -> RecordingContextScope:
        return self.__enter__()

    async def __aexit__(self, *exc_info: object) -> None:
        self.__exit__(*exc_info)


class RecordingContextManager:
    """Manages thread-isolated and task-isolated execution context stacks."""

    def push_scope(self, context_id: str, parent_node_id: str | None = None) -> RecordingContextScope:
        return RecordingContextScope(self, context_id, parent_node_id)

    @staticmethod
    def get_current_context_id() -> str | None:
        curr = _current_recording_context.get().current
        return curr.context_id if curr else None

    @staticmethod
    def get_current_parent_node_id() -> str | None:
        curr = _current_recording_context.get().current
        return curr.parent_node_id if curr else None

    @staticmethod
    def clear() -> None:
        _current_recording_context.set(_EMPTY_STACK)
