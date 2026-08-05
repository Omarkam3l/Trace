"""CLI command: traceforge visualize"""

from __future__ import annotations

import argparse

from traceforge.configuration.loader import ConfigurationLoader
from traceforge.service.service import TraceForgeApiService
from traceforge.storage.drivers.sqlite import SQLiteStorageDriver


def register_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("visualize", help="Generate frontend-ready visualization models.")
    parser.add_argument("session_id", help="Session ID to visualize.")
    parser.add_argument("--type", choices=["graph", "timeline", "flamegraph"], default="graph", help="Visualization model type.")
    parser.add_argument("--db", help="Database file path.")
    parser.set_defaults(func=execute)


def execute(args: argparse.Namespace) -> int:
    config = ConfigurationLoader().load_config()
    db_uri = args.db or config.storage.database_uri

    try:
        driver = SQLiteStorageDriver(db_uri)
        conn = driver.connection_manager.get_connection()
        service = TraceForgeApiService(conn)

        if args.type == "graph":
            vm = service.get_graph_visualization(args.session_id)
        elif args.type == "timeline":
            vm = service.get_timeline_visualization(args.session_id)
        else:
            vm = service.get_flamegraph_visualization(args.session_id)

        print(vm.model_dump_json(indent=2))
        driver.close()
        return 0
    except Exception as e:
        print(f"[!] Visualization error: {e}")
        return 1
