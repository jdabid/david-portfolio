# 10 Preguntas de Entrevista — Semana 5-6: AI Integration & Analytics

---

## 1. ¿Que es RAG y por que lo usas en lugar de fine-tuning?

**Respuesta:**
RAG (Retrieval-Augmented Generation) recupera documentos relevantes de una knowledge base y los inyecta como contexto en el prompt del LLM. Fine-tuning modifica los pesos del modelo con datos de entrenamiento.

RAG es mejor para este caso porque: (1) los datos del CV cambian frecuentemente — actualizar un JSON es instantaneo vs re-entrenar un modelo, (2) es transparente — puedes auditar exactamente que contexto recibio el modelo, (3) no requiere GPU ni entrenamiento costoso, (4) no hay riesgo de "olvidar" conocimiento base del modelo.

**Donde se implemento:**
- `backend/app/features/ai_chat/services/rag_service.py` — Indexa CV data en ChromaDB, `retrieve_context()` busca los 5 documentos mas relevantes
- `backend/app/features/ai_chat/services/llm_service.py:54-57` — `context = retrieve_context(query)` → inyecta en system prompt → envía a Claude
- `backend/data/knowledge/cv_data.json` — Knowledge base que ChromaDB indexa

**Por que importa:**
RAG es el patron dominante en produccion para LLM apps enterprise. Fine-tuning se usa cuando necesitas cambiar el comportamiento del modelo (tono, formato), no cuando necesitas darle datos nuevos.

---

## 2. ¿Como funcionan los embeddings y la busqueda vectorial en ChromaDB?

**Respuesta:**
Los embeddings convierten texto en vectores numericos de alta dimension donde textos semanticamente similares estan "cerca" en el espacio vectorial. ChromaDB almacena estos vectores y permite busqueda por similitud coseno — dado un query, retorna los documentos cuyos vectores son mas cercanos al vector del query.

**Donde se implemento:**
- `backend/app/features/ai_chat/services/rag_service.py:21-25` — `client.get_or_create_collection(name="portfolio_knowledge", metadata={"hnsw:space": "cosine"})` — crea collection con distancia coseno
- `rag_service.py:30-32` — `_index_knowledge_base()` procesa JSON/YAML en documentos de texto y los agrega a ChromaDB
- `rag_service.py:120-125` — `collection.query(query_texts=[query], n_results=5)` — busca los 5 mas relevantes
- ChromaDB usa internamente un modelo de embedding (default: `all-MiniLM-L6-v2`) para convertir texto a vectores

**Por que importa:**
Sin embeddings, buscar "que sabe de contenedores?" requiere keyword matching exacto. Con embeddings, "contenedores" matchea semanticamente con "Docker" y "Kubernetes" aunque no comparten palabras. Esto permite busqueda por concepto, no por texto.

---

## 3. ¿Como implementas WebSocket streaming para respuestas de AI?

**Respuesta:**
El endpoint WebSocket mantiene una conexion persistente. Cuando el cliente envia un mensaje, el server ejecuta el pipeline RAG y transmite cada token del LLM al instante. El cliente actualiza el UI token por token, creando el efecto de "escribiendo".

**Protocolo:**
- Cliente → Server: `{"message": "...", "session_id": "..."}`
- Server → Cliente: `{"type": "token", "content": "..."}` (por cada token)
- Server → Cliente: `{"type": "done", "session_id": "..."}` (al completar)

**Donde se implemento:**
- `backend/app/features/ai_chat/router.py:46-100` — WebSocket handler completo con persistencia
- `backend/app/features/ai_chat/services/llm_service.py:62-70` — `stream_response()` usa `llm.astream()` que yield tokens via `AsyncGenerator`
- `frontend/src/hooks/useChat.ts:30-50` — `ws.onmessage` acumula tokens en `streamBufferRef` y actualiza el ultimo mensaje in-place

**Por que importa:**
Sin streaming, el usuario espera 3-5 segundos viendo un loading spinner. Con streaming, el primer token aparece en <200ms y la respuesta se "escribe" en tiempo real. La latencia percibida baja drasticamente y la experiencia se siente interactiva.

