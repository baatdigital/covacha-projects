# SuperPago - Notificaciones Financieras (EP-SP-029 a EP-SP-030)

**Fecha**: 2026-02-14
**Product Owner**: SuperPago
**Estado**: EP-SP-029 COMPLETADO (backend) | EP-SP-030 Planificacion
**Continua desde**: BILLPAY-ONBOARDING-EPICS.md (EP-SP-021 a EP-SP-028, US-SP-085 a US-SP-116)
**User Stories**: US-SP-117 en adelante (continua desde US-SP-116)

---

## Tabla de Contenidos

1. [Contexto y Motivacion](#contexto-y-motivacion)
2. [Relacion con Epicas Existentes](#relacion-con-epicas-existentes)
3. [Arquitectura de Notificaciones](#arquitectura-de-notificaciones)
4. [Matriz de Eventos por Tier y Canal](#matriz-de-eventos-por-tier-y-canal)
5. [Mapa de Epicas Nuevas](#mapa-de-epicas-nuevas)
6. [Epicas Detalladas](#epicas-detalladas)
7. [User Stories Detalladas](#user-stories-detalladas)
8. [Roadmap](#roadmap)
9. [Grafo de Dependencias](#grafo-de-dependencias)
10. [Riesgos y Mitigaciones](#riesgos-y-mitigaciones)

---

## Contexto y Motivacion

El ecosistema SuperPago genera eventos financieros criticos (SPEI in/out, BillPay, Cash-In/Out, limites, conciliacion) que deben notificarse a tres audiencias distintas con canales y niveles de detalle diferentes. La historia US-SP-038 (EP-SP-010) definia notificaciones basicas para eventos SPEI. Estas dos epicas nuevas extienden ese concepto a un **sistema completo de notificaciones multi-canal, multi-tier y multi-evento** que cubre todos los productos financieros de SuperPago.

| Capacidad | Problema que Resuelve |
|-----------|----------------------|
| **Notificaciones Backend** | Routing inteligente de eventos financieros a los canales correctos por tier, con retry, audit trail, y templates por canal |
| **Frontend de Configuracion y Tiempo Real** | Admin ve alertas en vivo, B2B configura su webhook y canales, B2C gestiona sus preferencias de WhatsApp/email/SMS |

### Diferencia con EP-SP-010 (US-SP-038)

EP-SP-010/US-SP-038 definia notificaciones basicas de eventos SPEI con 3 canales (email, in-app, webhook). Las nuevas epicas extienden esto con:

- **EP-SP-029**: Modelo completo de preferencias por org+usuario, dispatcher multi-canal con SQS, webhook outbound con HMAC y retry, templates por canal y evento, dead letter queue, audit trail persistente
- **EP-SP-030**: Dashboard en tiempo real (SSE) para Tier 1, configurador de webhook para Tier 2, preferencias B2C con toggles granulares, historial de notificaciones enviadas

### Relacion con US-SP-038

US-SP-038 es **reemplazada y absorbida** por estas epicas. Los criterios de aceptacion de US-SP-038 se cubren completamente en US-SP-117 a US-SP-120 (dispatcher, templates, canales). US-SP-038 queda como story "legacy" que no necesita implementarse por separado.

---

## Relacion con Epicas Existentes

| Epica Existente | Relacion con Nuevas Epicas |
|-----------------|---------------------------|
| EP-SP-010 (Limites, Politicas, Notificaciones) | US-SP-038 absorbida por EP-SP-029. Los eventos de limite (80%, excedido) son inputs del dispatcher |
| EP-SP-004 (SPEI Out) | Eventos SPEI_OUT_COMPLETED, SPEI_OUT_FAILED son inputs del dispatcher |
| EP-SP-005 (SPEI In / Webhook) | Eventos SPEI_IN son inputs del dispatcher |
| EP-SP-006 (Movimientos Internos) | Eventos INTERNAL_TRANSFER son inputs del dispatcher |
| EP-SP-009 (Reconciliacion) | Eventos RECONCILIATION_OK, DISCREPANCY_DETECTED son inputs del dispatcher |
| EP-SP-015 (Cash-In/Cash-Out) | Eventos CASH_IN_CONFIRMED, CASH_OUT_EXECUTED son inputs del dispatcher |
| EP-SP-016 (Subasta de Efectivo) | Evento AUCTION_NEW_AVAILABLE es input del dispatcher |
| EP-SP-021-022 (BillPay) | Eventos BILLPAY_COMPLETED, BILLPAY_FAILED son inputs del dispatcher |
| EP-SP-023 (Conciliacion BillPay) | Eventos de discrepancia BillPay son inputs del dispatcher |
| EP-SP-024 (Onboarding) | Eventos ACCOUNT_CREATED, ACCOUNT_FROZEN son inputs del dispatcher |
| EP-SP-017 (Agente IA WhatsApp) | covacha-botia es el canal de delivery para notificaciones WhatsApp |
| EP-SP-007 (mf-sp Scaffold) | Base para las pantallas frontend de EP-SP-030 |
| EP-SP-008 (Portal Admin Tier 1) | Contexto para el dashboard en tiempo real |
| EP-SP-011 (Portal B2B Tier 2) | Contexto para la configuracion de webhook |
| EP-SP-012 (Portal B2C Tier 3) | Contexto para las preferencias de notificacion |

---

## Arquitectura de Notificaciones

### Flujo General

```
Evento financiero (SPEI_IN, BILLPAY, CASH_OUT, etc.)
    |
    v
SQS: sp-notification-events (cola central de eventos)
    |
    v
Lambda: notification-dispatcher
    |
    +-- Lee NotificationPreferences de la org/usuario
    +-- Determina tier (Admin/B2B/B2C)
    +-- Resuelve canales por evento + tier + preferencias
    +-- Renderiza template por canal
    |
    +---> SQS: sp-notify-webhook     --> Lambda: webhook-sender     --> HTTP POST (B2B)
    +---> SQS: sp-notify-email       --> Lambda: email-sender       --> SES
    +---> SQS: sp-notify-whatsapp    --> covacha-botia              --> Meta WhatsApp API
    +---> SQS: sp-notify-sms         --> Lambda: sms-sender         --> SNS
    +---> SQS: sp-notify-slack       --> Lambda: slack-sender       --> Slack Webhook (Admin)
    +---> SSE endpoint               --> mf-sp dashboard            --> Tier 1 real-time
    |
    v
DynamoDB: NotificationAudit (registro de cada notificacion enviada)
```

### Modelo de Datos DynamoDB

```
# Preferencias de notificacion por organizacion
PK: ORG#{org_id}#NOTIF_PREFS
SK: GLOBAL                           # Preferencias globales de la org
SK: USER#{user_id}                   # Override por usuario
SK: EVENT#{event_type}               # Override por tipo de evento

# Templates de notificacion
PK: NOTIF_TEMPLATE
SK: {event_type}#{channel}#{locale}  # Ej: SPEI_IN#whatsapp#es_MX

# Configuracion de webhook outbound (B2B)
PK: ORG#{org_id}#WEBHOOK_CONFIG
SK: PRIMARY                          # Webhook principal
SK: FALLBACK                         # Webhook de respaldo

# Audit trail de notificaciones enviadas
PK: ORG#{org_id}#NOTIF_LOG
SK: {timestamp}#{notification_id}
GSI-1: PK=NOTIF#{notification_id}, SK=DETAIL  (lookup por ID)
GSI-2: PK=ORG#{org_id}#CHANNEL#{channel}, SK={timestamp}  (historial por canal)
GSI-3: PK=ORG#{org_id}#EVENT#{event_type}, SK={timestamp}  (historial por evento)

# Dead Letter (notificaciones fallidas)
PK: NOTIF_DLQ
SK: {timestamp}#{notification_id}
GSI: PK=NOTIF_DLQ#ORG#{org_id}, SK={timestamp}
```

### Canales por Tier

| Canal | Tier 1 (Admin) | Tier 2 (B2B) | Tier 3 (B2C) |
|-------|:-:|:-:|:-:|
| Dashboard SSE (tiempo real) | Si | - | - |
| Email digest diario | Si | - | - |
| Slack/Teams webhook | Si (CRITICAL) | - | - |
| Webhook HTTP (outbound) | - | Si | - |
| Email transaccional | - | Si | Si |
| WhatsApp (covacha-botia) | - | Opcional | Si (principal) |
| SMS (SNS) | - | Opcional (CRITICAL) | Si (OTP + alertas) |
| Push notification (futuro) | - | - | Futuro |

---

## Matriz de Eventos por Tier y Canal

### Tier 1 - Admin SuperPago

| Evento | Dashboard SSE | Email Digest | Slack/Teams |
|--------|:-:|:-:|:-:|
| SPEI_IN (> umbral) | Si + alerta | Resumen | Si |
| SPEI_OUT completado | Si | Resumen | - |
| SPEI_OUT fallido | Si + CRITICAL | Inmediato | Si |
| Internal transfer | Si | Resumen | - |
| Cash-In confirmado | Si | Resumen | - |
| Cash-Out ejecutado | Si | Resumen | - |
| BillPay completado | Si | Resumen | - |
| BillPay fallido | Si + alerta | Inmediato | Si |
| Limite alcanzado (80%) | Si + alerta | Inmediato | - |
| Limite excedido | Si + CRITICAL | Inmediato | Si |
| Conciliacion OK | Si | Reporte diario | - |
| Discrepancia detectada | Si + CRITICAL | Inmediato | Si |
| Cuenta creada | Si | Resumen | - |
| Cuenta congelada | Si + alerta | Inmediato | Si |
| Subasta nueva disponible | Si | Resumen | - |

### Tier 2 - Cliente Empresa (B2B)

| Evento | Webhook HTTP | Email | WhatsApp | SMS |
|--------|:-:|:-:|:-:|:-:|
| SPEI_IN | Si | Si | Opcional | - |
| SPEI_OUT completado | Si | Si | Opcional | - |
| SPEI_OUT fallido | Si | Si | Opcional | - |
| Internal transfer | Si | - | - | - |
| Cash-In confirmado | Si | - | - | - |
| Cash-Out ejecutado | Si | - | - | - |
| BillPay completado | Si | Si | Opcional | - |
| BillPay fallido | Si | Si | Opcional | - |
| Limite alcanzado (80%) | Si | Si | - | - |
| Limite excedido | Si | Si | - | Si |
| Conciliacion OK | - | Resumen | - | - |
| Discrepancia detectada | Si | - | - | - |
| Cuenta creada | Si | Si | - | - |
| Cuenta congelada | Si | Si | - | - |
| Subasta nueva disponible | Si | Si | - | - |

### Tier 3 - Usuario Final (B2C)

| Evento | WhatsApp | Email | SMS | Push (futuro) |
|--------|:-:|:-:|:-:|:-:|
| SPEI_IN | Si | - | - | Si |
| SPEI_OUT completado | Si | - | - | Si |
| SPEI_OUT fallido | Si | - | - | Si |
| Internal transfer | Si | - | - | - |
| Cash-In confirmado | Si | - | Si | - |
| Cash-Out ejecutado | Si | - | Si | - |
| BillPay completado | Si | - | - | Si |
| BillPay fallido | Si | - | - | Si |
| Limite alcanzado (80%) | Si | - | - | - |
| Limite excedido | Si | - | Si | - |
| Cuenta creada | Si (bienvenida) | - | - | - |
| Cuenta congelada | Si | - | Si | - |
| OTP Cash-Out generado | Si | - | Si | - |

---

## Mapa de Epicas Nuevas

| ID | Epica | Complejidad | Sprint Sugerido | Dependencias | Estado |
|----|-------|-------------|-----------------|--------------|--------|
| EP-SP-029 | Notificaciones Financieras Backend | XL | 12-14 | EP-SP-010, EP-SP-004, EP-SP-005, EP-SP-017 | **COMPLETADO (backend)** |
| EP-SP-030 | Frontend de Configuracion y Tiempo Real | L | 14-16 | EP-SP-029, EP-SP-007, EP-SP-008, EP-SP-011, EP-SP-012 | Planificacion |

---

## Epicas Detalladas

---

### EP-SP-029: Notificaciones Financieras Backend

> **Estado: COMPLETADO (backend)** — 38/38 tests passing. Commit: `7660ac1` en `covacha-notification/develop`. 2026-02-17.

**Descripcion:**
Sistema completo de notificaciones financieras en covacha-notification. Incluye modelo de preferencias de notificacion por organizacion y usuario, dispatcher central que enruta eventos financieros a los canales correctos segun tier y preferencias, webhook outbound HTTP para clientes B2B con firma HMAC y retry con backoff, integracion con SES (email), SNS (SMS), covacha-botia (WhatsApp) y Slack (admin), templates por canal y evento con soporte i18n, dead letter queue para notificaciones fallidas, y audit trail completo de todas las notificaciones enviadas.

**User Stories:**
- US-SP-117, US-SP-118, US-SP-119, US-SP-120, US-SP-121, US-SP-122, US-SP-123, US-SP-124

**Criterios de Aceptacion de la Epica:**
- [ ] Modelo `NotificationPreference` persistido en DynamoDB con granularidad org > usuario > evento
- [ ] Cola SQS `sp-notification-events` recibiendo eventos de todos los servicios financieros
- [ ] Lambda `notification-dispatcher` enrutando eventos a colas por canal
- [ ] Webhook outbound funcional: HTTP POST con HMAC-SHA256, retry 3 intentos, dead letter
- [ ] Email via SES funcional con templates HTML renderizados
- [ ] SMS via SNS funcional para OTPs y alertas criticas
- [ ] WhatsApp via covacha-botia funcional con templates Meta aprobados
- [ ] Slack/Teams webhook funcional para alertas CRITICAL a equipo admin
- [ ] Templates cargados desde DynamoDB con cache, editables sin deploy
- [ ] Endpoint SSE para dashboard Tier 1 en tiempo real
- [ ] Dead Letter Queue con visibilidad y retry manual
- [ ] Audit trail de toda notificacion enviada, queryable por org, canal, evento, fecha
- [ ] Los 16 tipos de evento financiero procesados correctamente
- [ ] Preferencias respetadas: si usuario desactiva canal, no se envia
- [ ] Tests >= 98% coverage
- [ ] Metricas: latencia de entrega por canal, tasa de fallo, DLQ depth

**Dependencias:**
- EP-SP-010 (Limites y Politicas - genera eventos de limite)
- EP-SP-004/005 (SPEI In/Out - genera eventos SPEI)
- EP-SP-017 (Agente IA WhatsApp / covacha-botia - canal de delivery)
- EP-SP-015 (Cash In/Out - genera eventos cash)
- EP-SP-021/022 (BillPay - genera eventos billpay)
- EP-SP-024 (Onboarding - genera eventos de cuenta)

**Complejidad:** XL (sistema multi-canal, multi-tier, multiples integraciones externas)

**Repositorio:** `covacha-notification`

---

### EP-SP-030: Frontend de Configuracion y Tiempo Real

**Descripcion:**
Pantallas frontend en `mf-sp` para los 3 tiers del sistema de notificaciones. Tier 1 (Admin): dashboard en tiempo real via SSE con alertas CRITICAL destacadas y email digest configurable. Tier 2 (B2B): configurador de webhook URL con test de conectividad, selector de canales por evento, y visor de historial de entregas. Tier 3 (B2C): preferencias simples (WhatsApp si/no, email si/no, SMS si/no) con preview de ejemplo. Todos los tiers: historial de notificaciones enviadas con filtros y detalle.

**User Stories:**
- US-SP-125, US-SP-126, US-SP-127, US-SP-128, US-SP-129, US-SP-130

**Criterios de Aceptacion de la Epica:**
- [ ] Tier 1: Dashboard `/sp/admin/notifications` con feed SSE en tiempo real
- [ ] Tier 1: Alertas CRITICAL resaltadas con sonido/visual prominente
- [ ] Tier 1: Configuracion de email digest (frecuencia, horario, destinatarios)
- [ ] Tier 1: Configuracion de webhook Slack/Teams
- [ ] Tier 2: Pagina `/sp/business/settings/notifications` con configuracion de webhook
- [ ] Tier 2: Test de conectividad de webhook con resultado visual
- [ ] Tier 2: Selector granular de canales por tipo de evento (tabla interactiva)
- [ ] Tier 2: Historial de entregas webhook con status (200, 4xx, 5xx, timeout)
- [ ] Tier 3: Pagina `/sp/personal/settings/notifications` con toggles simples
- [ ] Tier 3: Preview de como se vera la notificacion en cada canal
- [ ] Todos: Historial de notificaciones con filtros (tipo, canal, fecha, estado)
- [ ] Todos: Detalle de notificacion individual (payload, timestamp, estado de entrega)
- [ ] Responsive design (mobile-first para Tier 3)
- [ ] Tests >= 98% coverage

**Dependencias:**
- EP-SP-029 (APIs de notificaciones, SSE endpoint, preferencias)
- EP-SP-007 (mf-sp scaffold y arquitectura multi-tier)
- EP-SP-008 (Portal Admin Tier 1 - layout y guards)
- EP-SP-011 (Portal B2B Tier 2 - layout y guards)
- EP-SP-012 (Portal B2C Tier 3 - layout y guards)
- EP-SP-013 (Componentes compartidos entre tiers)

**Complejidad:** L (6 pantallas con interactividad alta, SSE real-time, configuracion granular)

**Repositorio:** `mf-sp`

---

## User Stories Detalladas

---

### EP-SP-029: Notificaciones Financieras Backend

---

#### US-SP-117: Modelo de Preferencias de Notificacion

**ID:** US-SP-117
**Epica:** EP-SP-029
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero persistir las preferencias de notificacion de cada organizacion y sus usuarios para que el dispatcher sepa a que canales enviar cada tipo de evento, respetando las elecciones del cliente.

**Criterios de Aceptacion:**
- [ ] Dataclass `NotificationPreference` con campos:
  - `sp_organization_id`: string (PK parcial)
  - `scope`: GLOBAL | USER | EVENT (nivel de granularidad)
  - `scope_id`: string (user_id o event_type segun scope)
  - `tier`: ADMIN | B2B | B2C
  - `channels`: dict con estructura por canal:
    - `webhook`: `{ enabled: bool, url: str, secret: str, headers: dict, events: list[str] }`
    - `email`: `{ enabled: bool, recipients: list[str], events: list[str] }`
    - `whatsapp`: `{ enabled: bool, phone_number: str, events: list[str] }`
    - `sms`: `{ enabled: bool, phone_number: str, events: list[str] }`
    - `slack`: `{ enabled: bool, webhook_url: str, channel: str, events: list[str] }`
    - `sse`: `{ enabled: bool }`
  - `quiet_hours`: `{ enabled: bool, start: str, end: str, timezone: str }` (no enviar durante horas silenciosas, excepto CRITICAL)
  - `created_at`, `updated_at`: timestamps
- [ ] Persistencia en DynamoDB:
  - `PK: ORG#{org_id}#NOTIF_PREFS`, `SK: GLOBAL` para preferencias globales de la org
  - `PK: ORG#{org_id}#NOTIF_PREFS`, `SK: USER#{user_id}` para override por usuario
  - `PK: ORG#{org_id}#NOTIF_PREFS`, `SK: EVENT#{event_type}` para override por evento
- [ ] Resolucion de preferencias con herencia:
  1. Buscar override por usuario + evento especifico
  2. Si no existe, buscar override por usuario (todos los eventos)
  3. Si no existe, buscar override por evento (todos los usuarios)
  4. Si no existe, usar preferencia GLOBAL de la org
  5. Si no existe, usar defaults del tier
- [ ] Defaults por tier pre-cargados al crear organizacion:
  - Tier 1 (Admin): SSE=on, email_digest=on, slack=off (requiere config)
  - Tier 2 (B2B): webhook=off (requiere config), email=on, whatsapp=off, sms=off
  - Tier 3 (B2C): whatsapp=on, email=off, sms=off
- [ ] Endpoints REST:
  - `GET /api/v1/organizations/{org_id}/notification-preferences` (lista todas)
  - `GET /api/v1/organizations/{org_id}/notification-preferences/resolve?user_id=X&event_type=Y` (resuelve con herencia)
  - `PUT /api/v1/organizations/{org_id}/notification-preferences` (upsert global)
  - `PUT /api/v1/organizations/{org_id}/notification-preferences/users/{user_id}` (upsert usuario)
  - `PUT /api/v1/organizations/{org_id}/notification-preferences/events/{event_type}` (upsert evento)
  - `DELETE /api/v1/organizations/{org_id}/notification-preferences/users/{user_id}` (eliminar override)
- [ ] Validacion de webhook URL: formato HTTPS, no localhost en produccion, no IPs privadas
- [ ] Validacion de phone_number: formato E.164
- [ ] Validacion de email: formato valido
- [ ] Cache en memoria de preferencias con TTL de 5 minutos (el dispatcher consulta frecuentemente)

**Tareas Tecnicas:**
1. Crear dataclass `NotificationPreference` con validaciones
2. Crear dataclass `ChannelConfig` (webhook, email, whatsapp, sms, slack, sse)
3. Implementar `NotificationPreferenceRepository` (DynamoDB CRUD)
4. Implementar `PreferenceResolver` con logica de herencia
5. Crear Flask Blueprint `notification_preferences_bp`
6. Implementar cache en memoria con invalidacion
7. Defaults por tier al crear organizacion (integracion con onboarding)
8. Tests: herencia, defaults, validaciones, cache invalidation, CRUD

**Dependencias:** Ninguna (es la base de todo el sistema)
**Estimacion:** 5 dev-days

---

#### US-SP-118: Dispatcher Central de Eventos

**ID:** US-SP-118
**Epica:** EP-SP-029
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero un dispatcher que reciba eventos financieros desde una cola SQS, determine los destinatarios y canales correctos por tier y preferencias, y enrute cada notificacion a la cola del canal correspondiente, para que cada stakeholder reciba las notificaciones que le corresponden por el canal adecuado.

**Criterios de Aceptacion:**
- [ ] Cola SQS `sp-notification-events` como punto de entrada unico:
  - Todos los servicios (covacha-transaction, covacha-core, covacha-payment) publican eventos aqui
  - Formato del mensaje:
    ```json
    {
      "event_id": "uuid",
      "event_type": "SPEI_IN | SPEI_OUT_COMPLETED | SPEI_OUT_FAILED | INTERNAL_TRANSFER | CASH_IN_CONFIRMED | CASH_OUT_EXECUTED | BILLPAY_COMPLETED | BILLPAY_FAILED | LIMIT_REACHED_80 | LIMIT_EXCEEDED | RECONCILIATION_OK | DISCREPANCY_DETECTED | ACCOUNT_CREATED | ACCOUNT_FROZEN | AUCTION_NEW | OTP_CASH_OUT",
      "sp_organization_id": "string",
      "user_id": "string (opcional, para B2C)",
      "tier": "ADMIN | B2B | B2C",
      "severity": "INFO | WARNING | CRITICAL",
      "payload": { ... },
      "timestamp": "ISO 8601",
      "idempotency_key": "string"
    }
    ```
- [ ] Lambda `notification-dispatcher`:
  1. Deserializa evento desde SQS
  2. Valida schema del evento
  3. Resuelve preferencias via `PreferenceResolver` (US-SP-117)
  4. Determina canales activos para este evento + tier + usuario
  5. Renderiza template por canal (US-SP-120)
  6. Publica mensaje en la cola SQS de cada canal:
     - `sp-notify-webhook`: para webhook HTTP
     - `sp-notify-email`: para SES
     - `sp-notify-whatsapp`: para covacha-botia
     - `sp-notify-sms`: para SNS
     - `sp-notify-slack`: para Slack/Teams
  7. Para SSE: publica en Redis/ElastiCache pub/sub (consumido por endpoint SSE)
  8. Registra en NotificationAudit (US-SP-124)
- [ ] Idempotencia: mismo `event_id` no genera notificaciones duplicadas
  - Tabla de idempotencia con TTL de 24 horas
- [ ] Quiet hours: si esta configurado y no es CRITICAL, encola para envio al finalizar quiet hours
- [ ] Batch processing: procesa hasta 10 mensajes SQS por invocacion
- [ ] Error handling:
  - Si falla la resolucion de preferencias: usar defaults del tier, logear warning
  - Si falla el encolado a canal: retry 2 veces, si falla → DLQ del dispatcher
  - Si el evento es desconocido: logear error, enviar a DLQ
- [ ] Metricas CloudWatch:
  - `NotificationsDispatched` (por event_type, tier, channel)
  - `DispatcherErrors` (por error_type)
  - `DispatchLatencyMs` (tiempo de procesamiento)

**Tareas Tecnicas:**
1. Crear cola SQS `sp-notification-events` con DLQ
2. Crear 5 colas SQS de canales (webhook, email, whatsapp, sms, slack) cada una con DLQ
3. Implementar Lambda `notification-dispatcher`
4. Implementar `EventValidator` con schema validation
5. Implementar logica de routing por tier + preferencias
6. Implementar tabla de idempotencia en DynamoDB
7. Implementar quiet hours con scheduling
8. Publicacion a Redis/ElastiCache para SSE
9. Metricas CloudWatch custom
10. Tests: routing por tier, idempotencia, quiet hours, errores, batch processing

**Dependencias:** US-SP-117 (preferencias)
**Estimacion:** 6 dev-days

---

#### US-SP-119: Webhook Outbound para Clientes B2B

**ID:** US-SP-119
**Epica:** EP-SP-029
**Prioridad:** P0

**Historia:**
Como **Cliente Empresa (B2B)** quiero recibir eventos financieros en mi endpoint HTTP configurado para integrar las notificaciones de SuperPago con mis sistemas internos (ERP, contabilidad, monitoreo) de forma automatica y segura.

**Criterios de Aceptacion:**
- [ ] Lambda `webhook-sender` consume cola `sp-notify-webhook`:
  - Lee configuracion del webhook desde DynamoDB (`ORG#{org_id}#WEBHOOK_CONFIG`)
  - Construye payload JSON estandarizado:
    ```json
    {
      "event_id": "uuid",
      "event_type": "SPEI_IN",
      "timestamp": "2026-02-14T10:30:00Z",
      "sp_organization_id": "string",
      "data": {
        "amount": 50000.00,
        "currency": "MXN",
        "sender_name": "Empresa ABC",
        "sender_clabe": "012180000000000001",
        "reference": "Pago factura 1234",
        "tracking_key": "...",
        "account_id": "..."
      }
    }
    ```
- [ ] Firma HMAC-SHA256:
  - Header: `X-SuperPago-Signature: sha256={hmac_hex}`
  - Body del HMAC: raw JSON body del POST
  - Secret: almacenado encriptado en DynamoDB, configurable por org
  - Header adicional: `X-SuperPago-Timestamp: {unix_timestamp}` (anti-replay)
- [ ] Headers personalizables por organizacion (hasta 5 custom headers)
- [ ] HTTP POST con timeout de 10 segundos
- [ ] Retry con backoff exponencial:
  - Intento 1: inmediato
  - Intento 2: +30 segundos
  - Intento 3: +120 segundos
  - Despues de 3 fallos: enviar a `sp-notify-webhook-dlq`
- [ ] Clasificacion de errores:
  - 2xx: exito, registrar en audit
  - 4xx (excepto 429): no reintentar, registrar como `CLIENT_ERROR`
  - 429: reintentar respetando `Retry-After` header
  - 5xx: reintentar
  - Timeout: reintentar
  - DNS failure: no reintentar, registrar como `ENDPOINT_UNREACHABLE`
- [ ] Circuit breaker por organizacion:
  - Si 5 fallos consecutivos en 1 hora: abrir circuito, pausar entregas
  - Registrar estado de circuito en DynamoDB
  - Alertar a equipo admin (evento WEBHOOK_CIRCUIT_OPEN)
  - Retry automatico cada 15 minutos con 1 mensaje de prueba
  - Si exito: cerrar circuito, reanudar entregas
- [ ] Endpoint de test: `POST /api/v1/organizations/{org_id}/webhook/test`
  - Envia evento de prueba (`event_type: WEBHOOK_TEST`)
  - Retorna resultado del HTTP POST (status code, response time, headers)
- [ ] Registro en audit trail: cada intento (exito o fallo) con status code, latencia, error

**Tareas Tecnicas:**
1. Crear Lambda `webhook-sender` con SQS trigger
2. Implementar firma HMAC-SHA256 con timestamp anti-replay
3. Implementar retry con backoff exponencial (SQS visibility timeout)
4. Implementar circuit breaker con estado en DynamoDB
5. Implementar clasificacion de errores HTTP
6. Endpoint de test de webhook
7. Encriptacion del secret con KMS
8. Tests: firma HMAC, retry, circuit breaker, clasificacion de errores, test endpoint

**Dependencias:** US-SP-118 (dispatcher enruta a cola webhook)
**Estimacion:** 5 dev-days

---

#### US-SP-120: Templates de Notificacion por Canal y Evento

**ID:** US-SP-120
**Epica:** EP-SP-029
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero renderizar notificaciones con templates especificos por canal y tipo de evento para que cada notificacion tenga el formato, tono y nivel de detalle apropiado para su canal de entrega (un WhatsApp es corto y directo, un email tiene mas detalle, un webhook es JSON estructurado).

**Criterios de Aceptacion:**
- [ ] Modelo `NotificationTemplate` en DynamoDB:
  - `PK: NOTIF_TEMPLATE`, `SK: {event_type}#{channel}#{locale}`
  - Campos: `subject` (email), `body_template` (Jinja2/Mustache), `metadata`
  - Ejemplo SK: `SPEI_IN#whatsapp#es_MX`, `SPEI_IN#email#es_MX`, `SPEI_OUT_FAILED#sms#es_MX`
- [ ] Motor de templates con variables de contexto:
  - Variables globales: `{{org_name}}`, `{{timestamp}}`, `{{event_type}}`
  - Variables por evento: `{{amount}}`, `{{currency}}`, `{{sender_name}}`, `{{reference}}`, etc.
  - Formateo: `{{amount|currency}}` → "$50,000.00 MXN", `{{timestamp|datetime}}` → "14 Feb 2026, 10:30"
- [ ] Templates por canal:
  - **WhatsApp**: Template aprobado por Meta, maximo 1024 chars, con botones opcionales
    - Ejemplo SPEI_IN: "Recibiste un deposito de {{amount|currency}} de {{sender_name}}. Ref: {{reference}}. Saldo: {{balance|currency}}"
  - **Email**: HTML con header, cuerpo, footer, logo de la org, boton CTA
    - Ejemplo SPEI_IN: email completo con tabla de detalle de la operacion
  - **SMS**: Texto plano, maximo 160 chars
    - Ejemplo OTP: "SuperPago: Tu codigo para retiro de efectivo es {{otp_code}}. Valido por 5 minutos. No compartas este codigo."
  - **Slack**: Mensaje con attachments/blocks
    - Ejemplo CRITICAL: bloque rojo con detalle del evento critico
  - **Webhook**: JSON estructurado (ya definido en US-SP-119)
- [ ] Templates seed: conjunto inicial de templates para los 16 eventos x canales aplicables
  - Total estimado: ~45 templates (no todos los eventos usan todos los canales)
- [ ] Cache de templates en memoria con TTL de 10 minutos
- [ ] Fallback: si no existe template para locale, usar `es_MX` como default
- [ ] Endpoint de administracion (solo Tier 1):
  - `GET /api/v1/notification-templates` (lista todos)
  - `GET /api/v1/notification-templates/{event_type}/{channel}/{locale}` (uno especifico)
  - `PUT /api/v1/notification-templates/{event_type}/{channel}/{locale}` (crear/editar)
  - `POST /api/v1/notification-templates/{event_type}/{channel}/{locale}/preview` (preview renderizado con datos de ejemplo)
- [ ] Validacion de templates:
  - WhatsApp: validar longitud y formato Meta
  - SMS: validar longitud <= 160 chars (o multi-part)
  - Email: validar HTML bien formado
  - Variables: validar que las variables usadas existen en el contexto del evento

**Tareas Tecnicas:**
1. Crear dataclass `NotificationTemplate`
2. Implementar `TemplateRepository` (DynamoDB CRUD)
3. Implementar `TemplateRenderer` con motor Jinja2
4. Implementar filtros custom (currency, datetime, truncate)
5. Crear seed de ~45 templates iniciales
6. Cache en memoria con TTL
7. Flask Blueprint de administracion de templates
8. Endpoint de preview
9. Validaciones por canal
10. Tests: renderizado, filtros, cache, validaciones, fallback locale

**Dependencias:** Ninguna (puede desarrollarse en paralelo con US-SP-117 y US-SP-118)
**Estimacion:** 5 dev-days

---

#### US-SP-121: Canal Email via SES

**ID:** US-SP-121
**Epica:** EP-SP-029
**Prioridad:** P1

**Historia:**
Como **Sistema** quiero enviar notificaciones por email via Amazon SES con templates HTML profesionales para que los usuarios B2B y B2C reciban confirmaciones, alertas y resumenes de sus operaciones financieras en su correo electronico.

**Criterios de Aceptacion:**
- [ ] Lambda `email-sender` consume cola `sp-notify-email`:
  - Lee template renderizado del mensaje SQS
  - Envia via SES `send_email()`:
    - From: `notificaciones@superpago.com.mx` (verificado en SES)
    - To: destinatario(s) del mensaje
    - Subject: del template
    - Body HTML: del template renderizado
    - Body Text: version plain-text auto-generada
- [ ] Tipos de email:
  - **Transaccional**: inmediato (SPEI confirmado, BillPay completado, alerta)
  - **Digest**: agregado (resumen diario para Tier 1, resumen semanal opcional para Tier 2)
- [ ] Email digest (Tier 1 Admin):
  - Lambda programada (EventBridge, cron diario 8:00 AM CST)
  - Agrega todos los eventos de las ultimas 24 horas
  - Genera reporte con:
    - Resumen: total de transacciones, monto total, alertas CRITICAL
    - Top eventos por tipo
    - Eventos CRITICAL destacados
    - Graficas inline (imagenes generadas o links a dashboard)
  - Destinatarios configurables en preferencias
- [ ] Bounce/Complaint handling:
  - SES notifications → SNS → Lambda que actualiza preferencias
  - Si bounce permanente: desactivar email para ese destinatario
  - Si complaint: desactivar email + alertar equipo
- [ ] Rate limiting: maximo 14 emails/segundo (limite SES por defecto, ajustable)
- [ ] Registro en audit trail: message_id de SES, estado, bounce/delivery info

**Tareas Tecnicas:**
1. Crear Lambda `email-sender` con SQS trigger
2. Configurar SES: identidad verificada, DKIM, SPF, DMARC
3. Implementar envio transaccional
4. Implementar Lambda de email digest con EventBridge cron
5. Implementar agregacion de eventos para digest
6. Configurar SNS notifications para bounces/complaints
7. Lambda de bounce handler
8. Tests: envio mock, digest aggregation, bounce handling

**Dependencias:** US-SP-118 (dispatcher enruta a cola email), US-SP-120 (templates)
**Estimacion:** 4 dev-days

---

#### US-SP-122: Canal WhatsApp via covacha-botia y Canal SMS via SNS

**ID:** US-SP-122
**Epica:** EP-SP-029
**Prioridad:** P1

**Historia:**
Como **Sistema** quiero enviar notificaciones via WhatsApp (usando covacha-botia como proxy a Meta API) y via SMS (usando SNS) para que los usuarios B2C reciban alertas en tiempo real en sus canales principales, y los clientes B2B puedan optar por WhatsApp como canal complementario.

**Criterios de Aceptacion:**
- [ ] **WhatsApp** - Lambda `whatsapp-sender` consume cola `sp-notify-whatsapp`:
  - Publica mensaje en la cola de covacha-botia (no llama a Meta API directamente):
    ```json
    {
      "phone_number": "+5215512345678",
      "template_name": "spei_deposit_notification",
      "template_language": "es_MX",
      "template_parameters": ["$50,000.00", "Empresa ABC", "Pago factura 1234"],
      "sp_organization_id": "...",
      "notification_id": "..."
    }
    ```
  - covacha-botia se encarga de la comunicacion con Meta API
  - Recibe callback de covacha-botia con status (sent, delivered, read, failed)
- [ ] Templates WhatsApp deben estar pre-aprobados en Meta Business Manager:
  - Cada nuevo template requiere aprobacion (proceso manual, 24-48 horas)
  - Mantener catalogo de templates aprobados en DynamoDB
  - Si template no aprobado: no intentar enviar, registrar error en audit
- [ ] **SMS** - Lambda `sms-sender` consume cola `sp-notify-sms`:
  - Envia via SNS `publish()`:
    - PhoneNumber: formato E.164
    - Message: texto del template (max 160 chars por segmento)
    - MessageAttributes: `{ "AWS.SNS.SMS.SMSType": "Transactional" }` (para OTPs y alertas)
  - Sender ID: "SuperPago" (registrado en SNS)
- [ ] Tipos de SMS:
  - **Transactional** (alta prioridad): OTPs, alertas de seguridad (cuenta congelada, limite excedido)
  - **Promotional** (baja prioridad): no usado actualmente, reservado para futuro
- [ ] Rate limiting:
  - WhatsApp: respetar limites de Meta por numero de negocio (1000/dia tier 1, escalable)
  - SMS: respetar limites de SNS por region (20 SMS/segundo default)
- [ ] Opt-out handling:
  - WhatsApp: si usuario responde "STOP" → covacha-botia notifica → desactivar canal
  - SMS: SNS gestiona opt-out automaticamente (respuesta "STOP")
  - Actualizar preferencias automaticamente
- [ ] Registro en audit trail: message_id, canal, status, timestamp de entrega

**Tareas Tecnicas:**
1. Crear Lambda `whatsapp-sender` con SQS trigger
2. Implementar integracion con cola de covacha-botia
3. Crear Lambda `sms-sender` con SQS trigger
4. Implementar envio via SNS
5. Implementar callback handler para status updates de WhatsApp
6. Implementar opt-out handler (WhatsApp STOP, SMS STOP)
7. Catalogo de templates Meta aprobados en DynamoDB
8. Tests: envio mock WhatsApp, envio mock SMS, opt-out, rate limiting

**Dependencias:** US-SP-118 (dispatcher enruta a colas), US-SP-120 (templates), covacha-botia (canal WhatsApp existente)
**Estimacion:** 5 dev-days

---

#### US-SP-123: Canal Slack/Teams y Endpoint SSE para Dashboard Tier 1

**ID:** US-SP-123
**Epica:** EP-SP-029
**Prioridad:** P1

**Historia:**
Como **Administrador de SuperPago (Tier 1)** quiero recibir alertas CRITICAL en Slack/Teams y ver un feed en tiempo real de eventos en mi dashboard para reaccionar inmediatamente a incidentes financieros (SPEI fallido, discrepancia, cuenta congelada, limite excedido).

**Criterios de Aceptacion:**
- [ ] **Slack/Teams Webhook** - Lambda `slack-sender` consume cola `sp-notify-slack`:
  - Solo procesa eventos con severity CRITICAL o WARNING
  - HTTP POST al webhook URL configurado en preferencias del admin
  - Formato Slack Block Kit:
    ```json
    {
      "blocks": [
        {
          "type": "header",
          "text": { "type": "plain_text", "text": "ALERTA CRITICAL: SPEI Out Fallido" }
        },
        {
          "type": "section",
          "fields": [
            { "type": "mrkdwn", "text": "*Organizacion:*\nBoxito S.A." },
            { "type": "mrkdwn", "text": "*Monto:*\n$50,000.00 MXN" },
            { "type": "mrkdwn", "text": "*Error:*\nINSUFFICIENT_FUNDS" },
            { "type": "mrkdwn", "text": "*Timestamp:*\n2026-02-14 10:30:00 CST" }
          ]
        },
        {
          "type": "actions",
          "elements": [
            {
              "type": "button",
              "text": { "type": "plain_text", "text": "Ver en Dashboard" },
              "url": "https://app.superpago.com.mx/sp/admin/notifications?event_id=..."
            }
          ]
        }
      ]
    }
    ```
  - Soporte para Microsoft Teams (formato Adaptive Card como alternativa)
- [ ] **Endpoint SSE** para dashboard Tier 1:
  - `GET /api/v1/admin/notifications/stream` (Server-Sent Events)
  - Autenticacion: Bearer token con permiso `sp:admin`
  - El dispatcher (US-SP-118) publica eventos a Redis/ElastiCache pub/sub
  - El endpoint SSE suscribe al canal Redis `sp-notifications:{org_id}` y emite al cliente
  - Formato SSE:
    ```
    event: notification
    data: {"event_id":"...","event_type":"SPEI_OUT_FAILED","severity":"CRITICAL","payload":{...},"timestamp":"..."}

    event: heartbeat
    data: {"timestamp":"..."}
    ```
  - Heartbeat cada 30 segundos para mantener conexion viva
  - Reconexion automatica: header `Last-Event-ID` para resumir desde ultimo evento
  - Maximo 100 conexiones SSE concurrentes (limite configurable)
- [ ] Filtrado SSE:
  - Query param `?severity=CRITICAL,WARNING` para filtrar por severidad
  - Query param `?event_types=SPEI_OUT_FAILED,DISCREPANCY_DETECTED` para filtrar por tipo
- [ ] Fallback: si Redis no disponible, el dashboard puede hacer polling cada 10 segundos via REST

**Tareas Tecnicas:**
1. Crear Lambda `slack-sender` con SQS trigger
2. Implementar formato Slack Block Kit y Teams Adaptive Card
3. Implementar endpoint SSE en Flask (con streaming response)
4. Configurar Redis/ElastiCache pub/sub
5. Implementar publicacion del dispatcher a Redis
6. Implementar heartbeat y reconexion con Last-Event-ID
7. Implementar filtrado por severity y event_type
8. Tests: formato Slack, SSE streaming, Redis pub/sub, filtrado, reconexion

**Dependencias:** US-SP-118 (dispatcher publica a cola slack y a Redis)
**Estimacion:** 5 dev-days

---

#### US-SP-124: Audit Trail y Dead Letter Queue

**ID:** US-SP-124
**Epica:** EP-SP-029
**Prioridad:** P1

**Historia:**
Como **Administrador de SuperPago** quiero un registro completo de todas las notificaciones enviadas y un sistema de gestion de entregas fallidas para auditar la comunicacion con clientes, diagnosticar problemas de entrega, y reintentar notificaciones que no llegaron a su destino.

**Criterios de Aceptacion:**
- [ ] Modelo `NotificationAudit` en DynamoDB:
  - `PK: ORG#{org_id}#NOTIF_LOG`, `SK: {timestamp}#{notification_id}`
  - Campos:
    - `notification_id`: UUID
    - `event_id`: ID del evento fuente
    - `event_type`: tipo de evento
    - `sp_organization_id`: org destino
    - `user_id`: usuario destino (si aplica)
    - `tier`: ADMIN | B2B | B2C
    - `channel`: webhook | email | whatsapp | sms | slack | sse
    - `status`: SENT | DELIVERED | FAILED | BOUNCED | REJECTED | PENDING
    - `attempts`: lista de intentos `[{ timestamp, status_code, error, latency_ms }]`
    - `template_id`: template usado
    - `payload_hash`: SHA256 del payload (no almacenar PII en audit)
    - `created_at`, `delivered_at`, `failed_at`: timestamps
  - GSI-1: `PK=NOTIF#{notification_id}`, `SK=DETAIL` (lookup rapido por ID)
  - GSI-2: `PK=ORG#{org_id}#CHANNEL#{channel}`, `SK={timestamp}` (historial por canal)
  - GSI-3: `PK=ORG#{org_id}#EVENT#{event_type}`, `SK={timestamp}` (historial por evento)
  - TTL: 90 dias (configurable, compliance requirement)
- [ ] Cada Lambda sender (webhook, email, whatsapp, sms, slack) actualiza el audit:
  - Al enviar: status=SENT
  - Al confirmar delivery: status=DELIVERED (via callback o SES notification)
  - Al fallar: status=FAILED con detalle del error
- [ ] Dead Letter Queue (DLQ):
  - Cada cola de canal tiene su DLQ
  - `sp-notify-webhook-dlq`, `sp-notify-email-dlq`, etc.
  - Persistencia en DynamoDB:
    - `PK: NOTIF_DLQ`, `SK: {timestamp}#{notification_id}`
    - `GSI: PK=NOTIF_DLQ#ORG#{org_id}`, `SK={timestamp}`
  - Campos adicionales: `original_message`, `error_reason`, `retry_count`, `can_retry`
- [ ] Endpoints de consulta (Tier 1):
  - `GET /api/v1/admin/notifications/audit?org_id=X&channel=Y&event_type=Z&from=&to=&status=`
  - `GET /api/v1/admin/notifications/audit/{notification_id}` (detalle con intentos)
  - `GET /api/v1/admin/notifications/dlq?org_id=X&channel=Y`
  - `POST /api/v1/admin/notifications/dlq/{notification_id}/retry` (reenvio manual)
  - `DELETE /api/v1/admin/notifications/dlq/{notification_id}` (descartar)
  - `POST /api/v1/admin/notifications/dlq/retry-all?org_id=X&channel=Y` (reenvio masivo)
- [ ] Endpoints de consulta (Tier 2 y Tier 3, solo sus propias notificaciones):
  - `GET /api/v1/organizations/{org_id}/notifications?channel=Y&event_type=Z&from=&to=`
  - `GET /api/v1/organizations/{org_id}/notifications/{notification_id}`
- [ ] Metricas de salud del sistema:
  - `GET /api/v1/admin/notifications/health`
  - Response: profundidad de cada DLQ, tasa de entrega por canal (ultimas 24h), alertas activas
- [ ] Alarma CloudWatch: si DLQ depth > 50 mensajes → alerta CRITICAL al equipo

**Tareas Tecnicas:**
1. Crear dataclass `NotificationAudit` y `DLQEntry`
2. Implementar `NotificationAuditRepository` con DynamoDB y GSIs
3. Implementar `DLQRepository`
4. Integrar registro de audit en cada Lambda sender
5. Implementar endpoints REST de consulta (admin y org)
6. Implementar retry manual desde DLQ
7. Implementar retry masivo
8. Configurar alarmas CloudWatch para DLQ depth
9. Endpoint de health check
10. Tests: audit CRUD, DLQ retry, metricas, alarmas, permisos por tier

**Dependencias:** US-SP-118 (dispatcher), US-SP-119 (webhook sender), US-SP-121 (email sender), US-SP-122 (whatsapp/sms sender), US-SP-123 (slack sender)
**Estimacion:** 5 dev-days

---

### EP-SP-030: Frontend de Configuracion y Tiempo Real

---

#### US-SP-125: Dashboard de Notificaciones en Tiempo Real (Tier 1 Admin)

**ID:** US-SP-125
**Epica:** EP-SP-030
**Prioridad:** P0

**Historia:**
Como **Administrador de SuperPago** quiero ver un dashboard en tiempo real con todos los eventos financieros del ecosistema, con alertas CRITICAL destacadas visualmente, para monitorear la salud operativa de la plataforma y reaccionar inmediatamente a incidentes.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/admin/notifications` con 3 secciones:
  1. **Feed en Tiempo Real** (principal, 60% del viewport):
     - Conecta al endpoint SSE `/api/v1/admin/notifications/stream`
     - Muestra eventos como tarjetas en scroll infinito (mas recientes arriba)
     - Tarjeta por evento: tipo, severidad (badge color), org, monto, timestamp, canal de entrega
     - Colores: CRITICAL=rojo, WARNING=amarillo, INFO=gris
     - Eventos CRITICAL aparecen con animacion de pulso y sonido configurable
     - Filtros: por severidad, por tipo de evento, por organizacion
     - Indicador de conexion SSE (conectado/desconectado/reconectando)
  2. **Metricas Resumen** (sidebar derecho, 20%):
     - Total de notificaciones hoy
     - Desglose por canal (webhook: X, email: X, whatsapp: X, sms: X)
     - Tasa de entrega por canal (% exito)
     - DLQ depth actual por canal
     - Alertas CRITICAL activas (count con badge)
  3. **Configuracion Admin** (tab secundario):
     - Email digest: frecuencia (diario/semanal), horario, destinatarios
     - Slack webhook URL + test de conectividad
     - Umbrales de alerta (monto > X → CRITICAL)
- [ ] Componentes standalone OnPush:
  - `NotificationFeedComponent` (feed SSE con tarjetas)
  - `NotificationCardComponent` (tarjeta individual de evento)
  - `NotificationMetricsSidebarComponent` (metricas resumen)
  - `AdminNotificationConfigComponent` (configuracion)
  - `SseConnectionIndicatorComponent` (estado de conexion SSE)
- [ ] Reconexion automatica SSE: si se pierde conexion, reconectar con backoff (1s, 2s, 4s, 8s, max 30s)
- [ ] Persistencia del ultimo `Last-Event-ID` en localStorage para no perder eventos al recargar
- [ ] Responsive: en mobile, feed ocupa 100% y metricas colapsan a un drawer
- [ ] data-cy attributes en todos los elementos interactivos
- [ ] Tests >= 98%

**Tareas Tecnicas:**
1. Crear pagina `admin-notifications.page.ts` con routing
2. Crear `NotificationFeedComponent` con EventSource API y reconexion
3. Crear `NotificationCardComponent` con colores por severidad
4. Crear `NotificationMetricsSidebarComponent` con polling de metricas
5. Crear `AdminNotificationConfigComponent` con formularios
6. Crear `SseConnectionIndicatorComponent`
7. Implementar servicio `SseService` reutilizable
8. Crear adapter `notification-admin.adapter.ts`
9. Tests: SSE mock, feed rendering, filtros, reconexion, responsive

**Dependencias:** US-SP-123 (endpoint SSE), US-SP-124 (endpoints de metricas), EP-SP-008 (layout Admin)
**Estimacion:** 6 dev-days

---

#### US-SP-126: DLQ Viewer y Retry Manual (Tier 1 Admin)

**ID:** US-SP-126
**Epica:** EP-SP-030
**Prioridad:** P1

**Historia:**
Como **Administrador de SuperPago** quiero ver las notificaciones fallidas en la Dead Letter Queue, entender por que fallaron, y poder reintentarlas manualmente o descartarlas, para asegurar que ningun evento critico se pierda sin atencion.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/admin/notifications/dlq` con:
  1. **Tabla de DLQ** con columnas:
     - Canal (webhook/email/whatsapp/sms/slack)
     - Evento tipo + evento ID
     - Organizacion destino
     - Error (mensaje resumido)
     - Intentos realizados
     - Timestamp del ultimo intento
     - Acciones: Retry, Descartar, Ver Detalle
  2. **Filtros**: por canal, por organizacion, por fecha
  3. **Acciones masivas**:
     - "Retry All" filtrado por canal y/o org
     - "Discard All" con confirmacion
  4. **Detalle** (modal o panel lateral):
     - Payload original completo
     - Lista de intentos con timestamp, status code, error detallado, latencia
     - Razon del fallo
     - Boton de retry individual
- [ ] Badges de conteo en la navegacion:
  - Badge rojo en "DLQ" con conteo total de mensajes pendientes
  - Actualizar cada 30 segundos (polling o via SSE)
- [ ] Componentes standalone OnPush:
  - `DlqTableComponent` (tabla principal)
  - `DlqDetailPanelComponent` (detalle expandido)
  - `DlqActionsBarComponent` (acciones masivas + filtros)
- [ ] Feedback visual: al hacer retry, mostrar spinner y resultado (exito/fallo)
- [ ] data-cy attributes
- [ ] Tests >= 98%

**Tareas Tecnicas:**
1. Crear pagina `admin-dlq.page.ts` con routing
2. Crear `DlqTableComponent` con paginacion y filtros
3. Crear `DlqDetailPanelComponent` con historial de intentos
4. Crear `DlqActionsBarComponent` con acciones masivas
5. Crear adapter `notification-dlq.adapter.ts`
6. Implementar badge de conteo con polling
7. Tests: tabla, filtros, retry, detalle, acciones masivas

**Dependencias:** US-SP-124 (endpoints DLQ), EP-SP-008 (layout Admin)
**Estimacion:** 4 dev-days

---

#### US-SP-127: Configuracion de Webhook y Canales (Tier 2 B2B)

**ID:** US-SP-127
**Epica:** EP-SP-030
**Prioridad:** P0

**Historia:**
Como **Cliente Empresa (B2B)** quiero configurar mi endpoint de webhook, definir custom headers, probar la conectividad, y seleccionar que canales quiero activos para cada tipo de evento financiero, para integrar las notificaciones de SuperPago con mis sistemas internos de forma personalizada.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/business/settings/notifications` con 3 tabs:
  1. **Tab Webhook**:
     - Campo URL (HTTPS requerido) con validacion en tiempo real
     - Campo Secret (auto-generado o custom, con boton de regenerar)
     - Campos de custom headers (hasta 5, key-value pairs, dinamicos)
     - Boton "Test Webhook" que:
       - Envia evento de prueba al URL configurado
       - Muestra resultado: status code, latencia, respuesta parcial (primeros 500 chars)
       - Indicador verde/rojo segun resultado
     - Codigo de ejemplo para verificar firma HMAC en el lenguaje del cliente:
       - Python, Node.js, PHP, Java, Go (tabs con snippet)
     - Estado del circuit breaker: CLOSED (verde), OPEN (rojo con alerta), HALF_OPEN (amarillo)
  2. **Tab Canales por Evento** (tabla interactiva):
     - Filas: cada tipo de evento (SPEI_IN, SPEI_OUT, BillPay, etc.)
     - Columnas: Webhook, Email, WhatsApp (si configurado), SMS (si configurado)
     - Celdas: checkbox/toggle para activar/desactivar
     - Header de columna con toggle "activar/desactivar todos" para un canal
     - Pre-seleccion segun defaults del tier
     - Cambios auto-guardados (debounce 500ms) con indicador "guardando..."
  3. **Tab Historial de Entregas**:
     - Tabla de notificaciones recientes (ultimos 30 dias)
     - Columnas: evento, canal, status (entregado/fallido/pendiente), timestamp
     - Expandir fila para ver detalle del payload y de los intentos
     - Filtros por canal y por status
     - Paginacion server-side
- [ ] Componentes standalone OnPush:
  - `WebhookConfigFormComponent` (formulario + test)
  - `HmacCodeExampleComponent` (snippets por lenguaje)
  - `ChannelEventMatrixComponent` (tabla interactiva de canales x eventos)
  - `DeliveryHistoryTableComponent` (historial con expandable rows)
  - `CircuitBreakerStatusComponent` (indicador visual del estado)
- [ ] Validaciones:
  - URL debe ser HTTPS (no HTTP, no localhost en produccion, no IPs privadas)
  - Secret: minimo 32 caracteres
  - Al menos 1 canal activo para al menos 1 evento
- [ ] data-cy attributes
- [ ] Tests >= 98%

**Tareas Tecnicas:**
1. Crear pagina `business-notification-settings.page.ts` con tabs
2. Crear `WebhookConfigFormComponent` con validacion y test de conectividad
3. Crear `HmacCodeExampleComponent` con tabs de lenguajes
4. Crear `ChannelEventMatrixComponent` con auto-save
5. Crear `DeliveryHistoryTableComponent` con paginacion server-side
6. Crear `CircuitBreakerStatusComponent`
7. Crear adapter `notification-business.adapter.ts`
8. Tests: formulario, test webhook, matrix toggle, historial, validaciones

**Dependencias:** US-SP-117 (API preferencias), US-SP-119 (API test webhook), US-SP-124 (API historial), EP-SP-011 (layout B2B)
**Estimacion:** 6 dev-days

---

#### US-SP-128: Preferencias de Notificacion B2C (Tier 3)

**ID:** US-SP-128
**Epica:** EP-SP-030
**Prioridad:** P1

**Historia:**
Como **Usuario Final (B2C)** quiero configurar por que canales quiero recibir notificaciones (WhatsApp, email, SMS) con toggles simples y ver un preview de como se ven las notificaciones en cada canal, para controlar mi experiencia de comunicacion con SuperPago sin complicaciones.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/personal/settings/notifications` con diseno simple y mobile-first:
  1. **Seccion Canales Activos**:
     - Toggle WhatsApp: on/off (numero asociado mostrado, opcion de cambiar)
     - Toggle Email: on/off (email mostrado, opcion de cambiar)
     - Toggle SMS: on/off (numero asociado mostrado)
     - Cada toggle con icono del canal y descripcion breve:
       - WhatsApp: "Recibe confirmaciones de depositos, pagos y alertas"
       - Email: "Recibe resumenes y confirmaciones detalladas"
       - SMS: "Recibe codigos de seguridad y alertas criticas"
     - SMS no puede desactivarse completamente si tiene operaciones Cash-Out activas (OTP obligatorio)
  2. **Seccion Preview**:
     - Al activar un canal, mostrar ejemplo visual de como se ve una notificacion de SPEI_IN en ese canal
     - WhatsApp: mockup de burbuja de chat con template real
     - Email: preview del email HTML en iframe
     - SMS: mockup de mensaje de texto
  3. **Seccion Quiet Hours** (opcional):
     - Toggle "No molestar" con selector de horario (ej: 22:00 - 08:00)
     - Nota: "Las alertas de seguridad siempre se envian"
  4. **Seccion Historial** (link o inline):
     - Ultimas 10 notificaciones recibidas con canal y status
     - Link "Ver todo" → lista completa
- [ ] Componentes standalone OnPush:
  - `ChannelToggleComponent` (toggle individual con icono y descripcion)
  - `NotificationPreviewComponent` (preview por canal con mockup visual)
  - `QuietHoursConfigComponent` (selector de horario)
  - `RecentNotificationsListComponent` (ultimas N notificaciones)
- [ ] Auto-save: cambios se guardan inmediatamente con feedback visual ("Guardado")
- [ ] Onboarding: la primera vez que el usuario visita la pagina, mostrar tooltip guiado
- [ ] Mobile responsive: todo debe verse bien en pantallas < 375px de ancho
- [ ] data-cy attributes
- [ ] Tests >= 98%

**Tareas Tecnicas:**
1. Crear pagina `personal-notification-settings.page.ts`
2. Crear `ChannelToggleComponent` reutilizable
3. Crear `NotificationPreviewComponent` con mockups por canal
4. Crear `QuietHoursConfigComponent`
5. Crear `RecentNotificationsListComponent`
6. Crear adapter `notification-personal.adapter.ts`
7. Implementar auto-save con debounce
8. Tests: toggles, preview, quiet hours, auto-save, mobile responsive

**Dependencias:** US-SP-117 (API preferencias), US-SP-124 (API historial), EP-SP-012 (layout B2C)
**Estimacion:** 4 dev-days

---

#### US-SP-129: Historial de Notificaciones Multi-Tier

**ID:** US-SP-129
**Epica:** EP-SP-030
**Prioridad:** P1

**Historia:**
Como **Usuario de cualquier tier** quiero ver el historial completo de notificaciones que me fueron enviadas, con filtros por tipo de evento, canal y fecha, para auditar la comunicacion y verificar que mis alertas estan llegando correctamente.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/{tier}/notifications/history` (ruta adaptada por tier):
  - `/sp/admin/notifications/history` (Tier 1 - ve todas las orgs)
  - `/sp/business/notifications/history` (Tier 2 - solo su org)
  - `/sp/personal/notifications/history` (Tier 3 - solo las suyas)
- [ ] Tabla principal con columnas:
  - Tipo de evento (con icono y badge de severidad)
  - Canal de entrega (icono: webhook/email/whatsapp/sms/slack)
  - Estado de entrega (badge: Entregado=verde, Fallido=rojo, Pendiente=amarillo)
  - Fecha y hora
  - Resumen del contenido (primeros 100 chars)
  - Boton "Ver detalle"
- [ ] Filtros:
  - Tipo de evento (multi-select dropdown)
  - Canal (multi-select dropdown)
  - Estado (entregado/fallido/pendiente)
  - Rango de fechas (date picker)
  - Organizacion (solo visible en Tier 1)
  - Busqueda por texto en contenido
- [ ] Paginacion server-side (20 items por pagina, infinite scroll o botones)
- [ ] Detalle de notificacion (modal o panel lateral):
  - Contenido completo renderizado
  - Metadata: event_id, notification_id, timestamp, canal
  - Timeline de entrega: encolado → enviado → entregado (con timestamps)
  - Si fallido: razon del fallo
- [ ] Exportar: boton "Descargar CSV" con los filtros aplicados (maximo 1000 registros)
- [ ] Componentes standalone OnPush:
  - `NotificationHistoryTableComponent` (tabla principal, reutilizable entre tiers)
  - `NotificationHistoryFiltersComponent` (filtros)
  - `NotificationDetailModalComponent` (detalle con timeline)
  - `NotificationExportButtonComponent` (exportar CSV)
- [ ] Tier-aware: el componente de tabla es el mismo, pero recibe configuracion de columnas visibles segun tier
- [ ] data-cy attributes
- [ ] Tests >= 98%

**Tareas Tecnicas:**
1. Crear pagina `notification-history.page.ts` (compartida, tier-aware)
2. Crear `NotificationHistoryTableComponent` con paginacion server-side
3. Crear `NotificationHistoryFiltersComponent`
4. Crear `NotificationDetailModalComponent` con timeline visual
5. Crear `NotificationExportButtonComponent`
6. Crear adapter `notification-history.adapter.ts`
7. Configurar routing por tier (3 rutas, mismo componente, diferente config)
8. Tests: tabla, filtros, paginacion, detalle, export, permisos por tier

**Dependencias:** US-SP-124 (API audit/historial), EP-SP-007 (routing multi-tier)
**Estimacion:** 5 dev-days

---

#### US-SP-130: Gestion de Templates de Notificacion (Tier 1 Admin)

**ID:** US-SP-130
**Epica:** EP-SP-030
**Prioridad:** P2

**Historia:**
Como **Administrador de SuperPago** quiero editar los templates de notificacion desde la interfaz grafica, con preview en tiempo real del renderizado, para ajustar los mensajes sin necesidad de un deploy y asegurar que la comunicacion con clientes sea clara y profesional.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/admin/notifications/templates` con:
  1. **Lista de templates**:
     - Tabla con columnas: evento, canal, locale, ultima edicion, status
     - Filtros: por evento, por canal, por locale
     - Agrupacion visual por tipo de evento
  2. **Editor de template** (pagina o modal grande):
     - Split view: editor a la izquierda, preview a la derecha
     - Editor con syntax highlighting para Jinja2/Mustache
     - Variables disponibles listadas en sidebar con boton "insertar"
     - Preview renderizado con datos de ejemplo editables
     - Para WhatsApp: indicador de longitud (max 1024) con contador
     - Para SMS: indicador de longitud (max 160 per segment) con contador de segmentos
     - Para Email: preview en iframe con HTML renderizado
     - Boton "Guardar borrador" + "Publicar"
  3. **Versionamiento**:
     - Cada edicion crea una nueva version
     - Historial de versiones con diff visual
     - Rollback a version anterior
- [ ] Componentes standalone OnPush:
  - `TemplateListComponent` (tabla con filtros)
  - `TemplateEditorComponent` (split view editor + preview)
  - `TemplateSyntaxHighlighterComponent` (editor con highlighting)
  - `TemplatePreviewComponent` (renderizado con datos de ejemplo)
  - `TemplateVersionHistoryComponent` (lista de versiones con diff)
- [ ] Validacion en tiempo real:
  - Variables no reconocidas resaltadas en rojo
  - Longitud excedida resaltada con warning
  - HTML malformado detectado con error
- [ ] data-cy attributes
- [ ] Tests >= 98%

**Tareas Tecnicas:**
1. Crear pagina `admin-templates.page.ts`
2. Crear `TemplateListComponent` con filtros y agrupacion
3. Crear `TemplateEditorComponent` con split view
4. Crear `TemplateSyntaxHighlighterComponent` (usar CodeMirror o Monaco Editor light)
5. Crear `TemplatePreviewComponent` con renderizado real
6. Crear `TemplateVersionHistoryComponent`
7. Crear adapter `notification-templates.adapter.ts`
8. Tests: editor, preview, validaciones, versionamiento

**Dependencias:** US-SP-120 (API templates), EP-SP-008 (layout Admin)
**Estimacion:** 5 dev-days

---

## Roadmap

### Fase 1: Backend Core (Sprint 12-13)

| Sprint | Epica | User Stories | Dev-Days |
|--------|-------|-------------|----------|
| 12 | EP-SP-029 | US-SP-117 (Preferencias), US-SP-120 (Templates) | 10 |
| 12-13 | EP-SP-029 | US-SP-118 (Dispatcher) | 6 |

**Razonamiento:** Las preferencias y templates son independientes entre si y pueden desarrollarse en paralelo. El dispatcher depende de ambos, asi que arranca cuando ambos estan al 80%.

### Fase 2: Backend Canales (Sprint 13-14)

| Sprint | Epica | User Stories | Dev-Days |
|--------|-------|-------------|----------|
| 13 | EP-SP-029 | US-SP-119 (Webhook outbound) | 5 |
| 13-14 | EP-SP-029 | US-SP-121 (Email SES), US-SP-122 (WhatsApp + SMS) | 9 |
| 14 | EP-SP-029 | US-SP-123 (Slack + SSE), US-SP-124 (Audit + DLQ) | 10 |

**Razonamiento:** Los canales son independientes entre si. Webhook es prioridad P0 porque es el canal principal B2B. Email y WhatsApp+SMS pueden ir en paralelo con diferentes devs. Slack+SSE y Audit van al final porque dependen de que los senders esten funcionales.

### Fase 3: Frontend (Sprint 14-16)

| Sprint | Epica | User Stories | Dev-Days |
|--------|-------|-------------|----------|
| 14-15 | EP-SP-030 | US-SP-125 (Dashboard Tier 1), US-SP-127 (Config Tier 2) | 12 |
| 15 | EP-SP-030 | US-SP-126 (DLQ Viewer), US-SP-128 (Preferencias Tier 3) | 8 |
| 15-16 | EP-SP-030 | US-SP-129 (Historial multi-tier), US-SP-130 (Editor templates) | 10 |

**Razonamiento:** El dashboard admin y la config B2B son P0 y pueden desarrollarse en paralelo (diferentes tiers). El DLQ viewer y las preferencias B2C son P1 y van despues. El historial y el editor de templates son los ultimos porque tienen menor urgencia y reutilizan componentes de las pantallas anteriores.

### Resumen de Estimaciones

| Epica | User Stories | Dev-Days | Sprint |
|-------|-------------|----------|--------|
| EP-SP-029 | 8 (US-SP-117 a 124) | 40 | 12-14 |
| EP-SP-030 | 6 (US-SP-125 a 130) | 30 | 14-16 |
| **TOTAL** | **14** | **70** | 12-16 |

### Paralelismo Sugerido (2 equipos)

```
Sprint 12: [Equipo A: US-SP-117 Prefs + US-SP-118 Dispatcher]  [Equipo B: US-SP-120 Templates]
Sprint 13: [Equipo A: US-SP-118 cont. + US-SP-119 Webhook]     [Equipo B: US-SP-121 Email + US-SP-122 WA/SMS]
Sprint 14: [Equipo A: US-SP-123 Slack/SSE + US-SP-124 Audit]   [Equipo B: US-SP-125 Dashboard + US-SP-127 Config B2B]
Sprint 15: [Equipo A: US-SP-126 DLQ Viewer + US-SP-128 Prefs]  [Equipo B: US-SP-129 Historial]
Sprint 16: [Buffer + US-SP-130 Templates Editor]                [Buffer + QA + Deploy + Integration testing]
```

---

## Grafo de Dependencias

```
EXISTENTES:
EP-SP-004 (SPEI Out)        ──+
EP-SP-005 (SPEI In)         ──+
EP-SP-015 (Cash In/Out)     ──+──> Eventos financieros
EP-SP-021/022 (BillPay)     ──+    (productores de eventos)
EP-SP-024 (Onboarding)      ──+
EP-SP-009/023 (Conciliacion) ─+
EP-SP-010 (Limites)         ──+

EP-SP-017 (Agente IA WA)    ──> covacha-botia (canal WhatsApp)

NUEVAS - BACKEND (EP-SP-029):
US-SP-117 (Preferencias)  ──────+
US-SP-120 (Templates)      ─────+──> US-SP-118 (Dispatcher)
                                          |
                     +--------------------+--------------------+
                     |                    |                    |
                     v                    v                    v
              US-SP-119            US-SP-121              US-SP-122
              (Webhook)            (Email SES)           (WA + SMS)
                     |                    |                    |
                     +--------------------+--------------------+
                                          |
                                          v
                               US-SP-123 (Slack + SSE)
                                          |
                                          v
                               US-SP-124 (Audit + DLQ)

NUEVAS - FRONTEND (EP-SP-030):
EP-SP-008 (Admin Tier 1) ──+──> US-SP-125 (Dashboard RT)
US-SP-123 (SSE endpoint) ──+    US-SP-126 (DLQ Viewer)
US-SP-124 (Audit API)    ──+    US-SP-130 (Templates Editor)

EP-SP-011 (B2B Tier 2)   ──+──> US-SP-127 (Config Webhook + Canales)
US-SP-117 (Prefs API)    ──+
US-SP-119 (Test webhook)  ─+

EP-SP-012 (B2C Tier 3)   ──+──> US-SP-128 (Preferencias B2C)
US-SP-117 (Prefs API)    ──+

EP-SP-007 (Scaffold)      ──+──> US-SP-129 (Historial multi-tier)
US-SP-124 (Audit API)     ──+
```

---

## Riesgos y Mitigaciones

### R1: Aprobacion de templates WhatsApp por Meta es lenta (24-48 horas por template)

**Probabilidad:** Alta
**Impacto:** Medio (bloquea canal WhatsApp para eventos nuevos)
**Mitigacion:**
- Someter los ~15 templates WhatsApp a aprobacion desde Sprint 12, antes de que el codigo este listo
- Usar templates genericos aprobados como fallback ("Tienes una nueva notificacion de SuperPago. Consulta tu cuenta.")
- Mantener catalogo de templates aprobados en DynamoDB con status (pending, approved, rejected)
- Si template rechazado: ajustar y re-someter, usar generico mientras tanto

### R2: SES en sandbox mode requiere verificacion de cada destinatario

**Probabilidad:** Alta (en desarrollo y staging)
**Impacto:** Bajo (solo afecta ambientes no-produccion)
**Mitigacion:**
- Solicitar salida de sandbox de SES en produccion desde Sprint 11 (proceso de AWS: 24-48 horas)
- En desarrollo: usar lista de emails verificados pre-configurados
- Configurar DKIM, SPF y DMARC antes de salir de sandbox para evitar rechazo de la solicitud

### R3: Redis/ElastiCache como SPOF para SSE en tiempo real

**Probabilidad:** Baja (ElastiCache es managed)
**Impacto:** Medio (dashboard admin pierde tiempo real)
**Mitigacion:**
- ElastiCache con Multi-AZ y automatic failover
- Fallback: si Redis no disponible, el frontend hace polling REST cada 10 segundos
- El endpoint SSE detecta desconexion de Redis y envia evento especial `event: fallback` al cliente
- Monitoreo CloudWatch de ElastiCache con alarmas

### R4: Alto volumen de notificaciones satura las colas SQS o los rate limits de canales

**Probabilidad:** Media (a escala)
**Impacto:** Alto (notificaciones perdidas o retrasadas)
**Mitigacion:**
- SQS escala automaticamente (no es SPOF)
- Rate limiting por canal con token bucket en DynamoDB:
  - Email SES: 14/seg (solicitar aumento a 50/seg si necesario)
  - SMS SNS: 20/seg
  - WhatsApp Meta: segun tier del numero de negocio
  - Webhook: 100/seg por org (configurable)
- Si rate limit alcanzado: re-encolar con delay de visibilidad, no descartar
- Metricas de throughput por canal para anticipar necesidad de scaling

### R5: Webhook outbound a endpoints de clientes con latencia alta o errores frecuentes

**Probabilidad:** Alta (dependemos de la infraestructura del cliente)
**Impacto:** Medio (DLQ se llena, circuito se abre)
**Mitigacion:**
- Circuit breaker por organizacion (no global) para aislar clientes problematicos
- Timeout agresivo de 10 segundos (si el cliente no responde en 10s, es su problema)
- DLQ con retry manual disponible para el admin
- Alerta proactiva al cliente B2B cuando su webhook tiene problemas persistentes
- Dashboard de salud de webhook visible para el cliente en su portal

### R6: Inconsistencia entre audit trail y estado real de entrega

**Probabilidad:** Media
**Impacto:** Bajo (informacional, no afecta negocio)
**Mitigacion:**
- Eventualmente consistent: los callbacks de delivery (SES, WhatsApp) pueden tardar segundos/minutos
- Estado default "SENT" al enviar, actualizar a "DELIVERED" o "FAILED" cuando llega callback
- Job de limpieza: notificaciones en estado SENT por mas de 1 hora → marcar como UNKNOWN
- No usar audit trail para decisiones de negocio, solo para monitoreo y debugging
