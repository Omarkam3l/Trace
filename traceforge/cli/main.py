"""Main CLI entry point for TraceForge."""

from __future__ import annotations

import argparse
import sys

from traceforge.cli.commands import COMMAND_MODULES


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="traceforge",
        description="TraceForge: Framework-Agnostic Execution Replay & Analysis Platform.",
    )
    parser.add_argument("--version", action="version", version="TraceForge 1.0.0")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    for mod in COMMAND_MODULES:
        mod.register_parser(subparsers)

    return parser


def cli_entry(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        return 1

    try:
        return args.func(args)
    except Exception as e:
        print(f"[!] Command execution error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(cli_entry())
