# TraceForge Developer Onboarding & Quickstart

Welcome to TraceForge — the framework-agnostic execution replay & analysis platform.

## Quickstart Installation

```bash
pip install traceforge
```

## Initializing Workspace

To initialize a project workspace:

```bash
traceforge init my_project
cd my_project
```

This creates:
- `traceforge.yaml`
- `traces/`
- `exports/`
- `plugins/`
- `logs/`

## Launching Platform Server

```bash
traceforge server
```

Open `http://localhost:8000` to view the platform dashboard.
