"""Tracer public facade class."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from traceforge.domain.activity import Activity
from traceforge.domain.environment import Environment
from traceforge.domain.session import RecordingSession
from traceforge.instrumentation.config import InstrumentationConfig
from traceforge.instrumentation.context_managers import (
    ActivityContextManager,
    SessionContextManager,
)
from traceforge.instrumentation.decorators import wrap_with_activity
from traceforge.instrumentation.service import InstrumentationService


class Tracer:
    """Primary developer-facing facade for application instrumentation."""

    def __init__(self, config: InstrumentationConfig | None = None) -> None:
        self._service = InstrumentationService(config=config)

    @property
    def config(self) -> InstrumentationConfig:
        return self._service.config

    def configure(self, config: InstrumentationConfig) -> None:
        """Update instrumentation config. Raises ConfigurationFreezeError if session is active."""
        self._service.configure(config)

    def is_recording(self) -> bool:
        """Return True if a recording session is currently active."""
        return self._service.is_recording()

    def start_session(
        self,
        name: str = "Session",
        environment: Environment | None = None,
        session_id: str | None = None,
    ) -> RecordingSession:
        """Start a new recording session."""
        return self._service.start_session(name=name, environment=environment, session_id=session_id)

    def stop_session(self) -> RecordingSession:
        """Stop the active recording session and return the completed session object."""
        return self._service.stop_session()

    def session(
        self,
        name: str = "Session",
        environment: Environment | None = None,
        session_id: str | None = None,
    ) -> SessionContextManager:
        """Return a session context manager for 'with trace.session(...):' scopes."""
        return SessionContextManager(
            service=self._service,
            name=name,
            environment=environment,
            session_id=session_id,
        )

    def start_activity(self, name: str, activity_id: str | None = None) -> str:
        """Start a new activity scope."""
        return self._service.start_activity(name=name, activity_id=activity_id)

    def stop_activity(self) -> Activity:
        """Finish the active activity scope and return the completed Activity object."""
        return self._service.stop_activity()

    def activity(
        self,
        name: str | Callable[..., Any] | None = None,
    ) -> ActivityContextManager | Callable[..., Any]:
        """Activity scope helper supporting context manager or decorator usage."""
        if callable(name):
            return wrap_with_activity(self._service, fn=name)
        elif isinstance(name, str):
            return ActivityContextManager(service=self._service, name=name)
        else:
            return ActivityContextManager(service=self._service, name="Activity")

    def event(
        self,
        name: str,
        metadata: dict[str, Any] | None = None,
        payload: dict[str, Any] | None = None,
    ) -> None:
        """Emit a lightweight custom execution event marker."""
        self._service.emit_event(name=name, metadata=metadata, payload=payload)

    def current_session(self) -> dict[str, Any] | None:
        """Return current active session metadata, if any."""
        return self._service.current_session()

    def current_activity(self) -> Activity | None:
        """Return snapshot of current active activity, if any."""
        return self._service.current_activity()

    def __call__(
        self,
        fn_or_name: Callable[..., Any] | str | None = None,
    ) -> Any:
        """Decorator interface supporting @trace or @trace('activity_name')."""
        if callable(fn_or_name):
            return wrap_with_activity(self._service, fn=fn_or_name)
        elif isinstance(fn_or_name, str):

            def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
                return wrap_with_activity(self._service, fn=fn, activity_name=fn_or_name)

            return decorator
        else:

            def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
                return wrap_with_activity(self._service, fn=fn)

            return decorator
