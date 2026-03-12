# EP-MK-030: Sistema de Orquestacion Multi-Agente IA para Marketing Autonomo

> **Estado: EN PROGRESO** — Fases 1, 2 y 3 completadas. Fases 4 y 5 pendientes.

## Vision General

Sistema donde un **Agente Coordinador (Claude)** orquesta multiples agentes de IA (Gemini, ChatGPT, Perplexity) para:
1. Disenar estrategias de marketing basadas en objetivos del equipo
2. Generar contenido automaticamente (texto, imagenes, video)
3. Monitorear metricas en tiempo real (cada 2 min)
4. Evaluar cumplimiento de objetivos y re-ajustar estrategias

---

## Arquitectura del Sistema

```
                    +---------------------------+
                    |   EQUIPO DE MARKETING     |
                    |   Define: Objetivo +      |
                    |   Presupuesto + Plazo     |
                    +-------------+-------------+
                                  |
                                  v
                    +---------------------------+
                    |  AGENTE COORDINADOR       |
                    |  (Claude Sonnet/Opus)     |
                    |                           |
                    |  - Analiza objetivo        |
                    |  - Descompone en tareas   |
                    |  - Asigna a agentes       |
                    |  - Evalua resultados      |
                    |  - Re-planifica           |
                    +--+------+------+----------+
                       |      |      |
              +--------+  +---+---+  +--------+
              v           v         v          v
    +-----------+ +----------+ +---------+ +----------+
    | AGENTE    | | AGENTE   | | AGENTE  | | AGENTE   |
    | RESEARCH  | | COPY     | | VISUAL  | | ANALYTICS|
    | Perplexity| | ChatGPT  | | Gemini  | | Claude   |
    |           | |          | |         | |          |
    | Investiga | | Genera   | | Genera  | | Analiza  |
    | mercado,  | | captions,| | imgs,   | | metricas,|
    | trends,   | | scripts, | | videos, | | evalua   |
    | benchmark | | hashtags | | thumbs  | | KPIs     |
    +-----------+ +----------+ +---------+ +----------+
                       |      |      |
                       v      v      v
              +---------------------------+
              |   CONTENT PIPELINE        |
              |   Auto-genera + programa  |
              |   + publica + mide        |
              +---------------------------+
                          |
                          v
              +---------------------------+
              |   METRICS COLLECTOR       |
              |   Polling cada 2 min      |
              |   FB/IG API insights      |
              +---------------------------+
                          |
                          v
              +---------------------------+
              |   EVALUADOR DE ESTRATEGIA |
              |   Compliance check        |
              |   Re-evaluacion auto      |
              |   Alertas + sugerencias   |
              +---------------------------+
```

---

## FASE 1: Backend - Orquestador Multi-Agente (EP-MK-030-F1)

> **Estado: COMPLETADO (backend)** — Orquestador, 4 agentes, controller y routes implementados. 120 tests passing (33 orchestrator + 28 scheduler + 59 agent tests).

### US-MK-201: Servicio de Orquestacion de Agentes IA

**Descripcion:** Crear un servicio backend que actue como coordinador central, recibiendo un objetivo de marketing y delegando tareas a diferentes proveedores de IA.

**Archivo:** `covacha-core/src/mipay_core/services/ai_orchestrator_service.py`

**Modelo de datos:**

```python
# Tabla: modcore_ai_orchestration_sessions
{
    "PK": "ORG#{org_id}",
    "SK": "AI_SESSION#{session_id}",
    "session_id": "uuid",
    "sp_organization_id": "uuid",
    "sp_client_id": "uuid",
    "strategy_id": "uuid",

    # Objetivo definido por el equipo
    "objective": {
        "description": "Aumentar ventas online 30% en Q2",
        "category": "CONVERSIONS",  # AWARENESS|ENGAGEMENT|TRAFFIC|LEADS|CONVERSIONS
        "target_metric": "sales",
        "target_value": 30,
        "target_unit": "PERCENTAGE",
        "deadline": "2026-06-30",
        "budget": 50000,
        "currency": "MXN",
        "platforms": ["facebook", "instagram"],
        "audience_description": "Mujeres 25-45, CDMX, interesadas en moda"
    },

    # Plan generado por el coordinador
    "plan": {
        "phases": [
            {
                "id": "phase-1",
                "name": "Investigacion de mercado",
                "agent": "RESEARCH",
                "provider": "perplexity",
                "status": "COMPLETED",
                "tasks": [...],
                "output": {...},
                "started_at": "...",
                "completed_at": "..."
            },
            {
                "id": "phase-2",
                "name": "Generacion de contenido",
                "agent": "COPY",
                "provider": "openai",
                "status": "IN_PROGRESS",
                "tasks": [...]
            }
        ],
        "total_phases": 5,
        "current_phase": 2,
        "estimated_completion": "2026-03-15"
    },

    "status": "IN_PROGRESS",  # PLANNING|IN_PROGRESS|PAUSED|COMPLETED|FAILED
    "created_at": "...",
    "updated_at": "..."
}
```

