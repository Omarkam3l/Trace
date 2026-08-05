"""CLI command: traceforge version"""

from __future__ import annotations

import argparse
import platform
import sys


def register_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("version", help="Print TraceForge version and runtime environment info.")
    parser.set_defaults(func=execute)


def execute(args: argparse.Namespace) -> int:
    print(f"TraceForge v1.0.0")
    print(f"Python: {platform.python_version()} ({sys.executable})")
    print(f"OS: {platform.system()} {platform.release()} ({platform.machine()})")
    return 0
