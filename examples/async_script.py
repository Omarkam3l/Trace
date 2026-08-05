"""Async script example using TraceForge SDK."""

import asyncio

import traceforge


async def fetch_data(tracer):
    with tracer.start_span("fetch_remote"):
        await asyncio.sleep(0.05)
        return {"data": 123}


async def main():
    tracer = traceforge.Tracer("async-service")
    storage = traceforge.MemoryStorage()
    recorder = traceforge.Recorder(storage=storage).start()
    tracer.add_hook(recorder)

    with tracer.start_span("async_orchestration"):
        res = await fetch_data(tracer)
        print("Fetched:", res)

    recorder.stop()


if __name__ == "__main__":
    asyncio.run(main())
