"""Replay Engine exception hierarchy."""

from __future__ import annotations

from traceforge.api.exceptions import TraceForgeError


class ReplayError(TraceForgeError):
    """Base exception for all Replay Engine operations."""


class ReplayValidationError(ReplayError):
    """Raised when sequence validation or replay constraints fail."""


class ReplayConsistencyError(ReplayError):
    """Raised when structural or graph consistency checks fail during replay."""


class ReplayConfigurationError(ReplayError):
    """Raised when invalid ReplayConfig parameters are supplied."""
