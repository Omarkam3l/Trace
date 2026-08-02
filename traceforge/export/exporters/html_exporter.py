"""HtmlExporter generating self-contained HTML reports with modern CSS styling."""

from __future__ import annotations

from typing import TYPE_CHECKING

from traceforge.export.base import BaseExporter

if TYPE_CHECKING:
    from traceforge.diff.report import ExecutionDiffReport
    from traceforge.export.config import ExportConfig
    from traceforge.replay.session import ReplaySession


class HtmlExporter(BaseExporter):
    """Generates standalone HTML reports for ReplaySession and ExecutionDiffReport objects."""

    def export_session(self, session: ReplaySession, config: ExportConfig) -> str:
        sess_id = session.session.session_id if session.session else "Unknown"
        nodes_rows = "".join(
            f"<tr><td>{n.node_id}</td><td>{n.name}</td><td>{n.type}</td><td>{n.status}</td><td>{n.duration_ms or 0.0:.2f} ms</td></tr>"
            for n in session.nodes
        )

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>TraceForge Replay Session - {sess_id}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 2rem; }}
        h1 {{ color: #38bdf8; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(10px); border-radius: 8px; overflow: hidden; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #334155; }}
        th {{ background: #1e293b; color: #94a3b8; }}
    </style>
</head>
<body>
    <h1>TraceForge Execution Report: {sess_id}</h1>
    <h2>Nodes ({len(session.nodes)})</h2>
    <table>
        <thead><tr><th>Node ID</th><th>Name</th><th>Type</th><th>Status</th><th>Duration</th></tr></thead>
        <tbody>{nodes_rows}</tbody>
    </table>
</body>
</html>"""

    def export_diff_report(self, report: ExecutionDiffReport, config: ExportConfig) -> str:
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>TraceForge Diff Report - {report.baseline_session_id} vs {report.target_session_id}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 2rem; }}
        h1 {{ color: #38bdf8; }}
    </style>
</head>
<body>
    <h1>TraceForge Execution Diff Report</h1>
    <p>Baseline: {report.baseline_session_id} | Target: {report.target_session_id}</p>
</body>
</html>"""
