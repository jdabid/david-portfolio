# 10 Preguntas de Entrevista — Semana 3-4: Core Features

---

## 1. ¿Que es CQRS y como lo implementaste en este proyecto?

**Respuesta:**
CQRS (Command Query Responsibility Segregation) separa las operaciones de escritura (Commands) de las de lectura (Queries). Los Commands mutan estado y retornan confirmacion. Los Queries solo leen datos y nunca mutan estado. Cada uno puede tener su propio modelo de datos, storage, y optimizaciones.

**Donde se implemento:**
- `backend/app/shared/mediator.py` — Mediator que registra y despacha Commands y Queries a sus handlers
- `backend/app/features/profile/commands/update_profile.py` — Command que escribe a PostgreSQL e invalida cache
- `backend/app/features/profile/queries/get_profile.py` — Query que lee primero de Redis, fallback a PostgreSQL
- `backend/app/features/projects/queries/list_projects.py` — Query con filtros que usa cache contextual

**Por que importa:**
CQRS permite optimizar lectura y escritura independientemente. Las queries pueden usar cache agresivo porque no mutan estado. Los commands pueden validar reglas de negocio sin preocuparse por performance de lectura. En este proyecto, las lecturas van a Redis (microsegundos) mientras las escrituras van a PostgreSQL (milisegundos).

---

## 2. ¿Que es el patron cache-aside y que alternativas existen?

**Respuesta:**
Cache-aside (lazy loading): la aplicacion consulta el cache → si hay miss, consulta la DB → almacena el resultado en cache → retorna al cliente. Es la app quien decide cuando leer y escribir el cache.

Alternativas:
- **Write-through:** cada escritura a la DB tambien escribe al cache. El cache siempre esta actualizado pero cada write es mas lento.
- **Write-behind:** las escrituras van primero al cache y luego asincronamente a la DB. Mas rapido pero riesgo de perdida de datos.
- **Read-through:** el cache consulta la DB automaticamente en un miss. Similar a cache-aside pero la logica vive en el cache, no en la app.

**Donde se implemento:**
- `backend/app/features/profile/queries/get_profile.py:24-30` — `cache_get(CACHE_KEY)` → miss → query DB → `cache_set(CACHE_KEY, data, CACHE_TTL)`
- `backend/app/infrastructure/cache.py` — Las funciones `cache_get` y `cache_set` encapsulan el patron
- Invalidacion: `backend/app/features/profile/commands/update_profile.py:36` — `cache_delete("profile:*")` al mutar datos

**Por que importa:**
Cache-aside es el patron mas comun porque es simple, tolerante a fallos (si Redis cae, la app sigue), y no requiere infraestructura extra. Para un portfolio con pocas escrituras y muchas lecturas, es la eleccion optima.

---

## 3. ¿Como funciona el Mediator pattern y por que lo usas para CQRS?

**Respuesta:**
El Mediator centraliza la comunicacion entre objetos. En lugar de que los routers conozcan y llamen directamente a los handlers, envian un Command/Query al Mediator que lo despacha al handler registrado. Esto desacopla el "que hacer" (DTO) del "como hacerlo" (handler).

**Donde se implemento:**
- `backend/app/shared/mediator.py` — Dos diccionarios: `_command_handlers[type] = handler`, `_query_handlers[type] = handler`
- Los handlers se auto-registran al importarse: `register_command_handler(UpdateProfileCommand, handle_update_profile)`
- Los routers despachan via `send_command(command)` y `send_query(query)` sin conocer el handler
- `backend/app/main.py:20-26` — Los handlers se importan en el lifespan para que se registren con el mediator

**Por que importa:**
Sin mediator, el router tendria `from app.features.profile.commands.update_profile import handle_update_profile` y lo llamaria directamente. Con mediator, el router solo conoce `UpdateProfileCommand` y `send_command`. Esto permite intercambiar handlers (testing), agregar cross-cutting concerns (logging, validation), y mantener los routers como una capa thin.

---

## 4. ¿Que es un Domain Event y como fluye desde el backend hasta el worker?

**Respuesta:**
Un Domain Event es una notificacion de que algo relevante ocurrio en el dominio. Se publica despues de que el estado muta exitosamente. Es inmutable y contiene los datos necesarios para que cualquier consumidor actue.