**Endpoints nuevos:**

| Method | Route | Descripcion |
|--------|-------|-------------|
| POST | `/organization/{org_id}/ai/orchestrate` | Iniciar sesion de orquestacion con objetivo |
| GET | `/organization/{org_id}/ai/sessions` | Listar sesiones activas |
| GET | `/organization/{org_id}/ai/sessions/{id}` | Detalle de sesion con progreso |
| POST | `/organization/{org_id}/ai/sessions/{id}/pause` | Pausar sesion |
| POST | `/organization/{org_id}/ai/sessions/{id}/resume` | Reanudar sesion |
| POST | `/organization/{org_id}/ai/sessions/{id}/adjust` | Ajustar plan (re-planificar) |
| DELETE | `/organization/{org_id}/ai/sessions/{id}` | Cancelar sesion |

**Flujo del orquestador:**

```python
class AIOrchestrator:
    """
    Coordinador central que usa Claude como cerebro.
    Recibe un objetivo y genera un plan de ejecucion multi-agente.
    """

    def orchestrate(self, objective: dict) -> OrchestrationSession:
        # 1. Claude analiza el objetivo y genera plan
        plan = self.coordinator.create_plan(objective)

        # 2. Fase Research: Perplexity investiga mercado
        research = self.research_agent.execute(plan.research_tasks)

        # 3. Fase Strategy: Claude refina estrategia con research
        strategy = self.coordinator.refine_strategy(objective, research)

        # 4. Fase Content: ChatGPT genera textos
        content = self.copy_agent.generate_batch(strategy.content_plan)

        # 5. Fase Visual: Gemini genera imagenes/video
        visuals = self.visual_agent.generate_batch(strategy.visual_plan)

        # 6. Fase Assembly: Combina y programa publicaciones
        posts = self.assemble_posts(content, visuals, strategy.calendar)

        # 7. Retorna sesion con plan completo
        return session
```

**Criterios de aceptacion:**
- [x] Endpoint POST /ai/orchestrate acepta objetivo y retorna session_id
- [x] Claude genera plan con fases y tareas especificas
- [x] Cada fase delega a proveedor correcto (Perplexity, ChatGPT, Gemini)
- [x] Plan incluye calendario de contenido auto-generado
- [x] Sesion persiste en DynamoDB con estado actualizable
- [x] Manejo de errores: si un agente falla, el coordinador re-intenta o ajusta

> **Estado: COMPLETADO** — `ai_orchestrator_service.py` + `ai_orchestrator_controller.py` + `ai_orchestration.py` routes. 33 tests passing.

---

### US-MK-202: Agente de Investigacion (Perplexity)

**Descripcion:** Integrar Perplexity API como agente de investigacion de mercado, tendencias y benchmarks.

**Archivo:** `covacha-core/src/mipay_core/services/agents/research_agent.py`

**Tareas que ejecuta:**
1. Investigar tendencias del sector/industria del cliente
2. Analizar competencia (que publican, que funciona)
3. Identificar mejores horarios de publicacion
4. Sugerir hashtags trending
5. Benchmarks de metricas por industria

**Request a Perplexity:**
```python
{
    "model": "sonar-pro",
    "messages": [
        {
            "role": "system",
            "content": "Eres un investigador de marketing digital..."
        },
        {
            "role": "user",
            "content": "Investiga tendencias de marketing para {industria} en {region}. El objetivo es {objetivo}. Dame: 1) Trends actuales 2) Benchmarks de engagement 3) Mejores horarios 4) Hashtags trending 5) Que hace la competencia"
        }
    ],
    "search_domain_filter": ["instagram.com", "facebook.com", "statista.com"],
    "return_citations": true
}
```

**Output estructurado:**
```python
{
    "trends": [...],
    "benchmarks": {"avg_engagement": 3.5, "avg_reach": 1000},
    "best_times": [{"day": "monday", "hour": 10}, ...],
    "trending_hashtags": [...],
    "competitor_insights": [...],
    "citations": [...]  # URLs de las fuentes
}
```

**Criterios de aceptacion:**
- [x] Integracion con Perplexity API (sonar-pro)
- [x] Output estructurado parseado desde respuesta natural
- [x] Citations incluidas para transparencia
- [x] Cache de resultados (misma query < 24h no re-ejecuta)
- [x] Fallback a ChatGPT web search si Perplexity falla

> **Estado: COMPLETADO** — `research_agent.py` implementado en covacha-core. Tests passing.

---

### US-MK-203: Agente de Copywriting (ChatGPT)

