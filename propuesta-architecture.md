# 🚀 Portfolio CV App — Arquitectura & Plan de Desarrollo

## Visión General

Aplicación web fullstack que funciona como CV interactivo y portfolio profesional, diseñada desde cero para demostrar dominio en **DevOps**, **Backend Python**, **Cloud Native** y **AI Integration**. La app no solo muestra tu CV — *es* tu CV técnico en acción.

---

## 1. Stack Tecnológico

| Capa | Tecnología | Justificación |
|------|-----------|---------------|
| **Frontend** | React 18 + TypeScript + Vite | SPA moderna, tipado fuerte, build rápido |
| **UI Framework** | Tailwind CSS + Framer Motion | Diseño profesional con animaciones fluidas |
| **Backend API** | FastAPI (Python 3.12) | Async nativo, OpenAPI docs, tipado con Pydantic |
| **Base de Datos** | PostgreSQL 16 | Relacional, robusto, soporte JSON nativo |
| **Cache** | Redis 7 | Cache de respuestas, rate limiting, sessions |
| **Message Queue** | RabbitMQ 3.13 | Procesamiento async, event-driven decoupling |
| **Background Workers** | Celery + Celery Beat | Task queue, scheduled jobs, retries |
| **AI Engine** | LangChain + OpenAI/Anthropic API | Chat interactivo, generación dinámica |
| **ORM** | SQLAlchemy 2.0 (async) | Modelos declarativos, migrations con Alembic |
| **Containerización** | Docker + Docker Compose | Entornos reproducibles, multi-stage builds |
| **Orquestación** | Kubernetes (K8s) | Producción escalable, self-healing |
| **Package Manager** | Helm 3 | Charts reutilizables, releases versionados |
| **Config Management** | Kustomize | Overlays por ambiente (dev/staging/prod) |
| **CI/CD** | GitHub Actions | Pipeline automatizado, free tier |
| **Registry** | Docker Hub / GitHub Container Registry | Almacenamiento de imágenes |
| **Monitoring** | Prometheus + Grafana | Métricas, dashboards, alertas |
| **Logging** | ELK Stack (Elastic + Logstash + Kibana) | Logs centralizados |
| **API Gateway** | Nginx Ingress Controller | Routing, TLS, rate limiting |

---

## 2. Estructura de Carpetas

