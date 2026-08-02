"""Execution Diff Engine exception hierarchy."""

from __future__ import annotations

from traceforge.api.exceptions import TraceForgeError


class DiffError(TraceForgeError):
    """Base exception for all Execution Diff Engine operations."""


class DiffValidationError(DiffError):
    """Raised when comparing incompatible or un-replayable sessions."""


class DiffConfigurationError(DiffError):
    """Raised when invalid DiffConfig parameters are provided."""
