"""CLI command: traceforge replay"""

from __future__ import annotations

import argparse

from traceforge.configuration.loader import ConfigurationLoader
from traceforge.service.service import TraceForgeApiService
from traceforge.storage.drivers.sqlite import SQLiteStorageDriver


def register_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("replay", help="Reconstruct and display a historical execution session.")
    parser.add_argument("session_id", help="Target session ID to replay.")
    parser.add_argument("--db", help="Database file path (default: traceforge.db).")
    parser.set_defaults(func=execute)


def execute(args: argparse.Namespace) -> int:
    config = ConfigurationLoader().load_config()
    db_uri = args.db or config.storage.database_uri

    try:
        driver = SQLiteStorageDriver(db_uri)
        conn = driver.connection_manager.get_connection()
        service = TraceForgeApiService(conn)

        session_replay = service.replay_session(args.session_id)
        print(f"=== Execution Replay: Session {args.session_id} ===")
        print(f"Status: {session_replay.session.status}")
        print(f"Started At: {session_replay.session.started_at}")
        print(f"Environment OS: {session_replay.session.environment_os}")
        print(f"Nodes Count: {len(session_replay.nodes)}")
        print(f"Relationships Count: {len(session_replay.relationships)}")
        print(f"Timeline Events: {len(session_replay.timeline)}")
        driver.close()
        return 0
    except Exception as e:
        print(f"[!] Error replaying session {args.session_id}: {e}")
        return 1
