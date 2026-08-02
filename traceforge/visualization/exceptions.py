"""Visualization Data Adapter Layer exception hierarchy."""

from __future__ import annotations

from traceforge.api.exceptions import TraceForgeError


class VisualizationError(TraceForgeError):
    """Base exception for all Visualization Adapter Layer operations."""


class AdapterError(VisualizationError):
    """Raised when adapting a domain artifact into a visualization view model fails."""
