"""Authorization utilities for FastAPI route protection."""

from __future__ import annotations

from traceforge.security.exceptions import PermissionDeniedError
from traceforge.security.models.permissions import Permission, ROLE_PERMISSIONS
from traceforge.security.models.user import User


def check_permission(user: User, permission: Permission) -> None:
    """Check that a user has a required permission.

    Checks explicit user permissions first, then falls back to role-based permissions.
    Raises PermissionDeniedError if the user lacks the permission.
    """
    if permission in user.permissions:
        return

    for role in user.roles:
        role_perms = ROLE_PERMISSIONS.get(role, frozenset())
        if permission in role_perms:
            return

    raise PermissionDeniedError(
        f"User {user.user_id!r} lacks permission {permission.value!r}"
    )
