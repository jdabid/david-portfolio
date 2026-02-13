# Daily Log — Semana 5-6: AI Integration & Analytics

---

## S5 Lunes-Martes: Knowledge Base + ChromaDB Embeddings

### Que se hizo
- Datos estructurados del CV en `backend/data/knowledge/cv_data.json` (personal, skills, experience, education, projects)
- Skills matrix detallado en `backend/data/knowledge/skills_matrix.yaml` con evidencia por skill
- Configuracion AI en `backend/app/config.py` (anthropic_api_key, llm_model, chroma_persist_dir, knowledge_base_dir)
- Variables de entorno AI en `.env.example`
- Dependencias nuevas en `pyproject.toml`: langchain, langchain-anthropic, chromadb, websockets

### Por que se hizo asi

**Knowledge base en JSON + YAML**
Los datos del CV estan en JSON (estructurado, facil de parsear) y la skills matrix en YAML (mas legible para humanos, soporta comentarios). Esta separacion permite actualizar skills y evidencia sin tocar datos personales. ChromaDB indexa ambos en un vector store unificado.

**ChromaDB en lugar de pgvector**
Se eligio ChromaDB por simplicidad — corre in-memory para desarrollo y no requiere extensiones de PostgreSQL. Para produccion se puede cambiar a `PersistentClient` o migrar a pgvector. La abstraccion en `rag_service.py` hace este cambio transparente.

**Datos como documentos, no como rows**
En lugar de hacer queries SQL para construir el contexto del LLM, los datos se pre-procesan como documentos de texto natural y se indexan como embeddings. Esto permite busqueda semantica: "que sabe de contenedores?" matchea con Docker y Kubernetes sin necesitar keywords exactos.

---

## S5 Miercoles-Jueves: Slice `ai_chat` — RAG Pipeline + LangChain

### Que se hizo
- Modelos SQLAlchemy: `ChatSession` y `ChatMessage` para persistir conversaciones
- Schemas Pydantic: `ChatRequest`, `ChatResponse`, `ChatHistoryResponse`
- **RAG Service** (`rag_service.py`): indexa knowledge base en ChromaDB, recupera contexto relevante via vector search
- **LLM Service** (`llm_service.py`): orquesta el pipeline RAG con LangChain + Claude API, soporta `generate_response()` (completo) y `stream_response()` (streaming)
- **Prompt Templates** (`prompt_templates.py`): system prompt que define la persona del asistente + guidelines de respuesta
- Command `SendChatCommand`: persiste user message → genera respuesta AI → persiste AI message
- Query `GetChatHistoryQuery`: recupera historial con cache Redis (TTL 2 min)

### Por que se hizo asi

**RAG vs Fine-tuning**
RAG (Retrieval-Augmented Generation) recupera contexto relevante y lo inyecta en el prompt. Fine-tuning entrena un modelo custom. RAG es mejor aqui porque: (1) los datos cambian frecuentemente (actualizar CV), (2) no requiere entrenamiento costoso, (3) es transparente — puedes ver exactamente que contexto recibio el modelo.

**Pipeline: Query → Vector Search → Context → LLM**
El flujo es: usuario pregunta → ChromaDB busca los 5 documentos mas relevantes → se inyectan en el system prompt como contexto → Claude genera la respuesta. Esto asegura que el LLM solo habla sobre lo que realmente esta en el CV.

**Chat history limitado a 10 mensajes**
En `llm_service.py:33`, solo se envian los ultimos 10 mensajes al LLM. Esto evita exceder el context window y reduce costos de API. Las conversaciones mas largas pierden contexto antiguo pero mantienen la coherencia reciente.

**System prompt con guidelines estrictas**
El prompt en `prompt_templates.py` indica explicitamente: "If asked about something not in the context, say you don't have that information." Esto previene alucinaciones — el modelo no inventa informacion que no esta en el CV.

---

## S5 Viernes: WebSocket Streaming

### Que se hizo
- Endpoint WebSocket `ws://api/chat/ws` en `ai_chat/router.py`
- Protocolo: cliente envia `{"message": "...", "session_id": "..."}`, servidor stream `{"type": "token", "content": "..."}` por cada token, termina con `{"type": "done", "session_id": "..."}`
- Persistencia de mensajes dentro del WebSocket handler
- Invalidacion de cache de historial al completar respuesta
- Manejo de errores: `{"type": "error", "content": "..."}` + log de desconexiones

### Por que se hizo asi

**WebSocket vs Server-Sent Events (SSE)**
WebSocket es bidireccional — el cliente puede enviar mensajes sin cerrar la conexion. SSE es unidireccional (server → client). Para un chat, WebSocket es natural porque la misma conexion maneja envio y recepcion. Con SSE necesitarias POST para enviar + SSE para recibir.

