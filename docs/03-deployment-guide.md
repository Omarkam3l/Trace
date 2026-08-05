# TraceForge Production Deployment Guide

## Docker Container Deployment

```bash
docker build -t traceforge:latest .
docker run -d -p 8000:8000 -v /data/traces:/data traceforge:latest
```

## Docker Compose Deployment

```bash
docker-compose up -d
```

## Reverse Proxy Setup (Nginx)

Reference `nginx.conf` for reverse proxy configurations routing traffic to `traceforge:8000`.
