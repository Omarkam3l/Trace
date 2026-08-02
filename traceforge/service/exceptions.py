"""TraceForge API Service Layer exception hierarchy."""

from __future__ import annotations

from traceforge.api.exceptions import TraceForgeError


class ApiServiceError(TraceForgeError):
    """Base exception for all TraceForge API Service Layer operations."""


class ServiceNotFoundError(ApiServiceError):
    """Raised when a requested session or entity is not found in the service layer."""


class ServiceExecutionError(ApiServiceError):
    """Raised when a service layer workflow operation encounters an error."""