```
david-portfolio/
│
├── .github/
│   └── workflows/
│       ├── ci-backend.yml              # Lint, test, build backend
│       ├── ci-frontend.yml             # Lint, test, build frontend
│       ├── cd-deploy.yml               # Deploy to K8s
│       └── security-scan.yml           # Trivy, Snyk
│
├── frontend/
│   ├── Dockerfile                      # Multi-stage: build → nginx
│   ├── .dockerignore
│   ├── nginx.conf                      # SPA routing config
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── public/
│   │   └── assets/                     # Imágenes, favicon, CV PDF
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── routes/
│       │   └── index.tsx               # React Router config
│       ├── pages/
│       │   ├── Home/                   # Landing + Hero section
│       │   ├── About/                  # Bio, skills, timeline
│       │   ├── Projects/              # Portfolio showcase
│       │   ├── Experience/            # Work + Education
│       │   ├── Contact/              # Form + social links
│       │   └── AIChat/               # Chat interactivo con AI
│       ├── components/
│       │   ├── ui/                     # Botones, cards, modals
│       │   ├── layout/                # Navbar, Footer, Sidebar
│       │   └── sections/             # Componentes de sección
│       ├── hooks/
│       ├── services/                  # API client (axios/fetch)
│       ├── store/                     # Zustand o Context
│       ├── types/
│       └── styles/
│
├── backend/
│   ├── Dockerfile                      # Multi-stage: build → slim
│   ├── .dockerignore
│   ├── pyproject.toml                  # Poetry / uv
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/
│   │
│   ├── app/
│   │   ├── main.py                     # FastAPI app factory
│   │   ├── config.py                   # Settings con Pydantic
│   │   │
│   │   ├── infrastructure/            # Cross-cutting concerns
│   │   │   ├── database.py            # SQLAlchemy async engine
│   │   │   ├── redis.py               # Redis client
│   │   │   ├── rabbitmq.py            # RabbitMQ connection
│   │   │   ├── celery_app.py          # Celery config
│   │   │   ├── middleware/
│   │   │   │   ├── cors.py
│   │   │   │   ├── rate_limiter.py    # Redis-based
│   │   │   │   └── logging.py
│   │   │   └── exceptions/
│   │   │       └── handlers.py
│   │   │
│   │   ├── features/                  # ── VERTICAL SLICES ──
│   │   │   │
│   │   │   ├── profile/              # Slice: Perfil / CV Data
│   │   │   │   ├── models.py          # SQLAlchemy entities
│   │   │   │   ├── schemas.py         # Pydantic DTOs
│   │   │   │   ├── commands/          # CQRS Write side
│   │   │   │   │   ├── update_profile.py
│   │   │   │   │   └── upload_cv.py
│   │   │   │   ├── queries/           # CQRS Read side
│   │   │   │   │   ├── get_profile.py
│   │   │   │   │   └── get_skills.py
│   │   │   │   ├── events/            # Domain events → RabbitMQ
│   │   │   │   │   └── profile_updated.py
│   │   │   │   └── router.py          # FastAPI endpoints
│   │   │   │
│   │   │   ├── projects/             # Slice: Portfolio Projects
│   │   │   │   ├── models.py
│   │   │   │   ├── schemas.py
│   │   │   │   ├── commands/
│   │   │   │   │   └── create_project.py
│   │   │   │   ├── queries/
│   │   │   │   │   ├── list_projects.py
│   │   │   │   │   └── get_project_detail.py
│   │   │   │   ├── events/
│   │   │   │   └── router.py
│   │   │   │
│   │   │   ├── contact/              # Slice: Contact Form
│   │   │   │   ├── models.py
│   │   │   │   ├── schemas.py
│   │   │   │   ├── commands/
│   │   │   │   │   └── send_message.py
│   │   │   │   ├── tasks/             # Celery async tasks
│   │   │   │   │   └── send_email.py
│   │   │   │   ├── events/
│   │   │   │   │   └── message_received.py
│   │   │   │   └── router.py
│   │   │   │
│   │   │   ├── analytics/            # Slice: Visitor Analytics
│   │   │   │   ├── models.py
│   │   │   │   ├── schemas.py
│   │   │   │   ├── commands/
│   │   │   │   │   └── track_visit.py
│   │   │   │   ├── queries/
│   │   │   │   │   └── get_stats.py
│   │   │   │   ├── tasks/
│   │   │   │   │   └── aggregate_metrics.py
│   │   │   │   └── router.py
│   │   │   │
│   │   │   └── ai_chat/              # Slice: AI Assistant
│   │   │       ├── models.py          # Chat history
│   │   │       ├── schemas.py
│   │   │       ├── commands/
│   │   │       │   └── send_chat.py   # Process user message
│   │   │       ├── queries/
│   │   │       │   └── get_chat_history.py
│   │   │       ├── tasks/
│   │   │       │   └── process_ai_response.py
│   │   │       ├── services/
│   │   │       │   ├── llm_service.py      # LangChain orchestration
│   │   │       │   ├── rag_service.py      # RAG pipeline
│   │   │       │   └── prompt_templates.py
│   │   │       └── router.py          # WebSocket + REST
│   │   │
│   │   └── shared/                    # Shared kernel
│   │       ├── base_model.py          # SQLAlchemy base
│   │       ├── mediator.py            # Command/Query dispatcher
│   │       ├── event_bus.py           # RabbitMQ publisher
│   │       └── pagination.py
│   │
│   ├── workers/
│   │   ├── celery_worker.py           # Celery worker entrypoint
│   │   └── Dockerfile                 # Worker container separado
│   │
│   └── tests/
│       ├── conftest.py
│       ├── unit/
│       ├── integration/
│       └── e2e/
│
├── infra/
│   │
│   ├── docker/
│   │   ├── docker-compose.yml         # Desarrollo local full stack
│   │   ├── docker-compose.dev.yml     # Override para hot-reload
│   │   └── docker-compose.prod.yml    # Producción local
│   │
│   ├── kubernetes/
│   │   │
│   │   ├── helm/                      # ── HELM CHARTS ──
│   │   │   └── portfolio-app/
│   │   │       ├── Chart.yaml
│   │   │       ├── values.yaml             # Defaults
│   │   │       ├── values-dev.yaml
│   │   │       ├── values-staging.yaml
│   │   │       ├── values-prod.yaml
│   │   │       └── templates/
│   │   │           ├── _helpers.tpl
│   │   │           ├── backend-deployment.yaml
│   │   │           ├── backend-service.yaml
│   │   │           ├── backend-hpa.yaml         # Autoscaling
│   │   │           ├── frontend-deployment.yaml
│   │   │           ├── frontend-service.yaml
│   │   │           ├── worker-deployment.yaml
│   │   │           ├── ingress.yaml
│   │   │           ├── configmap.yaml
│   │   │           ├── secrets.yaml
│   │   │           ├── rabbitmq-statefulset.yaml
│   │   │           ├── redis-deployment.yaml
│   │   │           ├── postgres-statefulset.yaml
│   │   │           └── pvc.yaml                 # Persistent volumes
│   │   │
│   │   └── kustomize/                # ── KUSTOMIZE OVERLAYS ──
│   │       ├── base/
│   │       │   ├── kustomization.yaml
│   │       │   ├── namespace.yaml
│   │       │   ├── backend/
│   │       │   │   ├── deployment.yaml
│   │       │   │   ├── service.yaml
│   │       │   │   └── kustomization.yaml
│   │       │   ├── frontend/
│   │       │   │   ├── deployment.yaml
│   │       │   │   ├── service.yaml
│   │       │   │   └── kustomization.yaml
│   │       │   ├── worker/
│   │       │   ├── rabbitmq/
│   │       │   ├── redis/
│   │       │   └── postgres/
│   │       │
│   │       └── overlays/
│   │           ├── dev/
│   │           │   ├── kustomization.yaml      # replicas: 1, debug: true
│   │           │   └── patches/
│   │           ├── staging/
│   │           │   ├── kustomization.yaml      # replicas: 2, limits medium
│   │           │   └── patches/
│   │           └── prod/
│   │               ├── kustomization.yaml      # replicas: 3, HPA, limits high
│   │               └── patches/
│   │
│   └── monitoring/
│       ├── prometheus/
│       │   └── prometheus.yml
│       └── grafana/
│           └── dashboards/
│
├── docs/
│   ├── architecture.md
│   ├── api-contracts.md
│   └── runbooks/
│
├── scripts/
│   ├── setup-local.sh                 # Levanta todo el stack local
│   ├── seed-db.sh                     # Datos iniciales
│   └── deploy.sh                      # Deploy helper
│
├── Makefile                            # Comandos unificados
├── README.md
├── .env.example
└── .gitignore
```

