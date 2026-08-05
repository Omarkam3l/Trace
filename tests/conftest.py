"""Shared pytest fixtures for the TraceForge test suite."""

from __future__ import annotations

from pathlib import Path

import pytest

from traceforge.core.clock import FrozenClock
from traceforge.core.context import ContextManager
from traceforge.core.tracer import Tracer
from traceforge.storage.memory import MemoryStorage


@pytest.fixture(autouse=True)
def _reset_context():
    """Ensure no test leaks execution context into another."""
    token = ContextManager.clear()
    yield
    ContextManager.reset(token)


@pytest.fixture(autouse=True)
def _reset_default_tracer():
    from traceforge.api.functions import reset_default_tracer

    reset_default_tracer()
    yield
    reset_default_tracer()


@pytest.fixture
def frozen_clock() -> FrozenClock:
    return FrozenClock()


@pytest.fixture
def tracer(frozen_clock: FrozenClock) -> Tracer:
    return Tracer("test-service", clock=frozen_clock)


@pytest.fixture
def memory_storage() -> MemoryStorage:
    return MemoryStorage()


@pytest.fixture
def tmp_jsonl_path(tmp_path: Path) -> Path:
    return tmp_path / "spans.jsonl"


@pytest.fixture
def tmp_sqlite_path(tmp_path: Path) -> Path:
    return tmp_path / "spans.db"
