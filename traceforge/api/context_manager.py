"""Ergonomic span context managers built on top of the default tracer.

For explicit-tracer usage, prefer calling ``tracer.start_span(...)``
directly (see :mod:`traceforge.core.tracer`). These helpers exist for the
common case of a single, process-wide tracer configured via
``traceforge.configure(tracer)``.
"""

from __future__ import annotations

from traceforge.api.functions import get_tracer
from traceforge.core.span import Span
from traceforge.core.tracer import SpanContext
from traceforge.models.enums import SpanKind
from traceforge.models.metadata import Attributes


def span(
    name: str,
    *,
    kind: SpanKind = SpanKind.INTERNAL,
    attributes: Attributes | None = None,
) -> SpanContext:
    """Start a span on the configured default tracer.

    Usable as both ``with`` and ``async with``::

        with traceforge.span("parse-request") as s:
            ...

        async with traceforge.span("fetch-user") as s:
            ...
    """
    return get_tracer().start_span(name, kind=kind, attributes=attributes)


__all__ = ["span", "Span"]