---

## 3. Arquitectura: Vertical Slice + CQRS

### Flujo General

```
┌──────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                          │
│   Pages: Home │ About │ Projects │ Contact │ AI Chat │ Admin     │
└──────────────────┬───────────────────────────────────────────────┘
                   │ HTTP / WebSocket
                   ▼
┌──────────────────────────────────────────────────────────────────┐
│                    NGINX INGRESS CONTROLLER                       │
│              /api/* → backend    /* → frontend                   │
└──────────────────┬───────────────────────────────────────────────┘
                   ▼
┌──────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI)                             │
│                                                                  │
│  ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌──────────┐ ┌─────────┐ │
│  │ Profile │ │ Projects │ │ Contact │ │Analytics │ │ AI Chat │ │
│  │  Slice  │ │  Slice   │ │  Slice  │ │  Slice   │ │  Slice  │ │
│  └────┬────┘ └────┬─────┘ └────┬────┘ └────┬─────┘ └────┬────┘ │
│       │           │            │            │            │       │
│  ┌────▼───────────▼────────────▼────────────▼────────────▼────┐ │
│  │                    MEDIATOR (CQRS Bus)                      │ │
│  │         Commands → Handlers        Queries → Handlers       │ │
│  └────┬─────────────────────────────────────────────┬─────────┘ │
│       │                                             │           │
│  ┌────▼────┐                                  ┌─────▼─────┐    │
│  │ WRITE   │                                  │   READ     │    │
│  │ Command │                                  │   Query    │    │
│  │ Handler │                                  │  Handler   │    │
│  └────┬────┘                                  └─────┬──────┘    │
│       │                                             │           │
│       ▼                                             ▼           │
│  PostgreSQL (write)                         Redis Cache (read)  │
└──────┬───────────────────────────────────────────────────────────┘
       │ Domain Events
       ▼
┌──────────────────────────────────────────────────────────────────┐
│                        RABBITMQ                                  │
│                                                                  │
│   Exchanges:     │  Queues:                                      │
│   portfolio.events│  email.send                                  │
│   portfolio.commands  analytics.track                            │
│                  │  ai.process                                   │
│                  │  cache.invalidate                             │
└──────────────────┬───────────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────────────┐
│                    CELERY WORKERS                                 │
│                                                                  │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────────┐    │
│  │ Email Worker  │  │ Analytics   │  │ AI Processing Worker │    │
│  │ (SMTP send)   │  │ Aggregator  │  │ (LLM calls, RAG)     │    │
│  └──────────────┘  └─────────────┘  └──────────────────────┘    │
│                                                                  │
│  Celery Beat (Scheduler):                                        │
│  - Aggregate analytics cada hora                                 │
│  - Limpiar chat history cada 24h                                 │
│  - Health checks periódicos                                      │
└──────────────────────────────────────────────────────────────────┘
```

