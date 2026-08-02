"""RawEventRepository: append-only repository for RawEvent persistence."""

from __future__ import annotations

import json
import threading
from typing import TYPE_CHECKING

from traceforge.storage.records.raw_event_record import RawEventRecord

if TYPE_CHECKING:
    from traceforge.engine.raw_event import RawEvent
    from traceforge.storage.drivers.base import StorageDriver


class RawEventRepository:
    """Thread-safe append-only repository for persisting RawEvent instances."""

    def __init__(self, driver: StorageDriver) -> None:
        self._driver = driver
        self._lock = threading.RLock()

    def append_raw_events(self, events: list[RawEvent]) -> list[RawEventRecord]:
        """Convert RawEvent list to RawEventRecord instances and append to storage."""
        records: list[RawEventRecord] = []
        for event in events:
            rec = RawEventRecord(
                event_id=event.event_id,
                timestamp=event.timestamp,
                sequence=event.sequence,
                type=str(event.type),
                source=str(event.source),
                payload_json=json.dumps(event.payload),
                context_id=event.context_id,
                activity_hint=event.activity_hint,
                metadata_json=json.dumps(event.metadata),
            )
            records.append(rec)

        with self._lock:
            self._driver.write_batch(records)
        return records
