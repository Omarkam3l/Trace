"""CLI command: traceforge export"""

from __future__ import annotations

import argparse

from traceforge.configuration.loader import ConfigurationLoader
from traceforge.export.config import ExportConfig, ExportFormat
from traceforge.service.service import TraceForgeApiService
from traceforge.storage.drivers.sqlite import SQLiteStorageDriver


def register_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("export", help="Export session or diff artifact to external format.")
    parser.add_argument("session_id", help="Session ID to export.")
    parser.add_argument("--format", choices=["json", "mermaid", "html", "markdown"], default="json", help="Export format.")
    parser.add_argument("--output", help="Output file path (prints to stdout if omitted).")
    parser.add_argument("--db", help="Database file path.")
    parser.set_defaults(func=execute)


def execute(args: argparse.Namespace) -> int:
    config = ConfigurationLoader().load_config()
    db_uri = args.db or config.storage.database_uri

    try:
        driver = SQLiteStorageDriver(db_uri)
        conn = driver.connection_manager.get_connection()
        service = TraceForgeApiService(conn)

        export_fmt = ExportFormat(args.format.lower())
        output_str = service.export_session(args.session_id, config=ExportConfig(format=export_fmt))

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output_str)
            print(f"Exported session {args.session_id} to {args.output}")
        else:
            print(output_str)

        driver.close()
        return 0
    except Exception as e:
        print(f"[!] Export error: {e}")
        return 1
