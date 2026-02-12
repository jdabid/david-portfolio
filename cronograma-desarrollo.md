### Semana 1-2: Foundation & Infrastructure

| Día | Tarea |
|-----|-------|
| **S1 L-M** | Inicializar repos, estructura de carpetas, README |
| **S1 M-J** | Docker Compose con todos los servicios (PG, Redis, RabbitMQ) |
| **S1 V** | Dockerfiles multi-stage (backend + frontend) |
| **S2 L-M** | FastAPI skeleton: config, database, middleware, health checks |
| **S2 M-J** | React skeleton: routing, layout, componentes base, Tailwind setup |
| **S2 V** | Makefile, scripts de setup, verificar que todo levanta con `docker compose up` |

**Entregable:** Stack completo corriendo en Docker local.

---

### Semana 3-4: Core Features (Vertical Slices)

| Día | Tarea |
|-----|-------|
| **S3 L-M** | Slice `profile`: Models, CQRS handlers, endpoints CRUD |
| **S3 M-J** | Slice `projects`: Listado, detalle, filtros |
| **S3 V** | Redis cache layer para queries de profile y projects |
| **S4 L-M** | Slice `contact`: Formulario → Command → RabbitMQ event |
| **S4 M-J** | Celery worker: Email send task con retry logic |
| **S4 V** | Frontend: Pages Home, About, Projects conectadas al API |

**Entregable:** App funcional con CRUD, cache, y messaging.

---

### Semana 5-6: AI Integration & Analytics

| Día | Tarea |
|-----|-------|
| **S5 L-M** | Knowledge base: Estructurar CV data, embeddings con ChromaDB |
| **S5 M-J** | Slice `ai_chat`: RAG pipeline, LangChain + Claude/OpenAI API |
| **S5 V** | WebSocket endpoint para streaming de respuestas AI |
| **S6 L-M** | Frontend: AI Chat UI con streaming, historial |
| **S6 M-J** | Slice `analytics`: Track visits, Celery aggregation tasks |
| **S6 V** | Admin dashboard: Stats de visitas, mensajes, chats |

**Entregable:** AI Chat funcional + analytics básico.

---

### Semana 7-8: Kubernetes & Helm

| Día | Tarea |
|-----|-------|
| **S7 L-M** | K8s manifests base: Deployments, Services, ConfigMaps |
| **S7 M-J** | Helm chart: templates, values, helpers |
| **S7 V** | Kustomize overlays: dev, staging, prod |
| **S8 L-M** | Ingress controller + TLS config |
| **S8 M-J** | HPA (autoscaling), PDB, resource limits |
| **S8 V** | Deploy completo en Minikube/Kind, validar todos los servicios |

**Entregable:** App desplegada en K8s local con Helm + Kustomize.

---

### Semana 9: CI/CD & Monitoring

| Día | Tarea |
|-----|-------|
| **S9 L** | GitHub Actions: CI pipeline (lint, test, build) |
| **S9 M** | GitHub Actions: CD pipeline (push images, deploy) |
| **S9 M** | Security scanning (Trivy para imágenes) |
| **S9 J** | Prometheus + Grafana: métricas de backend y K8s |
| **S9 V** | Dashboards Grafana, alertas básicas |

**Entregable:** Pipeline CI/CD completo + monitoring.

---

### Semana 10: Polish, Testing & Documentation

| Día | Tarea |
|-----|-------|
| **S10 L** | Tests unitarios (pytest + vitest) — cobertura mínima 70% |
| **S10 M** | Tests de integración (testcontainers) |
| **S10 M** | Frontend polish: animaciones, responsive, performance |
| **S10 J** | Documentación: Architecture docs, API docs, runbooks |
| **S10 V** | README profesional con badges, diagrams, demo GIF |

**Entregable:** App production-ready, documentada, testeada.

---

### Resumen del Cronograma

```
S1-2  ████████████████░░░░░░░░░░░░░░░░░░░░░░░░  Foundation & Infra
S3-4  ░░░░░░░░░░░░░░░░████████████████░░░░░░░░  Core Features + CQRS
S5-6  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░████████  AI + Analytics
S7-8  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  K8s + Helm + Kustomize
S9    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  CI/CD + Monitoring
S10   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  Testing + Docs + Polish