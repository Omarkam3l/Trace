"""Export configuration and ExportFormat definitions."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class ExportFormat(StrEnum):
    """Supported export target formats."""

    JSON = "json"
    MERMAID = "mermaid"
    HTML = "html"
    MARKDOWN = "markdown"


class ExportConfig(BaseModel):
    """Immutable configuration for ExportEngine exporters."""

    model_config = ConfigDict(frozen=True)

    format: ExportFormat = ExportFormat.JSON
    pretty_print: bool = True
    include_timeline: bool = True
    include_performance: bool = True
