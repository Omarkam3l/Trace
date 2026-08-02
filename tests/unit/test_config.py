"""Unit tests for traceforge.config."""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from traceforge.config.loader import load_from_file, load_settings
from traceforge.config.settings import TraceForgeSettings


def test_defaults():
    settings = TraceForgeSettings()
    assert settings.service_name == "traceforge-service"
    assert settings.storage_backend == "memory"
    assert settings.enabled is True


def test_jsonl_backend_requires_storage_path():
    with pytest.raises(ValidationError):
        TraceForgeSettings(storage_backend="jsonl")
    settings = TraceForgeSettings(storage_backend="jsonl", storage_path="./x.jsonl")
    assert settings.storage_path == "./x.jsonl"


def test_sampling_rate_bounds():
    with pytest.raises(ValidationError):
        TraceForgeSettings(sampling_rate=1.5)
    with pytest.raises(ValidationError):
        TraceForgeSettings(sampling_rate=-0.1)


def test_batch_size_must_be_positive():
    with pytest.raises(ValidationError):
        TraceForgeSettings(batch_size=0)


def test_load_settings_from_env(monkeypatch):
    monkeypatch.setenv("TRACEFORGE_SERVICE_NAME", "env-service")
    monkeypatch.setenv("TRACEFORGE_BATCH_SIZE", "99")
    settings = load_settings()
    assert settings.service_name == "env-service"
    assert settings.batch_size == 99


def test_load_from_file(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"service_name": "file-service", "sampling_rate": 0.5}))
    settings = load_from_file(path)
    assert settings.service_name == "file-service"
    assert settings.sampling_rate == 0.5
