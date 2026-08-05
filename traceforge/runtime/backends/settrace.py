"""SetTraceBackend using sys.settrace for Deep Debug profiling."""

from __future__ import annotations

import sys
import threading
import uuid
from datetime import UTC, datetime
from types import FrameType
from typing import Any

from traceforge.domain.enums import SourceType
from traceforge.engine.raw_event import RawEvent
from traceforge.runtime.backends.base import InstrumentationBackend
from traceforge.runtime.enums import BackendType, RuntimeNodeType


class SetTraceBackend(InstrumentationBackend):
    """CPython sys.settrace instrumentation backend for Deep Debug tracing."""

    @property
    def backend_type(self) -> BackendType:
        return BackendType.SETTRACE

    def start(self) -> None:
        if not self._active:
            self._active = True
            sys.settrace(self._trace_callback)
            if hasattr(threading, "settrace"):
                threading.settrace(self._trace_callback)

    def stop(self) -> None:
        if self._active:
            sys.settrace(None)
            if hasattr(threading, "settrace"):
                threading.settrace(None)
            self._active = False

    def _trace_callback(self, frame: FrameType, event: str, arg: Any) -> Any:
        if not self._active:
            return None

        code = frame.f_code
        func_name = code.co_name
        module_name = frame.f_globals.get("__name__", "")
        filename = code.co_filename

        if not self._filter.should_trace(module_name, filename, func_name):
            return None

        now = datetime.now(UTC)

        if event == "call":
            payload: dict[str, Any] = {
                "name": func_name,
                "module": module_name,
                "filename": filename,
                "lineno": frame.f_lineno,
                "node_type": RuntimeNodeType.FUNCTION,
            }
            if self._config.capture_locals:
                payload["locals"] = {k: repr(v) for k, v in frame.f_locals.items() if not k.startswith("__")}

            evt = RawEvent(
                event_id=f"evt_{uuid.uuid4().hex[:16]}",
                timestamp=now,
                type="FunctionEntered",
                source=SourceType.PYTHON_SDK,
                payload=payload,
            )
            self._emit_callback(evt)

        elif event == "return":
            evt = RawEvent(
                event_id=f"evt_{uuid.uuid4().hex[:16]}",
                timestamp=now,
                type="FunctionReturned",
                source=SourceType.PYTHON_SDK,
                payload={"name": func_name, "return_value": repr(arg)},
            )
            self._emit_callback(evt)

        elif event == "exception":
            exc_type, exc_val, _exc_tb = arg
            evt = RawEvent(
                event_id=f"evt_{uuid.uuid4().hex[:16]}",
                timestamp=now,
                type="ExceptionThrown",
                source=SourceType.PYTHON_SDK,
                payload={
                    "name": getattr(exc_type, "__name__", "Exception"),
                    "exception_type": getattr(exc_type, "__name__", "Exception"),
                    "message": str(exc_val),
                    "node_type": RuntimeNodeType.EXCEPTION,
                },
            )
            self._emit_callback(evt)

        elif event == "line" and self._config.profile == self._config.profile.DEEP_DEBUG:
            evt = RawEvent(
                event_id=f"evt_{uuid.uuid4().hex[:16]}",
                timestamp=now,
                type="LineExecuted",
                source=SourceType.PYTHON_SDK,
                payload={
                    "filename": filename,
                    "lineno": frame.f_lineno,
                    "node_type": RuntimeNodeType.LINE,
                },
            )
            self._emit_callback(evt)

        return self._trace_callback
