"""Django view instrumentation reference example using TraceForge."""

import traceforge

tracer = traceforge.Tracer("django-service")

def my_django_view(request_path: str):
    with tracer.start_span("django_view_handler") as span:
        span.set_attribute("request.path", request_path)
        return {"status": "ok", "path": request_path}

if __name__ == "__main__":
    print(my_django_view("/dashboard"))
