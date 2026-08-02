"""MermaidExporter converting execution graphs to Mermaid flowchart syntax."""

from __future__ import annotations

from typing import TYPE_CHECKING

from traceforge.export.base import BaseExporter

if TYPE_CHECKING:
    from traceforge.diff.report import ExecutionDiffReport
    from traceforge.export.config import ExportConfig
    from traceforge.replay.session import ReplaySession


class MermaidExporter(BaseExporter):
    """Converts ReplaySession execution graphs into Mermaid flowchart code."""

    def export_session(self, session: ReplaySession, config: ExportConfig) -> str:
        lines = ["flowchart TD"]
        for node in session.nodes:
            lines.append(f'    {node.node_id}["{node.name} ({node.type})"]')

        for rel in session.relationships:
            lines.append(f"    {rel.source_node_id} -->|{rel.type}| {rel.target_node_id}")

        return "\n".join(lines)

    def export_diff_report(self, report: ExecutionDiffReport, config: ExportConfig) -> str:
        lines = ["flowchart TD"]
        if report.graph_diff:
            for added in report.graph_diff.added_nodes:
                lines.append(f'    added_{added}["+ {added}"]')
            for removed in report.graph_diff.removed_nodes:
                lines.append(f'    removed_{removed}["- {removed}"]')
            for modified in report.graph_diff.modified_nodes:
                lines.append(f'    modified_{modified}["~ {modified}"]')
        return "\n".join(lines)
