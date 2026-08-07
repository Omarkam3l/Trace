"""Regression tests: EnvSource must actually read TRACEFORGE_JWT_SECRET and TRACEFORGE_SECURITY_ENABLED from the environment.

Prior to this fix, EnvSource silently ignored both variables, meaning the
.env.example guidance to "set TRACEFORGE_JWT_SECRET" had no effect on the
resolved configuration used by `traceforge server`.
"""

from __future__ import annotations

from traceforge.configuration.sources.env import EnvSource


def test_env_source_reads_jwt_secret(monkeypatch):
    monkeypatch.setenv("TRACEFORGE_JWT_SECRET", "a" * 40)
    data = EnvSource().load()
    assert data["security"]["jwt_secret"] == "a" * 40


def test_env_source_reads_security_enabled_true(monkeypatch):
    monkeypatch.setenv("TRACEFORGE_SECURITY_ENABLED", "true")
    data = EnvSource().load()
    assert data["security"]["enabled"] is True


def test_env_source_reads_security_enabled_false(monkeypatch):
    monkeypatch.setenv("TRACEFORGE_SECURITY_ENABLED", "false")
    data = EnvSource().load()
    assert data["security"]["enabled"] is False


def test_env_source_omits_security_key_when_unset(monkeypatch):
    monkeypatch.delenv("TRACEFORGE_JWT_SECRET", raising=False)
    monkeypatch.delenv("TRACEFORGE_SECURITY_ENABLED", raising=False)
    data = EnvSource().load()
    assert "security" not in data


def test_env_source_jwt_secret_flows_through_loader(monkeypatch):
    """End-to-end: setting the env var actually changes what

    ConfigurationLoader resolves, not just what EnvSource.load() returns in
    isolation.
    """
    from traceforge.configuration.loader import ConfigurationLoader

    monkeypatch.setenv("TRACEFORGE_JWT_SECRET", "b" * 40)
    config = ConfigurationLoader().load_config(config_path=None, cli_overrides={})
    assert config.security.jwt_secret == "b" * 40
