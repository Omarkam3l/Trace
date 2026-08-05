"""CLI command: traceforge diff"""

from __future__ import annotations

import argparse

from traceforge.configuration.loader import ConfigurationLoader
from traceforge.service.service import TraceForgeApiService
from traceforge.storage.drivers.sqlite import SQLiteStorageDriver


def register_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("diff", help="Compare two historical execution sessions.")
    parser.add_argument("baseline_id", help="Baseline session ID.")
    parser.add_argument("target_id", help="Target session ID.")
    parser.add_argument("--db", help="Database file path.")
    parser.set_defaults(func=execute)


def execute(args: argparse.Namespace) -> int:
    config = ConfigurationLoader().load_config()
    db_uri = args.db or config.storage.database_uri

    try:
        driver = SQLiteStorageDriver(db_uri)
        conn = driver.connection_manager.get_connection()
        service = TraceForgeApiService(conn)

        diff_report = service.compare_sessions(args.baseline_id, args.target_id)
        print(f"=== Execution Diff Report ===")
        print(f"Baseline Session: {diff_report.baseline_session_id}")
        print(f"Target Session: {diff_report.target_session_id}")
        if diff_report.graph_diff:
            print(f"Added Nodes: {len(diff_report.graph_diff.added_nodes)}")
            print(f"Removed Nodes: {len(diff_report.graph_diff.removed_nodes)}")
            print(f"Modified Nodes: {len(diff_report.graph_diff.modified_nodes)}")
        driver.close()
        return 0
    except Exception as e:
        print(f"[!] Error comparing sessions: {e}")
        return 1
