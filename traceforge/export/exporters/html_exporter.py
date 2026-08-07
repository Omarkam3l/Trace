"""HtmlExporter generating self-contained HTML reports with modern CSS styling."""

from __future__ import annotations

import html as _html
from typing import TYPE_CHECKING

from traceforge.export.base import BaseExporter
from traceforge.visualization.engine import VisualizationEngine

if TYPE_CHECKING:
    from traceforge.diff.report import ExecutionDiffReport
    from traceforge.export.config import ExportConfig
    from traceforge.replay.session import ReplaySession
    from traceforge.visualization.models.flamegraph import FlamegraphSpanModel

# Depth-based warm palette, same family used by the gateway dashboard's
# flamegraph view (traceforge/gateway/static/index.html) for visual
# consistency between the live dashboard and this offline export.
_DEPTH_COLORS = ["#f97316", "#fb923c", "#fbbf24", "#facc15", "#a3e635", "#4ade80"]
_FAILED_COLOR = "#ef4444"


def _render_flamegraph_frame(
    node: FlamegraphSpanModel,
    depth: int,
    parent_value: float,
    status_by_name: dict[str, str],
) -> str:
    """Recursively render one flamegraph frame and its children as nested
    HTML/CSS bars. Rendered server-side (no JS/fetch) since this is a
    standalone, offline export file -- unlike the live dashboard, there's
    no backend to call.

    Each frame's CSS width% is computed relative to its immediate parent's
    value, not the global root total. CSS resolves nested percentage widths
    against the immediate containing block, so the browser naturally
    compounds these per-level percentages into the correct proportion
    relative to the root -- computing every level's percentage against the
    root directly would double-scale everything below the first level.
    """
    width_pct = (node.value / parent_value * 100) if parent_value > 0 else 0
    status = status_by_name.get(node.name)
    color = _FAILED_COLOR if status == "failed" else _DEPTH_COLORS[depth % len(_DEPTH_COLORS)]
    name = _html.escape(node.name)
    tooltip = _html.escape(f"{node.name} — {node.value:.2f} ms" + (f" ({status})" if status else ""))

    children_html = "".join(
        _render_flamegraph_frame(child, depth + 1, max(node.value, 0.0001), status_by_name) for child in node.children
    )

    return f"""<div class="flame-frame" style="background:{color};width:{width_pct:.4f}%" title="{tooltip}">
    <span class="flame-label">{name}</span>
    {f'<div class="flame-children">{children_html}</div>' if children_html else ""}
</div>"""


class HtmlExporter(BaseExporter):
    """Generates standalone HTML reports for ReplaySession and ExecutionDiffReport objects."""

    def export_session(self, session: ReplaySession, config: ExportConfig) -> str:
        sess_id = _html.escape(session.session.session_id if session.session else "Unknown")
        nodes_rows = "".join(
            f"<tr><td>{_html.escape(n.node_id)}</td><td>{_html.escape(n.name)}</td>"
            f"<td>{_html.escape(n.type)}</td><td>{_html.escape(n.status)}</td>"
            f"<td>{n.duration_ms or 0.0:.2f} ms</td></tr>"
            for n in session.nodes
        )

        flamegraph_html = ""
        flamegraph_model = VisualizationEngine().to_flamegraph_model(session)
        if flamegraph_model.root is not None:
            # Best-effort status lookup by name for color-coding failed
            # frames. FlamegraphSpanModel doesn't carry node_id, only name,
            # so this can mis-color if the same function name recurses or
            # repeats at different points in the tree with different
            # outcomes -- acceptable for a visual report, not used for any
            # correctness-sensitive decision.
            status_by_name = {n.name: n.status for n in session.nodes}
            root = flamegraph_model.root
            flamegraph_html = f"""
    <h2>Flamegraph</h2>
    <div class="flamegraph-container">
        {_render_flamegraph_frame(root, 0, max(root.value, 0.0001), status_by_name)}
    </div>"""

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
        .flamegraph-container {{ margin-top: 1rem; }}
        .flame-frame {{
            display: block;
            box-sizing: border-box;
            border: 1px solid #0f172a;
            border-radius: 3px;
            color: #0f172a;
            font-size: 12px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            padding: 3px 6px;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
            cursor: default;
        }}
        .flame-label {{ font-weight: 600; }}
        .flame-children {{ display: flex; width: 100%; margin-top: 2px; }}
        .flame-children .flame-frame {{ flex-shrink: 0; }}
    </style>
</head>
<body>
    <h1>TraceForge Execution Report: {sess_id}</h1>
    {flamegraph_html}
    <h2>Nodes ({len(session.nodes)})</h2>
    <table>
        <thead><tr><th>Node ID</th><th>Name</th><th>Type</th><th>Status</th><th>Duration</th></tr></thead>
        <tbody>{nodes_rows}</tbody>
    </table>
</body>
</html>"""

    def export_diff_report(self, report: ExecutionDiffReport, config: ExportConfig) -> str:
        baseline_id = _html.escape(report.baseline_session_id)
        target_id = _html.escape(report.target_session_id)
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>TraceForge Diff Report - {baseline_id} vs {target_id}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 2rem; }}
        h1 {{ color: #38bdf8; }}
    </style>
</head>
<body>
    <h1>TraceForge Execution Diff Report</h1>
    <p>Baseline: {baseline_id} | Target: {target_id}</p>
</body>
</html>"""
