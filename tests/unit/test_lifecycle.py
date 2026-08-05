"""Unit tests for traceforge.core.lifecycle.LifecycleManager."""

from __future__ import annotations

from datetime import UTC

from traceforge.core.lifecycle import LifecycleManager
from traceforge.models.enums import SpanKind, SpanStatus
from traceforge.models.span import SpanModel


def make_span_model() -> SpanModel:
    from datetime import datetime

    return SpanModel(
        id="s1",
        trace_id="t1",
        name="x",
        kind=SpanKind.INTERNAL,
        status=SpanStatus.UNSET,
        start_time=datetime.now(UTC),
    )


def test_register_and_notify():
    manager = LifecycleManager()
    events = []
    manager.register(
        type(
            "H",
            (),
            {
                "on_span_start": lambda self, s: events.append(("start", s.id)),
                "on_span_end": lambda self, s: events.append(("end", s.id)),
            },
        )()
    )
    span = make_span_model()
    manager.notify_start(span)
    manager.notify_end(span)
    assert events == [("start", "s1"), ("end", "s1")]


def test_unregister_stops_notifications():
    manager = LifecycleManager()
    calls = []

    class Hook:
        def on_span_start(self, s):
            calls.append(s.id)

        def on_span_end(self, s):
            pass

    hook = Hook()
    manager.register(hook)
    manager.unregister(hook)
    manager.notify_start(make_span_model())
    assert calls == []


def test_a_broken_hook_does_not_prevent_others_from_running():
    manager = LifecycleManager()
    calls = []

    class Broken:
        def on_span_start(self, s):
            raise RuntimeError("boom")

        def on_span_end(self, s):
            pass

    class Fine:
        def on_span_start(self, s):
            calls.append(s.id)

        def on_span_end(self, s):
            pass

    manager.register(Broken())
    manager.register(Fine())
    manager.notify_start(make_span_model())  # must not raise
    assert calls == ["s1"]
