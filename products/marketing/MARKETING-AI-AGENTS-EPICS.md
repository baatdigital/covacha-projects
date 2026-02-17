# Marketing - Agentes IA Especializados (EP-MK-014 a EP-MK-023)

**Fecha**: 2026-02-16
**Product Owner**: BaatDigital / Marketing
**Estado**: Planificacion
**Continua desde**: MARKETING-EPICS.md (EP-MK-006 a EP-MK-013, US-MK-001 a US-MK-038)
**User Stories**: US-MK-039 en adelante

---

## Tabla de Contenidos

1. [Contexto y Motivacion](#contexto-y-motivacion)
2. [Arquitectura de Agentes IA para Marketing](#arquitectura-de-agentes-ia-para-marketing)
3. [Mapa de Epicas](#mapa-de-epicas)
4. [Epicas Detalladas](#epicas-detalladas)
5. [User Stories Detalladas](#user-stories-detalladas)
6. [Roadmap](#roadmap)
7. [Grafo de Dependencias](#grafo-de-dependencias)
8. [Riesgos y Mitigaciones](#riesgos-y-mitigaciones)

---

## Contexto y Motivacion

La agencia digital BaatDigital opera con mf-marketing (Angular 21, Native Federation, arquitectura hexagonal) y covacha-core (Python 3.9+, Flask) como backend principal. Con 13 epicas previas (EP-MK-001 a EP-MK-013) se cubrio la gestion de clientes, social media, estrategias, landing pages, brand kit, campanas y configuracion de IA.

El siguiente paso es **automatizar las operaciones de la agencia** con 10 agentes IA especializados que viven en `covacha-botia` y se comunican con `covacha-core` via API interna. Estos agentes operan a traves de WhatsApp Business API y Web chat (mf-ia), permitiendo que los Account Managers y Community Managers deleguen tareas repetitivas a la IA.

### Capacidades y Problemas que Resuelven

| Capacidad Actual (Manual) | Problema | Agente IA que Resuelve |
|---|---|---|
| Crear calendarios editoriales a mano | 4-8 horas por cliente/mes | EP-MK-014: Content Planning |
| Publicar y monitorear redes manualmente | Errores de horario, respuestas lentas | EP-MK-015: Social Media Management |
| Crear campanas Ads en Meta/Google | Configuracion compleja, optimizacion reactiva | EP-MK-016: Campanas Publicitarias |
| Disenar landing pages desde cero | 2-3 dias por landing | EP-MK-017: Landing Page Generator |
| Campanas de email con herramientas externas | Sin integracion con CRM, segmentacion limitada | EP-MK-018: Email Marketing |
| Secuencias de WhatsApp manuales | Follow-up inconsistente, leads perdidos | EP-MK-019: WhatsApp Marketing |
| Reportes mensuales en PowerPoint | 1-2 dias por reporte, datos desactualizados | EP-MK-020: Analytics y Reportes |
| Calificacion de leads por intuicion | Leads calientes no priorizados | EP-MK-021: Lead Generation |
| Verificar brand guidelines manualmente | Inconsistencias de marca frecuentes | EP-MK-022: Brand Kit y Assets |
| SEO basado en experiencia individual | Keywords no investigadas, oportunidades perdidas | EP-MK-023: SEO/SEM |

### Relacion con Features Existentes de mf-marketing

| Feature Existente | Agente que lo Potencia | Integracion |
|---|---|---|
| Social media posts + calendario | EP-MK-015 (Social Media) | Publica automaticamente posts del calendario |
| Landing editor DnD (FASE 1-5) | EP-MK-017 (Landing Generator) | Genera estructura de landing que se edita en el DnD |
| Estrategias de marketing | EP-MK-014 (Content Planning) | Genera plan de contenido alineado a la estrategia |
| Templates WhatsApp | EP-MK-019 (WhatsApp Marketing) | Usa templates aprobados en secuencias automaticas |
| Brand kit | EP-MK-022 (Brand Kit Assets) | Valida y genera assets respetando guidelines |
| Campaign builder Facebook Ads | EP-MK-016 (Campanas) | Automatiza creacion y optimizacion de campanas |
| Workflow de aprobacion | Todos los agentes | Borradores generados entran al workflow existente |
| AI Config Multi-Provider (EP-MK-013) | Todos los agentes | Cada agente usa el proveedor IA configurado por cliente |

---

## Arquitectura de Agentes IA para Marketing

```
                          ┌─────────────────────────────────────────┐
                          │           CANALES DE ENTRADA            │
                          │                                         │
                          │  WhatsApp ──┐   Web Chat ──┐  Email ─┐ │
                          │  Business   │   (mf-ia)    │  (SES)  │ │
                          │  API        │              │         │ │
                          └─────────────┼──────────────┼─────────┼─┘
                                        │              │         │
                                        ▼              ▼         ▼
                          ┌─────────────────────────────────────────┐
                          │        ORQUESTADOR DE AGENTES           │
                          │           (covacha-botia)               │
                          │                                         │
                          │  ┌─────────────────────────────────┐    │
                          │  │   Router de Intenciones (NLU)   │    │
                          │  │   - Clasifica mensaje entrante  │    │
                          │  │   - Identifica agente destino   │    │
                          │  │   - Mantiene contexto de sesion │    │
                          │  └──────────────┬──────────────────┘    │
                          │                 │                       │
                          │    ┌────────────┼────────────┐          │
                          │    ▼            ▼            ▼          │
                          │  ┌────┐  ┌──────────┐  ┌────────┐      │
                          │  │EP14│  │  EP15-23  │  │Fallback│      │
                          │  │    │  │ (8 more)  │  │ Human  │      │
                          │  └────┘  └──────────┘  └────────┘      │
                          │                                         │
                          │  ┌─────────────────────────────────┐    │
                          │  │    Shared Agent Context (SAC)    │    │
                          │  │  - Client profile + brand kit   │    │
                          │  │  - Historial de conversacion    │    │
                          │  │  - Quotas IA (EP-MK-013)        │    │
                          │  │  - Permisos del usuario         │    │
                          │  └─────────────────────────────────┘    │
                          └──────────┬──────────────────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
        ┌───────────────┐  ┌──────────────┐  ┌──────────────┐
        │  covacha-core │  │   APIs       │  │     SQS      │
        │  (Marketing   │  │   Externas   │  │   (Async)    │
        │   APIs)       │  │              │  │              │
        │               │  │ - Meta Graph │  │ - Publicar   │
        │ - Clientes    │  │ - Google Ads │  │ - Generar    │
        │ - Posts       │  │ - Google     │  │   contenido  │
        │ - Estrategias │  │   Analytics  │  │ - Enviar     │
        │ - Landings    │  │ - SES        │  │   emails     │
        │ - Templates   │  │ - OpenAI     │  │ - Analytics  │
        │ - Brand Kit   │  │ - Bedrock    │  │   batch      │
        └───────────────┘  └──────────────┘  └──────────────┘
                    │                                │
                    ▼                                ▼
        ┌───────────────┐                  ┌──────────────┐
        │   DynamoDB    │                  │ mf-marketing │
        │               │                  │ (Angular 21) │
        │ PK: AGENT#    │                  │              │
        │ PK: CAMPAIGN# │                  │ - Dashboard  │
        │ PK: CONTENT#  │                  │   de agentes │
        │ PK: LEAD#     │                  │ - Config     │
        │ PK: SEO#      │                  │ - Historial  │
        └───────────────┘                  └──────────────┘
```

### Flujo de Comunicacion entre Agentes

```
  Usuario (WhatsApp/Web)
       │
       │ "Genera el calendario de contenido para Cliente X en febrero"
       │
       ▼
  ┌──────────────┐     clasifica     ┌──────────────────┐
  │   Router     │ ────────────────► │  EP-MK-014       │
  │   NLU        │                   │  Content Planning │
  └──────────────┘                   └────────┬─────────┘
                                              │
                                    consulta  │  genera
                                    contexto  │  plan
                                              │
                            ┌─────────────────┼──────────────────┐
                            ▼                 ▼                  ▼
                    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
                    │ SAC: Client  │  │ covacha-core │  │ OpenAI/      │
                    │ Profile +    │  │ GET /social/ │  │ Bedrock      │
                    │ Brand Kit    │  │ analytics    │  │ (generacion) │
                    └──────────────┘  └──────────────┘  └──────────────┘
                                              │
                                              ▼
                                    ┌──────────────────┐
                                    │  SQS: Crear      │
                                    │  posts borrador   │
                                    │  en covacha-core  │
                                    └──────────────────┘
                                              │
                                              ▼
                                    ┌──────────────────┐
                                    │  Workflow de      │
                                    │  aprobacion       │
                                    │  (mf-marketing)   │
                                    └──────────────────┘
```

### Patrones Compartidos entre Agentes

- **Shared Agent Context (SAC)**: Cada agente accede al perfil del cliente, brand kit, historial de interacciones y quotas de IA configuradas en EP-MK-013.
- **Workflow de Aprobacion**: Todo contenido generado por un agente entra como "borrador pendiente de aprobacion" al workflow existente de mf-marketing.
- **Fallback Humano**: Si el agente no puede resolver la solicitud (confianza < 0.7), escala a un Account Manager humano.
- **Auditing**: Todas las acciones de agentes se registran en DynamoDB con prefijo `AGENT#` para trazabilidad.
- **Rate Limiting**: Cada agente respeta las quotas de IA del cliente (EP-MK-013) y los rate limits de APIs externas.

---

## Mapa de Epicas

| ID | Epica | Complejidad | Sprint | Dependencias |
|---|---|---|---|---|
| EP-MK-014 | Agente de Content Planning y Generacion | XL | 11-13 | EP-MK-013 (AI Config) |
| EP-MK-015 | Agente de Social Media Management | XL | 12-14 | EP-MK-014, Social adapters existentes |
| EP-MK-016 | Agente de Campanas Publicitarias (FB/Google Ads) | XL | 14-16 | EP-MK-007 (Campaign Builder), EP-MK-015 |
| EP-MK-017 | Agente de Landing Page Generator | L | 13-15 | EP-MK-006 (Landing Editor), EP-MK-014 |
| EP-MK-018 | Agente de Email Marketing | L | 14-16 | EP-MK-014 |
| EP-MK-019 | Agente de WhatsApp Marketing (Secuencias) | L | 12-14 | Templates WhatsApp existentes, EP-MK-014 |
| EP-MK-020 | Agente de Analytics y Reportes de Marketing | L | 15-17 | EP-MK-015, EP-MK-016, EP-MK-018 |
| EP-MK-021 | Agente de Lead Generation y Nurturing | XL | 14-16 | EP-MK-019, EP-MK-018, covacha-crm |
| EP-MK-022 | Agente de Brand Kit y Assets | M | 13-14 | EP-MK-008 (Brand Kit Completo) |
| EP-MK-023 | Agente de SEO/SEM | L | 15-17 | EP-MK-017, EP-MK-014 |

**Totales:**
- 10 epicas nuevas (EP-MK-014 a EP-MK-023)
- 55 user stories (US-MK-039 a US-MK-093)
- Estimacion total: ~150-200 dev-days
- Sprints estimados: 11 a 17

---

## Epicas Detalladas

---

### EP-MK-014: Agente de Content Planning y Generacion

**Objetivo**: Automatizar la creacion de planes de contenido completos con IA: calendarios editoriales, sugerencias de posts por plataforma, copywriting automatico, hashtags y horarios optimos.

**Descripcion**: Este agente es el nucleo del sistema de IA para marketing. A partir de la estrategia del cliente, su industria, brand voice y rendimiento historico, genera calendarios editoriales completos para Facebook, Instagram, TikTok y LinkedIn. Incluye copywriting por post, sugerencias de hashtags, horarios optimos de publicacion basados en analytics, y genera borradores que entran al workflow de aprobacion existente de mf-marketing. El agente aprende del rendimiento historico para mejorar sus recomendaciones en cada ciclo.

**Criterios de Aceptacion:**
- [ ] El agente genera un calendario editorial mensual completo para un cliente
- [ ] Cada post incluye: copy, hashtags, tipo de contenido, plataforma destino, horario sugerido
- [ ] El calendario se alinea a la estrategia de marketing activa del cliente
- [ ] Los borradores generados entran al workflow de aprobacion existente
- [ ] El agente puede invocarse via WhatsApp o Web chat
- [ ] Las recomendaciones mejoran basandose en metricas de posts previos
- [ ] Se respetan las quotas de IA del cliente (EP-MK-013)

**APIs:**
- `POST /api/v1/agents/content-planning/generate` - Genera calendario editorial
- `GET /api/v1/agents/content-planning/suggestions/{clientId}` - Sugerencias basadas en historico
- `POST /api/v1/agents/content-planning/optimize` - Optimiza horarios y hashtags
- `GET /api/v1/agents/content-planning/templates` - Templates de calendario por industria
- Consume: `GET /api/v1/organization/{orgId}/social/analytics` (covacha-core)
- Consume: `GET /api/v1/organization/{orgId}/clients/{id}/strategies` (covacha-core)

**Dependencias:** EP-MK-013 (AI Config Multi-Provider)

**Repositorios:** covacha-botia, covacha-core, mf-marketing, mf-ia

**Complejidad:** XL

**Sprint sugerido:** 11-13

---

### EP-MK-015: Agente de Social Media Management

**Objetivo**: Automatizar la gestion diaria de redes sociales: publicacion programada, monitoreo de comentarios/menciones, respuestas inteligentes, deteccion de crisis de reputacion y engagement automatico.

**Descripcion**: Este agente actua como un Community Manager virtual que opera 24/7. Publica posts programados del calendario (generados por EP-MK-014 o creados manualmente), monitorea comentarios y menciones en Facebook e Instagram usando los adapters ya existentes, genera respuestas automaticas inteligentes respetando el tono de marca, detecta crisis de reputacion (picos de comentarios negativos) y alerta al equipo humano, y sugiere re-posts de contenido que tuvo buen rendimiento.

**Criterios de Aceptacion:**
- [ ] Publica automaticamente posts programados en FB/IG en el horario definido
- [ ] Monitorea comentarios y menciones cada 5 minutos
- [ ] Genera y publica respuestas automaticas a comentarios positivos/neutrales
- [ ] Escala a humano comentarios negativos o con sentimiento < 0.3
- [ ] Detecta crisis de reputacion (>5 comentarios negativos en 1 hora)
- [ ] Sugiere re-posts de contenido con engagement > promedio
- [ ] Dashboard de actividad del agente en mf-marketing

**APIs:**
- `POST /api/v1/agents/social-media/publish` - Publica post programado
- `GET /api/v1/agents/social-media/monitor/{clientId}` - Estado del monitoreo
- `POST /api/v1/agents/social-media/respond` - Genera respuesta a comentario
- `GET /api/v1/agents/social-media/alerts/{clientId}` - Alertas de crisis
- `POST /api/v1/agents/social-media/repost-suggestions` - Sugerencias de re-post
- Consume: Facebook Graph API (comentarios, menciones, publicacion)
- Consume: Instagram API (comentarios, menciones)

**Dependencias:** EP-MK-014, Social media adapters existentes en mf-marketing

**Repositorios:** covacha-botia, covacha-core, covacha-webhook, mf-marketing

**Complejidad:** XL

**Sprint sugerido:** 12-14

---

### EP-MK-016: Agente de Campanas Publicitarias (Facebook/Google Ads)

**Objetivo**: Crear y optimizar campanas publicitarias con IA: generacion de audiencias, presupuestos sugeridos, copys A/B, optimizacion automatica de bids, pausa de campanas de bajo rendimiento y reportes de ROAS.

**Descripcion**: Este agente potencia el Campaign Builder existente (EP-MK-007) con inteligencia artificial. Sugiere audiencias basadas en el perfil del cliente, genera multiples variantes de copy para A/B testing, optimiza bids automaticamente basandose en ROAS, pausa campanas que no alcanzan KPIs minimos, y genera reportes de rendimiento. Integra tanto Facebook Ads Manager como Google Ads APIs.

**Criterios de Aceptacion:**
- [ ] Genera audiencias sugeridas basadas en industria y clientes similares
- [ ] Crea multiples copys A/B automaticamente para cada anuncio
- [ ] Optimiza bids automaticamente cada 6 horas basandose en CPA/ROAS
- [ ] Pausa campanas con rendimiento < umbral configurable (notifica antes)
- [ ] Genera reportes de ROAS por campana, por canal, por periodo
- [ ] Soporta Facebook Ads Manager y Google Ads
- [ ] Recomendaciones de presupuesto basadas en objetivo y mercado

**APIs:**
- `POST /api/v1/agents/campaigns/generate-audience` - Genera audiencia sugerida
- `POST /api/v1/agents/campaigns/generate-copies` - Genera copys A/B
- `POST /api/v1/agents/campaigns/optimize/{campaignId}` - Optimiza bids
- `GET /api/v1/agents/campaigns/roas/{clientId}` - Reporte de ROAS
- `POST /api/v1/agents/campaigns/auto-pause` - Evalua y pausa campanas
- Consume: Facebook Marketing API, Google Ads API

**Dependencias:** EP-MK-007 (Campaign Builder), EP-MK-015

**Repositorios:** covacha-botia, covacha-core, mf-marketing

**Complejidad:** XL

**Sprint sugerido:** 14-16

---

### EP-MK-017: Agente de Landing Page Generator

**Objetivo**: Generar landing pages completas con IA a partir de un briefing de texto: estructura, copywriting, CTAs, formularios, SEO meta tags y componentes visuales.

**Descripcion**: A partir de un briefing simple (producto, objetivo, audiencia), el agente genera una estructura completa de landing page compatible con el editor DnD existente (EP-MK-006). Incluye secciones hero, beneficios, testimonios, CTA, formularios y footer. Genera el copywriting alineado al brand kit del cliente, meta tags SEO optimizados, y puede crear variantes A/B automaticamente. La landing generada se puede editar en el editor visual antes de publicar.

**Criterios de Aceptacion:**
- [ ] Genera landing page completa desde briefing de texto (< 200 palabras)
- [ ] Estructura compatible con el editor DnD (secciones, componentes)
- [ ] Copywriting alineado al brand kit y tono del cliente
- [ ] Meta tags SEO generados automaticamente (title, description, OG)
- [ ] Genera variantes A/B de headlines y CTAs
- [ ] La landing generada es editable en el editor visual existente
- [ ] Monitoreo de conversiones post-publicacion

**APIs:**
- `POST /api/v1/agents/landing/generate` - Genera landing desde briefing
- `POST /api/v1/agents/landing/variants` - Genera variantes A/B
- `GET /api/v1/agents/landing/conversions/{landingId}` - Metricas de conversion
- `POST /api/v1/agents/landing/optimize-seo` - Optimiza SEO de landing existente
- Consume: `POST /api/v1/organization/{orgId}/landings` (covacha-core)

**Dependencias:** EP-MK-006 (Landing Editor Avanzado), EP-MK-014

**Repositorios:** covacha-botia, covacha-core, mf-marketing

**Complejidad:** L

**Sprint sugerido:** 13-15

---

### EP-MK-018: Agente de Email Marketing

**Objetivo**: Disenar y ejecutar campanas de email con IA: generacion de templates, personalizacion por segmento, programacion, A/B testing de subject lines y monitoreo de metricas.

**Descripcion**: Este agente gestiona el ciclo completo de email marketing. Genera templates HTML responsivos a partir de las plantillas existentes y el brand kit del cliente, personaliza contenido por segmento de audiencia, programa envios en horarios optimos, ejecuta A/B testing de subject lines automaticamente, y monitorea open rates y click rates para sugerir optimizaciones. Usa AWS SES para envio masivo.

**Criterios de Aceptacion:**
- [ ] Genera templates de email HTML responsivos desde briefing
- [ ] Personaliza contenido por segmento (nombre, industria, historial)
- [ ] Programa envios en horarios optimos por zona horaria
- [ ] A/B testing automatico de subject lines (2-5 variantes)
- [ ] Dashboard de metricas: open rate, click rate, bounce rate, unsubscribe
- [ ] Sugiere optimizaciones basadas en rendimiento historico
- [ ] Cumple con CAN-SPAM: link de unsubscribe, direccion fisica

**APIs:**
- `POST /api/v1/agents/email/generate-template` - Genera template de email
- `POST /api/v1/agents/email/campaign` - Crea y programa campana
- `POST /api/v1/agents/email/ab-test` - Configura A/B test
- `GET /api/v1/agents/email/metrics/{campaignId}` - Metricas de campana
- `GET /api/v1/agents/email/segments/{clientId}` - Segmentos disponibles
- Consume: AWS SES (envio), DynamoDB (tracking)

**Dependencias:** EP-MK-014

**Repositorios:** covacha-botia, covacha-core, covacha-notification, mf-marketing

**Complejidad:** L

**Sprint sugerido:** 14-16

---

### EP-MK-019: Agente de WhatsApp Marketing (Secuencias)

**Objetivo**: Automatizar secuencias de WhatsApp Business: nurture sequences, follow-up automatico, segmentacion de contactos, envio de templates aprobados y tracking de conversiones.

**Descripcion**: Aprovechando la infraestructura existente de WhatsApp Business API y los templates ya creados en mf-marketing, este agente automatiza secuencias de mensajes para nurturing de leads. Configura flujos de follow-up basados en triggers (formulario completado, compra, inactividad), segmenta contactos automaticamente, envia templates aprobados por Meta en la secuencia correcta, y trackea conversiones en cada paso del funnel.

**Criterios de Aceptacion:**
- [ ] Crea secuencias de mensajes WhatsApp con triggers configurables
- [ ] Triggers soportados: formulario, compra, inactividad, fecha, manual
- [ ] Usa exclusivamente templates aprobados por Meta
- [ ] Segmentacion automatica de contactos por comportamiento
- [ ] Tracking de conversiones por paso del funnel
- [ ] Re-engagement automatico de contactos inactivos (>30 dias)
- [ ] Respeta ventana de 24 horas de WhatsApp Business API

**APIs:**
- `POST /api/v1/agents/whatsapp/sequences` - Crea secuencia
- `GET /api/v1/agents/whatsapp/sequences/{clientId}` - Lista secuencias
- `POST /api/v1/agents/whatsapp/sequences/{id}/trigger` - Dispara secuencia
- `GET /api/v1/agents/whatsapp/sequences/{id}/metrics` - Metricas de secuencia
- `POST /api/v1/agents/whatsapp/segment` - Segmenta contactos
- Consume: WhatsApp Business API (envio de templates)
- Consume: covacha-webhook (recepcion de respuestas)

**Dependencias:** Templates WhatsApp existentes, EP-MK-014

**Repositorios:** covacha-botia, covacha-webhook, covacha-core, mf-marketing

**Complejidad:** L

**Sprint sugerido:** 12-14

---

### EP-MK-020: Agente de Analytics y Reportes de Marketing

**Objetivo**: Generar reportes inteligentes bajo demanda o programados con metricas de campanas, ROI por canal, social media, conversiones y recomendaciones automaticas.

**Descripcion**: Este agente consolida datos de todos los canales de marketing (social media, ads, email, WhatsApp, landing pages) y genera reportes inteligentes. Puede ejecutarse bajo demanda via WhatsApp/chat ("Dame el reporte de Cliente X de enero") o programarse para envio automatico. Incluye comparativas periodo-a-periodo, insights automaticos con recomendaciones accionables, y exportacion a PDF/CSV.

**Criterios de Aceptacion:**
- [ ] Genera reportes bajo demanda via WhatsApp o Web chat
- [ ] Reportes programables (semanal, mensual)
- [ ] Consolida metricas de: social media, ads, email, WhatsApp, landing pages
- [ ] Comparativas periodo-a-periodo (mes actual vs anterior, YoY)
- [ ] Insights automaticos con recomendaciones accionables
- [ ] Exportacion PDF y CSV
- [ ] Envio automatico por email al cliente

**APIs:**
- `POST /api/v1/agents/analytics/generate-report` - Genera reporte
- `GET /api/v1/agents/analytics/summary/{clientId}` - Resumen rapido
- `POST /api/v1/agents/analytics/schedule` - Programa reporte recurrente
- `GET /api/v1/agents/analytics/insights/{clientId}` - Insights automaticos
- `GET /api/v1/agents/analytics/export/{reportId}` - Exporta PDF/CSV
- Consume: Metricas de EP-MK-015, EP-MK-016, EP-MK-018, EP-MK-019

**Dependencias:** EP-MK-015, EP-MK-016, EP-MK-018

**Repositorios:** covacha-botia, covacha-core, mf-marketing

**Complejidad:** L

**Sprint sugerido:** 15-17

---

### EP-MK-021: Agente de Lead Generation y Nurturing

**Objetivo**: Capturar, calificar y nutrir leads automaticamente con scoring basado en comportamiento, asignacion a vendedores, secuencias de follow-up y deteccion de leads calientes.

**Descripcion**: Este agente gestiona el ciclo completo de leads: captura desde formularios de landing pages, WhatsApp y ads; califica automaticamente con un modelo de scoring basado en comportamiento (paginas visitadas, emails abiertos, mensajes respondidos); asigna a vendedores segun territorio/producto; ejecuta secuencias de nurturing personalizadas; detecta leads calientes y alerta al equipo. Se integra con covacha-crm para pipeline visual.

**Criterios de Aceptacion:**
- [ ] Captura leads de: landing pages, WhatsApp, Facebook Lead Ads, formularios
- [ ] Scoring automatico basado en: comportamiento, demografia, engagement
- [ ] Asignacion automatica a vendedores por reglas configurables
- [ ] Secuencias de nurturing personalizadas por segmento
- [ ] Deteccion de leads calientes (score > umbral) con alerta inmediata
- [ ] Pipeline visual de leads integrado con covacha-crm
- [ ] Metricas: leads por fuente, tasa de conversion, tiempo promedio de cierre

**APIs:**
- `POST /api/v1/agents/leads/capture` - Captura lead
- `POST /api/v1/agents/leads/score/{leadId}` - Calcula/actualiza score
- `POST /api/v1/agents/leads/assign/{leadId}` - Asigna a vendedor
- `GET /api/v1/agents/leads/pipeline/{clientId}` - Pipeline de leads
- `POST /api/v1/agents/leads/nurture/{leadId}` - Inicia secuencia nurturing
- `GET /api/v1/agents/leads/hot/{clientId}` - Leads calientes
- Consume: covacha-crm (CRM), covacha-webhook (formularios)

**Dependencias:** EP-MK-019, EP-MK-018, covacha-crm

**Repositorios:** covacha-botia, covacha-core, covacha-crm, covacha-webhook, mf-marketing

**Complejidad:** XL

**Sprint sugerido:** 14-16

---

### EP-MK-022: Agente de Brand Kit y Assets

**Objetivo**: Mantener consistencia de marca automaticamente: generar assets graficos, validar contenido contra brand guidelines, generar variaciones de logos y paletas para distintas plataformas.

**Descripcion**: Este agente potencia el Brand Kit existente (EP-MK-008) con inteligencia artificial. Genera assets graficos (banners, headers, thumbnails) respetando automaticamente el brand kit del cliente (colores, tipografias, logos). Valida que cualquier contenido nuevo (posts, landings, emails) cumpla las guias de marca antes de publicar. Genera variaciones de logos para distintas plataformas (perfil FB, story IG, favicon), adapta la paleta de colores para accesibilidad (contraste WCAG), y sugiere complementos visuales coherentes.

**Criterios de Aceptacion:**
- [ ] Genera assets graficos (banners, headers) respetando brand kit
- [ ] Valida contenido contra brand guidelines antes de publicar
- [ ] Genera variaciones de logos por plataforma (FB, IG, LinkedIn, favicon)
- [ ] Verifica contraste de colores (WCAG AA minimo)
- [ ] Sugiere complementos visuales coherentes con la marca
- [ ] Historial de assets generados por cliente

**APIs:**
- `POST /api/v1/agents/brand/generate-asset` - Genera asset grafico
- `POST /api/v1/agents/brand/validate` - Valida contenido contra brand guidelines
- `POST /api/v1/agents/brand/logo-variations` - Genera variaciones de logo
- `GET /api/v1/agents/brand/accessibility/{clientId}` - Reporte de accesibilidad
- `GET /api/v1/agents/brand/assets/{clientId}` - Historial de assets generados
- Consume: `GET /api/v1/organization/{orgId}/clients/{id}/brand-kit` (covacha-core)

**Dependencias:** EP-MK-008 (Brand Kit Completo)

**Repositorios:** covacha-botia, covacha-core, mf-marketing

**Complejidad:** M

**Sprint sugerido:** 13-14

---

### EP-MK-023: Agente de SEO/SEM

**Objetivo**: Optimizar la presencia en buscadores con analisis de keywords, sugerencias de contenido SEO, auditorias tecnicas de landing pages, monitoreo de posiciones y analisis de competencia.

**Descripcion**: Este agente analiza y optimiza la presencia organica y de pago en buscadores. Investiga keywords relevantes para cada cliente, genera content briefs SEO-optimizados para alimentar al agente de Content Planning (EP-MK-014), realiza auditorias tecnicas de landing pages (velocidad, meta tags, estructura, mobile-friendly), monitorea posiciones en Google para keywords objetivo, analiza la estrategia SEO de competidores, y genera recomendaciones de backlinks.

**Criterios de Aceptacion:**
- [ ] Analisis de keywords: volumen, dificultad, oportunidad, CPC
- [ ] Genera content briefs SEO-optimizados para el agente de contenido
- [ ] Auditoria tecnica de landing pages (meta tags, velocidad, mobile, estructura H1-H6)
- [ ] Monitoreo de posiciones en Google para keywords seleccionadas
- [ ] Analisis de competencia: keywords que rankean, contenido top, backlinks
- [ ] Generacion de meta tags optimizados para landings existentes
- [ ] Tracking de backlinks entrantes

**APIs:**
- `POST /api/v1/agents/seo/keyword-research` - Investigacion de keywords
- `POST /api/v1/agents/seo/content-brief` - Genera content brief SEO
- `POST /api/v1/agents/seo/audit/{landingId}` - Auditoria tecnica
- `GET /api/v1/agents/seo/positions/{clientId}` - Monitoreo de posiciones
- `POST /api/v1/agents/seo/competitor-analysis` - Analisis de competencia
- `POST /api/v1/agents/seo/optimize-meta/{landingId}` - Optimiza meta tags
- Consume: Google Search Console API, Google Analytics Data API

**Dependencias:** EP-MK-017, EP-MK-014

**Repositorios:** covacha-botia, covacha-core, mf-marketing

**Complejidad:** L

**Sprint sugerido:** 15-17

---

## User Stories Detalladas

---

### EP-MK-014: Agente de Content Planning y Generacion

---

#### US-MK-039: Generacion de calendario editorial mensual

**ID:** US-MK-039
**Epica:** EP-MK-014
**Prioridad:** P0
**Story Points:** 8

Como **Account Manager** quiero solicitar al agente IA la generacion de un calendario editorial mensual completo para un cliente para reducir de 4-8 horas a minutos la planificacion de contenido.

**Criterios de Aceptacion:**
- [ ] El agente recibe: cliente_id, mes, plataformas destino (FB, IG, TikTok, LinkedIn)
- [ ] Genera 20-30 posts distribuidos en el mes segun frecuencia por plataforma
- [ ] Cada post incluye: fecha, hora sugerida, plataforma, tipo (imagen, video, carousel, story), copy, hashtags
- [ ] El calendario se alinea a la estrategia activa del cliente (si existe)
- [ ] Se persiste en DynamoDB con PK `CONTENT#{clientId}` SK `PLAN#{yearMonth}`
- [ ] El calendario generado es editable antes de confirmar

**Notas Tecnicas:**
- Crear servicio `ContentPlanningAgent` en covacha-botia
- Consumir estrategia activa via `GET /api/v1/organization/{orgId}/clients/{id}/strategies`
- Usar GPT-4 con system prompt que incluye industria, brand voice y productos del cliente
- Resultado entra como borradores en el workflow de aprobacion de mf-marketing

**Dependencias:** EP-MK-013

---

#### US-MK-040: Sugerencias de contenido basadas en rendimiento historico

**ID:** US-MK-040
**Epica:** EP-MK-014
**Prioridad:** P0
**Story Points:** 5

Como **Account Manager** quiero que el agente analice el rendimiento de posts anteriores del cliente para que las sugerencias futuras se basen en datos reales y no solo en heuristicas genericas.

**Criterios de Aceptacion:**
- [ ] El agente analiza los ultimos 90 dias de posts publicados
- [ ] Identifica: mejores horarios, tipos de contenido con mas engagement, hashtags mas efectivos
- [ ] Genera recomendaciones especificas: "Los posts de producto los martes a las 10am tienen 3x mas engagement"
- [ ] Las recomendaciones se incorporan automaticamente al siguiente calendario generado
- [ ] Dashboard en mf-marketing muestra las recomendaciones del agente

**Notas Tecnicas:**
- Consumir analytics via `GET /api/v1/organization/{orgId}/social/analytics`
- Modelo de scoring: engagement rate, reach, clicks por tipo/hora/dia
- Cache de analisis en DynamoDB con TTL de 24 horas

**Dependencias:** US-MK-039

---

#### US-MK-041: Generacion automatica de copywriting por post

**ID:** US-MK-041
**Epica:** EP-MK-014
**Prioridad:** P0
**Story Points:** 5

Como **Community Manager** quiero que el agente genere el copy completo de cada post (texto principal, hashtags, CTA) para no tener que redactar manualmente cada publicacion.

**Criterios de Aceptacion:**
- [ ] Genera copy adaptado a cada plataforma (FB: largo, IG: medio + hashtags, TikTok: corto + trending, LinkedIn: profesional)
- [ ] Incluye CTA especifico segun objetivo del post (engagement, trafico, conversion)
- [ ] Genera 2-3 variantes de copy para elegir
- [ ] Respeta el tono de marca definido en el brand kit
- [ ] Limites de caracteres por plataforma respetados automaticamente

**Notas Tecnicas:**
- Prompt engineering por plataforma con limites de caracteres
- Usar brand voice del cliente como parametro del system prompt
- Streaming de respuesta para UX fluida en mf-ia

**Dependencias:** US-MK-039

---

#### US-MK-042: Optimizacion de horarios de publicacion

**ID:** US-MK-042
**Epica:** EP-MK-014
**Prioridad:** P1
**Story Points:** 5

Como **Account Manager** quiero que el agente sugiera los horarios optimos de publicacion por plataforma y dia de la semana para maximizar el alcance y engagement de cada post.

**Criterios de Aceptacion:**
- [ ] Analiza datos de engagement por hora/dia de los ultimos 90 dias
- [ ] Genera mapa de calor de mejores horarios por plataforma
- [ ] Si no hay datos historicos suficientes, usa benchmarks de la industria
- [ ] Los horarios sugeridos se aplican automaticamente al calendario generado
- [ ] El usuario puede override manualmente cualquier horario
- [ ] Se recalcula semanalmente con nuevos datos

**Notas Tecnicas:**
- Algoritmo: weighted average de engagement rate por hora/dia por plataforma
- Fallback a benchmarks por industria si < 30 posts historicos
- Almacenar mapa de calor en DynamoDB con PK `CONTENT#{clientId}` SK `SCHEDULE#optimal`

**Dependencias:** US-MK-040

---

#### US-MK-043: Templates de calendario por industria

**ID:** US-MK-043
**Epica:** EP-MK-014
**Prioridad:** P1
**Story Points:** 3

Como **Account Manager** quiero seleccionar un template de calendario predefinido por industria (restaurante, e-commerce, servicios profesionales, salud) para arrancar rapidamente con clientes nuevos que no tienen historial.

**Criterios de Aceptacion:**
- [ ] Minimo 5 templates de industria disponibles: restaurantes, e-commerce, servicios profesionales, salud/bienestar, educacion
- [ ] Cada template incluye: tipos de post por dia, frecuencia por plataforma, temas recurrentes
- [ ] El template se personaliza automaticamente con datos del cliente (nombre, productos, brand voice)
- [ ] Los templates son editables y se pueden crear nuevos desde cero
- [ ] El agente sugiere el template mas adecuado segun la industria del cliente

**Notas Tecnicas:**
- Templates almacenados como JSON en DynamoDB con PK `CONTENT#TEMPLATE` SK `INDUSTRY#{type}`
- Endpoint CRUD para gestion de templates
- API: `GET /api/v1/agents/content-planning/templates`

**Dependencias:** US-MK-039

---

#### US-MK-044: Invocacion del agente via WhatsApp

**ID:** US-MK-044
**Epica:** EP-MK-014
**Prioridad:** P1
**Story Points:** 5

Como **Account Manager** quiero pedirle al agente via WhatsApp "Genera el calendario de febrero para Cliente X" para gestionar contenido desde el movil sin abrir la plataforma web.

**Criterios de Aceptacion:**
- [ ] El agente responde a mensajes de WhatsApp con intencion de content planning
- [ ] Soporta lenguaje natural: "calendario para febrero", "sugiere posts para la proxima semana"
- [ ] Responde con resumen del calendario generado y link a mf-marketing para ver completo
- [ ] Pide confirmacion antes de crear los borradores: "Genere 24 posts para febrero. Confirma para crear borradores?"
- [ ] Si falta informacion, pregunta: "Para que cliente?" "Que plataformas?"

**Notas Tecnicas:**
- Integrar con Router NLU del orquestador de agentes en covacha-botia
- Intent classification: `content_planning.generate`, `content_planning.suggest`
- Respuesta truncada para WhatsApp (max 4096 chars), link a web para detalle
- Consumir webhook de WhatsApp Business API via covacha-webhook

**Dependencias:** US-MK-039, Router NLU (orquestador)

---

### EP-MK-015: Agente de Social Media Management

---

#### US-MK-045: Publicacion automatica de posts programados

**ID:** US-MK-045
**Epica:** EP-MK-015
**Prioridad:** P0
**Story Points:** 8

Como **Community Manager** quiero que los posts aprobados en el calendario se publiquen automaticamente en la plataforma destino en el horario programado para no tener que publicar manualmente cada post.

**Criterios de Aceptacion:**
- [ ] Posts con status "aprobado" se publican automaticamente en la fecha/hora programada
- [ ] Soporta publicacion en: Facebook (paginas), Instagram (business), LinkedIn (company pages)
- [ ] Si la publicacion falla, reintenta 3 veces con backoff exponencial
- [ ] Notifica al Community Manager si la publicacion falla despues de los reintentos
- [ ] Log de publicaciones exitosas/fallidas en DynamoDB
- [ ] Soporte para imagenes, videos y carousel

**Notas Tecnicas:**
- Cron job en SQS que evalua posts pendientes cada minuto
- Publicacion via Facebook Graph API `/{page-id}/feed`, Instagram Content Publishing API
- Idempotency key por post para evitar publicaciones duplicadas
- PK `AGENT#{agentId}` SK `PUBLISH#{postId}` para log

**Dependencias:** Workflow de aprobacion existente en mf-marketing

---

#### US-MK-046: Monitoreo de comentarios y menciones

**ID:** US-MK-046
**Epica:** EP-MK-015
**Prioridad:** P0
**Story Points:** 5

Como **Community Manager** quiero que el agente monitoree automaticamente los comentarios y menciones en FB/IG para responder rapidamente y no perder interacciones.

**Criterios de Aceptacion:**
- [ ] Monitoreo cada 5 minutos de nuevos comentarios en posts publicados
- [ ] Monitoreo de menciones de la pagina/cuenta del cliente
- [ ] Clasificacion por sentimiento: positivo, neutral, negativo
- [ ] Resumen en dashboard de mf-marketing: nuevos comentarios, pendientes, respondidos
- [ ] Filtro por cliente, plataforma y sentimiento

**Notas Tecnicas:**
- Polling via Facebook Graph API `/{post-id}/comments` con campo `since`
- Analisis de sentimiento con modelo de NLP (OpenAI o modelo ligero local)
- Almacenar en DynamoDB con PK `AGENT#social` SK `COMMENT#{commentId}`
- SQS para procesamiento async del analisis de sentimiento

**Dependencias:** US-MK-045

---

#### US-MK-047: Respuestas automaticas inteligentes

**ID:** US-MK-047
**Epica:** EP-MK-015
**Prioridad:** P0
**Story Points:** 8

Como **Community Manager** quiero que el agente genere y publique respuestas automaticas a comentarios positivos y neutrales para mantener engagement sin intervencion manual.

**Criterios de Aceptacion:**
- [ ] Genera respuestas personalizadas (no genericas) basadas en el contenido del comentario
- [ ] Solo responde automaticamente a comentarios positivos y neutrales (sentimiento > 0.3)
- [ ] Respeta el tono de marca del cliente
- [ ] No responde a comentarios que ya fueron respondidos
- [ ] Configurable por cliente: activar/desactivar auto-respuestas
- [ ] Limite de respuestas por hora para evitar spam (configurable, default 20/hora)

**Notas Tecnicas:**
- Prompt: "Eres el community manager de {client_name}. Responde al siguiente comentario en tono {brand_voice}..."
- Publicar via Graph API `/{comment-id}/replies`
- Flag `auto_responded: true` en el comentario para evitar duplicados
- Respeta quotas de IA del cliente (EP-MK-013)

**Dependencias:** US-MK-046, EP-MK-013

---

#### US-MK-048: Deteccion de crisis de reputacion

**ID:** US-MK-048
**Epica:** EP-MK-015
**Prioridad:** P0
**Story Points:** 5

Como **Account Manager** quiero que el agente detecte automaticamente una crisis de reputacion y me alerte inmediatamente para poder intervenir antes de que escale.

**Criterios de Aceptacion:**
- [ ] Detecta crisis cuando hay >5 comentarios negativos en 1 hora en un mismo cliente
- [ ] Alerta inmediata via WhatsApp al Account Manager asignado
- [ ] Alerta en dashboard de mf-marketing con indicador rojo
- [ ] Resumen de la crisis: posts afectados, comentarios negativos, temas detectados
- [ ] Pausa automatica de respuestas automaticas durante crisis
- [ ] Log de crisis en historial del cliente

**Notas Tecnicas:**
- Ventana deslizante de 1 hora para deteccion de picos
- Umbral configurable por cliente (default: 5 negativos/hora)
- Alerta via WhatsApp Business API template "crisis_alert"
- Estado `CRISIS_ACTIVE` en DynamoDB con TTL de 24 horas

**Dependencias:** US-MK-046

---

#### US-MK-049: Sugerencias de re-posts de contenido exitoso

**ID:** US-MK-049
**Epica:** EP-MK-015
**Prioridad:** P1
**Story Points:** 3

Como **Community Manager** quiero que el agente sugiera re-publicar contenido que tuvo alto engagement para maximizar el alcance con minimo esfuerzo.

**Criterios de Aceptacion:**
- [ ] Identifica posts con engagement > 2x promedio del cliente
- [ ] Sugiere re-post con variante de copy (no identico)
- [ ] Respeta intervalo minimo entre post original y re-post (configurable, default 30 dias)
- [ ] No sugiere re-posts de contenido temporal (ofertas vencidas, eventos pasados)
- [ ] Maximo 3 sugerencias activas por cliente

**Notas Tecnicas:**
- Calcular engagement promedio por cliente de ultimos 90 dias
- Filtrar posts con fecha > 30 dias y engagement > 2x promedio
- Generar variante de copy con prompt "Reescribe este post manteniendo la esencia..."

**Dependencias:** US-MK-046

---

### EP-MK-016: Agente de Campanas Publicitarias (Facebook/Google Ads)

---

#### US-MK-050: Generacion de audiencias sugeridas con IA

**ID:** US-MK-050
**Epica:** EP-MK-016
**Prioridad:** P0
**Story Points:** 8

Como **Account Manager** quiero que el agente sugiera audiencias para campanas publicitarias basandose en la industria del cliente y datos de audiencias similares exitosas para no crear segmentaciones desde cero.

**Criterios de Aceptacion:**
- [ ] Genera 3-5 audiencias sugeridas por campana
- [ ] Cada audiencia incluye: nombre descriptivo, edad, genero, ubicacion, intereses, comportamientos
- [ ] Las sugerencias se basan en: industria del cliente, audiencias previas exitosas, benchmarks
- [ ] Estimacion de tamano de audiencia via Meta Marketing API
- [ ] Las audiencias generadas se pueden guardar para reutilizar (integracion con US-MK-010)

**Notas Tecnicas:**
- Prompt: "Genera 5 audiencias para una campana de {objective} en la industria {industry}..."
- Validar que los intereses sugeridos existan en Meta Targeting API
- Estimacion via Meta Reach & Frequency API
- Almacenar con PK `CAMPAIGN#{clientId}` SK `AUDIENCE#suggested#{timestamp}`

**Dependencias:** EP-MK-007 (Campaign Builder)

---

#### US-MK-051: Generacion de copys A/B para anuncios

**ID:** US-MK-051
**Epica:** EP-MK-016
**Prioridad:** P0
**Story Points:** 5

Como **Account Manager** quiero que el agente genere multiples variantes de copy publicitario para A/B testing para encontrar el mensaje que mejor convierte sin redactar manualmente cada variante.

**Criterios de Aceptacion:**
- [ ] Genera 3-5 variantes de copy por anuncio
- [ ] Cada variante incluye: headline, texto principal, descripcion, CTA
- [ ] Variantes cubren diferentes angulos: beneficio, urgencia, social proof, pregunta
- [ ] Copys respetan limites de caracteres de Meta Ads (headline: 40, text: 125, description: 30)
- [ ] Copys alineados al brand voice del cliente

**Notas Tecnicas:**
- Prompt engineering con tecnica de "variacion por angulo"
- Validar limites de caracteres post-generacion, regenerar si excede
- API: `POST /api/v1/agents/campaigns/generate-copies`

**Dependencias:** US-MK-050

---

#### US-MK-052: Optimizacion automatica de bids

**ID:** US-MK-052
**Epica:** EP-MK-016
**Prioridad:** P0
**Story Points:** 8

Como **Account Manager** quiero que el agente optimice automaticamente los bids de campanas activas para maximizar ROAS sin intervencion manual constante.

**Criterios de Aceptacion:**
- [ ] Evalua rendimiento de campanas activas cada 6 horas
- [ ] Ajusta bids basandose en CPA/ROAS vs objetivo definido
- [ ] Reglas: si CPA > objetivo * 1.5 → reducir bid 20%; si ROAS > objetivo * 1.2 → aumentar bid 15%
- [ ] No ajusta campanas en las primeras 48 horas (fase de aprendizaje)
- [ ] Log de todos los ajustes con razon en DynamoDB
- [ ] Notifica al Account Manager de cambios realizados

**Notas Tecnicas:**
- Cron job via SQS cada 6 horas
- Consumir metricas via Meta Marketing API Insights
- Ajustar via Meta Marketing API `/{ad-set-id}` PATCH con nuevo bid
- PK `CAMPAIGN#{campaignId}` SK `OPTIMIZATION#{timestamp}` para log

**Dependencias:** US-MK-050, US-MK-051

---

#### US-MK-053: Reporte de ROAS y rendimiento publicitario

**ID:** US-MK-053
**Epica:** EP-MK-016
**Prioridad:** P1
**Story Points:** 5

Como **Account Manager** quiero ver un reporte de ROAS por campana, canal y periodo para evaluar la rentabilidad del gasto publicitario de cada cliente.

**Criterios de Aceptacion:**
- [ ] Metricas por campana: ROAS, CPA, CPM, CTR, conversiones, gasto total
- [ ] Desglose por canal: Facebook, Instagram, Google Ads
- [ ] Comparativa periodo a periodo (semana, mes)
- [ ] Top campanas por ROAS y peores campanas
- [ ] Visualizacion en dashboard de mf-marketing
- [ ] Exportacion PDF/CSV

**Notas Tecnicas:**
- Consolidar metricas de Meta Insights API y Google Ads Reporting API
- Pre-computar agregados diarios en DynamoDB para rendimiento
- API: `GET /api/v1/agents/campaigns/roas/{clientId}`

**Dependencias:** US-MK-052

---

#### US-MK-054: Pausa automatica de campanas de bajo rendimiento

**ID:** US-MK-054
**Epica:** EP-MK-016
**Prioridad:** P1
**Story Points:** 5

Como **Account Manager** quiero que el agente pause automaticamente campanas que no alcanzan KPIs minimos despues de un periodo de prueba para no desperdiciar presupuesto en campanas ineficientes.

**Criterios de Aceptacion:**
- [ ] Evalua campanas activas con >7 dias de ejecucion
- [ ] Pausa si: ROAS < 50% del objetivo por 3 dias consecutivos
- [ ] Notifica al Account Manager 24 horas ANTES de pausar con recomendaciones
- [ ] El Account Manager puede cancelar la pausa automatica
- [ ] Log de campanas pausadas con razon y metricas
- [ ] Sugiere cambios: ajustar audiencia, cambiar creativo, aumentar presupuesto

**Notas Tecnicas:**
- Evaluacion via cron job diario
- Alerta previa via WhatsApp y notificacion in-app
- Pausa via Meta Marketing API `/{campaign-id}` PATCH status=PAUSED
- PK `CAMPAIGN#{campaignId}` SK `PAUSE#{timestamp}` para historial

**Dependencias:** US-MK-052

---

### EP-MK-017: Agente de Landing Page Generator

---

#### US-MK-055: Generacion de landing page desde briefing

**ID:** US-MK-055
**Epica:** EP-MK-017
**Prioridad:** P0
**Story Points:** 8

Como **Account Manager** quiero generar una landing page completa describiendo en texto lo que necesito para reducir de 2-3 dias a minutos la creacion de landings.

**Criterios de Aceptacion:**
- [ ] Acepta briefing en texto libre (< 500 palabras): producto, objetivo, audiencia, tono
- [ ] Genera estructura completa: hero, beneficios (3-5), testimonios, CTA, formulario, footer
- [ ] Cada seccion incluye: tipo, contenido, estilos sugeridos
- [ ] Estructura compatible con el formato del editor DnD (EP-MK-006)
- [ ] La landing generada se abre directamente en el editor visual para ajustes
- [ ] Aplica automaticamente el brand kit del cliente (colores, tipografias, logo)

**Notas Tecnicas:**
- Prompt engineering con schema JSON de secciones del editor DnD
- Output: JSON compatible con `LandingEditorModel` del frontend
- Consumir brand kit via `GET /api/v1/organization/{orgId}/clients/{id}/brand-kit`
- Persistir borrador via `POST /api/v1/organization/{orgId}/landings`
- API: `POST /api/v1/agents/landing/generate`

**Dependencias:** EP-MK-006 (Landing Editor Avanzado)

---

#### US-MK-056: Generacion de copywriting SEO para landing

**ID:** US-MK-056
**Epica:** EP-MK-017
**Prioridad:** P0
**Story Points:** 5

Como **Account Manager** quiero que el copy de la landing este optimizado para SEO automaticamente para que la pagina posicione bien en buscadores sin necesidad de un especialista SEO.

**Criterios de Aceptacion:**
- [ ] Genera title tag optimizado (50-60 caracteres con keyword principal)
- [ ] Meta description con CTA (150-160 caracteres)
- [ ] Headings jerarquicos (H1 > H2 > H3) con keywords naturales
- [ ] Densidad de keyword principal entre 1-2% del texto
- [ ] Open Graph tags para compartir en redes sociales
- [ ] Alt text para imagenes sugerido

**Notas Tecnicas:**
- Integrar analisis de keywords del agente SEO (EP-MK-023) cuando disponible
- Validar meta tags contra best practices de Google
- Output incluido en el JSON de la landing generada

**Dependencias:** US-MK-055

---

#### US-MK-057: Generacion de variantes A/B de landing

**ID:** US-MK-057
**Epica:** EP-MK-017
**Prioridad:** P1
**Story Points:** 5

Como **Account Manager** quiero generar variantes A/B de una landing automaticamente para probar cual convierte mejor sin disenar manualmente cada variante.

**Criterios de Aceptacion:**
- [ ] Genera 2-3 variantes de la landing original
- [ ] Variantes difieren en: headline, CTA, disposicion de secciones, copy principal
- [ ] Cada variante se guarda como landing independiente
- [ ] Configurar distribucion de trafico entre variantes (50/50, 70/30, etc.)
- [ ] Dashboard de metricas comparativas por variante

**Notas Tecnicas:**
- Prompt: "Genera una variante de esta landing cambiando el angulo de {headline/CTA/layout}..."
- Tracking de variante via query parameter `?variant=A|B|C`
- Almacenar metricas por variante en DynamoDB con PK `CONTENT#{landingId}` SK `VARIANT#{variantId}`

**Dependencias:** US-MK-055

---

#### US-MK-058: Monitoreo de conversiones de landing pages

**ID:** US-MK-058
**Epica:** EP-MK-017
**Prioridad:** P1
**Story Points:** 5

Como **Account Manager** quiero ver las metricas de conversion de cada landing generada para saber cuales funcionan y cuales necesitan ajustes.

**Criterios de Aceptacion:**
- [ ] Metricas por landing: visitas, formularios enviados, tasa de conversion, tiempo en pagina
- [ ] Desglose por fuente de trafico: organico, ads, redes sociales, directo
- [ ] Comparativa entre variantes A/B si existen
- [ ] Alertas si conversion cae > 20% respecto a semana anterior
- [ ] Recomendaciones automaticas del agente para mejorar conversion

**Notas Tecnicas:**
- Pixel de tracking en landing renderizada
- Almacenar eventos con PK `CONTENT#{landingId}` SK `EVENT#{timestamp}`
- Consolidar metricas diarias para dashboard
- API: `GET /api/v1/agents/landing/conversions/{landingId}`

**Dependencias:** US-MK-055

---

#### US-MK-059: Optimizacion de landing existente con IA

**ID:** US-MK-059
**Epica:** EP-MK-017
**Prioridad:** P2
**Story Points:** 3

Como **Account Manager** quiero pedirle al agente que analice y sugiera mejoras a una landing existente para optimizar su rendimiento sin crearla de nuevo.

**Criterios de Aceptacion:**
- [ ] Analiza landing existente: estructura, copy, CTAs, SEO
- [ ] Genera lista de sugerencias priorizadas por impacto estimado
- [ ] Sugiere cambios concretos: "Cambiar headline de X a Y", "Mover CTA arriba del fold"
- [ ] Puede aplicar las sugerencias automaticamente (con confirmacion)
- [ ] Compara metricas antes vs despues de aplicar cambios

**Notas Tecnicas:**
- Consumir landing actual via API de covacha-core
- Analisis de heuristicas de conversion + best practices
- API: `POST /api/v1/agents/landing/optimize-seo`

**Dependencias:** US-MK-058

---

### EP-MK-018: Agente de Email Marketing

---

#### US-MK-060: Generacion de templates de email con IA

**ID:** US-MK-060
**Epica:** EP-MK-018
**Prioridad:** P0
**Story Points:** 8

Como **Account Manager** quiero generar templates de email HTML responsivos a partir de un briefing para crear campanas de email sin necesidad de disenar manualmente cada template.

**Criterios de Aceptacion:**
- [ ] Acepta briefing: tipo (newsletter, promo, bienvenida, reactivacion), producto/tema, tono
- [ ] Genera HTML responsivo que se ve bien en Gmail, Outlook, Apple Mail
- [ ] Aplica brand kit del cliente automaticamente (colores, logo, tipografia)
- [ ] Incluye: header con logo, cuerpo con copy, imagenes placeholder, CTA, footer con unsubscribe
- [ ] Template editable en editor visual antes de enviar
- [ ] Genera 2 variantes para A/B testing

**Notas Tecnicas:**
- Generar HTML con tables para compatibilidad de clientes de email
- Validar rendering con Litmus/Email on Acid API (o validacion interna)
- Almacenar template con PK `CONTENT#{clientId}` SK `EMAIL_TEMPLATE#{templateId}`
- API: `POST /api/v1/agents/email/generate-template`

**Dependencias:** EP-MK-014

---

#### US-MK-061: Creacion y programacion de campanas de email

**ID:** US-MK-061
**Epica:** EP-MK-018
**Prioridad:** P0
**Story Points:** 8

Como **Account Manager** quiero crear una campana de email completa (template + segmento + programacion) para ejecutar envios masivos a los contactos del cliente.

**Criterios de Aceptacion:**
- [ ] Wizard: Seleccionar template > Seleccionar segmento > Configurar envio > Preview > Programar
- [ ] Segmentos disponibles: todos los contactos, por tag, por comportamiento, custom
- [ ] Programar envio: inmediato o fecha/hora especifica
- [ ] Horario optimo automatico por zona horaria del destinatario
- [ ] Preview del email con datos reales de un contacto del segmento
- [ ] Confirmacion antes de envio con estimacion de destinatarios

**Notas Tecnicas:**
- Envio via AWS SES con rate limit configurable (default 14/segundo)
- Personalizacion con merge tags: `{{nombre}}`, `{{empresa}}`, `{{producto}}`
- SQS para procesamiento async del envio masivo
- PK `CAMPAIGN#{clientId}` SK `EMAIL#{campaignId}` para tracking
- API: `POST /api/v1/agents/email/campaign`

**Dependencias:** US-MK-060

---

#### US-MK-062: A/B testing de subject lines

**ID:** US-MK-062
**Epica:** EP-MK-018
**Prioridad:** P1
**Story Points:** 5

Como **Account Manager** quiero probar automaticamente 2-5 variantes de subject line para enviar la version ganadora al resto de la lista.

**Criterios de Aceptacion:**
- [ ] Genera 2-5 variantes de subject line con IA
- [ ] Envia cada variante a un subconjunto de la lista (10-20% por variante)
- [ ] Mide open rate despues de 2-4 horas (configurable)
- [ ] Envia automaticamente la variante ganadora al resto de la lista
- [ ] Reporta resultados: open rate por variante, ganadora, diferencia estadistica

**Notas Tecnicas:**
- Split aleatorio de la lista de destinatarios
- Timer en SQS para evaluacion despues de periodo de prueba
- Significancia estadistica: minimo 100 opens para declarar ganador
- API: `POST /api/v1/agents/email/ab-test`

**Dependencias:** US-MK-061

---

#### US-MK-063: Dashboard de metricas de email

**ID:** US-MK-063
**Epica:** EP-MK-018
**Prioridad:** P1
**Story Points:** 5

Como **Account Manager** quiero ver las metricas de mis campanas de email para evaluar su rendimiento y optimizar futuras campanas.

**Criterios de Aceptacion:**
- [ ] Metricas por campana: enviados, entregados, opens, clicks, bounces, unsubscribes
- [ ] Open rate y click rate como porcentaje
- [ ] Mapa de calor de clicks en el email (que links recibieron mas clicks)
- [ ] Tendencia de metricas en ultimas 10 campanas
- [ ] Benchmarks de la industria para comparacion
- [ ] Alertas si bounce rate > 5% o unsubscribe rate > 2%

**Notas Tecnicas:**
- Tracking de opens via pixel invisible (1x1 gif)
- Tracking de clicks via redirect URL
- Consolidar metricas en DynamoDB con actualizacion en tiempo real
- API: `GET /api/v1/agents/email/metrics/{campaignId}`

**Dependencias:** US-MK-061

---

#### US-MK-064: Personalizacion de contenido por segmento

**ID:** US-MK-064
**Epica:** EP-MK-018
**Prioridad:** P2
**Story Points:** 5

Como **Account Manager** quiero que el contenido del email se personalice automaticamente segun el segmento del destinatario para aumentar relevancia y engagement.

**Criterios de Aceptacion:**
- [ ] Bloques condicionales en el template: mostrar/ocultar seccion segun segmento
- [ ] Contenido dinamico: producto recomendado, oferta personalizada
- [ ] Merge tags avanzados: `{{if segment == "vip"}}...{{endif}}`
- [ ] Preview por segmento: ver como se ve el email para cada segmento
- [ ] Metricas desglosadas por segmento

**Notas Tecnicas:**
- Motor de templates con soporte para logica condicional
- Resolver merge tags al momento del envio (no antes)
- Segmentos basados en tags de contactos y comportamiento previo

**Dependencias:** US-MK-061

---

### EP-MK-019: Agente de WhatsApp Marketing (Secuencias)

---

#### US-MK-065: Creacion de secuencias de mensajes WhatsApp

**ID:** US-MK-065
**Epica:** EP-MK-019
**Prioridad:** P0
**Story Points:** 8

Como **Account Manager** quiero crear secuencias automaticas de mensajes WhatsApp para nurturing de leads para automatizar el follow-up sin intervencion manual.

**Criterios de Aceptacion:**
- [ ] Builder visual de secuencia: nodos de mensaje conectados con flechas
- [ ] Tipos de nodo: enviar template, esperar N dias, condicion (respondio/no respondio), fin
- [ ] Solo usa templates aprobados por Meta (seleccion de catalogo existente)
- [ ] Preview del flujo completo antes de activar
- [ ] Limite de mensajes por contacto configurable (default: max 3/semana)
- [ ] Secuencia se pausa si el contacto responde (escala a humano)

**Notas Tecnicas:**
- Modelo de secuencia como grafo dirigido aciclico (DAG) en JSON
- Almacenar con PK `AGENT#whatsapp` SK `SEQUENCE#{sequenceId}`
- Ejecucion via SQS con delay para nodos de espera
- Respetar ventana de 24 horas de WhatsApp Business API
- API: `POST /api/v1/agents/whatsapp/sequences`

**Dependencias:** Templates WhatsApp existentes en mf-marketing

---

#### US-MK-066: Triggers automaticos para secuencias

**ID:** US-MK-066
**Epica:** EP-MK-019
**Prioridad:** P0
**Story Points:** 5

Como **Account Manager** quiero configurar triggers que inicien automaticamente una secuencia para que los leads reciban follow-up sin que tenga que dispararlo manualmente.

**Criterios de Aceptacion:**
- [ ] Triggers soportados: formulario de landing completado, compra realizada, inactividad >N dias, fecha especifica, manual
- [ ] Un trigger puede activar multiples secuencias
- [ ] Proteccion anti-spam: un contacto no puede estar en 2 secuencias simultaneas del mismo tipo
- [ ] Log de triggers disparados con timestamp y contacto
- [ ] Activar/desactivar triggers sin eliminar la secuencia

**Notas Tecnicas:**
- Webhook listeners en covacha-webhook para eventos de formulario/compra
- Cron job diario para triggers de inactividad y fecha
- PK `AGENT#whatsapp` SK `TRIGGER#{triggerId}` para configuracion
- API: `POST /api/v1/agents/whatsapp/sequences/{id}/trigger`

**Dependencias:** US-MK-065, covacha-webhook

---

#### US-MK-067: Segmentacion automatica de contactos

**ID:** US-MK-067
**Epica:** EP-MK-019
**Prioridad:** P1
**Story Points:** 5

Como **Account Manager** quiero que los contactos de WhatsApp se segmenten automaticamente segun su comportamiento para enviar secuencias relevantes a cada grupo.

**Criterios de Aceptacion:**
- [ ] Segmentos automaticos: nuevos (< 7 dias), activos (interaccion en ultimos 30 dias), inactivos (> 30 dias sin interaccion), compradores, no compradores
- [ ] Tags manuales adicionales por contacto
- [ ] Reglas de segmentacion custom: combinar condiciones con AND/OR
- [ ] Conteo de contactos por segmento en tiempo real
- [ ] Los segmentos se usan como target en secuencias y campanas

**Notas Tecnicas:**
- Evaluacion de segmentos como queries sobre historial de contactos
- Actualizar segmentos en batch cada hora via SQS
- PK `LEAD#{contactId}` SK `SEGMENT#{segmentId}` para membership
- API: `POST /api/v1/agents/whatsapp/segment`

**Dependencias:** US-MK-065

---

#### US-MK-068: Metricas de secuencias WhatsApp

**ID:** US-MK-068
**Epica:** EP-MK-019
**Prioridad:** P1
**Story Points:** 5

Como **Account Manager** quiero ver las metricas de cada secuencia para saber cuales funcionan y cuales necesitan ajustes.

**Criterios de Aceptacion:**
- [ ] Metricas por secuencia: contactos activos, completados, abandonados
- [ ] Metricas por nodo: enviados, entregados, leidos, respondidos
- [ ] Tasa de conversion del funnel completo
- [ ] Comparativa entre secuencias del mismo tipo
- [ ] Identificar nodo con mayor tasa de abandono (cuello de botella)

**Notas Tecnicas:**
- Tracking via webhooks de WhatsApp Business API (status: sent, delivered, read)
- Consolidar metricas por nodo en DynamoDB
- API: `GET /api/v1/agents/whatsapp/sequences/{id}/metrics`

**Dependencias:** US-MK-065

---

#### US-MK-069: Re-engagement de contactos inactivos

**ID:** US-MK-069
**Epica:** EP-MK-019
**Prioridad:** P2
**Story Points:** 3

Como **Account Manager** quiero que el agente identifique y re-engage automaticamente contactos que llevan >30 dias sin interaccion para recuperar leads potenciales antes de perderlos.

**Criterios de Aceptacion:**
- [ ] Identifica contactos sin interaccion en ultimos 30, 60, 90 dias
- [ ] Envia template de re-engagement personalizado segun tiempo de inactividad
- [ ] Si no responde despues de 2 intentos (separados por 7 dias), marca como "frio"
- [ ] Si responde, reactiva la secuencia de nurturing correspondiente
- [ ] Reporte de tasa de reactivacion por periodo

**Notas Tecnicas:**
- Cron job semanal para identificar contactos inactivos
- Templates de re-engagement pre-aprobados por Meta
- Maximo 2 intentos de re-engagement por contacto por ciclo de 90 dias

**Dependencias:** US-MK-067

---

### EP-MK-020: Agente de Analytics y Reportes de Marketing

---

#### US-MK-070: Generacion de reportes bajo demanda

**ID:** US-MK-070
**Epica:** EP-MK-020
**Prioridad:** P0
**Story Points:** 8

Como **Account Manager** quiero pedirle al agente "Dame el reporte de Cliente X de enero" via WhatsApp o web chat para obtener un resumen de rendimiento sin generar el reporte manualmente.

**Criterios de Aceptacion:**
- [ ] El agente entiende solicitudes de reporte en lenguaje natural
- [ ] Genera reporte consolidado con metricas de: social media, ads, email, WhatsApp, landing pages
- [ ] Via WhatsApp: responde con resumen de texto + link al reporte completo
- [ ] Via web chat: muestra reporte interactivo inline
- [ ] Tiempo de generacion < 30 segundos
- [ ] Cachea reportes por 1 hora para solicitudes repetidas

**Notas Tecnicas:**
- Intent classification: `analytics.report.generate`
- Consolidar datos de todos los agentes via APIs internas
- Cache en DynamoDB con TTL de 1 hora
- API: `POST /api/v1/agents/analytics/generate-report`

**Dependencias:** EP-MK-015, EP-MK-016, EP-MK-018

---

#### US-MK-071: Reportes programados automaticos

**ID:** US-MK-071
**Epica:** EP-MK-020
**Prioridad:** P0
**Story Points:** 5

Como **Account Manager** quiero programar reportes automaticos semanales o mensuales para que los clientes reciban su reporte sin que yo tenga que generarlo cada vez.

**Criterios de Aceptacion:**
- [ ] Configurar reporte recurrente: frecuencia (semanal/mensual), destinatarios, formato (PDF/HTML)
- [ ] Envio automatico por email con el reporte adjunto
- [ ] Envio automatico por WhatsApp con resumen + link al PDF
- [ ] Historial de reportes enviados por cliente
- [ ] Pausar/reanudar programacion sin eliminar configuracion

**Notas Tecnicas:**
- Cron job via SQS para evaluar reportes pendientes de generacion
- Generacion de PDF via puppeteer (server-side rendering)
- Envio via AWS SES con adjunto
- PK `AGENT#analytics` SK `SCHEDULE#{scheduleId}` para configuracion
- API: `POST /api/v1/agents/analytics/schedule`

**Dependencias:** US-MK-070

---

#### US-MK-072: Insights automaticos con recomendaciones

**ID:** US-MK-072
**Epica:** EP-MK-020
**Prioridad:** P1
**Story Points:** 5

Como **Account Manager** quiero que el agente genere insights automaticos con recomendaciones accionables para saber que ajustar sin tener que analizar los datos manualmente.

**Criterios de Aceptacion:**
- [ ] Genera 3-5 insights por reporte basados en anomalias y tendencias
- [ ] Formato: "El engagement de Instagram cayo 25% esta semana. Posible causa: publicaste 40% menos. Recomendacion: aumentar frecuencia a 5 posts/semana."
- [ ] Detecta: caidas, picos, tendencias, correlaciones entre canales
- [ ] Prioriza insights por impacto potencial (alto, medio, bajo)
- [ ] Los insights se incluyen en reportes automaticos y bajo demanda

**Notas Tecnicas:**
- Analisis estadistico: comparar metricas actuales vs media movil de 4 semanas
- Detectar anomalias con z-score > 2
- Prompt de IA para generar explicacion y recomendacion en lenguaje natural
- API: `GET /api/v1/agents/analytics/insights/{clientId}`

**Dependencias:** US-MK-070

---

#### US-MK-073: Comparativas periodo a periodo

**ID:** US-MK-073
**Epica:** EP-MK-020
**Prioridad:** P1
**Story Points:** 5

Como **Account Manager** quiero ver comparativas de metricas entre periodos para demostrar progreso al cliente y detectar regresiones.

**Criterios de Aceptacion:**
- [ ] Comparativa mes actual vs mes anterior para todas las metricas
- [ ] Comparativa mismo mes ano anterior (YoY) si hay datos disponibles
- [ ] Indicadores visuales: flecha verde (mejora), roja (regresion), gris (sin cambio)
- [ ] Porcentaje de cambio por metrica
- [ ] Se incluye automaticamente en reportes generados

**Notas Tecnicas:**
- Calcular deltas y porcentajes de cambio por metrica
- Almacenar snapshots mensuales para comparativas YoY
- Incluir en output de `POST /api/v1/agents/analytics/generate-report`

**Dependencias:** US-MK-070

---

#### US-MK-074: Exportacion de reportes PDF/CSV

**ID:** US-MK-074
**Epica:** EP-MK-020
**Prioridad:** P1
**Story Points:** 5

Como **Account Manager** quiero exportar reportes como PDF o CSV para compartir con clientes que no tienen acceso a la plataforma.

**Criterios de Aceptacion:**
- [ ] Exportar reporte completo como PDF con graficas renderizadas
- [ ] Exportar datos tabulares como CSV para analisis en Excel
- [ ] PDF incluye: logo del cliente, logo de agencia, fecha, metricas, graficas, insights
- [ ] Formato profesional con branding del cliente (brand kit)
- [ ] Link de descarga valido por 7 dias

**Notas Tecnicas:**
- PDF: puppeteer renderiza HTML a PDF en servidor
- CSV: generar desde datos crudos con libreria csv-writer
- Almacenar en S3 con presigned URL y TTL de 7 dias
- API: `GET /api/v1/agents/analytics/export/{reportId}`

**Dependencias:** US-MK-070

---

### EP-MK-021: Agente de Lead Generation y Nurturing

---

#### US-MK-075: Captura automatica de leads multicanal

**ID:** US-MK-075
**Epica:** EP-MK-021
**Prioridad:** P0
**Story Points:** 8

Como **Account Manager** quiero que el agente capture automaticamente leads desde todos los canales del cliente para centralizar la informacion sin captura manual.

**Criterios de Aceptacion:**
- [ ] Captura de: formularios de landing pages, mensajes WhatsApp, Facebook Lead Ads, formularios web
- [ ] Deduplicacion por email y/o telefono
- [ ] Datos capturados: nombre, email, telefono, fuente, canal, fecha, datos custom del formulario
- [ ] Normalizacion de datos (formato telefono, email lowercase)
- [ ] Confirmacion de captura al contacto (email/WhatsApp automatico)
- [ ] Almacenamiento en DynamoDB con PK `LEAD#{clientId}` SK `CONTACT#{leadId}`

**Notas Tecnicas:**
- Webhook listener en covacha-webhook para formularios y Facebook Lead Ads
- Parser de mensajes WhatsApp para extraer datos de contacto
- Deduplicacion con GSI en email y GSI en telefono
- API: `POST /api/v1/agents/leads/capture`

**Dependencias:** EP-MK-019, covacha-webhook

---

#### US-MK-076: Lead scoring automatico

**ID:** US-MK-076
**Epica:** EP-MK-021
**Prioridad:** P0
**Story Points:** 8

Como **Account Manager** quiero que cada lead tenga un score automatico basado en su comportamiento para priorizar los leads con mayor probabilidad de conversion.

**Criterios de Aceptacion:**
- [ ] Score de 0-100 basado en: fuente del lead, datos demograficos, engagement, comportamiento
- [ ] Factores de scoring configurables por cliente con pesos ajustables
- [ ] Score se actualiza automaticamente con cada interaccion
- [ ] Clasificacion: frio (0-30), tibio (31-60), caliente (61-80), muy caliente (81-100)
- [ ] Historial de cambios de score por lead
- [ ] Alerta inmediata cuando un lead pasa de tibio a caliente

**Notas Tecnicas:**
- Modelo de scoring: suma ponderada de factores
- Factores default: fuente (ads=20, organico=10), datos completos (+10), email abierto (+5), link clickeado (+10), formulario enviado (+15), respuesta WhatsApp (+10)
- Recalcular en cada evento via SQS
- PK `LEAD#{clientId}` SK `SCORE#{leadId}` para historial
- API: `POST /api/v1/agents/leads/score/{leadId}`

**Dependencias:** US-MK-075

---

#### US-MK-077: Asignacion automatica de leads a vendedores

**ID:** US-MK-077
**Epica:** EP-MK-021
**Prioridad:** P1
**Story Points:** 5

Como **Account Manager** quiero que los leads se asignen automaticamente al vendedor correcto segun reglas configurables para que cada lead sea atendido rapidamente por la persona indicada.

**Criterios de Aceptacion:**
- [ ] Reglas de asignacion: por zona geografica, por producto de interes, por fuente del lead, round-robin
- [ ] Configuracion de reglas por cliente
- [ ] Notificacion inmediata al vendedor asignado (WhatsApp + in-app)
- [ ] Reasignacion manual por Account Manager
- [ ] Balance de carga: no asignar mas de N leads activos por vendedor
- [ ] Fallback si ningun vendedor coincide: asignar al Account Manager

**Notas Tecnicas:**
- Motor de reglas evaluado en orden de prioridad
- Round-robin con counter en DynamoDB
- Notificacion via WhatsApp Business API template "lead_assignment"
- API: `POST /api/v1/agents/leads/assign/{leadId}`

**Dependencias:** US-MK-076

---

#### US-MK-078: Pipeline visual de leads

**ID:** US-MK-078
**Epica:** EP-MK-021
**Prioridad:** P1
**Story Points:** 5

Como **Account Manager** quiero ver un pipeline visual de leads (tipo kanban) con las etapas del funnel para tener visibilidad del estado de todos los leads.

**Criterios de Aceptacion:**
- [ ] Pipeline kanban con columnas: Nuevo, Contactado, Calificado, Propuesta, Negociacion, Cerrado (ganado/perdido)
- [ ] Drag-and-drop para mover leads entre etapas
- [ ] Tarjeta de lead con: nombre, score, fuente, tiempo en etapa, vendedor asignado
- [ ] Filtros: por vendedor, por score, por fuente, por fecha
- [ ] Metricas: leads por etapa, tasa de conversion por etapa, tiempo promedio por etapa
- [ ] Integrado con covacha-crm para leads que pasan a oportunidad

**Notas Tecnicas:**
- Componente kanban en mf-marketing reutilizando Angular CDK drag-drop
- Sincronizar con covacha-crm via API cuando lead pasa a "Propuesta"
- API: `GET /api/v1/agents/leads/pipeline/{clientId}`

**Dependencias:** US-MK-076, covacha-crm

---

#### US-MK-079: Deteccion y alerta de leads calientes

**ID:** US-MK-079
**Epica:** EP-MK-021
**Prioridad:** P0
**Story Points:** 5

Como **Account Manager** quiero recibir alertas inmediatas cuando un lead alcanza score de "caliente" para contactarlo antes de que pierda interes.

**Criterios de Aceptacion:**
- [ ] Alerta inmediata via WhatsApp cuando score > 80
- [ ] Alerta in-app con banner destacado en dashboard
- [ ] Resumen del lead en la alerta: nombre, score, ultimas interacciones, canal de origen
- [ ] Sugerencia de accion: "Llamar en las proximas 2 horas para maximizar conversion"
- [ ] Tiempo promedio entre deteccion y contacto como metrica del equipo

**Notas Tecnicas:**
- Trigger en recalculo de score cuando cruza umbral de 80
- WhatsApp template "hot_lead_alert" con datos del lead
- PK `LEAD#{clientId}` SK `ALERT#{leadId}#{timestamp}` para historial
- API: `GET /api/v1/agents/leads/hot/{clientId}`

**Dependencias:** US-MK-076

---

### EP-MK-022: Agente de Brand Kit y Assets

---

#### US-MK-080: Generacion de assets graficos con brand kit

**ID:** US-MK-080
**Epica:** EP-MK-022
**Prioridad:** P0
**Story Points:** 8

Como **Community Manager** quiero generar assets graficos (banners, headers, thumbnails) que respeten automaticamente el brand kit del cliente para crear contenido visual consistente rapidamente.

**Criterios de Aceptacion:**
- [ ] Genera assets para: banner FB (851x315), header IG (1080x1080), thumbnail YouTube (1280x720), story IG (1080x1920)
- [ ] Acepta briefing: texto a incluir, tipo de asset, tono visual
- [ ] Aplica automaticamente colores, tipografia y logo del brand kit del cliente
- [ ] Genera 2-3 variantes por solicitud
- [ ] Formato de salida: PNG y JPG optimizados para web
- [ ] Historial de assets generados por cliente

**Notas Tecnicas:**
- Usar modelo de generacion de imagen (DALL-E 3 o Stable Diffusion via Bedrock)
- Post-procesamiento: superponer logo, aplicar paleta de colores, tipografia
- Almacenar en S3 con referencia en DynamoDB PK `AGENT#brand` SK `ASSET#{assetId}`
- API: `POST /api/v1/agents/brand/generate-asset`

**Dependencias:** EP-MK-008 (Brand Kit Completo)

---

#### US-MK-081: Validacion de contenido contra brand guidelines

**ID:** US-MK-081
**Epica:** EP-MK-022
**Prioridad:** P0
**Story Points:** 5

Como **Account Manager** quiero que el agente valide automaticamente que cualquier contenido nuevo cumpla las guias de marca del cliente para evitar publicar contenido inconsistente.

**Criterios de Aceptacion:**
- [ ] Valida: colores usados vs paleta oficial, tipografia correcta, logo en formato correcto
- [ ] Valida tono de copy contra brand voice definido
- [ ] Resultado: aprobado / advertencias / rechazado con lista de incumplimientos
- [ ] Integracion con workflow de aprobacion: validacion automatica antes de publicar
- [ ] Override posible por Account Manager con justificacion
- [ ] Reporte de cumplimiento de marca por periodo

**Notas Tecnicas:**
- Analisis de imagen: extraer colores dominantes y compararlos con paleta
- Analisis de texto: clasificar tono con NLP y comparar con brand voice
- Integrar como paso previo en workflow de aprobacion de mf-marketing
- API: `POST /api/v1/agents/brand/validate`

**Dependencias:** US-MK-080

---

#### US-MK-082: Variaciones de logo por plataforma

**ID:** US-MK-082
**Epica:** EP-MK-022
**Prioridad:** P1
**Story Points:** 5

Como **Account Manager** quiero que el agente genere automaticamente variaciones del logo del cliente para cada plataforma para tener siempre el formato correcto listo para usar.

**Criterios de Aceptacion:**
- [ ] Genera variaciones: perfil FB (180x180), perfil IG (320x320), perfil LinkedIn (400x400), favicon (32x32, 16x16), Open Graph (1200x630)
- [ ] Adapta: recorte inteligente, padding adecuado por plataforma, fondo transparente o solido segun necesidad
- [ ] Verifica que el logo sea legible en cada tamano (alerta si es demasiado pequeno)
- [ ] Genera version monocromo y version sobre fondo oscuro si no existen
- [ ] Download pack con todos los formatos en ZIP

**Notas Tecnicas:**
- Procesamiento de imagen con Pillow (Python) para resize y adaptacion
- Deteccion de legibilidad: verificar contraste minimo a cada tamano
- Almacenar pack en S3 con referencia en brand kit del cliente
- API: `POST /api/v1/agents/brand/logo-variations`

**Dependencias:** EP-MK-008

---

#### US-MK-083: Verificacion de accesibilidad de colores

**ID:** US-MK-083
**Epica:** EP-MK-022
**Prioridad:** P1
**Story Points:** 3

Como **Account Manager** quiero que el agente verifique que la paleta de colores del cliente cumpla con estandares de accesibilidad WCAG para asegurar que el contenido sea legible para todos.

**Criterios de Aceptacion:**
- [ ] Evalua contraste de todas las combinaciones de colores del brand kit
- [ ] Reporte WCAG AA (minimo 4.5:1 para texto normal, 3:1 para texto grande)
- [ ] Sugiere ajustes de color si alguna combinacion no cumple
- [ ] Re-evaluacion automatica cuando se actualiza la paleta
- [ ] Badge "Accesible" en brand kit si todas las combinaciones cumplen

**Notas Tecnicas:**
- Calculo de contraste con formula WCAG 2.1
- Generar pares de colores: texto sobre fondo, CTA sobre fondo, etc.
- API: `GET /api/v1/agents/brand/accessibility/{clientId}`

**Dependencias:** EP-MK-008

---

#### US-MK-084: Sugerencia de complementos visuales

**ID:** US-MK-084
**Epica:** EP-MK-022
**Prioridad:** P2
**Story Points:** 3

Como **Community Manager** quiero que el agente sugiera elementos visuales complementarios (iconos, patrones, texturas) coherentes con el brand kit del cliente para enriquecer el contenido visual.

**Criterios de Aceptacion:**
- [ ] Sugiere iconos de librerias open source (Material Icons, Feather, etc.) que combinen con la marca
- [ ] Sugiere patrones/texturas de fondo basados en la paleta de colores
- [ ] Genera paleta extendida: colores complementarios, tints, shades
- [ ] Preview de sugerencias aplicadas a un mockup
- [ ] Las sugerencias se guardan en el brand kit para uso futuro

**Notas Tecnicas:**
- Teoria del color para generar complementarios, analogos, triadicos
- Match de iconos por industria y estilo visual
- API: `GET /api/v1/agents/brand/assets/{clientId}`

**Dependencias:** US-MK-080

---

### EP-MK-023: Agente de SEO/SEM

---

#### US-MK-085: Investigacion de keywords

**ID:** US-MK-085
**Epica:** EP-MK-023
**Prioridad:** P0
**Story Points:** 8

Como **Account Manager** quiero que el agente investigue y sugiera keywords relevantes para el negocio del cliente para basar la estrategia de contenido en datos reales de busqueda.

**Criterios de Aceptacion:**
- [ ] Genera lista de 20-50 keywords relevantes a partir de: industria, productos, servicios, competidores del cliente
- [ ] Cada keyword incluye: volumen de busqueda mensual, dificultad (0-100), CPC estimado, tendencia
- [ ] Clasificacion: head terms, long-tail, preguntas, transaccionales, informacionales
- [ ] Sugiere keyword clusters para organizar contenido
- [ ] Exportar lista como CSV
- [ ] Actualizacion mensual automatica de metricas

**Notas Tecnicas:**
- Integrar con Google Search Console API y/o Google Ads Keyword Planner
- Enriquecer con datos de IA: generar long-tail keywords basadas en head terms
- Almacenar con PK `SEO#{clientId}` SK `KEYWORD#{keyword}`
- API: `POST /api/v1/agents/seo/keyword-research`

**Dependencias:** EP-MK-017

---

#### US-MK-086: Content briefs SEO-optimizados

**ID:** US-MK-086
**Epica:** EP-MK-023
**Prioridad:** P0
**Story Points:** 5

Como **Account Manager** quiero que el agente genere content briefs optimizados para SEO para que el agente de Content Planning (EP-MK-014) genere contenido que posicione.

**Criterios de Aceptacion:**
- [ ] Genera brief que incluye: keyword principal, keywords secundarias, estructura H1-H6 sugerida, preguntas a responder, longitud recomendada
- [ ] Analiza top 10 resultados de Google para la keyword principal
- [ ] Sugiere angulo unico para diferenciarse de competidores
- [ ] Brief compatible como input para el agente de Content Planning
- [ ] Estimacion de dificultad de rankear para esa keyword

**Notas Tecnicas:**
- Scraping ligero de SERPs para analizar competencia (o API de tercero)
- Output: JSON estructurado que alimenta prompt del agente de contenido
- API: `POST /api/v1/agents/seo/content-brief`

**Dependencias:** US-MK-085, EP-MK-014

---

#### US-MK-087: Auditoria tecnica de landing pages

**ID:** US-MK-087
**Epica:** EP-MK-023
**Prioridad:** P0
**Story Points:** 5

Como **Account Manager** quiero que el agente audite tecnicamente las landing pages del cliente para identificar problemas que afecten el posicionamiento en buscadores.

**Criterios de Aceptacion:**
- [ ] Verifica: meta title (presente, longitud), meta description (presente, longitud), H1 (unico, presente), estructura H1-H6 (jerarquica)
- [ ] Verifica: velocidad de carga (< 3s), mobile-friendly, imagenes con alt text
- [ ] Verifica: canonical URL, robots.txt, sitemap.xml
- [ ] Score de 0-100 con desglose por categoria
- [ ] Lista priorizada de problemas con instrucciones de correccion
- [ ] Re-auditoria automatica despues de cambios

**Notas Tecnicas:**
- Crawler ligero en Python (requests + BeautifulSoup)
- PageSpeed Insights API para velocidad de carga
- Almacenar auditorias con PK `SEO#{clientId}` SK `AUDIT#{landingId}#{timestamp}`
- API: `POST /api/v1/agents/seo/audit/{landingId}`

**Dependencias:** EP-MK-017

---

#### US-MK-088: Monitoreo de posiciones en Google

**ID:** US-MK-088
**Epica:** EP-MK-023
**Prioridad:** P1
**Story Points:** 5

Como **Account Manager** quiero monitorear las posiciones de las keywords del cliente en Google para medir el impacto de la estrategia SEO.

**Criterios de Aceptacion:**
- [ ] Tracking diario de posicion para keywords seleccionadas (max 50 por cliente)
- [ ] Historial de posiciones con grafica de tendencia
- [ ] Alertas cuando una keyword sube o baja >5 posiciones
- [ ] Desglose por dispositivo: desktop vs mobile
- [ ] Promedio de posicion como KPI en reportes
- [ ] Comparativa con posicion de competidores (si disponible)

**Notas Tecnicas:**
- Integrar con Google Search Console API para posiciones reales
- Cron job diario para capturar posiciones
- PK `SEO#{clientId}` SK `POSITION#{keyword}#{date}` para historial
- API: `GET /api/v1/agents/seo/positions/{clientId}`

**Dependencias:** US-MK-085

---

#### US-MK-089: Analisis de competencia SEO

**ID:** US-MK-089
**Epica:** EP-MK-023
**Prioridad:** P1
**Story Points:** 5

Como **Account Manager** quiero que el agente analice la estrategia SEO de los competidores del cliente para identificar oportunidades y amenazas.

**Criterios de Aceptacion:**
- [ ] Analiza hasta 5 competidores por cliente
- [ ] Identifica: keywords que rankean, contenido top, dominios referentes
- [ ] Gap analysis: keywords donde compite el competidor pero no el cliente
- [ ] Oportunidades: keywords de baja competencia relevantes para el cliente
- [ ] Reporte comparativo exportable
- [ ] Actualizacion mensual automatica

**Notas Tecnicas:**
- Analisis basado en datos de Google Search Console + IA para inferir estrategia
- Alertar cuando un competidor empieza a rankear para una keyword del cliente
- API: `POST /api/v1/agents/seo/competitor-analysis`

**Dependencias:** US-MK-085

---

#### US-MK-090: Optimizacion automatica de meta tags

**ID:** US-MK-090
**Epica:** EP-MK-023
**Prioridad:** P1
**Story Points:** 3

Como **Account Manager** quiero que el agente optimice automaticamente los meta tags de landing pages existentes para mejorar el CTR en resultados de busqueda.

**Criterios de Aceptacion:**
- [ ] Genera title tags optimizados (keyword + brand, 50-60 chars)
- [ ] Genera meta descriptions con CTA (150-160 chars)
- [ ] Genera Open Graph tags para redes sociales
- [ ] Preview de como se vera en Google (SERP snippet preview)
- [ ] Puede aplicar automaticamente los cambios (con confirmacion)
- [ ] Tracking de CTR antes vs despues del cambio

**Notas Tecnicas:**
- Consumir keywords del analisis de EP-MK-023
- Validar contra best practices de Google (longitud, keyword placement)
- Actualizar via API de covacha-core landings
- API: `POST /api/v1/agents/seo/optimize-meta/{landingId}`

**Dependencias:** US-MK-087

---

#### US-MK-091: Tracking de backlinks

**ID:** US-MK-091
**Epica:** EP-MK-023
**Prioridad:** P2
**Story Points:** 3

Como **Account Manager** quiero monitorear los backlinks entrantes a las paginas del cliente para medir la autoridad del dominio y detectar backlinks toxicos.

**Criterios de Aceptacion:**
- [ ] Lista de backlinks entrantes con: dominio referente, pagina destino, anchor text, fecha de deteccion
- [ ] Clasificacion: backlinks de calidad, neutrales, toxicos
- [ ] Alerta cuando se detecta un backlink toxico
- [ ] Metricas: total backlinks, dominios referentes unicos, Domain Authority estimado
- [ ] Exportar lista como CSV para herramienta de disavow

**Notas Tecnicas:**
- Integrar con Google Search Console API (Links report)
- Clasificacion de calidad basada en Domain Authority del referente
- Almacenar con PK `SEO#{clientId}` SK `BACKLINK#{domain}#{date}`
- API: endpoint incluido en `GET /api/v1/agents/seo/positions/{clientId}`

**Dependencias:** US-MK-088

---

### User Stories Adicionales Cross-Agent

---

#### US-MK-092: Dashboard unificado de agentes IA en mf-marketing

**ID:** US-MK-092
**Epica:** Transversal (todos los agentes)
**Prioridad:** P0
**Story Points:** 8

Como **Administrador BaatDigital** quiero un dashboard unificado en mf-marketing que muestre el estado y actividad de todos los agentes IA para tener visibilidad completa de la automatizacion.

**Criterios de Aceptacion:**
- [ ] Dashboard con tarjeta por agente: nombre, estado (activo/pausado/error), actividad ultimas 24h
- [ ] Metricas globales: tareas ejecutadas hoy, tareas pendientes, errores, quotas consumidas
- [ ] Log de actividad reciente de todos los agentes con filtros
- [ ] Activar/desactivar agentes por cliente
- [ ] Alertas de agentes con errores o quotas agotadas
- [ ] Link a configuracion detallada de cada agente

**Notas Tecnicas:**
- Nueva pagina en mf-marketing: `/marketing/ai-agents/dashboard`
- Consumir endpoints de status de cada agente
- WebSocket o polling cada 30s para actualizacion en tiempo real
- Componente reutilizable `AgentCardComponent`

**Dependencias:** EP-MK-013 (AI Config)

---

#### US-MK-093: Orquestador de agentes y Router NLU

**ID:** US-MK-093
**Epica:** Transversal (todos los agentes)
**Prioridad:** P0
**Story Points:** 13

Como **Sistema** quiero un orquestador central que reciba mensajes de usuarios y los enrute al agente correcto para que el sistema multi-agente funcione como una experiencia unificada.

**Criterios de Aceptacion:**
- [ ] Clasifica la intencion del mensaje entrante y selecciona el agente destino
- [ ] Mantiene contexto de sesion: si el usuario esta en medio de una conversacion con un agente, continua con ese agente
- [ ] Soporta cambio de agente explicito: "Cambia al agente de SEO"
- [ ] Fallback a humano si confianza de clasificacion < 0.7
- [ ] Shared Agent Context (SAC) disponible para todos los agentes
- [ ] Rate limiting por usuario: max 100 mensajes/hora
- [ ] Logging de todas las interacciones para auditoria

**Notas Tecnicas:**
- Implementar en covacha-botia como servicio central `AgentOrchestrator`
- NLU: clasificacion de intenciones con GPT-4 + reglas heuristicas
- Sesion con TTL de 30 minutos en DynamoDB PK `AGENT#session` SK `USER#{userId}`
- SAC: pre-cargar perfil de cliente, brand kit, quotas al inicio de sesion
- SQS para procesamiento async de mensajes pesados

**Dependencias:** Ninguna (es prerequisito de todos los agentes)

---

## Roadmap

### Fase 0 - Infraestructura Base (Sprint 11)

| Sprint | User Stories | Descripcion |
|---|---|---|
| 11 | US-MK-093 | Orquestador de agentes y Router NLU (prerequisito) |
| 11 | US-MK-092 | Dashboard unificado de agentes en mf-marketing |

### Fase 1 - Agentes Core (Sprint 11-14)

| Sprint | User Stories | Descripcion |
|---|---|---|
| 11-12 | US-MK-039 a US-MK-044 | EP-MK-014: Content Planning y Generacion |
| 12-13 | US-MK-065 a US-MK-069 | EP-MK-019: WhatsApp Marketing (Secuencias) |
| 12-14 | US-MK-045 a US-MK-049 | EP-MK-015: Social Media Management |
| 13-14 | US-MK-080 a US-MK-084 | EP-MK-022: Brand Kit y Assets |

### Fase 2 - Agentes de Generacion (Sprint 13-16)

| Sprint | User Stories | Descripcion |
|---|---|---|
| 13-15 | US-MK-055 a US-MK-059 | EP-MK-017: Landing Page Generator |
| 14-16 | US-MK-060 a US-MK-064 | EP-MK-018: Email Marketing |
| 14-16 | US-MK-050 a US-MK-054 | EP-MK-016: Campanas Publicitarias |

### Fase 3 - Agentes de Inteligencia (Sprint 14-17)

| Sprint | User Stories | Descripcion |
|---|---|---|
| 14-16 | US-MK-075 a US-MK-079 | EP-MK-021: Lead Generation y Nurturing |
| 15-17 | US-MK-070 a US-MK-074 | EP-MK-020: Analytics y Reportes |
| 15-17 | US-MK-085 a US-MK-091 | EP-MK-023: SEO/SEM |

### Resumen del Roadmap

```
Sprint:  11     12     13     14     15     16     17
         │      │      │      │      │      │      │
Infra:   ██████ │      │      │      │      │      │  US-MK-092, US-MK-093
         │      │      │      │      │      │      │
EP-014:  ██████████████ │      │      │      │      │  Content Planning
EP-019:  │ ████████████ │      │      │      │      │  WhatsApp Marketing
EP-015:  │ ██████████████████ │      │      │      │  Social Media
EP-022:  │      │ ████████████ │      │      │      │  Brand Kit Assets
         │      │      │      │      │      │      │
EP-017:  │      │ ████████████████ │      │      │  Landing Generator
EP-018:  │      │      │ ████████████████ │      │  Email Marketing
EP-016:  │      │      │ ████████████████ │      │  Campanas Ads
         │      │      │      │      │      │      │
EP-021:  │      │      │ ████████████████ │      │  Lead Generation
EP-020:  │      │      │      │ ████████████████ │  Analytics/Reportes
EP-023:  │      │      │      │ ████████████████ │  SEO/SEM
```

---

## Grafo de Dependencias

```
                          ┌──────────────┐
                          │  US-MK-093   │
                          │ Orquestador  │
                          │    NLU       │
                          └──────┬───────┘
                                 │
                    ┌────────────┼────────────────────────┐
                    │            │                        │
                    ▼            ▼                        ▼
          ┌──────────────┐ ┌──────────────┐    ┌──────────────┐
          │  EP-MK-013   │ │  US-MK-092   │    │  Adapters    │
          │  AI Config   │ │  Dashboard   │    │  existentes  │
          │  (existente) │ │  Agentes     │    │  (FB/IG/WA)  │
          └──────┬───────┘ └──────────────┘    └──────┬───────┘
                 │                                     │
        ┌────────┼────────────────────────┐           │
        │        │                        │           │
        ▼        ▼                        ▼           ▼
  ┌──────────┐ ┌──────────┐      ┌──────────────┐ ┌──────────────┐
  │ EP-MK-014│ │ EP-MK-022│      │  EP-MK-015   │ │  EP-MK-019   │
  │ Content  │ │ Brand Kit│      │  Social Media│ │  WhatsApp    │
  │ Planning │ │ Assets   │      │  Management  │ │  Marketing   │
  └────┬─────┘ └──────────┘      └──────┬───────┘ └──────┬───────┘
       │                                │                │
       ├──────────────┬─────────────────┤                │
       │              │                 │                │
       ▼              ▼                 ▼                ▼
 ┌──────────┐  ┌──────────┐    ┌──────────────┐  ┌──────────────┐
 │ EP-MK-017│  │ EP-MK-023│    │  EP-MK-016   │  │  EP-MK-021   │
 │ Landing  │  │ SEO/SEM  │    │  Campanas     │  │  Lead Gen    │
 │ Generator│  │          │    │  Publicitarias│  │  & Nurturing │
 └────┬─────┘  └──────────┘    └──────┬───────┘  └──────────────┘
      │                               │
      └───────────────┬───────────────┘
                      │
                      ▼
              ┌──────────────┐
              │  EP-MK-018   │
              │  Email       │
              │  Marketing   │
              └──────┬───────┘
                     │
                     ▼
              ┌──────────────┐
              │  EP-MK-020   │
              │  Analytics   │
              │  & Reportes  │
              └──────────────┘


Dependencias entre Epicas:

  EP-MK-014 ──► EP-MK-015 (contenido alimenta publicacion)
  EP-MK-014 ──► EP-MK-017 (content briefs alimentan landings)
  EP-MK-014 ──► EP-MK-018 (contenido alimenta emails)
  EP-MK-014 ──► EP-MK-023 (briefs SEO alimentan contenido)
  EP-MK-015 ──► EP-MK-016 (metricas sociales alimentan campanas)
  EP-MK-015 ──► EP-MK-020 (metricas para reportes)
  EP-MK-016 ──► EP-MK-020 (metricas de ads para reportes)
  EP-MK-017 ──► EP-MK-023 (landings auditadas por SEO)
  EP-MK-018 ──► EP-MK-020 (metricas de email para reportes)
  EP-MK-018 ──► EP-MK-021 (emails para nurturing de leads)
  EP-MK-019 ──► EP-MK-021 (WhatsApp para nurturing de leads)
  EP-MK-008 ──► EP-MK-022 (brand kit base para assets IA)
  EP-MK-006 ──► EP-MK-017 (editor DnD para editar landings generadas)
  EP-MK-007 ──► EP-MK-016 (campaign builder para crear campanas)

Dependencias Externas:

  EP-MK-013 (AI Config) ──► Todos los agentes
  covacha-crm ──► EP-MK-021 (Lead Generation)
  Facebook Graph API ──► EP-MK-015, EP-MK-016
  Google Ads API ──► EP-MK-016
  Google Search Console ──► EP-MK-023
  AWS SES ──► EP-MK-018
  WhatsApp Business API ──► EP-MK-019, US-MK-093
```

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigacion |
|---|---|---|---|
| Costos de IA descontrolados por uso masivo de agentes | Alta | Alto | Quotas por cliente (EP-MK-013), alertas al 80%, modelo de fallback mas barato (GPT-3.5/Bedrock) |
| Rate limits de APIs externas (Meta, Google) bloquean agentes | Alta | Alto | Cache agresivo de datos (TTL 1h), batch operations, backoff exponencial, cola de reintentos en SQS |
| Calidad de contenido generado por IA insuficiente | Media | Alto | Workflow de aprobacion obligatorio, scoring de calidad pre-publicacion, fine-tuning con datos del cliente |
| WhatsApp Business API rechaza templates o banea cuenta | Media | Alto | Validacion previa de templates, respetar rate limits, monitoreo de quality rating, cuenta de contingencia |
| Complejidad del orquestador multi-agente (US-MK-093) | Alta | Alto | Implementar incrementalmente: 2 agentes primero, agregar de a 1, tests de integracion exhaustivos |
| Latencia alta en respuestas de agentes via WhatsApp | Media | Medio | Streaming donde posible, respuesta inmediata "Procesando..." + respuesta async, SQS para tareas pesadas |
| Datos insuficientes para recomendaciones de IA (clientes nuevos) | Alta | Medio | Fallback a benchmarks de industria, templates predefinidos, periodo de "aprendizaje" de 30 dias minimo |
| Brand Kit incompleto impide generacion de assets consistentes | Media | Medio | Wizard obligatorio de brand kit al onboarding, valores default por industria, validacion de completitud |
| Conflicto entre agentes actuando sobre el mismo cliente simultaneamente | Baja | Alto | Lock por cliente en orquestador, cola de prioridad por agente, Shared Agent Context con semaforos |
| Cambios en APIs externas (Meta, Google) rompen integraciones | Media | Alto | Abstraccion con adapter pattern, versionado de APIs, alertas de deprecation, tests de integracion periodicos |
| Leads duplicados o mal calificados | Media | Medio | Deduplicacion por email+telefono, validacion de datos al capturar, recalibracion mensual de scoring model |
| Reportes con datos incorrectos o desactualizados | Baja | Alto | Validacion cruzada de metricas entre fuentes, timestamp visible en reportes, refresh manual disponible |

---

## Definition of Done (Global para Agentes IA)

Para considerar una user story de agente IA como DONE:

- [ ] Agente implementado en covacha-botia con tests unitarios (pytest, coverage >= 80%)
- [ ] APIs expuestas documentadas con OpenAPI/Swagger
- [ ] Integracion con orquestador (Router NLU) verificada
- [ ] Invocacion via WhatsApp probada end-to-end
- [ ] Invocacion via Web chat (mf-ia) probada end-to-end
- [ ] Respeta quotas de IA del cliente (EP-MK-013)
- [ ] Contenido generado entra al workflow de aprobacion
- [ ] Fallback a humano funciona cuando confianza < 0.7
- [ ] Logging de todas las acciones en DynamoDB (prefijo AGENT#)
- [ ] UI en mf-marketing actualizada (dashboard, configuracion)
- [ ] Tests de mf-marketing con coverage >= 80% (Karma + Jasmine)
- [ ] Build de produccion exitoso en ambos repos
- [ ] Ningun archivo > 1000 lineas
- [ ] Ninguna funcion > 50 lineas
- [ ] Code review aprobado
- [ ] PR creado automaticamente via GitHub Actions (coverage >= 98%)
