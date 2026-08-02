"""BackendSelector for automatic CPython instrumentation backend resolution."""

from __future__ import annotations

import sys
from collections.abc import Callable
from typing import TYPE_CHECKING

from traceforge.runtime.backends.base import InstrumentationBackend
from traceforge.runtime.backends.pep669 import PEP669Backend
from traceforge.runtime.backends.setprofile import SetProfileBackend
from traceforge.runtime.backends.settrace import SetTraceBackend
from traceforge.runtime.enums import BackendType, ProfileType

if TYPE_CHECKING:
    from traceforge.engine.raw_event import RawEvent
    from traceforge.runtime.config import RuntimeConfig
    from traceforge.runtime.filter import RuntimeFilter


class BackendSelector:
    """Selects the optimal InstrumentationBackend for the current Python environment."""

    @staticmethod
    def select_backend(
        config: RuntimeConfig,
        emit_callback: Callable[[RawEvent], None],
        filter_evaluator: RuntimeFilter,
    ) -> InstrumentationBackend:
        # 1. Explicit user configuration override
        if config.backend == BackendType.PEP669:
            return PEP669Backend(emit_callback, filter_evaluator, config)
        elif config.backend == BackendType.SETTRACE:
            return SetTraceBackend(emit_callback, filter_evaluator, config)
        elif config.backend == BackendType.SETPROFILE:
            return SetProfileBackend(emit_callback, filter_evaluator, config)

        # 2. Deep Debug profile requires sys.settrace for line events and variable capture
        if config.profile == ProfileType.DEEP_DEBUG:
            return SetTraceBackend(emit_callback, filter_evaluator, config)

        # 3. Automatic Python 3.12+ PEP 669 selection
        if sys.version_info >= (3, 12) and hasattr(sys, "monitoring"):
            return PEP669Backend(emit_callback, filter_evaluator, config)

        # 4. Default fallback: sys.setprofile
        return SetProfileBackend(emit_callback, filter_evaluator, config)