**Flujo completo:**
1. `POST /api/contact` → Router llama `send_command(SendMessageCommand)`
2. Handler persiste `ContactMessage` en PostgreSQL con status `pending`
3. Handler llama `emit_message_received()` que publica `MessageReceivedEvent` a RabbitMQ
4. RabbitMQ enruta el mensaje via topic exchange `portfolio.events` con routing key `contact.message.received`
5. Celery worker consume de la queue `email.send` y ejecuta `send_contact_email` task
6. Task envia el email y actualiza el status a `sent` en PostgreSQL

**Donde se implemento:**
- `backend/app/features/contact/commands/send_message.py:32` — Llama a `emit_message_received()`
- `backend/app/features/contact/events/message_received.py` — Define el evento y lo publica
- `backend/app/shared/event_bus.py:28-45` — `publish_event()` usa aio-pika para publicar a RabbitMQ
- `backend/app/features/contact/tasks/send_email.py` — Celery task que consume el evento

**Por que importa:**
Sin eventos, el command handler tendria que llamar directamente al email service (acoplamiento fuerte). Con eventos, si mañana quieres agregar un "notificar en Slack" ademas del email, solo agregas un nuevo consumer — no tocas el command handler.

---

## 5. ¿Como implementas retry con exponential backoff en Celery y por que?

**Respuesta:**
Exponential backoff incrementa el tiempo de espera entre retries: 60s → 120s → 240s. Se usa para evitar sobrecargar un servicio caido con retries constantes (thundering herd). Celery lo implementa nativamente con `retry_backoff=True`.

**Donde se implemento:**
- `backend/app/features/contact/tasks/send_email.py:18-25`:
  ```python
  @celery_app.task(
      bind=True,
      max_retries=3,
      default_retry_delay=60,
      autoretry_for=(smtplib.SMTPException, ConnectionError),
      retry_backoff=True,
      retry_backoff_max=600,
  )
  ```
- `bind=True` permite acceder a `self.retry(exc=exc)` para reintentar manualmente
- `autoretry_for` reintenta automaticamente para excepciones especificas
- `retry_backoff_max=600` pone un tope de 10 minutos entre retries

**Por que importa:**
Sin backoff, 3 retries a 60s cada uno significan 3 intentos en 3 minutos contra un servidor que probablemente sigue caido. Con backoff, los intentos se espacian (60s, 120s, 240s = ~7 minutos total), dando mas tiempo al servicio para recuperarse. El `max_retries=3` evita retries infinitos — despues del tercero, el task falla definitivamente y el mensaje queda con status `failed`.

---

## 6. ¿Por que usas `task_acks_late=True` en Celery y que problema resuelve?

**Respuesta:**
Por defecto, Celery confirma (ACK) el mensaje de la queue ANTES de ejecutar el task. Si el worker crashea a mitad del task, el mensaje ya fue consumido y se pierde. Con `task_acks_late=True`, el ACK se envia DESPUES de que el task completa exitosamente. Si el worker crashea, el mensaje vuelve a la queue y otro worker lo procesa.

**Donde se implemento:**
- `backend/app/infrastructure/celery_app.py:25-28`:
  ```python
  task_acks_late=True,
  worker_prefetch_multiplier=1,
  task_reject_on_worker_lost=True,
  ```
- `worker_prefetch_multiplier=1` complementa el ack late — cada worker solo toma 1 task, evitando que un worker lento acumule tasks que no puede procesar

**Por que importa:**
En un sistema de envio de emails, perder un mensaje significa que un usuario que envio un formulario de contacto nunca recibe respuesta. Con ack late, la garantia es "at-least-once delivery" — el email puede enviarse mas de una vez (si el worker crashea justo despues de enviar pero antes del ACK), pero nunca se pierde. Para emails, duplicados son preferibles a no-envio.

---

## 7. ¿Que es Vertical Slice Architecture y como se diferencia de la arquitectura por capas?

**Respuesta:**
En **capas**: el codigo se organiza por tipo tecnico (`controllers/`, `services/`, `repositories/`). Agregar un feature requiere tocar archivos en 4-5 carpetas.

En **slices**: el codigo se organiza por feature (`profile/`, `projects/`, `contact/`). Todo lo relacionado a un feature esta en una carpeta: modelos, schemas, handlers, eventos, router.

