"""Unified authentication provider facade."""

from __future__ import annotations

from traceforge.security.auth.api_key import ApiKeyProvider
from traceforge.security.auth.jwt import JwtProvider
from traceforge.security.config import SecurityConfig
from traceforge.security.exceptions import AuthenticationError
from traceforge.security.models.user import User


class AuthProvider:
    """Unified facade delegating to JWT or API key authentication providers."""

    def __init__(self, config: SecurityConfig) -> None:
        self._config = config
        self._jwt = JwtProvider(config)
        self._api_key = ApiKeyProvider()

    @property
    def jwt(self) -> JwtProvider:
        return self._jwt

    @property
    def api_key(self) -> ApiKeyProvider:
        return self._api_key

    def authenticate(self, authorization: str) -> User:
        """Authenticate a user from an Authorization header value.

        Supports:
          - Bearer <jwt-token>
          - Api-Key <key>
        """
        if not authorization:
            raise AuthenticationError("Missing Authorization header")

        parts = authorization.split(" ", 1)
        if len(parts) != 2:
            raise AuthenticationError("Malformed Authorization header")

        scheme, credential = parts[0].lower(), parts[1]

        if scheme == "bearer":
            return self._jwt.token_to_user(credential)
        elif scheme == "api-key" and self._config.enable_api_keys:
            return self._api_key.validate_key(credential)
        else:
            raise AuthenticationError(f"Unsupported authentication scheme: {parts[0]}")
