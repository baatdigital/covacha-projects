# IA/Bots - Plataforma de Inteligencia Artificial (EP-IA-001 a EP-IA-010)

**Fecha**: 2026-02-16
**Product Owner**: SuperPago / BaatDigital
**Estado**: Planificacion
**Prefijo Epicas**: EP-IA
**Prefijo User Stories**: US-IA
**User Stories**: US-IA-001 a US-IA-055

---

## Tabla de Contenidos

1. [Contexto y Motivacion](#contexto-y-motivacion)
2. [Arquitectura de la Plataforma IA](#arquitectura-de-la-plataforma-ia)
3. [Mapa de Epicas](#mapa-de-epicas)
4. [Epicas Detalladas](#epicas-detalladas)
5. [User Stories Detalladas](#user-stories-detalladas)
6. [Roadmap](#roadmap)
7. [Grafo de Dependencias](#grafo-de-dependencias)
8. [Riesgos y Mitigaciones](#riesgos-y-mitigaciones)

---

## Contexto y Motivacion

El ecosistema SuperPago/BaatDigital cuenta con **20 agentes IA especializados** planificados:

| Documento | Epicas | Agentes |
|-----------|--------|---------|
| SUPERPAGO-AI-AGENTS-EPICS.md | EP-SP-031 a EP-SP-040 | 10 agentes financieros (onboarding, soporte, SPEI, conciliacion, BillPay, cash, fraude, reportes, subasta, compliance) |
| MARKETING-AI-AGENTS-EPICS.md | EP-MK-014 a EP-MK-023 | 10 agentes de marketing (content, social, ads, landing, email, WhatsApp, analytics, leads, brand, SEO) |
| SPEI-EXPANSION-EPICS.md | EP-SP-017, EP-SP-018 | Agente IA WhatsApp Core + BillPay conversacional |

Todos estos agentes necesitan una **plataforma base compartida** que provea:

| Capacidad de Plataforma | Problema sin ella |
|--------------------------|-------------------|
| **Orquestacion de Agentes** | Cada agente tendria su propio routing, duplicando logica de NLU, sesion y contexto |
| **Motor de Conversacion** | Cada agente implementaria su propia state machine, sin estandar de memoria ni slot filling |
| **Integracion WhatsApp** | Multiples implementaciones del webhook receiver, parsers de mensaje y template management |
| **Web Chat** | Sin widget reutilizable; cada equipo construiria su propia interfaz de chat |
| **Abstraccion LLM** | Acoplamiento directo a OpenAI; sin fallback, sin control de costos, sin versionado de prompts |
| **Knowledge Base / RAG** | Sin base de conocimiento consultable; cada agente hardcodearia respuestas |
| **Flow Builder** | Sin editor visual; flujos definidos solo en codigo, inaccesibles para no-desarrolladores |
| **Analytics** | Sin metricas centralizadas; imposible comparar rendimiento entre agentes |
| **Mejora Continua** | Sin feedback loop; sin forma de medir calidad ni re-entrenar |
| **Multi-Canal/Tenant** | Sin abstraccion de canal; agregar Telegram o SMS requeriria reescribir cada agente |

**Este documento (EP-IA-001 a EP-IA-010) define esa plataforma base.** Los agentes especializados de SuperPago y Marketing son **consumidores** de esta plataforma.

### Repositorios Involucrados

| Repositorio | Funcion | Puerto Dev |
|-------------|---------|------------|
| `covacha-botia` | Backend principal de la plataforma IA (Flask) | 5005 |
| `mf-ia` | Micro-frontend de configuracion de agentes y web chat | 4208 |
| `mf-whatsapp` | Micro-frontend de gestion WhatsApp | 4209 |
| `covacha-webhook` | Receptor de webhooks WhatsApp | 5006 |
| `covacha-libs` | Modelos y utilidades compartidas | N/A |

### Roles

| ID | Rol | Descripcion |
|----|-----|-------------|
| R1 | Administrador IA | Configura agentes, prompts, knowledge base. Accede a analytics globales. |
| R2 | Disenador de Flujos | Crea y edita flujos conversacionales en el Flow Builder visual. |
| R3 | Analista de Conversaciones | Revisa transcripts, metricas de calidad, identifica mejoras. |
| R4 | Sistema | Procesos automaticos: routing, NLU, colas SQS, cron jobs. |
| R5 | Usuario Final | Persona que interactua con los bots via WhatsApp o Web Chat. |

---

## Arquitectura de la Plataforma IA

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        CANALES DE ENTRADA                               │
│                                                                         │
│  WhatsApp ───┐    Web Chat ───┐    Telegram ──┐    SMS ──┐   Email ──┐ │
│  Business    │    (mf-ia)     │    (futuro)   │  (futuro)│   (futuro)│ │
│  API (Meta)  │    WebSocket   │               │          │           │ │
└──────────────┼────────────────┼───────────────┼──────────┼───────────┼─┘
               │                │               │          │           │
               ▼                ▼               ▼          ▼           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    CAPA DE RECEPCION                                     │
│                                                                         │
│  covacha-webhook ──► SQS: ia-inbound ──► Channel Adapter (normalize)   │
│  (WhatsApp verify)   (cola unificada)    (texto, imagen, audio, doc)   │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌═══════════════════════════════════════════════════════════════════════════┐
║                     covacha-botia (Flask)                                ║
║                                                                         ║
║  ┌───────────────────────────────────────────────────────────────────┐  ║
║  │               EP-IA-001: ORQUESTADOR DE AGENTES                  │  ║
║  │                                                                   │  ║
║  │  1. Session Manager ──► Identifica usuario + sesion activa       │  ║
║  │  2. NLU Classifier  ──► Clasifica intent con LLM                 │  ║
║  │  3. Agent Registry   ──► Busca agente habilitado para el intent  │  ║
║  │  4. Router           ──► Despacha al agente correcto             │  ║
║  │  5. Fallback Handler ──► Maneja intents no reconocidos           │  ║
║  │  6. Handoff Manager  ──► Transfiere conversacion entre agentes   │  ║
║  └───────────────────────────────────────────────────────────────────┘  ║
║           │         │         │         │         │                      ║
║           ▼         ▼         ▼         ▼         ▼                      ║
║  ┌──────────────────────────────────────────────────────────────┐       ║
║  │         AGENTES ESPECIALIZADOS (consumidores)                │       ║
║  │                                                              │       ║
║  │  EP-SP-031..040   EP-MK-014..023   EP-SP-017/018           │       ║
║  │  (10 financieros) (10 marketing)   (WhatsApp Core)          │       ║
║  │                                                              │       ║
║  │  Cada agente implementa: AgentInterface                     │       ║
║  │    - handle_message(context, message) -> Response            │       ║
║  │    - get_supported_intents() -> list[str]                    │       ║
║  │    - get_state_machine() -> StateMachine                     │       ║
║  └──────────────────────────────────────────────────────────────┘       ║
║           │                                                             ║
║           ▼                                                             ║
║  ┌───────────────────────────────────────────────────────────────────┐  ║
║  │            EP-IA-002: MOTOR DE CONVERSACION                      │  ║
║  │                                                                   │  ║
║  │  State Machine ── Memory Manager ── Slot Filler ── Confirmador  │  ║
║  │  (por conv)       (short+long)      (extraer datos) (SI/NO/2FA) │  ║
║  └───────────────────────────────────────────────────────────────────┘  ║
║           │                                                             ║
║           ▼                                                             ║
║  ┌───────────────────────────────────────────────────────────────────┐  ║
║  │            EP-IA-005: MOTOR DE LLM                               │  ║
║  │                                                                   │  ║
║  │  Provider Abstraction ── Prompt Templates ── Token Manager       │  ║
║  │  (OpenAI/Bedrock/      (versionados)        (cost tracking)     │  ║
║  │   Anthropic)                                                     │  ║
║  └───────────────────────────────────────────────────────────────────┘  ║
║           │                                                             ║
║           ▼                                                             ║
║  ┌───────────────────────────────────────────────────────────────────┐  ║
║  │            EP-IA-006: KNOWLEDGE BASE / RAG                       │  ║
║  │                                                                   │  ║
║  │  Document Ingestion ── Chunker ── Vector Store ── RAG Pipeline  │  ║
║  │  (PDF, DOCX, web)     (smart)    (embeddings)   (retrieve+gen)  │  ║
║  └───────────────────────────────────────────────────────────────────┘  ║
║                                                                         ║
║  ┌────────────────────┐  ┌────────────────────┐  ┌──────────────────┐  ║
║  │ EP-IA-008:         │  │ EP-IA-009:         │  │ EP-IA-010:       │  ║
║  │ Analytics           │  │ Mejora Continua    │  │ Multi-Canal/     │  ║
║  │ (metricas, funnel)  │  │ (feedback, A/B)    │  │ Multi-Tenant     │  ║
║  └────────────────────┘  └────────────────────┘  └──────────────────┘  ║
╚═══════════════════════════════════════════════════════════════════════════╝
               │                              │
               ▼                              ▼
┌──────────────────────────┐    ┌──────────────────────────────┐
│     FRONTENDS            │    │     SERVICIOS BACKEND        │
│                          │    │                              │
│  mf-ia:                  │    │  covacha-payment             │
│   - Config agentes       │    │  covacha-transaction         │
│   - Flow Builder (007)   │    │  covacha-core                │
│   - Analytics (008)      │    │  covacha-notification        │
│   - Web Chat (004)       │    │  (consumidos por agentes     │
│                          │    │   especializados)            │
│  mf-whatsapp:            │    │                              │
│   - Templates            │    └──────────────────────────────┘
│   - Configuracion WA     │
│   - Monitor mensajes     │
└──────────────────────────┘
```

### Modelo de Datos DynamoDB

```
# ═══════════════════════════════════════════
# AGENT REGISTRY (EP-IA-001)
# ═══════════════════════════════════════════
PK: AGENT#{agent_id}
SK: META
Attrs: name, description, type, version, supported_intents[], status (active/inactive),
       config{}, fallback_agent_id, created_at, updated_at

PK: AGENT#{agent_id}
SK: TENANT#{tenant_id}
Attrs: enabled, custom_config{}, welcome_message, active_hours{}, limits{}

GSI-1: PK=AGENT#TYPE#{type}, SK=#{agent_id}  (buscar agentes por tipo)

# ═══════════════════════════════════════════
# CONVERSATIONS (EP-IA-002)
# ═══════════════════════════════════════════
PK: CONV#{conversation_id}
SK: META
Attrs: user_id, channel, agent_id, status (active/paused/closed), tenant_id,
       started_at, last_activity, metadata{}

PK: CONV#{conversation_id}
SK: MSG#{timestamp}#{msg_id}
Attrs: direction (IN/OUT), content, content_type (text/image/audio/doc),
       intent, confidence, agent_id, metadata{}

PK: CONV#{conversation_id}
SK: STATE
Attrs: current_step, slots{}, memory_short{}, context_data{}, ttl

GSI-2: PK=USER#{user_id}#CONVS, SK=#{timestamp}  (conversaciones por usuario)
GSI-3: PK=AGENT#{agent_id}#CONVS, SK=#{date}     (conversaciones por agente)

# ═══════════════════════════════════════════
# INTENTS (EP-IA-001)
# ═══════════════════════════════════════════
PK: INTENT#{intent_id}
SK: META
Attrs: name, description, agent_id, examples[], training_phrases[], priority

PK: INTENT#LOG#{date}
SK: #{timestamp}#{log_id}
Attrs: intent_name, confidence, agent_id, user_id, resolved, channel

# ═══════════════════════════════════════════
# PROMPTS (EP-IA-005)
# ═══════════════════════════════════════════
PK: PROMPT#{prompt_id}
SK: V#{version}
Attrs: name, template, variables[], provider, model, max_tokens, temperature,
       status (draft/active/archived), created_at, metrics{}

# ═══════════════════════════════════════════
# FLOWS (EP-IA-007)
# ═══════════════════════════════════════════
PK: FLOW#{flow_id}
SK: META
Attrs: name, description, agent_id, status (draft/published), version,
       tenant_id, created_by, created_at, updated_at

PK: FLOW#{flow_id}
SK: NODE#{node_id}
Attrs: type (message/condition/api_call/wait_input/handoff), position{x,y},
       config{}, connections[{target_node_id, condition}]

# ═══════════════════════════════════════════
# KNOWLEDGE BASE (EP-IA-006)
# ═══════════════════════════════════════════
PK: KB#{kb_id}
SK: META
Attrs: name, description, tenant_id, document_count, chunk_count, status,
       last_indexed_at, embedding_model

PK: KB#{kb_id}
SK: DOC#{doc_id}
Attrs: title, source_type (pdf/docx/url/text), source_url, chunk_count,
       status (processing/indexed/error), uploaded_at

# ═══════════════════════════════════════════
# TEMPLATES WhatsApp (EP-IA-003)
# ═══════════════════════════════════════════
PK: TEMPLATE#{template_id}
SK: META
Attrs: name, category, language, status (pending/approved/rejected),
       components[], tenant_id, wa_template_id

# ═══════════════════════════════════════════
# BOT CONFIG por Tenant (EP-IA-010)
# ═══════════════════════════════════════════
PK: BOT#{tenant_id}
SK: CONFIG
Attrs: name, avatar_url, welcome_message, fallback_message, active_hours{},
       channels_enabled[], branding{}, language, timezone
```

---

## Mapa de Epicas

| ID | Epica | Complejidad | Sprint Sugerido | Dependencias |
|----|-------|-------------|-----------------|--------------|
| EP-IA-001 | Plataforma de Orquestacion de Agentes | XL | 1-3 | - |
| EP-IA-002 | Motor de Conversacion | XL | 2-4 | EP-IA-001 |
| EP-IA-003 | Integracion WhatsApp Business API | L | 1-3 | EP-IA-001 |
| EP-IA-004 | Integracion Web Chat (mf-ia) | L | 3-5 | EP-IA-001, EP-IA-002 |
| EP-IA-005 | Motor de LLM y Prompt Engineering | XL | 1-3 | - |
| EP-IA-006 | Knowledge Base y RAG | XL | 4-6 | EP-IA-005 |
| EP-IA-007 | Flow Builder Visual (mf-ia) | XL | 5-7 | EP-IA-002, EP-IA-004 |
| EP-IA-008 | Analytics de Conversaciones | L | 5-7 | EP-IA-001, EP-IA-002 |
| EP-IA-009 | Entrenamiento y Mejora Continua | L | 7-9 | EP-IA-005, EP-IA-008 |
| EP-IA-010 | Multi-Canal y Multi-Tenant | L | 6-8 | EP-IA-001, EP-IA-003 |

**Totales:**
- 10 epicas
- 55 user stories (US-IA-001 a US-IA-055)
- Estimacion total: ~180-220 dev-days

---

## Epicas Detalladas

---

### EP-IA-001: Plataforma de Orquestacion de Agentes (Agent Orchestrator)

**Descripcion:**
Motor central que recibe mensajes de cualquier canal, identifica al usuario, clasifica la intencion mediante NLU, y rutea al agente especializado correcto. Incluye un Agent Registry donde se registran todos los agentes disponibles (tanto los de SuperPago EP-SP-031..040 como los de Marketing EP-MK-014..023), routing rules configurables, fallback handling cuando ningun agente puede atender, y conversation handoff para transferir una conversacion de un agente a otro sin perder contexto.

**Consumidores directos:**
- EP-SP-031 a EP-SP-040 (10 agentes financieros SuperPago)
- EP-MK-014 a EP-MK-023 (10 agentes marketing BaatDigital)
- EP-SP-017/018 (Agente IA WhatsApp Core)

**User Stories:** US-IA-001 a US-IA-006

**Criterios de Aceptacion de la Epica:**
- [ ] Agent Registry con CRUD completo (registrar, listar, activar/desactivar agentes)
- [ ] NLU Classifier que determina intent con confianza >= 0.7
- [ ] Router que despacha al agente correcto segun intent + tenant + permisos
- [ ] Fallback handler con mensaje configurable cuando confianza < 0.7
- [ ] Handoff entre agentes preservando contexto completo de conversacion
- [ ] Interfaz `AgentInterface` que todos los agentes especializados deben implementar
- [ ] API REST: `GET/POST/PUT/DELETE /api/v1/agents`
- [ ] Tests >= 98%

**Repositorio:** `covacha-botia`
**Complejidad:** XL (6 user stories, fundacion de toda la plataforma)

---

### EP-IA-002: Motor de Conversacion (Conversation Engine)

**Descripcion:**
Gestion de conversaciones multi-turno con state machine por conversacion. Incluye memoria de corto plazo (contexto del turno actual) y largo plazo (historial persistente), slot filling para extraer datos estructurados del lenguaje natural, confirmaciones y cancelaciones, y context switching cuando el usuario cambia de tema mid-conversation.

**User Stories:** US-IA-007 a US-IA-012

**Criterios de Aceptacion de la Epica:**
- [ ] State machine configurable por agente con transiciones definidas
- [ ] Memory manager con short-term (TTL 30 min) y long-term (persistente)
- [ ] Slot filler que extrae entidades del mensaje (monto, CLABE, nombre, fecha)
- [ ] Confirmacion explicita antes de operaciones sensibles
- [ ] Cancelacion en cualquier punto del flujo con limpieza de estado
- [ ] Context switching: detectar cambio de tema y ofrecer bifurcacion
- [ ] API REST: `GET/POST /api/v1/conversations`
- [ ] Tests >= 98%

**Repositorio:** `covacha-botia`
**Complejidad:** XL (6 user stories)
**Dependencias:** EP-IA-001

---

### EP-IA-003: Integracion WhatsApp Business API

**Descripcion:**
Integracion completa con Meta WhatsApp Business API. Webhook receiver con verificacion de token, parser de todos los tipos de mensaje (texto, imagen, audio, documento, ubicacion, contacto, botones interactivos, listas), template management para mensajes outbound aprobados por Meta, message sender con rate limiting, status tracking (enviado, entregado, leido), y media handling (descarga, almacenamiento S3, transcripcion de audio).

**User Stories:** US-IA-013 a US-IA-018

**Criterios de Aceptacion de la Epica:**
- [ ] Webhook receiver con verificacion de token Meta en `covacha-webhook`
- [ ] Parser para 8 tipos de mensaje: texto, imagen, audio, documento, ubicacion, contacto, boton, lista
- [ ] Template CRUD con sync a Meta API (crear, editar, eliminar, consultar estado)
- [ ] Message sender con retry y rate limiting (1000 msg/seg maximo por WABA)
- [ ] Status tracking: sent, delivered, read, failed con callbacks
- [ ] Media handler: descarga a S3, thumbnail generation, transcripcion de audio (Whisper)
- [ ] API REST: `POST /api/v1/whatsapp/send`, `GET /api/v1/whatsapp/templates`
- [ ] Tests >= 98%

**Repositorios:** `covacha-webhook`, `covacha-botia`, `mf-whatsapp`
**Complejidad:** L (6 user stories)
**Dependencias:** EP-IA-001

---

### EP-IA-004: Integracion Web Chat (mf-ia)

**Descripcion:**
Widget de chat embeddable en mf-ia con comunicacion WebSocket en tiempo real. Typing indicators, file upload, rich messages (carousels, quick replies, cards), historial de chat persistente, indicador online/offline, y soporte para multiples conversaciones simultaneas.

**User Stories:** US-IA-019 a US-IA-024

**Criterios de Aceptacion de la Epica:**
- [ ] Componente Angular standalone `<sp-chat-widget>` embeddable
- [ ] WebSocket bidireccional con reconexion automatica
- [ ] Typing indicators (usuario escribiendo, bot procesando)
- [ ] File upload con drag-and-drop (imagenes, PDF, maximo 10MB)
- [ ] Rich messages: carousel, quick reply buttons, info cards
- [ ] Historial de chat con scroll infinito y busqueda
- [ ] Tests >= 98% (Karma + Jasmine)

**Repositorios:** `mf-ia`, `covacha-botia`
**Complejidad:** L (6 user stories)
**Dependencias:** EP-IA-001, EP-IA-002

---

### EP-IA-005: Motor de LLM y Prompt Engineering

**Descripcion:**
Capa de abstraccion multi-provider para LLMs. Soporta OpenAI GPT-4 como primario, AWS Bedrock (Claude) como fallback, y es extensible a otros proveedores. Incluye prompt templates versionados con variables, token management con tracking de costos por agente/tenant, response caching para reducir latencia y costos, fallback chain automatico, y A/B testing de prompts.

**User Stories:** US-IA-025 a US-IA-030

**Criterios de Aceptacion de la Epica:**
- [ ] Provider abstraction con Strategy Pattern (OpenAI, Bedrock, Anthropic)
- [ ] Fallback chain: si OpenAI falla -> Bedrock -> respuesta estatica
- [ ] Prompt template CRUD con versionado (draft, active, archived)
- [ ] Token counter y cost tracker por request, por agente, por tenant
- [ ] Response cache con TTL configurable (identico prompt+context = cache hit)
- [ ] A/B testing: asignar % de trafico a diferentes versiones de prompt
- [ ] API REST: `GET/POST/PUT /api/v1/prompts`, `GET /api/v1/llm/usage`
- [ ] Tests >= 98%

**Repositorio:** `covacha-botia`
**Complejidad:** XL (6 user stories, critico para todos los agentes)

---

### EP-IA-006: Knowledge Base y RAG (Retrieval-Augmented Generation)

**Descripcion:**
Sistema de bases de conocimiento donde se ingieren documentos del negocio (PDF, DOCX, paginas web) que se procesan en chunks, se generan embeddings vectoriales, y se almacenan para busqueda semantica. El pipeline RAG recupera los chunks mas relevantes al contexto de la conversacion y los inyecta como contexto en el prompt del LLM, permitiendo respuestas fundamentadas en documentacion real.

**User Stories:** US-IA-031 a US-IA-036

**Criterios de Aceptacion de la Epica:**
- [ ] Ingestion de documentos: PDF, DOCX, URL (web scraping), texto plano
- [ ] Chunking inteligente: por parrafos, respetando limites semanticos
- [ ] Generacion de embeddings (OpenAI ada-002 o Bedrock Titan)
- [ ] Vector store con busqueda por similitud coseno (top-k configurable)
- [ ] RAG pipeline: query -> retrieve chunks -> inject context -> generate response
- [ ] CRUD de knowledge bases por tenant con re-indexacion manual y automatica
- [ ] API REST: `GET/POST/PUT/DELETE /api/v1/knowledge`
- [ ] Tests >= 98%

**Repositorio:** `covacha-botia`
**Complejidad:** XL (6 user stories)
**Dependencias:** EP-IA-005

---

### EP-IA-007: Flow Builder Visual (mf-ia)

**Descripcion:**
Editor visual de flujos conversacionales con interfaz drag-and-drop en mf-ia. Permite a Disenadores de Flujos (no-desarrolladores) crear flujos sin codigo. Tipos de nodos: mensaje de texto, condicion (if/else), llamada a API externa, esperar input del usuario, transferir a otro agente o a humano. Incluye preview interactivo, publicacion con versionado, e import/export de flujos.

**User Stories:** US-IA-037 a US-IA-042

**Criterios de Aceptacion de la Epica:**
- [ ] Canvas drag-and-drop con Angular CDK
- [ ] 6 tipos de nodos: mensaje, condicion, API call, esperar input, transferir agente, delay
- [ ] Conexiones visuales entre nodos con flechas direccionales
- [ ] Panel de propiedades para configurar cada nodo
- [ ] Preview interactivo: simular conversacion paso a paso
- [ ] Publicar flujo con versionado (draft -> published), rollback a version anterior
- [ ] Import/export JSON de flujos
- [ ] API REST: `GET/POST/PUT/DELETE /api/v1/flows`
- [ ] Tests >= 98% (Karma + Jasmine)

**Repositorios:** `mf-ia`, `covacha-botia`
**Complejidad:** XL (6 user stories)
**Dependencias:** EP-IA-002, EP-IA-004

---

### EP-IA-008: Analytics de Conversaciones

**Descripcion:**
Dashboard de metricas de la plataforma IA. Muestra KPIs clave: conversaciones por dia, tasa de resolucion, tiempo promedio de respuesta, satisfaccion del usuario, intents mas frecuentes, intents no resueltos. Funnel de conversion por agente. Exportacion de transcripts para analisis manual. Todo visualizado en mf-ia.

**User Stories:** US-IA-043 a US-IA-048

**Criterios de Aceptacion de la Epica:**
- [ ] Dashboard con KPIs: conversaciones/dia, tasa de resolucion, tiempo promedio, CSAT
- [ ] Filtros por agente, canal, tenant, rango de fechas
- [ ] Funnel de conversion: mensaje inicial -> intent detectado -> resuelto -> satisfecho
- [ ] Top 10 intents mas frecuentes y top 10 intents no resueltos
- [ ] Exportacion de transcripts (CSV, JSON)
- [ ] Graficas de tendencia (linea temporal, comparativo entre agentes)
- [ ] API REST: `GET /api/v1/analytics/conversations`, `GET /api/v1/analytics/agents`
- [ ] Tests >= 98%

**Repositorios:** `mf-ia`, `covacha-botia`
**Complejidad:** L (6 user stories)
**Dependencias:** EP-IA-001, EP-IA-002

---

### EP-IA-009: Entrenamiento y Mejora Continua

**Descripcion:**
Sistema de feedback loop donde los usuarios califican respuestas del bot (pulgar arriba/abajo), los analistas revisan transcripts de baja calidad, y el sistema auto-etiqueta intents para mejorar el clasificador. Incluye dashboard de calidad, generacion de dataset para fine-tuning, A/B testing de agentes (agente nuevo en shadow mode vs agente actual), y metricas de mejora en el tiempo.

**User Stories:** US-IA-049 a US-IA-052

**Criterios de Aceptacion de la Epica:**
- [ ] Widget de feedback en cada respuesta del bot (thumbs up/down + comentario opcional)
- [ ] Dashboard de calidad: % respuestas positivas por agente, tendencia semanal
- [ ] Cola de revision: transcripts con calificacion negativa para revision manual
- [ ] Auto-labeling: sugerir intent correcto para mensajes mal clasificados
- [ ] A/B testing de agentes: shadow mode donde agente nuevo genera respuesta pero no la envia
- [ ] Exportacion de dataset para fine-tuning (formato JSONL compatible con OpenAI)
- [ ] Tests >= 98%

**Repositorios:** `mf-ia`, `covacha-botia`
**Complejidad:** L (4 user stories)
**Dependencias:** EP-IA-005, EP-IA-008

---

### EP-IA-010: Multi-Canal y Multi-Tenant

**Descripcion:**
Abstraccion de canales para soportar WhatsApp (actual), Web Chat (EP-IA-004), y futuros canales (Telegram, SMS, Email, Slack) sin modificar los agentes. Configuracion de canales habilitados por tenant/organizacion. Branding personalizado del bot por tenant (nombre, avatar, colores, welcome message). Horarios de atencion configurables. Respuesta automatica fuera de horario.

**User Stories:** US-IA-053 a US-IA-055

**Criterios de Aceptacion de la Epica:**
- [ ] Channel Adapter interface que normaliza mensajes de cualquier canal
- [ ] Configuracion de canales habilitados por tenant (WhatsApp, Web, Telegram, SMS, Email)
- [ ] Branding de bot por tenant: nombre, avatar, colores, welcome/farewell messages
- [ ] Horarios de atencion por tenant con timezone y respuesta automatica fuera de horario
- [ ] Routing de respuesta al canal de origen (el bot responde por donde le escribieron)
- [ ] API REST: `GET/PUT /api/v1/bots/{tenant_id}/config`
- [ ] Tests >= 98%

**Repositorios:** `covacha-botia`, `mf-ia`
**Complejidad:** L (3 user stories)
**Dependencias:** EP-IA-001, EP-IA-003

---

## User Stories Detalladas

---

### EP-IA-001: Plataforma de Orquestacion de Agentes

---

#### US-IA-001: Registrar agente en el Agent Registry

**Como** Administrador IA
**Quiero** registrar un nuevo agente en la plataforma
**Para** que el orquestador pueda rutear mensajes hacia el

**Criterios de Aceptacion:**
- [ ] `POST /api/v1/agents` crea registro `AGENT#{agent_id}` con nombre, tipo, version, intents soportados
- [ ] Valida que no exista otro agente con el mismo `agent_id`
- [ ] Valida que los intents declarados no colisionen con otro agente activo (warning, no error)
- [ ] Status inicial: `inactive` (requiere activacion explicita)
- [ ] Retorna 201 con el agente creado

**Datos DynamoDB:**
```
PK: AGENT#{agent_id} | SK: META
```

**API:** `POST /api/v1/agents`
**Repo:** `covacha-botia`
**Estimacion:** 3 dev-days

---

#### US-IA-002: Listar y buscar agentes registrados

**Como** Administrador IA
**Quiero** listar todos los agentes registrados con filtros
**Para** ver el estado de la plataforma y gestionar agentes

**Criterios de Aceptacion:**
- [ ] `GET /api/v1/agents` retorna lista paginada de agentes
- [ ] Filtros opcionales: `status` (active/inactive), `type`, `tenant_id`
- [ ] Incluye conteo de conversaciones activas por agente
- [ ] Retorna 200 con array de agentes

**API:** `GET /api/v1/agents`
**Repo:** `covacha-botia`
**Estimacion:** 2 dev-days

---

#### US-IA-003: Clasificar intent con NLU

**Como** Sistema
**Quiero** clasificar automaticamente la intencion de cada mensaje entrante
**Para** determinar cual agente debe atenderlo

**Criterios de Aceptacion:**
- [ ] Recibe mensaje de texto + contexto de sesion
- [ ] Envia al LLM (EP-IA-005) con prompt de clasificacion que incluye lista de intents disponibles
- [ ] Retorna intent name + confidence score (0.0 a 1.0)
- [ ] Si confidence < 0.7, marca como `UNRESOLVED` y activa fallback
- [ ] Persiste clasificacion en `INTENT#LOG#{date}` para analytics
- [ ] Latencia maxima: 500ms (usa cache de prompts)

**Repo:** `covacha-botia`
**Estimacion:** 5 dev-days

---

#### US-IA-004: Rutear mensaje al agente correcto

**Como** Sistema
**Quiero** despachar el mensaje al agente que corresponde segun el intent clasificado
**Para** que el usuario reciba la respuesta del agente especializado

**Criterios de Aceptacion:**
- [ ] Consulta Agent Registry para encontrar agente activo que soporte el intent
- [ ] Verifica que el agente este habilitado para el tenant del usuario
- [ ] Invoca `agent.handle_message(context, message)` del agente seleccionado
- [ ] Si el agente no esta disponible, rutea al fallback agent
- [ ] Registra en `CONV#{conversation_id}` el agente asignado
- [ ] Soporta re-routing si el agente devuelve `HANDOFF` a otro agente

**Repo:** `covacha-botia`
**Estimacion:** 4 dev-days

---

#### US-IA-005: Manejar fallback cuando ningun agente puede atender

**Como** Sistema
**Quiero** responder de forma amigable cuando no se identifica el intent
**Para** que el usuario no quede sin respuesta

**Criterios de Aceptacion:**
- [ ] Si confidence < 0.7 y no hay agente para el intent, activa fallback
- [ ] Fallback responde con mensaje configurable por tenant: "No entendi tu mensaje, estas son las cosas que puedo ayudarte..."
- [ ] Lista los 5 intents mas usados como sugerencias (quick reply buttons en WhatsApp)
- [ ] Si el usuario falla 3 veces seguidas, ofrece escalar a humano
- [ ] Persiste intents fallback en analytics para identificar gaps

**Repo:** `covacha-botia`
**Estimacion:** 3 dev-days

---

#### US-IA-006: Transferir conversacion entre agentes (handoff)

**Como** Sistema
**Quiero** transferir una conversacion de un agente a otro sin perder contexto
**Para** que el usuario no tenga que repetir informacion

**Criterios de Aceptacion:**
- [ ] Agente origen devuelve `HANDOFF(target_agent_id, context_data)`
- [ ] Orquestador copia `memory_short` y `slots` al contexto del agente destino
- [ ] Agente destino recibe conversacion con resumen del contexto previo
- [ ] El usuario recibe mensaje: "Te transfiero con [nombre agente destino] que puede ayudarte mejor con esto"
- [ ] Historial de mensajes se mantiene en la misma conversacion (`CONV#`)
- [ ] Audit trail registra el handoff con timestamp, origen y destino

**Repo:** `covacha-botia`
**Estimacion:** 4 dev-days

---

### EP-IA-002: Motor de Conversacion

---

#### US-IA-007: Crear y gestionar state machine por conversacion

**Como** Sistema
**Quiero** ejecutar una state machine configurable por cada conversacion activa
**Para** guiar el flujo conversacional paso a paso

**Criterios de Aceptacion:**
- [ ] Cada agente define su state machine con estados y transiciones
- [ ] Estado actual se persiste en `CONV#{conv_id} | SK: STATE`
- [ ] Transiciones validan condiciones (slot lleno, confirmacion recibida, timeout)
- [ ] Soporta estados: `INITIAL`, `COLLECTING`, `CONFIRMING`, `EXECUTING`, `DONE`, `ERROR`
- [ ] TTL de 30 minutos de inactividad; vuelve a `INITIAL` al expirar
- [ ] Log de cada transicion para debugging

**Repo:** `covacha-botia`
**Estimacion:** 5 dev-days

---

#### US-IA-008: Gestionar memoria de conversacion (short-term y long-term)

**Como** Sistema
**Quiero** mantener memoria de corto y largo plazo para cada usuario
**Para** que el bot recuerde contexto reciente y preferencias historicas

**Criterios de Aceptacion:**
- [ ] Short-term memory: datos del turno actual (ultimos 10 mensajes, slots, contexto). TTL 30 min.
- [ ] Long-term memory: preferencias del usuario (nombre preferido, cuentas frecuentes, idioma). Persistente.
- [ ] Short-term se inyecta automaticamente en cada llamada al LLM
- [ ] Long-term se consulta al inicio de cada conversacion nueva
- [ ] API para limpiar memoria: `DELETE /api/v1/conversations/{id}/memory`
- [ ] Cumple GDPR: exportar y eliminar toda la memoria de un usuario

**Datos DynamoDB:**
```
PK: CONV#{conv_id} | SK: STATE          # short-term
PK: USER#{user_id} | SK: MEMORY#LONG    # long-term
```

**Repo:** `covacha-botia`
**Estimacion:** 4 dev-days

---

#### US-IA-009: Extraer datos estructurados del mensaje (Slot Filling)

**Como** Sistema
**Quiero** extraer entidades del lenguaje natural para llenar slots de datos
**Para** completar operaciones sin preguntar dato por dato

**Criterios de Aceptacion:**
- [ ] Define slots por agente/flujo: `monto`, `clabe`, `servicio`, `fecha`, `nombre`
- [ ] Usa LLM para extraction: "Del mensaje 'transfiere 500 a la CLABE 012345678901234567' extrae monto=500, clabe=012345678901234567"
- [ ] Si faltan slots obligatorios, pregunta solo los faltantes
- [ ] Validacion de formato por tipo de slot (monto: numerico, CLABE: 18 digitos, etc.)
- [ ] Si el usuario corrige un slot, actualiza sin reiniciar el flujo

**Repo:** `covacha-botia`
**Estimacion:** 4 dev-days

---

#### US-IA-010: Confirmar operacion antes de ejecutar

**Como** Usuario Final
**Quiero** ver un resumen de la operacion antes de confirmarla
**Para** evitar errores en operaciones sensibles

**Criterios de Aceptacion:**
- [ ] Antes de ejecutar operacion sensible, bot presenta resumen estructurado
- [ ] Formato WhatsApp: mensaje con todos los datos + botones "Confirmar" / "Cancelar"
- [ ] Formato Web: card con datos + botones primario/secundario
- [ ] Si usuario confirma, ejecuta la operacion y reporta resultado
- [ ] Si usuario cancela, limpia slots y regresa a estado inicial
- [ ] Timeout de confirmacion: 5 minutos, despues cancela automaticamente

**Repo:** `covacha-botia`
**Estimacion:** 3 dev-days

---

#### US-IA-011: Cancelar flujo en cualquier punto

**Como** Usuario Final
**Quiero** poder cancelar la operacion en cualquier momento escribiendo "cancelar"
**Para** no quedar atrapado en un flujo no deseado

**Criterios de Aceptacion:**
- [ ] Detecta palabras de cancelacion: "cancelar", "salir", "no", "detener", "stop"
- [ ] Limpia slots y short-term memory del flujo actual
- [ ] Regresa state machine a `INITIAL`
- [ ] Responde: "Operacion cancelada. En que mas puedo ayudarte?"
- [ ] No cancela si estamos en medio de una ejecucion ya confirmada

**Repo:** `covacha-botia`
**Estimacion:** 2 dev-days

---

#### US-IA-012: Detectar y manejar cambio de contexto (context switching)

**Como** Sistema
**Quiero** detectar cuando el usuario cambia de tema en medio de un flujo
**Para** ofrecer bifurcacion sin perder el flujo original

**Criterios de Aceptacion:**
- [ ] Si el usuario envia un mensaje cuyo intent no coincide con el agente actual, detecta context switch
- [ ] Ofrece opciones: "Veo que quieres [nuevo tema]. Quieres: 1) Continuar con [tema actual] o 2) Cambiar a [nuevo tema]?"
- [ ] Si cambia, guarda estado del flujo actual para posible retorno
- [ ] Si continua, descarta el mensaje fuera de contexto y repite la pregunta pendiente
- [ ] Maximo 1 nivel de anidamiento (no guardar flujos recursivamente)

**Repo:** `covacha-botia`
**Estimacion:** 3 dev-days

---

### EP-IA-003: Integracion WhatsApp Business API

---

#### US-IA-013: Recibir y verificar webhooks de WhatsApp

**Como** Sistema
**Quiero** recibir webhooks de Meta WhatsApp Business API con verificacion de token
**Para** procesar mensajes entrantes de forma segura

**Criterios de Aceptacion:**
- [ ] `GET /webhook/whatsapp` responde al challenge de verificacion con `hub.verify_token`
- [ ] `POST /webhook/whatsapp` recibe payload de Meta, valida firma HMAC-SHA256
- [ ] Payload valido se publica a SQS `ia-inbound` para procesamiento async
- [ ] Payload invalido retorna 403 y se loggea como alerta
- [ ] Responde 200 inmediatamente (antes de procesar) para cumplir SLA de Meta (< 5 seg)

**API:** `GET/POST /webhook/whatsapp`
**Repo:** `covacha-webhook`
**Estimacion:** 3 dev-days

---

#### US-IA-014: Parsear todos los tipos de mensaje WhatsApp

**Como** Sistema
**Quiero** parsear correctamente los 8 tipos de mensaje de WhatsApp
**Para** que los agentes reciban datos normalizados independientemente del tipo

**Criterios de Aceptacion:**
- [ ] Parser para: `text`, `image`, `audio`, `document`, `location`, `contacts`, `interactive` (button_reply, list_reply)
- [ ] Normaliza a estructura unificada: `{type, content, media_url?, metadata{}}`
- [ ] Imagenes y documentos: descarga media de Meta API, sube a S3, retorna URL S3
- [ ] Audio: descarga, sube a S3, envia a transcripcion (Whisper), retorna texto + URL
- [ ] Ubicacion: extrae latitud, longitud, nombre del lugar
- [ ] Contactos: extrae nombre, telefono, email

**Repo:** `covacha-botia`
**Estimacion:** 4 dev-days

---

#### US-IA-015: Gestionar templates de WhatsApp

**Como** Administrador IA
**Quiero** crear, editar y consultar templates de WhatsApp desde mf-whatsapp
**Para** enviar mensajes outbound aprobados por Meta

**Criterios de Aceptacion:**
- [ ] CRUD de templates en DynamoDB `TEMPLATE#{template_id}`
- [ ] Sync con Meta API: al crear template, lo envia a Meta para aprobacion
- [ ] Consulta periodica de estado (pending, approved, rejected) via cron
- [ ] UI en mf-whatsapp: lista de templates con estado, preview, crear nuevo
- [ ] Soporte para templates con variables: `{{1}}`, `{{2}}`, header image, botones
- [ ] Al enviar mensaje, valida que template este aprobado

**API:** `GET/POST/PUT/DELETE /api/v1/whatsapp/templates`
**Repos:** `covacha-botia`, `mf-whatsapp`
**Estimacion:** 4 dev-days

---

#### US-IA-016: Enviar mensajes via WhatsApp con rate limiting

**Como** Sistema
**Quiero** enviar mensajes outbound respetando limites de Meta
**Para** evitar bloqueos de la cuenta WABA

**Criterios de Aceptacion:**
- [ ] `POST /api/v1/whatsapp/send` envia mensaje a numero destino
- [ ] Soporta: texto libre (dentro de ventana 24h), template (fuera de ventana), media (imagen, doc)
- [ ] Rate limiter: maximo 1000 msg/seg por WABA, cola si se excede
- [ ] Retry con backoff exponencial en caso de error 429 o 500 de Meta
- [ ] Persiste mensaje enviado con `wa_message_id` para tracking

**API:** `POST /api/v1/whatsapp/send`
**Repo:** `covacha-botia`
**Estimacion:** 3 dev-days

---

#### US-IA-017: Rastrear status de mensajes enviados

**Como** Administrador IA
**Quiero** ver el estado de entrega de cada mensaje enviado
**Para** detectar problemas de entrega y medir efectividad

**Criterios de Aceptacion:**
- [ ] Recibe callbacks de status de Meta: `sent`, `delivered`, `read`, `failed`
- [ ] Actualiza estado del mensaje en DynamoDB
- [ ] Si `failed`, registra error_code y error_message de Meta
- [ ] API de consulta: `GET /api/v1/whatsapp/messages/{id}/status`
- [ ] Metricas agregadas: tasa de entrega, tasa de lectura por template

**Repo:** `covacha-botia`
**Estimacion:** 2 dev-days

---

#### US-IA-018: Descargar y procesar media de WhatsApp

**Como** Sistema
**Quiero** descargar automaticamente los archivos media que envian los usuarios
**Para** que los agentes puedan procesar imagenes, audio y documentos

**Criterios de Aceptacion:**
- [ ] Al recibir mensaje con media, descarga archivo de Meta CDN (URL temporal, 24h)
- [ ] Sube a S3 bucket `sp-ia-media/{tenant_id}/{date}/{media_id}.{ext}`
- [ ] Genera thumbnail para imagenes (200x200px)
- [ ] Audio: envia a OpenAI Whisper para transcripcion, almacena texto resultante
- [ ] Limpieza automatica de media > 90 dias (lifecycle policy S3)
- [ ] Maximo 16MB por archivo (limite de WhatsApp)

**Repo:** `covacha-botia`
**Estimacion:** 3 dev-days

---

### EP-IA-004: Integracion Web Chat (mf-ia)

---

#### US-IA-019: Componente Angular de chat widget

**Como** Administrador IA
**Quiero** un componente de chat embeddable en mf-ia
**Para** que los usuarios internos puedan interactuar con los bots desde el portal web

**Criterios de Aceptacion:**
- [ ] Componente standalone `ChatWidgetComponent` con OnPush change detection
- [ ] Icono flotante (bottom-right) que abre panel de chat
- [ ] Panel: header con nombre del bot + avatar, area de mensajes scrolleable, input con boton enviar
- [ ] Soporta temas claro/oscuro segun configuracion del shell (mf-core)
- [ ] Responsive: panel completo en desktop, fullscreen en mobile
- [ ] Animaciones de apertura/cierre (Angular Animations)

**Repo:** `mf-ia`
**Estimacion:** 4 dev-days

---

#### US-IA-020: Comunicacion WebSocket en tiempo real

**Como** Sistema
**Quiero** comunicacion bidireccional via WebSocket entre el chat widget y covacha-botia
**Para** que los mensajes se envien y reciban en tiempo real

**Criterios de Aceptacion:**
- [ ] WebSocket endpoint: `wss://api.superpago.com.mx/ws/chat`
- [ ] Autenticacion via token JWT en el handshake
- [ ] Reconexion automatica con backoff exponencial (1s, 2s, 4s, 8s, max 30s)
- [ ] Heartbeat cada 30 segundos para mantener conexion
- [ ] Si WebSocket no disponible, fallback a polling HTTP cada 3 segundos
- [ ] Eventos: `message`, `typing`, `status_change`, `agent_handoff`

**Repos:** `mf-ia`, `covacha-botia`
**Estimacion:** 4 dev-days

---

#### US-IA-021: Typing indicators y status del bot

**Como** Usuario Final
**Quiero** ver cuando el bot esta procesando mi mensaje
**Para** saber que mi mensaje fue recibido y se esta atendiendo

**Criterios de Aceptacion:**
- [ ] Al recibir mensaje del usuario, envia evento `bot_typing` al WebSocket
- [ ] UI muestra indicador animado de "escribiendo..." (3 puntos)
- [ ] Al enviar respuesta, cancela indicador y muestra el mensaje
- [ ] Si el procesamiento tarda > 10 seg, muestra "Esto puede tardar un momento..."
- [ ] Indicador de estado: online (verde), procesando (amarillo), offline (gris)

**Repos:** `mf-ia`, `covacha-botia`
**Estimacion:** 2 dev-days

---

#### US-IA-022: Upload de archivos en el chat

**Como** Usuario Final
**Quiero** enviar imagenes y documentos en el chat
**Para** que el bot pueda procesarlos

**Criterios de Aceptacion:**
- [ ] Boton de adjuntar archivo en el input del chat
- [ ] Drag-and-drop sobre el area de chat
- [ ] Tipos permitidos: imagenes (jpg, png, gif), documentos (pdf, docx), maximo 10MB
- [ ] Preview de imagen antes de enviar
- [ ] Progress bar durante upload
- [ ] Upload a S3 via presigned URL, luego envia referencia al bot

**Repo:** `mf-ia`
**Estimacion:** 3 dev-days

---

#### US-IA-023: Rich messages en el chat (carousels, quick replies, cards)

**Como** Sistema
**Quiero** renderizar mensajes enriquecidos en el chat web
**Para** ofrecer una experiencia interactiva mas alla de texto plano

**Criterios de Aceptacion:**
- [ ] Quick reply buttons: botones horizontales que el usuario puede clicar
- [ ] Info cards: titulo + descripcion + imagen + boton de accion
- [ ] Carousel: scroll horizontal de cards (minimo 2, maximo 10)
- [ ] Botones con acciones: enviar texto predefinido, abrir URL, ejecutar accion
- [ ] Markdown basico en mensajes de texto: **bold**, *italic*, `code`, links

**Repo:** `mf-ia`
**Estimacion:** 4 dev-days

---

#### US-IA-024: Historial de chat persistente

**Como** Usuario Final
**Quiero** ver el historial de mis conversaciones anteriores
**Para** retomar temas y revisar informacion que me dio el bot

**Criterios de Aceptacion:**
- [ ] Al abrir el chat, carga los ultimos 50 mensajes de la conversacion activa
- [ ] Scroll infinito hacia arriba para cargar mensajes anteriores (paginacion de 50)
- [ ] Lista de conversaciones previas en sidebar (ultimas 20)
- [ ] Busqueda de texto en el historial
- [ ] Cada mensaje muestra timestamp y estado (enviado, leido)
- [ ] Opcion de iniciar conversacion nueva

**Repos:** `mf-ia`, `covacha-botia`
**Estimacion:** 3 dev-days

---

### EP-IA-005: Motor de LLM y Prompt Engineering

---

#### US-IA-025: Abstraccion multi-provider de LLM (Strategy Pattern)

**Como** Sistema
**Quiero** una capa de abstraccion que permita cambiar de proveedor LLM sin modificar agentes
**Para** evitar vendor lock-in y tener fallback automatico

**Criterios de Aceptacion:**
- [ ] Interface `LLMProvider` con metodos: `complete(prompt, config) -> Response`, `embed(text) -> vector`
- [ ] Implementaciones: `OpenAIProvider` (GPT-4), `BedrockProvider` (Claude), extensible a otros
- [ ] Configuracion por tenant y por agente: cual provider usar como primario
- [ ] Factory pattern: `LLMFactory.get_provider(config) -> LLMProvider`
- [ ] Cada provider normaliza respuesta a formato unificado: `{text, tokens_used, model, latency_ms}`

**Repo:** `covacha-botia`
**Estimacion:** 4 dev-days

---

#### US-IA-026: Fallback chain automatico entre providers

**Como** Sistema
**Quiero** que si el provider primario falla, se intente automaticamente con el siguiente
**Para** garantizar disponibilidad de la plataforma IA

**Criterios de Aceptacion:**
- [ ] Cadena configurable: `[OpenAI, Bedrock, StaticFallback]`
- [ ] Si provider retorna error (timeout, 429, 500), intenta el siguiente
- [ ] Timeout configurable por provider (default: OpenAI 30s, Bedrock 45s)
- [ ] Si todos los providers fallan, responde con mensaje estatico: "Estoy experimentando dificultades. Intenta en unos minutos."
- [ ] Registra cada fallback como alerta para monitoreo
- [ ] Circuit breaker: si un provider falla 5 veces en 1 minuto, lo desactiva por 5 minutos

**Repo:** `covacha-botia`
**Estimacion:** 3 dev-days

---

#### US-IA-027: CRUD de prompt templates con versionado

**Como** Administrador IA
**Quiero** crear y versionar prompt templates desde mf-ia
**Para** iterar sobre los prompts sin modificar codigo

**Criterios de Aceptacion:**
- [ ] `POST /api/v1/prompts` crea prompt template con nombre, cuerpo, variables, provider, config LLM
- [ ] Cada edicion crea nueva version (`V#1`, `V#2`, etc.), la anterior se archiva
- [ ] Status: `draft` (en edicion), `active` (en produccion), `archived` (historico)
- [ ] Solo 1 version activa por prompt a la vez
- [ ] UI en mf-ia: lista de prompts, editor con syntax highlighting, historial de versiones
- [ ] Preview: probar prompt con datos de prueba antes de activar

**API:** `GET/POST/PUT /api/v1/prompts`
**Repos:** `covacha-botia`, `mf-ia`
**Estimacion:** 4 dev-days

---

#### US-IA-028: Tracking de tokens y costos por agente/tenant

**Como** Administrador IA
**Quiero** ver cuantos tokens y cuanto dinero consume cada agente y cada tenant
**Para** controlar costos y detectar agentes ineficientes

**Criterios de Aceptacion:**
- [ ] Cada request al LLM registra: tokens_input, tokens_output, model, costo_estimado
- [ ] Agregacion por: agente, tenant, dia, semana, mes
- [ ] Dashboard en mf-ia: graficas de consumo, top 5 agentes mas costosos, tendencia
- [ ] Alertas configurables: "Si agente X supera $100/dia, notificar"
- [ ] `GET /api/v1/llm/usage?agent_id=X&from=Y&to=Z`

**Repos:** `covacha-botia`, `mf-ia`
**Estimacion:** 3 dev-days

---

#### US-IA-029: Cache de respuestas LLM

**Como** Sistema
**Quiero** cachear respuestas del LLM para prompts identicos
**Para** reducir latencia y costos en consultas repetitivas

**Criterios de Aceptacion:**
- [ ] Hash de (prompt_template_id + version + variables_values) como cache key
- [ ] TTL configurable por prompt template (default: 1 hora)
- [ ] Cache en DynamoDB con TTL nativo
- [ ] Cache hit retorna respuesta en < 50ms (vs 1-3s del LLM)
- [ ] Metricas de cache: hit rate, miss rate, ahorro estimado
- [ ] Opcion de invalidar cache manualmente o al activar nueva version del prompt

**Repo:** `covacha-botia`
**Estimacion:** 3 dev-days

---

#### US-IA-030: A/B testing de prompts

**Como** Administrador IA
**Quiero** probar dos versiones de un prompt con porcentajes de trafico configurables
**Para** medir cual version genera mejores respuestas

**Criterios de Aceptacion:**
- [ ] Crear experimento: prompt_id, version_A, version_B, traffic_split (ej: 80/20)
- [ ] Router de prompts asigna version segun split y hash de user_id (consistente)
- [ ] Metricas por version: tiempo respuesta, tokens, feedback positivo/negativo
- [ ] Dashboard de experimento: comparativa lado a lado
- [ ] Finalizar experimento: promover ganador a `active`, archivar perdedor
- [ ] Maximo 1 experimento activo por prompt

**API:** `POST /api/v1/prompts/{id}/experiment`
**Repos:** `covacha-botia`, `mf-ia`
**Estimacion:** 4 dev-days

---

### EP-IA-006: Knowledge Base y RAG

---

#### US-IA-031: CRUD de Knowledge Bases

**Como** Administrador IA
**Quiero** crear y gestionar bases de conocimiento por tenant
**Para** que los agentes respondan con informacion especifica del negocio

**Criterios de Aceptacion:**
- [ ] `POST /api/v1/knowledge` crea KB con nombre, descripcion, tenant_id
- [ ] `GET /api/v1/knowledge` lista KBs del tenant con estadisticas (docs, chunks, ultima indexacion)
- [ ] `PUT /api/v1/knowledge/{id}` actualiza nombre/descripcion
- [ ] `DELETE /api/v1/knowledge/{id}` elimina KB y todos sus documentos/embeddings
- [ ] Limite: 10 KBs por tenant, 1000 documentos por KB

**API:** `GET/POST/PUT/DELETE /api/v1/knowledge`
**Repo:** `covacha-botia`
**Estimacion:** 3 dev-days

---

#### US-IA-032: Ingerir documentos a la Knowledge Base

**Como** Administrador IA
**Quiero** subir documentos PDF, DOCX y URLs para alimentar la knowledge base
**Para** que el bot tenga acceso a informacion actualizada del negocio

**Criterios de Aceptacion:**
- [ ] `POST /api/v1/knowledge/{kb_id}/documents` acepta archivo (multipart) o URL
- [ ] Tipos soportados: PDF (hasta 50 paginas), DOCX, texto plano, URL (web scraping)
- [ ] Procesamiento async via SQS: upload -> cola -> worker extrae texto -> chunking -> embedding
- [ ] Status del documento: `processing`, `indexed`, `error`
- [ ] Notificacion cuando el documento esta listo (o si fallo con razon del error)
- [ ] Maximo 10MB por documento

**API:** `POST /api/v1/knowledge/{kb_id}/documents`
**Repo:** `covacha-botia`
**Estimacion:** 5 dev-days

---

#### US-IA-033: Chunking inteligente de documentos

**Como** Sistema
**Quiero** dividir documentos en chunks semanticos
**Para** que la busqueda vectorial retorne fragmentos relevantes y coherentes

**Criterios de Aceptacion:**
- [ ] Chunking por parrafos con overlap de 2 oraciones entre chunks
- [ ] Tamano objetivo: 500-1000 tokens por chunk
- [ ] Respeta limites semanticos: no corta en medio de oracion, tabla o lista
- [ ] Metadata por chunk: titulo de seccion, numero de pagina, posicion en documento
- [ ] Si el documento tiene headers (H1, H2), usa como separadores principales
- [ ] Registra chunk_count en el documento padre

**Repo:** `covacha-botia`
**Estimacion:** 4 dev-days

---

#### US-IA-034: Generar y almacenar embeddings vectoriales

**Como** Sistema
**Quiero** generar embeddings vectoriales para cada chunk de texto
**Para** habilitar busqueda semantica por similitud

**Criterios de Aceptacion:**
- [ ] Usa OpenAI `text-embedding-ada-002` (1536 dimensiones) como default
- [ ] Fallback a Bedrock Titan Embeddings si OpenAI falla
- [ ] Almacena embeddings en DynamoDB con vector serializado (JSON array)
- [ ] Indice invertido para busqueda rapida (o integracion con OpenSearch Serverless como fase 2)
- [ ] Batch processing: genera embeddings de hasta 100 chunks por request
- [ ] Re-genera embeddings si cambia el modelo de embedding

**Repo:** `covacha-botia`
**Estimacion:** 4 dev-days

---

#### US-IA-035: Busqueda semantica en la Knowledge Base

**Como** Sistema
**Quiero** buscar los chunks mas relevantes dado un query en lenguaje natural
**Para** inyectar contexto preciso en el prompt del LLM

**Criterios de Aceptacion:**
- [ ] Recibe query de texto, genera embedding del query
- [ ] Calcula similitud coseno contra todos los chunks de la KB
- [ ] Retorna top-k chunks (k configurable, default 5) con score de similitud
- [ ] Filtra chunks con score < 0.7 (no relevantes)
- [ ] Latencia maxima: 500ms para KB de hasta 10,000 chunks
- [ ] `GET /api/v1/knowledge/{kb_id}/search?q=texto&top_k=5`

**API:** `GET /api/v1/knowledge/{kb_id}/search`
**Repo:** `covacha-botia`
**Estimacion:** 3 dev-days

---

#### US-IA-036: Pipeline RAG completo (retrieve + augment + generate)

**Como** Sistema
**Quiero** un pipeline que combine busqueda semantica con generacion LLM
**Para** que los agentes den respuestas fundamentadas en documentacion real

**Criterios de Aceptacion:**
- [ ] Pipeline: recibe pregunta -> busca en KB -> inyecta top chunks en prompt -> genera respuesta
- [ ] Prompt template RAG: "Responde la siguiente pregunta usando SOLO la informacion proporcionada: [chunks]. Pregunta: [query]"
- [ ] Si ningun chunk es relevante (score < 0.7), responde: "No tengo informacion sobre eso en mi base de conocimiento"
- [ ] Incluye referencias: "Fuente: [nombre documento], pagina X"
- [ ] Configurable por agente: cual KB usar, top_k, umbral de relevancia
- [ ] Metricas: % respuestas con fuente vs sin fuente, chunks promedio usados

**Repo:** `covacha-botia`
**Estimacion:** 4 dev-days

---

### EP-IA-007: Flow Builder Visual (mf-ia)

---

#### US-IA-037: Canvas drag-and-drop para disenar flujos

**Como** Disenador de Flujos
**Quiero** un canvas visual donde pueda arrastrar y conectar nodos
**Para** crear flujos conversacionales sin escribir codigo

**Criterios de Aceptacion:**
- [ ] Canvas con zoom (ctrl+scroll), pan (click-drag fondo), y grid de fondo
- [ ] Paleta lateral con los 6 tipos de nodo disponibles
- [ ] Drag desde paleta al canvas para crear nodo
- [ ] Seleccionar nodo para ver/editar propiedades en panel lateral derecho
- [ ] Eliminar nodo con tecla Delete o boton en el panel
- [ ] Undo/redo (Ctrl+Z, Ctrl+Shift+Z) con historial de 50 acciones
- [ ] Construido con Angular CDK drag-and-drop + SVG para conexiones

**Repo:** `mf-ia`
**Estimacion:** 6 dev-days

---

#### US-IA-038: Tipos de nodo y configuracion

**Como** Disenador de Flujos
**Quiero** 6 tipos de nodo con configuracion especifica
**Para** modelar cualquier flujo conversacional

**Criterios de Aceptacion:**
- [ ] **Mensaje**: texto libre, markdown, variables `{{slot_name}}`
- [ ] **Condicion**: expresion if/else sobre slots o estado (`if monto > 1000 then ...`)
- [ ] **API Call**: URL, metodo, headers, body template, mapeo de respuesta a slots
- [ ] **Esperar Input**: mensaje de prompt, tipo de dato esperado, validacion, timeout
- [ ] **Transferir Agente**: agente destino, contexto a transferir, mensaje de transicion
- [ ] **Delay**: tiempo de espera en segundos antes de continuar (para UX natural)
- [ ] Cada nodo tiene: nombre editable, descripcion, icono por tipo, color por tipo

**Repo:** `mf-ia`
**Estimacion:** 4 dev-days

---

#### US-IA-039: Conexiones entre nodos

**Como** Disenador de Flujos
**Quiero** conectar nodos con flechas para definir el flujo
**Para** establecer el orden de ejecucion de la conversacion

**Criterios de Aceptacion:**
- [ ] Click en puerto de salida de nodo A + click en puerto de entrada de nodo B = conexion
- [ ] Flechas SVG con curva bezier entre nodos
- [ ] Nodo condicion tiene 2 salidas: "Si" (verde) y "No" (rojo)
- [ ] Validacion: no permitir ciclos infinitos (detectar loops)
- [ ] Validacion: nodo inicial obligatorio (marcado con estrella)
- [ ] Eliminar conexion con click derecho o seleccionar + Delete

**Repo:** `mf-ia`
**Estimacion:** 3 dev-days

---

#### US-IA-040: Preview interactivo del flujo

**Como** Disenador de Flujos
**Quiero** simular una conversacion paso a paso en el flujo que disene
**Para** verificar que funciona correctamente antes de publicar

**Criterios de Aceptacion:**
- [ ] Boton "Preview" abre panel de simulacion tipo chat
- [ ] Ejecuta el flujo nodo por nodo: muestra mensajes, espera input del usuario
- [ ] Nodo condicion evalua con datos de prueba ingresados por el disenador
- [ ] Nodo API Call muestra request/response mock (configurable)
- [ ] Resalta el nodo activo en el canvas durante la simulacion
- [ ] Al finalizar muestra resumen: nodos visitados, tiempo estimado, slots recolectados

**Repos:** `mf-ia`, `covacha-botia`
**Estimacion:** 4 dev-days

---

#### US-IA-041: Publicar y versionar flujos

**Como** Disenador de Flujos
**Quiero** publicar un flujo para que los agentes lo ejecuten
**Para** poner en produccion los cambios al flujo conversacional

**Criterios de Aceptacion:**
- [ ] Status: `draft` (en edicion), `published` (en produccion)
- [ ] Al publicar, crea version inmutable (`V1`, `V2`, etc.)
- [ ] Solo 1 version published a la vez por flujo
- [ ] Rollback: reactivar version anterior con un click
- [ ] Historial de versiones con fecha, autor y changelog
- [ ] `POST /api/v1/flows/{id}/publish`, `POST /api/v1/flows/{id}/rollback/{version}`

**API:** `POST /api/v1/flows/{id}/publish`
**Repos:** `mf-ia`, `covacha-botia`
**Estimacion:** 3 dev-days

---

#### US-IA-042: Import/export de flujos

**Como** Disenador de Flujos
**Quiero** exportar un flujo como JSON e importarlo en otro tenant o ambiente
**Para** reutilizar flujos entre organizaciones y ambientes (dev, staging, prod)

**Criterios de Aceptacion:**
- [ ] `GET /api/v1/flows/{id}/export` retorna JSON completo del flujo (nodos, conexiones, config)
- [ ] `POST /api/v1/flows/import` acepta JSON y crea flujo nuevo en el tenant actual
- [ ] Al importar, genera nuevos IDs para nodos (no colisiona con existentes)
- [ ] Validacion: verifica que el JSON es un flujo valido antes de importar
- [ ] Soporte para export de multiples flujos como ZIP

**API:** `GET /api/v1/flows/{id}/export`, `POST /api/v1/flows/import`
**Repos:** `mf-ia`, `covacha-botia`
**Estimacion:** 2 dev-days

---

### EP-IA-008: Analytics de Conversaciones

---

#### US-IA-043: Dashboard de KPIs de conversaciones

**Como** Analista de Conversaciones
**Quiero** un dashboard con KPIs principales de la plataforma IA
**Para** monitorear la salud y rendimiento de los agentes

**Criterios de Aceptacion:**
- [ ] KPIs mostrados: total conversaciones (hoy, semana, mes), tasa de resolucion (%), tiempo promedio de respuesta, CSAT promedio
- [ ] Graficas de tendencia: linea temporal de los ultimos 30 dias
- [ ] Comparativo entre periodos: esta semana vs semana pasada
- [ ] Auto-refresh cada 5 minutos
- [ ] Filtros: rango de fechas, canal (WhatsApp/Web), tenant

**Repo:** `mf-ia`
**Estimacion:** 4 dev-days

---

#### US-IA-044: Metricas por agente

**Como** Analista de Conversaciones
**Quiero** ver metricas desglosadas por agente
**Para** identificar que agentes rinden bien y cuales necesitan mejora

**Criterios de Aceptacion:**
- [ ] Tabla de agentes con columnas: nombre, conversaciones, tasa resolucion, CSAT, tiempo promedio
- [ ] Click en agente abre detalle con graficas de tendencia propias
- [ ] Ranking de agentes por cada metrica (mejor a peor)
- [ ] Indicadores de semaforo: verde (>80% resolucion), amarillo (60-80%), rojo (<60%)
- [ ] `GET /api/v1/analytics/agents`

**API:** `GET /api/v1/analytics/agents`
**Repos:** `mf-ia`, `covacha-botia`
**Estimacion:** 3 dev-days

---

#### US-IA-045: Top intents resueltos y no resueltos

**Como** Analista de Conversaciones
**Quiero** ver los intents mas frecuentes y los que mas fallan
**Para** priorizar mejoras en los agentes y agregar capacidades faltantes

**Criterios de Aceptacion:**
- [ ] Top 10 intents mas frecuentes con: nombre, count, agente que atiende, tasa resolucion
- [ ] Top 10 intents no resueltos (confidence < 0.7) con: mensaje ejemplo, frecuencia
- [ ] Grafica de distribucion de intents (pie chart o treemap)
- [ ] Filtro por periodo y por agente
- [ ] Accion rapida: click en intent no resuelto -> crear training example (link a EP-IA-009)

**Repos:** `mf-ia`, `covacha-botia`
**Estimacion:** 3 dev-days

---

#### US-IA-046: Funnel de conversion por agente

**Como** Analista de Conversaciones
**Quiero** ver el funnel completo de cada agente
**Para** detectar donde se pierden los usuarios en el flujo

**Criterios de Aceptacion:**
- [ ] Funnel de 5 pasos: Mensaje recibido -> Intent detectado -> Agente asignado -> Flujo completado -> Satisfecho
- [ ] Porcentaje de conversion entre cada paso
- [ ] Drill-down: click en paso con baja conversion muestra transcripts de ejemplo
- [ ] Comparativo entre agentes en el mismo funnel
- [ ] Periodo configurable: ultima semana, ultimo mes, custom

**Repos:** `mf-ia`, `covacha-botia`
**Estimacion:** 4 dev-days

---

#### US-IA-047: Exportacion de transcripts

**Como** Analista de Conversaciones
**Quiero** exportar transcripts de conversaciones
**Para** analisis manual offline o entrenamiento de modelos

**Criterios de Aceptacion:**
- [ ] `GET /api/v1/analytics/conversations/export?format=csv&from=X&to=Y`
- [ ] Formatos: CSV (tabular), JSON (estructurado), JSONL (para fine-tuning)
- [ ] Filtros: agente, canal, resolucion (resuelto/no resuelto), CSAT, periodo
- [ ] CSV incluye: conversation_id, timestamp, user_message, bot_response, intent, agent, resolved
- [ ] Maximo 10,000 conversaciones por export
- [ ] Anonimizacion opcional: reemplazar datos sensibles (telefono, CLABE) con placeholders

**API:** `GET /api/v1/analytics/conversations/export`
**Repo:** `covacha-botia`
**Estimacion:** 3 dev-days

---

#### US-IA-048: Graficas de tendencia y comparativos

**Como** Analista de Conversaciones
**Quiero** graficas de tendencia con comparativos temporales
**Para** medir la mejora de la plataforma en el tiempo

**Criterios de Aceptacion:**
- [ ] Grafica de linea: conversaciones por dia (ultimos 30/60/90 dias)
- [ ] Grafica de linea: CSAT promedio por semana
- [ ] Grafica de barras: resolucion por agente (comparativo mensual)
- [ ] Overlay: comparar periodo actual vs periodo anterior (linea punteada)
- [ ] Exportar graficas como PNG o PDF
- [ ] Componentes Angular reutilizables con ngx-charts o similar

**Repo:** `mf-ia`
**Estimacion:** 3 dev-days

---

### EP-IA-009: Entrenamiento y Mejora Continua

---

#### US-IA-049: Widget de feedback en respuestas del bot

**Como** Usuario Final
**Quiero** calificar cada respuesta del bot con pulgar arriba o abajo
**Para** indicar si la respuesta fue util o no

**Criterios de Aceptacion:**
- [ ] Debajo de cada respuesta del bot: iconos de pulgar arriba y pulgar abajo
- [ ] Al dar feedback negativo, muestra campo opcional para comentario
- [ ] Persiste en DynamoDB vinculado al mensaje: `CONV#{conv_id} | MSG#{msg_id}` + feedback attrs
- [ ] Solo permite un feedback por mensaje (idempotente)
- [ ] Funciona tanto en Web Chat como en WhatsApp (en WA usa reaction emoji como proxy)

**Repos:** `mf-ia`, `covacha-botia`
**Estimacion:** 3 dev-days

---

#### US-IA-050: Dashboard de calidad y cola de revision

**Como** Analista de Conversaciones
**Quiero** ver un dashboard de calidad y una cola de transcripts con feedback negativo
**Para** identificar y corregir problemas en las respuestas del bot

**Criterios de Aceptacion:**
- [ ] KPIs de calidad: % positivo, % negativo, % sin feedback, tendencia semanal
- [ ] Cola de revision: lista de conversaciones con feedback negativo, ordenada por fecha
- [ ] Click en conversacion abre transcript completo con el mensaje senalado resaltado
- [ ] Acciones del analista: marcar como "revisado", "corregido", "ignorado", agregar nota
- [ ] Filtro por agente, severidad (negativo con comentario priorizado)

**Repos:** `mf-ia`, `covacha-botia`
**Estimacion:** 4 dev-days

---

#### US-IA-051: A/B testing de agentes (shadow mode)

**Como** Administrador IA
**Quiero** poner un agente nuevo en shadow mode contra el agente actual
**Para** comparar calidad de respuestas antes de hacer el switch

**Criterios de Aceptacion:**
- [ ] Shadow mode: agente nuevo recibe los mismos mensajes que el actual, genera respuesta, pero NO la envia
- [ ] Respuestas shadow se almacenan para comparacion posterior
- [ ] Dashboard de comparacion: respuesta actual vs respuesta shadow lado a lado
- [ ] Metricas: % donde shadow fue mejor/peor/igual (evaluacion manual o automatica via LLM)
- [ ] Promover agente shadow a produccion con un click

**Repos:** `covacha-botia`, `mf-ia`
**Estimacion:** 5 dev-days

---

#### US-IA-052: Exportar dataset para fine-tuning

**Como** Administrador IA
**Quiero** exportar conversaciones de alta calidad como dataset de entrenamiento
**Para** hacer fine-tuning del modelo o mejorar el clasificador de intents

**Criterios de Aceptacion:**
- [ ] Seleccionar conversaciones por filtros: solo feedback positivo, solo resueltas, por agente
- [ ] Exportar en formato JSONL compatible con OpenAI fine-tuning API
- [ ] Formato: `{"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}`
- [ ] Incluir intent labels para entrenamiento de clasificador
- [ ] Sanitizacion automatica de datos personales (PII) antes de exportar
- [ ] Estadisticas del dataset: total ejemplos, distribucion por intent, distribucion por agente

**API:** `POST /api/v1/training/export`
**Repo:** `covacha-botia`
**Estimacion:** 3 dev-days

---

### EP-IA-010: Multi-Canal y Multi-Tenant

---

#### US-IA-053: Channel Adapter para normalizacion de canales

**Como** Sistema
**Quiero** una capa de abstraccion que normalice mensajes de diferentes canales
**Para** que los agentes no necesiten saber por cual canal llego el mensaje

**Criterios de Aceptacion:**
- [ ] Interface `ChannelAdapter` con: `parse_inbound(raw) -> NormalizedMessage`, `send_outbound(message, channel_config) -> Result`
- [ ] Implementaciones: `WhatsAppAdapter`, `WebChatAdapter`, extensible a `TelegramAdapter`, `SMSAdapter`, `EmailAdapter`
- [ ] NormalizedMessage: `{channel, user_id, content, content_type, media_url, metadata, timestamp}`
- [ ] Respuesta se serializa segun canal destino (WhatsApp: botones interactivos, Web: HTML cards, Email: HTML template)
- [ ] Factory: `ChannelFactory.get_adapter(channel_type) -> ChannelAdapter`

**Repo:** `covacha-botia`
**Estimacion:** 4 dev-days

---

#### US-IA-054: Configuracion de bot por tenant (branding y horarios)

**Como** Administrador IA
**Quiero** configurar el nombre, avatar, colores y horarios del bot por cada tenant
**Para** que cada organizacion tenga un bot personalizado a su marca

**Criterios de Aceptacion:**
- [ ] `PUT /api/v1/bots/{tenant_id}/config` actualiza configuracion del bot
- [ ] Campos: name, avatar_url, primary_color, welcome_message, farewell_message, fallback_message
- [ ] Horarios de atencion: dias de la semana, hora inicio/fin, timezone
- [ ] Fuera de horario: mensaje automatico "Nuestro horario de atencion es L-V 9:00-18:00. Te responderemos pronto."
- [ ] Canales habilitados por tenant: `["whatsapp", "web"]`
- [ ] UI en mf-ia: formulario de configuracion del bot con preview

**API:** `GET/PUT /api/v1/bots/{tenant_id}/config`
**Repos:** `covacha-botia`, `mf-ia`
**Estimacion:** 3 dev-days

---

#### US-IA-055: Habilitar canales por tenant/organizacion

**Como** Administrador IA
**Quiero** habilitar o deshabilitar canales de comunicacion por organizacion
**Para** que cada tenant use solo los canales que tiene contratados

**Criterios de Aceptacion:**
- [ ] Lista de canales disponibles en la plataforma: WhatsApp, Web Chat, Telegram, SMS, Email
- [ ] Por tenant, configurar cuales estan habilitados (toggle on/off)
- [ ] Si un mensaje llega por un canal deshabilitado, responde: "Este canal no esta habilitado para tu organizacion"
- [ ] Configuracion especifica por canal (ej: WhatsApp requiere WABA ID, Telegram requiere Bot Token)
- [ ] UI en mf-ia: tabla de canales con toggle y formulario de configuracion por canal
- [ ] `GET /api/v1/bots/{tenant_id}/channels`, `PUT /api/v1/bots/{tenant_id}/channels/{channel}`

**API:** `GET/PUT /api/v1/bots/{tenant_id}/channels`
**Repos:** `covacha-botia`, `mf-ia`
**Estimacion:** 3 dev-days

---

## Roadmap

```
Sprint 1-3 (Fundaciones)
├── EP-IA-001: Orquestador de Agentes          ████████████████████████████  [S1------S3]
├── EP-IA-003: Integracion WhatsApp             ████████████████████████████  [S1------S3]
└── EP-IA-005: Motor de LLM                     ████████████████████████████  [S1------S3]

Sprint 2-4 (Motor de Conversacion)
└── EP-IA-002: Motor de Conversacion             ████████████████████████████  [S2------S4]

Sprint 3-5 (Web Chat)
└── EP-IA-004: Web Chat (mf-ia)                    ████████████████████████  [S3----S5]

Sprint 4-6 (Knowledge Base)
└── EP-IA-006: Knowledge Base / RAG                  ████████████████████████  [S4----S6]

Sprint 5-7 (Flow Builder + Analytics)
├── EP-IA-007: Flow Builder Visual                     ████████████████████████  [S5----S7]
└── EP-IA-008: Analytics de Conversaciones             ████████████████████████  [S5----S7]

Sprint 6-8 (Multi-Canal)
└── EP-IA-010: Multi-Canal y Multi-Tenant                ████████████████████████  [S6----S8]

Sprint 7-9 (Mejora Continua)
└── EP-IA-009: Entrenamiento y Mejora Continua             ████████████████████████  [S7----S9]

Sprint 10+ (Agentes Especializados - OTROS DOCUMENTOS)
├── EP-SP-031..040: Agentes SuperPago                        ██████████████████████████
└── EP-MK-014..023: Agentes Marketing                        ██████████████████████████
```

**Nota:** Los agentes especializados de SuperPago (EP-SP-031 a EP-SP-040) y Marketing (EP-MK-014 a EP-MK-023) comienzan DESPUES de que la plataforma base este funcional (EP-IA-001 a EP-IA-005 minimo). Estan definidos en sus documentos respectivos.

### Hitos Clave

| Hito | Sprint | Criterio |
|------|--------|----------|
| Plataforma IA funcional | S3 | EP-IA-001 + EP-IA-003 + EP-IA-005 operativos. Un agente puede recibir mensaje WhatsApp, clasificar intent, generar respuesta con LLM, y responder. |
| Conversaciones multi-turno | S4 | EP-IA-002 operativo. Agentes pueden mantener estado, hacer slot filling, confirmaciones. |
| Web Chat operativo | S5 | EP-IA-004 operativo. Chat en mf-ia funcionando con WebSocket. |
| Knowledge Base habilitada | S6 | EP-IA-006 operativo. Agentes responden con RAG sobre documentos del negocio. |
| Flow Builder publicado | S7 | EP-IA-007 operativo. Disenadores pueden crear flujos sin codigo. |
| Analytics y mejora continua | S9 | EP-IA-008 + EP-IA-009 operativos. Feedback loop completo. |
| Plataforma multi-canal | S8 | EP-IA-010 operativo. Canales adicionales configurables por tenant. |

---

## Grafo de Dependencias

```
                    ┌──────────────┐
                    │  EP-IA-005   │
                    │  Motor LLM   │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
     ┌──────────────┐ ┌──────────┐ ┌──────────────┐
     │  EP-IA-006   │ │EP-IA-009 │ │  EP-IA-001   │
     │  KB / RAG    │ │ Mejora   │ │ Orquestador  │
     └──────────────┘ │ Continua │ └──────┬───────┘
                      └─────┬────┘        │
                            │    ┌────────┼────────────┬────────────┐
                            │    │        │            │            │
                            │    ▼        ▼            ▼            ▼
                            │ ┌────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
                            │ │EP-IA-  │ │EP-IA-002 │ │EP-IA-003 │ │EP-IA-010 │
                            │ │008     │ │ Motor    │ │ WhatsApp │ │ Multi-   │
                            │ │Analytic│ │ Conv     │ │ Integr   │ │ Canal    │
                            │ └───┬────┘ └────┬─────┘ └──────────┘ └──────────┘
                            │     │           │
                            ▼     │           ▼
                      ┌───────────┘    ┌──────────────┐
                      │                │  EP-IA-004   │
                      │                │  Web Chat    │
                      │                └──────┬───────┘
                      │                       │
                      │                       ▼
                      │                ┌──────────────┐
                      └───────────────►│  EP-IA-007   │
                                       │ Flow Builder │
                                       └──────────────┘

Dependencias explicitas:
EP-IA-001 (Orquestador)   → sin dependencias internas (usa EP-IA-005 para NLU)
EP-IA-002 (Motor Conv)    → EP-IA-001
EP-IA-003 (WhatsApp)      → EP-IA-001
EP-IA-004 (Web Chat)      → EP-IA-001, EP-IA-002
EP-IA-005 (Motor LLM)     → sin dependencias internas
EP-IA-006 (KB / RAG)      → EP-IA-005
EP-IA-007 (Flow Builder)  → EP-IA-002, EP-IA-004
EP-IA-008 (Analytics)     → EP-IA-001, EP-IA-002
EP-IA-009 (Mejora)        → EP-IA-005, EP-IA-008
EP-IA-010 (Multi-Canal)   → EP-IA-001, EP-IA-003

Consumidores externos (otros documentos):
EP-SP-031..040 (Agentes SuperPago)   → EP-IA-001, EP-IA-002, EP-IA-005
EP-MK-014..023 (Agentes Marketing)   → EP-IA-001, EP-IA-002, EP-IA-005
EP-SP-017/018 (WhatsApp Core)        → EP-IA-001, EP-IA-003
```

---

## Riesgos y Mitigaciones

| # | Riesgo | Probabilidad | Impacto | Mitigacion |
|---|--------|-------------|---------|------------|
| R1 | **Latencia LLM alta** (>3s por respuesta) | Alta | Alto | Cache agresivo (US-IA-029), fallback a respuestas pre-computadas, streaming de respuesta en web chat |
| R2 | **Costos de OpenAI se disparan** con 20 agentes activos | Alta | Alto | Token tracking granular (US-IA-028), cache de respuestas, limites por tenant, Bedrock como alternativa mas economica |
| R3 | **WhatsApp Business API rate limiting** en picos de trafico | Media | Alto | Cola SQS para buffering, rate limiter propio antes de enviar, multiples WABAs si necesario |
| R4 | **Calidad de clasificacion NLU baja** con muchos intents (20+ agentes x 5+ intents cada uno) | Alta | Alto | Clasificacion jerarquica (primero dominio, luego intent), embeddings de intents pre-computados, fine-tuning del clasificador |
| R5 | **Vector store en DynamoDB no escala** para busqueda semantica con >100K chunks | Media | Medio | Fase 1 en DynamoDB, fase 2 migrar a OpenSearch Serverless o Pinecone. Abstraccion desde dia 1. |
| R6 | **Colision de intents** entre agentes de SuperPago y Marketing | Media | Medio | Namespace por producto en intents (`sp.transfer`, `mk.content`), router jerarquico que primero determina dominio |
| R7 | **Flow Builder complejo para no-tecnicos** | Media | Medio | Templates pre-construidos para flujos comunes, wizard guiado, documentacion con videos |
| R8 | **Datos sensibles en transcripts** (numeros de tarjeta, CLABEs en conversaciones) | Alta | Critico | PII detection en tiempo real, enmascaramiento antes de persistir, sanitizacion en exports (US-IA-052) |
| R9 | **Disponibilidad de proveedores IA** (OpenAI outage) | Baja | Critico | Fallback chain (US-IA-026) con circuit breaker, respuestas estaticas como ultimo recurso |
| R10 | **Multi-tenancy leaks** (un tenant ve conversaciones de otro) | Baja | Critico | Tenant isolation en todas las queries DynamoDB (partition key incluye tenant_id), validacion en middleware, tests de aislamiento |
