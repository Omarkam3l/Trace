"""Structured metadata primitives: attributes and exception info.

TraceForge is deliberately *not* business-logic aware — attributes are an
opaque bag of JSON-serializable key/value pairs supplied by the caller.
The only responsibility this module has is to make sure that bag stays
safe to serialize (JSON, JSONL, SQLite, OTLP-JSON, etc.) no matter what
the caller throws at it.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

Attributes = dict[str, Any]

_PRIMITIVE_TYPES = (str, int, float, bool, type(None))
_MAX_STRING_LENGTH = 8192
_MAX_ATTRIBUTES = 256


def _sanitize_value(value: Any, *, _depth: int = 0) -> Any:
    """Coerce a single attribute value into something JSON-serializable.

    Non-serializable values are converted to their ``repr()`` (truncated)
    rather than raising, since a bad attribute value should never crash
    the host application's execution.
    """
    if _depth > 4:
        return "<max-depth-exceeded>"

    if isinstance(value, _PRIMITIVE_TYPES):
        if isinstance(value, str) and len(value) > _MAX_STRING_LENGTH:
            return value[:_MAX_STRING_LENGTH] + "...<truncated>"
        return value

    if isinstance(value, (list, tuple, set)):
        return [_sanitize_value(v, _depth=_depth + 1) for v in list(value)[:_MAX_ATTRIBUTES]]

    if isinstance(value, dict):
        return {str(k): _sanitize_value(v, _depth=_depth + 1) for k, v in list(value.items())[:_MAX_ATTRIBUTES]}

    try:
        text = repr(value)
    except Exception:  # noqa: BLE001 - defensive: repr() itself may raise
        text = f"<unrepresentable:{type(value).__name__}>"
    return text[:_MAX_STRING_LENGTH]


def sanitize_attributes(attributes: Attributes | None) -> Attributes:
    """Return a defensively-copied, JSON-safe version of ``attributes``.

    - Caps the number of top-level keys to avoid unbounded memory growth.
    - Recursively sanitizes nested lists/dicts.
    - Falls back to ``repr()`` for values that aren't JSON-serializable.
    """
    if not attributes:
        return {}
    items = list(attributes.items())[:_MAX_ATTRIBUTES]
    return {str(key): _sanitize_value(value) for key, value in items}


class ExceptionInfo(BaseModel):
    """Structured representation of a captured exception."""

    type: str
    message: str
    stacktrace: str | None = None
    attributes: Attributes = Field(default_factory=dict)

    @classmethod
    def from_exception(cls, exc: BaseException) -> ExceptionInfo:
        import traceback

        return cls(
            type=type(exc).__qualname__,
            message=str(exc),
            stacktrace="".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
        )
