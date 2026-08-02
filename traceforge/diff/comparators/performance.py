"""PerformanceDiffComparator for timing deltas and bottleneck analysis."""

from __future__ import annotations

from typing import TYPE_CHECKING

from traceforge.diff.report import PerformanceDiff

if TYPE_CHECKING:
    from traceforge.diff.config import DiffConfig
    from traceforge.replay.session import ReplaySession


class PerformanceDiffComparator:
    """Compares timing metrics and calculates latency regressions."""

    def compare(self, baseline: ReplaySession, target: ReplaySession, config: DiffConfig) -> PerformanceDiff:
        """Calculate duration deltas and flag latency regressions exceeding threshold."""
        base_dur = baseline.session.duration_ms if baseline.session else None
        target_dur = target.session.duration_ms if target.session else None

        duration_delta = (target_dur - base_dur) if (base_dur is not None and target_dur is not None) else None

        base_node_durations = {n.name: n.duration_ms for n in baseline.nodes if n.duration_ms is not None}
        target_node_durations = {n.name: n.duration_ms for n in target.nodes if n.duration_ms is not None}

        slow_nodes: list[tuple[str, float]] = []
        for name, t_dur in sorted(target_node_durations.items()):
            b_dur = base_node_durations.get(name)
            if b_dur is not None:
                delta = t_dur - b_dur
                if delta >= config.duration_threshold_ms:
                    slow_nodes.append((name, delta))

        return PerformanceDiff(
            baseline_duration_ms=base_dur,
            target_duration_ms=target_dur,
            duration_delta_ms=duration_delta,
            slow_nodes=slow_nodes,
        )
