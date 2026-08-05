"""ExportEngine public facade for Phase 10 Export & Artifact System."""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

from traceforge.export.config import ExportConfig, ExportFormat
from traceforge.export.exceptions import ExporterNotFoundError
from traceforge.export.exporters.html_exporter import HtmlExporter
from traceforge.export.exporters.json_exporter import JsonExporter
from traceforge.export.exporters.markdown_exporter import MarkdownExporter
from traceforge.export.exporters.mermaid_exporter import MermaidExporter

if TYPE_CHECKING:
    from traceforge.diff.report import ExecutionDiffReport
    from traceforge.export.base import BaseExporter
    from traceforge.replay.session import ReplaySession


class ExportEngine:
    """Public facade for converting execution artifacts into formatted external representations."""

    def __init__(self) -> None:
        self._exporters: dict[ExportFormat, BaseExporter] = {
            ExportFormat.JSON: JsonExporter(),
            ExportFormat.MERMAID: MermaidExporter(),
            ExportFormat.HTML: HtmlExporter(),
            ExportFormat.MARKDOWN: MarkdownExporter(),
        }
        self._lock = threading.RLock()

    def register_exporter(self, fmt: ExportFormat, exporter: BaseExporter) -> None:
        """Register a custom BaseExporter instance for a target ExportFormat."""
        with self._lock:
            self._exporters[fmt] = exporter

    def export_session(self, session: ReplaySession, config: ExportConfig | None = None) -> str:
        """Export a ReplaySession to string format."""
        cfg = config or ExportConfig()
        exporter = self._get_exporter(cfg.format)
        with self._lock:
            return exporter.export_session(session, cfg)

    def export_diff_report(self, report: ExecutionDiffReport, config: ExportConfig | None = None) -> str:
        """Export an ExecutionDiffReport to string format."""
        cfg = config or ExportConfig()
        exporter = self._get_exporter(cfg.format)
        with self._lock:
            return exporter.export_diff_report(report, cfg)

    def _get_exporter(self, fmt: ExportFormat) -> BaseExporter:
        with self._lock:
            exporter = self._exporters.get(fmt)
            if not exporter:
                raise ExporterNotFoundError(f"No exporter registered for format {fmt!r}")
            return exporter
