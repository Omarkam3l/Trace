"""VisualizationEngine public facade for Phase 11 Visualization Data Adapter Layer."""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

from traceforge.visualization.adapters.diff_adapter import DiffAdapter
from traceforge.visualization.adapters.flamegraph_adapter import FlamegraphAdapter
from traceforge.visualization.adapters.graph_adapter import GraphAdapter
from traceforge.visualization.adapters.timeline_adapter import TimelineAdapter
from traceforge.visualization.config import VisualizationConfig

if TYPE_CHECKING:
    from traceforge.diff.report import ExecutionDiffReport
    from traceforge.replay.session import ReplaySession
    from traceforge.visualization.models.diff import DiffViewModel
    from traceforge.visualization.models.flamegraph import FlamegraphViewModel
    from traceforge.visualization.models.graph import GraphViewModel
    from traceforge.visualization.models.timeline import TimelineViewModel


class VisualizationEngine:
    """Public facade converting execution artifacts into frontend-ready view models."""

    def __init__(self) -> None:
        self._graph_adapter = GraphAdapter()
        self._timeline_adapter = TimelineAdapter()
        self._flamegraph_adapter = FlamegraphAdapter()
        self._diff_adapter = DiffAdapter()
        self._lock = threading.RLock()

    def to_graph_model(self, session: ReplaySession, config: VisualizationConfig | None = None) -> GraphViewModel:
        """Convert a ReplaySession to a GraphViewModel."""
        cfg = config or VisualizationConfig()
        with self._lock:
            return self._graph_adapter.adapt(session, cfg)

    def to_timeline_model(self, session: ReplaySession, config: VisualizationConfig | None = None) -> TimelineViewModel:
        """Convert a ReplaySession to a TimelineViewModel."""
        cfg = config or VisualizationConfig()
        with self._lock:
            return self._timeline_adapter.adapt(session, cfg)

    def to_flamegraph_model(self, session: ReplaySession, config: VisualizationConfig | None = None) -> FlamegraphViewModel:
        """Convert a ReplaySession to a FlamegraphViewModel."""
        cfg = config or VisualizationConfig()
        with self._lock:
            return self._flamegraph_adapter.adapt(session, cfg)

    def to_diff_model(self, report: ExecutionDiffReport, config: VisualizationConfig | None = None) -> DiffViewModel:
        """Convert an ExecutionDiffReport to a DiffViewModel."""
        cfg = config or VisualizationConfig()
        with self._lock:
            return self._diff_adapter.adapt(report, cfg)
