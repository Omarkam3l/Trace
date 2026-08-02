"""Load :class:`TraceForgeSettings` from environment variables or a JSON file."""

from __future__ import annotations

import json
import os
from pathlib import Path

from traceforge.config.defaults import ENV_PREFIX
from traceforge.config.settings import TraceForgeSettings


def load_settings(env_prefix: str = ENV_PREFIX) -> TraceForgeSettings:
    """Build settings from ``{env_prefix}*`` environment variables.

    Unset variables fall back to :class:`TraceForgeSettings` defaults.
    """
    field_names = TraceForgeSettings.model_fields.keys()
    overrides: dict[str, str] = {}
    for field_name in field_names:
        env_var = f"{env_prefix}{field_name.upper()}"
        if env_var in os.environ:
            overrides[field_name] = os.environ[env_var]
    return TraceForgeSettings.model_validate(overrides)


def load_from_file(path: str | Path) -> TraceForgeSettings:
    """Build settings from a JSON file."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return TraceForgeSettings.model_validate(data)