**Descripcion:** ChatGPT como agente especializado en generacion de textos para redes sociales.

**Archivo:** `covacha-core/src/mipay_core/services/agents/copy_agent.py`

**Extiende el AIContentService existente** para soportar generacion en batch:

**Tareas que ejecuta:**
1. Generar captions para posts (por plataforma)
2. Crear scripts de carruseles (5-10 slides)
3. Crear scripts de reels/videos
4. Generar variaciones A/B de textos
5. Adaptar contenido por plataforma (FB vs IG vs TikTok)

**Batch generation:**
```python
def generate_content_batch(self, content_plan: list) -> list:
    """
    Recibe plan de contenido (20-30 posts/mes) y genera
    todo el texto para cada uno.
    """
    results = []
    for item in content_plan:
        result = self.generate(
            type=item["content_type"],  # caption, carousel, reel
            prompt=item["topic"],
            context=item["brand_context"],
            platform=item["platform"],
            tone=item["tone"]
        )
        results.append(result)
    return results
```

**Criterios de aceptacion:**
- [x] Genera batch de 20-30 piezas de contenido en una sola llamada
- [x] Respeta tono de marca (del Brand Kit del cliente)
- [x] Incluye hashtags relevantes (del research)
- [x] Genera variaciones A/B (2 opciones por post)
- [x] Adapta formato por plataforma (FB largo, IG medio, TikTok corto)

> **Estado: COMPLETADO** — `copy_agent.py` implementado en covacha-core. Tests passing.

---

### US-MK-204: Agente Visual (Gemini + Integraciones)

**Descripcion:** Gemini como agente para generacion de imagenes y conceptos visuales, con integracion a APIs de generacion de imagen/video.

**Archivo:** `covacha-core/src/mipay_core/services/agents/visual_agent.py`

**Tareas que ejecuta:**
1. Generar prompts detallados para imagenes (a partir del contenido)
2. Llamar APIs de generacion de imagen (DALL-E 3, Midjourney API, Imagen)
3. Generar thumbnails para videos
4. Crear conceptos de carrusel (layout + colores)
5. Sugerir ediciones de video (scene cuts, overlays)

**Flujo de generacion visual:**
```python
def generate_visuals(self, content_item: dict, brand_kit: dict) -> dict:
    # 1. Gemini analiza el copy y brand kit
    visual_brief = self.gemini.analyze(
        copy=content_item["text"],
        brand_colors=brand_kit["colors"],
        brand_fonts=brand_kit["fonts"],
        style=brand_kit["visual_style"]
    )

    # 2. Genera prompt optimizado para imagen
    image_prompt = visual_brief["image_prompt"]

    # 3. Llama API de generacion de imagen
    image = self.image_generator.generate(
        prompt=image_prompt,
        style=visual_brief["style"],
        aspect_ratio=content_item["aspect_ratio"],  # 1:1, 9:16, 16:9
        brand_colors=brand_kit["colors"]
    )

    # 4. Sube a S3
    url = self.s3.upload(image, folder=f"ai-generated/{client_id}/")

    return {
        "image_url": url,
        "prompt_used": image_prompt,
        "style": visual_brief["style"],
        "alt_text": visual_brief["alt_text"]
    }
```

**Criterios de aceptacion:**
- [x] Gemini genera prompts visuales alineados al brand kit
- [x] Integracion con al menos 1 API de imagen (DALL-E 3 o Imagen)
- [x] Imagenes en formatos correctos (1:1 feed, 9:16 stories/reels, 16:9 cover)
- [x] Auto-upload a S3 con URL accesible
- [x] Para video: genera storyboard con instrucciones de edicion

> **Estado: COMPLETADO** — `visual_agent.py` implementado en covacha-core. Tests passing.

---

### US-MK-205: Agente de Analytics y Evaluacion (Claude)

**Descripcion:** Claude como agente analista que evalua metricas, cumplimiento de KPIs, y sugiere ajustes a la estrategia.

**Archivo:** `covacha-core/src/mipay_core/services/agents/analytics_agent.py`

**Tareas que ejecuta:**
1. Analizar metricas actuales vs. KPIs objetivo
2. Identificar posts de alto/bajo rendimiento
3. Detectar patrones (mejores horarios, tipos de contenido)
4. Generar reporte de cumplimiento de estrategia
5. Sugerir ajustes al plan de contenido

