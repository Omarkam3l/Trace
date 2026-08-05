"""CLI command: traceforge server"""

from __future__ import annotations

import argparse

from traceforge.configuration.loader import ConfigurationLoader
from traceforge.gateway.server import create_app
from traceforge.security.config import DEFAULT_JWT_SECRET
from traceforge.service.service import TraceForgeApiService
from traceforge.storage.drivers.sqlite import SQLiteStorageDriver


def register_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("server", help="Start the TraceForge HTTP Gateway server.")
    parser.add_argument("--host", help="Host address to bind to (default: 127.0.0.1).")
    parser.add_argument("--port", type=int, help="Port to listen on (default: 8000).")
    parser.add_argument("--config", help="Path to traceforge.yaml configuration file.")
    parser.set_defaults(func=execute)


def execute(args: argparse.Namespace) -> int:
    cli_overrides = {}
    if args.host:
        cli_overrides["server"] = {"host": args.host}
    if args.port:
        if "server" not in cli_overrides:
            cli_overrides["server"] = {}
        cli_overrides["server"]["port"] = args.port

    config = ConfigurationLoader().load_config(config_path=args.config, cli_overrides=cli_overrides)

    # config.security.jwt_secret is validated on construction: the
    # SecurityConfigSchema field_validator (shared with SecurityConfig) already
    # warns via the `warnings` module if it's still the default. This check
    # additionally prints a hard-to-miss, unsuppressible message on the
    # server's own stdout, since `warnings` output can be filtered/hidden by
    # the environment uvicorn runs in.
    if config.security.jwt_secret == DEFAULT_JWT_SECRET:
        print("=" * 70)
        print("[!] SECURITY WARNING: Server is using the DEFAULT JWT secret.")
        print("    Anyone who has read this open-source repository knows this")
        print("    value and can forge valid, admin-role auth tokens.")
        print("    Set TRACEFORGE_JWT_SECRET to a random 32+ character value")
        print("    before exposing this server outside localhost.")
        print("=" * 70)

    if not config.security.enabled:
        print("[!] WARNING: Security layer is DISABLED (TRACEFORGE_SECURITY_ENABLED=false).")
        print("    All endpoints are reachable without authentication.")

    print("Starting TraceForge HTTP Gateway Server v1.0.0...")
    print(f"Binding to http://{config.server.host}:{config.server.port}")
    print(f"Database URI: {config.storage.database_uri}")

    driver = SQLiteStorageDriver(config.storage.database_uri)
    conn = driver.connection_manager.get_connection()
    service = TraceForgeApiService(conn)
    app = create_app(
        service,
        security_config=config.security.to_security_config(),
        security_enabled=config.security.enabled,
    )

    try:
        import uvicorn

        uvicorn.run(app, host=config.server.host, port=config.server.port, log_level="info")
        return 0
    except ImportError:
        print("[!] Error: uvicorn package is required to run the web server.")
        return 1
    except Exception as e:
        print(f"[!] Server error: {e}")
        return 1
