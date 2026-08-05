"""Context managers for session and activity scope management."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from traceforge.domain.environment import Environment
    from traceforge.domain.session import RecordingSession
    from traceforge.instrumentation.service import InstrumentationService


class SessionContextManager:
    """Sync and async context manager for recording session scopes."""

    def __init__(
        self,
        service: InstrumentationService,
        name: str = "Session",
        environment: Environment | None = None,
        session_id: str | None = None,
    ) -> None:
        self._service = service
        self._name = name
        self._environment = environment
        self._session_id = session_id
        self._session: RecordingSession | None = None

    def __enter__(self) -> SessionContextManager:
        try:
            self._session = self._service.start_session(
                name=self._name,
                environment=self._environment,
                session_id=self._session_id,
            )
        except Exception:
            pass
        return self

    def __exit__(self, *exc_info: object) -> None:
        try:
            self.completed_session = self._service.stop_session()
        except Exception:
            pass

    async def __aenter__(self) -> SessionContextManager:
        return self.__enter__()

    async def __aexit__(self, *exc_info: object) -> None:
        self.__exit__(*exc_info)


class ActivityContextManager:
    """Sync and async context manager for activity scopes."""

    def __init__(
        self,
        service: InstrumentationService,
        name: str = "Activity",
        activity_id: str | None = None,
    ) -> None:
        self._service = service
        self._name = name
        self._activity_id = activity_id

    def __enter__(self) -> ActivityContextManager:
        try:
            if self._service.is_recording():
                self._service.start_activity(name=self._name, activity_id=self._activity_id)
        except Exception:
            pass
        return self

    def __exit__(self, *exc_info: object) -> None:
        try:
            if self._service.is_recording():
                self._service.stop_activity()
        except Exception:
            pass

    async def __aenter__(self) -> ActivityContextManager:
        return self.__enter__()

    async def __aexit__(self, *exc_info: object) -> None:
        self.__exit__(*exc_info)
