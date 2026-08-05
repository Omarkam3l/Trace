# TraceForge Troubleshooting Guide

- **Database Locked Error**: Ensure thread isolation or set SQLite WAL mode.
- **Missing Module Error**: Install `uvicorn` and `PyJWT` via `pip install traceforge`.
- **401 Unauthorized**: Pass `Authorization: Bearer <token>` or `Authorization: Api-Key <key>`.
