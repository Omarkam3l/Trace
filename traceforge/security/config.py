"""Security configuration definitions."""

from __future__ import annotations

import warnings

from pydantic import BaseModel, ConfigDict, field_validator

DEFAULT_JWT_SECRET = "traceforge-default-secret-change-in-production"


class SecurityConfig(BaseModel):
    """Immutable configuration for TraceForge security layer."""

    model_config = ConfigDict(frozen=True)

    jwt_secret: str = DEFAULT_JWT_SECRET
    jwt_algorithm: str = "HS256"
    token_expiration_minutes: int = 60
    enable_api_keys: bool = True
    rate_limit_requests: int = 100

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if v == DEFAULT_JWT_SECRET:
            warnings.warn(
                "Security Warning: Using default jwt_secret in SecurityConfig! Set TRACEFORGE_JWT_SECRET in production.",
                UserWarning,
                stacklevel=2,
            )
        elif len(v) < 32:
            raise ValueError(
                f"Insecure JWT secret key length ({len(v)} bytes). Key length must be at least 32 bytes/characters for security compliance."
            )
        return v
