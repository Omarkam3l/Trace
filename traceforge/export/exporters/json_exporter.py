"""JsonExporter formatting artifacts to deterministic JSON strings."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from traceforge.export.base import BaseExporter

if TYPE_CHECKING:
    from traceforge.diff.report import ExecutionDiffReport
    from traceforge.export.config import ExportConfig
    from traceforge.replay.session import ReplaySession


class JsonExporter(BaseExporter):
    """Formats ReplaySession and ExecutionDiffReport objects into JSON strings."""

    def export_session(self, session: ReplaySession, config: ExportConfig) -> str:
        indent = 2 if config.pretty_print else None
        data = session.model_dump(mode="json")
        return json.dumps(data, indent=indent, sort_keys=True)

    def export_diff_report(self, report: ExecutionDiffReport, config: ExportConfig) -> str:
        indent = 2 if config.pretty_print else None
        data = report.model_dump(mode="json")
        return json.dumps(data, indent=indent, sort_keys=True)
