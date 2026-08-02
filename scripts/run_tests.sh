#!/usr/bin/env bash
# Run the full TraceForge test suite with coverage.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pytest --cov=traceforge --cov-report=term-missing "$@"
