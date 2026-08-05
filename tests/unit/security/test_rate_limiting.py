"""Unit tests for rate limiting middleware."""

from __future__ import annotations

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from traceforge.security.auth.provider import AuthProvider
from traceforge.security.config import SecurityConfig
from traceforge.security.dependencies import get_current_user
from traceforge.security.middleware.authentication import AuthenticationMiddleware
from traceforge.security.middleware.rate_limit import RateLimitMiddleware
from traceforge.security.models.permissions import Role
from traceforge.security.models.user import User


def test_rate_limit_exceeded():
    config = SecurityConfig(jwt_secret="rl-test-secret-must-be-at-least-32-chars")
    auth_provider = AuthProvider(config)

    app = FastAPI()
    # Rate limit middleware runs AFTER authentication
    app.add_middleware(RateLimitMiddleware, max_requests=3, window_seconds=60)
    app.add_middleware(AuthenticationMiddleware, auth_provider=auth_provider)

    @app.get("/ping")
    def ping(user: User = Depends(get_current_user)):
        return {"ok": True}

    client = TestClient(app)
    user = User(user_id="u1", roles=[Role.ADMIN])
    token = auth_provider.jwt.create_token(user)
    headers = {"Authorization": f"Bearer {token}"}

    # First 3 requests should succeed
    for _ in range(3):
        res = client.get("/ping", headers=headers)
        assert res.status_code == 200

    # 4th request should be rate-limited
    res = client.get("/ping", headers=headers)
    assert res.status_code == 429
    assert res.json()["error"]["type"] == "RateLimitExceededError"
