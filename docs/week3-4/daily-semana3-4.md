# Daily Log — Semana 3-4: Core Features (Vertical Slices)

---

## S3 Lunes-Martes: Slice `profile` — Models, CQRS handlers, CRUD

### Que se hizo
- Modelos SQLAlchemy: `Profile`, `Skill`, `Experience`, `Education` en `backend/app/features/profile/models.py`
- Schemas Pydantic: `ProfileResponse`, `UpdateProfileRequest`, `SkillResponse`, etc. en `schemas.py`
- CQRS Mediator en `backend/app/shared/mediator.py` — dispatcher generico de Commands y Queries
- Command `UpdateProfileCommand` con handler que persiste en PG e invalida cache Redis
- Query `GetProfileQuery` con cache-aside pattern (Redis → PG → Redis)
- Query `GetSkillsQuery` con agrupacion por categoria
- Domain Event `ProfileUpdatedEvent` publicado a RabbitMQ
- Router con 3 endpoints: `GET /api/profile`, `GET /api/profile/skills`, `PATCH /api/profile/{id}`

### Por que se hizo asi

**Mediator Pattern para CQRS**
Se creo un mediator simple (`shared/mediator.py`) en lugar de usar una libreria como `mediatr-py`. El mediator mantiene dos registros (`_command_handlers`, `_query_handlers`) y cada handler se auto-registra al importarse. Esto mantiene los handlers desacoplados de los routers — el router solo conoce el Command/Query DTO y el mediator, no la implementacion del handler.

**Cache-aside en queries**
El pattern cache-aside en `get_profile.py` sigue el flujo: check Redis → miss → query PostgreSQL → store in Redis con TTL. La alternativa (write-through) seria escribir al cache en cada command, pero cache-aside es mas simple y tolerante a fallos de Redis — si Redis cae, la app sigue funcionando con queries directas a PG.

**Schemas separados de Models**
Los schemas Pydantic (`schemas.py`) son DTOs separados de los modelos SQLAlchemy (`models.py`). Esto permite que la API retorne una forma diferente a como se almacenan los datos. Por ejemplo, `ProfileResponse` incluye `skills`, `experiences` y `educations` como listas anidadas, mientras que en la DB son tablas separadas con foreign keys.

**selectinload para evitar N+1**
En `get_profile.py` se usa `selectinload(Profile.skills)` en lugar de lazy loading. Sin esto, acceder a `profile.skills` generaria una query separada por cada relacion (N+1 problem). `selectinload` hace UNA query por relacion usando `WHERE skill.profile_id IN (...)`.

---

## S3 Miercoles-Jueves: Slice `projects` — Listado, detalle, filtros

### Que se hizo
- Modelo `Project` con campos: title, slug, description, tags (ARRAY), featured flag, sort_order
- Command `CreateProjectCommand` para crear proyectos
- Query `ListProjectsQuery` con filtros por tag y featured flag
- Query `GetProjectDetailQuery` por slug (URL-friendly)
- Router con 3 endpoints: `GET /api/projects`, `GET /api/projects/{slug}`, `POST /api/projects`
- Cache Redis en ambos queries con keys contextuales (`projects:list:tag=X:featured=Y`)

### Por que se hizo asi

**PostgreSQL ARRAY para tags**
Se uso `ARRAY(String)` en lugar de una tabla many-to-many `project_tags`. Para un portfolio con <50 proyectos, ARRAY es mas simple y performante — un solo query sin JOINs. PostgreSQL permite filtrar con `.any()` sobre arrays. Si fueran miles de proyectos con queries complejas por tags, una tabla de tags con indice seria mejor.

**Slug como identificador publico**
Los endpoints de detalle usan `slug` en lugar de UUID (`/api/projects/portfolio-cv` vs `/api/projects/550e8400-...`). Los slugs son URL-friendly, SEO-friendly, y legibles. El UUID se mantiene como PK interno en la DB.

**Cache keys contextuales**
El cache key incluye los parametros del filtro: `projects:list:tag=Python:featured=True`. Esto evita retornar resultados cacheados con filtros diferentes. La invalidacion usa `cache_delete("projects:*")` que borra TODAS las variantes del cache cuando se crea un proyecto nuevo.

---

## S3 Viernes: Redis cache layer

### Que se hizo
- Servicio de cache centralizado en `backend/app/infrastructure/cache.py`
- Funciones `cache_get`, `cache_set`, `cache_delete` con manejo de errores graceful
- Decorador `@cached(prefix, ttl)` para queries frecuentes
- TTLs configurables por query (profile: 10min, projects: 5min)
- Invalidacion de cache en los command handlers

### Por que se hizo asi

**Cache como servicio, no como decorator obligatorio**
Se proporcionaron tanto funciones directas (`cache_get/set/delete`) como un decorator (`@cached`). Los handlers de profile y projects usan las funciones directas porque necesitan control granular sobre el cache key y la logica de serializacion. El decorator es para queries simples sin logica custom.

