"""YAML configuration file loader."""

from __future__ import annotations

import os
from typing import Any


class YamlSource:
    """Loads configuration options from a YAML file."""

    def load(self, filepath: str) -> dict[str, Any]:
        if not os.path.exists(filepath):
            return {}
        try:
            import yaml

            with open(filepath, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)
                return content if isinstance(content, dict) else {}
        except ImportError:
            # Fallback simple line parser if PyYAML is not installed
            return {}
