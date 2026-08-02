"""TraceForge's exception hierarchy.

All exceptions the SDK raises inherit from :class:`TraceForgeError` so
callers can catch broadly (``except TraceForgeError``) or narrowly.
"""

from __future__ import annotations


class TraceForgeError(Exception):
    """Base class for all TraceForge exceptions."""


class SpanNotActiveError(TraceForgeError):
    """Raised when mutating a span that has already finished."""


class TracerNotConfiguredError(TraceForgeError):
    """Raised when a default tracer is used before being configured."""


class StorageError(TraceForgeError):
    """Raised by storage adapters on read/write failures."""


class ExporterError(TraceForgeError):
    """Raised by exporters on export/configuration failures."""


class ConfigurationError(TraceForgeError):
    """Raised for invalid TraceForge configuration."""


class ConfigurationFreezeError(ConfigurationError):
    """Raised when attempting to reconfigure TraceForge during an active recording session."""
