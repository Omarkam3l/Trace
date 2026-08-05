"""Unit tests for ConfigurationLoader."""

from __future__ import annotations

import os
import tempfile

from traceforge.configuration.loader import ConfigurationLoader


def test_configuration_loader_defaults():
    loader = ConfigurationLoader()
    cfg = loader.load_config()
    assert cfg.server.port == 8000
    assert cfg.storage.driver == "sqlite"


def test_configuration_loader_cli_overrides():
    loader = ConfigurationLoader()
    cfg = loader.load_config(cli_overrides={"server": {"port": 9090}})
    assert cfg.server.port == 9090


def test_configuration_loader_json_file():
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        f.write('{"env": "staging", "server": {"port": 8888}}')
        f_path = f.name

    try:
        loader = ConfigurationLoader()
        cfg = loader.load_config(config_path=f_path)
        assert cfg.env == "staging"
        assert cfg.server.port == 8888
    finally:
        os.remove(f_path)
