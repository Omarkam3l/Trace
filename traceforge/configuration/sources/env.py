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
        security_dict: dict[str, Any] = {}

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
        if "TRACEFORGE_JWT_SECRET" in os.environ:
            security_dict["jwt_secret"] = os.environ["TRACEFORGE_JWT_SECRET"]
        if "TRACEFORGE_SECURITY_ENABLED" in os.environ:
            security_dict["enabled"] = os.environ["TRACEFORGE_SECURITY_ENABLED"].strip().lower() not in (
                "0",
                "false",
                "no",
            )

        if server_dict:
            result["server"] = server_dict
        if storage_dict:
            result["storage"] = storage_dict
        if security_dict:
            result["security"] = security_dict

        return result