### Patrón CQRS por Slice

Cada feature slice sigue esta convención:

```
feature/
├── commands/           # WRITE: Mutan estado
│   └── create_X.py     #   → Command DTO + Handler
│                        #   → Valida, persiste en PostgreSQL
│                        #   → Publica evento a RabbitMQ
│
├── queries/            # READ: Solo lectura
│   └── get_X.py        #   → Query DTO + Handler  
│                        #   → Lee de Redis cache primero
│                        #   → Fallback a PostgreSQL
│                        #   → Cachea resultado en Redis
│
├── events/             # DOMAIN EVENTS
│   └── X_created.py    #   → Publicados vía RabbitMQ
│                        #   → Consumidos por workers async
│
├── tasks/              # BACKGROUND JOBS (Celery)
│   └── process_X.py    #   → Triggered by events
│                        #   → Heavy lifting fuera del request
│
├── models.py           # SQLAlchemy entities (solo este slice)
├── schemas.py          # Pydantic request/response DTOs
└── router.py           # FastAPI endpoints (thin layer)
```

---

## 4. Message Queue & Background Processing

### Topología RabbitMQ

| Exchange | Type | Routing Key | Queue | Consumer |
|----------|------|-------------|-------|----------|
| `portfolio.events` | topic | `contact.message.received` | `email.send` | Email Worker |
| `portfolio.events` | topic | `visit.tracked` | `analytics.aggregate` | Analytics Worker |
| `portfolio.events` | topic | `ai.chat.requested` | `ai.process` | AI Worker |
| `portfolio.events` | topic | `profile.updated` | `cache.invalidate` | Cache Worker |
| `portfolio.dlx` | fanout | `*` | `dead_letter` | Error Monitoring |

