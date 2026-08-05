"""Internal InstrumentationService layer orchestrating facade calls to Recorder."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from traceforge.api.exceptions import ConfigurationFreezeError
from traceforge.domain.activity import Activity
from traceforge.domain.environment import Environment
from traceforge.domain.session import RecordingSession
from traceforge.engine.raw_event import RawEvent
from traceforge.engine.recorder import Recorder
from traceforge.instrumentation.config import InstrumentationConfig


class InstrumentationService:
    """Internal orchestration service bridging Tracer facade to Recorder."""

    def __init__(self, config: InstrumentationConfig | None = None) -> None:
        self._config = config or InstrumentationConfig()
        self._recorder = Recorder()

    @property
    def config(self) -> InstrumentationConfig:
        return self._config

    @property
    def recorder(self) -> Recorder:
        return self._recorder

    def configure(self, config: InstrumentationConfig) -> None:
        """Update instrumentation config. Raises ConfigurationFreezeError if session is active."""
        if self.is_recording():
            raise ConfigurationFreezeError(
                "Cannot reconfigure InstrumentationConfig while a recording session is active."
            )
        self._config = config

    def is_recording(self) -> bool:
        return self._recorder.current_session() is not None

    def start_session(
        self,
        name: str = "Session",
        environment: Environment | None = None,
        session_id: str | None = None,
    ) -> RecordingSession:
        return self._recorder.start_session(
            environment=environment,
            profile=self._config.profile,
            session_id=session_id,
        )

    def stop_session(self) -> RecordingSession:
        return self._recorder.stop_session()

    def start_activity(self, name: str, activity_id: str | None = None) -> str:
        return self._recorder.start_activity(name=name, activity_id=activity_id)

    def stop_activity(self) -> Activity:
        return self._recorder.stop_activity()

    def emit_event(
        self,
        name: str,
        metadata: dict[str, Any] | None = None,
        payload: dict[str, Any] | None = None,
    ) -> None:
        if not self.is_recording():
            return

        payload_dict = dict(payload or {})
        payload_dict["name"] = name

        event = RawEvent(
            event_id=f"evt_{uuid.uuid4().hex[:16]}",
            timestamp=datetime.now(timezone.utc),
            type="Custom",
            payload=payload_dict,
            metadata=dict(metadata or {}),
        )
        self._recorder.emit(event)

    def current_session(self) -> dict[str, Any] | None:
        return self._recorder.current_session()

    def current_activity(self) -> Activity | None:
        return self._recorder.current_activity()
