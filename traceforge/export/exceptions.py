"""Export System exception hierarchy."""

from __future__ import annotations

from traceforge.api.exceptions import TraceForgeError


class ExportError(TraceForgeError):
    """Base exception for all Export System operations."""


class ExporterNotFoundError(ExportError):
    """Raised when an unsupported or unregistered export format is requested."""


class ExportFormattingError(ExportError):
    """Raised when formatting an artifact into a target export format fails."""
