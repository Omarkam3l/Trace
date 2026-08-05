"""Unit tests for EventBus publish/subscribe and deterministic ordering."""

from __future__ import annotations

from datetime import UTC, datetime

from traceforge.engine.event_bus import EventBus
from traceforge.engine.raw_event import RawEvent


def test_event_bus_pub_sub_and_unsubscribe():
    bus = EventBus()
    received: list[RawEvent] = []

    def handler(evt: RawEvent):
        received.append(evt)

    unsub = bus.subscribe(handler)

    e1 = RawEvent(event_id="e1", timestamp=datetime.now(UTC), type="Custom")
    bus.publish(e1)
    assert len(received) == 1

    unsub()
    e2 = RawEvent(event_id="e2", timestamp=datetime.now(UTC), type="Custom")
    bus.publish(e2)
    assert len(received) == 1  # Unsubscribed handler received no more events


def test_deterministic_event_ordering_sort_key():
    now = datetime.now(UTC)

    e1 = RawEvent(event_id="evt_a", timestamp=now, sequence=1, type="A")
    e2 = RawEvent(event_id="evt_b", timestamp=now, sequence=1, type="B")
    e3 = RawEvent(event_id="evt_c", timestamp=now, sequence=2, type="C")

    # Sequence key sorting
    events = [e3, e2, e1]
    sorted_events = sorted(events, key=lambda e: (e.timestamp, e.sequence, e.event_id))

    assert [e.event_id for e in sorted_events] == ["evt_a", "evt_b", "evt_c"]
