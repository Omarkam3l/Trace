"""DiffAdapter converting ExecutionDiffReport to DiffViewModel."""

from __future__ import annotations

from typing import TYPE_CHECKING

from traceforge.visualization.models.diff import DiffViewModel

if TYPE_CHECKING:
    from traceforge.diff.report import ExecutionDiffReport
    from traceforge.visualization.config import VisualizationConfig


class DiffAdapter:
    """Transforms ExecutionDiffReport artifacts into UI-ready DiffViewModel objects."""

    def adapt(self, report: ExecutionDiffReport, config: VisualizationConfig) -> DiffViewModel:
        """Convert diff report into DiffViewModel summary."""
        summary = {
            "timestamp": report.timestamp.isoformat(),
            "added_nodes_count": len(report.graph_diff.added_nodes) if report.graph_diff else 0,
            "removed_nodes_count": len(report.graph_diff.removed_nodes) if report.graph_diff else 0,
            "modified_nodes_count": len(report.graph_diff.modified_nodes) if report.graph_diff else 0,
            "duration_delta_ms": report.performance_diff.duration_delta_ms if report.performance_diff else None,
        }

        return DiffViewModel(
            baseline_id=report.baseline_session_id,
            target_id=report.target_session_id,
            summary=summary,
        )
