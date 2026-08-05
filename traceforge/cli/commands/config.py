"""CLI command: traceforge config"""

from __future__ import annotations

import argparse

from traceforge.configuration.loader import ConfigurationLoader


def register_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("config", help="Inspect active TraceForge configuration.")
    parser.add_argument("--file", help="Path to config file.")
    parser.set_defaults(func=execute)


def execute(args: argparse.Namespace) -> int:
    config = ConfigurationLoader().load_config(config_path=args.file)
    print("=== Active TraceForge Configuration ===")
    print(config.model_dump_json(indent=2))
    return 0
