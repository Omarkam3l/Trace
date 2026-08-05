"""SessionManager: manages RecordingSession lifecycle and enforces single active session."""

from __future__ import annotations

import sys
import threading
import uuid
from datetime import datetime, timezone
from typing import Any

from traceforge.domain.activity import Activity
from traceforge.domain.enums import SessionStatus
from traceforge.domain.environment import Environment
from traceforge.domain.profile import RecordingProfile
from traceforge.domain.session import RecordingSession


class SessionManager:
    """Manages active RecordingSession state and lifecycle."""

    def __init__(self) -> None:
        self._current_session_id: str | None = None
        self._started_at: datetime | None = None
        self._environment: Environment | None = None
        self._profile: RecordingProfile | None = None
        self._status: SessionStatus = SessionStatus.STOPPED
        self._activities: list[Activity] = []
        self._lock = threading.RLock()

    @property
    def is_active(self) -> bool:
        with self._lock:
            return self._status == SessionStatus.RECORDING

    def start_session(
        self,
        session_id: str | None = None,
        environment: Environment | None = None,
        profile: RecordingProfile | None = None,
        started_at: datetime | None = None,
    ) -> str:
        with self._lock:
            if self._status == SessionStatus.RECORDING:
                raise RuntimeError("A recording session is already active")

            sess_id = session_id or f"sess_{uuid.uuid4().hex[:16]}"
            self._current_session_id = sess_id
            self._started_at = started_at or datetime.now(timezone.utc)
            self._environment = environment or Environment(
                os=sys.platform,
                python_version=sys.version.split()[0],
            )
            self._profile = profile or RecordingProfile()
            self._status = SessionStatus.RECORDING
            self._activities = []
            return sess_id

    def register_completed_activity(self, activity: Activity) -> None:
        with self._lock:
            self._activities.append(activity)

    def stop_session(
        self,
        finished_at: datetime | None = None,
        status: SessionStatus = SessionStatus.COMPLETED,
    ) -> RecordingSession:
        with self._lock:
            if self._status != SessionStatus.RECORDING or self._current_session_id is None:
                raise RuntimeError("No active recording session to stop")

            end_time = finished_at or datetime.now(timezone.utc)
            start_time = self._started_at or end_time
            duration_ms = max(0.0, (end_time - start_time).total_seconds() * 1000.0)

            session = RecordingSession(
                session_id=self._current_session_id,
                started_at=start_time,
                finished_at=end_time,
                duration_ms=duration_ms,
                status=status,
                environment=self._environment or Environment(os="unknown", python_version="unknown"),
                profile=self._profile or RecordingProfile(),
                activities=list(self._activities),
            )

            self._status = SessionStatus.STOPPED
            self._current_session_id = None
            self._started_at = None
            return session

    def get_current_session_info(self) -> dict[str, Any] | None:
        with self._lock:
            if not self.is_active or self._current_session_id is None:
                return None
            return {
                "session_id": self._current_session_id,
                "started_at": self._started_at,
                "environment": self._environment,
                "profile": self._profile,
            }
