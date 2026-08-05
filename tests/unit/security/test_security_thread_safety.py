"""Unit tests for multi-threaded concurrent security operations."""

from __future__ import annotations

import concurrent.futures

from traceforge.security.auth.api_key import ApiKeyProvider
from traceforge.security.auth.jwt import JwtProvider
from traceforge.security.config import SecurityConfig
from traceforge.security.models.permissions import Role
from traceforge.security.models.user import User


def test_concurrent_jwt_operations():
    config = SecurityConfig(jwt_secret="thread-test-secret-must-be-at-least-32-chars")
    provider = JwtProvider(config)
    user = User(user_id="u1", roles=[Role.ADMIN])

    def worker(worker_id: int):
        token = provider.create_token(user)
        payload = provider.validate_token(token)
        assert payload.user_id == "u1"

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(worker, i) for i in range(20)]
        concurrent.futures.wait(futures)
        for f in futures:
            f.result()


def test_concurrent_api_key_operations():
    provider = ApiKeyProvider()
    user = User(user_id="u1", roles=[Role.VIEWER])

    def worker(worker_id: int):
        key = provider.register_key(user)
        recovered = provider.validate_key(key)
        assert recovered.user_id == "u1"

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(worker, i) for i in range(20)]
        concurrent.futures.wait(futures)
        for f in futures:
            f.result()
