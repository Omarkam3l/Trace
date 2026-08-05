"""ExecutionDiffEngine public facade for Phase 9 Execution Diff Engine."""

from __future__ import annotations

import threading
from datetime import UTC, datetime

from traceforge.diff.comparators.exception import ExceptionDiffComparator
from traceforge.diff.comparators.graph import GraphDiffComparator
from traceforge.diff.comparators.metadata import MetadataDiffComparator
from traceforge.diff.comparators.performance import PerformanceDiffComparator
from traceforge.diff.comparators.timeline import TimelineDiffComparator
from traceforge.diff.config import DiffCategory, DiffConfig
from traceforge.diff.exceptions import DiffValidationError
from traceforge.diff.report import ExecutionDiffReport
from traceforge.replay.session import ReplaySession


class ExecutionDiffEngine:
    """Public facade for comparing two ReplaySession objects deterministically."""

    def __init__(self) -> None:
        self._graph_comp = GraphDiffComparator()
        self._timeline_comp = TimelineDiffComparator()
        self._perf_comp = PerformanceDiffComparator()
        self._exc_comp = ExceptionDiffComparator()
        self._meta_comp = MetadataDiffComparator()
        self._lock = threading.RLock()

    def compare(
        self,
        baseline: ReplaySession,
        target: ReplaySession,
        config: DiffConfig | None = None,
    ) -> ExecutionDiffReport:
        """Compare baseline and target ReplaySessions and generate an ExecutionDiffReport."""
        if not baseline.session or not target.session:
            raise DiffValidationError(
                "Baseline and target ReplaySessions must contain non-null SessionRecord instances"
            )

        cfg = config or DiffConfig()
        with self._lock:
            graph_diff = self._graph_comp.compare(baseline, target) if DiffCategory.GRAPH in cfg.categories else None
            timeline_diff = (
                self._timeline_comp.compare(baseline, target) if DiffCategory.TIMELINE in cfg.categories else None
            )
            perf_diff = (
                self._perf_comp.compare(baseline, target, cfg) if DiffCategory.PERFORMANCE in cfg.categories else None
            )
            exc_diff = self._exc_comp.compare(baseline, target) if DiffCategory.EXCEPTION in cfg.categories else None
            meta_diff = self._meta_comp.compare(baseline, target) if DiffCategory.METADATA in cfg.categories else None

            return ExecutionDiffReport(
                baseline_session_id=baseline.session.session_id,
                target_session_id=target.session.session_id,
                timestamp=datetime.now(UTC),
                graph_diff=graph_diff,
                timeline_diff=timeline_diff,
                performance_diff=perf_diff,
                exception_diff=exc_diff,
                metadata_diff=meta_diff,
            )
