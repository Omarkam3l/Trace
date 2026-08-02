"""Token payload model for TraceForge security."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from traceforge.security.models.permissions import Permission, Role


class TokenPayload(BaseModel):
    """Immutable JWT token payload representation."""

    model_config = ConfigDict(frozen=True)

    user_id: str
    roles: list[Role] = Field(default_factory=list)
    permissions: list[Permission] = Field(default_factory=list)
    exp: float = 0.0
