"""Permission and Role definitions for TraceForge security."""

from __future__ import annotations

from enum import Enum


class Permission(str, Enum):
    """Granular permissions for TraceForge API operations."""

    READ_SESSIONS = "read:sessions"
    READ_REPLAY = "read:replay"
    READ_DIFF = "read:diff"
    EXPORT_ARTIFACTS = "export:artifacts"
    VIEW_VISUALIZATION = "view:visualization"


class Role(str, Enum):
    """User roles with pre-defined permission sets."""

    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.ADMIN: frozenset(Permission),
    Role.ANALYST: frozenset({
        Permission.READ_SESSIONS,
        Permission.READ_REPLAY,
        Permission.READ_DIFF,
        Permission.VIEW_VISUALIZATION,
    }),
    Role.VIEWER: frozenset({
        Permission.READ_SESSIONS,
        Permission.VIEW_VISUALIZATION,
    }),
}