**Evaluacion periodica:**
```python
def evaluate_strategy(self, strategy_id: str) -> StrategyEvaluation:
    # 1. Obtener metricas actuales de todas las publicaciones
    metrics = self.get_current_metrics(strategy_id)

    # 2. Obtener KPIs objetivo
    kpis = self.get_strategy_kpis(strategy_id)

    # 3. Claude analiza cumplimiento
    evaluation = self.claude.analyze(
        prompt=f"""
        Analiza el cumplimiento de esta estrategia de marketing:

        OBJETIVO: {strategy.objective}
        PERIODO: {strategy.start_date} a {strategy.end_date}
        PRESUPUESTO: {strategy.budget} {strategy.currency}

        KPIs OBJETIVO vs ACTUAL:
        {format_kpis(kpis, metrics)}

        POSTS PUBLICADOS: {len(metrics.posts)}
        TOP 5 POSTS: {format_top_posts(metrics)}
        BOTTOM 5 POSTS: {format_bottom_posts(metrics)}

        Genera:
        1. Porcentaje de cumplimiento general
        2. KPIs en track / at risk / off track
        3. Patrones detectados
        4. 5 acciones correctivas concretas
        5. Ajustes sugeridos al calendario
        """
    )

    return StrategyEvaluation(
        compliance_score=evaluation["compliance"],
        kpi_status=evaluation["kpi_status"],
        patterns=evaluation["patterns"],
        recommendations=evaluation["recommendations"],
        calendar_adjustments=evaluation["adjustments"]
    )
```

**Criterios de aceptacion:**
- [x] Evalua KPIs vs metricas reales cada vez que se actualicen datos
- [x] Genera score de cumplimiento 0-100%
- [x] Clasifica KPIs en: on_track (>=80%), at_risk (50-80%), off_track (<50%)
- [x] Sugiere acciones correctivas concretas
- [x] Puede auto-ajustar el plan de contenido futuro (con aprobacion)

> **Estado: COMPLETADO** — `analytics_agent.py` implementado en covacha-core. Tests passing.

---

## FASE 2: Backend - Polling de Metricas en Tiempo Real (EP-MK-030-F2)

> **Estado: COMPLETADO (backend)** — Metrics collector scheduler implementado. 28 tests passing.

### US-MK-206: Collector de Metricas cada 2 Minutos

**Descripcion:** Servicio background que actualiza metricas de publicaciones de redes sociales cada 2 minutos para todos los clientes activos.

**Archivo:** `covacha-core/src/mipay_core/jobs/metrics_collector_job.py`

**Arquitectura:**

```
CloudWatch Events (cron: rate(2 minutes))
    |
    v
Lambda: metrics-collector-trigger
    |
    v
SQS: metrics-collection-queue
    |
    v
Worker (EC2 / Lambda):
    Para cada cliente activo:
        1. Facebook Graph API: GET /{post_id}/insights
        2. Instagram Graph API: GET /{media_id}/insights
        3. Guardar en DynamoDB
        4. Evaluar alertas
        5. Actualizar KPIs de estrategia
```

**Tabla de metricas:**
```python
# Tabla: modcore_post_metrics_history
{
    "PK": "POST#{post_id}",
    "SK": "METRIC#{timestamp}",
    "post_id": "uuid",
    "platform": "facebook|instagram",
    "platform_post_id": "fb_post_123",
    "sp_client_id": "uuid",
    "strategy_id": "uuid",

    "metrics": {
        "likes": 150,
        "comments": 23,
        "shares": 8,
        "saves": 45,
        "reach": 5200,
        "impressions": 8400,
        "engagement_rate": 4.3,
        "clicks": 120,
        "video_views": 0,
        "video_avg_watch_time": 0
    },

    "delta": {  # Cambio desde ultima medicion
        "likes": +12,
        "comments": +3,
        "reach": +400,
        "engagement_rate": +0.2
    },

    "collected_at": "2026-03-07T10:02:00Z"
}
```

**Rate limiting inteligente:**
```python
class MetricsCollector:
    """
    Recolecta metricas respetando rate limits de Meta API.
    Prioriza posts recientes (< 48h) sobre posts antiguos.
    """

    PRIORITIES = {
        "RECENT": 2,      # < 48h: cada 2 min
        "THIS_WEEK": 10,  # < 7 dias: cada 10 min
        "THIS_MONTH": 60, # < 30 dias: cada hora
        "OLDER": 1440     # > 30 dias: 1 vez al dia
    }

    def collect(self):
        clients = self.get_active_clients()

        for client in clients:
            accounts = self.get_social_accounts(client.id)

            for account in accounts:
                posts = self.get_posts_to_update(account, self.PRIORITIES)

                for post in posts:
                    metrics = self.fetch_insights(post)
                    delta = self.calculate_delta(post, metrics)
                    self.store_metrics(post, metrics, delta)

                    # Evaluar si algun KPI cambio significativamente
                    if delta.is_significant():
                        self.trigger_kpi_update(post.strategy_id, metrics)
                        self.check_alerts(post, metrics, delta)
```

