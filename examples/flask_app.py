"""Flask app instrumentation example using TraceForge."""

import traceforge

tracer = traceforge.Tracer("flask-service")

def handle_request(path: str):
    with tracer.start_span("handle_request") as span:
        span.set_attribute("http.path", path)
        return f"Response for {path}"

if __name__ == "__main__":
    print(handle_request("/api/users"))
