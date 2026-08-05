# TraceForge Plugin Development Guide

Plugins inherit from `TraceForgePluginInterface` and consume public TraceForge APIs.

```python
from traceforge.plugins import TraceForgePluginInterface, PluginMetadata

class CustomPlugin(TraceForgePluginInterface):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(name="custom-plugin", version="1.0.0")

    def initialize(self, context=None) -> None:
        print("Initialized CustomPlugin")

    def shutdown(self) -> None:
        print("Shutdown CustomPlugin")
```
