"""JSON configuration file loader."""

from __future__ import annotations

import json
import os
from typing import Any


class JsonSource:
    """Loads configuration options from a JSON file."""

    def load(self, filepath: str) -> dict[str, Any]:
        if not os.path.exists(filepath):
            return {}
        try:
            with open(filepath, encoding="utf-8") as f:
                content = json.load(f)
                return content if isinstance(content, dict) else {}
        except Exception:
            return {}
