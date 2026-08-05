"""PEP669Backend using CPython 3.12+ sys.monitoring API."""

from __future__ import annotations

import sys
import uuid
from datetime import UTC, datetime
from types import CodeType
from typing import Any

from traceforge.domain.enums import SourceType
from traceforge.engine.raw_event import RawEvent
from traceforge.runtime.backends.base import InstrumentationBackend
from traceforge.runtime.backends.setprofile import SetProfileBackend
from traceforge.runtime.enums import BackendType, RuntimeNodeType


class PEP669Backend(InstrumentationBackend):
    """CPython 3.12+ sys.monitoring API instrumentation backend."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._fallback_backend: SetProfileBackend | None = None
        if not hasattr(sys, "monitoring"):
            # Fallback to sys.setprofile on Python < 3.12
            self._fallback_backend = SetProfileBackend(*args, **kwargs)

    @property
    def backend_type(self) -> BackendType:
        return BackendType.PEP669

    def start(self) -> None:
        if self._fallback_backend:
            self._fallback_backend.start()
            self._active = True
            return

        if not self._active:
            self._active = True
            tool_id = getattr(sys.monitoring, "PROFILER_ID", 2)
            sys.monitoring.use_tool_id(tool_id, "traceforge")

            events = sys.monitoring.events.PY_START | sys.monitoring.events.PY_RETURN | sys.monitoring.events.RAISE
            sys.monitoring.set_events(tool_id, events)

            def py_start_func(code: CodeType, instruction_offset: int) -> Any:
                if not self._active:
                    return
                mod_name = code.co_name
                if self._filter.should_trace(mod_name, code.co_filename, code.co_name):
                    evt = RawEvent(
                        event_id=f"evt_{uuid.uuid4().hex[:16]}",
                        timestamp=datetime.now(UTC),
                        type="FunctionEntered",
                        source=SourceType.PYTHON_SDK,
                        payload={
                            "name": code.co_name,
                            "filename": code.co_filename,
                            "node_type": RuntimeNodeType.FUNCTION,
                        },
                    )
                    self._emit_callback(evt)

            def py_return_func(code: CodeType, instruction_offset: int, retval: Any) -> Any:
                if not self._active:
                    return
                mod_name = code.co_name
                if self._filter.should_trace(mod_name, code.co_filename, code.co_name):
                    evt = RawEvent(
                        event_id=f"evt_{uuid.uuid4().hex[:16]}",
                        timestamp=datetime.now(UTC),
                        type="FunctionReturned",
                        source=SourceType.PYTHON_SDK,
                        payload={"name": code.co_name, "node_type": RuntimeNodeType.FUNCTION},
                    )
                    self._emit_callback(evt)

            sys.monitoring.register_callback(tool_id, sys.monitoring.events.PY_START, py_start_func)
            sys.monitoring.register_callback(tool_id, sys.monitoring.events.PY_RETURN, py_return_func)

    def stop(self) -> None:
        if self._fallback_backend:
            self._fallback_backend.stop()
            self._active = False
            return

        if self._active:
            tool_id = getattr(sys.monitoring, "PROFILER_ID", 2)
            sys.monitoring.set_events(tool_id, 0)
            sys.monitoring.free_tool_id(tool_id)
            self._active = False
