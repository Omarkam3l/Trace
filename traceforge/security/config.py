"""Security configuration definitions."""

from __future__ import annotations

import warnings

from pydantic import BaseModel, ConfigDict, field_validator

# Single source of truth for the insecure placeholder secret. Every other
# module that needs to compare against "the default secret" (config schema,
# CLI warnings, tests) must import this constant rather than re-typing the
# string, so the comparison can never silently drift out of sync again.
DEFAULT_JWT_SECRET = "traceforge-default-secret-change-in-production"

MIN_JWT_SECRET_LENGTH = 32


def validate_jwt_secret_value(v: str) -> str:
    """Shared validation logic for a jwt_secret value.

    - The known default placeholder is allowed through (so the app can still
      start in a fresh dev environment) but always emits a loud warning.
    - Any other secret must meet the minimum length for HMAC-SHA256.

    Shared between ``SecurityConfig`` and ``configuration.schema.SecurityConfigSchema``
    so the two config surfaces can never enforce different rules.
    """
    if v == DEFAULT_JWT_SECRET:
        warnings.warn(
            "Security Warning: Using the default TraceForge jwt_secret. "
            "Set TRACEFORGE_JWT_SECRET to a random value of at least "
            f"{MIN_JWT_SECRET_LENGTH} characters before deploying.",
            UserWarning,
            stacklevel=3,
        )
    elif len(v) < MIN_JWT_SECRET_LENGTH:
        raise ValueError(
            f"Insecure JWT secret key length ({len(v)} bytes). "
            f"Key length must be at least {MIN_JWT_SECRET_LENGTH} bytes/characters "
            "for security compliance."
        )
    return v


class SecurityConfig(BaseModel):
    """Immutable configuration for TraceForge security layer."""

    # validate_default=True is required: without it, Pydantic v2 skips
    # field_validators entirely when a field is left at its default value —
    # which is exactly the common case (SecurityConfig() with no overrides)
    # that this validator exists to catch.
    model_config = ConfigDict(frozen=True, validate_default=True)

    jwt_secret: str = DEFAULT_JWT_SECRET
    jwt_algorithm: str = "HS256"
    token_expiration_minutes: int = 60
    enable_api_keys: bool = True
    rate_limit_requests: int = 100

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        return validate_jwt_secret_value(v)
