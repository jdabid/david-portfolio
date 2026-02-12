# 10 Preguntas de Entrevista — Semana 1

Cada pregunta incluye: la respuesta tecnica, donde se implemento en el proyecto, y por que importa.

---

## 1. ¿Que es un multi-stage build en Docker y por que lo usarias?

**Respuesta:**
Un multi-stage build permite definir multiples `FROM` statements en un solo Dockerfile. Cada stage puede copiar artifacts del anterior usando `COPY --from=`. El objetivo es separar el entorno de build del entorno de runtime para que la imagen final sea lo mas pequena posible.

**Donde se implemento:**
- `backend/Dockerfile` — 3 stages: `base` (instala deps), `development` (agrega devtools), `production` (copia solo el codigo y las deps de runtime)
- `frontend/Dockerfile` — 3 stages: `development` (vite dev), `builder` (npm run build), `production` (nginx:alpine con el dist/)

**Por que importa:**
La imagen de desarrollo del backend pesa ~1.2GB. Con multi-stage, la imagen de produccion pesa ~200MB. Imagenes mas pequenas significan deploys mas rapidos, menos storage en el registry, y menor superficie de ataque (menos paquetes instalados = menos vulnerabilidades).

---

## 2. ¿Como manejas la configuracion de una aplicacion en diferentes ambientes (dev, staging, prod)?

**Respuesta:**
Usando variables de entorno validadas al startup con un esquema tipado. En Python, `pydantic-settings` permite definir un modelo con tipos, valores por defecto, y validacion automatica. Las variables se cargan de `.env` en desarrollo y de ConfigMaps/Secrets en Kubernetes.

**Donde se implemento:**
- `backend/app/config.py` — La clase `Settings(BaseSettings)` define todas las variables (DB, Redis, RabbitMQ) con tipos y defaults. Las properties `database_url`, `redis_url` y `rabbitmq_url` construyen las connection strings.
- `.env.example` — Template con todas las variables documentadas.
- `infra/docker/docker-compose.yml` — `env_file: ../../.env` inyecta las variables al container.

**Por que importa:**
Si un developer olvida configurar `POSTGRES_PASSWORD`, la app falla inmediatamente al startup con un error de validacion claro, en lugar de fallar en runtime cuando se intente conectar a la DB. Esto sigue el principio de "fail fast".

---

## 3. ¿Que es un healthcheck en Docker Compose y por que es necesario?

**Respuesta:**
Un healthcheck es un comando que Docker ejecuta periodicamente para verificar que un container esta funcionando correctamente. `depends_on` con `condition: service_healthy` asegura que los servicios dependientes no arranquen hasta que sus dependencias esten realmente listas (no solo "iniciadas").

**Donde se implemento:**
- `infra/docker/docker-compose.yml`:
  - PostgreSQL: `pg_isready -U portfolio_user -d portfolio_db`
  - Redis: `redis-cli ping`
  - RabbitMQ: `rabbitmq-diagnostics -q ping`
  - Backend depende de los 3 con `condition: service_healthy`

**Por que importa:**
Sin healthchecks, `depends_on` solo espera a que el container inicie, no a que el servicio dentro este listo. PostgreSQL puede tardar 5-10 segundos en aceptar conexiones despues de iniciar el container. Sin healthcheck, el backend crashea al intentar conectar y requiere restart manual.

---

## 4. ¿Que patron de arquitectura sigues en el backend y por que?

**Respuesta:**
Vertical Slice Architecture con CQRS. En lugar de organizar por capas tecnicas (controllers, services, repositories), se organiza por features. Cada feature (profile, projects, contact, etc.) contiene sus propios models, schemas, commands, queries, events y router. CQRS separa las operaciones de lectura y escritura.

**Donde se implemento:**
- `backend/app/features/` — Cada subdirectorio es un slice auto-contenido con su propia estructura: `commands/`, `queries/`, `events/`, `models.py`, `schemas.py`, `router.py`
- `backend/app/shared/` — Kernel compartido con `base_model.py` (mixins comunes)

**Por que importa:**
En arquitectura por capas, agregar un feature requiere tocar 4-5 archivos en diferentes carpetas. Con slices, todo lo relacionado a un feature esta junto. Esto mejora la cohesion (alta cohesion dentro del slice), reduce el acoplamiento (cada slice es independiente), y facilita que multiples developers trabajen en paralelo sin conflictos de merge.

---

## 5. ¿Por que usas async/await en FastAPI con SQLAlchemy?

**Respuesta:**
FastAPI es un framework async-native que usa `asyncio`. Si usas operaciones de DB sincronas, cada query bloquea el event loop, impidiendo que se procesen otros requests. Con SQLAlchemy 2.0 async + asyncpg, las queries de DB son non-blocking — el event loop puede manejar otros requests mientras espera la respuesta de PostgreSQL.

**Donde se implemento:**
- `backend/app/infrastructure/database.py` — `create_async_engine()` con driver `asyncpg`, `async_sessionmaker` con `AsyncSession`
- `backend/app/config.py` — Connection string usa `postgresql+asyncpg://`
- `backend/pyproject.toml` — Dependencias: `sqlalchemy[asyncio]`, `asyncpg`

**Por que importa:**
En un endpoint que hace una query de 50ms, un server sync puede manejar ~20 req/s por worker. Un server async puede manejar ~200+ req/s por worker porque no se bloquea durante el I/O. Para un portfolio con analytics y AI chat, la concurrencia es critica.

