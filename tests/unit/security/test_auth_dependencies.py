"""Unit tests for FastAPI auth dependencies (get_current_user, require_permission)."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from traceforge.security.auth.jwt import JwtProvider
from traceforge.security.config import SecurityConfig
from traceforge.security.dependencies import get_current_user, require_permission
from traceforge.security.exceptions import PermissionDeniedError
from traceforge.security.middleware.authentication import AuthenticationMiddleware
from traceforge.security.auth.provider import AuthProvider
from traceforge.security.models.permissions import Permission, Role
from traceforge.security.models.user import User


def _make_app_and_client():
    config = SecurityConfig(jwt_secret="dep-test-secret")
    auth_provider = AuthProvider(config)

    app = FastAPI()
    app.add_middleware(AuthenticationMiddleware, auth_provider=auth_provider)

    @app.exception_handler(PermissionDeniedError)
    async def perm_denied_handler(request: Request, exc: PermissionDeniedError) -> JSONResponse:
        return JSONResponse(status_code=403, content={"detail": str(exc)})

    @app.get("/me")
    def me(user: User = Depends(get_current_user)):
        return {"user_id": user.user_id}

    @app.get("/protected")
    def protected(user: User = Depends(require_permission(Permission.READ_SESSIONS))):
        return {"user_id": user.user_id, "allowed": True}

    @app.get("/export")
    def export_route(user: User = Depends(require_permission(Permission.EXPORT_ARTIFACTS))):
        return {"user_id": user.user_id, "allowed": True}

    return app, auth_provider, TestClient(app, raise_server_exceptions=False)


def test_get_current_user_dependency():
    app, auth_provider, client = _make_app_and_client()
    user = User(user_id="u1", roles=[Role.ADMIN])
    token = auth_provider.jwt.create_token(user)

    res = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["user_id"] == "u1"


def test_require_permission_allowed():
    app, auth_provider, client = _make_app_and_client()
    user = User(user_id="u1", roles=[Role.ADMIN])
    token = auth_provider.jwt.create_token(user)

    res = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["allowed"] is True


def test_require_permission_denied():
    app, auth_provider, client = _make_app_and_client()
    # Viewer does not have EXPORT_ARTIFACTS
    user = User(user_id="u1", roles=[Role.VIEWER])
    token = auth_provider.jwt.create_token(user)

    res = client.get("/export", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403


def test_no_auth_header_returns_401():
    _, _, client = _make_app_and_client()

    res = client.get("/me")
    assert res.status_code == 401
