"""Exception hierarchy for Phase 5.5 Execution Pipeline."""

from __future__ import annotations

from traceforge.api.exceptions import TraceForgeError


class PipelineError(TraceForgeError):
    """Base exception for all Execution Pipeline errors."""


class ConsumerRegistrationError(PipelineError):
    """Raised when registering or unregistering a consumer fails."""


class ConsumerExecutionError(PipelineError):
    """Raised when a consumer execution fails internally."""