**Streaming token-by-token**
El LLM genera respuestas token a token. En lugar de esperar la respuesta completa (2-5 segundos), se envia cada token al instante. El usuario ve la respuesta "escribiendose" en tiempo real — la latencia percibida baja de 3s a <100ms para el primer token.

**Buffer + persist al final**
Los tokens se acumulan en el server y solo se persisten cuando el stream completa (`"type": "done"`). Persistir cada token seria demasiadas escrituras a DB. El trade-off: si la conexion cae a mitad del stream, se pierde esa respuesta parcial. Para un portfolio, esto es aceptable.

---

## S6 Lunes-Martes: Frontend AI Chat UI

### Que se hizo
- Hook `useChat()` en `frontend/src/hooks/useChat.ts` para manejo de WebSocket
- Pagina `AIChat` con: mensajes con bubbles, sugerencias iniciales, streaming visual, auto-scroll
- Streaming in-place: el ultimo mensaje del assistant se actualiza token por token via `streamBufferRef`
- Estados: connected, streaming, error, con indicador de cursor pulsante

### Por que se hizo asi

**useRef para stream buffer**
Se usa `useRef` en lugar de `useState` para el buffer de streaming. Un `useState` causaria un re-render por cada token (posiblemente 100+ por respuesta). Con `useRef`, el buffer se actualiza sin re-render, y se hace un unico `setMessages` para actualizar el UI. Esto evita jank visual y mejora performance.

**Placeholder message pattern**
Al enviar un mensaje, se crean inmediatamente DOS messages: el user message y un assistant placeholder vacio. Conforme llegan tokens, se actualiza el placeholder in-place. Esto da feedback instantaneo al usuario — ve su mensaje aparecer y el cursor del assistant pulsando.

**Sugerencias como onboarding**
La pagina muestra 4 preguntas sugeridas cuando no hay mensajes. Esto guia al usuario sobre que puede preguntar y reduce la friccion de empezar una conversacion.

---

## S6 Miercoles-Jueves: Slice `analytics` + Celery Aggregation

### Que se hizo
- Modelos: `PageVisit` (track individual) y `DailyStats` (agregado diario)
- Command `TrackVisitCommand`: registra visita con path, visitor_id, user_agent, IP
- Query `GetStatsQuery`: agrega totales + daily stats + top pages
- Celery task `aggregate_daily_metrics`: corre cada hora via Beat, agrega visitas en `daily_stats`
- Router: `POST /api/analytics/track` (204 No Content) + `GET /api/analytics/dashboard`
- Celery Beat schedule en `celery_app.py` con crontab(minute=0)

### Por que se hizo asi

**204 No Content para tracking**
El endpoint de tracking retorna 204 sin body porque el cliente no necesita confirmacion. El `fetch` usa `keepalive: true` para que la request complete incluso si el usuario navega fuera de la pagina. Esto es un patron estandar para analytics.

**Two-table pattern (raw + aggregated)**
`page_visits` almacena cada visita individual (INSERT rapido, append-only). `daily_stats` almacena metricas pre-computadas por dia. Los queries del dashboard leen de `daily_stats` (una fila por dia) en lugar de agregar millones de visitas on-the-fly. Celery Beat actualiza los agregados cada hora.

**UPSERT para daily_stats**
`aggregate_daily_metrics` usa `INSERT ... ON CONFLICT (date) DO UPDATE` (upsert). Cada hora re-calcula los stats de hoy y los sobreescribe. Esto es idempotente — correr el task 10 veces produce el mismo resultado. Importante para Celery donde un task puede ejecutarse mas de una vez.

---

## S6 Viernes: Admin Dashboard

### Que se hizo
- Pagina `Admin` con 4 stat cards (visits, unique, messages, chats) + top pages + daily activity
- Hook `usePageTracking()` en `App.tsx` que trackea cada cambio de ruta
- `getVisitorId()` en `api.ts`: genera UUID persistente en localStorage por browser
- Rutas actualizadas: `/chat` y `/admin` en App.tsx + Navbar con link AI Chat

### Por que se hizo asi

**usePageTracking como efecto global**
El hook se invoca una vez en `App.tsx` y escucha `location.pathname`. Cada cambio de ruta dispara un `trackVisit()` fire-and-forget. El `.catch(() => {})` silencia errores — analytics nunca debe romper la UX. Esto es el equivalente de un Google Analytics tag pero self-hosted.

**Visitor ID en localStorage**
Se genera un UUID v4 por browser y se persiste en localStorage. Esto permite contar "unique visitors" sin cookies ni login. No es 100% preciso (incognito, clear storage) pero es suficiente para analytics basico y no requiere consentimiento de cookies.

**Admin sin autenticacion (por ahora)**
El dashboard esta en `/admin` sin auth. En un portfolio personal es aceptable — los datos no son sensibles. En semanas futuras se puede agregar autenticacion basica si se desea.