**Criterios de aceptacion:**
- [x] Job ejecuta cada 2 minutos via CloudWatch/cron
- [x] Prioriza posts recientes sobre antiguos
- [x] Respeta rate limits de Meta API (200 calls/hour/user)
- [x] Calcula delta (cambio) entre mediciones
- [x] Almacena historial de metricas por post
- [x] Trigger de actualizacion de KPIs cuando cambio es significativo
- [x] No duplica datos (idempotente por timestamp)

> **Estado: COMPLETADO** — `metrics_collector_scheduler.py` + `test_metrics_collector_scheduler.py` (28 tests passing).

---

### US-MK-207: API de Metricas en Tiempo Real (WebSocket/SSE)

**Descripcion:** Endpoint que permite al frontend recibir actualizaciones de metricas en tiempo real.

**Opciones de implementacion:**

**Opcion A: Server-Sent Events (SSE) - Recomendada**
```python
@app.route("/organization/<org_id>/metrics/stream")
def metrics_stream(org_id):
    """SSE endpoint para metricas en tiempo real"""
    def generate():
        last_check = datetime.utcnow()
        while True:
            # Buscar metricas nuevas desde last_check
            new_metrics = get_metrics_since(org_id, last_check)
            if new_metrics:
                yield f"data: {json.dumps(new_metrics)}\n\n"
                last_check = datetime.utcnow()
            time.sleep(30)  # Check cada 30s

    return Response(generate(), mimetype='text/event-stream')
```

**Opcion B: Polling optimizado desde frontend**
```
GET /organization/{org_id}/metrics/latest?since={timestamp}
```
Retorna solo metricas que cambiaron desde el timestamp dado.

**Criterios de aceptacion:**
- [ ] Frontend puede suscribirse a stream de metricas
- [ ] Solo envia datos que cambiaron (no payload completo)
- [ ] Incluye delta para visualizacion de tendencia
- [ ] Agrupa por cliente y por estrategia
- [ ] Fallback a polling si SSE no disponible

---

### US-MK-208: Auto-evaluacion de Estrategia por Metricas

**Descripcion:** Cuando las metricas se actualizan, evaluar automaticamente el cumplimiento de KPIs y generar alertas/sugerencias.

**Flujo:**
```
Metrics Collector actualiza metricas
    |
    v
KPI Evaluator compara vs targets
    |
    +---> KPI on track: actualizar valor, no accion
    |
    +---> KPI at risk (50-80%): alerta amarilla
    |
    +---> KPI off track (<50%): alerta roja + trigger evaluacion IA
              |
              v
         Analytics Agent (Claude) genera:
           - Diagnostico del problema
           - 3-5 acciones correctivas
           - Ajuste sugerido al calendario
              |
              v
         Notificacion al equipo (toast + email)
```

**Criterios de aceptacion:**
- [ ] Evaluacion automatica cuando metricas cambian >5%
- [ ] Clasificacion de KPIs: on_track / at_risk / off_track
- [ ] Alerta automatica cuando KPI cae a off_track
- [ ] Evaluacion IA se ejecuta max 1 vez por hora (no spam)
- [ ] Notificacion push al equipo con resumen y acciones
- [ ] Historial de evaluaciones almacenado

---

## FASE 3: Frontend - UI de Orquestacion (EP-MK-030-F3)

> **Estado: COMPLETADO (frontend)** — Wizard, dashboard, live-metrics y strategy-evaluation implementados. Domain models, adapter y service registrados. 5424 Karma + 111 Jest tests passing.

### US-MK-209: Wizard de Definicion de Objetivo

**Descripcion:** Componente wizard donde el equipo define el objetivo de marketing que el sistema de IA ejecutara.

**Ruta:** `/marketing/ai-orchestrator/new`

**Archivo:** `mf-marketing/src/app/presentation/pages/ai-orchestrator/`

**Wizard de 4 pasos:**

```
Paso 1: Objetivo
  - Descripcion del objetivo (textarea)
  - Categoria: AWARENESS | ENGAGEMENT | TRAFFIC | LEADS | CONVERSIONS
  - Metrica principal + valor objetivo (ej: "ventas +30%")
  - Fecha limite

Paso 2: Contexto
  - Seleccionar cliente
  - Presupuesto total
  - Plataformas (FB, IG, TikTok)
  - Audiencia objetivo (descripcion)
  - Tono de marca (del Brand Kit)
  - Frecuencia de publicacion deseada

Paso 3: Configuracion de Agentes
  - Agente Research: ON/OFF, proveedor preferido
  - Agente Copy: ON/OFF, modelo preferido, idioma
  - Agente Visual: ON/OFF, estilo visual preferido
  - Agente Analytics: ON/OFF, frecuencia de evaluacion
  - Nivel de autonomia: MANUAL (aprueba cada pieza) | SEMI-AUTO (aprueba batch) | FULL-AUTO (solo monitorea)

Paso 4: Revision y Lanzamiento
  - Resumen del objetivo + configuracion
  - Preview del plan que generara Claude
  - Boton "Lanzar Orquestacion"
```

