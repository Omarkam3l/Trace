"""FastAPI dependencies for authentication and authorization."""

from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, Request

from traceforge.security.exceptions import AuthenticationError
from traceforge.security.middleware.authorization import check_permission
from traceforge.security.models.permissions import Permission
from traceforge.security.models.user import User


def get_current_user(request: Request) -> User:
    """FastAPI dependency extracting the authenticated user from request state."""
    user = getattr(request.state, "user", None)
    if user is None:
        raise AuthenticationError("No authenticated user in request")
    return user


def require_permission(permission: Permission) -> Callable:
    """Dependency factory returning a checker that verifies the user has the required permission."""

    def _checker(user: User = Depends(get_current_user)) -> User:
        check_permission(user, permission)
        return user

    return _checker
