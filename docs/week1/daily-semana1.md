# Daily Log — Semana 1: Foundation & Infrastructure

---

## S1 Lunes-Martes: Inicializar repos, estructura de carpetas, README

### Que se hizo
- Creacion de la estructura completa de directorios del proyecto
- Configuracion de `.gitignore`, `.env.example`, `Makefile`, `README.md`
- Skeleton del backend con FastAPI: `config.py`, `main.py`, `database.py`, `redis.py`, `rabbitmq.py`
- Base model de SQLAlchemy con mixins (`UUIDMixin`, `TimestampMixin`)
- Setup de Alembic para migraciones async
- Skeleton del frontend con React 18 + TypeScript + Vite + Tailwind CSS
- Componentes base: `Navbar`, `Footer`, pages `Home`, `About`, `Projects`
- API service layer con `api.ts`

### Por que se hizo asi

**Estructura de carpetas (Vertical Slice Architecture)**
Se organizo por features (`profile/`, `projects/`, `contact/`, etc.) en lugar de por capas tecnicas (`controllers/`, `services/`, `repositories/`). Esto mantiene cada feature cohesiva y auto-contenida, facilitando que un dev trabaje en un slice sin tocar otros.

**pydantic-settings para configuracion**
Se uso `pydantic-settings` en `backend/app/config.py` porque valida tipos en tiempo de startup. Si falta una variable critica, la app falla rapido con un error claro en lugar de fallar en runtime.

**SQLAlchemy 2.0 async + asyncpg**
Se eligio el modo async de SQLAlchemy con `asyncpg` como driver porque FastAPI es async-native. Mezclar sync DB con async handlers crea bottlenecks. El session factory (`async_sessionmaker`) se configuro con `expire_on_commit=False` para evitar lazy-loading accidental en contextos async.

**Mixins (UUIDMixin, TimestampMixin)**
Se crearon mixins reutilizables en `shared/base_model.py` para UUID PKs y timestamps. Esto evita duplicar `id`, `created_at`, `updated_at` en cada modelo y establece convenciones desde el dia 1.

**React + Vite + Tailwind**
Vite se eligio sobre CRA por velocidad de build (ESBuild vs Webpack). Tailwind se eligio por utilidad-first — evita CSS custom innecesario y mantiene consistencia visual. El path alias `@/` se configuro en `tsconfig.json` y `vite.config.ts` para imports limpios.

**Componentes de Layout separados**
`Navbar` y `Footer` se extrajeron a `components/layout/` para seguir el principio de composicion de React. El `Navbar` usa `useLocation()` de React Router para highlighting activo sin estado global.

---

## S1 Miercoles-Jueves: Docker Compose con todos los servicios

### Que se hizo
- `docker-compose.yml` con 6 servicios: backend, frontend, worker, postgres, redis, rabbitmq
- `docker-compose.dev.yml` como override para desarrollo con hot-reload
- Healthchecks para todos los servicios de datos
- Dependencias ordenadas con `depends_on` + `condition: service_healthy`
- Volumes persistentes para postgres, redis y rabbitmq
- Red bridge dedicada `portfolio-net`

### Por que se hizo asi

**Compose con healthchecks**
Cada servicio de datos (PG, Redis, RabbitMQ) tiene healthcheck nativo. Sin esto, el backend intentaria conectar antes de que PG este listo, causando crashes al startup. `depends_on.condition: service_healthy` resuelve el race condition.

**Archivo dev override separado**
Se uso `docker-compose.dev.yml` como override en lugar de un solo archivo con profiles. Esto es el patron recomendado por Docker — el archivo base tiene la config de produccion, el override agrega volumes para hot-reload y modo debug. Se ejecuta con `docker compose -f base.yml -f dev.yml up`.

**Red bridge dedicada**
Se creo `portfolio-net` en lugar de usar la red default. Los servicios se referencian por nombre de servicio (ej: `postgres`, `redis`), lo cual funciona como DNS interno de Docker. Esto es critico para que las URLs de conexion en `.env` funcionen.

**Volumes con nombre**
Se usaron named volumes (`postgres_data:`, etc.) en lugar de bind mounts para datos persistentes. Los named volumes sobreviven a `docker compose down` (se borran solo con `-v`), evitando perdida accidental de datos en desarrollo.

---

## S1 Viernes: Dockerfiles multi-stage

### Que se hizo
- Backend Dockerfile con 3 stages: `base` (deps) → `development` (hot-reload) → `production` (slim)
- Frontend Dockerfile con 3 stages: `development` (vite dev) → `builder` (compile) → `production` (nginx)
- `.dockerignore` para ambos servicios
- `nginx.conf` con SPA routing, proxy reverso a backend, cache de assets, security headers

### Por que se hizo asi

**Multi-stage builds**
El backend production image solo tiene las dependencias de runtime (sin pytest, ruff, etc.). Esto reduce el tamano de imagen de ~1.2GB a ~200MB. El stage `development` incluye devtools y se usa solo en docker-compose.dev.yml via `target: development`.

**Non-root user en produccion**
El Dockerfile de backend crea un usuario `appuser` sin privilegios para el stage de produccion. Ejecutar como root en containers es un anti-patron de seguridad — si hay un exploit, el atacante tendria acceso root al container.

**Nginx para SPA routing**
La directiva `try_files $uri $uri/ /index.html` es esencial para SPAs con React Router. Sin esto, hacer refresh en `/about` retorna 404 porque nginx busca un archivo `/about` que no existe. El fallback a `index.html` deja que React Router maneje la ruta.

**Proxy reverso en nginx**
El bloque `location /api/` proxea al backend. Esto elimina problemas de CORS en produccion porque frontend y API comparten el mismo dominio. Las cabeceras `X-Real-IP` y `X-Forwarded-For` preservan la IP del cliente a traves del proxy.

**Cache de assets estaticos**
Los archivos JS/CSS/imagenes se sirven con `expires 1y` y `Cache-Control: immutable`. Vite genera filenames con hash de contenido (`app-a3f2c1.js`), asi que el cache largo es seguro — si el contenido cambia, el hash cambia y el browser descarga el nuevo archivo.
