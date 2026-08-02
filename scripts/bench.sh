#!/usr/bin/env bash
# Run the lightweight benchmark suite.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 benchmarks/bench_tracer.py
