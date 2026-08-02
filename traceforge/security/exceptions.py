"""Security layer exception hierarchy."""

from __future__ import annotations

from traceforge.api.exceptions import TraceForgeError


class SecurityError(TraceForgeError):
    """Base exception for all security layer operations."""


class AuthenticationError(SecurityError):
    """Raised when authentication fails (HTTP 401)."""


class InvalidTokenError(AuthenticationError):
    """Raised when a JWT or API key token is invalid or expired (HTTP 401)."""


class AuthorizationError(SecurityError):
    """Raised when authorization fails (HTTP 403)."""


class PermissionDeniedError(AuthorizationError):
    """Raised when the authenticated user lacks a required permission (HTTP 403)."""


class RateLimitExceededError(SecurityError):
    """Raised when a user exceeds the configured rate limit (HTTP 429)."""
