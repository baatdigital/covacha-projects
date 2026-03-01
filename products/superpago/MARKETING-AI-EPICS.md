# Marketing AI Multi-Agent (EP-MK-031 a EP-MK-034)

**Fecha**: 2026-03-01
**Product Owner**: SuperPago - Marketing
**Estado**: PLANIFICADO
**Continua desde**: EP-MK-030 (Tests y Cobertura Completa Promociones)
**User Stories**: US-MK-131 en adelante
**Repos**: covacha-botia (backend), mf-marketing (frontend), covacha-libs (modelos)

---

## Tabla de Contenidos

1. [Contexto y Motivacion](#contexto-y-motivacion)
2. [Arquitectura Multi-Agent](#arquitectura-multi-agent)
3. [Mapa de Epicas Nuevas](#mapa-de-epicas-nuevas)
4. [Epicas Detalladas](#epicas-detalladas)
5. [User Stories Detalladas](#user-stories-detalladas)
6. [Roadmap](#roadmap)
7. [Grafo de Dependencias](#grafo-de-dependencias)
8. [Riesgos y Mitigaciones](#riesgos-y-mitigaciones)

---

## Contexto y Motivacion

El ecosistema SuperPago tiene un modulo de marketing (mf-marketing + covacha-botia) con 10 agentes especializados y un frontend al 95%. Sin embargo, falta la pieza clave: **orquestacion multi-LLM** para que al definir una estrategia de marketing, el sistema automaticamente:

1. **Investigue** el mercado, competencia y tendencias consultando multiples LLMs en paralelo
2. **Sintetice** los insights en un plan de contenido unificado
3. **Genere** copies, prompts de imagen, scripts de video y calendario de publicacion
4. **Presente** el plan completo en el dashboard para revision y aprobacion

| Capacidad | Problema que Resuelve |
|-----------|----------------------|
| **Multi-Agent Research** | Un solo LLM tiene sesgos y limitaciones. Consultar Claude + Gemini + Perplexity en paralelo da vision 360 del mercado |
| **Strategy-to-Plan Pipeline** | Hoy definir estrategia y crear plan de contenido son pasos manuales. La automatizacion reduce de dias a minutos |
| **Content Generation** | Generar copies, prompts de imagen y scripts de video manualmente es lento. Los agentes aceleran x10 |
| **Multi-Platform Adaptation** | Cada red social tiene formatos distintos. Los agentes adaptan contenido automaticamente por plataforma |

### Que existe hoy

| Componente | Estado | Donde |
|------------|--------|-------|
| 10 agentes marketing (content, analytics, social, email, campaigns, leads, landing, brand, SEO, WhatsApp) | Scaffolded | covacha-botia/agents/ |
| Frontend strategy-first (picker, builder, dashboard, pipeline, calendar) | 95% implementado | mf-marketing/ |
| AI Content Service (genera copies, hashtags, carruseles) | Implementado | mf-marketing/core/services/ai-content.service.ts |
| LLM Providers (Claude + OpenAI) | Implementado | covacha-botia/vendor/llm/ |
| Workflow engine (5000+ lineas, triggers, runner, actions) | Implementado | covacha-botia/workflows/ |
| Modelos marketing (strategy, content-plan, social-media) | Implementado | mf-marketing/domain/models/ + covacha-libs |

### Que falta (estas epicas)

| Componente | Gap |
|------------|-----|
| Provider Gemini | No existe en covacha-botia |
| Provider Perplexity | No existe en covacha-botia |
| Orquestador multi-agente paralelo | No existe - hoy cada agente opera individual |
| Pipeline strategy -> plan de contenido | No existe - hoy es manual |
| Generacion de prompts de imagen | No existe |
| Generacion de scripts de video | No existe |
| UI de generacion AI en strategy builder | No existe |

---

## Arquitectura Multi-Agent

### Flujo General

```
Usuario define estrategia en mf-marketing
    |
    v
POST /organization/{org}/marketing/strategies/{id}/generate-plan
    |
    v
MarketingOrchestrator (covacha-botia)
    |
    +---> [Fase 1: Research en paralelo]
    |     |
    |     +---> Claude Agent (analisis de marca, audiencia, tono)
    |     +---> Gemini Agent (tendencias visuales, ideas de contenido)
    |     +---> Perplexity Agent (investigacion mercado real-time, competencia)
    |     |
    |     v
    |     ResultAggregator (sintetiza insights de los 3 LLMs)
    |
    +---> [Fase 2: Planificacion]
    |     |
    |     +---> ContentPlanningAgent (calendario 30/60/90 dias)
    |     +---> CopyAgent (textos por plataforma y formato)
    |     +---> ImagePromptAgent (prompts DALL-E/Midjourney)
    |     +---> VideoScriptAgent (guiones, storyboards, escenas)
    |     |
    |     v
    |     PlanAssembler (ensambla plan completo)
    |
    +---> [Fase 3: Persistencia]
          |
          +---> Crear ContentPlanItems en DynamoDB
          +---> Crear assets (prompts, scripts) en S3
          +---> Notificar al frontend via SSE/WebSocket
          |
          v
    Dashboard muestra plan generado para revision
```

### Providers LLM

| Provider | Modelo | Rol en Orquestacion | Fortaleza |
|----------|--------|---------------------|-----------|
| **Anthropic (Claude)** | claude-sonnet-4-20250514 | Analisis estrategico, copywriting, tono de marca | Razonamiento profundo, nuance |
| **Google (Gemini)** | gemini-2.0-flash | Tendencias visuales, ideas multimedia, adaptacion cultural | Multimodal, velocidad |
| **Perplexity** | sonar-pro | Investigacion mercado real-time, datos competencia, trending topics | Acceso web real-time, fuentes citadas |
| **OpenAI (DALL-E)** | dall-e-3 | Generacion de imagenes desde prompts | Calidad de imagen |

### Modelo de Datos

```
MarketingResearchSession (NUEVO - covacha-libs)
  PK: RESEARCH#{session_id}
  SK: ORG#{org_id}
  strategy_id: str
  status: PENDING | RESEARCHING | PLANNING | GENERATING | COMPLETED | FAILED
  research_results: {
    claude: { insights: [], confidence: float }
    gemini: { insights: [], visual_ideas: [] }
    perplexity: { market_data: [], sources: [], trends: [] }
  }
  synthesized_plan: {
    content_calendar: []
    copies: { platform: { posts: [] } }
    image_prompts: []
    video_scripts: []
    hashtag_strategy: {}
    posting_schedule: {}
  }
  created_at, updated_at, completed_at
  total_tokens_used: int
  estimated_cost: Decimal
```

---

## Mapa de Epicas Nuevas

| Epica | Titulo | Scope | Stories | Estado |
|-------|--------|-------|---------|--------|
| **EP-MK-031** | Multi-Provider LLM Engine | Backend - Agregar Gemini + Perplexity + orquestador paralelo | US-MK-131 a US-MK-136 | PLANIFICADO |
| **EP-MK-032** | Marketing Strategy AI Generator | Backend - Pipeline strategy->plan con agentes especializados | US-MK-137 a US-MK-143 | PLANIFICADO |
| **EP-MK-033** | Marketing AI Frontend Integration | Frontend - UI de generacion, progreso, revision y edicion | US-MK-144 a US-MK-149 | PLANIFICADO |
| **EP-MK-034** | Content Asset Generation Pipeline | Backend+Frontend - Imagenes, video, adaptacion multi-plataforma | US-MK-150 a US-MK-155 | PLANIFICADO |

---

## Epicas Detalladas

### EP-MK-031: Multi-Provider LLM Engine

> **Estado: PLANIFICADO**

**Objetivo**: Extender covacha-botia para soportar Gemini y Perplexity como providers LLM, y crear un orquestador que ejecute queries en paralelo a multiples LLMs, agregue resultados y sintetice insights.

**Repo principal**: `baatdigital/covacha-botia`
**Repos afectados**: `covacha-libs` (modelos), `covacha-botia` (providers, orquestador)

#### Criterios de Aceptacion

- [ ] Provider Gemini funcional con streaming y tool calling
- [ ] Provider Perplexity funcional con fuentes citadas
- [ ] ProviderFactory soporta 4 providers: anthropic, openai, gemini, perplexity
- [ ] Orquestador ejecuta queries en paralelo (asyncio.gather)
- [ ] Resultados se agregan con scoring de confianza
- [ ] Timeout y fallback si un provider falla
- [ ] Tests con coverage >= 98%
- [ ] Credenciales encriptadas para Gemini y Perplexity (CovClientCredentials)

#### User Stories

| Story | Titulo | Puntos |
|-------|--------|--------|
| US-MK-131 | Implementar Gemini LLM Provider | 5 |
| US-MK-132 | Implementar Perplexity LLM Provider | 5 |
| US-MK-133 | Extender CovClientCredentials para Gemini y Perplexity | 3 |
| US-MK-134 | Crear MultiLLMOrchestrator (ejecucion paralela) | 8 |
| US-MK-135 | Crear ResultAggregator (sintesis de respuestas multi-LLM) | 5 |
| US-MK-136 | Tests unitarios e integracion del engine multi-provider | 5 |

---

### EP-MK-032: Marketing Strategy AI Generator

> **Estado: PLANIFICADO**

**Objetivo**: Cuando un usuario define una estrategia de marketing, el sistema dispara automaticamente un pipeline de agentes que investiga el mercado, genera un plan de contenido completo (calendario, copies, prompts de imagen, scripts de video) y lo persiste para revision.

**Repo principal**: `baatdigital/covacha-botia`
**Repos afectados**: `covacha-libs` (modelos), `covacha-botia` (controllers, services)

#### Criterios de Aceptacion

- [ ] Endpoint `POST /strategies/{id}/generate-plan` dispara el pipeline
- [ ] Fase Research: 3 LLMs en paralelo (Claude=estrategia, Gemini=visual, Perplexity=mercado)
- [ ] Fase Planning: genera calendario 30/60/90 dias segun periodo de estrategia
- [ ] Fase Content: copies por plataforma (IG, FB, TikTok, LinkedIn, Twitter)
- [ ] Genera prompts de imagen (DALL-E compatible)
- [ ] Genera scripts de video (escenas, duracion, texto overlay)
- [ ] Genera estrategia de hashtags por plataforma
- [ ] Plan se persiste como ContentPlanItems en DynamoDB
- [ ] Progreso en tiempo real via SSE al frontend
- [ ] Tests con coverage >= 98%

#### User Stories

| Story | Titulo | Puntos |
|-------|--------|--------|
| US-MK-137 | Crear modelo MarketingResearchSession en covacha-libs | 3 |
| US-MK-138 | Implementar MarketingResearchAgent (Fase Research) | 8 |
| US-MK-139 | Implementar ContentPlanGeneratorAgent (Fase Planning) | 8 |
| US-MK-140 | Implementar CopyGeneratorAgent (copies multi-plataforma) | 5 |
| US-MK-141 | Implementar ImagePromptGeneratorAgent (prompts DALL-E/Midjourney) | 5 |
| US-MK-142 | Implementar VideoScriptGeneratorAgent (guiones y storyboards) | 5 |
| US-MK-143 | Crear endpoint generate-plan y MarketingPipelineService | 8 |

---

### EP-MK-033: Marketing AI Frontend Integration

> **Estado: PLANIFICADO**

**Objetivo**: Integrar la generacion AI en el frontend de marketing. El usuario define una estrategia, hace clic en "Generar Plan con IA", ve progreso en tiempo real, revisa el plan generado y puede editar/aprobar items individuales.

**Repo principal**: `baatdigital/mf-marketing`
**Repos afectados**: `mf-marketing` (components, services, adapters)

#### Criterios de Aceptacion

- [ ] Boton "Generar Plan con IA" en strategy-builder y strategy-detail
- [ ] Modal de configuracion: periodo, plataformas, tono, frecuencia
- [ ] Pantalla de progreso con fases (Research -> Planning -> Generating)
- [ ] Indicador por agente (Claude investigando... Gemini analizando... Perplexity buscando...)
- [ ] Preview del plan generado antes de confirmar
- [ ] Edicion individual de items generados (copy, imagen, video)
- [ ] Bulk approve/reject de items
- [ ] Plan generado se integra en Pipeline existente (Kanban)
- [ ] Tests con cobertura adecuada

#### User Stories

| Story | Titulo | Puntos |
|-------|--------|--------|
| US-MK-144 | Crear AI Plan Generation Service (adapter + service) | 5 |
| US-MK-145 | Crear componente GeneratePlanModal (config + trigger) | 5 |
| US-MK-146 | Crear componente GenerationProgressPanel (SSE real-time) | 5 |
| US-MK-147 | Crear componente GeneratedPlanReview (preview + edicion) | 8 |
| US-MK-148 | Integrar plan generado en Pipeline existente (Kanban) | 5 |
| US-MK-149 | Bulk actions: aprobar, rechazar, regenerar items | 3 |

---

### EP-MK-034: Content Asset Generation Pipeline

> **Estado: PLANIFICADO**

**Objetivo**: Pipeline completo de generacion de assets: imagenes via DALL-E/Stable Diffusion, scripts de video con storyboard, adaptacion automatica de contenido por plataforma (aspect ratios, limites de texto, formatos). Incluye integracion con media library y preview.

**Repo principal**: `baatdigital/covacha-botia` + `baatdigital/mf-marketing`
**Repos afectados**: `covacha-libs` (modelos), `covacha-botia` (services), `mf-marketing` (UI)

#### Criterios de Aceptacion

- [ ] Generacion de imagenes via DALL-E 3 desde prompts del plan
- [ ] Preview de imagen generada antes de confirmar
- [ ] Variaciones de imagen (regenerar con ajustes)
- [ ] Scripts de video con timeline: escenas, duracion, texto overlay, transiciones
- [ ] Adaptacion automatica por plataforma (IG Feed 1:1, IG Story 9:16, FB 16:9, TikTok 9:16)
- [ ] Assets generados se guardan en S3 y se vinculan al ContentPlanItem
- [ ] Galeria de assets generados en media library
- [ ] Estimacion de costo antes de generar (tokens + API calls)
- [ ] Tests con coverage >= 98%

#### User Stories

| Story | Titulo | Puntos |
|-------|--------|--------|
| US-MK-150 | Implementar ImageGenerationService (DALL-E 3 integration) | 8 |
| US-MK-151 | Implementar VideoScriptService (timeline + storyboard) | 5 |
| US-MK-152 | Implementar PlatformAdapterService (formatos por red social) | 5 |
| US-MK-153 | Frontend: componente ImageGenerationPanel (prompt, preview, variaciones) | 5 |
| US-MK-154 | Frontend: componente VideoStoryboardEditor (timeline visual) | 8 |
| US-MK-155 | Integracion con Media Library y estimacion de costos | 3 |

---

## User Stories Detalladas

### US-MK-131: Implementar Gemini LLM Provider

**Como** desarrollador del sistema de IA,
**Quiero** un provider de Gemini integrado en la factory de LLM,
**Para que** los agentes puedan consultar Gemini 2.0 Flash para analisis de tendencias visuales y contenido multimedia.

#### Criterios de Aceptacion

- [ ] Clase `GeminiProvider` en `vendor/llm/gemini_provider.py`
- [ ] Soporte para `generate()` (texto), `generate_stream()` (streaming), `generate_with_tools()` (function calling)
- [ ] Configuracion via `GOOGLE_API_KEY` o credenciales del cliente
- [ ] Manejo de rate limits y retry con backoff exponencial
- [ ] Mapeo de roles (user/assistant/system) al formato Gemini
- [ ] Soporte multimodal (texto + imagen como input)
- [ ] `ProviderFactory.get_provider("gemini")` retorna instancia correcta
- [ ] Tests: happy path, error handling, rate limit, timeout

#### Tareas Tecnicas

- [ ] Crear `src/covacha_botia/vendor/llm/gemini_provider.py`
- [ ] Agregar `google-generativeai>=0.8.0` a requirements.txt
- [ ] Registrar en `provider_factory.py`
- [ ] Agregar `GOOGLE_API_KEY` a settings.py
- [ ] Tests en `tests/unit/test_gemini_provider.py`

#### Estimacion: 5 puntos | Complejidad: Media

---

### US-MK-132: Implementar Perplexity LLM Provider

**Como** desarrollador del sistema de IA,
**Quiero** un provider de Perplexity integrado en la factory de LLM,
**Para que** los agentes puedan hacer investigacion de mercado en tiempo real con fuentes citadas.

#### Criterios de Aceptacion

- [ ] Clase `PerplexityProvider` en `vendor/llm/perplexity_provider.py`
- [ ] Usa API compatible con OpenAI SDK (base_url=https://api.perplexity.ai)
- [ ] Soporte para modelos: `sonar-pro`, `sonar`, `sonar-reasoning-pro`
- [ ] Extraccion de `citations[]` de las respuestas
- [ ] Configuracion via `PERPLEXITY_API_KEY` o credenciales del cliente
- [ ] `ProviderFactory.get_provider("perplexity")` retorna instancia correcta
- [ ] Tests: happy path, citations parsing, error handling

#### Tareas Tecnicas

- [ ] Crear `src/covacha_botia/vendor/llm/perplexity_provider.py`
- [ ] Registrar en `provider_factory.py`
- [ ] Agregar `PERPLEXITY_API_KEY` a settings.py
- [ ] Tests en `tests/unit/test_perplexity_provider.py`

#### Estimacion: 5 puntos | Complejidad: Media

---

### US-MK-133: Extender CovClientCredentials para Gemini y Perplexity

**Como** administrador de clientes IA,
**Quiero** poder almacenar API keys de Gemini y Perplexity por cliente,
**Para que** cada cliente pueda usar sus propias credenciales multi-provider.

#### Criterios de Aceptacion

- [ ] Campos `google_api_key` y `perplexity_api_key` en CovClientCredentials (covacha-libs)
- [ ] Encriptacion AES igual que openai/anthropic keys
- [ ] `has_own_credentials("gemini")` y `has_own_credentials("perplexity")` funcionan
- [ ] `get_api_key("gemini")` y `get_api_key("perplexity")` retornan key desencriptada
- [ ] Endpoint de credenciales muestra keys maskeadas (ultimos 4 chars)
- [ ] Endpoint `transfer-system` transfiere keys de Gemini y Perplexity
- [ ] Frontend credentials form tiene campos para Google y Perplexity
- [ ] Tests de encriptacion/desencriptacion para nuevos providers

#### Tareas Tecnicas

- [ ] Modificar `CovClientCredentials` en covacha-libs
- [ ] Actualizar `credentials_controller.py` en covacha-botia
- [ ] Actualizar UI de credenciales en mf-ia
- [ ] Tests en covacha-libs y covacha-botia

#### Estimacion: 3 puntos | Complejidad: Baja

---

### US-MK-134: Crear MultiLLMOrchestrator (ejecucion paralela)

**Como** sistema de IA,
**Quiero** un orquestador que ejecute queries a multiples LLMs en paralelo,
**Para que** pueda obtener respuestas de Claude, Gemini y Perplexity simultaneamente y combinarlas.

#### Criterios de Aceptacion

- [ ] Clase `MultiLLMOrchestrator` en `vendor/llm/multi_llm_orchestrator.py`
- [ ] Metodo `research_parallel(prompts: Dict[str, str]) -> Dict[str, LLMResponse]`
- [ ] Ejecuta queries en paralelo con `asyncio.gather()`
- [ ] Timeout configurable por provider (default 30s)
- [ ] Si un provider falla, los demas continuan (partial results)
- [ ] Retry automatico (1 retry con backoff) antes de marcar como fallido
- [ ] Tracking de tokens por provider para billing
- [ ] Log detallado de tiempos de respuesta por provider
- [ ] Tests: parallelism real, timeout, partial failure, full failure

#### Tareas Tecnicas

- [ ] Crear `src/covacha_botia/vendor/llm/multi_llm_orchestrator.py`
- [ ] Integrar con ProviderFactory para instanciar providers
- [ ] Agregar metricas de tiempo y tokens
- [ ] Tests en `tests/unit/test_multi_llm_orchestrator.py`

#### Estimacion: 8 puntos | Complejidad: Alta

---

### US-MK-135: Crear ResultAggregator (sintesis de respuestas multi-LLM)

**Como** sistema de IA,
**Quiero** un agregador que sintetice respuestas de multiples LLMs en un resultado unificado,
**Para que** el pipeline de marketing tenga insights consolidados sin redundancia.

#### Criterios de Aceptacion

- [ ] Clase `ResultAggregator` en `vendor/llm/result_aggregator.py`
- [ ] Metodo `synthesize(results: Dict[str, LLMResponse]) -> SynthesizedInsights`
- [ ] Elimina duplicados entre respuestas de diferentes LLMs
- [ ] Asigna scoring de confianza basado en consenso (si 2+ LLMs coinciden = alta confianza)
- [ ] Preserva fuentes citadas de Perplexity
- [ ] Estructura de salida: `{ themes: [], trends: [], audience_insights: [], content_ideas: [], competitor_analysis: [], sources: [] }`
- [ ] Usa un LLM (Claude) como "meta-sintetizador" para unificar
- [ ] Tests: dedup, scoring, merge logic

#### Tareas Tecnicas

- [ ] Crear `src/covacha_botia/vendor/llm/result_aggregator.py`
- [ ] Definir `SynthesizedInsights` en covacha-libs
- [ ] Tests en `tests/unit/test_result_aggregator.py`

#### Estimacion: 5 puntos | Complejidad: Media

---

### US-MK-136: Tests unitarios e integracion del engine multi-provider

**Como** desarrollador,
**Quiero** tests completos del engine multi-provider,
**Para que** tenga confianza en que el sistema funciona correctamente con 4 providers.

#### Criterios de Aceptacion

- [ ] Tests unitarios para GeminiProvider (mock de google API)
- [ ] Tests unitarios para PerplexityProvider (mock de API)
- [ ] Tests unitarios para MultiLLMOrchestrator (mock de providers)
- [ ] Tests unitarios para ResultAggregator
- [ ] Tests de integracion: pipeline completo con mocks
- [ ] Coverage >= 98% en todos los archivos nuevos
- [ ] Tests de error: timeout, rate limit, invalid key, partial failure

#### Estimacion: 5 puntos | Complejidad: Media

---

### US-MK-137: Crear modelo MarketingResearchSession en covacha-libs

**Como** desarrollador,
**Quiero** un modelo Pydantic para persistir sesiones de investigacion de marketing,
**Para que** pueda trackear el progreso y resultados de cada generacion de plan.

#### Criterios de Aceptacion

- [ ] Modelo `MarketingResearchSession` en `covacha_libs/models/modmarketing/`
- [ ] Campos: session_id, org_id, strategy_id, status, research_results, synthesized_plan, tokens_used, cost
- [ ] Status enum: PENDING, RESEARCHING, PLANNING, GENERATING, COMPLETED, FAILED
- [ ] Metodos: `from_dynamodb()`, `to_dynamodb()`, `to_response()`
- [ ] Tabla DynamoDB: `modIA_marketing_research_sessions_prod`
- [ ] Repository: `MarketingResearchSessionRepository`
- [ ] Tests para modelo y repository

#### Estimacion: 3 puntos | Complejidad: Baja

---

### US-MK-138: Implementar MarketingResearchAgent (Fase Research)

**Como** sistema de marketing IA,
**Quiero** un agente que coordine la investigacion multi-LLM para una estrategia,
**Para que** obtenga insights de mercado, competencia y tendencias automaticamente.

#### Criterios de Aceptacion

- [ ] Clase `MarketingResearchAgent` en `vendor/agents/marketing/`
- [ ] Recibe: estrategia (nombre, industria, audiencia, objetivos, plataformas)
- [ ] Genera prompts especializados por provider:
  - Claude: "Analiza la marca X en la industria Y. Audiencia: Z. Sugiere tono, pilares de contenido, diferenciadores..."
  - Gemini: "Identifica tendencias visuales actuales para la industria Y en redes sociales. Formatos que funcionan, estetica, colores..."
  - Perplexity: "Investiga competidores de X en Y. Que publican, frecuencia, engagement, hashtags populares, trending topics..."
- [ ] Usa MultiLLMOrchestrator para ejecucion paralela
- [ ] Usa ResultAggregator para sintetizar
- [ ] Persiste resultados en MarketingResearchSession
- [ ] Emite eventos SSE de progreso: `research_started`, `provider_completed`, `research_done`
- [ ] Tests con mocks de providers

#### Estimacion: 8 puntos | Complejidad: Alta

---

### US-MK-139: Implementar ContentPlanGeneratorAgent (Fase Planning)

**Como** sistema de marketing IA,
**Quiero** un agente que genere un calendario de contenido basado en los insights de research,
**Para que** el plan tenga publicaciones distribuidas estrategicamente en el tiempo.

#### Criterios de Aceptacion

- [ ] Clase `ContentPlanGeneratorAgent` en `vendor/agents/marketing/`
- [ ] Recibe: insights sintetizados + config de estrategia (periodo, plataformas, frecuencia)
- [ ] Genera calendario con:
  - Distribucion por dia de la semana (optima por plataforma)
  - Mix de formatos: 40% posts, 25% carruseles, 20% reels/video, 15% stories
  - Pilares de contenido balanceados
  - Fechas especiales y trending topics integrados
  - Horarios optimos por plataforma
- [ ] Output: lista de ContentPlanItems con fecha, plataforma, formato, tema, hashtags sugeridos
- [ ] Soporta periodos: semanal, quincenal, mensual, trimestral
- [ ] Tests con diferentes configuraciones de estrategia

#### Estimacion: 8 puntos | Complejidad: Alta

---

### US-MK-140: Implementar CopyGeneratorAgent (copies multi-plataforma)

**Como** sistema de marketing IA,
**Quiero** un agente que genere copies adaptados por plataforma para cada item del plan,
**Para que** cada publicacion tenga texto optimizado para su red social.

#### Criterios de Aceptacion

- [ ] Clase `CopyGeneratorAgent` en `vendor/agents/marketing/`
- [ ] Genera copy adaptado por plataforma:
  - Instagram: visual, emojis, 2200 chars max, 30 hashtags
  - Facebook: conversacional, links, sin limite estricto
  - TikTok: casual, trending, hashtags virales, corto
  - LinkedIn: profesional, insights, CTAs corporativos
  - Twitter/X: conciso, 280 chars, threads si necesario
- [ ] Respeta tono de marca definido en estrategia
- [ ] Incluye CTA relevante por objetivo (awareness, engagement, conversion)
- [ ] Genera 2-3 variantes por item para A/B testing
- [ ] Tests por plataforma y formato

#### Estimacion: 5 puntos | Complejidad: Media

---

### US-MK-141: Implementar ImagePromptGeneratorAgent

**Como** sistema de marketing IA,
**Quiero** un agente que genere prompts de imagen optimizados para DALL-E y Midjourney,
**Para que** cada publicacion tenga un prompt listo para generar su visual.

#### Criterios de Aceptacion

- [ ] Clase `ImagePromptGeneratorAgent` en `vendor/agents/marketing/`
- [ ] Genera prompts DALL-E 3 compatibles con:
  - Estilo visual de la marca (colores, estetica)
  - Formato correcto por plataforma (1:1, 9:16, 16:9)
  - Texto overlay sugerido
  - Negative prompts para evitar elementos no deseados
- [ ] Genera prompt alternativo Midjourney (--ar, --style, --v)
- [ ] Categorias de visual: producto, lifestyle, infografia, quote, behind-the-scenes
- [ ] Output incluye: prompt, negative_prompt, aspect_ratio, style_reference
- [ ] Tests con diferentes tipos de contenido

#### Estimacion: 5 puntos | Complejidad: Media

---

### US-MK-142: Implementar VideoScriptGeneratorAgent

**Como** sistema de marketing IA,
**Quiero** un agente que genere scripts de video con estructura de escenas,
**Para que** cada reel/video tenga un guion listo para produccion.

#### Criterios de Aceptacion

- [ ] Clase `VideoScriptGeneratorAgent` en `vendor/agents/marketing/`
- [ ] Genera scripts con estructura:
  - Hook (0-3s): gancho inicial
  - Desarrollo (3-45s): contenido principal
  - CTA (45-60s): llamada a accion
- [ ] Cada escena incluye: duracion, texto en pantalla, audio/voz, transicion, visual
- [ ] Formatos soportados:
  - Reel (15s, 30s, 60s, 90s)
  - TikTok (15s, 60s, 3min)
  - YouTube Short (60s)
  - Story (15s)
- [ ] Sugiere musica/audio trending por plataforma
- [ ] Output: JSON con timeline de escenas
- [ ] Tests por formato y duracion

#### Estimacion: 5 puntos | Complejidad: Media

---

### US-MK-143: Crear endpoint generate-plan y MarketingPipelineService

**Como** usuario de marketing,
**Quiero** un endpoint que dispare toda la pipeline de generacion,
**Para que** con un solo click genere el plan completo de contenido.

#### Criterios de Aceptacion

- [ ] Endpoint `POST /organization/{org}/marketing/strategies/{id}/generate-plan`
- [ ] Body: `{ period: "monthly", platforms: ["instagram", "facebook", "tiktok"], tone: "professional", frequency: { instagram: 5, facebook: 3, tiktok: 4 } }`
- [ ] `MarketingPipelineService` coordina las 3 fases secuencialmente
- [ ] Fase 1 (Research) ejecuta en paralelo los 3 LLMs
- [ ] Fase 2 (Planning) genera calendario + copies + prompts + scripts
- [ ] Fase 3 (Persist) crea ContentPlanItems en DynamoDB
- [ ] SSE endpoint para progreso: `GET /strategies/{id}/generation-progress`
- [ ] Eventos SSE: `{ phase: "research", step: "claude_completed", progress: 33 }`
- [ ] Manejo de errores: si una fase falla, reporta y no pierde lo generado
- [ ] Blueprint `marketing_generation_routes.py` registrado en app.py
- [ ] Tests del pipeline completo con mocks

#### Estimacion: 8 puntos | Complejidad: Alta

---

### US-MK-144: Crear AI Plan Generation Service (adapter + service)

**Como** desarrollador frontend,
**Quiero** un service y adapter para comunicarme con el backend de generacion,
**Para que** los componentes puedan disparar y monitorear la generacion de planes.

#### Criterios de Aceptacion

- [ ] `AIPlanGenerationAdapter` en `infrastructure/adapters/`
- [ ] `AIPlanGenerationService` en `core/services/`
- [ ] Metodos: `generatePlan(strategyId, config)`, `getProgress(strategyId)`, `cancelGeneration(strategyId)`
- [ ] Conexion SSE para progreso en tiempo real
- [ ] Signal `generationProgress$` con estado actual
- [ ] Signal `generationResult$` con plan generado
- [ ] Error handling: timeout, cancelacion, fallo parcial
- [ ] Tests unitarios del service

#### Estimacion: 5 puntos | Complejidad: Media

---

### US-MK-145: Crear componente GeneratePlanModal

**Como** usuario de marketing,
**Quiero** un modal donde configure los parametros de generacion del plan,
**Para que** pueda personalizar que tipo de contenido quiero antes de generar.

#### Criterios de Aceptacion

- [ ] Componente standalone `GeneratePlanModalComponent`
- [ ] Formulario con:
  - Periodo: Semanal, Quincenal, Mensual, Trimestral
  - Plataformas: checkboxes (IG, FB, TikTok, LinkedIn, Twitter)
  - Frecuencia por plataforma: input numerico (posts/semana)
  - Tono: selector (profesional, casual, divertido, inspiracional)
  - Tipos de contenido: checkboxes (posts, carruseles, reels, stories, videos)
  - Generar imagenes: toggle (on/off + estimacion de costo)
  - Generar scripts video: toggle (on/off)
- [ ] Estimacion de costo antes de confirmar (tokens estimados)
- [ ] Boton "Generar Plan" dispara el pipeline
- [ ] Accesible desde strategy-builder y strategy-detail
- [ ] Responsive (mobile-friendly)
- [ ] Tests del componente

#### Estimacion: 5 puntos | Complejidad: Media

---

### US-MK-146: Crear componente GenerationProgressPanel

**Como** usuario de marketing,
**Quiero** ver el progreso de la generacion en tiempo real,
**Para que** sepa en que fase esta y cuanto falta.

#### Criterios de Aceptacion

- [ ] Componente standalone `GenerationProgressPanelComponent`
- [ ] Muestra 3 fases con estado: Research -> Planning -> Generating
- [ ] En fase Research, muestra status por provider:
  - "Claude: Analizando marca y audiencia..." (spinner)
  - "Gemini: Identificando tendencias visuales..." (check verde)
  - "Perplexity: Investigando competencia..." (spinner)
- [ ] Barra de progreso general (0-100%)
- [ ] Tiempo transcurrido y estimado
- [ ] Boton cancelar (con confirmacion)
- [ ] Animaciones suaves entre estados
- [ ] Si falla un provider, muestra warning pero continua
- [ ] Al completar, transiciona a pantalla de review
- [ ] Tests del componente

#### Estimacion: 5 puntos | Complejidad: Media

---

### US-MK-147: Crear componente GeneratedPlanReview

**Como** usuario de marketing,
**Quiero** revisar el plan generado antes de confirmarlo,
**Para que** pueda editar, ajustar o rechazar items individuales.

#### Criterios de Aceptacion

- [ ] Componente standalone `GeneratedPlanReviewComponent`
- [ ] Vista de calendario con items generados posicionados
- [ ] Vista de lista con filtros (por plataforma, formato, fecha)
- [ ] Cada item muestra: fecha, plataforma, formato, copy preview, imagen prompt, hashtags
- [ ] Click en item abre detalle editable:
  - Editar copy (con vista por plataforma)
  - Editar prompt de imagen
  - Ver/editar script de video
  - Cambiar fecha, plataforma, formato
  - Aprobar o rechazar item individual
- [ ] Resumen estadistico: X posts IG, Y reels TikTok, Z articles LinkedIn
- [ ] Boton "Aprobar Todo" (mueve a fase COPYWRITING en pipeline)
- [ ] Boton "Regenerar" (vuelve a ejecutar con ajustes)
- [ ] Boton "Descartar" (elimina plan generado)
- [ ] Tests del componente

#### Estimacion: 8 puntos | Complejidad: Alta

---

### US-MK-148: Integrar plan generado en Pipeline existente

**Como** usuario de marketing,
**Quiero** que los items aprobados se integren en el Pipeline Kanban existente,
**Para que** sigan el flujo normal de IDEATION -> COPYWRITING -> DESIGN -> REVIEW -> APPROVAL -> SCHEDULING -> PUBLISHED.

#### Criterios de Aceptacion

- [ ] Items aprobados se crean como ContentPlanItems con status=COPYWRITING
- [ ] Aparecen en la columna COPYWRITING del Kanban
- [ ] Cada item tiene tag "AI Generated" para distinguirlo de items manuales
- [ ] Prompt de imagen se vincula al item como metadata
- [ ] Script de video se vincula al item como metadata
- [ ] Si el usuario quiere, puede mover directo a DESIGN (skip copywriting)
- [ ] Items rechazados se marcan como DISCARDED y no aparecen en Pipeline
- [ ] Tests de integracion

#### Estimacion: 5 puntos | Complejidad: Media

---

### US-MK-149: Bulk actions: aprobar, rechazar, regenerar items

**Como** usuario de marketing,
**Quiero** poder aprobar, rechazar o regenerar multiples items a la vez,
**Para que** no tenga que hacerlo uno por uno cuando hay 30+ items.

#### Criterios de Aceptacion

- [ ] Checkbox de seleccion en cada item del plan generado
- [ ] "Seleccionar todos" / "Deseleccionar todos"
- [ ] Acciones bulk: Aprobar seleccionados, Rechazar seleccionados, Regenerar seleccionados
- [ ] Regenerar re-ejecuta solo los items seleccionados (no todo el plan)
- [ ] Confirmacion antes de acciones destructivas (rechazar)
- [ ] Feedback visual: items aprobados se mueven al pipeline con animacion
- [ ] Tests del componente

#### Estimacion: 3 puntos | Complejidad: Baja

---

### US-MK-150: Implementar ImageGenerationService (DALL-E 3)

**Como** sistema de marketing IA,
**Quiero** un servicio que genere imagenes reales via DALL-E 3,
**Para que** los prompts del plan se conviertan en imagenes listas para publicar.

#### Criterios de Aceptacion

- [ ] Clase `ImageGenerationService` en `vendor/tools/image_generation.py`
- [ ] Metodo `generate_image(prompt, size, style, quality) -> ImageResult`
- [ ] Sizes soportados: 1024x1024, 1024x1792 (9:16), 1792x1024 (16:9)
- [ ] Estilos: natural, vivid
- [ ] Quality: standard, hd
- [ ] Imagen se sube automaticamente a S3
- [ ] Retorna URL de S3 + metadata (prompt, size, cost)
- [ ] Rate limiting para no exceder limites de OpenAI
- [ ] Metodo `generate_variations(image_url, n=3)` para alternativas
- [ ] Estimacion de costo antes de generar ($0.04 standard, $0.08 HD)
- [ ] Tests con mock de OpenAI

#### Estimacion: 8 puntos | Complejidad: Alta

---

### US-MK-151: Implementar VideoScriptService (timeline + storyboard)

**Como** sistema de marketing IA,
**Quiero** un servicio que estructura scripts de video como storyboards visuales,
**Para que** el equipo de produccion tenga un documento claro para grabar.

#### Criterios de Aceptacion

- [ ] Clase `VideoScriptService` en `vendor/tools/video_script.py`
- [ ] Metodo `generate_storyboard(script_json) -> Storyboard`
- [ ] Storyboard incluye: escenas con duracion, texto, indicaciones de camara, transiciones
- [ ] Genera thumbnail sugerido (prompt de imagen para portada)
- [ ] Exportable como JSON (para frontend) y Markdown (para produccion)
- [ ] Soporta templates: tutorial, testimonial, behind-the-scenes, producto, trend
- [ ] Tests por template

#### Estimacion: 5 puntos | Complejidad: Media

---

### US-MK-152: Implementar PlatformAdapterService

**Como** sistema de marketing IA,
**Quiero** un servicio que adapte contenido automaticamente por plataforma,
**Para que** cada red social reciba el formato y texto optimizado.

#### Criterios de Aceptacion

- [ ] Clase `PlatformAdapterService` en `vendor/tools/platform_adapter.py`
- [ ] Adapta copy: trunca para Twitter (280), agrega hashtags para IG (30 max), profesionaliza para LinkedIn
- [ ] Adapta imagen: aspect ratio por plataforma (1:1, 9:16, 16:9, 4:5)
- [ ] Adapta video: duracion maxima por plataforma (Reel 90s, TikTok 3min, Story 15s)
- [ ] Sugiere mejor horario de publicacion por plataforma y timezone
- [ ] Genera preview de como se vera en cada plataforma
- [ ] Tests por plataforma

#### Estimacion: 5 puntos | Complejidad: Media

---

### US-MK-153: Frontend: ImageGenerationPanel

**Como** usuario de marketing,
**Quiero** un panel donde pueda generar y previsualizar imagenes desde prompts,
**Para que** no tenga que salir de la plataforma para crear visuales.

#### Criterios de Aceptacion

- [ ] Componente standalone `ImageGenerationPanelComponent`
- [ ] Input de prompt (editable, pre-llenado del plan)
- [ ] Selector de formato: Feed (1:1), Story (9:16), Cover (16:9), Post (4:5)
- [ ] Selector de estilo: Natural, Vivid
- [ ] Selector de calidad: Standard ($0.04), HD ($0.08)
- [ ] Boton "Generar" con spinner durante generacion (~10-15s)
- [ ] Preview de imagen generada
- [ ] Boton "Variaciones" genera 3 alternativas
- [ ] Boton "Usar" vincula imagen al ContentPlanItem
- [ ] Historial de imagenes generadas (ultimo 10)
- [ ] Tests del componente

#### Estimacion: 5 puntos | Complejidad: Media

---

### US-MK-154: Frontend: VideoStoryboardEditor

**Como** usuario de marketing,
**Quiero** un editor visual de storyboard para scripts de video,
**Para que** pueda ver y editar la timeline de cada video del plan.

#### Criterios de Aceptacion

- [ ] Componente standalone `VideoStoryboardEditorComponent`
- [ ] Timeline visual horizontal con escenas como cards
- [ ] Cada escena muestra: duracion, texto overlay, indicaciones, transicion
- [ ] Drag & drop para reordenar escenas
- [ ] Click para editar contenido de escena
- [ ] Indicador de duracion total y por escena
- [ ] Preview de texto overlay sobre placeholder visual
- [ ] Exportar como PDF o compartir link
- [ ] Templates predefinidos: tutorial, unboxing, trend, educational
- [ ] Tests del componente

#### Estimacion: 8 puntos | Complejidad: Alta

---

### US-MK-155: Integracion con Media Library y estimacion de costos

**Como** usuario de marketing,
**Quiero** que las imagenes generadas se guarden en la Media Library y ver costos acumulados,
**Para que** pueda reusar assets y controlar el presupuesto de generacion IA.

#### Criterios de Aceptacion

- [ ] Imagenes generadas se guardan automaticamente en Media Library con tags
- [ ] Tags automaticos: "ai-generated", nombre de estrategia, plataforma, fecha
- [ ] Dashboard de costos: tokens usados, imagenes generadas, costo por estrategia
- [ ] Alerta cuando costo se acerca al presupuesto de IA del cliente
- [ ] Historial de generaciones: que se genero, cuando, costo
- [ ] Busqueda en Media Library por "ai-generated" filtra solo assets IA
- [ ] Tests de integracion

#### Estimacion: 3 puntos | Complejidad: Baja

---

## Roadmap

### Sprint 1 (6 dias) - Foundation
- **US-MK-131**: Gemini Provider
- **US-MK-132**: Perplexity Provider
- **US-MK-133**: Extender credenciales
- **US-MK-136**: Tests del engine

### Sprint 2 (6 dias) - Orchestration
- **US-MK-134**: MultiLLMOrchestrator
- **US-MK-135**: ResultAggregator
- **US-MK-137**: Modelo MarketingResearchSession

### Sprint 3 (6 dias) - Research + Planning Agents
- **US-MK-138**: MarketingResearchAgent
- **US-MK-139**: ContentPlanGeneratorAgent
- **US-MK-143**: Endpoint generate-plan + PipelineService

### Sprint 4 (6 dias) - Content Generation Agents
- **US-MK-140**: CopyGeneratorAgent
- **US-MK-141**: ImagePromptGeneratorAgent
- **US-MK-142**: VideoScriptGeneratorAgent

### Sprint 5 (6 dias) - Frontend Integration
- **US-MK-144**: AI Plan Generation Service
- **US-MK-145**: GeneratePlanModal
- **US-MK-146**: GenerationProgressPanel
- **US-MK-148**: Integracion con Pipeline

### Sprint 6 (6 dias) - Review + Assets
- **US-MK-147**: GeneratedPlanReview
- **US-MK-149**: Bulk actions
- **US-MK-150**: ImageGenerationService (DALL-E)
- **US-MK-155**: Media Library + costos

### Sprint 7 (6 dias) - Video + Platform
- **US-MK-151**: VideoScriptService
- **US-MK-152**: PlatformAdapterService
- **US-MK-153**: ImageGenerationPanel
- **US-MK-154**: VideoStoryboardEditor

---

## Grafo de Dependencias

```
EP-MK-031 (Multi-Provider Engine)
  |
  +--- US-MK-131 (Gemini) ----+
  +--- US-MK-132 (Perplexity) -+---> US-MK-134 (Orchestrator) ---> US-MK-135 (Aggregator)
  +--- US-MK-133 (Credentials) +           |                              |
  +--- US-MK-136 (Tests) ------+           v                              v
                                    EP-MK-032 (Strategy AI Generator)
                                           |
                                    US-MK-137 (Model) ---+
                                           |             |
                                    US-MK-138 (Research) +---> US-MK-143 (Pipeline Endpoint)
                                    US-MK-139 (Planning) +         |
                                    US-MK-140 (Copy)     +         |
                                    US-MK-141 (Image)    +         |
                                    US-MK-142 (Video)    +         |
                                                                   v
                                                          EP-MK-033 (Frontend)
                                                                   |
                                                          US-MK-144 (Service) --+
                                                          US-MK-145 (Modal)     |
                                                          US-MK-146 (Progress)  +---> US-MK-148 (Pipeline Integration)
                                                          US-MK-147 (Review)    |
                                                          US-MK-149 (Bulk)      +
                                                                   |
                                                                   v
                                                          EP-MK-034 (Assets)
                                                                   |
                                                          US-MK-150 (DALL-E) ---+
                                                          US-MK-151 (Video)     |
                                                          US-MK-152 (Platform)  +---> US-MK-155 (Media + Costos)
                                                          US-MK-153 (Image UI)  |
                                                          US-MK-154 (Video UI)  +
```

---

## Riesgos y Mitigaciones

| Riesgo | Impacto | Probabilidad | Mitigacion |
|--------|---------|--------------|------------|
| Rate limits de Perplexity/Gemini | Generacion lenta o fallida | Media | Timeout + fallback a Claude only. Cache de resultados similares |
| Costo elevado de DALL-E por volumen | Presupuesto excedido | Alta | Estimacion previa + limite configurable por cliente + quality standard por defecto |
| Calidad inconsistente entre LLMs | Plan con contenido incoherente | Media | ResultAggregator usa Claude como meta-sintetizador. Review obligatorio antes de aprobar |
| Latencia alta (3 LLMs + generacion) | UX lenta, abandono | Media | SSE para progreso real-time. Background job con notificacion al completar |
| Prompts de imagen no producen resultados esperados | Imagenes inutiles | Media | Preview antes de confirmar. 3 variaciones. Edicion manual del prompt |
| Complejidad del VideoScriptAgent | Scripts poco utiles | Baja | Templates predefinidos como base. Edicion manual siempre disponible |

---

## Resumen de Puntos

| Epica | Stories | Puntos Totales | Sprints Estimados |
|-------|---------|---------------|-------------------|
| EP-MK-031: Multi-Provider Engine | 6 | 31 | 2 |
| EP-MK-032: Strategy AI Generator | 7 | 42 | 2 |
| EP-MK-033: Frontend Integration | 6 | 31 | 1.5 |
| EP-MK-034: Asset Generation | 6 | 34 | 1.5 |
| **TOTAL** | **25** | **138** | **7 sprints** |
