"""Simple script example using TraceForge SDK."""

import traceforge


def main():
    tracer = traceforge.Tracer("simple-script-service")
    storage = traceforge.MemoryStorage()
    recorder = traceforge.Recorder(storage=storage).start()
    tracer.add_hook(recorder)

    with tracer.start_span("main_task") as span:
        span.set_attribute("env", "demo")
        with tracer.start_span("sub_task"):
            print("Executing subtask...")

    recorder.stop()
    print("Recorded spans successfully!")

if __name__ == "__main__":
    main()
