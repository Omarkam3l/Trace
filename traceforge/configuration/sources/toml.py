"""TOML configuration file loader."""

from __future__ import annotations

import os
import sys
from typing import Any


class TomlSource:
    """Loads configuration options from a TOML file."""

    def load(self, filepath: str) -> dict[str, Any]:
        if not os.path.exists(filepath):
            return {}
        try:
            if sys.version_info >= (3, 11):
                import tomllib

                with open(filepath, "rb") as f:
                    return tomllib.load(f)
            else:
                import tomli

                with open(filepath, "rb") as f:
                    return tomli.load(f)
        except ImportError:
            return {}
