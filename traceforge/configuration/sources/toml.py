"""TOML configuration file loader."""

from __future__ import annotations

import os
from typing import Any


class TomlSource:
    """Loads configuration options from a TOML file."""

    def load(self, filepath: str) -> dict[str, Any]:
        if not os.path.exists(filepath):
            return {}
        try:
            import tomllib

            with open(filepath, "rb") as f:
                return tomllib.load(f)
        except ImportError:
            return {}
