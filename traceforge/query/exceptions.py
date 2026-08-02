"""Query Engine exception hierarchy."""

from __future__ import annotations

from traceforge.api.exceptions import TraceForgeError


class QueryError(TraceForgeError):
    """Base exception for all Query Engine read operations."""


class NotFoundError(QueryError):
    """Raised when a requested domain entity or record is not found."""


class InvalidQueryError(QueryError):
    """Raised when a query object, filter, or pagination specification is invalid."""


class RepositoryError(QueryError):
    """Raised when an internal read repository or query driver failure occurs."""