**Criterios de aceptacion:**
- [x] Wizard de 4 pasos funcional con validacion
- [x] Seleccion de cliente carga Brand Kit automaticamente
- [x] Configuracion de agentes con toggle ON/OFF
- [x] Nivel de autonomia configurable
- [x] Al lanzar, llama POST /ai/orchestrate y navega a dashboard

> **Estado: COMPLETADO** — `ai-orchestrator-wizard.component.ts` implementado con 4 pasos.

---

### US-MK-210: Dashboard de Sesion de Orquestacion

**Descripcion:** Dashboard en tiempo real que muestra el progreso de la sesion de IA: fases completadas, contenido generado, metricas.

**Ruta:** `/marketing/ai-orchestrator/:sessionId`

**Secciones:**

```
+----------------------------------------------------------+
| SESION: "Aumentar ventas 30% Q2"      Status: IN_PROGRESS|
| Cliente: Boutique Maria  |  Budget: $50,000  |  Dia 15/90|
+----------------------------------------------------------+
|                                                          |
| PIPELINE DE FASES                                        |
| [x] Research    [x] Strategy    [>] Content    [ ] Visual|
|                                                          |
| FASE ACTUAL: Generacion de Contenido (12/30 posts)       |
| ============================================ 40%          |
|                                                          |
+----------------------------------------------------------+
|                                                          |
| CONTENIDO GENERADO                    [Aprobar Todo]     |
| +--------+ +--------+ +--------+ +--------+             |
| | Post 1 | | Post 2 | | Post 3 | | Post 4 |             |
| | IG Feed| | FB Post| | IG Reel| | IG Caro|             |
| | [Img]  | | [Img]  | | [Vid]  | | [Slides|             |
| | Like   | | Edit   | | Like   | | Like   |             |
| +--------+ +--------+ +--------+ +--------+             |
|                                                          |
+----------------------------------------------------------+
|                                                          |
| METRICAS EN VIVO (actualiza cada 2 min)                  |
| Reach: 12,500 (+340)  | Engagement: 4.2% (+0.3)         |
| Clicks: 890 (+45)     | Conversions: 23 (+2)             |
|                                                          |
| KPIs                                                      |
| Ventas:      [=====>          ] 23/100 (23%) AT RISK     |
| Engagement:  [============>  ] 85/100 (85%) ON TRACK     |
| Reach:       [=========>     ] 65/100 (65%) AT RISK      |
|                                                          |
+----------------------------------------------------------+
|                                                          |
| EVALUACION IA (ultima: hace 45 min)                      |
| Score: 67/100                                            |
| "El engagement esta en track pero las conversiones van   |
|  rezagadas. Recomiendo: 1) Aumentar CTA en posts..."     |
| [Ver Evaluacion Completa] [Solicitar Re-evaluacion]      |
|                                                          |
+----------------------------------------------------------+
```

**Criterios de aceptacion:**
- [x] Pipeline visual de fases con progreso
- [x] Grid de contenido generado con preview
- [x] Acciones: aprobar, editar, rechazar cada pieza
- [x] Metricas en vivo con delta (SSE o polling 30s)
- [x] KPI bars con clasificacion on_track/at_risk/off_track
- [x] Seccion de evaluacion IA con recomendaciones
- [x] Boton para solicitar re-evaluacion manual

> **Estado: COMPLETADO** — `ai-orchestrator-dashboard.component.ts` implementado.

---

### US-MK-211: Panel de Metricas en Tiempo Real (Client Workspace)

**Descripcion:** Agregar tab de metricas en tiempo real al workspace del cliente, con auto-refresh cada 2 minutos.

**Ruta:** `/marketing/clients/:clientId` (tab "Metricas Live")

**Componente:** `mf-marketing/src/app/presentation/components/live-metrics/`

**Funcionalidades:**
1. Metricas agregadas del cliente (reach, engagement, clicks)
2. Timeline de actividad (ultimas actualizaciones)
3. Posts con mayor crecimiento en ultimas 24h
4. Comparacion con periodo anterior
5. Auto-refresh cada 2 minutos con indicador visual

**Implementacion polling:**
```typescript
// live-metrics.component.ts
private readonly REFRESH_INTERVAL = 2 * 60 * 1000; // 2 minutos

ngOnInit(): void {
    this.loadMetrics();

    // Polling cada 2 minutos
    this.refreshInterval = setInterval(() => {
        this.loadMetrics();
    }, this.REFRESH_INTERVAL);
}

private loadMetrics(): void {
    const since = this.lastUpdate()?.toISOString();
    this.httpService.get<MetricsUpdate>(
        `/organization/${orgId}/metrics/latest?since=${since}`
    ).subscribe(update => {
        this.mergeMetrics(update);
        this.lastUpdate.set(new Date());
        this.refreshCountdown.set(120); // Reset countdown
    });
}

ngOnDestroy(): void {
    clearInterval(this.refreshInterval);
}
```

