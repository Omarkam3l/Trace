"""Unit tests for Authentication middleware."""

from __future__ import annotations

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from traceforge.security.auth.provider import AuthProvider
from traceforge.security.config import SecurityConfig
from traceforge.security.dependencies import get_current_user
from traceforge.security.middleware.authentication import AuthenticationMiddleware
from traceforge.security.models.permissions import Role
from traceforge.security.models.user import User


def _make_app():
    config = SecurityConfig(jwt_secret="mw-test-secret")
    auth_provider = AuthProvider(config)
    app = FastAPI()
    app.add_middleware(AuthenticationMiddleware, auth_provider=auth_provider)

    @app.get("/check")
    def check(user: User = Depends(get_current_user)):
        return {"user_id": user.user_id}

    return app, auth_provider, TestClient(app)


def test_middleware_jwt_authentication():
    app, auth_provider, client = _make_app()
    user = User(user_id="u1", roles=[Role.ADMIN])
    token = auth_provider.jwt.create_token(user)

    res = client.get("/check", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["user_id"] == "u1"


def test_middleware_api_key_authentication():
    app, auth_provider, client = _make_app()
    user = User(user_id="u2", roles=[Role.VIEWER])
    key = auth_provider.api_key.register_key(user)

    res = client.get("/check", headers={"Authorization": f"Api-Key {key}"})
    assert res.status_code == 200
    assert res.json()["user_id"] == "u2"


def test_middleware_missing_header():
    _, _, client = _make_app()
    res = client.get("/check")
    assert res.status_code == 401


def test_middleware_malformed_header():
    _, _, client = _make_app()
    res = client.get("/check", headers={"Authorization": "malformed"})
    assert res.status_code == 401


def test_middleware_invalid_token():
    _, _, client = _make_app()
    res = client.get("/check", headers={"Authorization": "Bearer bad.token.value"})
    assert res.status_code == 401
