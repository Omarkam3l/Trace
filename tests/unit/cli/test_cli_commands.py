"""Unit tests for modular CLI commands."""

from __future__ import annotations

import os
import tempfile

from traceforge.cli.main import build_parser, cli_entry


def test_cli_parser_version():
    parser = build_parser()
    args = parser.parse_args(["version"])
    assert hasattr(args, "func")
    code = args.func(args)
    assert code == 0


def test_cli_parser_config():
    parser = build_parser()
    args = parser.parse_args(["config"])
    code = args.func(args)
    assert code == 0


def test_cli_init_command():
    with tempfile.TemporaryDirectory() as tmpdir:
        code = cli_entry(["init", tmpdir])
        assert code == 0
        assert os.path.exists(os.path.join(tmpdir, "traceforge.yaml"))
        assert os.path.exists(os.path.join(tmpdir, "traces"))
        assert os.path.exists(os.path.join(tmpdir, "exports"))
