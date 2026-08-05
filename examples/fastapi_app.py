"""FastAPI app instrumentation example using TraceForge."""

from fastapi import FastAPI

import traceforge

app = FastAPI(title="Instrumented Service")
tracer = traceforge.Tracer("fastapi-service")
storage = traceforge.MemoryStorage()
recorder = traceforge.Recorder(storage=storage).start()
tracer.add_hook(recorder)

@app.get("/items/{item_id}")
def read_item(item_id: int):
    with tracer.start_span("read_item_handler") as span:
        span.set_attribute("item_id", str(item_id))
        return {"item_id": item_id, "status": "active"}