**Criterios de aceptacion:**
- [x] Auto-refresh cada 2 minutos con countdown visible
- [x] Indicador "Ultima actualizacion: hace X segundos"
- [x] Delta visual (flechas verdes/rojas) en cada metrica
- [x] Posts con mayor crecimiento destacados
- [x] Comparacion vs periodo anterior
- [x] Se detiene al salir del componente (no memory leak)

> **Estado: COMPLETADO** — `live-metrics.component.ts` implementado con polling cada 2 min.

---

### US-MK-212: Re-evaluacion de Estrategia desde UI

**Descripcion:** Permitir al equipo solicitar re-evaluacion de estrategia y ver resultados historicos.

**Ruta:** `/marketing/clients/:clientId/strategies/:strategyId/dashboard` (seccion "Evaluacion IA")

**Funcionalidades:**
1. Boton "Evaluar Ahora" que trigger evaluacion IA
2. Score de cumplimiento con gauge visual (0-100)
3. Lista de KPIs con semaforo (verde/amarillo/rojo)
4. Recomendaciones de Claude con acciones concretas
5. Historial de evaluaciones (grafica temporal)
6. Opcion de "Aplicar Sugerencias" que ajusta calendario

**Criterios de aceptacion:**
- [x] Boton de evaluacion manual con loading state
- [x] Gauge de compliance score animado
- [x] Semaforo de KPIs con colores
- [x] Recomendaciones mostradas como cards accionables
- [x] Historial de evaluaciones en grafica de linea
- [x] "Aplicar Sugerencias" modifica content plan (con confirmacion)

> **Estado: COMPLETADO** — `strategy-evaluation.component.ts` implementado con gauge, semaforo y cards.

---

## FASE 4: Pipeline de Contenido Automatico (EP-MK-030-F4)

### US-MK-213: Auto-generacion de Calendario de Contenido

**Descripcion:** El coordinador genera automaticamente un calendario mensual de contenido basado en el objetivo, research, y brand kit.

**Flujo:**
```
Objetivo + Research + Brand Kit
    |
    v
Claude genera calendario:
    - 20-30 posts/mes distribuidos
    - Mix de tipos (60% feed, 20% reels, 10% stories, 10% carousel)
    - Horarios optimos (del research)
    - Temas alineados al objetivo
    - Hashtags por post
    |
    v
Calendario se crea como ContentPlanItems
    |
    v
ChatGPT genera copy para cada item
    |
    v
Gemini genera visuales para cada item
    |
    v
Posts listos para revision/aprobacion
```

**Criterios de aceptacion:**
- [ ] Genera calendario completo de 1 mes
- [ ] Distribuye posts en horarios optimos
- [ ] Mix de tipos de contenido configurable
- [ ] Cada post tiene: copy + hashtags + visual + fecha programada
- [ ] Se crean como ContentPlanItems en fase PENDING_APPROVAL
- [ ] Vista preview antes de aceptar el calendario

---

### US-MK-214: Auto-publicacion con Aprobacion

**Descripcion:** Posts aprobados se programan y publican automaticamente via Meta API.

**Flujo:**
```
Post aprobado (status: APPROVED)
    |
    v
Scheduler programa en cola:
    - Fecha/hora del calendario
    - Platform (FB/IG)
    - Media ya subida a S3
    |
    v
Al llegar la hora:
    - Publica via Meta Graph API
    - Actualiza status a PUBLISHED
    - Inicia tracking de metricas (cada 2 min)
    |
    v
Post publicado → entra al pipeline de metrics collector
```

**Criterios de aceptacion:**
- [ ] Posts aprobados se programan automaticamente
- [ ] Publicacion via Meta API en la hora exacta
- [ ] Manejo de errores (token expirado, rate limit)
- [ ] Notificacion al equipo cuando se publica
- [ ] Post entra inmediatamente al collector de metricas

---

## FASE 5: Inteligencia Continua (EP-MK-030-F5)

### US-MK-215: Aprendizaje y Optimizacion Continua

**Descripcion:** El sistema aprende de los resultados para mejorar futuras generaciones.

**Funcionalidades:**
1. Analizar que posts funcionaron mejor → alimentar contexto de generacion
2. Ajustar horarios optimos basados en datos reales (no solo research)
3. Refinar tono/estilo basado en engagement
4. Sugerir re-uso de formatos exitosos
5. Detectar fatiga de audiencia (engagement decreciente)