---

## 6. ¿Como funciona el proxy reverso en tu configuracion de nginx y por que lo usas?

**Respuesta:**
Nginx actua como entry point unico. Sirve los archivos estaticos del frontend directamente y proxea las requests `/api/*` al backend de FastAPI. Esto elimina la necesidad de CORS en produccion (mismo origen) y permite agregar caching, rate limiting, y TLS en un solo punto.

**Donde se implemento:**
- `frontend/nginx.conf`:
  - `location /` → `try_files $uri $uri/ /index.html` (SPA routing)
  - `location /api/` → `proxy_pass http://backend:8000` (proxy reverso)
  - Headers: `X-Real-IP`, `X-Forwarded-For` para preservar IP del cliente
  - Cache de assets estaticos con `expires 1y` + `Cache-Control: immutable`

**Por que importa:**
Sin nginx, necesitarias servir el frontend desde un CDN o server separado, configurar CORS correctamente (complicado y propenso a errores), y manejar TLS en cada servicio. Con nginx como proxy reverso, todo se simplifica en un solo punto de entrada.

---

## 7. ¿Que es un Docker volume y cual es la diferencia entre named volumes y bind mounts?

**Respuesta:**
Un Docker volume es almacenamiento persistente que sobrevive al ciclo de vida del container. Los **named volumes** son manejados por Docker y almacenados en `/var/lib/docker/volumes/`. Los **bind mounts** mapean un directorio del host directamente al container.

**Donde se implemento:**
- `infra/docker/docker-compose.yml` — Named volumes para datos persistentes:
  - `postgres_data:/var/lib/postgresql/data`
  - `redis_data:/data`
  - `rabbitmq_data:/var/lib/rabbitmq`
- `infra/docker/docker-compose.dev.yml` — Bind mounts para hot-reload:
  - `../../backend/app:/app/app` (codigo fuente del backend)
  - `../../frontend/src:/app/src` (codigo fuente del frontend)

**Por que importa:**
Named volumes se usan para datos que deben persistir (DB) porque son portatiles y performantes. Bind mounts se usan para desarrollo porque reflejan cambios del host en tiempo real (hot-reload). Mezclarlos seria un error: bind mount para datos de PG causaria problemas de permisos, y named volume para codigo fuente no permite hot-reload.

---

## 8. ¿Por que separas el frontend Dockerfile en stage de build y stage de produccion?

**Respuesta:**
El stage de build usa Node.js para compilar TypeScript, procesar Tailwind, y generar el bundle con Vite. La salida es HTML/CSS/JS estático en `dist/`. El stage de produccion usa nginx:alpine (~5MB) para servir esos archivos. No necesita Node.js en produccion.

**Donde se implemento:**
- `frontend/Dockerfile`:
  - `builder` stage: `node:20-alpine`, ejecuta `npm ci && npm run build`
  - `production` stage: `nginx:alpine`, copia `dist/` + `nginx.conf`

**Por que importa:**
La imagen de Node.js pesa ~300MB. La imagen de nginx:alpine pesa ~5MB + el bundle de ~2MB. En Kubernetes, pull time importa para autoscaling — si un pod necesita escalar bajo carga, una imagen de 7MB se descarga en segundos vs 300MB que podria tardar minutos.

---

## 9. ¿Que son los mixins en SQLAlchemy y para que los usas?

**Respuesta:**
Los mixins son clases Python que definen columnas reutilizables y se agregan a modelos via herencia multiple. En lugar de definir `id`, `created_at`, `updated_at` en cada modelo, se definen una vez en mixins y cada modelo hereda de ellos.

**Donde se implemento:**
- `backend/app/shared/base_model.py`:
  - `UUIDMixin` — agrega columna `id` como UUID PK con `default=uuid.uuid4`
  - `TimestampMixin` — agrega `created_at` y `updated_at` con `server_default=func.now()`
  - `Base(DeclarativeBase)` — base class para todos los modelos

**Por que importa:**
Sin mixins, cada modelo repite las mismas 3 columnas. Con 6 features (profile, projects, contact, analytics, ai_chat + shared), eso son ~18 columnas duplicadas. Los mixins eliminan esa duplicacion y aseguran consistencia — si decides cambiar UUID a ULID, lo cambias en un solo lugar.

---

## 10. ¿Como estructurar un `docker-compose.yml` para que sea reutilizable entre ambientes?

**Respuesta:**
Usando archivos compose de override. El archivo base (`docker-compose.yml`) define la configuracion completa de produccion. Los archivos de override (`docker-compose.dev.yml`) solo contienen las diferencias para desarrollo: bind mounts para hot-reload, modo debug, stages de build diferentes.

**Donde se implemento:**
- `infra/docker/docker-compose.yml` — Configuracion base con todos los servicios, healthchecks, volumes
- `infra/docker/docker-compose.dev.yml` — Override: agrega volumes para hot-reload, cambia commands para uvicorn con `--reload`, seta `DEBUG=true`
- `Makefile` — `make dev` ejecuta `docker compose -f base.yml -f dev.yml up`

**Por que importa:**
Sin overrides, tendrias un solo archivo con condicionales o perderias la capacidad de tener configs diferentes. El patron de override es la practica recomendada por Docker: el base es production-ready, los overrides agregan conveniencias de desarrollo. No hay duplicacion de configuracion y cada archivo tiene una responsabilidad clara.
