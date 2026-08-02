"""SetProfileBackend using sys.setprofile."""

from __future__ import annotations

import sys
import threading
import uuid
from datetime import datetime, timezone
from types import FrameType
from typing import Any

from traceforge.domain.enums import SourceType
from traceforge.engine.raw_event import RawEvent
from traceforge.runtime.backends.base import InstrumentationBackend
from traceforge.runtime.enums import BackendType, RuntimeNodeType


class SetProfileBackend(InstrumentationBackend):
    """CPython sys.setprofile instrumentation backend."""

    @property
    def backend_type(self) -> BackendType:
        return BackendType.SETPROFILE

    def start(self) -> None:
        if not self._active:
            self._active = True
            sys.setprofile(self._profile_callback)
            if hasattr(threading, "setprofile"):
                threading.setprofile(self._profile_callback)

    def stop(self) -> None:
        if self._active:
            sys.setprofile(None)
            if hasattr(threading, "setprofile"):
                threading.setprofile(None)
            self._active = False

    def _profile_callback(self, frame: FrameType, event: str, arg: Any) -> None:
        if not self._active:
            return

        code = frame.f_code
        func_name = code.co_name
        module_name = frame.f_globals.get("__name__", "")
        filename = code.co_filename

        # Filter check
        if not self._filter.should_trace(module_name, filename, func_name):
            return

        now = datetime.now(timezone.utc)

        if event == "call":
            evt = RawEvent(
                event_id=f"evt_{uuid.uuid4().hex[:16]}",
                timestamp=now,
                type="FunctionEntered",
                source=SourceType.PYTHON_SDK,
                payload={
                    "name": func_name,
                    "module": module_name,
                    "filename": filename,
                    "lineno": frame.f_lineno,
                    "node_type": RuntimeNodeType.FUNCTION,
                },
                metadata={
                    "code.function": func_name,
                    "code.filepath": filename,
                    "code.lineno": frame.f_lineno,
                },
            )
            self._emit_callback(evt)

        elif event == "return":
            evt = RawEvent(
                event_id=f"evt_{uuid.uuid4().hex[:16]}",
                timestamp=now,
                type="FunctionReturned",
                source=SourceType.PYTHON_SDK,
                payload={
                    "name": func_name,
                    "module": module_name,
                    "node_type": RuntimeNodeType.FUNCTION,
                },
            )
            self._emit_callback(evt)
