"""Unit tests for ActivityManager and Activity lifecycle."""

from __future__ import annotations

import pytest

from traceforge.domain.enums import ActivityStatus
from traceforge.engine.activity_manager import ActivityManager


def test_activity_lifecycle_and_stack():
    manager = ActivityManager()
    assert manager.get_current_activity_record() is None

    act1_id = manager.start_activity(session_id="sess_1", name="Checkout")
    assert manager.get_current_activity_record().activity_id == act1_id

    # Nested activity
    act2_id = manager.start_activity(session_id="sess_1", name="Process Payment")
    assert manager.get_current_activity_record().activity_id == act2_id

    completed_act2 = manager.finish_activity()
    assert completed_act2.id == act2_id
    assert completed_act2.name == "Process Payment"
    assert completed_act2.status == ActivityStatus.COMPLETED

    assert manager.get_current_activity_record().activity_id == act1_id
    completed_act1 = manager.finish_activity()
    assert completed_act1.id == act1_id
    assert completed_act1.name == "Checkout"

    assert manager.get_current_activity_record() is None


def test_finishing_activity_without_active_raises():
    manager = ActivityManager()
    with pytest.raises(RuntimeError):
        manager.finish_activity()
