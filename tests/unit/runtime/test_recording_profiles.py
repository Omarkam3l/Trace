"""Unit tests for Recording Profiles configuration."""

from __future__ import annotations

from traceforge.runtime.config import RuntimeConfig
from traceforge.runtime.enums import ProfileType


def test_recording_profile_configuration():
    cfg_minimal = RuntimeConfig(profile=ProfileType.MINIMAL)
    assert cfg_minimal.profile == ProfileType.MINIMAL
    assert not cfg_minimal.capture_variables

    cfg_debug = RuntimeConfig(profile=ProfileType.DEEP_DEBUG, capture_variables=True, capture_locals=True)
    assert cfg_debug.profile == ProfileType.DEEP_DEBUG
    assert cfg_debug.capture_variables is True
    assert cfg_debug.capture_locals is True
