# David Portfolio — CV App

Full-stack portfolio application built with **FastAPI**, **React**, **Docker**, **Kubernetes**, and **AI integration**.

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + TypeScript + Vite + Tailwind CSS |
| Backend | FastAPI + Python 3.12 + SQLAlchemy 2.0 (async) |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Message Queue | RabbitMQ 3.13 |
| Workers | Celery |
| Containers | Docker + Docker Compose |
| Orchestration | Kubernetes + Helm + Kustomize |
| CI/CD | GitHub Actions |

## Quick Start

```bash
# 1. Clone and configure
cp .env.example .env

# 2. Start all services
make dev-build

# 3. Access
# Frontend:  http://localhost:3000
# Backend:   http://localhost:8000/api/docs
# RabbitMQ:  http://localhost:15672
```

## Project Structure

```
david-portfolio/
├── backend/          # FastAPI + CQRS + Vertical Slices
├── frontend/         # React + TypeScript + Tailwind
├── infra/
│   ├── docker/       # Docker Compose configs
│   ├── kubernetes/   # Helm charts + Kustomize overlays
│   └── monitoring/   # Prometheus + Grafana
├── scripts/          # Setup and deploy helpers
├── docs/             # Architecture documentation
└── Makefile          # Unified commands
```

## Architecture

- **Vertical Slice Architecture** — each feature is self-contained
- **CQRS** — separated read/write paths
- **Event-Driven** — RabbitMQ for async processing
- **Multi-Stage Docker Builds** — optimized images