**Donde se implemento:**
- `backend/app/features/profile/` — Contiene models, schemas, commands/, queries/, events/, router.py
- `backend/app/features/projects/` — Misma estructura, completamente independiente
- `backend/app/features/contact/` — Misma estructura, con tasks/ adicional para Celery
- `backend/app/shared/` — Solo lo genuinamente compartido: base_model, mediator, event_bus, pagination

**Por que importa:**
Con slices, dos developers pueden trabajar en `profile/` y `projects/` simultaneamente sin conflictos de merge (no tocan los mismos archivos). Cada slice es testeable aisladamente. Si decides remover el feature `contact`, borras una carpeta — no tienes que buscar en 5 archivos diferentes que lineas pertenecen a contact.

---

## 8. ¿Como resuelves el problema N+1 en SQLAlchemy async?

**Respuesta:**
El N+1 ocurre cuando acceder a una relacion lazy-loaded genera una query por cada registro. Si tienes 1 profile con 10 skills, haces 1 query para el profile + 10 queries para los skills = 11 queries. Con `selectinload`, se hacen 2 queries: 1 para profile + 1 para TODOS los skills.

**Donde se implemento:**
- `backend/app/features/profile/queries/get_profile.py:33-38`:
  ```python
  select(Profile).options(
      selectinload(Profile.skills),
      selectinload(Profile.experiences),
      selectinload(Profile.educations),
  )
  ```
- Esto genera 4 queries totales (1 profile + 1 skills + 1 experiences + 1 educations) en lugar de 1 + N + M + K

**Por que importa:**
Con lazy loading, si un profile tiene 5 skills, 3 experiences y 2 educations, serian 11 queries. Con selectinload son 4. La diferencia se amplifica con mas datos — 100 skills serian 101 queries vs 4. Ademas, en SQLAlchemy async, lazy loading no esta soportado por defecto (lanza `MissingGreenlet` error), asi que eager loading es obligatorio.

---

## 9. ¿Como funciona la comunicacion frontend-backend y como manejas errores de red?

**Respuesta:**
El frontend usa `fetch()` con un client wrapper tipado. Cada API call retorna un tipo TypeScript especifico. Los errores se manejan en tres capas: el API client lanza excepciones tipadas, el hook `useApi` captura y expone el error, y cada page decide como mostrarlo.

**Donde se implemento:**
- `frontend/src/services/api.ts:5-14` — Wrapper `request<T>()` que valida `res.ok` y lanza `Error` con status code
- `frontend/src/hooks/useApi.ts` — Hook generico que maneja `loading`, `error`, `data` y cleanup de componentes desmontados
- `frontend/src/pages/Projects/index.tsx:21` — `const displayProjects = projects ?? fallbackProjects` — si la API falla, muestra datos fallback
- `frontend/src/pages/Contact/index.tsx:17-20` — Maneja estado `error` con mensaje visible al usuario

**Por que importa:**
Un portfolio no puede mostrar paginas en blanco si la API esta caida. El patron de fallback data asegura que el contenido siempre se muestra. El hook `useApi` con `cancelled` flag evita memory leaks por state updates en componentes desmontados (React strict mode lo detecta en dev).

---

## 10. ¿Por que el endpoint de contacto retorna 202 en lugar de 200 y que implica para el cliente?

**Respuesta:**
HTTP 202 Accepted significa "la request fue aceptada para procesamiento, pero no se ha completado". 200 OK significaria "el email se envio exitosamente", lo cual es falso — el email se encola en RabbitMQ y un Celery worker lo procesara asincronamente.

**Donde se implemento:**
- `backend/app/features/contact/router.py:15` — `@router.post("", status_code=202)`
- El response incluye `{ "id": "...", "status": "pending", "detail": "Message received. Email will be sent shortly." }`
- El frontend maneja esto en `Contact/index.tsx` mostrando un mensaje de "Message sent!" que realmente significa "received and queued"

**Por que importa:**
Usar el status code correcto es semantica HTTP. Si retornaras 200, el cliente asume que todo se completo. Con 202, el cliente sabe que la operacion es eventual. Esto abre la puerta a implementar polling (`GET /api/contact/{id}/status`) o WebSocket notifications para informar cuando el email realmente se envio. Es la base para sistemas asincrono correctos.
