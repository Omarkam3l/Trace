"""Unit tests for DiffAdapter."""

from __future__ import annotations

from datetime import UTC, datetime

from traceforge.diff.report import ExecutionDiffReport, NodeGraphDiff
from traceforge.visualization.adapters.diff_adapter import DiffAdapter
from traceforge.visualization.config import VisualizationConfig


def test_diff_adapter():
    now = datetime.now(UTC)
    report = ExecutionDiffReport(
        baseline_session_id="s1",
        target_session_id="s2",
        timestamp=now,
        graph_diff=NodeGraphDiff(added_nodes=["n1"], removed_nodes=["n2"]),
    )

    adapter = DiffAdapter()
    vm = adapter.adapt(report, VisualizationConfig())

    assert vm.baseline_id == "s1"
    assert vm.target_id == "s2"
    assert vm.summary["added_nodes_count"] == 1
    assert vm.summary["removed_nodes_count"] == 1
