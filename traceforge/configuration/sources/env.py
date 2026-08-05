"""Environment variable configuration source loader."""

from __future__ import annotations

import os
from typing import Any


class EnvSource:
    """Loads configuration options from TRACEFORGE_* environment variables."""

    def load(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        server_dict: dict[str, Any] = {}
        storage_dict: dict[str, Any] = {}

        if "TRACEFORGE_ENV" in os.environ:
            result["env"] = os.environ["TRACEFORGE_ENV"]
        if "TRACEFORGE_PROJECT_NAME" in os.environ:
            result["project_name"] = os.environ["TRACEFORGE_PROJECT_NAME"]
        if "TRACEFORGE_HOST" in os.environ:
            server_dict["host"] = os.environ["TRACEFORGE_HOST"]
        if "TRACEFORGE_PORT" in os.environ:
            server_dict["port"] = int(os.environ["TRACEFORGE_PORT"])
        if "TRACEFORGE_DB_URI" in os.environ:
            storage_dict["database_uri"] = os.environ["TRACEFORGE_DB_URI"]

        if server_dict:
            result["server"] = server_dict
        if storage_dict:
            result["storage"] = storage_dict

        return result