---

## 4. ¿Por que usas `useRef` en lugar de `useState` para el stream buffer?

**Respuesta:**
`useState` causa un re-render del componente cada vez que se actualiza. Si el LLM genera 200 tokens, eso serian 200 re-renders en 3 segundos — causando jank visual y lag. `useRef` mantiene un valor mutable sin triggerar re-renders. Se actualiza el `ref.current` por cada token y se hace un solo `setMessages` para actualizar el UI.

**Donde se implemento:**
- `frontend/src/hooks/useChat.ts:9` — `const streamBufferRef = useRef("")`
- `useChat.ts:33-34` — En `onmessage`, `streamBufferRef.current += data.content` (no re-render)
- `useChat.ts:36-42` — Un `setMessages` actualiza el contenido del ultimo mensaje usando el buffer completo

**Por que importa:**
Es un patron comun en React para manejar datos de alta frecuencia (WebSocket, mouse events, animation frames). La regla: si un valor cambia mas rapido de lo que el UI puede renderizar, usa `useRef`. Si el usuario necesita ver el cambio, usa `useState`. Aqui combinamos ambos: `ref` para acumular tokens rapido, `state` para actualizar el UI a un ritmo visible.

---

## 5. ¿Como funciona el pipeline completo desde que el usuario envia un mensaje hasta que ve la respuesta?

**Respuesta:**
1. Usuario escribe en el input y presiona Send
2. `useChat.sendMessage()` envia via WebSocket: `{"message": "...", "session_id": "..."}`
3. Frontend agrega user message + assistant placeholder al estado (feedback instantaneo)
4. Backend WebSocket handler recibe el mensaje
5. Si hay `session_id`, carga historial de chat desde DB
6. Persiste el user message en PostgreSQL
7. `stream_response()` ejecuta: query → ChromaDB vector search → top 5 documentos
8. Construye messages: system prompt + contexto + historial + user message
9. `llm.astream()` envia a Claude API y yield tokens
10. Cada token se envia al cliente via WebSocket `{"type": "token", "content": "..."}`
11. Frontend actualiza el assistant placeholder token por token
12. Al completar, server persiste AI message en DB, invalida cache
13. Server envia `{"type": "done", "session_id": "..."}`
14. Frontend marca streaming como completado

**Donde se implemento:**
Todo el flujo cruza: `frontend/hooks/useChat.ts` → `backend/ai_chat/router.py` → `services/llm_service.py` → `services/rag_service.py` → ChromaDB → Claude API → WebSocket → React UI

---

## 6. ¿Que es Celery Beat y como lo usas para analytics?

**Respuesta:**
Celery Beat es un scheduler que ejecuta tasks periodicamente (como cron pero dentro de Celery). Se configura con `beat_schedule` y soporta intervalos (cada 30s) o crontab (cada hora a las :00).

**Donde se implemento:**
- `backend/app/infrastructure/celery_app.py:47-52`:
  ```python
  beat_schedule={
      "aggregate-daily-metrics": {
          "task": "analytics.aggregate_daily",
          "schedule": crontab(minute=0),  # Every hour at :00
      },
  }
  ```
- `backend/app/features/analytics/tasks/aggregate_metrics.py` — El task agrega page_visits en daily_stats con UPSERT

**Por que importa:**
Sin Beat, tendrias que usar cron del OS (no portable, no versionado) o un servicio externo. Celery Beat se configura en Python, vive en el repo, y se escala con el stack. El task de agregacion es idempotente — si se ejecuta 10 veces produce el mismo resultado, critico para sistemas distribuidos.

---

## 7. ¿Que patron usas para analytics y por que separas raw events de aggregated stats?

**Respuesta:**
Es el patron **Two-Table Analytics**: una tabla de eventos raw (append-only, INSERT rapido) y una tabla de metricas pre-computadas (read-optimized, updated periodicamente).

- `page_visits`: cada visita es un INSERT. Sin queries complejos. Alta velocidad de escritura.
- `daily_stats`: una fila por dia con totales pre-computados. Los dashboards leen de aqui (1 fila por dia vs N visitas).