### Celery Tasks Pipeline

```
Request → FastAPI → Publish Event (RabbitMQ) → Celery Worker → Result

Ejemplo flujo Contact:
1. POST /api/contact → CreateMessageCommand
2. Handler persiste en PostgreSQL
3. Publica event: contact.message.received
4. Celery Email Worker consume → envía email via SMTP
5. Actualiza estado del mensaje en DB
6. Si falla → retry con exponential backoff → DLQ
```

### Redis Usos

| Uso | Implementación |
|-----|---------------|
| **Response Cache** | Cache de queries GET con TTL (profile, projects) |
| **Rate Limiting** | Sliding window por IP en endpoints públicos |
| **Session Store** | Sesiones de admin panel |
| **AI Chat Context** | Contexto temporal de conversación (TTL: 30min) |
| **Celery Broker/Backend** | Backend de resultados para Celery |
| **Real-time Pub/Sub** | WebSocket notifications |

---

## 5. Propuesta de Integración de IA

### Funcionalidades AI

| Feature | Descripción | Tecnología |
|---------|------------|------------|
| **AI Chat Assistant** | Chat que responde preguntas sobre tu perfil, skills, proyectos como si fuera "tu representante" | LangChain + RAG |
| **Dynamic CV Generation** | Genera versiones del CV adaptadas al rol que pregunte el recruiter | LLM + Prompt Templates |
| **Smart Contact** | Clasifica mensajes del formulario por prioridad/intención | LLM Classification |
| **Project Summarizer** | Genera resúmenes inteligentes de tus repos de GitHub | LLM + GitHub API |
| **Skill Recommender** | Sugiere skills relevantes basado en tendencias del mercado | LLM + Web Search |

### Arquitectura AI (RAG Pipeline)

```
┌─────────────────────────────────────────────────┐
│                 AI CHAT FLOW                     │
│                                                  │
│  User Question                                   │
│       │                                          │
│       ▼                                          │
│  ┌──────────┐    ┌──────────────────────┐       │
│  │ Classify  │───▶│ Knowledge Base (RAG) │       │
│  │ Intent    │    │                      │       │
│  └──────────┘    │  • CV Data (JSON/MD)  │       │
│                  │  • Project READMEs     │       │
│                  │  • Skills Matrix       │       │
│                  │  • Work Experience     │       │
│                  │  • Blog Posts          │       │
│                  └──────────┬─────────────┘       │
│                             │                    │
│                    Vector Search                  │
│                    (ChromaDB / pgvector)          │
│                             │                    │
│                             ▼                    │
│                  ┌──────────────────────┐        │
│                  │   LLM (Claude API)   │        │
│                  │                      │        │
│                  │  System Prompt:       │        │
│                  │  "Eres el asistente   │        │
│                  │   de David, un Dev    │        │
│                  │   DevOps Engineer..." │        │
│                  │                      │        │
│                  │  + Retrieved Context  │        │
│                  │  + Chat History       │        │
│                  └──────────┬───────────┘        │
│                             │                    │
│                             ▼                    │
│                  Streamed Response                │
│                  (WebSocket → Frontend)           │
└─────────────────────────────────────────────────┘
```

### Modelo de Datos AI

```
Knowledge Base:
├── cv_data.json          # Datos estructurados del CV
├── projects/*.md         # READMEs de cada proyecto
├── skills_matrix.yaml    # Skills con niveles y evidencia
└── embeddings/           # Vectores pre-computados (ChromaDB)
```

---

## 6. Dockerización

### Estrategia Multi-Stage Builds

