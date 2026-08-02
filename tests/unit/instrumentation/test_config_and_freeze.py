"""Unit tests for InstrumentationConfig and Configuration Freeze enforcement."""

from __future__ import annotations

import pytest

from traceforge.exceptions import ConfigurationFreezeError
from traceforge.instrumentation.config import InstrumentationConfig
from traceforge.instrumentation.tracer import Tracer


def test_instrumentation_config_immutability():
    config = InstrumentationConfig(sampling_rate=0.8, capture_exceptions=True)
    assert config.sampling_rate == 0.8
    assert config.capture_exceptions is True

    with pytest.raises(Exception):
        config.sampling_rate = 0.5  # Immutability enforcement


def test_configuration_freeze_during_active_session():
    tracer = Tracer()
    assert not tracer.is_recording()

    new_config = InstrumentationConfig(sampling_rate=0.5)
    tracer.configure(new_config)  # Succeeds when session is stopped
    assert tracer.config.sampling_rate == 0.5

    tracer.start_session(name="Test Session")
    assert tracer.is_recording()

    # Reconfiguring active session must raise ConfigurationFreezeError
    with pytest.raises(ConfigurationFreezeError) as exc_info:
        tracer.configure(InstrumentationConfig(sampling_rate=0.1))

    assert "Cannot reconfigure" in str(exc_info.value)
    tracer.stop_session()
