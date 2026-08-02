#!/usr/bin/env bash
# Run static analysis: ruff (lint) + mypy (types).
set -euo pipefail
cd "$(dirname "$0")/.."
echo "== ruff =="
python3 -m ruff check traceforge
echo "== mypy =="
python3 -m mypy traceforge --ignore-missing-imports