```dockerfile
# Backend: 3 stages
Stage 1: python-base       → Instala dependencias (uv/poetry)
Stage 2: builder           → Compila wheels
Stage 3: production        → python:3.12-slim, copia solo lo necesario

# Frontend: 2 stages
Stage 1: node-builder      → npm install + vite build
Stage 2: production        → nginx:alpine, copia dist/

# Worker: hereda de backend
Stage 1: Reutiliza backend base
Stage 2: Entrypoint → celery worker
```

### Docker Compose (Servicios)

```
services:
  frontend        → :3000  (React dev / Nginx prod)
  backend         → :8000  (FastAPI + Uvicorn)
  worker          → Celery worker (no expone puerto)
  beat            → Celery Beat scheduler
  postgres        → :5432  (con volume persistente)
  redis           → :6379  (con volume)
  rabbitmq        → :5672 + :15672 (management UI)
  prometheus      → :9090
  grafana         → :3001
```

---

## 7. Kubernetes + Helm + Kustomize

### Estrategia de Deployment

| Concepto | Helm | Kustomize |
|----------|------|-----------|
| **Propósito** | Packaging y releases versionados | Patching por ambiente |
| **Uso** | `helm install portfolio ./helm/portfolio-app` | `kubectl apply -k overlays/prod` |
| **Cuándo** | Release inicial, upgrades, rollbacks | Ajustes finos per-environment |
| **Complemento** | Helm genera los manifests base | Kustomize aplica patches encima |

### Recursos K8s por Servicio

```
Backend:     Deployment + Service + HPA + PDB
Frontend:    Deployment + Service
Worker:      Deployment (sin Service, no recibe tráfico)
PostgreSQL:  StatefulSet + PVC + Service (ClusterIP)
Redis:       Deployment + Service (ClusterIP)
RabbitMQ:    StatefulSet + PVC + Service (ClusterIP)
Ingress:     Nginx Ingress → routing rules
Monitoring:  Prometheus + Grafana Deployments
```

### Helm Values por Ambiente

```yaml
# values-dev.yaml                    # values-prod.yaml
backend:                             backend:
  replicas: 1                          replicas: 3
  resources:                           resources:
    cpu: "250m"                          cpu: "1000m"
    memory: "256Mi"                      memory: "1Gi"
  autoscaling: false                   autoscaling: true
                                       minReplicas: 3
                                       maxReplicas: 10
```

---

## 8. CI/CD Pipeline

```
┌──────────────────────────────────────────────────────────────────┐
│                     GITHUB ACTIONS PIPELINE                       │
│                                                                  │
│  PR / Push to main                                               │
│       │                                                          │
│       ├─► Lint (ruff + eslint)                                   │
│       ├─► Unit Tests (pytest + vitest)                           │
│       ├─► Integration Tests (testcontainers)                     │
│       ├─► Security Scan (Trivy + Snyk)                           │
│       ├─► Build Docker Images (multi-stage)                      │
│       ├─► Push to Registry (tagged: sha + semver)                │
│       ├─► Deploy to Dev (Kustomize overlay)                      │
│       ├─► Smoke Tests                                            │
│       └─► Deploy to Prod (Helm upgrade, manual approval)         │
└──────────────────────────────────────────────────────────────────┘
```

---

## 9. Cronograma de Desarrollo — 10 Semanas


```

---

## 10. Quick Commands (Makefile)

```makefile
make dev          # docker compose up (todo el stack)
make build        # Build todas las imágenes
make test         # Run todos los tests
make lint         # Ruff + ESLint
make migrate      # Alembic upgrade head
make seed         # Poblar DB con datos del CV
make helm-dev     # helm install en minikube
make kust-dev     # kubectl apply -k overlays/dev
make deploy-prod  # Full deploy pipeline
```

---

> **Nota final:** Esta app está diseñada para que cada componente sea una pieza demostrable en entrevistas. El recruiter ve un CV bonito, el tech lead ve Vertical Slice + CQRS + event-driven, el DevOps lead ve Docker + K8s + Helm + CI/CD, y el AI lead ve RAG + LLM integration. Todo en un solo proyecto.
