Archivos creados — Semana 3-4                                                                                                                                                                                                       
                                                                                                                                                                                                                                        
  Shared Kernel (4 archivos nuevos)                                                                                                                                                                                                     
  ┌─────────────────────────────────────┬──────────────────────────────────────────────────────────────────────────┐
  │               Archivo               │                                Proposito                                 │                                                                                                                    
  ├─────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────┤                                                                                                                    
  │ backend/app/shared/mediator.py      │ CQRS dispatcher — registra y despacha Commands/Queries a handlers        │                                                                                                                    
  ├─────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
  │ backend/app/shared/event_bus.py     │ Publica Domain Events a RabbitMQ via aio-pika                            │
  ├─────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
  │ backend/app/shared/pagination.py    │ Utilidades de paginacion para list endpoints                             │
  ├─────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
  │ backend/app/infrastructure/cache.py │ Redis cache-aside: cache_get, cache_set, cache_delete, decorator @cached │
  └─────────────────────────────────────┴──────────────────────────────────────────────────────────────────────────┘
  S3 L-M: Slice profile (8 archivos)
  ┌─────────────────────────────────────────────┬────────────────────────────────────────────────────────────┐
  │                   Archivo                   │                         Proposito                          │
  ├─────────────────────────────────────────────┼────────────────────────────────────────────────────────────┤
  │ features/profile/models.py                  │ 4 modelos: Profile, Skill, Experience, Education           │
  ├─────────────────────────────────────────────┼────────────────────────────────────────────────────────────┤
  │ features/profile/schemas.py                 │ DTOs Pydantic: ProfileResponse, UpdateProfileRequest, etc. │
  ├─────────────────────────────────────────────┼────────────────────────────────────────────────────────────┤
  │ features/profile/commands/update_profile.py │ Command: actualiza perfil + invalida cache                 │
  ├─────────────────────────────────────────────┼────────────────────────────────────────────────────────────┤
  │ features/profile/queries/get_profile.py     │ Query: Redis cache-aside → PG con selectinload             │
  ├─────────────────────────────────────────────┼────────────────────────────────────────────────────────────┤
  │ features/profile/queries/get_skills.py      │ Query: skills agrupados por categoria con cache            │
  ├─────────────────────────────────────────────┼────────────────────────────────────────────────────────────┤
  │ features/profile/events/profile_updated.py  │ Domain Event → RabbitMQ                                    │
  ├─────────────────────────────────────────────┼────────────────────────────────────────────────────────────┤
  │ features/profile/router.py                  │ 3 endpoints: GET profile, GET skills, PATCH profile        │
  └─────────────────────────────────────────────┴────────────────────────────────────────────────────────────┘
  S3 M-J: Slice projects (7 archivos)
  ┌─────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────┐
  │                     Archivo                     │                          Proposito                           │
  ├─────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤
  │ features/projects/models.py                     │ Modelo Project con ARRAY tags, slug, featured                │
  ├─────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤
  │ features/projects/schemas.py                    │ DTOs: ProjectResponse, ProjectListItem, CreateProjectRequest │
  ├─────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤
  │ features/projects/commands/create_project.py    │ Command: crea proyecto + invalida cache                      │
  ├─────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤
  │ features/projects/queries/list_projects.py      │ Query: filtros por tag/featured, cache contextual            │
  ├─────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤
  │ features/projects/queries/get_project_detail.py │ Query: detalle por slug con cache                            │
  ├─────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤
  │ features/projects/router.py                     │ 3 endpoints: GET list, GET detail, POST create               │
  └─────────────────────────────────────────────────┴──────────────────────────────────────────────────────────────┘
  S4 L-M: Slice contact + Events (6 archivos)
  ┌─────────────────────────────────────────────┬───────────────────────────────────────────────────────────┐
  │                   Archivo                   │                         Proposito                         │
  ├─────────────────────────────────────────────┼───────────────────────────────────────────────────────────┤
  │ features/contact/models.py                  │ ContactMessage con status (pending/sent/failed)           │
  ├─────────────────────────────────────────────┼───────────────────────────────────────────────────────────┤
  │ features/contact/schemas.py                 │ SendMessageRequest, ContactMessageResponse                │
  ├─────────────────────────────────────────────┼───────────────────────────────────────────────────────────┤
  │ features/contact/commands/send_message.py   │ Command: persiste → publica evento a RabbitMQ             │
  ├─────────────────────────────────────────────┼───────────────────────────────────────────────────────────┤
  │ features/contact/events/message_received.py │ Domain Event con routing key contact.message.received     │
  ├─────────────────────────────────────────────┼───────────────────────────────────────────────────────────┤
  │ features/contact/tasks/send_email.py        │ Celery task con retry exponential backoff (60s/120s/240s) │
  ├─────────────────────────────────────────────┼───────────────────────────────────────────────────────────┤
  │ features/contact/router.py                  │ POST /api/contact → 202 Accepted                          │
  └─────────────────────────────────────────────┴───────────────────────────────────────────────────────────┘
  S4 M-J: Celery Worker (2 archivos)
  ┌──────────────────────────────────────────┬──────────────────────────────────────────────────────────────────┐
  │                 Archivo                  │                            Proposito                             │
  ├──────────────────────────────────────────┼──────────────────────────────────────────────────────────────────┤
  │ backend/app/infrastructure/celery_app.py │ Celery config: broker RabbitMQ, backend Redis, routing, ack_late │
  ├──────────────────────────────────────────┼──────────────────────────────────────────────────────────────────┤
  │ backend/workers/celery_worker.py         │ Worker entrypoint                                                │
  └──────────────────────────────────────────┴──────────────────────────────────────────────────────────────────┘
  S4 V: Frontend conectado al API (7 archivos nuevos/actualizados)
  ┌───────────────────────────────────────┬────────────────────────────────────────────────────────────────┐
  │                Archivo                │                           Proposito                            │
  ├───────────────────────────────────────┼────────────────────────────────────────────────────────────────┤
  │ frontend/src/types/index.ts           │ TypeScript interfaces: Profile, Project, ContactMessage, etc.  │
  ├───────────────────────────────────────┼────────────────────────────────────────────────────────────────┤
  │ frontend/src/services/api.ts          │ API client tipado: getProfile, getProjects, sendContactMessage │
  ├───────────────────────────────────────┼────────────────────────────────────────────────────────────────┤
  │ frontend/src/hooks/useApi.ts          │ Hook generico useApi<T> con loading/error/data                 │
  ├───────────────────────────────────────┼────────────────────────────────────────────────────────────────┤
  │ frontend/src/pages/Home/index.tsx     │ Datos dinamicos desde API + fallback                           │
  ├───────────────────────────────────────┼────────────────────────────────────────────────────────────────┤
  │ frontend/src/pages/About/index.tsx    │ Skills desde API + Experience timeline                         │
  ├───────────────────────────────────────┼────────────────────────────────────────────────────────────────┤
  │ frontend/src/pages/Projects/index.tsx │ Filtros por tag + datos desde API                              │
  ├───────────────────────────────────────┼────────────────────────────────────────────────────────────────┤
  │ frontend/src/pages/Contact/index.tsx  │ Formulario con estados idle/sending/sent/error                 │
  └───────────────────────────────────────┴────────────────────────────────────────────────────────────────┘
  Actualizados
  ┌───────────────────────────────────────────┬───────────────────────────────────────────────────┐
  │                  Archivo                  │                      Cambio                       │
  ├───────────────────────────────────────────┼───────────────────────────────────────────────────┤
  │ backend/app/main.py                       │ Registra routers + importa handlers para mediator │
  ├───────────────────────────────────────────┼───────────────────────────────────────────────────┤
  │ backend/pyproject.toml                    │ Agrega aio-pika>=9.4.0                            │
  ├───────────────────────────────────────────┼───────────────────────────────────────────────────┤
  │ frontend/src/App.tsx                      │ Agrega ruta /contact                              │
  ├───────────────────────────────────────────┼───────────────────────────────────────────────────┤
  │ frontend/src/components/layout/Navbar.tsx │ Agrega link Contact                               │
  └───────────────────────────────────────────┴───────────────────────────────────────────────────┘
  Documentacion
  ┌──────────────────────────────────────┬─────────────────────────────────────────────────────────────────┐
  │               Archivo                │                            Proposito                            │
  ├──────────────────────────────────────┼─────────────────────────────────────────────────────────────────┤
  │ docs/week3-4/daily-semana3-4.md      │ Daily log: QUE se hizo + POR QUE para cada dia                  │
  ├──────────────────────────────────────┼─────────────────────────────────────────────────────────────────┤
  │ docs/week3-4/entrevista-semana3-4.md │ 10 preguntas de entrevista con respuestas y ubicacion en codigo │
  └──────────────────────────────────────┴─────────────────────────────────────────────────────────────────┘
  ---
  Endpoints API disponibles (Semana 3-4)

  GET    /api/health              → Health check
  GET    /api/profile             → Perfil completo con skills/experience
  GET    /api/profile/skills      → Skills agrupados por categoria
  PATCH  /api/profile/{id}        → Actualizar perfil (parcial)
  GET    /api/projects             → Listar proyectos (?tag=X&featured=true)
  GET    /api/projects/{slug}      → Detalle de proyecto
  POST   /api/projects             → Crear proyecto
  POST   /api/contact              → Enviar mensaje (202 Accepted → async email)