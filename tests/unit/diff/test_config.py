"""Unit tests for DiffConfig immutability and category selection."""

from __future__ import annotations

from traceforge.diff.config import DiffCategory, DiffConfig


def test_diff_config_defaults_and_categories():
    cfg = DiffConfig()
    assert len(cfg.categories) == 5
    assert cfg.duration_threshold_ms == 10.0

    custom_cfg = DiffConfig(categories={DiffCategory.GRAPH, DiffCategory.PERFORMANCE})
    assert len(custom_cfg.categories) == 2
    assert DiffCategory.GRAPH in custom_cfg.categories
    assert DiffCategory.TIMELINE not in custom_cfg.categories