**Donde se implemento:**
- `backend/app/features/analytics/models.py` — `PageVisit` (raw) + `DailyStats` (aggregated)
- `backend/app/features/analytics/commands/track_visit.py` — INSERT a page_visits
- `backend/app/features/analytics/tasks/aggregate_metrics.py` — UPSERT a daily_stats cada hora
- `backend/app/features/analytics/queries/get_stats.py` — Lee de daily_stats + counts en vivo

**Por que importa:**
Si el dashboard hiciera `SELECT COUNT(*) FROM page_visits WHERE date = today` en cada request, con 10,000 visitas diarias seria lento. Leyendo de `daily_stats`, es siempre O(1) independientemente del volumen. Es el mismo patron que usa Google Analytics internamente.

---

## 8. ¿Como manejas la persistencia de sesiones de chat y por que?

**Respuesta:**
Cada conversacion tiene un `ChatSession` con un `visitor_id`. Los mensajes (`ChatMessage`) pertenecen a una sesion via FK. El `session_id` se retorna al frontend en el primer mensaje y se envia en mensajes subsecuentes para mantener continuidad.

**Donde se implemento:**
- `backend/app/features/ai_chat/models.py` — `ChatSession` (1) → `ChatMessage` (N)
- `backend/app/features/ai_chat/commands/send_chat.py:32-40` — Si no hay session_id, crea una nueva; si hay, carga el historial
- `backend/app/features/ai_chat/router.py:90` — WebSocket envia `session_id` en `"done"` message
- `frontend/src/hooks/useChat.ts:51` — `setSessionId(data.session_id)` y lo envia en mensajes posteriores

**Por que importa:**
Sin sesiones, cada mensaje seria independiente — el AI no tendria contexto de la conversacion previa. Con sesiones, el historial se carga y se envia al LLM como contexto, permitiendo respuestas coherentes como "como te dije antes..." o follow-ups como "explica mas sobre eso".

---

## 9. ¿Como trackeas visitantes unicos sin cookies y cual es la limitacion?

**Respuesta:**
Se genera un UUID v4 al primer visit y se persiste en `localStorage`. En requests subsecuentes se envia como `visitor_id`. El backend cuenta `DISTINCT visitor_id` para unique visitors.

**Limitacion:** localStorage es per-browser, per-origin. Incognito mode, limpiar datos, o usar otro browser genera un nuevo ID. No es 100% preciso pero no requiere cookie consent banners.

**Donde se implemento:**
- `frontend/src/services/api.ts:67-74` — `getVisitorId()`: genera y persiste UUID en localStorage
- `frontend/src/hooks/usePageTracking.ts` — Envia visitor_id en cada `trackVisit()` call
- `backend/app/features/analytics/queries/get_stats.py:45-48` — `COUNT(DISTINCT visitor_id)` para unicos

**Por que importa:**
En un portfolio, la precision de analytics no es critica — es para metricas internas. localStorage es la solucion mas simple que no requiere consentimiento GDPR. Si necesitaras precision, usarias fingerprinting (controversial) o login obligatorio.

---

## 10. ¿Como aseguras que el tracking de analytics nunca rompa la experiencia del usuario?

**Respuesta:**
Tres capas de proteccion: (1) el hook ignora errores con `.catch(() => {})`, (2) el fetch usa `keepalive: true` para que complete aunque el usuario navegue, (3) el endpoint retorna 204 No Content (sin body, sin espera).

**Donde se implemento:**
- `frontend/src/hooks/usePageTracking.ts:10-12`:
  ```typescript
  trackVisit(location.pathname).catch(() => {
    // Silently ignore tracking failures
  });
  ```
- `frontend/src/services/api.ts:52-58` — `fetch()` con `keepalive: true` — el browser completa la request en background
- `backend/app/features/analytics/router.py:15` — `status_code=204` — respuesta sin body

**Por que importa:**
Analytics es un "nice to have", no una funcionalidad critica. Si el API de analytics falla (network error, server down, rate limit), el usuario no debe ver un error ni experimentar lag. El patron fire-and-forget con error swallowing es estandar en todos los analytics SDKs (Google Analytics, Mixpanel, etc.).
