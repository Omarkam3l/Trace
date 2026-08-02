"""The instrumentation interface that framework adapters implement.

An ``Instrumentor`` knows how to hook a specific framework (FastAPI,
Flask, Django, Express, Next.js, React, Flutter, LangGraph, ...) so that
requests/executions automatically become TraceForge spans. None of the
concrete adapters are implemented yet — see the per-framework
subpackages, each currently reserved for future work — but this is the
stable contract they'll implement against.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from traceforge.core.tracer import Tracer


class Instrumentor(ABC):
    """Base class for framework-specific auto-instrumentation."""

    @abstractmethod
    def install(self, tracer: Tracer) -> None:
        """Patch/hook the target framework to emit spans via ``tracer``."""
        raise NotImplementedError

    @abstractmethod
    def uninstall(self) -> None:
        """Undo whatever ``install`` did."""
        raise NotImplementedError
