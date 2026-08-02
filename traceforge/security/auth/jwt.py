"""JWT authentication provider."""

from __future__ import annotations

import time
from typing import Any

import jwt

from traceforge.security.config import SecurityConfig
from traceforge.security.exceptions import InvalidTokenError
from traceforge.security.models.permissions import Permission, Role
from traceforge.security.models.token import TokenPayload
from traceforge.security.models.user import User


class JwtProvider:
    """Creates and validates JWT tokens."""

    def __init__(self, config: SecurityConfig) -> None:
        self._config = config

    def create_token(self, user: User) -> str:
        """Create a signed JWT token for the given user."""
        exp = time.time() + (self._config.token_expiration_minutes * 60)
        payload: dict[str, Any] = {
            "user_id": user.user_id,
            "roles": [r.value for r in user.roles],
            "permissions": [p.value for p in user.permissions],
            "exp": exp,
        }
        return jwt.encode(payload, self._config.jwt_secret, algorithm=self._config.jwt_algorithm)

    def validate_token(self, token: str) -> TokenPayload:
        """Validate and decode a JWT token, returning the TokenPayload."""
        try:
            data = jwt.decode(token, self._config.jwt_secret, algorithms=[self._config.jwt_algorithm])
        except jwt.ExpiredSignatureError as err:
            raise InvalidTokenError("Token has expired") from err
        except jwt.InvalidTokenError as err:
            raise InvalidTokenError(f"Invalid token: {err}") from err

        return TokenPayload(
            user_id=data["user_id"],
            roles=[Role(r) for r in data.get("roles", [])],
            permissions=[Permission(p) for p in data.get("permissions", [])],
            exp=data.get("exp", 0.0),
        )

    def token_to_user(self, token: str) -> User:
        """Validate a JWT token and return the corresponding User."""
        payload = self.validate_token(token)
        return User(
            user_id=payload.user_id,
            roles=payload.roles,
            permissions=payload.permissions,
        )
