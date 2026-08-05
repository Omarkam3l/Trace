"""Unit tests for JWT authentication provider."""

from __future__ import annotations

import time

import pytest

from traceforge.security.auth.jwt import JwtProvider
from traceforge.security.config import SecurityConfig
from traceforge.security.exceptions import InvalidTokenError
from traceforge.security.models.permissions import Permission, Role
from traceforge.security.models.user import User

VALID_TEST_SECRET = "test-secret-key-must-be-at-least-32-chars-long"


def test_jwt_create_and_validate():
    config = SecurityConfig(jwt_secret=VALID_TEST_SECRET)
    provider = JwtProvider(config)
    user = User(user_id="u1", roles=[Role.ADMIN], permissions=[Permission.READ_SESSIONS])

    token = provider.create_token(user)
    assert isinstance(token, str)

    payload = provider.validate_token(token)
    assert payload.user_id == "u1"
    assert Role.ADMIN in payload.roles
    assert Permission.READ_SESSIONS in payload.permissions


def test_jwt_token_to_user():
    config = SecurityConfig(jwt_secret=VALID_TEST_SECRET)
    provider = JwtProvider(config)
    user = User(user_id="u1", roles=[Role.ANALYST])

    token = provider.create_token(user)
    recovered = provider.token_to_user(token)
    assert recovered.user_id == "u1"
    assert Role.ANALYST in recovered.roles


def test_jwt_expired_token():
    config = SecurityConfig(jwt_secret=VALID_TEST_SECRET, token_expiration_minutes=0)
    provider = JwtProvider(config)
    user = User(user_id="u1")

    token = provider.create_token(user)
    time.sleep(0.1)

    with pytest.raises(InvalidTokenError, match="expired"):
        provider.validate_token(token)


def test_jwt_invalid_signature():
    config_a = SecurityConfig(jwt_secret="secret-a-key-must-be-at-least-32-chars-long")
    config_b = SecurityConfig(jwt_secret="secret-b-key-must-be-at-least-32-chars-long")
    provider_a = JwtProvider(config_a)
    provider_b = JwtProvider(config_b)

    user = User(user_id="u1")
    token = provider_a.create_token(user)

    with pytest.raises(InvalidTokenError):
        provider_b.validate_token(token)


def test_jwt_invalid_token_string():
    config = SecurityConfig(jwt_secret=VALID_TEST_SECRET)
    provider = JwtProvider(config)

    with pytest.raises(InvalidTokenError):
        provider.validate_token("not.a.valid.token")


def test_jwt_secret_length_validation():
    with pytest.raises(ValueError, match="Insecure JWT secret key length"):
        SecurityConfig(jwt_secret="too-short")