**Modelo de aprendizaje:**
```python
# Tabla: modcore_ai_learnings
{
    "PK": "CLIENT#{client_id}",
    "SK": "LEARNING#{timestamp}",
    "category": "CONTENT_PERFORMANCE|TIMING|AUDIENCE|FORMAT",
    "insight": "Posts con preguntas en caption tienen 2.3x mas comentarios",
    "confidence": 0.85,
    "sample_size": 45,
    "source_posts": ["post_1", "post_2", ...],
    "applied_to_sessions": ["session_1"],
    "created_at": "..."
}
```

**Criterios de aceptacion:**
- [ ] Sistema identifica patrones despues de 30+ posts
- [ ] Insights almacenados y usados en futuras generaciones
- [ ] Dashboard de insights acumulados por cliente
- [ ] Confidence score para cada insight
- [ ] Insights se inyectan como contexto al agente de copy

---

## Resumen de User Stories

| ID | Titulo | Fase | Prioridad | Estado |
|----|--------|------|-----------|--------|
| US-MK-201 | Servicio de Orquestacion Multi-Agente | F1 | CRITICA | COMPLETADO |
| US-MK-202 | Agente de Investigacion (Perplexity) | F1 | ALTA | COMPLETADO |
| US-MK-203 | Agente de Copywriting (ChatGPT) | F1 | ALTA | COMPLETADO |
| US-MK-204 | Agente Visual (Gemini + Imagen) | F1 | ALTA | COMPLETADO |
| US-MK-205 | Agente Analytics y Evaluacion (Claude) | F1 | ALTA | COMPLETADO |
| US-MK-206 | Collector de Metricas cada 2 min | F2 | CRITICA | COMPLETADO |
| US-MK-207 | API de Metricas Tiempo Real (SSE) | F2 | ALTA | PENDIENTE |
| US-MK-208 | Auto-evaluacion por Metricas | F2 | ALTA | PENDIENTE |
| US-MK-209 | Wizard de Definicion de Objetivo | F3 | CRITICA | COMPLETADO |
| US-MK-210 | Dashboard de Sesion de Orquestacion | F3 | CRITICA | COMPLETADO |
| US-MK-211 | Panel Metricas en Tiempo Real | F3 | ALTA | COMPLETADO |
| US-MK-212 | Re-evaluacion de Estrategia UI | F3 | MEDIA | COMPLETADO |
| US-MK-213 | Auto-generacion Calendario | F4 | ALTA | PENDIENTE |
| US-MK-214 | Auto-publicacion con Aprobacion | F4 | ALTA | PENDIENTE |
| US-MK-215 | Aprendizaje y Optimizacion Continua | F5 | MEDIA | PENDIENTE |

---

## Dependencias Tecnicas

### APIs externas requeridas:
- **Anthropic API** (Claude) - Coordinador + Analytics
- **OpenAI API** (GPT-4o) - Copywriting (ya integrado)
- **Google AI API** (Gemini) - Visual analysis (ya integrado)
- **Perplexity API** (sonar-pro) - Research (NUEVO)
- **DALL-E 3 API** o **Google Imagen** - Generacion de imagenes (NUEVO)
- **Meta Graph API** - Publicacion + Insights (ya integrado)

### Infraestructura nueva:
- **CloudWatch Events** - Cron cada 2 min para metrics collector
- **SQS Queue** - Cola de tareas de recoleccion
- **Lambda o Worker** - Procesamiento de metricas
- **DynamoDB** - Tablas nuevas: ai_orchestration_sessions, post_metrics_history, ai_learnings

### Codigo existente que se extiende:
- `AIContentService` (frontend) → agregar orquestacion multi-agente
- `ai_content_controller.py` (backend) → agregar endpoints de orquestacion
- `social_sync_controller.py` (backend) → agregar polling programado
- `strategy_controller.py` (backend) → agregar auto-evaluacion
- `DashboardDataService` (frontend) → agregar metricas en tiempo real
- `StrategyDashboardAdapter` (frontend) → agregar evaluacion IA

---

## Orden de Implementacion Sugerido

```
Semana 1-2: US-MK-201 (Orquestador) + US-MK-206 (Metrics Collector)
Semana 3:   US-MK-202 (Perplexity) + US-MK-203 (ChatGPT batch)
Semana 4:   US-MK-204 (Visual Agent) + US-MK-205 (Analytics Agent)
Semana 5:   US-MK-209 (Wizard UI) + US-MK-207 (SSE/Polling)
Semana 6:   US-MK-210 (Dashboard Sesion) + US-MK-211 (Live Metrics)
Semana 7:   US-MK-213 (Auto Calendar) + US-MK-214 (Auto Publish)
Semana 8:   US-MK-208 (Auto Eval) + US-MK-212 (Eval UI) + US-MK-215 (Learning)
```
