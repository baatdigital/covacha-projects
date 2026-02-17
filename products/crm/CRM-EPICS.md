# CRM - Epicas de Gestion de Relaciones (EP-CR-001 a EP-CR-008)

**Fecha**: 2026-02-16
**Product Owner**: SuperPago / BaatDigital
**Estado**: Planificacion
**Prioridad**: P3
**Prefijo Epicas**: EP-CR
**Prefijo User Stories**: US-CR

---

## Tabla de Contenidos

1. [Contexto y Motivacion](#contexto-y-motivacion)
2. [Roles Involucrados](#roles-involucrados)
3. [Arquitectura CRM](#arquitectura-crm)
4. [Modelo de Datos DynamoDB](#modelo-de-datos-dynamodb)
5. [Mapa de Epicas](#mapa-de-epicas)
6. [Epicas Detalladas](#epicas-detalladas)
7. [User Stories Detalladas](#user-stories-detalladas)
8. [Roadmap](#roadmap)
9. [Grafo de Dependencias](#grafo-de-dependencias)
10. [Riesgos y Mitigaciones](#riesgos-y-mitigaciones)
11. [Definition of Done Global](#definition-of-done-global)

---

## Contexto y Motivacion

El ecosistema SuperPago/BaatDigital carece de un CRM centralizado. Actualmente, la gestion de clientes se hace de forma fragmentada:

| Problema | Situacion Actual |
|----------|-----------------|
| Contactos dispersos | Cada producto (SuperPago, BaatDigital, AlertaTribunal) gestiona clientes de forma independiente |
| Sin pipeline de ventas | No hay seguimiento estructurado de oportunidades de negocio |
| Sin historial unificado | Las interacciones por WhatsApp, email y llamadas no se centralizan |
| Sin automatizaciones | Tareas repetitivas (follow-ups, recordatorios) se hacen manualmente |
| Sin metricas de ventas | No hay visibilidad de conversion, ciclo de venta ni forecast |

### Que es y que NO es este CRM

| Es | No es |
|----|-------|
| CRM independiente multi-tenant para gestionar contactos, deals y actividades | Gestion de clientes de agencia (eso vive en mf-marketing) |
| Consumido por SuperPago (clientes empresa), BaatDigital (clientes agencia), AlertaTribunal (despachos) | Reemplazo del modulo de clientes de marketing |
| Integrado con WhatsApp via covacha-botia y email via covacha-notification | Un producto standalone sin relacion con el ecosistema |

### Repositorios Involucrados

| Repositorio | Funcion | Puerto Dev |
|-------------|---------|------------|
| `covacha-crm` | Backend CRM (contactos, deals, activities, workflows) | 5010 |
| `covacha-libs` | Modelos compartidos, repositorios base, decoradores | N/A |
| `covacha-botia` | Integracion WhatsApp (envio/recepcion mensajes) | 5003 |
| `covacha-notification` | Envio de emails y notificaciones push | 5005 |

### Tenants Consumidores

| Tenant | Uso del CRM | Tipo de Contactos |
|--------|------------|-------------------|
| **SuperPago** | Pipeline de ventas de productos financieros (SPEI, BillPay, Openpay) | Empresas, personas morales, tesoreros |
| **BaatDigital** | Pipeline de ventas de servicios de agencia (marketing, diseno, desarrollo) | PyMEs, emprendedores, directores de marketing |
| **AlertaTribunal** | Pipeline de ventas de alertas legales | Despachos juridicos, abogados, notarios |

---

## Roles Involucrados

### R1: Vendedor

Ejecutivo comercial que gestiona contactos y avanza deals por el pipeline.

**Responsabilidades:**
- Crear y actualizar contactos con informacion relevante
- Gestionar deals asignados a su nombre
- Registrar actividades (llamadas, reuniones, emails)
- Avanzar deals por las etapas del pipeline
- Comunicarse con contactos via WhatsApp y email desde el CRM

### R2: Gerente de Ventas

Lider de equipo que supervisa el rendimiento del equipo comercial.

**Responsabilidades:**
- Ver pipeline consolidado de todo su equipo
- Reasignar deals entre vendedores
- Monitorear metricas de conversion y ciclo de venta
- Aprobar descuentos o condiciones especiales en deals
- Generar reportes de forecast y rendimiento

### R3: Administrador CRM

Responsable de configurar el CRM para su organizacion/tenant.

**Responsabilidades:**
- Configurar etapas del pipeline
- Crear campos personalizados para contactos y deals
- Configurar automatizaciones (workflows)
- Gestionar API keys y webhooks
- Administrar permisos y roles del equipo
- Importar/exportar datos masivos

### R4: Sistema

Procesos automatizados que operan sin intervencion humana.

**Responsabilidades:**
- Ejecutar workflows programados (triggers, acciones, condiciones)
- Enviar recordatorios automaticos de actividades
- Sincronizar mensajes de WhatsApp al timeline del contacto
- Registrar emails entrantes/salientes en el timeline
- Detectar y sugerir merge de contactos duplicados
- Generar reportes periodicos automaticos

---

## Arquitectura CRM

### Diagrama de Componentes

```
                    +-------------------+
                    |     mf-core       |
                    |   (Shell host)    |
                    +--------+----------+
                             |
                             | (futuro: mf-crm)
                             |
+----------------------------v----------------------------+
|                    API Gateway + WAF                     |
|              api.superpago.com.mx/api/v1/crm            |
+---+----------------+----------------+----------------+--+
    |                |                |                |
    v                v                v                v
+--------+   +----------+   +-----------+   +-------------+
|covacha |   | covacha  |   | covacha   |   | covacha     |
|  -crm  |   |  -botia  |   | -notif.   |   |  -libs      |
|        |   |          |   |           |   |             |
|Contacts|   | WhatsApp |   | Email     |   | BaseModel   |
|Deals   |   | Templates|   | Templates |   | BaseRepo    |
|Activit.|   | Send/Recv|   | SMTP/IMAP |   | Decorators  |
|Workflows   | Bulk msg |   | Tracking  |   | Auth utils  |
|Reports |   |          |   |           |   |             |
+---+----+   +----+-----+   +----+------+   +------+------+
    |              |              |                 |
    +--------------+--------------+-----------------+
                   |
            +------v------+
            |  DynamoDB   |
            | Single-Table|
            |             |
            | CONTACT#    |
            | DEAL#       |
            | PIPELINE#   |
            | ACTIVITY#   |
            | WORKFLOW#   |
            | SEGMENT#    |
            +------+------+
                   |
            +------v------+
            |    SQS      |
            | Async Tasks |
            |             |
            | workflow-exec|
            | email-sync   |
            | bulk-msg     |
            | dedup-detect |
            +-------------+
```

### Flujo de Datos Principal

```
Vendedor                CRM API                 DynamoDB          WhatsApp/Email
   |                      |                       |                    |
   |-- POST /contacts --> |                       |                    |
   |                      |-- PutItem CONTACT# -->|                    |
   |                      |<-- OK ---------------|                    |
   |<-- 201 Created ------|                       |                    |
   |                      |                       |                    |
   |-- POST /deals ------>|                       |                    |
   |                      |-- PutItem DEAL# ----->|                    |
   |                      |-- Trigger workflow -->| SQS                |
   |                      |                       |-- Auto-send msg -->|
   |<-- 201 Created ------|                       |                    |
   |                      |                       |                    |
   |-- POST /activities ->|                       |                    |
   |                      |-- PutItem ACTIVITY# ->|                    |
   |                      |-- Log to timeline --->|                    |
   |<-- 201 Created ------|                       |                    |
```

### Estructura de Carpetas (covacha-crm)

```
covacha-crm/
├── src/
│   ├── crm/
│   │   ├── config/
│   │   │   ├── routes/
│   │   │   │   ├── contact_routes.py       # Blueprint contactos
│   │   │   │   ├── deal_routes.py          # Blueprint deals
│   │   │   │   ├── activity_routes.py      # Blueprint actividades
│   │   │   │   ├── pipeline_routes.py      # Blueprint pipelines
│   │   │   │   ├── workflow_routes.py      # Blueprint workflows
│   │   │   │   ├── segment_routes.py       # Blueprint segmentos
│   │   │   │   ├── report_routes.py        # Blueprint reportes
│   │   │   │   └── webhook_routes.py       # Blueprint webhooks CRM
│   │   │   └── settings.py
│   │   ├── models/
│   │   │   ├── contact.py                  # Modelo de contacto
│   │   │   ├── deal.py                     # Modelo de deal
│   │   │   ├── activity.py                 # Modelo de actividad
│   │   │   ├── pipeline.py                 # Modelo de pipeline/etapa
│   │   │   ├── workflow.py                 # Modelo de workflow
│   │   │   ├── segment.py                  # Modelo de segmento
│   │   │   └── custom_field.py             # Campos personalizables
│   │   ├── services/
│   │   │   ├── contact_service.py          # Logica de contactos
│   │   │   ├── deal_service.py             # Logica de deals
│   │   │   ├── activity_service.py         # Logica de actividades
│   │   │   ├── pipeline_service.py         # Logica de pipelines
│   │   │   ├── workflow_engine.py          # Motor de workflows
│   │   │   ├── segment_service.py          # Logica de segmentos
│   │   │   ├── dedup_service.py            # Deteccion de duplicados
│   │   │   ├── report_service.py           # Generacion de reportes
│   │   │   └── import_export_service.py    # Import/export masivo
│   │   ├── repositories/
│   │   │   ├── contact_repository.py
│   │   │   ├── deal_repository.py
│   │   │   ├── activity_repository.py
│   │   │   ├── pipeline_repository.py
│   │   │   ├── workflow_repository.py
│   │   │   └── segment_repository.py
│   │   └── integrations/
│   │       ├── whatsapp_integration.py     # Integracion covacha-botia
│   │       ├── email_integration.py        # Integracion covacha-notification
│   │       └── webhook_dispatcher.py       # Despacho webhooks CRM
│   └── app.py
├── tests/
│   ├── test_contact_service.py
│   ├── test_deal_service.py
│   ├── test_activity_service.py
│   ├── test_pipeline_service.py
│   ├── test_workflow_engine.py
│   ├── test_segment_service.py
│   ├── test_dedup_service.py
│   ├── test_report_service.py
│   └── test_import_export_service.py
├── requirements.txt
├── Procfile
└── README.md
```

---

## Modelo de Datos DynamoDB

### Single-Table Design

| Entidad | PK | SK | GSI1-PK | GSI1-SK |
|---------|----|----|---------|---------|
| Contacto | `TENANT#<tid>#ORG#<oid>` | `CONTACT#<cid>` | `CONTACT#<cid>` | `META` |
| Deal | `TENANT#<tid>#ORG#<oid>` | `DEAL#<did>` | `PIPELINE#<pid>` | `STAGE#<stage>#DEAL#<did>` |
| Actividad | `CONTACT#<cid>` | `ACTIVITY#<ts>#<aid>` | `DEAL#<did>` | `ACTIVITY#<ts>#<aid>` |
| Pipeline | `TENANT#<tid>#ORG#<oid>` | `PIPELINE#<pid>` | `PIPELINE#<pid>` | `META` |
| Etapa | `PIPELINE#<pid>` | `STAGE#<order>#<sid>` | - | - |
| Workflow | `TENANT#<tid>#ORG#<oid>` | `WORKFLOW#<wid>` | `WORKFLOW#<wid>` | `META` |
| WorkflowExec | `WORKFLOW#<wid>` | `EXEC#<ts>#<eid>` | - | - |
| Segmento | `TENANT#<tid>#ORG#<oid>` | `SEGMENT#<sid>` | `SEGMENT#<sid>` | `META` |
| ContactTag | `CONTACT#<cid>` | `TAG#<tag>` | `TAG#<tag>` | `TENANT#<tid>#ORG#<oid>` |
| CustomField | `TENANT#<tid>#ORG#<oid>` | `CFIELD#<entity>#<fid>` | - | - |
| TimelineEntry | `CONTACT#<cid>` | `TIMELINE#<ts>#<type>` | - | - |
| EmailThread | `CONTACT#<cid>` | `EMAIL#<ts>#<eid>` | `EMAIL#<eid>` | `META` |
| Webhook | `TENANT#<tid>#ORG#<oid>` | `WEBHOOK#<whid>` | - | - |
| APIKey | `TENANT#<tid>#ORG#<oid>` | `APIKEY#<kid>` | `APIKEY#<key_hash>` | `META` |

### GSIs Requeridos

| GSI | PK | SK | Proposito |
|-----|----|----|-----------|
| GSI1 | `gsi1_pk` | `gsi1_sk` | Buscar contacto por ID, deals por pipeline/stage, actividades por deal |
| GSI2 | `assigned_to` | `entity_type#created_at` | Buscar deals/actividades por vendedor asignado |
| GSI3 | `email` | `tenant_id#org_id` | Buscar contacto por email (dedup, email sync) |
| GSI4 | `phone` | `tenant_id#org_id` | Buscar contacto por telefono (WhatsApp linking) |

### Access Patterns Principales

| # | Patron | Uso |
|---|--------|-----|
| 1 | Listar contactos de una organizacion | `PK = TENANT#<tid>#ORG#<oid>, SK begins_with CONTACT#` |
| 2 | Ver timeline de un contacto | `PK = CONTACT#<cid>, SK begins_with TIMELINE#` |
| 3 | Listar deals por pipeline y etapa | `GSI1: PK = PIPELINE#<pid>, SK begins_with STAGE#<stage>` |
| 4 | Actividades de un deal | `GSI1: PK = DEAL#<did>, SK begins_with ACTIVITY#` |
| 5 | Deals asignados a un vendedor | `GSI2: PK = <user_id>, SK begins_with DEAL#` |
| 6 | Buscar contacto por email | `GSI3: PK = <email>` |
| 7 | Buscar contacto por telefono | `GSI4: PK = <phone>` |
| 8 | Tags de un contacto | `PK = CONTACT#<cid>, SK begins_with TAG#` |
| 9 | Contactos por tag | `GSI1: PK = TAG#<tag>, SK = TENANT#<tid>#ORG#<oid>` |
| 10 | Ejecuciones de un workflow | `PK = WORKFLOW#<wid>, SK begins_with EXEC#` |

---

## Mapa de Epicas

| ID | Epica | Complejidad | Sprint Sugerido | Dependencias |
|----|-------|-------------|-----------------|--------------|
| EP-CR-001 | Gestion de Contactos | XL | 1-3 | Ninguna |
| EP-CR-002 | Pipeline de Ventas (Deals) | XL | 2-4 | EP-CR-001 |
| EP-CR-003 | Actividades y Tareas | L | 3-5 | EP-CR-001, EP-CR-002 |
| EP-CR-004 | Automatizaciones (Workflows) | XL | 5-7 | EP-CR-001, EP-CR-002, EP-CR-003 |
| EP-CR-005 | Integracion WhatsApp | L | 4-6 | EP-CR-001 |
| EP-CR-006 | Reportes y Analytics CRM | L | 6-8 | EP-CR-001, EP-CR-002, EP-CR-003 |
| EP-CR-007 | Email Integration | L | 5-7 | EP-CR-001, EP-CR-003 |
| EP-CR-008 | API y Webhooks CRM | L | 7-9 | EP-CR-001, EP-CR-002 |

**Totales:**
- 8 epicas
- 48 user stories (US-CR-001 a US-CR-048)
- Estimacion total: ~160-200 dev-days

---

## Epicas Detalladas

---

### EP-CR-001: Gestion de Contactos

**Descripcion:**
CRUD completo de contactos con campos personalizables, tags, segmentos, importacion masiva, busqueda avanzada, merge de duplicados, y timeline de interacciones. Cada contacto puede tener multiples canales de comunicacion (telefono, email, WhatsApp) y pertenece a un tenant+organizacion. Es la base sobre la que se construyen todas las demas epicas.

**User Stories:**
- US-CR-001, US-CR-002, US-CR-003, US-CR-004, US-CR-005, US-CR-006, US-CR-007, US-CR-008

**Criterios de Aceptacion de la Epica:**
- [ ] CRUD completo de contactos con validaciones de datos
- [ ] Campos personalizables por organizacion (texto, numero, fecha, select, multi-select)
- [ ] Sistema de tags con creacion dinamica y busqueda por tag
- [ ] Segmentos dinamicos basados en filtros (tags, campos, fechas, actividad)
- [ ] Importacion masiva desde CSV y Excel con mapeo de columnas
- [ ] Busqueda avanzada con filtros combinados (AND/OR)
- [ ] Deteccion de duplicados por email, telefono o nombre similar
- [ ] Merge de contactos duplicados preservando historial completo
- [ ] Timeline de interacciones (llamadas, emails, WhatsApp, notas, deals)
- [ ] Multi-canal: telefono(s), email(s), WhatsApp por contacto
- [ ] Paginacion server-side con cursor-based pagination
- [ ] Multi-tenant: cada organizacion ve solo sus contactos
- [ ] API REST completa con documentacion OpenAPI
- [ ] Tests >= 98% coverage

**Dependencias:** Ninguna (puede empezar de inmediato)

**Complejidad:** XL (8 user stories, modelado de dominio fundacional)

**Repositorios:** `covacha-crm`, `covacha-libs`

---

### EP-CR-002: Pipeline de Ventas (Deals)

**Descripcion:**
Sistema de gestion de oportunidades de venta (deals) con pipelines configurables por organizacion. Cada pipeline tiene etapas ordenadas con probabilidad de cierre. Los deals se mueven entre etapas (drag-and-drop en frontend, PATCH en API). Incluye valor estimado, fecha de cierre esperada, asignacion a vendedor, y metricas de conversion por etapa.

**User Stories:**
- US-CR-009, US-CR-010, US-CR-011, US-CR-012, US-CR-013, US-CR-014

**Criterios de Aceptacion de la Epica:**
- [ ] CRUD de pipelines con etapas configurables (nombre, orden, probabilidad, color)
- [ ] CRUD de deals con valor, moneda, fecha cierre esperada, contacto asociado
- [ ] Mover deal entre etapas con validacion de transiciones permitidas
- [ ] Asignacion de deal a vendedor con reasignacion
- [ ] Multiples pipelines por organizacion (ventas, renovaciones, upsell)
- [ ] Metricas por pipeline: total value, weighted value, conversion rate por etapa
- [ ] Estados de deal: OPEN, WON, LOST, ABANDONED
- [ ] Razon de perdida obligatoria al marcar deal como LOST
- [ ] Historial de cambios de etapa con timestamps y usuario
- [ ] Filtros: por pipeline, etapa, vendedor, rango de valor, fecha
- [ ] Vista Kanban (API preparada con agrupacion por etapa)
- [ ] Tests >= 98% coverage

**Dependencias:** EP-CR-001 (un deal se asocia a un contacto)

**Complejidad:** XL (6 user stories, logica de pipeline configurable)

**Repositorios:** `covacha-crm`

---

### EP-CR-003: Actividades y Tareas

**Descripcion:**
Sistema de actividades vinculadas a contactos y/o deals. Los vendedores registran llamadas, reuniones, emails, mensajes de WhatsApp y tareas pendientes. Las actividades se muestran en el timeline del contacto y del deal. Incluye recordatorios automaticos, calendario de actividades, y asignacion a equipo.

**User Stories:**
- US-CR-015, US-CR-016, US-CR-017, US-CR-018, US-CR-019

**Criterios de Aceptacion de la Epica:**
- [ ] CRUD de actividades con tipos: CALL, MEETING, EMAIL, WHATSAPP, TASK, NOTE
- [ ] Actividad vinculada a contacto y/o deal (al menos uno obligatorio)
- [ ] Estados de tarea: PENDING, IN_PROGRESS, COMPLETED, CANCELLED
- [ ] Fecha de vencimiento con recordatorios automaticos (15 min, 1 hora, 1 dia antes)
- [ ] Asignacion a usuario del equipo
- [ ] Actividades se muestran en timeline de contacto y deal
- [ ] Calendario de actividades por vendedor y equipo
- [ ] Registro automatico de actividad al enviar email o WhatsApp
- [ ] Notas de texto libre asociadas a actividades
- [ ] Duracion para llamadas y reuniones
- [ ] Filtros: por tipo, estado, asignado, rango de fechas
- [ ] Tests >= 98% coverage

**Dependencias:** EP-CR-001 (contactos), EP-CR-002 (deals)

**Complejidad:** L (5 user stories, integracion con timeline)

**Repositorios:** `covacha-crm`

---

### EP-CR-004: Automatizaciones (Workflows)

**Descripcion:**
Motor de automatizaciones que permite al Administrador CRM definir workflows con triggers, condiciones y acciones. Cuando se cumple un trigger (nuevo contacto, cambio de etapa, inactividad, fecha), el motor evalua condiciones y ejecuta acciones automaticamente (enviar email, enviar WhatsApp, crear tarea, mover deal, notificar equipo). Incluye historial de ejecuciones y logs de cada paso.

**User Stories:**
- US-CR-020, US-CR-021, US-CR-022, US-CR-023, US-CR-024, US-CR-025

**Criterios de Aceptacion de la Epica:**
- [ ] CRUD de workflows con nombre, descripcion, estado (ACTIVE, PAUSED, DRAFT)
- [ ] Triggers soportados: CONTACT_CREATED, CONTACT_UPDATED, DEAL_STAGE_CHANGED, DEAL_CREATED, DEAL_WON, DEAL_LOST, ACTIVITY_OVERDUE, CONTACT_INACTIVE_DAYS, SCHEDULED_DATE
- [ ] Condiciones con operadores: equals, not_equals, contains, greater_than, less_than, is_empty, is_not_empty
- [ ] Condiciones con logica AND/OR y branches (if/else)
- [ ] Acciones soportadas: SEND_EMAIL, SEND_WHATSAPP, CREATE_TASK, MOVE_DEAL_STAGE, ASSIGN_TO, ADD_TAG, REMOVE_TAG, NOTIFY_USER, WAIT_DELAY, HTTP_WEBHOOK
- [ ] Ejecucion asincrona via SQS (no bloquea la operacion original)
- [ ] Historial de ejecuciones con resultado por paso (SUCCESS, FAILED, SKIPPED)
- [ ] Limites configurables: max workflows activos por org, max ejecuciones/dia
- [ ] Idempotencia: mismo evento no dispara el workflow 2 veces
- [ ] Logs detallados para debugging de workflows
- [ ] Tests >= 98% coverage

**Dependencias:** EP-CR-001 (contactos), EP-CR-002 (deals), EP-CR-003 (actividades para crear tareas)

**Complejidad:** XL (6 user stories, motor de reglas, ejecucion asincrona)

**Repositorios:** `covacha-crm`, `covacha-libs` (SQS patterns)

---

### EP-CR-005: Integracion WhatsApp

**Descripcion:**
Integracion bidireccional con WhatsApp via `covacha-botia`. Los vendedores pueden enviar mensajes a contactos directamente desde el CRM, usar templates pre-aprobados, y ver el historial completo de conversaciones en el timeline del contacto. Incluye envio masivo a segmentos y vinculacion automatica contacto-telefono-WhatsApp.

**User Stories:**
- US-CR-026, US-CR-027, US-CR-028, US-CR-029, US-CR-030

**Criterios de Aceptacion de la Epica:**
- [ ] Envio de mensaje WhatsApp individual desde perfil de contacto
- [ ] Templates pre-aprobados de WhatsApp con variables dinamicas (nombre, empresa, deal)
- [ ] Historial de conversaciones WhatsApp en timeline del contacto
- [ ] Envio masivo (bulk) a segmentos de contactos con throttling
- [ ] Respuestas rapidas (canned responses) personalizables por organizacion
- [ ] Vinculacion automatica: mensaje entrante de WhatsApp se asocia al contacto por telefono
- [ ] Creacion automatica de contacto si el telefono no existe (configurable)
- [ ] Actividad tipo WHATSAPP se crea automaticamente al enviar/recibir
- [ ] Status de delivery del mensaje (sent, delivered, read, failed)
- [ ] Rate limiting para proteger la cuenta de WhatsApp Business
- [ ] Tests >= 98% coverage

**Dependencias:** EP-CR-001 (contactos con telefono)

**Complejidad:** L (5 user stories, integracion con covacha-botia)

**Repositorios:** `covacha-crm`, `covacha-botia`

---

### EP-CR-006: Reportes y Analytics CRM

**Descripcion:**
Dashboard de metricas de ventas y rendimiento del equipo comercial. Incluye pipeline value total y ponderado, conversion rate por etapa, ciclo de venta promedio, win rate, forecast de ingresos, y reportes por vendedor/equipo. Los reportes se pueden personalizar, exportar en PDF y CSV, y programar para envio periodico.

**User Stories:**
- US-CR-031, US-CR-032, US-CR-033, US-CR-034, US-CR-035, US-CR-036

**Criterios de Aceptacion de la Epica:**
- [ ] Dashboard con KPIs: pipeline value, weighted value, deals abiertos, win rate, ciclo promedio
- [ ] Metricas por etapa: deals en cada etapa, conversion rate etapa a etapa, tiempo promedio por etapa
- [ ] Reporte por vendedor: deals asignados, won/lost, valor cerrado, actividades realizadas
- [ ] Reporte por equipo: rendimiento comparativo entre vendedores
- [ ] Forecast de ingresos basado en pipeline value ponderado + historico de conversion
- [ ] Filtros de periodo: hoy, esta semana, este mes, trimestre, ano, rango personalizado
- [ ] Reportes personalizados con seleccion de metricas y agrupaciones
- [ ] Exportacion en PDF y CSV
- [ ] Programacion de reportes periodicos (diario, semanal, mensual) por email
- [ ] Cache de metricas para respuesta rapida (< 500ms)
- [ ] Tests >= 98% coverage

**Dependencias:** EP-CR-001 (contactos), EP-CR-002 (deals), EP-CR-003 (actividades)

**Complejidad:** L (6 user stories, agregaciones DynamoDB, cache)

**Repositorios:** `covacha-crm`, `covacha-notification` (envio de reportes)

---

### EP-CR-007: Email Integration

**Descripcion:**
Sincronizacion bidireccional de emails con el CRM. Los emails enviados y recibidos se vinculan automaticamente al contacto correspondiente por direccion de email. Incluye templates de email con variables, secuencias automaticas (drip campaigns), y tracking de opens/clicks. La sincronizacion se hace via IMAP/SMTP a traves de `covacha-notification`.

**User Stories:**
- US-CR-037, US-CR-038, US-CR-039, US-CR-040, US-CR-041

**Criterios de Aceptacion de la Epica:**
- [ ] Configuracion de cuenta email por organizacion (IMAP/SMTP credentials encriptadas)
- [ ] Sync bidireccional: emails enviados y recibidos aparecen en timeline del contacto
- [ ] Vinculacion automatica por email del contacto (GSI3)
- [ ] Templates de email con variables dinamicas ({{nombre}}, {{empresa}}, {{deal_name}})
- [ ] Secuencias de email automaticas: serie de emails con delays configurables
- [ ] Cancelacion automatica de secuencia si contacto responde
- [ ] Tracking de opens y clicks via pixel de tracking y link wrapping
- [ ] Metricas de email: open rate, click rate, reply rate, bounce rate
- [ ] Actividad tipo EMAIL creada automaticamente al enviar/recibir
- [ ] Unsubscribe automatico respetando preferencias del contacto
- [ ] Tests >= 98% coverage

**Dependencias:** EP-CR-001 (contactos con email), EP-CR-003 (actividades para registro automatico)

**Complejidad:** L (5 user stories, integracion IMAP/SMTP, tracking)

**Repositorios:** `covacha-crm`, `covacha-notification`

---

### EP-CR-008: API y Webhooks CRM

**Descripcion:**
API REST publica documentada para integraciones externas y webhooks configurables que notifican a sistemas externos cuando ocurren eventos en el CRM. Incluye generacion de API keys por organizacion, rate limiting, SDK para `covacha-libs`, y documentacion OpenAPI completa. Los webhooks permiten a los tenants conectar el CRM con sus propios sistemas.

**User Stories:**
- US-CR-042, US-CR-043, US-CR-044, US-CR-045, US-CR-046, US-CR-047, US-CR-048

**Criterios de Aceptacion de la Epica:**
- [ ] API REST publica con versionado: `/api/v1/crm/...`
- [ ] Autenticacion via API key (Bearer token) con permisos granulares
- [ ] CRUD de API keys por organizacion con revocacion
- [ ] Rate limiting configurable por API key (default: 100 req/min)
- [ ] Webhooks configurables: nuevo contacto, deal creado, deal etapa cambiada, deal ganado, deal perdido, actividad creada
- [ ] Webhook con firma HMAC para verificacion de integridad
- [ ] Reintentos automaticos de webhook (3 intentos con backoff exponencial)
- [ ] Dead letter queue para webhooks fallidos
- [ ] SDK Python para covacha-libs (CRMClient con metodos tipados)
- [ ] Documentacion OpenAPI 3.0 autogenerada y servida en `/api/v1/crm/docs`
- [ ] Logs de uso de API por key (requests, errors, latency)
- [ ] Tests >= 98% coverage

**Dependencias:** EP-CR-001 (contactos), EP-CR-002 (deals)

**Complejidad:** L (7 user stories, API publica, webhooks, SDK)

**Repositorios:** `covacha-crm`, `covacha-libs` (SDK)

---

## User Stories Detalladas

---

### EP-CR-001: Gestion de Contactos

---

#### US-CR-001: CRUD basico de contactos

**Como** Vendedor
**Quiero** crear, ver, editar y eliminar contactos con sus datos basicos
**Para** mantener una base de datos organizada de mis prospectos y clientes

**Criterios de Aceptacion:**
- [ ] Crear contacto con: nombre, apellido, email, telefono, empresa, cargo, notas
- [ ] Validacion de email unico por organizacion (warn, no block)
- [ ] Validacion de telefono en formato E.164 (+52XXXXXXXXXX)
- [ ] Editar cualquier campo del contacto
- [ ] Eliminar contacto (soft delete: status = DELETED, no aparece en listados)
- [ ] Ver detalle de contacto con toda su informacion
- [ ] Listar contactos con paginacion cursor-based (50 por pagina default)
- [ ] Ordenar por: nombre, fecha de creacion, ultima actividad
- [ ] Multi-tenant: el vendedor solo ve contactos de su organizacion

**Tareas Tecnicas:**
- [ ] Modelo `Contact` en `models/contact.py` con validaciones
- [ ] `ContactRepository` con operaciones DynamoDB (PutItem, GetItem, UpdateItem, Query)
- [ ] `ContactService` con logica de negocio (validacion, soft delete, paginacion)
- [ ] Blueprint `contact_routes.py` con endpoints REST
- [ ] Endpoints: `POST /api/v1/crm/contacts`, `GET /api/v1/crm/contacts`, `GET /api/v1/crm/contacts/<id>`, `PUT /api/v1/crm/contacts/<id>`, `DELETE /api/v1/crm/contacts/<id>`
- [ ] Tests: 8+ unit tests (happy path, validaciones, edge cases)

**Estimacion:** 5 dev-days

---

#### US-CR-002: Campos personalizables por organizacion

**Como** Administrador CRM
**Quiero** definir campos personalizados para los contactos de mi organizacion
**Para** capturar informacion especifica de mi industria que no esta en los campos estandar

**Criterios de Aceptacion:**
- [ ] Crear campo personalizado con: nombre, tipo (TEXT, NUMBER, DATE, SELECT, MULTI_SELECT), obligatorio (si/no)
- [ ] Tipos SELECT y MULTI_SELECT permiten definir opciones validas
- [ ] Maximo 50 campos personalizados por organizacion
- [ ] Los campos personalizados se almacenan en `custom_fields` del contacto (schema flexible)
- [ ] Validacion de tipo de dato al guardar valores
- [ ] Editar y eliminar campos personalizados (eliminar no borra datos existentes)
- [ ] Los campos personalizados se incluyen en busqueda avanzada

**Tareas Tecnicas:**
- [ ] Modelo `CustomField` en `models/custom_field.py`
- [ ] Endpoint CRUD: `POST/GET/PUT/DELETE /api/v1/crm/custom-fields`
- [ ] Validacion dinamica en `ContactService` al crear/editar contactos
- [ ] Tests: 6+ unit tests

**Estimacion:** 3 dev-days

---

#### US-CR-003: Tags y sistema de etiquetado

**Como** Vendedor
**Quiero** agregar tags a los contactos y filtrar por tags
**Para** categorizar rapidamente mis contactos (VIP, prospecto caliente, referido, etc.)

**Criterios de Aceptacion:**
- [ ] Agregar 1 o mas tags a un contacto (string libre, lowercase, sin espacios)
- [ ] Remover tags de un contacto
- [ ] Listar todos los tags existentes en la organizacion (para autocompletado)
- [ ] Filtrar contactos por 1 o mas tags (AND: todos los tags, OR: cualquier tag)
- [ ] Conteo de contactos por tag
- [ ] Busqueda parcial de tags (autocomplete con prefix match)
- [ ] Tags se persisten como items independientes para busqueda eficiente (GSI)

**Tareas Tecnicas:**
- [ ] Items `ContactTag` en DynamoDB: `PK = CONTACT#<cid>, SK = TAG#<tag>`
- [ ] GSI para buscar contactos por tag: `PK = TAG#<tag>, SK = TENANT#ORG#`
- [ ] Endpoints: `POST /api/v1/crm/contacts/<id>/tags`, `DELETE /api/v1/crm/contacts/<id>/tags/<tag>`, `GET /api/v1/crm/tags`
- [ ] Tests: 5+ unit tests

**Estimacion:** 3 dev-days

---

#### US-CR-004: Segmentos dinamicos

**Como** Gerente de Ventas
**Quiero** crear segmentos de contactos basados en filtros dinamicos
**Para** agrupar contactos automaticamente segun criterios de negocio (industria, tag, valor de deals, inactividad)

**Criterios de Aceptacion:**
- [ ] Crear segmento con nombre y definicion de filtros (JSON de condiciones)
- [ ] Filtros soportados: tag, campo estandar, campo personalizado, tiene deal activo, ultimo contacto > N dias
- [ ] Logica AND/OR entre condiciones
- [ ] El segmento se recalcula dinamicamente al consultar (no se guarda lista fija)
- [ ] Conteo de contactos en el segmento
- [ ] Listar contactos del segmento con paginacion
- [ ] Segmentos se usan para envio masivo de WhatsApp (EP-CR-005) y email (EP-CR-007)

**Tareas Tecnicas:**
- [ ] Modelo `Segment` en `models/segment.py` con `filter_definition` (JSON)
- [ ] `SegmentService` que traduce filtros a queries DynamoDB/scan con filtros
- [ ] Endpoints: `POST/GET/PUT/DELETE /api/v1/crm/segments`, `GET /api/v1/crm/segments/<id>/contacts`
- [ ] Tests: 6+ unit tests (combinaciones de filtros)

**Estimacion:** 5 dev-days

---

#### US-CR-005: Importacion masiva de contactos

**Como** Administrador CRM
**Quiero** importar contactos masivamente desde un archivo CSV o Excel
**Para** migrar datos existentes de hojas de calculo o sistemas anteriores al CRM

**Criterios de Aceptacion:**
- [ ] Upload de archivo CSV o Excel (.xlsx) hasta 10MB
- [ ] Vista previa de las primeras 5 filas antes de importar
- [ ] Mapeo de columnas del archivo a campos del CRM (drag-and-drop o select)
- [ ] Deteccion automatica de columnas por nombre (nombre, email, telefono)
- [ ] Validacion pre-import: emails invalidos, telefonos malformados, campos obligatorios vacios
- [ ] Reporte de errores por fila (fila X: email invalido)
- [ ] Importacion en background (async via SQS) con progreso consultable
- [ ] Opcion de skip o sobrescribir contactos existentes (match por email)
- [ ] Maximo 10,000 contactos por importacion
- [ ] Tags opcionales aplicados a todos los contactos importados
- [ ] Notificacion al completar la importacion

**Tareas Tecnicas:**
- [ ] `ImportExportService` en `services/import_export_service.py`
- [ ] Parser CSV/Excel con `pandas` o `openpyxl`
- [ ] Job SQS para procesamiento async con batch writes a DynamoDB
- [ ] Endpoints: `POST /api/v1/crm/contacts/import` (upload), `GET /api/v1/crm/contacts/import/<job_id>` (status)
- [ ] Tests: 6+ unit tests (CSV valido, invalido, duplicados, limite)

**Estimacion:** 5 dev-days

---

#### US-CR-006: Busqueda avanzada con filtros

**Como** Vendedor
**Quiero** buscar contactos usando filtros combinados (nombre, email, tag, campo personalizado, fecha)
**Para** encontrar rapidamente el contacto que necesito entre miles de registros

**Criterios de Aceptacion:**
- [ ] Busqueda por texto libre (nombre, email, empresa, notas) con match parcial
- [ ] Filtros combinables: tag, campo personalizado, fecha de creacion, tiene deal activo
- [ ] Operadores: contiene, igual, mayor que, menor que, esta vacio, no esta vacio
- [ ] Logica AND entre filtros (todos deben cumplirse)
- [ ] Resultados paginados con total count
- [ ] Orden por relevancia o por campo especifico
- [ ] Response time < 500ms para organizaciones con hasta 50,000 contactos

**Tareas Tecnicas:**
- [ ] Endpoint: `POST /api/v1/crm/contacts/search` con body de filtros
- [ ] Query builder que traduce filtros a FilterExpression de DynamoDB
- [ ] Para texto libre: usar GSI3/GSI4 o scan con FilterExpression
- [ ] Considerar ElasticSearch/OpenSearch si DynamoDB scan no cumple latencia
- [ ] Tests: 5+ unit tests

**Estimacion:** 4 dev-days

---

#### US-CR-007: Deteccion y merge de contactos duplicados

**Como** Administrador CRM
**Quiero** que el sistema detecte contactos duplicados y me permita fusionarlos
**Para** mantener la base de datos limpia y evitar comunicaciones redundantes

**Criterios de Aceptacion:**
- [ ] Deteccion automatica al crear contacto: si email o telefono ya existen, mostrar warning
- [ ] Endpoint de busqueda de duplicados: analiza toda la base y sugiere posibles duplicados
- [ ] Criterios de match: email exacto, telefono exacto, nombre similar (Levenshtein distance < 3)
- [ ] Vista de comparacion lado a lado de 2 contactos candidatos a merge
- [ ] Merge: seleccionar cual campo prevalece (master vs duplicado)
- [ ] Al hacer merge: el contacto duplicado se elimina, sus deals, actividades y timeline se transfieren al master
- [ ] Historial de merges realizados con undo (dentro de 24 horas)
- [ ] Job de deteccion periodico (semanal) con notificacion al admin

**Tareas Tecnicas:**
- [ ] `DedupService` en `services/dedup_service.py`
- [ ] Algoritmo de similarity matching (email exact, phone exact, fuzzy name)
- [ ] Endpoint merge: `POST /api/v1/crm/contacts/<master_id>/merge/<duplicate_id>`
- [ ] Endpoint duplicados: `GET /api/v1/crm/contacts/duplicates`
- [ ] Job SQS para deteccion periodica
- [ ] Tests: 7+ unit tests (exact match, fuzzy, merge, undo)

**Estimacion:** 5 dev-days

---

#### US-CR-008: Timeline de interacciones por contacto

**Como** Vendedor
**Quiero** ver un timeline cronologico con todas las interacciones de un contacto
**Para** tener contexto completo antes de una llamada o reunion

**Criterios de Aceptacion:**
- [ ] Timeline muestra: notas, llamadas, reuniones, emails, WhatsApp, cambios de deal, tags agregados/removidos
- [ ] Orden cronologico inverso (mas reciente primero)
- [ ] Paginacion infinite scroll (cursor-based, 20 entries por pagina)
- [ ] Cada entry muestra: tipo (icono), fecha/hora, usuario que realizo la accion, resumen
- [ ] Agregar nota rapida al timeline directamente
- [ ] Filtrar timeline por tipo de interaccion
- [ ] Timeline se alimenta automaticamente de actividades, emails y WhatsApp

**Tareas Tecnicas:**
- [ ] Items `TimelineEntry` en DynamoDB: `PK = CONTACT#<cid>, SK = TIMELINE#<ts>#<type>`
- [ ] `TimelineService` que agrega entries automaticamente cuando se crean actividades/emails/WhatsApp
- [ ] Endpoint: `GET /api/v1/crm/contacts/<id>/timeline?cursor=X&type=Y`
- [ ] Endpoint: `POST /api/v1/crm/contacts/<id>/timeline/notes` (nota rapida)
- [ ] Tests: 5+ unit tests

**Estimacion:** 4 dev-days

---

### EP-CR-002: Pipeline de Ventas (Deals)

---

#### US-CR-009: CRUD de pipelines y etapas

**Como** Administrador CRM
**Quiero** crear y configurar pipelines de ventas con etapas personalizadas
**Para** modelar los diferentes procesos de venta de mi organizacion

**Criterios de Aceptacion:**
- [ ] Crear pipeline con nombre y descripcion
- [ ] Agregar etapas al pipeline con: nombre, orden, probabilidad de cierre (0-100%), color
- [ ] Etapas default al crear pipeline: Prospecto (10%), Calificado (25%), Propuesta (50%), Negociacion (75%), Ganado (100%), Perdido (0%)
- [ ] Reordenar etapas (drag-and-drop en frontend, PATCH orden en API)
- [ ] Maximo 5 pipelines por organizacion, 15 etapas por pipeline
- [ ] Editar nombre/probabilidad/color de etapa existente
- [ ] No se puede eliminar etapa si tiene deals activos (mover deals primero)
- [ ] Pipeline default marcado (el que se usa si no se especifica)

**Tareas Tecnicas:**
- [ ] Modelo `Pipeline` y `PipelineStage` en `models/pipeline.py`
- [ ] `PipelineRepository` y `PipelineService`
- [ ] Endpoints: `POST/GET/PUT/DELETE /api/v1/crm/pipelines`, `POST/PUT/DELETE /api/v1/crm/pipelines/<id>/stages`
- [ ] Tests: 6+ unit tests

**Estimacion:** 4 dev-days

---

#### US-CR-010: CRUD de deals con valor y fechas

**Como** Vendedor
**Quiero** crear deals asociados a un contacto y pipeline con valor estimado
**Para** dar seguimiento a mis oportunidades de venta

**Criterios de Aceptacion:**
- [ ] Crear deal con: nombre, contacto asociado, pipeline, etapa, valor estimado, moneda (MXN, USD), fecha cierre esperada
- [ ] Un deal pertenece a exactamente 1 pipeline y 1 etapa
- [ ] Un contacto puede tener multiples deals
- [ ] Editar cualquier campo del deal
- [ ] Eliminar deal (soft delete)
- [ ] Listar deals con filtros: pipeline, etapa, vendedor, rango de valor, fecha
- [ ] Paginacion cursor-based
- [ ] Al crear deal, se agrega entrada al timeline del contacto

**Tareas Tecnicas:**
- [ ] Modelo `Deal` en `models/deal.py`
- [ ] `DealRepository` con GSI1 para query por pipeline+stage
- [ ] `DealService` con validaciones
- [ ] Endpoints: `POST/GET/PUT/DELETE /api/v1/crm/deals`
- [ ] Tests: 6+ unit tests

**Estimacion:** 4 dev-days

---

#### US-CR-011: Mover deals entre etapas del pipeline

**Como** Vendedor
**Quiero** mover un deal de una etapa a otra en el pipeline
**Para** reflejar el avance real de la negociacion

**Criterios de Aceptacion:**
- [ ] Cambiar etapa del deal via `PATCH /api/v1/crm/deals/<id>/stage`
- [ ] Registrar historial de cambios: etapa anterior, etapa nueva, fecha, usuario
- [ ] Recalcular probabilidad de cierre segun la nueva etapa
- [ ] Al mover a etapa "Ganado": deal status = WON, fecha de cierre real = hoy
- [ ] Al mover a etapa "Perdido": deal status = LOST, requiere razon de perdida
- [ ] Validacion: no se puede mover un deal ya WON o LOST (reabrir primero)
- [ ] Actividad automatica en timeline: "Deal movido de X a Y"
- [ ] Trigger para workflows (DEAL_STAGE_CHANGED)

**Tareas Tecnicas:**
- [ ] Metodo `change_stage()` en `DealService` con historial
- [ ] Campo `stage_history: list[dict]` en modelo Deal
- [ ] Endpoint: `PATCH /api/v1/crm/deals/<id>/stage` con body `{stage_id, loss_reason?}`
- [ ] Emitir evento SQS para workflows
- [ ] Tests: 7+ unit tests (avance, retroceso, won, lost, validaciones)

**Estimacion:** 4 dev-days

---

#### US-CR-012: Asignacion de deals a vendedores

**Como** Gerente de Ventas
**Quiero** asignar y reasignar deals a los vendedores de mi equipo
**Para** distribuir las oportunidades de venta equitativamente

**Criterios de Aceptacion:**
- [ ] Asignar deal a un usuario del equipo al crearlo
- [ ] Reasignar deal a otro vendedor (cambiar `assigned_to`)
- [ ] Historial de reasignaciones (quien, cuando, de quien a quien)
- [ ] Listar deals por vendedor asignado (GSI2)
- [ ] Notificacion al vendedor cuando se le asigna un deal nuevo
- [ ] El vendedor original puede ver el deal despues de reasignacion (read-only)
- [ ] Vista de carga de trabajo: cuantos deals tiene cada vendedor

**Tareas Tecnicas:**
- [ ] GSI2 en DynamoDB: `PK = assigned_to, SK = DEAL#created_at`
- [ ] Endpoint: `PATCH /api/v1/crm/deals/<id>/assign` con body `{assigned_to}`
- [ ] Endpoint: `GET /api/v1/crm/deals?assigned_to=<user_id>`
- [ ] Endpoint: `GET /api/v1/crm/team/workload` (conteo de deals por vendedor)
- [ ] Tests: 5+ unit tests

**Estimacion:** 3 dev-days

---

#### US-CR-013: Metricas de pipeline en tiempo real

**Como** Gerente de Ventas
**Quiero** ver metricas del pipeline en tiempo real (valor total, ponderado, conversion)
**Para** tomar decisiones informadas sobre la estrategia comercial

**Criterios de Aceptacion:**
- [ ] Valor total del pipeline: suma de todos los deals OPEN
- [ ] Valor ponderado: suma de (valor * probabilidad) de cada deal OPEN
- [ ] Deals por etapa: conteo y valor por cada etapa
- [ ] Conversion rate por etapa: % de deals que avanzan de etapa N a etapa N+1
- [ ] Tiempo promedio en cada etapa (dias)
- [ ] Metricas filtradas por: pipeline, vendedor, periodo
- [ ] Response time < 500ms (usar cache si es necesario)

**Tareas Tecnicas:**
- [ ] Endpoint: `GET /api/v1/crm/pipelines/<id>/metrics?from=X&to=Y&assigned_to=Z`
- [ ] Calculos de agregacion: scan deals del pipeline, agrupar por stage
- [ ] Cache con TTL de 5 minutos para metricas frecuentes
- [ ] Tests: 5+ unit tests (metricas correctas, filtros, cache)

**Estimacion:** 4 dev-days

---

#### US-CR-014: Vista Kanban (datos API)

**Como** Vendedor
**Quiero** que la API me devuelva los deals agrupados por etapa del pipeline
**Para** que el frontend pueda renderizar un tablero Kanban

**Criterios de Aceptacion:**
- [ ] Endpoint que retorna deals agrupados por etapa: `{stages: [{id, name, deals: [...]}]}`
- [ ] Cada deal incluye: id, nombre, valor, contacto (nombre + avatar), assigned_to, dias en etapa
- [ ] Ordenar deals dentro de cada etapa por: valor descendente (default) o fecha
- [ ] Paginacion por etapa (max 50 deals por etapa, cursor para cargar mas)
- [ ] Filtros opcionales: assigned_to, rango de valor, fecha cierre
- [ ] Incluir conteo total y valor total por etapa en la respuesta

**Tareas Tecnicas:**
- [ ] Endpoint: `GET /api/v1/crm/pipelines/<id>/kanban?assigned_to=X`
- [ ] Query eficiente: GSI1 con `PK = PIPELINE#<pid>, SK begins_with STAGE#<stage>`
- [ ] Serializer optimizado (solo campos necesarios para Kanban)
- [ ] Tests: 4+ unit tests

**Estimacion:** 3 dev-days

---

### EP-CR-003: Actividades y Tareas

---

#### US-CR-015: CRUD de actividades con tipos

**Como** Vendedor
**Quiero** registrar actividades de diferentes tipos vinculadas a contactos y deals
**Para** mantener un registro completo de mis interacciones comerciales

**Criterios de Aceptacion:**
- [ ] Crear actividad con: tipo (CALL, MEETING, EMAIL, WHATSAPP, TASK, NOTE), titulo, descripcion, contacto, deal (opcional)
- [ ] Campos por tipo: CALL/MEETING: duracion, resultado; TASK: fecha vencimiento, prioridad; NOTE: contenido markdown
- [ ] Editar y eliminar actividades
- [ ] Listar actividades con filtros: tipo, contacto, deal, asignado, rango de fechas
- [ ] Al crear actividad, automaticamente se agrega al timeline del contacto y del deal
- [ ] Paginacion cursor-based

**Tareas Tecnicas:**
- [ ] Modelo `Activity` en `models/activity.py` con tipos enum
- [ ] `ActivityRepository` con query por contacto (PK) y por deal (GSI1)
- [ ] `ActivityService` con validacion de tipo y creacion de timeline entry
- [ ] Endpoints: `POST/GET/PUT/DELETE /api/v1/crm/activities`
- [ ] Tests: 6+ unit tests

**Estimacion:** 4 dev-days

---

#### US-CR-016: Tareas con vencimiento y prioridad

**Como** Vendedor
**Quiero** crear tareas con fecha de vencimiento, prioridad y estado
**Para** organizar mi trabajo diario y no olvidar follow-ups importantes

**Criterios de Aceptacion:**
- [ ] Tarea es un tipo especial de actividad (type = TASK) con campos adicionales
- [ ] Campos: fecha de vencimiento, prioridad (LOW, MEDIUM, HIGH, URGENT), estado (PENDING, IN_PROGRESS, COMPLETED, CANCELLED)
- [ ] Listar "mis tareas pendientes" ordenadas por vencimiento y prioridad
- [ ] Tareas vencidas se resaltan (campo `is_overdue` calculado)
- [ ] Cambiar estado de la tarea
- [ ] Conteo de tareas por estado para badge en UI

**Tareas Tecnicas:**
- [ ] Campos adicionales en modelo `Activity` cuando `type = TASK`
- [ ] Endpoint: `GET /api/v1/crm/activities/tasks?status=PENDING&assigned_to=me`
- [ ] Filtro `is_overdue` calculado en query time
- [ ] Endpoint: `PATCH /api/v1/crm/activities/<id>/status` con body `{status}`
- [ ] Tests: 5+ unit tests

**Estimacion:** 3 dev-days

---

#### US-CR-017: Recordatorios automaticos de actividades

**Como** Vendedor
**Quiero** recibir recordatorios antes de que venzan mis tareas y actividades programadas
**Para** no perder llamadas, reuniones ni follow-ups importantes

**Criterios de Aceptacion:**
- [ ] Configurar recordatorio por actividad: 15 min antes, 1 hora antes, 1 dia antes, personalizado
- [ ] Multiples recordatorios por actividad
- [ ] Recordatorio se envia via notificacion push (in-app) y opcionalmente email
- [ ] Recordatorio de tarea vencida al dia siguiente si no se completo
- [ ] Resumen diario matutino: "Tienes 5 tareas para hoy, 2 vencidas"
- [ ] El vendedor puede silenciar recordatorios por actividad individual

**Tareas Tecnicas:**
- [ ] Modelo de recordatorio: `reminder_at: list[datetime]` en Activity
- [ ] Lambda o cron job que revisa actividades proximas a vencer (cada 5 min)
- [ ] Integracion con `covacha-notification` para envio
- [ ] SQS para programar envios futuros
- [ ] Tests: 5+ unit tests

**Estimacion:** 4 dev-days

---

#### US-CR-018: Calendario de actividades

**Como** Vendedor
**Quiero** ver mis actividades programadas en formato de calendario (dia, semana, mes)
**Para** visualizar mi agenda y detectar huecos o conflictos

**Criterios de Aceptacion:**
- [ ] Endpoint que retorna actividades en rango de fechas para vista calendario
- [ ] Response incluye: fecha/hora inicio, duracion (si aplica), tipo, titulo, contacto
- [ ] Filtrar por: asignado (yo o todo el equipo), tipo de actividad
- [ ] Gerente de Ventas puede ver calendario de todo su equipo
- [ ] Deteccion de conflictos: 2 actividades en el mismo horario
- [ ] Response optimizado para rendering rapido (< 300ms)

**Tareas Tecnicas:**
- [ ] Endpoint: `GET /api/v1/crm/activities/calendar?from=X&to=Y&assigned_to=Z`
- [ ] Query por rango de fechas: `PK = CONTACT#, SK between ACTIVITY#<from> and ACTIVITY#<to>` (o GSI por usuario)
- [ ] Serializacion optimizada para calendario
- [ ] Tests: 4+ unit tests

**Estimacion:** 3 dev-days

---

#### US-CR-019: Log automatico de actividad

**Como** Sistema
**Quiero** registrar actividades automaticamente cuando se envian emails o mensajes de WhatsApp
**Para** que el timeline del contacto siempre este actualizado sin intervencion manual

**Criterios de Aceptacion:**
- [ ] Al enviar WhatsApp desde CRM: crear actividad tipo WHATSAPP con contenido del mensaje
- [ ] Al recibir WhatsApp: crear actividad tipo WHATSAPP con contenido recibido
- [ ] Al enviar email desde CRM: crear actividad tipo EMAIL con subject y preview
- [ ] Al recibir email sincronizado: crear actividad tipo EMAIL
- [ ] Al mover deal de etapa: crear actividad tipo NOTE con "Deal movido de X a Y"
- [ ] Al ganar/perder deal: crear actividad tipo NOTE con resultado
- [ ] Actividades automaticas se marcan con `auto_generated: true`

**Tareas Tecnicas:**
- [ ] Event handler en `ActivityService` que escucha eventos de WhatsApp, email y deals
- [ ] Eventos via SQS: `crm.whatsapp.sent`, `crm.email.received`, `crm.deal.stage_changed`
- [ ] Consumer SQS que crea actividades automaticamente
- [ ] Tests: 5+ unit tests (cada tipo de evento)

**Estimacion:** 3 dev-days

---

### EP-CR-004: Automatizaciones (Workflows)

---

#### US-CR-020: CRUD de workflows

**Como** Administrador CRM
**Quiero** crear workflows de automatizacion con nombre, descripcion y estado
**Para** automatizar tareas repetitivas en mi proceso de ventas

**Criterios de Aceptacion:**
- [ ] Crear workflow con: nombre, descripcion, estado (DRAFT, ACTIVE, PAUSED)
- [ ] Un workflow se compone de: 1 trigger, N condiciones (opcionales), N acciones
- [ ] Listar workflows de la organizacion con su estado y estadisticas basicas
- [ ] Editar workflow (solo si esta en DRAFT o PAUSED)
- [ ] Activar workflow (DRAFT/PAUSED -> ACTIVE)
- [ ] Pausar workflow (ACTIVE -> PAUSED)
- [ ] Eliminar workflow (soft delete)
- [ ] Maximo 20 workflows activos por organizacion
- [ ] Clonar workflow existente como DRAFT

**Tareas Tecnicas:**
- [ ] Modelo `Workflow` en `models/workflow.py` con trigger, conditions, actions (JSON)
- [ ] `WorkflowRepository` con queries por organizacion
- [ ] `WorkflowService` con validacion de estructura y limites
- [ ] Endpoints: `POST/GET/PUT/DELETE /api/v1/crm/workflows`, `PATCH /api/v1/crm/workflows/<id>/activate`, `PATCH /api/v1/crm/workflows/<id>/pause`
- [ ] Tests: 6+ unit tests

**Estimacion:** 4 dev-days

---

#### US-CR-021: Triggers de workflows

**Como** Administrador CRM
**Quiero** configurar diferentes eventos que disparan un workflow
**Para** que las automatizaciones se ejecuten en el momento correcto

**Criterios de Aceptacion:**
- [ ] Triggers soportados:
  - `CONTACT_CREATED`: cuando se crea un contacto nuevo
  - `CONTACT_UPDATED`: cuando se modifica un campo del contacto (especificar cual campo)
  - `DEAL_CREATED`: cuando se crea un deal nuevo
  - `DEAL_STAGE_CHANGED`: cuando un deal cambia de etapa (especificar etapa origen/destino)
  - `DEAL_WON`: cuando se gana un deal
  - `DEAL_LOST`: cuando se pierde un deal
  - `ACTIVITY_OVERDUE`: cuando una tarea pasa su fecha de vencimiento
  - `CONTACT_INACTIVE`: cuando un contacto no tiene actividad en N dias
  - `SCHEDULED`: ejecutar en fecha/hora especifica o recurrente (cron)
- [ ] Cada workflow tiene exactamente 1 trigger
- [ ] El trigger incluye parametros especificos segun el tipo

**Tareas Tecnicas:**
- [ ] Enum `TriggerType` y modelo `WorkflowTrigger` con configuracion por tipo
- [ ] Event dispatcher que evalua triggers activos cuando ocurre un evento
- [ ] Para `CONTACT_INACTIVE` y `SCHEDULED`: Lambda/cron que revisa periodicamente
- [ ] Tests: 6+ unit tests (uno por tipo de trigger)

**Estimacion:** 5 dev-days

---

#### US-CR-022: Condiciones y branches en workflows

**Como** Administrador CRM
**Quiero** agregar condiciones a mis workflows para que las acciones se ejecuten solo cuando se cumplen ciertos criterios
**Para** crear automatizaciones inteligentes que actuen diferente segun el contexto

**Criterios de Aceptacion:**
- [ ] Condiciones evaluan propiedades del contacto, deal o actividad que disparo el trigger
- [ ] Operadores: equals, not_equals, contains, not_contains, greater_than, less_than, is_empty, is_not_empty
- [ ] Logica AND/OR entre condiciones
- [ ] Branches (if/else): si se cumple la condicion ejecutar acciones A, si no, ejecutar acciones B
- [ ] Condiciones pueden evaluar campos personalizados
- [ ] Maximo 10 condiciones por workflow
- [ ] Logs de evaluacion: que condicion se evaluo y resultado (true/false)

**Tareas Tecnicas:**
- [ ] Modelo `WorkflowCondition` con operador, campo, valor, logica
- [ ] `ConditionEvaluator` que recibe la entidad y evalua condiciones
- [ ] Soporte para branches en la estructura del workflow (tree de nodos)
- [ ] Tests: 7+ unit tests (cada operador, AND/OR, branches)

**Estimacion:** 5 dev-days

---

#### US-CR-023: Acciones de workflows

**Como** Administrador CRM
**Quiero** configurar acciones que se ejecutan cuando un workflow se dispara y cumple condiciones
**Para** automatizar envio de mensajes, creacion de tareas y notificaciones

**Criterios de Aceptacion:**
- [ ] Acciones soportadas:
  - `SEND_EMAIL`: enviar email usando template con variables
  - `SEND_WHATSAPP`: enviar WhatsApp usando template
  - `CREATE_TASK`: crear tarea asignada a usuario especifico
  - `MOVE_DEAL_STAGE`: mover deal a etapa especifica
  - `ASSIGN_TO`: asignar deal/contacto a usuario
  - `ADD_TAG`: agregar tag al contacto
  - `REMOVE_TAG`: quitar tag del contacto
  - `NOTIFY_USER`: enviar notificacion in-app a usuario
  - `WAIT_DELAY`: esperar N minutos/horas/dias antes de la siguiente accion
  - `HTTP_WEBHOOK`: enviar HTTP POST a URL externa con payload
- [ ] Multiples acciones por workflow, ejecutadas en orden secuencial
- [ ] Variables dinamicas en templates: `{{contact.name}}`, `{{deal.value}}`, `{{deal.stage}}`
- [ ] Cada accion reporta su resultado: SUCCESS, FAILED, SKIPPED

**Tareas Tecnicas:**
- [ ] Modelo `WorkflowAction` con tipo y configuracion especifica
- [ ] `ActionExecutor` con strategy pattern: una clase por tipo de accion
- [ ] Integracion con `covacha-botia` (SEND_WHATSAPP) y `covacha-notification` (SEND_EMAIL)
- [ ] Para WAIT_DELAY: usar SQS delay queues o DynamoDB TTL + Lambda
- [ ] Tests: 6+ unit tests (una por tipo de accion)

**Estimacion:** 6 dev-days

---

#### US-CR-024: Motor de ejecucion de workflows (engine)

**Como** Sistema
**Quiero** un motor que ejecute workflows de forma asincrona y confiable
**Para** garantizar que las automatizaciones se ejecuten correctamente sin impactar el rendimiento

**Criterios de Aceptacion:**
- [ ] Ejecucion asincrona via SQS (no bloquea la operacion que disparo el trigger)
- [ ] Cada ejecucion genera un registro `WorkflowExecution` con: workflow_id, trigger_event, timestamp, status, resultado por paso
- [ ] Estados de ejecucion: QUEUED, RUNNING, COMPLETED, FAILED, PARTIALLY_COMPLETED
- [ ] Si una accion falla: registrar error, continuar con las demas (no abortar todo el workflow)
- [ ] Idempotencia: el mismo evento no puede disparar el mismo workflow 2 veces (dedup key)
- [ ] Timeout: si un workflow no completa en 5 minutos, marcar como FAILED
- [ ] Concurrencia: maximo 10 ejecuciones simultaneas por organizacion

**Tareas Tecnicas:**
- [ ] `WorkflowEngine` en `services/workflow_engine.py`
- [ ] Consumer SQS: `crm-workflow-execution` queue
- [ ] Modelo `WorkflowExecution` en DynamoDB: `PK = WORKFLOW#<wid>, SK = EXEC#<ts>#<eid>`
- [ ] Dedup con DynamoDB conditional writes
- [ ] Tests: 8+ unit tests (happy path, fallo parcial, idempotencia, timeout)

**Estimacion:** 6 dev-days

---

#### US-CR-025: Historial y monitoreo de ejecuciones

**Como** Administrador CRM
**Quiero** ver el historial de ejecuciones de mis workflows con logs detallados
**Para** diagnosticar problemas y optimizar mis automatizaciones

**Criterios de Aceptacion:**
- [ ] Listar ejecuciones por workflow con paginacion
- [ ] Detalle de ejecucion: trigger event, entity involucrada, resultado por paso, errores
- [ ] Filtrar por: estado (COMPLETED, FAILED), rango de fechas
- [ ] Estadisticas por workflow: total ejecuciones, % exitosas, % fallidas, acciones mas frecuentes
- [ ] Alerta cuando un workflow tiene mas de 50% de fallos en las ultimas 24 horas
- [ ] Pausar automaticamente un workflow con fallos consecutivos (configurable: 5, 10, 20)

**Tareas Tecnicas:**
- [ ] Endpoints: `GET /api/v1/crm/workflows/<id>/executions`, `GET /api/v1/crm/workflows/<id>/executions/<eid>`
- [ ] Endpoint estadisticas: `GET /api/v1/crm/workflows/<id>/stats`
- [ ] Logica de auto-pause por fallos consecutivos en `WorkflowEngine`
- [ ] Tests: 5+ unit tests

**Estimacion:** 4 dev-days

---

### EP-CR-005: Integracion WhatsApp

---

#### US-CR-026: Envio de mensajes WhatsApp individuales desde CRM

**Como** Vendedor
**Quiero** enviar un mensaje de WhatsApp a un contacto directamente desde su perfil en el CRM
**Para** comunicarme rapidamente sin salir del CRM ni buscar el numero en mi telefono

**Criterios de Aceptacion:**
- [ ] Boton "Enviar WhatsApp" en el perfil del contacto (si tiene telefono registrado)
- [ ] Composer de mensaje con texto libre
- [ ] Envio via API de `covacha-botia` (endpoint de envio de mensaje)
- [ ] Confirmacion de envio con status (sent, delivered, read, failed)
- [ ] Actividad tipo WHATSAPP creada automaticamente en timeline
- [ ] Si el contacto no tiene telefono, mostrar error claro
- [ ] Rate limit: maximo 30 mensajes/hora por vendedor

**Tareas Tecnicas:**
- [ ] `WhatsAppIntegration` en `integrations/whatsapp_integration.py`
- [ ] Endpoint: `POST /api/v1/crm/contacts/<id>/whatsapp` con body `{message}`
- [ ] Llamada HTTP a `covacha-botia`: `POST /api/v1/whatsapp/send`
- [ ] Callback/webhook de status update desde covacha-botia
- [ ] Tests: 5+ unit tests (envio exitoso, sin telefono, rate limit)

**Estimacion:** 4 dev-days

---

#### US-CR-027: Templates de WhatsApp con variables

**Como** Vendedor
**Quiero** usar templates pre-aprobados de WhatsApp con variables que se llenan automaticamente
**Para** enviar mensajes consistentes y profesionales sin escribir desde cero cada vez

**Criterios de Aceptacion:**
- [ ] CRUD de templates con nombre, cuerpo del mensaje, y variables ({{nombre}}, {{empresa}}, {{deal_name}})
- [ ] Templates marcados como "aprobados" por el admin (WhatsApp Business requiere aprobacion)
- [ ] Al seleccionar template, variables se llenan automaticamente con datos del contacto/deal
- [ ] Preview del mensaje antes de enviar
- [ ] Templates compartidos por organizacion
- [ ] Maximo 50 templates por organizacion
- [ ] Categorias de template: seguimiento, propuesta, bienvenida, recordatorio, cierre

**Tareas Tecnicas:**
- [ ] Modelo de template con variables y categoria
- [ ] Endpoints: `POST/GET/PUT/DELETE /api/v1/crm/whatsapp-templates`
- [ ] Endpoint: `POST /api/v1/crm/contacts/<id>/whatsapp/template` con body `{template_id}`
- [ ] Variable resolver que extrae datos del contacto/deal
- [ ] Tests: 5+ unit tests

**Estimacion:** 3 dev-days

---

#### US-CR-028: Historial de conversaciones WhatsApp en timeline

**Como** Vendedor
**Quiero** ver el historial completo de mensajes de WhatsApp con un contacto dentro de su timeline
**Para** tener contexto de conversaciones previas antes de escribirle

**Criterios de Aceptacion:**
- [ ] Mensajes enviados y recibidos aparecen en el timeline del contacto
- [ ] Cada mensaje muestra: contenido, fecha/hora, direccion (enviado/recibido), status (sent/delivered/read)
- [ ] Los mensajes se agrupan visualmente como conversacion
- [ ] Webhook de `covacha-botia` actualiza mensajes recibidos en el CRM automaticamente
- [ ] Vinculacion automatica: mensaje recibido se asocia al contacto por numero de telefono (GSI4)
- [ ] Si el telefono no esta registrado, marcar como "mensaje de contacto desconocido"

**Tareas Tecnicas:**
- [ ] Webhook handler: `POST /api/v1/crm/webhooks/whatsapp/incoming`
- [ ] Busqueda de contacto por telefono via GSI4
- [ ] Crear TimelineEntry tipo WHATSAPP con detalle del mensaje
- [ ] Tests: 5+ unit tests (mensaje conocido, desconocido, status update)

**Estimacion:** 4 dev-days

---

#### US-CR-029: Envio masivo (bulk) de WhatsApp a segmentos

**Como** Gerente de Ventas
**Quiero** enviar un mensaje masivo de WhatsApp a todos los contactos de un segmento
**Para** comunicar ofertas, novedades o seguimientos a multiples contactos de una vez

**Criterios de Aceptacion:**
- [ ] Seleccionar un segmento de contactos como destinatarios
- [ ] Usar template pre-aprobado (obligatorio para envio masivo)
- [ ] Vista previa de cuantos contactos recibiran el mensaje
- [ ] Envio con throttling: maximo 50 mensajes/minuto para proteger la cuenta WhatsApp Business
- [ ] Progreso consultable: X de Y enviados, Z fallidos
- [ ] Reporte post-envio: enviados, entregados, leidos, fallidos
- [ ] Actividad tipo WHATSAPP_BULK creada en timeline de cada contacto
- [ ] Maximo 5,000 contactos por envio masivo

**Tareas Tecnicas:**
- [ ] Endpoint: `POST /api/v1/crm/whatsapp/bulk` con body `{segment_id, template_id}`
- [ ] Job SQS para envio async con throttling
- [ ] Modelo `BulkSendJob` para tracking de progreso
- [ ] Endpoint status: `GET /api/v1/crm/whatsapp/bulk/<job_id>`
- [ ] Tests: 5+ unit tests (envio exitoso, throttling, contactos sin telefono)

**Estimacion:** 5 dev-days

---

#### US-CR-030: Respuestas rapidas (canned responses) de WhatsApp

**Como** Vendedor
**Quiero** tener respuestas rapidas predefinidas para mensajes comunes de WhatsApp
**Para** responder mas rapido sin tener que escribir el mismo mensaje repetidamente

**Criterios de Aceptacion:**
- [ ] CRUD de canned responses: shortcut (keyword), contenido, categoria
- [ ] Buscar response escribiendo `/shortcut` en el composer
- [ ] Canned responses compartidas por organizacion
- [ ] Canned responses personales del vendedor
- [ ] Soporte para variables basicas ({{nombre}}, {{empresa}})
- [ ] Maximo 100 canned responses por organizacion + 50 por vendedor
- [ ] Ordenar por frecuencia de uso

**Tareas Tecnicas:**
- [ ] Endpoints: `POST/GET/PUT/DELETE /api/v1/crm/canned-responses`
- [ ] Scope: `organization` o `personal`
- [ ] Contador de uso para ordenamiento
- [ ] Tests: 4+ unit tests

**Estimacion:** 2 dev-days

---

### EP-CR-006: Reportes y Analytics CRM

---

#### US-CR-031: Dashboard de KPIs de ventas

**Como** Gerente de Ventas
**Quiero** un dashboard con los KPIs principales de mi pipeline de ventas
**Para** monitorear el rendimiento del equipo de un vistazo

**Criterios de Aceptacion:**
- [ ] KPIs mostrados:
  - Pipeline value total (deals OPEN)
  - Pipeline value ponderado (valor * probabilidad)
  - Deals abiertos (conteo)
  - Deals ganados este periodo (conteo + valor)
  - Deals perdidos este periodo (conteo + valor)
  - Win rate (ganados / (ganados + perdidos))
  - Ciclo de venta promedio (dias desde creacion hasta won)
  - Ticket promedio (valor promedio de deals ganados)
- [ ] Filtros: periodo (hoy, semana, mes, trimestre, ano, custom), pipeline, vendedor
- [ ] Comparativa con periodo anterior (delta + flecha up/down)
- [ ] Response time < 500ms

**Tareas Tecnicas:**
- [ ] Endpoint: `GET /api/v1/crm/reports/dashboard?period=month&pipeline_id=X`
- [ ] `ReportService` con calculo de metricas desde DynamoDB
- [ ] Cache de metricas con TTL de 10 minutos
- [ ] Tests: 6+ unit tests (cada KPI, filtros)

**Estimacion:** 5 dev-days

---

#### US-CR-032: Reporte de conversion por etapa (funnel)

**Como** Gerente de Ventas
**Quiero** ver las tasas de conversion entre cada etapa del pipeline
**Para** identificar en que etapa estamos perdiendo mas deals y enfocar esfuerzos

**Criterios de Aceptacion:**
- [ ] Funnel chart data: cuantos deals entraron a cada etapa y cuantos pasaron a la siguiente
- [ ] Conversion rate entre etapas adyacentes (%)
- [ ] Tiempo promedio en cada etapa (dias)
- [ ] Razon de perdida mas frecuente por etapa
- [ ] Filtros: periodo, pipeline, vendedor
- [ ] Comparativa con periodo anterior

**Tareas Tecnicas:**
- [ ] Endpoint: `GET /api/v1/crm/reports/funnel?pipeline_id=X&period=month`
- [ ] Calculo basado en `stage_history` de los deals
- [ ] Tests: 4+ unit tests

**Estimacion:** 4 dev-days

---

#### US-CR-033: Reporte por vendedor

**Como** Gerente de Ventas
**Quiero** ver metricas de rendimiento individuales para cada vendedor de mi equipo
**Para** identificar top performers, dar coaching y distribuir mejor las oportunidades

**Criterios de Aceptacion:**
- [ ] Metricas por vendedor: deals abiertos, deals ganados, deals perdidos, valor cerrado, win rate, ciclo promedio, actividades realizadas
- [ ] Ranking de vendedores por valor cerrado
- [ ] Comparativa entre vendedores (tabla o grafico de barras)
- [ ] Tendencia mensual por vendedor (grafico de linea)
- [ ] Filtros: periodo, pipeline

**Tareas Tecnicas:**
- [ ] Endpoint: `GET /api/v1/crm/reports/team?period=month&pipeline_id=X`
- [ ] Query usando GSI2 (deals por assigned_to)
- [ ] Agregacion por vendedor
- [ ] Tests: 4+ unit tests

**Estimacion:** 4 dev-days

---

#### US-CR-034: Forecast de ingresos

**Como** Gerente de Ventas
**Quiero** ver una proyeccion de ingresos futuros basada en el pipeline actual
**Para** hacer forecast para la direccion y planificar recursos

**Criterios de Aceptacion:**
- [ ] Forecast basado en: pipeline value ponderado + factor historico de conversion
- [ ] Proyeccion por mes: proximo mes, 3 meses, 6 meses, 12 meses
- [ ] Escenarios: optimista (best case: todos los OPEN se ganan), realista (weighted), pesimista (solo deals >75% probabilidad)
- [ ] Deals con fecha de cierre esperada asignados al mes correspondiente
- [ ] Comparacion con forecast anterior (desviacion)
- [ ] Filtros: pipeline, vendedor

**Tareas Tecnicas:**
- [ ] Endpoint: `GET /api/v1/crm/reports/forecast?months=3&pipeline_id=X`
- [ ] Algoritmo de proyeccion: agrupar deals por fecha_cierre_esperada * probabilidad
- [ ] Factor historico: win_rate de ultimos 6 meses como ajuste
- [ ] Tests: 5+ unit tests (escenarios, sin datos, filtros)

**Estimacion:** 4 dev-days

---

#### US-CR-035: Reportes personalizados

**Como** Administrador CRM
**Quiero** crear reportes personalizados seleccionando metricas y agrupaciones
**Para** obtener vistas especificas de datos que los reportes estandar no cubren

**Criterios de Aceptacion:**
- [ ] Seleccionar metricas: conteo deals, valor total, valor promedio, win rate, actividades
- [ ] Agrupar por: vendedor, pipeline, etapa, tag, campo personalizado, mes, semana
- [ ] Filtros: periodo, pipeline, vendedor, tag, campo personalizado
- [ ] Guardar reporte como favorito con nombre
- [ ] Compartir reporte con otros usuarios de la organizacion
- [ ] Maximo 20 reportes guardados por organizacion

**Tareas Tecnicas:**
- [ ] Modelo `CustomReport` con definicion de metricas, agrupaciones y filtros
- [ ] Endpoints: `POST/GET/PUT/DELETE /api/v1/crm/reports/custom`
- [ ] Endpoint ejecutar: `GET /api/v1/crm/reports/custom/<id>/execute`
- [ ] Query builder generico que traduce la definicion a queries DynamoDB
- [ ] Tests: 5+ unit tests

**Estimacion:** 5 dev-days

---

#### US-CR-036: Exportacion y programacion de reportes

**Como** Gerente de Ventas
**Quiero** exportar reportes en PDF y CSV, y programar su envio periodico por email
**Para** compartir metricas con la direccion sin acceso al CRM

**Criterios de Aceptacion:**
- [ ] Exportar cualquier reporte (dashboard, funnel, team, custom) en PDF y CSV
- [ ] PDF con formato profesional: logo organizacion, fecha, filtros aplicados, tablas y graficos
- [ ] CSV con headers claros y formato compatible con Excel
- [ ] Programar envio de reporte: diario (8am), semanal (lunes 8am), mensual (dia 1 8am)
- [ ] Configurar destinatarios (emails)
- [ ] Historial de reportes enviados
- [ ] Cancelar programacion de envio

**Tareas Tecnicas:**
- [ ] Generacion de PDF con ReportLab o WeasyPrint
- [ ] Generacion de CSV con modulo csv estandar
- [ ] Endpoint: `POST /api/v1/crm/reports/<id>/export?format=pdf|csv`
- [ ] Modelo `ScheduledReport` con cron expression y destinatarios
- [ ] Lambda o cron que ejecuta reportes programados y envia via `covacha-notification`
- [ ] Tests: 4+ unit tests (PDF, CSV, programacion)

**Estimacion:** 5 dev-days

---

### EP-CR-007: Email Integration

---

#### US-CR-037: Configuracion de cuenta de email por organizacion

**Como** Administrador CRM
**Quiero** configurar la cuenta de email de mi organizacion para sincronizar con el CRM
**Para** que los emails enviados y recibidos se vinculen automaticamente a los contactos

**Criterios de Aceptacion:**
- [ ] Formulario de configuracion: servidor IMAP, puerto, servidor SMTP, puerto, email, contrasena
- [ ] Credenciales encriptadas en DynamoDB (encryption at rest + AES para password)
- [ ] Test de conexion antes de guardar (verificar IMAP y SMTP)
- [ ] Soporte para Gmail, Outlook y servidores IMAP genericos
- [ ] Sync iniciar: importar emails de los ultimos 30 dias
- [ ] Configuracion de frecuencia de sync: cada 5 min, 15 min, 30 min, 1 hora
- [ ] Solo 1 cuenta email por organizacion (v1)

**Tareas Tecnicas:**
- [ ] Modelo `EmailConfig` con credenciales encriptadas
- [ ] `EmailIntegration` en `integrations/email_integration.py`
- [ ] Endpoints: `POST/GET/PUT /api/v1/crm/email/config`, `POST /api/v1/crm/email/config/test`
- [ ] Encriptacion AES-256 para credenciales usando AWS KMS
- [ ] Tests: 5+ unit tests (config valida, test conexion mock, encriptacion)

**Estimacion:** 4 dev-days

---

#### US-CR-038: Sincronizacion bidireccional de emails

**Como** Sistema
**Quiero** sincronizar emails entrantes y salientes con el CRM automaticamente
**Para** que el timeline de cada contacto refleje todas las comunicaciones por email

**Criterios de Aceptacion:**
- [ ] Sync periodico via IMAP: descargar emails nuevos desde ultima sincronizacion
- [ ] Vincular email a contacto por direccion de email (busqueda GSI3)
- [ ] Si el email es de un contacto conocido: crear TimelineEntry tipo EMAIL
- [ ] Si el email es de un remitente desconocido: almacenar sin vincular (opcion de vincular manual)
- [ ] Sync de emails enviados (carpeta Sent) para registrar respuestas del vendedor
- [ ] Almacenar: from, to, subject, body (preview 500 chars), date, message_id
- [ ] Deduplicacion por message_id (IMAP puede devolver el mismo email 2 veces)
- [ ] No almacenar adjuntos (v1), solo metadata

**Tareas Tecnicas:**
- [ ] Job de sync: Lambda o cron que ejecuta IMAP fetch por organizacion
- [ ] IMAP client con `imaplib` de Python
- [ ] Busqueda de contacto por email (GSI3)
- [ ] Modelo `EmailThread` en DynamoDB: `PK = CONTACT#<cid>, SK = EMAIL#<ts>#<eid>`
- [ ] SQS queue `crm-email-sync` para procesamiento async
- [ ] Tests: 6+ unit tests (email conocido, desconocido, dedup, parse)

**Estimacion:** 5 dev-days

---

#### US-CR-039: Templates de email con variables

**Como** Vendedor
**Quiero** usar templates de email con variables que se llenan con datos del contacto y deal
**Para** enviar emails profesionales y personalizados rapidamente

**Criterios de Aceptacion:**
- [ ] CRUD de templates: nombre, subject, body (HTML basico), variables
- [ ] Variables soportadas: {{contact.name}}, {{contact.company}}, {{deal.name}}, {{deal.value}}, {{sender.name}}, {{sender.signature}}
- [ ] Preview del template con datos reales de un contacto antes de enviar
- [ ] Templates compartidos por organizacion + templates personales del vendedor
- [ ] Categorias: seguimiento, propuesta, bienvenida, agradecimiento, custom
- [ ] Enviar email usando template: `POST /api/v1/crm/contacts/<id>/email/template`

**Tareas Tecnicas:**
- [ ] Modelo de email template con body HTML y variables
- [ ] Endpoints: `POST/GET/PUT/DELETE /api/v1/crm/email-templates`
- [ ] Template engine simple (replace {{var}} con datos reales)
- [ ] Envio via SMTP a traves de `covacha-notification`
- [ ] Tests: 5+ unit tests

**Estimacion:** 3 dev-days

---

#### US-CR-040: Secuencias de email automaticas (drip campaigns)

**Como** Vendedor
**Quiero** crear secuencias de emails automaticos que se envian en intervalos programados
**Para** nutrir prospectos frios con informacion sin hacerlo manualmente email por email

**Criterios de Aceptacion:**
- [ ] Crear secuencia: nombre, lista de pasos (email template + delay en dias)
- [ ] Enrollar un contacto en una secuencia manualmente
- [ ] Enrollar contactos de un segmento en una secuencia
- [ ] Ejecucion automatica: enviar email del paso N, esperar delay, enviar paso N+1
- [ ] Cancelacion automatica: si el contacto responde, detener la secuencia
- [ ] Cancelacion manual: sacar contacto de la secuencia
- [ ] Status por contacto: activo, completado, cancelado (por respuesta), cancelado (manual)
- [ ] Maximo 10 secuencias activas por organizacion
- [ ] Maximo 10 pasos por secuencia

**Tareas Tecnicas:**
- [ ] Modelo `EmailSequence` con pasos y estado por contacto enrollado
- [ ] Endpoints: `POST/GET/PUT/DELETE /api/v1/crm/email-sequences`, `POST /api/v1/crm/email-sequences/<id>/enroll`
- [ ] Job SQS/Lambda que verifica diariamente que paso toca enviar
- [ ] Listener de emails recibidos para auto-cancelar secuencias
- [ ] Tests: 6+ unit tests (happy path, respuesta cancela, manual cancel, limites)

**Estimacion:** 6 dev-days

---

#### US-CR-041: Tracking de opens y clicks en emails

**Como** Vendedor
**Quiero** saber si el contacto abrio mi email y si hizo click en algun link
**Para** priorizar follow-ups con contactos que muestran interes

**Criterios de Aceptacion:**
- [ ] Pixel de tracking invisible insertado en emails enviados desde el CRM
- [ ] Registro de open: fecha/hora, IP, user agent
- [ ] Links en el email wrapeados con redirect tracker
- [ ] Registro de click: fecha/hora, URL original, IP
- [ ] Metricas en el perfil del contacto: emails enviados, opens, clicks
- [ ] Indicador visual en timeline: email abierto (ojo), email con click (link)
- [ ] Metricas agregadas por template: open rate, click rate
- [ ] Opcion de desactivar tracking por organizacion (privacy)

**Tareas Tecnicas:**
- [ ] Endpoint de tracking pixel: `GET /api/v1/crm/tracking/open/<tracking_id>` (retorna 1x1 gif)
- [ ] Endpoint de redirect: `GET /api/v1/crm/tracking/click/<tracking_id>` (redirect a URL original)
- [ ] Insertar pixel y wrap links antes de enviar email
- [ ] Modelo de tracking events en DynamoDB
- [ ] Tests: 5+ unit tests (open tracking, click tracking, metricas)

**Estimacion:** 4 dev-days

---

### EP-CR-008: API y Webhooks CRM

---

#### US-CR-042: API REST publica versionada

**Como** Administrador CRM
**Quiero** una API REST publica y documentada para integrar el CRM con mis sistemas externos
**Para** automatizar sincronizacion de datos entre el CRM y mi ERP/website/otros

**Criterios de Aceptacion:**
- [ ] API base: `/api/v1/crm/` con versionado en URL
- [ ] Endpoints publicos de contactos, deals, actividades, pipelines (read/write)
- [ ] Paginacion consistente: cursor-based con parametros `cursor` y `limit`
- [ ] Formato de response estandar: `{data: [...], meta: {cursor, has_more, total}}`
- [ ] Errores estandar: `{error: {code, message, details}}`
- [ ] Codigos HTTP correctos: 200, 201, 400, 401, 403, 404, 409, 422, 429, 500
- [ ] CORS configurado para dominios permitidos del tenant
- [ ] Documentacion OpenAPI 3.0 servida en `/api/v1/crm/docs`

**Tareas Tecnicas:**
- [ ] Review y estandarizacion de todos los endpoints existentes
- [ ] Middleware de formato de response consistente
- [ ] Generacion automatica de OpenAPI spec con `flask-smorest` o `apispec`
- [ ] Swagger UI integrado en endpoint /docs
- [ ] Tests: 4+ unit tests (formato response, errores, CORS)

**Estimacion:** 4 dev-days

---

#### US-CR-043: Autenticacion por API key

**Como** Administrador CRM
**Quiero** generar API keys con permisos granulares para cada integracion
**Para** controlar que puede hacer cada sistema externo y revocar acceso si es necesario

**Criterios de Aceptacion:**
- [ ] Crear API key con: nombre, permisos (read_contacts, write_contacts, read_deals, write_deals, etc.)
- [ ] API key generada: prefijo `crm_` + 40 chars aleatorios (almacenar hash, no plaintext)
- [ ] Mostrar key completa solo al crear (luego solo primeros 8 chars)
- [ ] Autenticacion via header: `Authorization: Bearer crm_xxxx...`
- [ ] Revocar API key (soft delete, deja de funcionar inmediatamente)
- [ ] Listar API keys activas con ultimo uso y conteo de requests
- [ ] Maximo 10 API keys por organizacion

**Tareas Tecnicas:**
- [ ] Modelo `APIKey` en DynamoDB con hash SHA-256 y permisos
- [ ] GSI para buscar key por hash: `PK = APIKEY#<key_hash>`
- [ ] Middleware de autenticacion que valida key y permisos por endpoint
- [ ] Endpoints: `POST/GET/DELETE /api/v1/crm/api-keys`
- [ ] Tests: 6+ unit tests (crear, autenticar, permisos, revocar)

**Estimacion:** 4 dev-days

---

#### US-CR-044: Rate limiting por API key

**Como** Sistema
**Quiero** aplicar rate limiting por API key para proteger el servicio
**Para** evitar que una integracion mal configurada sature el CRM

**Criterios de Aceptacion:**
- [ ] Rate limit default: 100 requests/minuto por API key
- [ ] Rate limit configurable por API key individual (50, 100, 500, 1000 req/min)
- [ ] Response 429 Too Many Requests cuando se excede el limite
- [ ] Headers de rate limit en response: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- [ ] Rate limit tambien aplica a usuarios internos (mas alto: 500 req/min)
- [ ] Implementacion con sliding window (no fixed window)

**Tareas Tecnicas:**
- [ ] Rate limiter con DynamoDB (counter con TTL) o en-memory con Redis si se agrega
- [ ] Middleware de rate limiting que lee la API key y aplica limites
- [ ] Tests: 4+ unit tests (bajo limite, exceder limite, headers)

**Estimacion:** 3 dev-days

---

#### US-CR-045: Webhooks configurables

**Como** Administrador CRM
**Quiero** configurar webhooks que notifiquen a mis sistemas cuando ocurren eventos en el CRM
**Para** mantener mis otros sistemas sincronizados en tiempo real

**Criterios de Aceptacion:**
- [ ] CRUD de webhooks: URL destino, eventos suscritos, estado (ACTIVE, PAUSED)
- [ ] Eventos disponibles: CONTACT_CREATED, CONTACT_UPDATED, CONTACT_DELETED, DEAL_CREATED, DEAL_STAGE_CHANGED, DEAL_WON, DEAL_LOST, ACTIVITY_CREATED
- [ ] Payload del webhook: `{event, timestamp, data: {entity completa}}`
- [ ] Firma HMAC-SHA256 en header `X-CRM-Signature` para verificar integridad
- [ ] Secret de firma unico por webhook (generado al crear)
- [ ] Reintentos automaticos: 3 intentos con backoff (1 min, 5 min, 30 min)
- [ ] Dead letter queue: webhooks que fallan 3 veces se guardan para reenvio manual
- [ ] Maximo 10 webhooks por organizacion

**Tareas Tecnicas:**
- [ ] Modelo `Webhook` en DynamoDB con URL, events, secret
- [ ] `WebhookDispatcher` en `integrations/webhook_dispatcher.py`
- [ ] SQS queue `crm-webhook-dispatch` para envio async
- [ ] Firma HMAC del payload con secret del webhook
- [ ] Endpoints: `POST/GET/PUT/DELETE /api/v1/crm/webhooks`
- [ ] Tests: 6+ unit tests (dispatch, firma, reintentos, dead letter)

**Estimacion:** 5 dev-days

---

#### US-CR-046: Logs de uso de API

**Como** Administrador CRM
**Quiero** ver logs de uso de la API por cada API key
**Para** monitorear el consumo, detectar anomalias y debugging de integraciones

**Criterios de Aceptacion:**
- [ ] Registrar cada request: timestamp, API key (primeros 8 chars), method, path, status code, latency
- [ ] Listar logs con filtros: API key, period, status code, path
- [ ] Metricas agregadas: requests/dia, errores/dia, latencia promedio por key
- [ ] Retencion de logs: 30 dias
- [ ] No registrar body de request/response (seguridad)
- [ ] Endpoint de healthcheck excluido de logs

**Tareas Tecnicas:**
- [ ] Middleware de logging que registra requests en DynamoDB (o CloudWatch)
- [ ] TTL de 30 dias en items de log
- [ ] Endpoints: `GET /api/v1/crm/api-keys/<id>/logs`, `GET /api/v1/crm/api-keys/<id>/metrics`
- [ ] Tests: 3+ unit tests

**Estimacion:** 3 dev-days

---

#### US-CR-047: SDK Python para covacha-libs

**Como** Desarrollador backend
**Quiero** un SDK Python en covacha-libs para consumir la API del CRM
**Para** integrar otros servicios del ecosistema con el CRM sin escribir HTTP requests manualmente

**Criterios de Aceptacion:**
- [ ] Clase `CRMClient` con metodos tipados:
  - `create_contact(data) -> Contact`
  - `get_contact(id) -> Contact`
  - `list_contacts(filters) -> PaginatedResult[Contact]`
  - `create_deal(data) -> Deal`
  - `move_deal_stage(deal_id, stage_id) -> Deal`
  - `create_activity(data) -> Activity`
  - `search_contacts(query) -> PaginatedResult[Contact]`
- [ ] Configuracion: `CRMClient(api_url, api_key)`
- [ ] Manejo de errores con excepciones tipadas: `CRMNotFoundError`, `CRMValidationError`, `CRMRateLimitError`
- [ ] Retry automatico en errores transitorios (429, 500, 502, 503)
- [ ] Type hints completos para autocompletado en IDE
- [ ] Publicado como modulo en covacha-libs

**Tareas Tecnicas:**
- [ ] Modulo `covacha_libs/crm_client.py` con CRMClient
- [ ] Modelos de datos: Contact, Deal, Activity, PipelineStage (dataclasses)
- [ ] HTTP client con `requests` y retry con `tenacity`
- [ ] Tests: 8+ unit tests (cada metodo + errores + retry)

**Estimacion:** 5 dev-days

---

#### US-CR-048: Documentacion OpenAPI completa

**Como** Desarrollador externo
**Quiero** documentacion OpenAPI 3.0 completa e interactiva de la API del CRM
**Para** integrar mis sistemas rapidamente sin necesidad de soporte humano

**Criterios de Aceptacion:**
- [ ] Spec OpenAPI 3.0 con todos los endpoints del CRM
- [ ] Schemas de request y response para cada endpoint
- [ ] Ejemplos de request y response para cada endpoint
- [ ] Autenticacion documentada (API key, header format)
- [ ] Codigos de error documentados con ejemplos
- [ ] Rate limiting documentado
- [ ] Webhooks documentados con ejemplos de payload y verificacion de firma
- [ ] Swagger UI interactivo en `/api/v1/crm/docs` con "Try it out"
- [ ] Spec descargable en JSON y YAML

**Tareas Tecnicas:**
- [ ] Decoradores de OpenAPI en cada Blueprint
- [ ] Schemas con `marshmallow` o `pydantic` para request/response
- [ ] Swagger UI servido con `flask-smorest`
- [ ] Endpoint: `GET /api/v1/crm/docs` (UI), `GET /api/v1/crm/openapi.json` (spec)
- [ ] Tests: 3+ unit tests (spec valida, schemas correctos)

**Estimacion:** 4 dev-days

---

## Roadmap

### Fase 1: Fundamentos (Sprints 1-4) ~34 dev-days

| Sprint | Epicas | User Stories | Objetivo |
|--------|--------|-------------|----------|
| Sprint 1-2 | EP-CR-001 (parcial) | US-CR-001, US-CR-002, US-CR-003 | CRUD de contactos con campos custom y tags |
| Sprint 2-3 | EP-CR-001 (completa) | US-CR-004, US-CR-005, US-CR-006, US-CR-007, US-CR-008 | Segmentos, import, busqueda, dedup, timeline |
| Sprint 3-4 | EP-CR-002 (parcial) | US-CR-009, US-CR-010 | Pipelines y CRUD de deals |

### Fase 2: Pipeline Completo (Sprints 4-6) ~32 dev-days

| Sprint | Epicas | User Stories | Objetivo |
|--------|--------|-------------|----------|
| Sprint 4-5 | EP-CR-002 (completa) | US-CR-011, US-CR-012, US-CR-013, US-CR-014 | Mover deals, asignacion, metricas, kanban |
| Sprint 5-6 | EP-CR-003 | US-CR-015, US-CR-016, US-CR-017, US-CR-018, US-CR-019 | Actividades, tareas, recordatorios, calendario |

### Fase 3: Comunicaciones (Sprints 6-9) ~40 dev-days

| Sprint | Epicas | User Stories | Objetivo |
|--------|--------|-------------|----------|
| Sprint 6-7 | EP-CR-005 | US-CR-026, US-CR-027, US-CR-028, US-CR-029, US-CR-030 | WhatsApp integration completa |
| Sprint 7-8 | EP-CR-007 | US-CR-037, US-CR-038, US-CR-039, US-CR-040, US-CR-041 | Email integration completa |

### Fase 4: Automatizacion y Analytics (Sprints 9-13) ~61 dev-days

| Sprint | Epicas | User Stories | Objetivo |
|--------|--------|-------------|----------|
| Sprint 9-10 | EP-CR-004 (parcial) | US-CR-020, US-CR-021, US-CR-022, US-CR-023 | Workflow CRUD, triggers, condiciones, acciones |
| Sprint 10-11 | EP-CR-004 (completa) | US-CR-024, US-CR-025 | Motor de ejecucion, historial |
| Sprint 11-12 | EP-CR-006 | US-CR-031, US-CR-032, US-CR-033, US-CR-034, US-CR-035, US-CR-036 | Reportes y analytics completos |
| Sprint 12-13 | EP-CR-008 | US-CR-042, US-CR-043, US-CR-044, US-CR-045, US-CR-046, US-CR-047, US-CR-048 | API publica, webhooks, SDK, docs |

### Resumen del Roadmap

```
Sprint:  1    2    3    4    5    6    7    8    9    10   11   12   13
         |    |    |    |    |    |    |    |    |    |    |    |    |
EP-CR-001 ██████████████
EP-CR-002      ██████████████████
EP-CR-003                ██████████████
EP-CR-005                          ██████████
EP-CR-007                               ██████████
EP-CR-004                                         ██████████████
EP-CR-006                                                   ██████████
EP-CR-008                                                        ██████████
         |    |    |    |    |    |    |    |    |    |    |    |    |
         FASE 1         FASE 2         FASE 3              FASE 4
```

---

## Grafo de Dependencias

### Dependencias entre Epicas

```
EP-CR-001 (Contactos) ──────────────────────────────────┐
    |          |             |            |              |
    v          v             v            v              v
EP-CR-002  EP-CR-005    EP-CR-007    EP-CR-008     EP-CR-006
(Deals)    (WhatsApp)   (Email)      (API/Hooks)   (Reportes)
    |                                    ^              ^
    v                                    |              |
EP-CR-003 (Actividades) ────────────────┘              |
    |                                                   |
    v                                                   |
EP-CR-004 (Workflows) ─────────────────────────────────┘
```

### Dependencias con Repos Externos

```
covacha-crm
    |
    +-- depende de --> covacha-libs (modelos base, repositorios, auth decorators)
    |
    +-- consume   --> covacha-botia (envio WhatsApp, recepcion mensajes)
    |                     via HTTP: POST /api/v1/whatsapp/send
    |                     via webhook: POST /api/v1/crm/webhooks/whatsapp/incoming
    |
    +-- consume   --> covacha-notification (envio email, notificaciones push)
    |                     via HTTP: POST /api/v1/notifications/email/send
    |                     via SQS: crm-email-notifications queue
    |
    +-- consumido por --> covacha-core (futuro: lookup de contactos en modulos compartidos)
                              via SDK: CRMClient en covacha-libs
```

### Endpoints entre Servicios

| Origen | Destino | Endpoint | Proposito |
|--------|---------|----------|-----------|
| covacha-crm | covacha-botia | `POST /api/v1/whatsapp/send` | Enviar WhatsApp |
| covacha-crm | covacha-botia | `POST /api/v1/whatsapp/bulk` | Envio masivo WhatsApp |
| covacha-botia | covacha-crm | `POST /api/v1/crm/webhooks/whatsapp/incoming` | Mensaje recibido |
| covacha-crm | covacha-notification | `POST /api/v1/notifications/email/send` | Enviar email |
| covacha-crm | covacha-notification | `POST /api/v1/notifications/push` | Notificacion push |
| covacha-notification | covacha-crm | `POST /api/v1/crm/webhooks/email/tracking` | Email open/click |
| covacha-core | covacha-crm | (via SDK CRMClient) | Lookup de contactos |

---

## Riesgos y Mitigaciones

| # | Riesgo | Probabilidad | Impacto | Mitigacion |
|---|--------|-------------|---------|------------|
| 1 | **DynamoDB scan lento** en busqueda avanzada con 50k+ contactos | Alta | Alto | Evaluar OpenSearch/ElasticSearch para busqueda full-text. Iniciar con DynamoDB FilterExpression y migrar si latencia > 500ms |
| 2 | **Rate limiting de WhatsApp Business** al enviar masivos | Alta | Medio | Throttling estricto (50 msg/min), queue con backoff, monitoreo de status de la cuenta |
| 3 | **Credenciales IMAP/SMTP** expuestas o mal manejadas | Media | Alto | Encriptacion AES-256 con AWS KMS. Nunca loggear credenciales. Audit trail de acceso |
| 4 | **Workflows infinitos** (workflow A dispara workflow B que dispara workflow A) | Media | Alto | Limitar profundidad de ejecucion a 3 niveles. Dedup key con TTL. Max ejecuciones/hora por workflow |
| 5 | **Duplicados masivos** al importar CSV con datos existentes | Alta | Medio | Validacion pre-import con match por email. Opcion skip/overwrite. Preview antes de confirmar |
| 6 | **Performance de metricas** con muchos deals y actividades | Media | Medio | Cache con TTL de 5-10 min. Agregaciones incrementales en vez de full scan. DynamoDB Streams para actualizar contadores |
| 7 | **Multi-tenancy leak** (un tenant ve datos de otro) | Baja | Critico | Partition key siempre incluye TENANT#. Middleware de validacion de tenant en cada request. Tests de aislamiento |
| 8 | **Email tracking bloqueado** por clientes de correo | Alta | Bajo | Informar que las metricas son aproximadas. No depender de tracking para funcionalidad critica |
| 9 | **Scope creep** (CRM intenta replicar Salesforce/HubSpot) | Media | Medio | Mantener P3 estricto. No agregar features fuera del scope definido sin aprobacion. MVP primero |
| 10 | **Integracion fragil** con covacha-botia y covacha-notification | Media | Alto | Circuit breaker en llamadas HTTP. Fallback graceful (si WhatsApp falla, loggear y no bloquear). Retry con SQS |

---

## Definition of Done Global

Cada user story se considera DONE cuando:

- [ ] Codigo implementado en la rama `feature/EP-CR-XXX-descripcion`
- [ ] Tests unitarios con coverage >= 98%
- [ ] Tests pasan en CI (GitHub Actions)
- [ ] Endpoint documentado en OpenAPI spec
- [ ] Code review aprobado (por otro dev o Copilot)
- [ ] Multi-tenancy verificado: test de aislamiento entre tenants
- [ ] Logs estructurados para operaciones importantes
- [ ] Manejo de errores con mensajes claros (nunca stack trace al usuario)
- [ ] Performance: response time < 500ms para operaciones de lectura
- [ ] Sin datos sensibles en logs (emails de contactos OK, credenciales NUNCA)
- [ ] PR creado automaticamente via GitHub Action (coverage gate)
- [ ] Merge a develop

---

## Resumen Ejecutivo

| Metrica | Valor |
|---------|-------|
| Total epicas | 8 (EP-CR-001 a EP-CR-008) |
| Total user stories | 48 (US-CR-001 a US-CR-048) |
| Estimacion total | ~167 dev-days |
| Sprints estimados | 13 (asumiendo 2 semanas por sprint) |
| Duracion total estimada | ~6.5 meses |
| Repos impactados | covacha-crm (principal), covacha-libs (SDK), covacha-botia (WhatsApp), covacha-notification (email) |
| Prioridad producto | P3 |
| Dependencias externas | WhatsApp Business API (via covacha-botia), IMAP/SMTP (proveedores email) |
