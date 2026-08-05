# TraceForge Architecture Overview

TraceForge is built using clean CQRS and domain-driven design principles:

```
Recorder (Write) ──► Storage ──► Query Engine (Read) ──► Replay Engine
                                                               │
                                                               ▼
HTTP Gateway ◄── TraceForgeApiService ◄── Visualization & Exporters
```

- **Phases 1-3**: Core SDK, Instrumentation API & Spans
- **Phases 4-5**: Plugin SDK & Python Runtime Plugin
- **Phase 6**: Storage Architecture & SQLite Driver
- **Phase 7**: Read-Only Query Engine
- **Phase 8**: Deterministic Replay Engine
- **Phase 9**: Execution Diff Engine
- **Phase 10**: Exporters (JSON, Mermaid, HTML, Markdown)
- **Phase 11**: Visualization Data Adapters
- **Phase 12**: API Service Layer
- **Phase 13**: FastAPI REST HTTP Gateway
- **Phase 14**: Auth & Security Layer
- **Phase 15**: Platform CLI, Configuration, Deployment & Dashboard
