"""Tests for HtmlExporter's flamegraph rendering.

Before this fix, HtmlExporter.export_session() produced a static <table>
only, despite FlamegraphViewModel/VisualizationEngine already existing and
being unused here. These tests cover the new rendering, with particular
attention to the CSS percentage-nesting math: since width% on a nested
block resolves against its *immediate* parent's rendered width (not a
global root), each frame's declared percentage must be relative to its own
parent's value, not the tree's total -- getting this wrong silently
under-renders deeply nested frames without raising any error.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime

from traceforge.export.config import ExportConfig
from traceforge.export.exporters.html_exporter import HtmlExporter
from traceforge.replay.session import ReplaySession
from traceforge.storage.records import NodeRecord, SessionRecord


def _session_with_nodes(*nodes: NodeRecord) -> ReplaySession:
    now = datetime.now(UTC)
    sess_rec = SessionRecord(
        session_id="s1",
        started_at=now,
        status="completed",
        environment_os="linux",
        environment_python="3.12",
        profile_name="standard",
    )
    return ReplaySession(session=sess_rec, nodes=list(nodes))


def test_export_session_with_no_nodes_has_no_flamegraph_section():
    session = _session_with_nodes()
    html = HtmlExporter().export_session(session, ExportConfig())
    assert "<!DOCTYPE html>" in html
    assert "<h2>Flamegraph</h2>" not in html
    assert '<div class="flame-frame"' not in html


def test_export_session_renders_flame_frames():
    now = datetime.now(UTC)
    root = NodeRecord(
        node_id="n1",
        graph_id="g1",
        type="function",
        name="checkout",
        started_at=now,
        duration_ms=100.0,
        status="completed",
        child_ids=["n2"],
    )
    child = NodeRecord(
        node_id="n2",
        graph_id="g1",
        type="function",
        name="charge-card",
        started_at=now,
        duration_ms=40.0,
        status="completed",
        parent_id="n1",
    )
    html = HtmlExporter().export_session(_session_with_nodes(root, child), ExportConfig())
    assert html.count('<div class="flame-frame"') == 2
    assert "checkout" in html
    assert "charge-card" in html


def test_failed_node_gets_the_failure_color():
    now = datetime.now(UTC)
    root = NodeRecord(
        node_id="n1",
        graph_id="g1",
        type="function",
        name="checkout",
        started_at=now,
        duration_ms=100.0,
        status="failed",
        child_ids=[],
    )
    html = HtmlExporter().export_session(_session_with_nodes(root), ExportConfig())
    assert "#ef4444" in html  # _FAILED_COLOR


def test_node_name_is_html_escaped():
    """XSS safety: a span/function name is arbitrary user/application data

    and must not be interpretable as HTML in the exported report.
    """
    now = datetime.now(UTC)
    root = NodeRecord(
        node_id="n1",
        graph_id="g1",
        type="function",
        name="<script>alert(1)</script>",
        started_at=now,
        duration_ms=10.0,
        status="completed",
        child_ids=[],
    )
    html = HtmlExporter().export_session(_session_with_nodes(root), ExportConfig())
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_node_table_also_escapes_names_pre_existing_bug():
    """Regression test for a pre-existing (unrelated to the flamegraph

    change) bug: the plain <table> rows never escaped node_id/name/type/
    status, so the same malicious name would also break out of the table
    even with no flamegraph involved.
    """
    now = datetime.now(UTC)
    root = NodeRecord(
        node_id="n1",
        graph_id="g1",
        type="function",
        name='"><img src=x onerror=alert(1)>',
        started_at=now,
        duration_ms=10.0,
        status="completed",
        child_ids=[],
    )
    html = HtmlExporter().export_session(_session_with_nodes(root), ExportConfig())
    assert "<img src=x onerror=alert(1)>" not in html
    assert "&lt;img" in html


def _extract_width_pct(html: str, node_id_marker: str) -> float:
    """Find the flame-frame div containing node_id_marker in its tooltip and

    return its declared width percentage.
    """
    pattern = rf'style="background:[^"]+;width:([\d.]+)%"[^>]*title="{re.escape(node_id_marker)}[^"]*"'
    match = re.search(pattern, html)
    assert match, f"could not find frame for {node_id_marker!r} in HTML"
    return float(match.group(1))


def test_nested_percentages_compound_correctly_when_multiplied():
    """The core correctness check for the CSS-nesting approach: each frame's

    declared width% must be relative to its immediate parent's value. When you
    multiply the percentages down the chain (mirroring how a browser actually
    resolves nested percentage widths), the result must equal the node's true
    proportion of the root's total duration.

    root: 200ms
      -> mid: 100ms   (50% of root)
           -> leaf: 25ms  (25% of mid)

    True proportion of leaf relative to root: 25/200 = 12.5%.
    If leaf's declared % were (wrongly) computed against the root total
    instead of its parent, this compounding check would fail.
    """
    now = datetime.now(UTC)
    root = NodeRecord(
        node_id="n1",
        graph_id="g1",
        type="function",
        name="root-frame",
        started_at=now,
        duration_ms=200.0,
        status="completed",
        child_ids=["n2"],
    )
    mid = NodeRecord(
        node_id="n2",
        graph_id="g1",
        type="function",
        name="mid-frame",
        started_at=now,
        duration_ms=100.0,
        status="completed",
        parent_id="n1",
        child_ids=["n3"],
    )
    leaf = NodeRecord(
        node_id="n3",
        graph_id="g1",
        type="function",
        name="leaf-frame",
        started_at=now,
        duration_ms=25.0,
        status="completed",
        parent_id="n2",
    )
    html = HtmlExporter().export_session(_session_with_nodes(root, mid, leaf), ExportConfig())

    root_pct = _extract_width_pct(html, "root-frame")
    mid_pct = _extract_width_pct(html, "mid-frame")
    leaf_pct = _extract_width_pct(html, "leaf-frame")

    assert abs(root_pct - 100.0) < 0.01
    assert abs(mid_pct - 50.0) < 0.01  # 100/200
    assert abs(leaf_pct - 25.0) < 0.01  # 25/100, relative to its parent (mid), not root

    # The actual check that matters: multiply the chain the way a browser
    # would (each % relative to the previous level's already-scaled width)
    # and confirm it equals the true global proportion.
    compounded = (root_pct / 100) * (mid_pct / 100) * (leaf_pct / 100) * 100
    true_proportion = leaf.duration_ms / root.duration_ms * 100
    assert abs(compounded - true_proportion) < 0.01
