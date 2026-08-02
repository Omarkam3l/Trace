"""BaseExporter abstract base class for Export System."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from traceforge.diff.report import ExecutionDiffReport
    from traceforge.export.config import ExportConfig
    from traceforge.replay.session import ReplaySession


class BaseExporter(ABC):
    """Abstract contract for formatting execution artifacts into target export representations."""

    @abstractmethod
    def export_session(self, session: ReplaySession, config: ExportConfig) -> str:
        """Export a ReplaySession artifact to string format."""

    @abstractmethod
    def export_diff_report(self, report: ExecutionDiffReport, config: ExportConfig) -> str:
        """Export an ExecutionDiffReport artifact to string format."""
