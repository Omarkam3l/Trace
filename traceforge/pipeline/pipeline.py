"""ExecutionPipeline: decoupled artifact pipeline manager."""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

from traceforge.pipeline.consumer import ExecutionConsumer
from traceforge.pipeline.dispatcher import PipelineDispatcher
from traceforge.pipeline.exceptions import ConsumerRegistrationError
from traceforge.pipeline.stats import PipelineStatistics, PipelineStatsSnapshot

if TYPE_CHECKING:
    from traceforge.domain.activity import Activity
    from traceforge.domain.graph import ExecutionGraph
    from traceforge.domain.session import RecordingSession


class ExecutionPipeline:
    """Decoupled pipeline manager linking execution recording to downstream consumers."""

    def __init__(self) -> None:
        self._consumers: list[ExecutionConsumer] = []
        self._consumer_map: dict[str, ExecutionConsumer] = {}
        self._stats = PipelineStatistics()
        self._dispatcher = PipelineDispatcher(self._stats)
        self._shutdown: bool = False
        self._lock = threading.RLock()

    @property
    def is_shutdown(self) -> bool:
        with self._lock:
            return self._shutdown

    def register_consumer(self, consumer: ExecutionConsumer) -> None:
        """Register an ExecutionConsumer with the pipeline."""
        with self._lock:
            if self._shutdown:
                raise ConsumerRegistrationError("Cannot register consumer on shutdown ExecutionPipeline")

            cid = consumer.consumer_id
            if cid in self._consumer_map:
                raise ConsumerRegistrationError(f"Consumer with ID {cid!r} is already registered")

            self._consumers.append(consumer)
            self._consumer_map[cid] = consumer
            self._update_stats_active_count()

    def unregister_consumer(self, consumer_id_or_name: str) -> ExecutionConsumer | None:
        """Unregister a consumer by ID or name."""
        with self._lock:
            consumer = self._consumer_map.pop(consumer_id_or_name, None)
            if consumer is None:
                # Fallback search by name
                for c in self._consumers:
                    if c.name == consumer_id_or_name:
                        consumer = c
                        self._consumer_map.pop(c.consumer_id, None)
                        break

            if consumer and consumer in self._consumers:
                self._consumers.remove(consumer)

            self._update_stats_active_count()
            return consumer

    def enable_consumer(self, consumer_id_or_name: str) -> bool:
        """Enable a registered consumer."""
        with self._lock:
            consumer = self._get_consumer(consumer_id_or_name)
            if consumer:
                consumer.enable()
                self._update_stats_active_count()
                return True
            return False

    def disable_consumer(self, consumer_id_or_name: str) -> bool:
        """Disable a registered consumer."""
        with self._lock:
            consumer = self._get_consumer(consumer_id_or_name)
            if consumer:
                consumer.disable()
                self._update_stats_active_count()
                return True
            return False

    def publish_session(self, session: RecordingSession) -> None:
        """Publish completed RecordingSession artifact to pipeline consumers."""
        with self._lock:
            if self._shutdown:
                return
            consumers_snapshot = list(self._consumers)

        self._dispatcher.dispatch_session(session, consumers_snapshot)

    def publish_activity(self, activity: Activity) -> None:
        """Publish completed Activity artifact to pipeline consumers."""
        with self._lock:
            if self._shutdown:
                return
            consumers_snapshot = list(self._consumers)

        self._dispatcher.dispatch_activity(activity, consumers_snapshot)

    def publish_graph(self, graph: ExecutionGraph) -> None:
        """Publish completed ExecutionGraph artifact to pipeline consumers."""
        with self._lock:
            if self._shutdown:
                return
            consumers_snapshot = list(self._consumers)

        self._dispatcher.dispatch_graph(graph, consumers_snapshot)

    def get_statistics(self) -> PipelineStatsSnapshot:
        """Return snapshot of pipeline statistics."""
        return self._stats.snapshot()

    def shutdown(self) -> None:
        """Shutdown the pipeline and disable all consumers."""
        with self._lock:
            self._shutdown = True
            for consumer in self._consumers:
                try:
                    consumer.disable()
                except Exception:
                    pass
            self._consumers.clear()
            self._consumer_map.clear()
            self._update_stats_active_count()

    def _get_consumer(self, identifier: str) -> ExecutionConsumer | None:
        if identifier in self._consumer_map:
            return self._consumer_map[identifier]
        for c in self._consumers:
            if c.name == identifier:
                return c
        return None

    def _update_stats_active_count(self) -> None:
        active_count = sum(1 for c in self._consumers if c.is_enabled)
        self._stats.set_active_consumers_count(active_count)
