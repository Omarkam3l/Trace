"""Unit tests for traceforge.api.decorators.traced."""

from __future__ import annotations

import pytest

from traceforge.api.decorators import traced
from traceforge.core.lifecycle import SpanLifecycleHook
from traceforge.models.enums import SpanStatus
from traceforge.models.span import SpanModel


class RecordingHook(SpanLifecycleHook):
    def __init__(self):
        self.ended: list[SpanModel] = []

    def on_span_start(self, span):
        pass

    def on_span_end(self, span):
        self.ended.append(span)


def test_traced_sync_function_creates_span(tracer):
    hook = RecordingHook()
    tracer.add_hook(hook)

    @traced(tracer=tracer)
    def add(a, b):
        return a + b

    assert add(1, 2) == 3
    assert len(hook.ended) == 1
    assert hook.ended[0].name == "test_traced_sync_function_creates_span.<locals>.add"


async def test_traced_async_function_creates_span(tracer):
    hook = RecordingHook()
    tracer.add_hook(hook)

    @traced(name="custom-name", tracer=tracer)
    async def fetch():
        return 42

    assert await fetch() == 42
    assert hook.ended[0].name == "custom-name"


def test_traced_captures_exceptions(tracer):
    hook = RecordingHook()
    tracer.add_hook(hook)

    @traced(tracer=tracer)
    def fails():
        raise RuntimeError("nope")

    with pytest.raises(RuntimeError):
        fails()
    assert hook.ended[0].status is SpanStatus.ERROR


def test_traced_preserves_function_metadata(tracer):
    @traced(tracer=tracer)
    def documented():
        """A docstring."""
        return None

    assert documented.__name__ == "documented"
    assert documented.__doc__ == "A docstring."


def test_traced_uses_default_tracer_when_none_given(tracer):
    import traceforge

    traceforge.configure(tracer)
    hook = RecordingHook()
    tracer.add_hook(hook)

    @traced()
    def work():
        return "ok"

    assert work() == "ok"
    assert len(hook.ended) == 1


def test_traced_captures_return_value(tracer):
    hook = RecordingHook()
    tracer.add_hook(hook)

    @traced(tracer=tracer)
    def multiply(a, b):
        return a * b

    assert multiply(3, 4) == 12
    assert hook.ended[0].attributes.get("result") == 12


async def test_traced_async_captures_return_value(tracer):
    hook = RecordingHook()
    tracer.add_hook(hook)

    @traced(tracer=tracer)
    async def get_data():
        return {"status": "ok"}

    res = await get_data()
    assert res == {"status": "ok"}
    assert hook.ended[0].attributes.get("result") == {"status": "ok"}


def test_traced_can_disable_return_value_capture(tracer):
    hook = RecordingHook()
    tracer.add_hook(hook)

    @traced(tracer=tracer, capture_return=False)
    def secret():
        return "sensitive"

    assert secret() == "sensitive"
    assert "result" not in hook.ended[0].attributes

