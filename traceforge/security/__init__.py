"""TraceForge Authentication & Authorization Security Layer (Phase 14)."""

from traceforge.security.auth import ApiKeyProvider, AuthProvider, JwtProvider
from traceforge.security.config import SecurityConfig
from traceforge.security.dependencies import get_current_user, require_permission
from traceforge.security.exceptions import (
    AuthenticationError,
    AuthorizationError,
    InvalidTokenError,
    PermissionDeniedError,
    RateLimitExceededError,
    SecurityError,
)
from traceforge.security.middleware import AuthenticationMiddleware, RateLimitMiddleware
from traceforge.security.models import ROLE_PERMISSIONS, Permission, Role, TokenPayload, User

__all__ = [
    "ROLE_PERMISSIONS",
    "ApiKeyProvider",
    "AuthProvider",
    "AuthenticationError",
    "AuthenticationMiddleware",
    "AuthorizationError",
    "InvalidTokenError",
    "JwtProvider",
    "Permission",
    "PermissionDeniedError",
    "RateLimitExceededError",
    "RateLimitMiddleware",
    "Role",
    "SecurityConfig",
    "SecurityError",
    "TokenPayload",
    "User",
    "get_current_user",
    "require_permission",
]
