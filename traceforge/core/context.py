"""Execution context propagation.

Uses ``contextvars`` exclusively (never a plain module-level mutable
variable) so that context is correctly isolated per-thread *and* per-async-task,
without any manual passing of "current span" through call signatures.

This is the mechanism that gives TraceForge automatic parent-child linking:
whichever span is "current" when a new span starts becomes its parent.
"""

from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExecutionContext:
    """An immutable snapshot of "where we are" in the execution tree."""

    trace_id: str | None = None
    span_id: str | None = None
    parent_span_id: str | None = None
    correlation_id: str | None = None
    session_id: str | None = None

    def is_empty(self) -> bool:
        return self.trace_id is None and self.span_id is None


_EMPTY_CONTEXT = ExecutionContext()

_current_context: ContextVar[ExecutionContext] = ContextVar(
    "traceforge_current_context", default=_EMPTY_CONTEXT
)


class ContextManager:
    """Static accessor for the current :class:`ExecutionContext`.

    Grouped as a class (rather than bare module functions) to give the
    context-variable operations a single, discoverable, mockable surface.
    """

    @staticmethod
    def get_current() -> ExecutionContext:
        return _current_context.get()

    @staticmethod
    def set_current(context: ExecutionContext) -> Token[ExecutionContext]:
        return _current_context.set(context)

    @staticmethod
    def reset(token: Token[ExecutionContext]) -> None:
        try:
            _current_context.reset(token)
        except RuntimeError:
            pass

    @staticmethod
    def clear() -> Token[ExecutionContext]:
        """Reset to an empty context (e.g. at the start of a new task)."""
        return _current_context.set(_EMPTY_CONTEXT)
