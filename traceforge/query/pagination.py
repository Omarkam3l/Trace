"""Pagination model for Query Engine read operations."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, field_validator

from traceforge.query.exceptions import InvalidQueryError


class Pagination(BaseModel):
    """Immutable pagination parameters for query results."""

    model_config = ConfigDict(frozen=True)

    limit: int = 100
    offset: int = 0

    @field_validator("limit")
    @classmethod
    def validate_limit(cls, v: int) -> int:
        if v <= 0:
            raise InvalidQueryError("Pagination limit must be greater than 0")
        return v

    @field_validator("offset")
    @classmethod
    def validate_offset(cls, v: int) -> int:
        if v < 0:
            raise InvalidQueryError("Pagination offset must be greater than or equal to 0")
        return v
