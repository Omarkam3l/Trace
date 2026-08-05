"""Unit tests for API key authentication provider."""

from __future__ import annotations

import pytest

from traceforge.security.auth.api_key import ApiKeyProvider
from traceforge.security.exceptions import InvalidTokenError
from traceforge.security.models.permissions import Role
from traceforge.security.models.user import User


def test_api_key_register_and_validate():
    provider = ApiKeyProvider()
    user = User(user_id="u1", roles=[Role.VIEWER])

    key = provider.register_key(user)
    assert isinstance(key, str)

    recovered = provider.validate_key(key)
    assert recovered.user_id == "u1"


def test_api_key_custom_key():
    provider = ApiKeyProvider()
    user = User(user_id="u1")

    key = provider.register_key(user, key="my-custom-key")
    assert key == "my-custom-key"

    recovered = provider.validate_key("my-custom-key")
    assert recovered.user_id == "u1"


def test_api_key_invalid():
    provider = ApiKeyProvider()

    with pytest.raises(InvalidTokenError, match="Invalid API key"):
        provider.validate_key("nonexistent")


def test_api_key_disable():
    provider = ApiKeyProvider()
    user = User(user_id="u1")

    key = provider.register_key(user)
    provider.disable_key(key)

    with pytest.raises(InvalidTokenError, match="disabled"):
        provider.validate_key(key)


def test_api_key_rotation():
    provider = ApiKeyProvider()
    user = User(user_id="u1")

    old_key = provider.register_key(user)
    new_key = provider.rotate_key(old_key)
    assert new_key != old_key

    # Old key should be disabled
    with pytest.raises(InvalidTokenError, match="disabled"):
        provider.validate_key(old_key)

    # New key should work
    recovered = provider.validate_key(new_key)
    assert recovered.user_id == "u1"