**Graceful degradation**
Todos los metodos de cache tienen try/except que loggean warnings en lugar de propagar excepciones. Si Redis se cae, la app NO crashea — simplemente pasa a queries directas a PostgreSQL. Esto es critico para resiliencia en produccion.

**scan_iter para invalidacion por patron**
`cache_delete` usa `scan_iter` en lugar de `KEYS *` para buscar keys que matchean un patron. `KEYS` bloquea Redis y es O(N) sobre TODAS las keys. `scan_iter` es incremental y no bloquea, haciendolo safe para produccion.

---

## S4 Lunes-Martes: Slice `contact` — Formulario + RabbitMQ event

### Que se hizo
- Modelo `ContactMessage` con campos: name, email, subject, message, status (pending/sent/failed)
- Command `SendMessageCommand` que persiste el mensaje y publica evento a RabbitMQ
- Domain Event `MessageReceivedEvent` con routing key `contact.message.received`
- Event Bus generico (`shared/event_bus.py`) con aio-pika para AMQP async
- Router `POST /api/contact` que retorna 202 Accepted

### Por que se hizo asi

**202 Accepted en lugar de 200 OK**
El endpoint retorna `202 Accepted` porque el email NO se envia en el request. Se encola para procesamiento async. 202 indica "recibimos tu request, la vamos a procesar despues". Esto es correcto semanticamente y mantiene el response time bajo (<100ms) independientemente de cuanto tarde el email.

**Event-driven desacoplamiento**
El command handler NO llama directamente al email service. Publica un evento a RabbitMQ y un Celery worker lo consume. Esto desacopla el "guardar mensaje" del "enviar email". Si el email service falla, el mensaje ya esta persistido en PG con status `pending`. El worker puede reintentar sin perdida de datos.

**aio-pika para publicacion async**
Se eligio aio-pika sobre pika porque el backend es async. Publicar un evento con pika (sync) dentro de un handler async bloquea el event loop. aio-pika es nativo asyncio y se integra naturalmente con FastAPI.

---

## S4 Miercoles-Jueves: Celery worker — Email send task con retry

### Que se hizo
- Celery app configuration en `backend/app/infrastructure/celery_app.py`
- Task `send_contact_email` con retry exponential backoff (60s, 120s, 240s)
- Worker entrypoint en `backend/workers/celery_worker.py`
- Task routing: `contact.send_email` → queue `email.send`
- Helper `_update_message_status` para actualizar estado del mensaje en DB desde el worker

### Por que se hizo asi

**Exponential backoff en retries**
El task usa `retry_backoff=True` con `retry_backoff_max=600`. El primer retry es a los 60s, el segundo a 120s, el tercero a 240s. Esto evita bombardear un SMTP server caido con retries constantes (que podrian causar rate limiting o blacklisting). El backoff exponencial es una best practice para sistemas distribuidos.

**task_acks_late + worker_prefetch_multiplier=1**
`task_acks_late=True` significa que el mensaje de RabbitMQ solo se confirma DESPUES de que el task completa exitosamente. Si el worker crashea a mitad del task, el mensaje vuelve a la queue. `worker_prefetch_multiplier=1` asegura que cada worker solo toma un task a la vez, evitando que un worker lento acumule tasks.

**Sync DB helper en el worker**
El helper `_update_message_status` usa SQLAlchemy sync (no async) porque Celery workers corren en un contexto sync. Crear un engine sync temporal para una sola query es mas simple que configurar un event loop dentro del worker.

---

## S4 Viernes: Frontend conectado al API

### Que se hizo
- TypeScript interfaces en `frontend/src/types/index.ts` para Profile, Project, Contact
- API client completo en `frontend/src/services/api.ts` con typed requests
- Custom hook `useApi<T>` en `frontend/src/hooks/useApi.ts` para fetch generico
- Home page conectada al API con datos dinamicos del profile
- About page con skills desde API + experience timeline
- Projects page con filtros por tag (client-side) conectados al API
- Contact page con formulario completo y estados (idle, sending, sent, error)
- Actualizados App.tsx y Navbar.tsx con ruta `/contact`

### Por que se hizo asi

**Fallback data en cada page**
Cada page tiene datos hardcoded como fallback (`fallbackProjects`, `fallbackSkills`). Si el API no responde (primera vez sin DB seed, o API caida), el frontend sigue mostrando contenido. Esto es UX resiliente — el portfolio nunca muestra una pagina en blanco.

**useApi hook generico**
El hook `useApi<T>` encapsula el patron fetch-loading-error en un solo lugar. Retorna `{ data, loading, error }` y maneja cleanup con `cancelled` flag para evitar state updates en componentes desmontados. Esto elimina duplicacion de logica en cada page.

**Contact form con 202 Accepted flow**
El formulario cambia entre 4 estados: `idle` → `sending` → `sent` / `error`. El estado `sent` muestra un mensaje de confirmacion y la opcion de enviar otro. Esto matchea con el backend que retorna 202 (el email se procesa async, no podemos confirmar que se envio en el momento).
