"""CLI command: traceforge init"""

from __future__ import annotations

import argparse
import os


def register_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("init", help="Initialize a new TraceForge project workspace.")
    parser.add_argument("directory", nargs="?", default=".", help="Target project directory (default: current directory).")
    parser.set_defaults(func=execute)


def execute(args: argparse.Namespace) -> int:
    target_dir = os.path.abspath(args.directory)
    print(f"Initializing TraceForge project in: {target_dir}")

    os.makedirs(target_dir, exist_ok=True)
    subdirs = ["traces", "exports", "plugins", "logs"]
    for sd in subdirs:
        path = os.path.join(target_dir, sd)
        os.makedirs(path, exist_ok=True)
        print(f"  [+] Created directory: {sd}/")

    config_path = os.path.join(target_dir, "traceforge.yaml")
    if not os.path.exists(config_path):
        with open(config_path, "w", encoding="utf-8") as f:
            f.write("""# TraceForge Platform Configuration
env: development
project_name: traceforge_app
data_dir: traces
logs_dir: logs
plugins_dir: plugins

server:
  host: 127.0.0.1
  port: 8000
  reload: false
  workers: 1

storage:
  driver: sqlite
  database_uri: traces/traceforge.db

security:
  enabled: false
  jwt_secret: traceforge-default-secret-change-in-production

export:
  default_format: json
  output_dir: exports
""")
        print("  [+] Created configuration file: traceforge.yaml")
    else:
        print("  [*] Config file traceforge.yaml already exists. Skipping.")

    print("\nProject initialization complete! Next steps:")
    print("  1. cd " + (args.directory if args.directory != "." else "."))
    print("  2. traceforge server")
    return 0
