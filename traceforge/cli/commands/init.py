"""CLI command: traceforge init"""

from __future__ import annotations

import argparse
import os


def register_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("init", help="Initialize a new TraceForge project workspace.")
    parser.add_argument(
        "directory", nargs="?", default=".", help="Target project directory (default: current directory)."
    )
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
  # Do NOT set jwt_secret here if this file will be committed to version
  # control. Set the TRACEFORGE_JWT_SECRET environment variable instead
  # (see .env.example) -- env vars override this file and won't leak into
  # git history. `enabled: false` is fine for local development; flip to
  # true and set TRACEFORGE_JWT_SECRET before deploying anywhere reachable
  # by others.

export:
  default_format: json
  output_dir: exports
""")
        print("  [+] Created configuration file: traceforge.yaml")
    else:
        print("  [*] Config file traceforge.yaml already exists. Skipping.")

    env_example_path = os.path.join(target_dir, ".env.example")
    if not os.path.exists(env_example_path):
        with open(env_example_path, "w", encoding="utf-8") as f:
            f.write("""# TraceForge Environment Variables
TRACEFORGE_ENV=development
TRACEFORGE_HOST=127.0.0.1
TRACEFORGE_PORT=8000
TRACEFORGE_JWT_SECRET=your-secure-jwt-secret-key-here
""")
        print("  [+] Created environment template: .env.example")

    print("\nProject initialization complete! Next steps:")
    print("  1. cd " + (args.directory if args.directory != "." else "."))
    print("  2. traceforge server")
    return 0
