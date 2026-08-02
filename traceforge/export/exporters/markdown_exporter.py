"""MarkdownExporter producing GitHub-flavored Markdown text."""

from __future__ import annotations

from typing import TYPE_CHECKING

from traceforge.export.base import BaseExporter

if TYPE_CHECKING:
    from traceforge.diff.report import ExecutionDiffReport
    from traceforge.export.config import ExportConfig
    from traceforge.replay.session import ReplaySession


class MarkdownExporter(BaseExporter):
    """Converts ReplaySession and ExecutionDiffReport objects into Markdown."""

    def export_session(self, session: ReplaySession, config: ExportConfig) -> str:
        sess_id = session.session.session_id if session.session else "Unknown"
        lines = [
            f"# TraceForge Replay Session: `{sess_id}`",
            "",
            "## Summary",
            f"- **Activities**: {len(session.activities)}",
            f"- **Nodes**: {len(session.nodes)}",
            f"- **Relationships**: {len(session.relationships)}",
            f"- **Timeline Events**: {len(session.timeline)}",
            "",
            "## Execution Nodes",
            "| Node ID | Name | Type | Status | Duration (ms) |",
            "|---|---|---|---|---|",
        ]
        for n in session.nodes:
            lines.append(f"| `{n.node_id}` | `{n.name}` | `{n.type}` | `{n.status}` | `{n.duration_ms or 0.0:.2f}` |")

        return "\n".join(lines)

    def export_diff_report(self, report: ExecutionDiffReport, config: ExportConfig) -> str:
        lines = [
            "# TraceForge Execution Diff Report",
            "",
            f"- **Baseline Session**: `{report.baseline_session_id}`",
            f"- **Target Session**: `{report.target_session_id}`",
            "",
        ]
        if report.graph_diff:
            lines.extend([
                "## Graph Differences",
                f"- **Added Nodes**: {', '.join(f'`{x}`' for x in report.graph_diff.added_nodes) or 'None'}",
                f"- **Removed Nodes**: {', '.join(f'`{x}`' for x in report.graph_diff.removed_nodes) or 'None'}",
                f"- **Modified Nodes**: {', '.join(f'`{x}`' for x in report.graph_diff.modified_nodes) or 'None'}",
                "",
            ])
        if report.performance_diff:
            lines.extend([
                "## Performance Differences",
                f"- **Baseline Duration**: `{report.performance_diff.baseline_duration_ms}` ms",
                f"- **Target Duration**: `{report.performance_diff.target_duration_ms}` ms",
                f"- **Duration Delta**: `{report.performance_diff.duration_delta_ms}` ms",
                "",
            ])
        return "\n".join(lines)
