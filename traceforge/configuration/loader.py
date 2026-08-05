"""Configuration loader implementing hierarchical priority."""

from __future__ import annotations

import os
from typing import Any

from traceforge.configuration.defaults import DEFAULT_CONFIG
from traceforge.configuration.schema import TraceForgeConfig
from traceforge.configuration.sources.env import EnvSource
from traceforge.configuration.sources.json import JsonSource
from traceforge.configuration.sources.toml import TomlSource
from traceforge.configuration.sources.yaml import YamlSource


class ConfigurationLoader:
    """Loads configuration with priority: CLI > ENV > Config file > Defaults."""

    def load_config(
        self,
        config_path: str | None = None,
        cli_overrides: dict[str, Any] | None = None,
    ) -> TraceForgeConfig:
        merged_data: dict[str, Any] = DEFAULT_CONFIG.model_dump()

        # 1. Load config file if specified or found in workspace
        file_path = config_path or self._find_default_config_file()
        if file_path and os.path.exists(file_path):
            file_data = self._load_file(file_path)
            self._deep_merge(merged_data, file_data)

        # 2. Merge Environment variables
        env_data = EnvSource().load()
        self._deep_merge(merged_data, env_data)

        # 3. Merge CLI Overrides
        if cli_overrides:
            self._deep_merge(merged_data, cli_overrides)

        return TraceForgeConfig.model_validate(merged_data)

    def _find_default_config_file(self) -> str | None:
        candidates = ["traceforge.yaml", "traceforge.yml", "traceforge.toml", "traceforge.json"]
        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate
        return None

    def _load_file(self, filepath: str) -> dict[str, Any]:
        ext = os.path.splitext(filepath)[1].lower()
        if ext in (".yaml", ".yml"):
            return YamlSource().load(filepath)
        elif ext == ".toml":
            return TomlSource().load(filepath)
        elif ext == ".json":
            return JsonSource().load(filepath)
        return {}

    def _deep_merge(self, base: dict[str, Any], override: dict[str, Any]) -> None:
        for k, v in override.items():
            if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                self._deep_merge(base[k], v)
            elif v is not None:
                base[k] = v
