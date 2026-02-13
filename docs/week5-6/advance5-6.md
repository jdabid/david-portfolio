Archivos creados — Semana 5-6                                                                                                                                                                                                       
                                                                                                                                                                                                                                        
  S5 L-M: Knowledge Base (3 archivos)                                                                                                                                                                                                   
  ┌───────────────────────────────────────────┬───────────────────────────────────────────────────────────────────────────────────┐
  │                  Archivo                  │                                     Proposito                                     │                                                                                                     
  ├───────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────┤                                                                                                     
  │ backend/data/knowledge/cv_data.json       │ Datos estructurados del CV: personal, skills, experience, education, projects     │                                                                                                     
  ├───────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────┤
  │ backend/data/knowledge/skills_matrix.yaml │ Skills detallados con niveles y evidencia por categoria                           │
  ├───────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────┤
  │ backend/app/config.py                     │ (actualizado) — Agrega settings: anthropic_api_key, llm_model, chroma_persist_dir │
  └───────────────────────────────────────────┴───────────────────────────────────────────────────────────────────────────────────┘
  S5 M-J: AI Chat Slice — RAG Pipeline (9 archivos)
  ┌───────────────────────────────────────────────┬──────────────────────────────────────────────────────────────────────┐
  │                    Archivo                    │                              Proposito                               │
  ├───────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────┤
  │ features/ai_chat/models.py                    │ ChatSession + ChatMessage (historial persistente)                    │
  ├───────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────┤
  │ features/ai_chat/schemas.py                   │ ChatRequest, ChatResponse, ChatHistoryResponse                       │
  ├───────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────┤
  │ features/ai_chat/services/prompt_templates.py │ System prompt persona + guidelines (no alucinar)                     │
  ├───────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────┤
  │ features/ai_chat/services/rag_service.py      │ Indexa CV en ChromaDB, retrieve_context() busqueda vectorial top-5   │
  ├───────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────┤
  │ features/ai_chat/services/llm_service.py      │ Orquesta RAG: context → system prompt → Claude API. Sync + streaming │
  ├───────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────┤
  │ features/ai_chat/commands/send_chat.py        │ Command: persiste user msg → RAG → persiste AI msg                   │
  ├───────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────┤
  │ features/ai_chat/queries/get_chat_history.py  │ Query: historial con cache Redis (TTL 2min)                          │
  └───────────────────────────────────────────────┴──────────────────────────────────────────────────────────────────────┘
  S5 V: WebSocket Streaming (1 archivo)
  ┌────────────────────────────┬───────────────────────────────────────────────────────────────────────────────┐
  │          Archivo           │                                   Proposito                                   │
  ├────────────────────────────┼───────────────────────────────────────────────────────────────────────────────┤
  │ features/ai_chat/router.py │ REST POST /api/chat + WebSocket ws://api/chat/ws con streaming token-by-token │
  └────────────────────────────┴───────────────────────────────────────────────────────────────────────────────┘
  S6 L-M: Frontend AI Chat (3 archivos)
  ┌───────────────────────────────────────┬───────────────────────────────────────────────────────────────┐
  │                Archivo                │                           Proposito                           │
  ├───────────────────────────────────────┼───────────────────────────────────────────────────────────────┤
  │ frontend/src/hooks/useChat.ts         │ WebSocket hook: conexion, streaming via useRef, message state │
  ├───────────────────────────────────────┼───────────────────────────────────────────────────────────────┤
  │ frontend/src/pages/AIChat/index.tsx   │ Chat UI: bubbles, sugerencias, streaming visual, auto-scroll  │
  ├───────────────────────────────────────┼───────────────────────────────────────────────────────────────┤
  │ frontend/src/hooks/usePageTracking.ts │ Trackea cada cambio de ruta → POST /api/analytics/track       │
  └───────────────────────────────────────┴───────────────────────────────────────────────────────────────┘
  S6 M-J: Analytics Slice (7 archivos)
  ┌───────────────────────────────────────────────┬───────────────────────────────────────────┐
  │                    Archivo                    │                 Proposito                 │
  ├───────────────────────────────────────────────┼───────────────────────────────────────────┤
  │ features/analytics/models.py                  │ PageVisit (raw) + DailyStats (aggregated) │
  ├───────────────────────────────────────────────┼───────────────────────────────────────────┤
  │ features/analytics/schemas.py                 │ TrackVisitRequest, DashboardResponse      │
  ├───────────────────────────────────────────────┼───────────────────────────────────────────┤
  │ features/analytics/commands/track_visit.py    │ Command: INSERT visita (lightweight)      │
  ├───────────────────────────────────────────────┼───────────────────────────────────────────┤
  │ features/analytics/queries/get_stats.py       │ Query: agrega totales + daily + top pages │
  ├───────────────────────────────────────────────┼───────────────────────────────────────────┤
  │ features/analytics/tasks/aggregate_metrics.py │ Celery task: UPSERT daily_stats cada hora │
  ├───────────────────────────────────────────────┼───────────────────────────────────────────┤
  │ features/analytics/router.py                  │ POST /track (204) + GET /dashboard        │
  └───────────────────────────────────────────────┴───────────────────────────────────────────┘
  S6 V: Admin Dashboard (1 archivo)
  ┌────────────────────────────────────┬───────────────────────────────────────────────────────┐
  │              Archivo               │                       Proposito                       │
  ├────────────────────────────────────┼───────────────────────────────────────────────────────┤
  │ frontend/src/pages/Admin/index.tsx │ Dashboard con stat cards + top pages + daily activity │
  └────────────────────────────────────┴───────────────────────────────────────────────────────┘
  Archivos actualizados
  ┌───────────────────────────────────────────┬──────────────────────────────────────────────────────────────────────────────┐
  │                  Archivo                  │                                    Cambio                                    │
  ├───────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────┤
  │ backend/app/main.py                       │ Registra ai_chat + analytics routers y handlers                              │
  ├───────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────┤
  │ backend/app/infrastructure/celery_app.py  │ Agrega analytics task routing + Celery Beat schedule                         │
  ├───────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────┤
  │ backend/pyproject.toml                    │ Agrega langchain, langchain-anthropic, chromadb, websockets, psycopg2        │
  ├───────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────┤
  │ .env.example                              │ Agrega ANTHROPIC_API_KEY, LLM_MODEL, CHROMA/KNOWLEDGE dirs                   │
  ├───────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────┤
  │ frontend/src/App.tsx                      │ Agrega rutas /chat, /admin + usePageTracking()                               │
  ├───────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────┤
  │ frontend/src/components/layout/Navbar.tsx │ Agrega link AI Chat                                                          │
  ├───────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────┤
  │ frontend/src/services/api.ts              │ Agrega sendChatMessage, getChatWsUrl, trackVisit, getDashboard, getVisitorId │
  ├───────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────┤
  │ frontend/src/types/index.ts               │ Agrega ChatMessage, ChatResponse, DailyStats, DashboardData                  │
  └───────────────────────────────────────────┴──────────────────────────────────────────────────────────────────────────────┘
  Documentacion
  ┌──────────────────────────────────────┬───────────────────────────────────────────────────┐
  │               Archivo                │                     Proposito                     │
  ├──────────────────────────────────────┼───────────────────────────────────────────────────┤
  │ docs/week5-6/daily-semana5-6.md      │ Daily log con QUE + POR QUE para cada dia         │
  ├──────────────────────────────────────┼───────────────────────────────────────────────────┤
  │ docs/week5-6/entrevista-semana5-6.md │ 10 preguntas con respuestas y ubicacion en codigo │
  └──────────────────────────────────────┴───────────────────────────────────────────────────┘
  ---
  Endpoints API nuevos (Semana 5-6)

  POST   /api/chat                → Enviar mensaje AI (sync, respuesta completa)
  GET    /api/chat/history/{id}   → Historial de sesion de chat
  WS     /api/chat/ws             → WebSocket streaming token-by-token
  POST   /api/analytics/track     → Trackear visita (204 No Content)
  GET    /api/analytics/dashboard  → Dashboard con stats agregados
