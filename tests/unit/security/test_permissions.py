"""Unit tests for Permission and Role definitions."""

from __future__ import annotations

from traceforge.security.models.permissions import ROLE_PERMISSIONS, Permission, Role


def test_permission_enum_values():
    assert Permission.READ_SESSIONS == "read:sessions"
    assert Permission.READ_REPLAY == "read:replay"
    assert Permission.READ_DIFF == "read:diff"
    assert Permission.EXPORT_ARTIFACTS == "export:artifacts"
    assert Permission.VIEW_VISUALIZATION == "view:visualization"


def test_role_enum_values():
    assert Role.ADMIN == "admin"
    assert Role.ANALYST == "analyst"
    assert Role.VIEWER == "viewer"


def test_admin_has_all_permissions():
    admin_perms = ROLE_PERMISSIONS[Role.ADMIN]
    for perm in Permission:
        assert perm in admin_perms


def test_analyst_permissions():
    analyst_perms = ROLE_PERMISSIONS[Role.ANALYST]
    assert Permission.READ_SESSIONS in analyst_perms
    assert Permission.READ_REPLAY in analyst_perms
    assert Permission.READ_DIFF in analyst_perms
    assert Permission.VIEW_VISUALIZATION in analyst_perms
    assert Permission.EXPORT_ARTIFACTS not in analyst_perms


def test_viewer_permissions():
    viewer_perms = ROLE_PERMISSIONS[Role.VIEWER]
    assert Permission.READ_SESSIONS in viewer_perms
    assert Permission.VIEW_VISUALIZATION in viewer_perms
    assert Permission.READ_REPLAY not in viewer_perms
    assert Permission.READ_DIFF not in viewer_perms
    assert Permission.EXPORT_ARTIFACTS not in viewer_perms
