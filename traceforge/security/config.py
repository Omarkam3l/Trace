"""Security configuration definitions."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class SecurityConfig(BaseModel):
    """Immutable configuration for TraceForge security layer."""

    model_config = ConfigDict(frozen=True)

    jwt_secret: str = "traceforge-default-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    token_expiration_minutes: int = 60
    enable_api_keys: bool = True
    rate_limit_requests: int = 100
