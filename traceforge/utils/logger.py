"""Internal logging for TraceForge's own diagnostics.

This is deliberately separate from the tracing engine itself: TraceForge
is not a logger, but it still needs to report its *own* internal problems
(a broken exporter, a storage write failure) somewhere. It uses stdlib
``logging`` with a ``NullHandler`` by default so it stays silent unless
the host application opts in.
"""

from __future__ import annotations

import logging

_ROOT_LOGGER_NAME = "traceforge"
logging.getLogger(_ROOT_LOGGER_NAME).addHandler(logging.NullHandler())


def get_logger(name: str) -> logging.Logger:
    if not name.startswith(_ROOT_LOGGER_NAME):
        name = f"{_ROOT_LOGGER_NAME}.{name}"
    return logging.getLogger(name)
