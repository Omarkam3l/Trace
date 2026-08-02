"""Unit tests for SessionManager and RecordingSession lifecycle."""

from __future__ import annotations

import pytest

from traceforge.domain.enums import SessionStatus
from traceforge.domain.environment import Environment
from traceforge.domain.profile import RecordingProfile
from traceforge.engine.session_manager import SessionManager


def test_session_start_and_stop():
    manager = SessionManager()
    assert not manager.is_active

    env = Environment(os="Linux", python_version="3.12")
    profile = RecordingProfile(name="test")

    session_id = manager.start_session(session_id="sess_1", environment=env, profile=profile)
    assert session_id == "sess_1"
    assert manager.is_active

    session = manager.stop_session()
    assert not manager.is_active
    assert session.id == "sess_1"
    assert session.status == SessionStatus.COMPLETED
    assert session.environment.os == "Linux"
    assert session.duration_ms is not None
    assert session.duration_ms >= 0.0


def test_single_active_session_enforcement():
    manager = SessionManager()
    manager.start_session(session_id="sess_1")

    with pytest.raises(RuntimeError) as exc_info:
        manager.start_session(session_id="sess_2")

    assert "already active" in str(exc_info.value)
    manager.stop_session()


def test_stopping_without_active_session_raises():
    manager = SessionManager()
    with pytest.raises(RuntimeError) as exc_info:
        manager.stop_session()

    assert "No active recording session" in str(exc_info.value)
