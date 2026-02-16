# Dashboard - Epicas de Metricas y Reportes (EP-DB-001 a EP-DB-008)

**Fecha**: 2026-02-16
**Product Owner**: SuperPago
**Estado**: Planificacion
**Prefijo Epicas**: EP-DB
**Prefijo User Stories**: US-DB

---

## Tabla de Contenidos

1. [Contexto y Motivacion](#contexto-y-motivacion)
2. [Roles Involucrados](#roles-involucrados)
3. [Arquitectura del Dashboard](#arquitectura-del-dashboard)
4. [Mapa de Epicas](#mapa-de-epicas)
5. [Epicas Detalladas](#epicas-detalladas)
6. [User Stories Detalladas](#user-stories-detalladas)
7. [Roadmap](#roadmap)
8. [Grafo de Dependencias](#grafo-de-dependencias)
9. [Riesgos y Mitigaciones](#riesgos-y-mitigaciones)
10. [Definition of Done Global](#definition-of-done-global)

---

## Contexto y Motivacion

El producto Dashboard es el centro de inteligencia del ecosistema SuperPago/BaatDigital. Proporciona visibilidad sobre metricas financieras, transacciones, KPIs de negocio y salud operativa a tres audiencias diferenciadas por tier. Actualmente existe monitoring basico en Grafana (grafana.superpago.com.mx) orientado a infraestructura, pero no hay un dashboard de negocio integrado en la plataforma.

| Capacidad | Problema que Resuelve |
|-----------|----------------------|
| **Dashboard Principal Multi-Tier** | Cada rol necesita una vista diferente: Admin ve el ecosistema completo, B2B ve su organizacion, B2C ve su actividad personal |
| **Reportes de Transacciones** | Los clientes necesitan consultar, filtrar y auditar sus transacciones de forma autonoma |
| **Analytics y Graficas** | Detectar tendencias, comparar periodos y tomar decisiones basadas en datos |
| **KPIs Configurables** | Cada organizacion tiene metricas diferentes que importan para su negocio |
| **Exportacion de Reportes** | Cumplimiento regulatorio, contabilidad interna y auditoria requieren reportes descargables |
| **Dashboard en Tiempo Real** | Operaciones criticas requieren visibilidad instantanea (SPEI, alertas, status) |
| **Alertas y Notificaciones** | Proactividad ante eventos criticos sin depender de revision manual |
| **Conciliacion y Salud Financiera** | Garantizar integridad del ledger y detectar discrepancias automaticamente |

### Repositorios Involucrados

| Repositorio | Funcion | Puerto Dev |
|-------------|---------|------------|
| `mf-dashboard` | Micro-frontend Angular 21 (Native Federation) | 4203 |
| `covacha-core` | Backend API - organizaciones, usuarios, configuracion | 5001 |
| `covacha-transaction` | Backend API - transacciones, ledger, conciliacion | 5003 |
| `covacha-notification` | Backend API - alertas, notificaciones, SSE | 5005 |
| `covacha-libs` | Modelos compartidos, utilidades, repositorios base | N/A |
| `mf-core` | Shell host - registrar remote mfDashboard | N/A |

### Relacion con Epicas Existentes

| Epica Existente | Relacion con Dashboard |
|-----------------|----------------------|
| EP-SP-003 (Double-Entry Ledger) | Fuente de datos para metricas financieras, balances y conciliacion |
| EP-SP-004/005 (SPEI Out/In) | Fuente de datos para reportes de transacciones SPEI |
| EP-SP-009 (Reconciliacion) | Base para EP-DB-008 (Conciliacion y Salud Financiera) |
| EP-SP-010 (Limites y Politicas) | Alimenta alertas de umbrales en EP-DB-007 |
| EP-SP-021/022 (BillPay) | Fuente de datos para reportes de pagos de servicios |
| EP-SP-029 (Notificaciones Backend) | Infraestructura para alertas en tiempo real de EP-DB-006 y EP-DB-007 |
| EP-SP-030 (Notificaciones Frontend) | Componentes compartidos de SSE y configuracion de alertas |

---

## Roles Involucrados

### R1: Administrador SuperPago (Tier 1)

Persona interna de SuperPago que monitorea la salud del ecosistema completo.

**Necesidades de Dashboard:**
- Metricas globales: volumen total de transacciones, GMV, comisiones, TPS
- Vision cross-organizacion: ranking de orgs por volumen, crecimiento, churn
- Alertas criticas: discrepancias de conciliacion, fallos SPEI, limites excedidos
- Reportes regulatorios y de compliance
- Health checks del sistema financiero en tiempo real

### R2: Cliente Empresa (Tier 2 - B2B)

Empresa que usa SuperPago y necesita visibilidad de sus operaciones.

**Necesidades de Dashboard:**
- Metricas de su organizacion: volumen, montos, comisiones, cuentas
- Reportes de transacciones filtrables y exportables
- KPIs personalizados para su negocio
- Alertas configurables por umbrales propios
- Conciliacion de su actividad vs extractos bancarios

### R3: Usuario Final (Tier 3 - B2C)

Persona natural que usa SuperPago para operaciones personales.

**Necesidades de Dashboard:**
- Resumen de actividad: ultimos movimientos, saldo, gastos del mes
- Graficas simples de ingresos vs egresos
- Historial de transacciones con busqueda basica
- Notificaciones de movimientos

### R4: Sistema

Procesos automatizados que generan datos para el dashboard.

**Responsabilidades:**
- Agregar metricas en periodos (horario, diario, semanal, mensual)
- Pre-calcular KPIs para consulta rapida
- Ejecutar conciliacion automatica y reportar discrepancias
- Generar reportes programados y enviarlos por email
- Emitir eventos SSE para actualizaciones en tiempo real

---

## Arquitectura del Dashboard

### Flujo General de Datos

```
Fuentes de Datos (backends)                 Agregacion                    Frontend
================================           =============                 =========

covacha-transaction                        covacha-core
  |-- Transacciones SPEI In/Out   --.      (API Dashboard)
  |-- Transacciones BillPay        |       +------------------+
  |-- Transacciones Cash In/Out    |       | /api/v1/dashboard |
  |-- Movimientos internos         +-----> |   /metrics        |-------> mf-dashboard
  |-- Ledger entries               |       |   /summary        |           |
                                   |       |   /kpis           |           +-- Tier 1 (Admin)
covacha-core                       |       +------------------+            |   Vista global
  |-- Organizaciones              -+       | /api/v1/reports   |           |
  |-- Usuarios                     |       |   /transactions   |           +-- Tier 2 (B2B)
  |-- Cuentas                      +-----> |   /generate       |           |   Vista org
  |-- Configuracion                |       |   /scheduled      |           |
                                   |       +------------------+            +-- Tier 3 (B2C)
covacha-notification               |       | /api/v1/analytics |               Vista personal
  |-- Alertas activas             -+       |   /timeseries     |
  |-- Historial notificaciones     |       |   /distribution   |
  |-- Eventos SSE                --+-----> |   /comparison     |
                                           +------------------+

                                   SQS: dashboard-aggregation
                                     |
                                     v
                                   Lambda: metrics-aggregator
                                     |
                                     +-- Pre-calcula metricas por hora/dia/semana/mes
                                     +-- Persiste en DynamoDB (METRIC# keys)
                                     +-- Invalida cache de metricas
```

### Modelo de Datos DynamoDB

```
# Metricas pre-calculadas por organizacion y periodo
PK: ORG#{org_id}#METRICS
SK: {period_type}#{period_value}        # Ej: DAILY#2026-02-16, MONTHLY#2026-02
Attributes: transaction_count, total_amount, avg_amount, commission_total,
            spei_in_count, spei_out_count, billpay_count, cash_count,
            internal_count, success_rate, avg_latency_ms

# Metricas globales (Admin)
PK: GLOBAL#METRICS
SK: {period_type}#{period_value}
Attributes: (mismos que arriba + org_count, active_users, new_accounts)

# KPIs configurables por organizacion
PK: ORG#{org_id}#KPI
SK: KPI#{kpi_id}
Attributes: name, formula, metric_source, threshold_warning, threshold_critical,
            display_type (number|percentage|currency), position, created_by

# Widgets de dashboard por usuario
PK: USER#{user_id}#DASHBOARD
SK: WIDGET#{widget_id}
Attributes: widget_type (kpi_card|chart|table|alert_feed), position_x, position_y,
            width, height, config (JSON), created_at

# Layouts guardados
PK: USER#{user_id}#DASHBOARD
SK: LAYOUT#{layout_name}
Attributes: widgets (list de widget_ids con posiciones), is_default, created_at

# Reportes generados
PK: ORG#{org_id}#REPORT
SK: REPORT#{report_id}
Attributes: type (transactions|summary|conciliation|custom), format (pdf|csv|xlsx),
            status (pending|generating|completed|failed), s3_key, filters,
            requested_by, created_at, completed_at, file_size_bytes
GSI-1: PK=REPORT#{report_id}, SK=DETAIL (lookup por ID)

# Reportes programados
PK: ORG#{org_id}#SCHEDULED_REPORT
SK: SCHEDULE#{schedule_id}
Attributes: report_type, frequency (daily|weekly|monthly), filters, format,
            recipients (list de emails), next_run_at, last_run_at, enabled

# Alertas configurables por organizacion
PK: ORG#{org_id}#ALERT_RULE
SK: ALERT#{alert_id}
Attributes: name, metric, operator (gt|lt|eq|gte|lte), threshold, severity,
            channels (list), cooldown_minutes, enabled, last_triggered_at
```

### SSE (Server-Sent Events) para Tiempo Real

```
mf-dashboard (browser)
    |
    | EventSource("/api/v1/dashboard/stream?org_id=X&tier=Y")
    |
    v
covacha-core (Flask endpoint SSE)
    |
    | Redis Pub/Sub channel: dashboard:{org_id}
    |
    v
Lambda: metrics-aggregator
    |
    +-- Publica evento cuando se procesa una transaccion
    +-- Publica evento cuando cambia un KPI
    +-- Publica evento cuando se activa una alerta
```

---

## Mapa de Epicas

| ID | Epica | Complejidad | Sprint Sugerido | Dependencias |
|----|-------|-------------|-----------------|--------------|
| EP-DB-001 | Dashboard Principal Multi-Tier | L | 1-3 | EP-SP-003 (ledger) |
| EP-DB-002 | Reportes de Transacciones | L | 2-4 | EP-DB-001, EP-SP-003, EP-SP-004/005 |
| EP-DB-003 | Analytics y Graficas Interactivas | L | 3-5 | EP-DB-001, EP-DB-002 |
| EP-DB-004 | KPIs Configurables | L | 4-6 | EP-DB-001, EP-DB-003 |
| EP-DB-005 | Exportacion y Reportes Programados | M | 5-7 | EP-DB-002 |
| EP-DB-006 | Dashboard en Tiempo Real | L | 6-8 | EP-DB-001, EP-SP-029 |
| EP-DB-007 | Alertas y Notificaciones en Dashboard | M | 7-9 | EP-DB-006, EP-SP-029/030 |
| EP-DB-008 | Dashboard de Conciliacion y Salud Financiera | L | 8-10 | EP-DB-001, EP-DB-002, EP-SP-009 |

**Totales:**
- 8 epicas
- 45 user stories (US-DB-001 a US-DB-045)
- Estimacion total: ~120-160 dev-days

---

## Epicas Detalladas

---

### EP-DB-001: Dashboard Principal Multi-Tier

**Descripcion:**
Vista principal del dashboard diferenciada por tier. Tier 1 (Admin SuperPago) ve metricas globales del ecosistema: volumen total, GMV, comisiones, TPS, ranking de organizaciones y salud general. Tier 2 (B2B) ve metricas de su organizacion: saldos, transacciones del periodo, comisiones acumuladas, cuentas activas. Tier 3 (B2C) ve resumen personal: ultimo saldo, movimientos recientes, gastos del mes. Incluye cards de KPIs principales, graficas de tendencia simplificadas y feed de actividad reciente.

**User Stories:** US-DB-001, US-DB-002, US-DB-003, US-DB-004, US-DB-005, US-DB-006

**Criterios de Aceptacion de la Epica:**
- [ ] Ruta `/dashboard` registrada en mf-core via Native Federation
- [ ] Tier 1: Vista admin con metricas globales (GMV, TPS, comisiones, orgs activas)
- [ ] Tier 2: Vista empresa con metricas de organizacion (saldo, volumen, comisiones)
- [ ] Tier 3: Vista personal con resumen simplificado (saldo, movimientos, gastos)
- [ ] Cards de KPI con valor actual, delta vs periodo anterior, indicador visual (up/down)
- [ ] Grafica de tendencia de 7 dias en la vista principal
- [ ] Feed de actividad reciente (ultimas 10 transacciones/eventos)
- [ ] Backend: endpoints de metricas agregadas con cache en Redis (TTL 5 min)
- [ ] Backend: Lambda de pre-calculo de metricas por hora/dia/semana/mes
- [ ] Responsive design (mobile-first para Tier 3)
- [ ] Tests >= 98% coverage (frontend y backend)

**Dependencias:**
- EP-SP-003 (Ledger de partida doble - fuente de datos financieros)

**Complejidad:** L (3 vistas tier, backend de agregacion, pre-calculo)

**Repositorios:** `mf-dashboard`, `covacha-core`, `covacha-transaction`, `covacha-libs`

---

### EP-DB-002: Reportes de Transacciones

**Descripcion:**
Tabla de transacciones con filtros avanzados (rango de fechas, tipo de transaccion, rango de monto, estado, cuenta origen/destino, referencia). Detalle expandible de cada transaccion con asientos contables. Agrupacion por periodo (dia, semana, mes). Totales y subtotales calculados. Paginacion server-side con cursor-based pagination para rendimiento con millones de registros.

**User Stories:** US-DB-007, US-DB-008, US-DB-009, US-DB-010, US-DB-011

**Criterios de Aceptacion de la Epica:**
- [ ] Tabla de transacciones con columnas: fecha, tipo, monto, estado, cuenta, referencia
- [ ] Filtros avanzados: rango de fechas (date picker), tipo (SPEI_IN, SPEI_OUT, BILLPAY, CASH_IN, CASH_OUT, INTERNAL), rango de monto (min/max), estado (completed, pending, failed), cuenta, referencia
- [ ] Paginacion server-side cursor-based (no offset) con 25/50/100 items por pagina
- [ ] Detalle expandible de transaccion con asientos de partida doble
- [ ] Agrupacion por dia/semana/mes con subtotales
- [ ] Totales generales segun filtros aplicados
- [ ] Tier 1: ve todas las transacciones de todas las organizaciones
- [ ] Tier 2: ve solo transacciones de su organizacion
- [ ] Tier 3: ve solo sus transacciones personales
- [ ] Busqueda por referencia o ID de transaccion
- [ ] Tests >= 98% coverage

**Dependencias:**
- EP-DB-001 (scaffold del dashboard y guards por tier)
- EP-SP-003 (ledger entries)
- EP-SP-004/005 (transacciones SPEI)

**Complejidad:** L (paginacion cursor-based, filtros complejos, agrupacion)

**Repositorios:** `mf-dashboard`, `covacha-transaction`, `covacha-libs`

---

### EP-DB-003: Analytics y Graficas Interactivas

**Descripcion:**
Modulo de analytics con graficas interactivas. Time series de volumen y monto de transacciones con granularidad configurable (hora, dia, semana, mes). Distribucion por tipo de operacion (pie chart). Comparativas periodo-a-periodo (mes actual vs anterior, YoY). Drill-down por cuenta u organizacion. Heatmap de actividad por hora del dia y dia de la semana.

**User Stories:** US-DB-012, US-DB-013, US-DB-014, US-DB-015, US-DB-016, US-DB-017

**Criterios de Aceptacion de la Epica:**
- [ ] Time series chart: volumen y monto con granularidad hora/dia/semana/mes
- [ ] Pie chart: distribucion de transacciones por tipo (SPEI, BillPay, Cash, Internal)
- [ ] Bar chart: comparativa periodo actual vs anterior (monto, volumen, comisiones)
- [ ] Heatmap: actividad por hora del dia y dia de la semana
- [ ] Drill-down: click en segmento del pie o barra navega a detalle filtrado
- [ ] Tier 1: drill-down por organizacion (click en org → metricas de esa org)
- [ ] Tier 2: drill-down por cuenta (click en cuenta → movimientos de esa cuenta)
- [ ] Tier 3: solo graficas simples de ingresos vs egresos
- [ ] Libreria de graficas: usar libreria compatible con Angular 21 (Chart.js o ngx-charts)
- [ ] Tooltips informativos en hover con valores exactos
- [ ] Graficas responsive (adaptan layout en mobile)
- [ ] Tests >= 98% coverage

**Dependencias:**
- EP-DB-001 (metricas pre-calculadas)
- EP-DB-002 (datos de transacciones para drill-down)

**Complejidad:** L (multiples tipos de grafica, drill-down, heatmap)

**Repositorios:** `mf-dashboard`, `covacha-core`, `covacha-transaction`

---

### EP-DB-004: KPIs Configurables

**Descripcion:**
Builder de KPIs personalizados por organizacion. Metricas predefinidas disponibles (GMV, TPS, comisiones totales, tasa de crecimiento, tasa de exito, tiempo promedio de procesamiento). Umbrales de alerta por KPI (warning, critical). Widgets de KPI con drag-and-drop para personalizar el layout del dashboard. Layouts guardados por usuario con opcion de restaurar default.

**User Stories:** US-DB-018, US-DB-019, US-DB-020, US-DB-021, US-DB-022

**Criterios de Aceptacion de la Epica:**
- [ ] Catalogo de metricas predefinidas: GMV, TPS, comisiones, crecimiento, tasa de exito, latencia
- [ ] Builder de KPI: seleccionar metrica, definir formula (si es custom), configurar display
- [ ] Umbrales por KPI: valor warning y valor critical con colores visuales
- [ ] Widgets de KPI en cards drag-and-drop (Angular CDK DragDrop)
- [ ] Layouts guardados por usuario en DynamoDB
- [ ] Restaurar layout por defecto del tier
- [ ] Tier 1: puede crear KPIs globales y por organizacion
- [ ] Tier 2: puede crear KPIs para su organizacion
- [ ] Tier 3: no puede crear KPIs, ve los predefinidos
- [ ] Minimo 8 metricas predefinidas disponibles
- [ ] Tests >= 98% coverage

**Dependencias:**
- EP-DB-001 (vista principal del dashboard)
- EP-DB-003 (metricas que alimentan los KPIs)

**Complejidad:** L (builder, drag-and-drop, formulas, persistencia de layouts)

**Repositorios:** `mf-dashboard`, `covacha-core`, `covacha-libs`

---

### EP-DB-005: Exportacion y Reportes Programados

**Descripcion:**
Exportacion de datos a PDF, CSV y Excel (XLSX). Reportes programados con frecuencia configurable (diario, semanal, mensual). Envio automatico por email a destinatarios configurados. Templates de reporte personalizables. Historial de reportes generados con descarga directa desde S3.

**User Stories:** US-DB-023, US-DB-024, US-DB-025, US-DB-026, US-DB-027

**Criterios de Aceptacion de la Epica:**
- [ ] Exportacion on-demand: boton "Exportar" en tabla de transacciones y analytics
- [ ] Formatos soportados: PDF (con header corporativo), CSV, XLSX
- [ ] Generacion asincrona via SQS para reportes grandes (>1000 filas)
- [ ] Archivo generado en S3 con URL pre-firmada (expira en 24h)
- [ ] Notificacion al usuario cuando el reporte esta listo (in-app + email)
- [ ] Reportes programados: configurar frecuencia, filtros, formato, destinatarios
- [ ] Historial de reportes generados con status y descarga
- [ ] Tier 1: puede generar reportes de cualquier organizacion
- [ ] Tier 2: puede generar reportes de su organizacion
- [ ] Tier 3: puede exportar su historial personal (solo CSV)
- [ ] Limite de tamano: maximo 100,000 filas por reporte
- [ ] Tests >= 98% coverage

**Dependencias:**
- EP-DB-002 (datos de transacciones para exportar)

**Complejidad:** M (generacion asincrona, multiples formatos, scheduling)

**Repositorios:** `mf-dashboard`, `covacha-core`, `covacha-transaction`, `covacha-libs`

---

### EP-DB-006: Dashboard en Tiempo Real

**Descripcion:**
Server-Sent Events (SSE) para metricas en vivo. Contadores de transacciones en tiempo real que se actualizan sin refresh. Indicador de TPS (transacciones por segundo) en vivo. Feed de actividad con nuevas transacciones apareciendo en tiempo real. Status de servicios del ecosistema (health checks de cada backend).

**User Stories:** US-DB-028, US-DB-029, US-DB-030, US-DB-031, US-DB-032

**Criterios de Aceptacion de la Epica:**
- [ ] Endpoint SSE: `GET /api/v1/dashboard/stream` con autenticacion y filtro por org/tier
- [ ] Tipos de evento SSE: `metric_update`, `new_transaction`, `alert_triggered`, `service_status`
- [ ] Contadores en vivo: transacciones del dia, monto acumulado, TPS actual
- [ ] Feed de actividad: nuevas transacciones aparecen en lista sin refresh
- [ ] Status de servicios: indicador verde/amarillo/rojo por backend (health check cada 30s)
- [ ] Reconexion automatica si se pierde la conexion SSE
- [ ] Tier 1: ve metricas globales en tiempo real + status de servicios
- [ ] Tier 2: ve metricas de su organizacion en tiempo real
- [ ] Tier 3: ve notificaciones de movimientos en tiempo real
- [ ] Backend: Redis Pub/Sub para distribuir eventos entre instancias
- [ ] Limite de conexiones SSE concurrentes por organizacion
- [ ] Tests >= 98% coverage

**Dependencias:**
- EP-DB-001 (dashboard base)
- EP-SP-029 (infraestructura de notificaciones y eventos)

**Complejidad:** L (SSE, Redis Pub/Sub, reconexion, health checks)

**Repositorios:** `mf-dashboard`, `covacha-core`, `covacha-notification`, `covacha-libs`

---

### EP-DB-007: Alertas y Notificaciones en Dashboard

**Descripcion:**
Centro de notificaciones integrado en mf-dashboard. Alertas configurables basadas en metricas con umbrales personalizados. Panel de alertas activas con severidad visual. Acciones sobre alertas: acknowledge, snooze, dismiss. Integracion con EP-SP-029/030 para recibir notificaciones financieras y mostrarlas en el dashboard.

**User Stories:** US-DB-033, US-DB-034, US-DB-035, US-DB-036, US-DB-037

**Criterios de Aceptacion de la Epica:**
- [ ] Centro de notificaciones: icono de campana en header con badge de conteo
- [ ] Panel desplegable con lista de notificaciones recientes (ultimas 50)
- [ ] Alertas por metrica: configurar regla (metrica > umbral → alerta)
- [ ] Severidad visual: INFO (azul), WARNING (amarillo), CRITICAL (rojo)
- [ ] Acciones: marcar como leida, snooze (1h, 4h, 24h), dismiss permanente
- [ ] Sonido/vibracion opcional para alertas CRITICAL
- [ ] Historial de alertas con filtros (severidad, fecha, tipo)
- [ ] Tier 1: configura alertas globales del ecosistema
- [ ] Tier 2: configura alertas de su organizacion
- [ ] Tier 3: solo recibe notificaciones, no configura alertas
- [ ] Integracion con EP-SP-029: eventos financieros se muestran como notificaciones
- [ ] Cooldown por alerta para evitar spam (configurable por regla)
- [ ] Tests >= 98% coverage

**Dependencias:**
- EP-DB-006 (SSE para recibir alertas en tiempo real)
- EP-SP-029/030 (sistema de notificaciones financieras)

**Complejidad:** M (reglas de alerta, acciones, integracion con notificaciones existentes)

**Repositorios:** `mf-dashboard`, `covacha-core`, `covacha-notification`

---

### EP-DB-008: Dashboard de Conciliacion y Salud Financiera

**Descripcion:**
Vista de conciliacion diaria que muestra el balance entre transacciones procesadas y asientos contables. Status de cuentas del ecosistema. Balance general por organizacion. Deteccion y visualizacion de discrepancias. Integridad del ledger de partida doble (debitos = creditos). Health checks del sistema financiero con metricas de consistencia.

**User Stories:** US-DB-038, US-DB-039, US-DB-040, US-DB-041, US-DB-042, US-DB-043, US-DB-044, US-DB-045

**Criterios de Aceptacion de la Epica:**
- [ ] Vista de conciliacion diaria: tabla con fecha, transacciones esperadas vs procesadas, delta
- [ ] Indicador visual: verde (OK), amarillo (pendiente), rojo (discrepancia)
- [ ] Balance general por organizacion: saldos de todas las cuentas con totales
- [ ] Verificacion de integridad del ledger: sum(debitos) == sum(creditos) por organizacion
- [ ] Lista de discrepancias detectadas con detalle (transaccion, monto esperado vs real, timestamp)
- [ ] Accion manual: marcar discrepancia como resuelta con nota explicativa
- [ ] Health check financiero: metricas de consistencia (ledger integrity %, reconciliation rate, pending settlements)
- [ ] Tier 1: ve conciliacion de todas las organizaciones
- [ ] Tier 2: ve conciliacion de su organizacion
- [ ] Tier 3: no tiene acceso a conciliacion
- [ ] Reporte de conciliacion exportable (PDF con firma de timestamp)
- [ ] Tests >= 98% coverage

**Dependencias:**
- EP-DB-001 (dashboard base)
- EP-DB-002 (datos de transacciones)
- EP-SP-009 (motor de reconciliacion existente)

**Complejidad:** L (conciliacion, integridad de ledger, discrepancias, multiples vistas)

**Repositorios:** `mf-dashboard`, `covacha-core`, `covacha-transaction`, `covacha-libs`

---

## User Stories Detalladas

---

### EP-DB-001: Dashboard Principal Multi-Tier

---

#### US-DB-001: Scaffold de mf-dashboard con arquitectura multi-tier

**ID:** US-DB-001
**Epica:** EP-DB-001
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero que mf-dashboard tenga la estructura base con routing diferenciado por tier, guards de autenticacion y lazy loading para que cada tipo de usuario vea la vista correcta automaticamente al entrar.

**Criterios de Aceptacion:**
- [ ] Modulo `mf-dashboard` registrado en `mf-core` via Native Federation (remoteEntry.json)
- [ ] Routing base:
  - `/dashboard` → redirect segun tier del usuario
  - `/dashboard/admin` → vista Tier 1 (guard: rol Admin)
  - `/dashboard/business` → vista Tier 2 (guard: rol B2B + org_id)
  - `/dashboard/personal` → vista Tier 3 (guard: rol B2C)
- [ ] Guards de autenticacion que verifican tier via Cognito claims
- [ ] Layout compartido: header con nombre de org/usuario, sidebar con navegacion por seccion
- [ ] Lazy loading de cada vista tier (standalone components)
- [ ] Servicio `DashboardContextService` que expone: tier, org_id, user_id, permissions
- [ ] Arquitectura hexagonal: domain/, application/, infrastructure/, presentation/
- [ ] Tests: guards, routing, context service

**Tareas Tecnicas:**
1. Configurar Native Federation en mf-dashboard (federation.config.js)
2. Registrar remote en mf-core (app.routes.ts)
3. Crear guards: `AdminGuard`, `BusinessGuard`, `PersonalGuard`
4. Crear `DashboardContextService` con signals
5. Crear layout compartido con sidebar de navegacion
6. Crear componentes placeholder para cada tier
7. Tests: 10+ unit tests

**Dependencias:** Ninguna (es la base)
**Estimacion:** 4 dev-days

---

#### US-DB-002: Vista Admin - Metricas globales del ecosistema

**ID:** US-DB-002
**Epica:** EP-DB-001
**Prioridad:** P0

**Historia:**
Como **Administrador SuperPago** quiero ver metricas globales del ecosistema (GMV total, numero de transacciones, comisiones, TPS promedio, organizaciones activas) en mi dashboard para monitorear la salud general de la plataforma de un vistazo.

**Criterios de Aceptacion:**
- [ ] Cards de KPI en la parte superior:
  - GMV total del periodo (con delta % vs periodo anterior)
  - Transacciones totales del periodo (con delta %)
  - Comisiones generadas (con delta %)
  - TPS promedio (con indicador de pico)
  - Organizaciones activas (con nuevas del periodo)
  - Usuarios activos (con nuevos del periodo)
- [ ] Grafica de tendencia de 7 dias (line chart) debajo de las cards
- [ ] Selector de periodo: hoy, 7 dias, 30 dias, trimestre, custom
- [ ] Datos provienen de metricas pre-calculadas (endpoint agregado, no queries en vivo)
- [ ] Loading skeleton mientras se cargan los datos
- [ ] Refresh automatico cada 5 minutos (o manual con boton)

**Tareas Tecnicas:**
1. Crear `AdminDashboardComponent` standalone con OnPush
2. Crear `MetricCardComponent` reutilizable (valor, delta, icono, color)
3. Crear `TrendChartComponent` con Chart.js
4. Crear `DashboardMetricsAdapter` (infrastructure) para llamar a la API
5. Endpoint backend: `GET /api/v1/dashboard/metrics/global?period=7d`
6. Lambda de pre-calculo de metricas globales (cada hora)
7. Tests: 8+ unit tests (componentes + adapter + endpoint)

**Dependencias:** US-DB-001
**Estimacion:** 5 dev-days

---

#### US-DB-003: Vista B2B - Metricas de organizacion

**ID:** US-DB-003
**Epica:** EP-DB-001
**Prioridad:** P0

**Historia:**
Como **Cliente Empresa** quiero ver las metricas de mi organizacion (saldo total, transacciones del periodo, comisiones acumuladas, cuentas activas, ultimos movimientos) en mi dashboard para tener control financiero de mis operaciones.

**Criterios de Aceptacion:**
- [ ] Cards de KPI:
  - Saldo total consolidado (suma de todas las cuentas)
  - Transacciones del periodo (con delta %)
  - Comisiones acumuladas del periodo
  - Cuentas activas (CLABE, dispersion, reservadas)
  - Volumen SPEI In del periodo
  - Volumen SPEI Out del periodo
- [ ] Grafica de tendencia de 7 dias (ingresos vs egresos)
- [ ] Lista de ultimos 10 movimientos (mini-tabla con fecha, tipo, monto, estado)
- [ ] Selector de periodo: hoy, 7 dias, 30 dias, custom
- [ ] Solo muestra datos de la organizacion del usuario autenticado
- [ ] Endpoint filtra por `sp_organization_id` del token

**Tareas Tecnicas:**
1. Crear `BusinessDashboardComponent` standalone con OnPush
2. Reutilizar `MetricCardComponent` de US-DB-002
3. Crear `RecentTransactionsComponent` (mini-tabla)
4. Endpoint backend: `GET /api/v1/dashboard/metrics/org/{org_id}?period=7d`
5. Pre-calculo de metricas por organizacion (Lambda)
6. Tests: 8+ unit tests

**Dependencias:** US-DB-001, US-DB-002 (componentes reutilizables)
**Estimacion:** 4 dev-days

---

#### US-DB-004: Vista B2C - Resumen personal

**ID:** US-DB-004
**Epica:** EP-DB-001
**Prioridad:** P1

**Historia:**
Como **Usuario Final** quiero ver un resumen simplificado de mi actividad (saldo disponible, gastos del mes, ingresos del mes, ultimos 5 movimientos) para tener claridad sobre mis finanzas personales en SuperPago.

**Criterios de Aceptacion:**
- [ ] Tarjeta principal grande: saldo disponible con icono de ojo para ocultar
- [ ] Tarjetas secundarias: gastos del mes, ingresos del mes, numero de transacciones
- [ ] Grafica donut simple: distribucion de gastos por tipo (SPEI, BillPay, Cash)
- [ ] Lista de ultimos 5 movimientos con icono por tipo, descripcion corta y monto
- [ ] Diseno mobile-first (la mayoria de B2C usara desde movil)
- [ ] Sin selector de periodo (siempre muestra mes actual)
- [ ] Endpoint filtra por `user_id` del token

**Tareas Tecnicas:**
1. Crear `PersonalDashboardComponent` standalone con OnPush
2. Crear `BalanceCardComponent` con toggle de visibilidad
3. Crear `ExpenseDonutComponent` con Chart.js
4. Endpoint backend: `GET /api/v1/dashboard/metrics/personal?user_id=X`
5. Tests: 6+ unit tests

**Dependencias:** US-DB-001
**Estimacion:** 3 dev-days

---

#### US-DB-005: Backend - Motor de pre-calculo de metricas

**ID:** US-DB-005
**Epica:** EP-DB-001
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero un motor de pre-calculo que agregue metricas financieras por hora, dia, semana y mes para que los endpoints del dashboard respondan en menos de 200ms sin hacer queries costosos en tiempo real.

**Criterios de Aceptacion:**
- [ ] Cola SQS `dashboard-aggregation` que recibe eventos de transacciones completadas
- [ ] Lambda `metrics-aggregator` que procesa eventos y actualiza contadores:
  - Incrementa contadores atomicos en DynamoDB (`ADD` operation)
  - Actualiza metricas por periodo: hourly, daily, weekly, monthly
  - Calcula promedios moviles (latencia, monto promedio)
- [ ] Metricas almacenadas en DynamoDB:
  - `PK: ORG#{org_id}#METRICS`, `SK: DAILY#2026-02-16`
  - `PK: GLOBAL#METRICS`, `SK: DAILY#2026-02-16`
- [ ] Cache en Redis con TTL de 5 minutos para queries frecuentes
- [ ] Invalidacion de cache cuando se actualiza una metrica
- [ ] Endpoints REST:
  - `GET /api/v1/dashboard/metrics/global?period={period}`
  - `GET /api/v1/dashboard/metrics/org/{org_id}?period={period}`
  - `GET /api/v1/dashboard/metrics/personal?user_id={user_id}`
- [ ] Tiempo de respuesta de endpoints < 200ms (p99)
- [ ] Idempotencia: mismo evento procesado 2 veces no duplica contadores

**Tareas Tecnicas:**
1. Crear cola SQS `dashboard-aggregation` con DLQ
2. Implementar Lambda `metrics-aggregator`
3. Crear `MetricsRepository` en covacha-libs (DynamoDB CRUD de metricas)
4. Crear Flask Blueprint `dashboard_metrics_bp` en covacha-core
5. Implementar cache en Redis con invalidacion
6. Configurar publicacion de eventos desde covacha-transaction
7. Tests: idempotencia, agregacion, cache invalidation, endpoints

**Dependencias:** EP-SP-003 (ledger como fuente de datos)
**Estimacion:** 6 dev-days

---

#### US-DB-006: Feed de actividad reciente por tier

**ID:** US-DB-006
**Epica:** EP-DB-001
**Prioridad:** P1

**Historia:**
Como **Usuario del dashboard** (cualquier tier) quiero ver un feed de actividad reciente contextualizado a mi rol para estar al tanto de los ultimos eventos relevantes sin tener que navegar a la seccion de transacciones.

**Criterios de Aceptacion:**
- [ ] Componente `ActivityFeedComponent` reutilizable entre tiers
- [ ] Tier 1: ultimos 20 eventos globales (transacciones grandes, alertas, nuevas orgs)
- [ ] Tier 2: ultimos 15 movimientos de la organizacion
- [ ] Tier 3: ultimos 5 movimientos personales
- [ ] Cada item muestra: icono por tipo, descripcion, monto (si aplica), tiempo relativo
- [ ] Click en item navega al detalle de la transaccion (link a EP-DB-002)
- [ ] Endpoint: `GET /api/v1/dashboard/activity?scope={global|org|personal}&limit=N`
- [ ] Ordenado por fecha descendente

**Tareas Tecnicas:**
1. Crear `ActivityFeedComponent` standalone con OnPush
2. Crear `ActivityItemComponent` con icono, descripcion, tiempo relativo
3. Crear `ActivityFeedAdapter` (infrastructure)
4. Endpoint backend con query a ultimas transacciones y eventos
5. Tests: 5+ unit tests

**Dependencias:** US-DB-001
**Estimacion:** 3 dev-days

---

### EP-DB-002: Reportes de Transacciones

---

#### US-DB-007: Tabla de transacciones con paginacion server-side

**ID:** US-DB-007
**Epica:** EP-DB-002
**Prioridad:** P0

**Historia:**
Como **Cliente Empresa** quiero ver una tabla de mis transacciones con paginacion eficiente para poder revisar el historial de operaciones sin que la interfaz se ralentice con grandes volumenes de datos.

**Criterios de Aceptacion:**
- [ ] Tabla con columnas: fecha/hora, tipo, concepto, monto, estado, cuenta, referencia
- [ ] Paginacion cursor-based (no offset): boton "Siguiente" y "Anterior" con `last_evaluated_key`
- [ ] Selector de items por pagina: 25, 50, 100
- [ ] Indicador de total estimado de registros
- [ ] Ordenamiento por fecha (desc por defecto, toggle asc/desc)
- [ ] Tier 1: filtro adicional por organizacion (dropdown de orgs)
- [ ] Tier 2: automaticamente filtrado por sp_organization_id
- [ ] Tier 3: automaticamente filtrado por user_id
- [ ] Endpoint: `GET /api/v1/reports/transactions?org_id=X&cursor=Y&limit=Z`
- [ ] Respuesta incluye `items`, `next_cursor`, `prev_cursor`, `total_estimate`

**Tareas Tecnicas:**
1. Crear `TransactionTableComponent` standalone con material table o CDK table
2. Crear `PaginationComponent` con cursor-based navigation
3. Crear `TransactionReportAdapter` (infrastructure)
4. Endpoint backend con DynamoDB query + cursor pagination
5. Crear `TransactionQueryService` en covacha-transaction
6. Tests: 8+ unit tests (frontend + backend)

**Dependencias:** US-DB-001 (routing y guards)
**Estimacion:** 5 dev-days

---

#### US-DB-008: Filtros avanzados de transacciones

**ID:** US-DB-008
**Epica:** EP-DB-002
**Prioridad:** P0

**Historia:**
Como **Cliente Empresa** quiero poder filtrar mis transacciones por multiples criterios (fecha, tipo, monto, estado, cuenta) para encontrar rapidamente las operaciones que necesito revisar o auditar.

**Criterios de Aceptacion:**
- [ ] Panel de filtros colapsable encima de la tabla
- [ ] Filtro por rango de fechas: date picker con presets (hoy, ayer, ultima semana, ultimo mes, custom)
- [ ] Filtro por tipo: multiselect (SPEI_IN, SPEI_OUT, BILLPAY, CASH_IN, CASH_OUT, INTERNAL)
- [ ] Filtro por rango de monto: inputs numerico min y max
- [ ] Filtro por estado: multiselect (COMPLETED, PENDING, FAILED, REVERSED)
- [ ] Filtro por cuenta: dropdown de cuentas de la organizacion
- [ ] Busqueda por referencia o ID: input de texto libre
- [ ] Boton "Limpiar filtros" para resetear todos
- [ ] Filtros se reflejan en URL (query params) para compartir links filtrados
- [ ] Filtros se envian al backend como query params del endpoint

**Tareas Tecnicas:**
1. Crear `TransactionFiltersComponent` standalone con reactive forms
2. Integrar filtros con `TransactionTableComponent` (EventEmitter)
3. Sincronizar filtros con query params del router
4. Actualizar endpoint backend para aceptar todos los filtros
5. Indices DynamoDB (GSIs) para queries eficientes por tipo y estado
6. Tests: 6+ unit tests

**Dependencias:** US-DB-007 (tabla base)
**Estimacion:** 4 dev-days

---

#### US-DB-009: Detalle expandible de transaccion

**ID:** US-DB-009
**Epica:** EP-DB-002
**Prioridad:** P1

**Historia:**
Como **Cliente Empresa** quiero expandir una fila de la tabla de transacciones para ver el detalle completo (asientos contables, cuentas involucradas, timestamps, metadata) sin salir de la vista de la tabla.

**Criterios de Aceptacion:**
- [ ] Click en fila expande seccion de detalle debajo de la fila
- [ ] Detalle muestra:
  - Informacion general: ID, tipo, concepto, referencia externa
  - Cuentas: origen (nombre, tipo, CLABE), destino (nombre, tipo, CLABE/banco)
  - Montos: monto bruto, comision, IVA, monto neto
  - Timestamps: creado, procesado, completado/fallido
  - Asientos contables de partida doble (tabla: cuenta, debito, credito)
  - Estado con timeline visual (created → processing → completed/failed)
- [ ] Boton "Ver completo" navega a pagina de detalle individual
- [ ] Solo una fila expandida a la vez (expandir otra colapsa la anterior)
- [ ] Endpoint: `GET /api/v1/reports/transactions/{transaction_id}/detail`

**Tareas Tecnicas:**
1. Crear `TransactionDetailComponent` standalone
2. Crear `LedgerEntriesComponent` para mostrar asientos de partida doble
3. Crear `TransactionTimelineComponent` para timeline visual de estados
4. Endpoint backend de detalle con join a ledger entries
5. Tests: 5+ unit tests

**Dependencias:** US-DB-007 (tabla base)
**Estimacion:** 3 dev-days

---

#### US-DB-010: Agrupacion por periodo con subtotales

**ID:** US-DB-010
**Epica:** EP-DB-002
**Prioridad:** P1

**Historia:**
Como **Cliente Empresa** quiero agrupar las transacciones de mi reporte por periodo (dia, semana, mes) con subtotales por grupo para tener una vision consolidada de la actividad por periodo.

**Criterios de Aceptacion:**
- [ ] Selector de agrupacion: ninguna, por dia, por semana, por mes
- [ ] Cuando esta activa la agrupacion: filas de encabezado de grupo con subtotales
- [ ] Subtotales por grupo: cantidad de transacciones, suma de montos, suma de comisiones
- [ ] Grupos colapsables (click en encabezado muestra/oculta transacciones del grupo)
- [ ] Total general al final de la tabla (suma de todos los grupos)
- [ ] Backend calcula subtotales en servidor (no en cliente) para grandes volumenes
- [ ] Endpoint: `GET /api/v1/reports/transactions?group_by=daily&include_subtotals=true`

**Tareas Tecnicas:**
1. Crear `GroupedTableComponent` que extiende la tabla base
2. Crear `SubtotalRowComponent` para filas de subtotal
3. Actualizar endpoint backend para agrupar y calcular subtotales
4. Tests: 5+ unit tests

**Dependencias:** US-DB-007, US-DB-008
**Estimacion:** 3 dev-days

---

#### US-DB-011: Busqueda rapida de transacciones por referencia

**ID:** US-DB-011
**Epica:** EP-DB-002
**Prioridad:** P2

**Historia:**
Como **Cliente Empresa** quiero buscar una transaccion especifica por su referencia, CLABE de rastreo o ID interno para localizar rapidamente una operacion cuando un cliente o proveedor me pregunta por ella.

**Criterios de Aceptacion:**
- [ ] Input de busqueda en la parte superior de la vista de transacciones
- [ ] Busca por: ID de transaccion, referencia numerica, CLABE de rastreo, concepto (parcial)
- [ ] Resultados aparecen mientras se escribe (debounce 300ms, minimo 3 caracteres)
- [ ] Resultado muestra match resaltado (highlight del texto que coincide)
- [ ] Si hay un solo resultado, auto-expande el detalle
- [ ] Endpoint: `GET /api/v1/reports/transactions/search?q={query}&org_id=X`
- [ ] GSI de busqueda en DynamoDB por referencia

**Tareas Tecnicas:**
1. Crear `TransactionSearchComponent` con debounce y highlight
2. Endpoint backend de busqueda con query a GSI
3. GSI: `PK=ORG#{org_id}#TXN_REF`, `SK={referencia}` para busqueda por referencia
4. Tests: 4+ unit tests

**Dependencias:** US-DB-007
**Estimacion:** 2 dev-days

---

### EP-DB-003: Analytics y Graficas Interactivas

---

#### US-DB-012: Time series de volumen y monto de transacciones

**ID:** US-DB-012
**Epica:** EP-DB-003
**Prioridad:** P0

**Historia:**
Como **Administrador SuperPago** quiero ver graficas de series de tiempo con el volumen y monto de transacciones con granularidad configurable para identificar tendencias, picos y anomalias en la actividad financiera.

**Criterios de Aceptacion:**
- [ ] Line chart con doble eje Y: volumen (izquierda), monto (derecha)
- [ ] Granularidad configurable: por hora (ultimas 24h), por dia (ultimo mes), por semana (ultimo trimestre), por mes (ultimo ano)
- [ ] Lineas separadas por tipo de transaccion (toggle para mostrar/ocultar cada tipo)
- [ ] Tooltip en hover: fecha, volumen exacto, monto exacto por tipo
- [ ] Zoom con selector de rango en eje X
- [ ] Datos de endpoint: `GET /api/v1/analytics/timeseries?granularity=daily&period=30d&org_id=X`
- [ ] Tier 1: datos globales; Tier 2: datos de org

**Tareas Tecnicas:**
1. Crear `TimeSeriesChartComponent` standalone con Chart.js
2. Crear servicio `AnalyticsAdapter` (infrastructure)
3. Endpoint backend que consulta metricas pre-calculadas por periodo
4. Tests: 5+ unit tests

**Dependencias:** US-DB-005 (metricas pre-calculadas)
**Estimacion:** 4 dev-days

---

#### US-DB-013: Distribucion por tipo de operacion (pie chart)

**ID:** US-DB-013
**Epica:** EP-DB-003
**Prioridad:** P1

**Historia:**
Como **Cliente Empresa** quiero ver un pie chart con la distribucion de mis transacciones por tipo de operacion para entender como se distribuye mi actividad financiera entre SPEI, BillPay, Cash e internos.

**Criterios de Aceptacion:**
- [ ] Pie chart (o donut) con segmentos por tipo: SPEI In, SPEI Out, BillPay, Cash In, Cash Out, Internal
- [ ] Toggle: distribucion por volumen (cantidad) o por monto (dinero)
- [ ] Leyenda con porcentajes y valores absolutos
- [ ] Click en segmento aplica filtro en tabla de transacciones (drill-down a EP-DB-002)
- [ ] Selector de periodo (mismo que el dashboard principal)
- [ ] Endpoint: `GET /api/v1/analytics/distribution?by=type&metric=volume&period=30d`

**Tareas Tecnicas:**
1. Crear `DistributionChartComponent` standalone con Chart.js
2. Integrar drill-down con router (navega a transacciones filtradas)
3. Endpoint backend de distribucion con agrupacion por tipo
4. Tests: 4+ unit tests

**Dependencias:** US-DB-012 (adapter reutilizable)
**Estimacion:** 3 dev-days

---

#### US-DB-014: Comparativa periodo-a-periodo

**ID:** US-DB-014
**Epica:** EP-DB-003
**Prioridad:** P1

**Historia:**
Como **Administrador SuperPago** quiero ver graficas comparativas entre periodos (mes actual vs anterior, trimestre actual vs anterior) para evaluar el crecimiento o decrecimiento de la plataforma.

**Criterios de Aceptacion:**
- [ ] Bar chart agrupado: periodo actual vs periodo anterior (lado a lado)
- [ ] Metricas comparables: volumen, monto total, comisiones, transacciones exitosas, tasa de fallo
- [ ] Indicador de delta porcentual sobre cada barra (verde si crece, rojo si decrece)
- [ ] Selector de comparacion: mes vs mes anterior, trimestre vs trimestre anterior, YoY (mismo mes del ano pasado)
- [ ] Tabla debajo del chart con valores exactos y deltas
- [ ] Endpoint: `GET /api/v1/analytics/comparison?current=2026-02&previous=2026-01`

**Tareas Tecnicas:**
1. Crear `ComparisonChartComponent` standalone con Chart.js (grouped bar)
2. Crear `ComparisonTableComponent` con deltas
3. Endpoint backend de comparacion entre dos periodos
4. Tests: 4+ unit tests

**Dependencias:** US-DB-005 (metricas por periodo)
**Estimacion:** 3 dev-days

---

#### US-DB-015: Heatmap de actividad

**ID:** US-DB-015
**Epica:** EP-DB-003
**Prioridad:** P2

**Historia:**
Como **Administrador SuperPago** quiero ver un heatmap de actividad por hora del dia y dia de la semana para identificar patrones de uso y planificar ventanas de mantenimiento en horarios de baja actividad.

**Criterios de Aceptacion:**
- [ ] Heatmap: eje X = hora del dia (0-23), eje Y = dia de la semana (lun-dom)
- [ ] Color de celda segun intensidad (gradiente de azul claro a azul oscuro)
- [ ] Tooltip en hover: dia, hora, volumen de transacciones, monto total
- [ ] Periodo configurable: ultima semana, ultimo mes, ultimo trimestre
- [ ] Endpoint: `GET /api/v1/analytics/heatmap?period=30d&org_id=X`

**Tareas Tecnicas:**
1. Crear `ActivityHeatmapComponent` standalone (canvas o SVG)
2. Endpoint backend que agrupa transacciones por dia_semana + hora
3. Tests: 3+ unit tests

**Dependencias:** US-DB-005
**Estimacion:** 3 dev-days

---

#### US-DB-016: Drill-down por organizacion (Tier 1)

**ID:** US-DB-016
**Epica:** EP-DB-003
**Prioridad:** P1

**Historia:**
Como **Administrador SuperPago** quiero hacer click en una organizacion desde las graficas globales para profundizar en las metricas especificas de esa organizacion sin tener que cambiar de vista manualmente.

**Criterios de Aceptacion:**
- [ ] En todas las graficas globales: click en data point que tenga org → navega a vista de esa org
- [ ] Vista de drill-down: mismas graficas pero filtradas a una organizacion
- [ ] Breadcrumb de navegacion: Dashboard > Global > Org: {nombre}
- [ ] Boton "Volver a global" para regresar
- [ ] Ranking de organizaciones (tabla con barras): top 10 por volumen/monto

**Tareas Tecnicas:**
1. Crear `OrgDrilldownComponent` standalone
2. Crear `OrgRankingComponent` con barra horizontal inline
3. Router con parametro: `/dashboard/admin/analytics/org/:orgId`
4. Tests: 4+ unit tests

**Dependencias:** US-DB-012, US-DB-013, US-DB-014
**Estimacion:** 3 dev-days

---

#### US-DB-017: Pagina de Analytics consolidada

**ID:** US-DB-017
**Epica:** EP-DB-003
**Prioridad:** P1

**Historia:**
Como **Usuario del dashboard** (Tier 1 o Tier 2) quiero una pagina dedicada de analytics que agrupe todas las graficas (time series, distribucion, comparativa, heatmap) en un layout organizado con tabs o secciones para tener una vista completa de mis datos analiticos.

**Criterios de Aceptacion:**
- [ ] Pagina `/dashboard/{tier}/analytics` con tabs: Tendencias, Distribucion, Comparativas, Actividad
- [ ] Tab Tendencias: time series (US-DB-012)
- [ ] Tab Distribucion: pie charts por tipo, por cuenta, por estado (US-DB-013)
- [ ] Tab Comparativas: comparacion entre periodos (US-DB-014)
- [ ] Tab Actividad: heatmap (US-DB-015) + drill-down (US-DB-016, solo Tier 1)
- [ ] Filtros globales en la parte superior (periodo, organizacion) que aplican a todas las tabs
- [ ] Estado de tab activa persistido en URL (query param `tab=tendencias`)

**Tareas Tecnicas:**
1. Crear `AnalyticsPageComponent` standalone con tabs (mat-tab-group o custom)
2. Integrar componentes de US-DB-012 a US-DB-016
3. Crear `GlobalFiltersComponent` con EventEmitter
4. Tests: 4+ unit tests

**Dependencias:** US-DB-012, US-DB-013, US-DB-014, US-DB-015
**Estimacion:** 3 dev-days

---

### EP-DB-004: KPIs Configurables

---

#### US-DB-018: Catalogo de metricas predefinidas

**ID:** US-DB-018
**Epica:** EP-DB-004
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero un catalogo de metricas predefinidas con formulas de calculo estandar para que los usuarios puedan seleccionar KPIs desde un listado sin tener que definir formulas manualmente.

**Criterios de Aceptacion:**
- [ ] Catalogo de metricas almacenado en DynamoDB:
  - `PK: METRIC_CATALOG`, `SK: METRIC#{metric_id}`
- [ ] Metricas predefinidas (minimo 10):
  - `GMV`: Gross Merchandise Value (suma de montos de transacciones completadas)
  - `TPS`: Transacciones por segundo (promedio del periodo)
  - `TPS_PEAK`: TPS maximo registrado en el periodo
  - `COMMISSION_TOTAL`: Total de comisiones generadas
  - `GROWTH_RATE`: Porcentaje de crecimiento vs periodo anterior
  - `SUCCESS_RATE`: Porcentaje de transacciones exitosas vs totales
  - `AVG_TRANSACTION`: Monto promedio de transaccion
  - `AVG_LATENCY`: Latencia promedio de procesamiento (ms)
  - `ACTIVE_ACCOUNTS`: Numero de cuentas con actividad en el periodo
  - `NEW_ACCOUNTS`: Numero de cuentas nuevas en el periodo
- [ ] Cada metrica tiene: id, nombre, descripcion, formula, unidad (currency, percentage, number, time), source_service
- [ ] Endpoint: `GET /api/v1/dashboard/kpis/catalog`

**Tareas Tecnicas:**
1. Crear dataclass `MetricDefinition` en covacha-libs
2. Seed de catalogo de metricas en DynamoDB
3. Crear `MetricCatalogRepository` (DynamoDB)
4. Endpoint REST en covacha-core
5. Tests: 4+ unit tests

**Dependencias:** Ninguna (es base para los demas US de la epica)
**Estimacion:** 3 dev-days

---

#### US-DB-019: Builder de KPI personalizado

**ID:** US-DB-019
**Epica:** EP-DB-004
**Prioridad:** P1

**Historia:**
Como **Cliente Empresa** quiero crear KPIs personalizados seleccionando una metrica del catalogo, configurando umbrales de alerta y eligiendo como se muestra en mi dashboard para adaptar la herramienta a las metricas que son relevantes para mi negocio.

**Criterios de Aceptacion:**
- [ ] Modal o drawer de creacion de KPI con pasos:
  1. Seleccionar metrica del catalogo (dropdown con preview)
  2. Configurar display: nombre custom, tipo de visualizacion (numero, gauge, sparkline)
  3. Configurar umbrales: valor warning, valor critical (opcionales)
  4. Preview del widget antes de guardar
- [ ] Persistencia en DynamoDB:
  - `PK: ORG#{org_id}#KPI`, `SK: KPI#{kpi_id}`
- [ ] Maximo 20 KPIs por organizacion (para evitar sobrecarga)
- [ ] Endpoint: `POST /api/v1/dashboard/kpis` (crear), `PUT /api/v1/dashboard/kpis/{kpi_id}` (editar), `DELETE /api/v1/dashboard/kpis/{kpi_id}` (eliminar)
- [ ] Tier 1: puede crear KPIs globales (sin org_id) o por org
- [ ] Tier 2: solo puede crear KPIs de su organizacion

**Tareas Tecnicas:**
1. Crear `KpiBuilderComponent` standalone con stepper (steps de Angular Material o custom)
2. Crear `KpiPreviewComponent` con preview en vivo
3. Crear `KpiAdapter` (infrastructure)
4. Endpoint backend CRUD de KPIs
5. Crear `KpiRepository` en covacha-libs
6. Tests: 6+ unit tests

**Dependencias:** US-DB-018 (catalogo de metricas)
**Estimacion:** 4 dev-days

---

#### US-DB-020: Widgets de KPI con drag-and-drop

**ID:** US-DB-020
**Epica:** EP-DB-004
**Prioridad:** P1

**Historia:**
Como **Cliente Empresa** quiero organizar los widgets de KPI en mi dashboard arrastrando y soltando para personalizar el layout segun mis preferencias y tener las metricas mas importantes en la posicion mas visible.

**Criterios de Aceptacion:**
- [ ] Grid de widgets con drag-and-drop (Angular CDK DragDrop)
- [ ] Widgets de tamanos configurables: 1x1, 2x1, 1x2, 2x2
- [ ] Cada widget muestra: nombre del KPI, valor actual, delta %, indicador de umbral
- [ ] Drop zones visuales al arrastrar (sombra donde se puede soltar)
- [ ] Guardar layout automaticamente al soltar (auto-save con debounce 2s)
- [ ] Layout guardado por usuario: `PK: USER#{user_id}#DASHBOARD`, `SK: LAYOUT#default`
- [ ] Boton "Agregar widget" que abre lista de KPIs disponibles

**Tareas Tecnicas:**
1. Crear `KpiGridComponent` standalone con CDK DragDropModule
2. Crear `KpiWidgetComponent` reutilizable con config de tamano
3. Crear `DashboardLayoutService` (guarda/carga layouts)
4. Endpoints: `GET/PUT /api/v1/dashboard/layouts/{user_id}`
5. Tests: 5+ unit tests

**Dependencias:** US-DB-019 (KPIs creados)
**Estimacion:** 4 dev-days

---

#### US-DB-021: Umbrales de alerta por KPI

**ID:** US-DB-021
**Epica:** EP-DB-004
**Prioridad:** P2

**Historia:**
Como **Cliente Empresa** quiero configurar umbrales de warning y critical en cada KPI para recibir indicacion visual inmediata cuando una metrica esta fuera de los rangos esperados.

**Criterios de Aceptacion:**
- [ ] En el widget de KPI: borde de color segun estado:
  - Normal (verde): valor dentro de rango
  - Warning (amarillo): valor supera umbral warning
  - Critical (rojo): valor supera umbral critical
- [ ] Animacion sutil de pulso en widgets con estado critical
- [ ] Evaluacion de umbrales cada vez que se actualiza el valor del KPI
- [ ] Si umbral critical se activa → opcionalmente crear alerta (link con EP-DB-007)
- [ ] Configuracion de umbrales editable desde el widget (click en icono de settings)

**Tareas Tecnicas:**
1. Actualizar `KpiWidgetComponent` con logica de umbrales y colores
2. Crear `ThresholdEvaluatorService` en application layer
3. Integrar con sistema de alertas (EP-DB-007) via evento
4. Tests: 4+ unit tests

**Dependencias:** US-DB-020 (widgets de KPI)
**Estimacion:** 2 dev-days

---

#### US-DB-022: Restaurar layout por defecto

**ID:** US-DB-022
**Epica:** EP-DB-004
**Prioridad:** P2

**Historia:**
Como **Cliente Empresa** quiero poder restaurar mi dashboard al layout por defecto de mi tier para volver a una configuracion limpia si mis personalizaciones se vuelven confusas.

**Criterios de Aceptacion:**
- [ ] Boton "Restaurar layout por defecto" en settings del dashboard
- [ ] Confirmacion con dialogo: "Esto eliminara tus widgets y layout personalizados. Continuar?"
- [ ] Layouts por defecto definidos por tier:
  - Tier 1: GMV, TPS, Comisiones, Success Rate, Orgs Activas + grafica de 7 dias
  - Tier 2: Saldo, Volumen, Comisiones, Success Rate + grafica de 7 dias
  - Tier 3: Saldo, Gastos del mes, Ingresos del mes + donut
- [ ] El layout por defecto se genera a partir de template del tier (no hardcoded en frontend)
- [ ] Endpoint: `POST /api/v1/dashboard/layouts/{user_id}/reset`

**Tareas Tecnicas:**
1. Crear templates de layout por defecto (configuracion en backend)
2. Endpoint de reset que elimina layout custom y genera el default
3. Dialogo de confirmacion en frontend
4. Tests: 3+ unit tests

**Dependencias:** US-DB-020
**Estimacion:** 2 dev-days

---

### EP-DB-005: Exportacion y Reportes Programados

---

#### US-DB-023: Exportacion on-demand a CSV, PDF y Excel

**ID:** US-DB-023
**Epica:** EP-DB-005
**Prioridad:** P0

**Historia:**
Como **Cliente Empresa** quiero exportar la tabla de transacciones actual (con los filtros aplicados) a CSV, PDF o Excel para integrar los datos con mi sistema contable o archivarlos como respaldo.

**Criterios de Aceptacion:**
- [ ] Boton "Exportar" en la barra de acciones de la tabla de transacciones
- [ ] Dropdown de formato: CSV, PDF, XLSX
- [ ] Exportacion incluye los filtros actualmente aplicados (mismos resultados que ve el usuario)
- [ ] Para reportes pequenos (<1000 filas): generacion inmediata en frontend (CSV) o sincrona (PDF/XLSX)
- [ ] Para reportes grandes (>=1000 filas): generacion asincrona via SQS:
  - Endpoint: `POST /api/v1/reports/generate` con body `{ type, format, filters }`
  - Respuesta: `{ report_id, status: "pending" }`
  - Notificacion cuando esta listo (in-app + email)
- [ ] Archivo en S3 con URL pre-firmada (expira en 24 horas)
- [ ] PDF incluye: header con logo y nombre de organizacion, fecha de generacion, filtros aplicados
- [ ] XLSX incluye: hoja de datos + hoja de resumen con totales

**Tareas Tecnicas:**
1. Crear `ExportService` (frontend) para CSV generado en cliente
2. Endpoint backend: `POST /api/v1/reports/generate`
3. Lambda `report-generator` que genera PDF (weasyprint o reportlab) y XLSX (openpyxl)
4. Almacenamiento en S3 con URL pre-firmada
5. Cola SQS `dashboard-reports` para generacion asincrona
6. Notificacion al completar (via covacha-notification)
7. Tests: 6+ unit tests

**Dependencias:** US-DB-007, US-DB-008 (tabla y filtros)
**Estimacion:** 5 dev-days

---

#### US-DB-024: Historial de reportes generados

**ID:** US-DB-024
**Epica:** EP-DB-005
**Prioridad:** P1

**Historia:**
Como **Cliente Empresa** quiero ver el historial de reportes que he generado con su estado y opcion de descarga para poder re-descargar reportes anteriores sin tener que regenerarlos.

**Criterios de Aceptacion:**
- [ ] Pagina `/dashboard/{tier}/reports/history`
- [ ] Tabla: fecha de solicitud, tipo de reporte, formato, filtros aplicados, estado, tamano, accion
- [ ] Estados: pendiente (spinner), generando (barra de progreso), completado (boton descargar), fallido (icono error + mensaje)
- [ ] Boton "Descargar" genera URL pre-firmada nueva de S3 (por si la anterior expiro)
- [ ] Boton "Regenerar" para reportes fallidos
- [ ] Retencion: reportes disponibles por 30 dias (TTL en DynamoDB)
- [ ] Endpoint: `GET /api/v1/reports/history?org_id=X&limit=20`

**Tareas Tecnicas:**
1. Crear `ReportHistoryComponent` standalone
2. Crear `ReportHistoryAdapter` (infrastructure)
3. Endpoint backend que consulta `ORG#{org_id}#REPORT` entries
4. Endpoint de re-descarga con nueva URL pre-firmada
5. Tests: 4+ unit tests

**Dependencias:** US-DB-023 (generacion de reportes)
**Estimacion:** 3 dev-days

---

#### US-DB-025: Reportes programados

**ID:** US-DB-025
**Epica:** EP-DB-005
**Prioridad:** P1

**Historia:**
Como **Cliente Empresa** quiero programar reportes automaticos (diario, semanal, mensual) que se generen y envien a mi email para recibir informacion financiera periodica sin tener que entrar a la plataforma.

**Criterios de Aceptacion:**
- [ ] Pagina `/dashboard/{tier}/reports/scheduled`
- [ ] Formulario de creacion de reporte programado:
  - Tipo de reporte: transacciones, resumen, conciliacion
  - Frecuencia: diario (a las 7am), semanal (lunes 7am), mensual (dia 1 a las 7am)
  - Formato: PDF, CSV, XLSX
  - Filtros predefinidos: tipo de transaccion, cuentas
  - Destinatarios: lista de emails (maximo 5)
- [ ] Persistencia: `PK: ORG#{org_id}#SCHEDULED_REPORT`, `SK: SCHEDULE#{schedule_id}`
- [ ] EventBridge rule que ejecuta Lambda segun frecuencia
- [ ] Lambda genera el reporte y envia por email via SES
- [ ] Toggle de habilitado/deshabilitado por schedule
- [ ] Maximo 5 reportes programados por organizacion
- [ ] Endpoints: CRUD `POST/GET/PUT/DELETE /api/v1/reports/scheduled`

**Tareas Tecnicas:**
1. Crear `ScheduledReportsComponent` standalone con formulario
2. Crear `ScheduledReportAdapter` (infrastructure)
3. Endpoint backend CRUD de reportes programados
4. EventBridge rules para ejecutar Lambda segun frecuencia
5. Lambda `scheduled-report-executor` que genera y envia
6. Tests: 5+ unit tests

**Dependencias:** US-DB-023 (Lambda de generacion reutilizable)
**Estimacion:** 5 dev-days

---

#### US-DB-026: Templates de reporte personalizables

**ID:** US-DB-026
**Epica:** EP-DB-005
**Prioridad:** P2

**Historia:**
Como **Administrador SuperPago** quiero definir templates de reporte con secciones configurables (metricas a incluir, columnas de la tabla, graficas, header/footer) para que los reportes generados tengan un formato profesional y consistente.

**Criterios de Aceptacion:**
- [ ] Templates almacenados en DynamoDB: `PK: REPORT_TEMPLATE`, `SK: TEMPLATE#{template_id}`
- [ ] Template define:
  - Header: logo, nombre de organizacion, titulo del reporte
  - Secciones: lista ordenada de bloques (resumen_metricas, tabla_transacciones, grafica_tendencia, grafica_distribucion)
  - Columnas de tabla: cuales mostrar y en que orden
  - Footer: disclaimer, fecha de generacion, pagina X de Y
- [ ] Templates por defecto para cada tipo de reporte (transacciones, resumen, conciliacion)
- [ ] Solo Tier 1 puede crear/editar templates
- [ ] Tier 2 selecciona un template al generar reporte
- [ ] Endpoint: `GET/POST/PUT /api/v1/reports/templates`

**Tareas Tecnicas:**
1. Crear dataclass `ReportTemplate` en covacha-libs
2. Crear `ReportTemplateRepository` (DynamoDB)
3. Endpoint CRUD de templates
4. Integrar templates con Lambda de generacion (US-DB-023)
5. Tests: 4+ unit tests

**Dependencias:** US-DB-023
**Estimacion:** 4 dev-days

---

#### US-DB-027: Exportacion simplificada para B2C

**ID:** US-DB-027
**Epica:** EP-DB-005
**Prioridad:** P2

**Historia:**
Como **Usuario Final** quiero descargar mi historial de movimientos como CSV desde mi vista personal para tener un respaldo de mis operaciones en un formato simple.

**Criterios de Aceptacion:**
- [ ] Boton "Descargar historial" en vista personal (solo CSV)
- [ ] Exporta los movimientos del mes actual por defecto
- [ ] Selector simple de mes para exportar meses anteriores
- [ ] Generacion inmediata en frontend (el volumen B2C es bajo)
- [ ] CSV con columnas: Fecha, Tipo, Concepto, Monto, Estado
- [ ] Nombre del archivo: `movimientos_{mes}_{ano}.csv`

**Tareas Tecnicas:**
1. Crear `PersonalExportComponent` con boton y selector de mes
2. Generacion CSV en frontend usando Blob + download
3. Tests: 3+ unit tests

**Dependencias:** US-DB-004 (vista personal)
**Estimacion:** 1 dev-day

---

### EP-DB-006: Dashboard en Tiempo Real

---

#### US-DB-028: Endpoint SSE para metricas en vivo

**ID:** US-DB-028
**Epica:** EP-DB-006
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero un endpoint Server-Sent Events (SSE) que emita actualizaciones de metricas en tiempo real para que el frontend pueda mostrar cambios sin necesidad de polling.

**Criterios de Aceptacion:**
- [ ] Endpoint SSE: `GET /api/v1/dashboard/stream`
- [ ] Query params: `org_id` (filtro), `tier` (filtro), `token` (autenticacion)
- [ ] Tipos de evento SSE:
  - `metric_update`: `{ metric_id, value, delta, timestamp }`
  - `new_transaction`: `{ transaction_id, type, amount, status, timestamp }`
  - `alert_triggered`: `{ alert_id, severity, message, timestamp }`
  - `service_status`: `{ service_name, status: healthy|degraded|down, timestamp }`
- [ ] Backend usa Redis Pub/Sub para distribuir eventos entre instancias
- [ ] Canal Redis: `dashboard:{org_id}` (por org), `dashboard:global` (para Tier 1)
- [ ] Lambda publica a Redis cuando procesa transacciones (via metrics-aggregator)
- [ ] Heartbeat cada 30 segundos para mantener conexion viva
- [ ] Limite: maximo 50 conexiones SSE concurrentes por organizacion
- [ ] Autenticacion via token JWT en query param (SSE no soporta headers custom)

**Tareas Tecnicas:**
1. Implementar endpoint SSE en Flask (streaming response con `text/event-stream`)
2. Configurar Redis Pub/Sub en covacha-core
3. Crear `SSEPublisher` que publica eventos a Redis desde Lambda
4. Implementar heartbeat y connection management
5. Autenticacion de SSE via query param token
6. Tests: 5+ unit tests

**Dependencias:** US-DB-005 (Lambda que genera eventos)
**Estimacion:** 5 dev-days

---

#### US-DB-029: Contadores en vivo y TPS

**ID:** US-DB-029
**Epica:** EP-DB-006
**Prioridad:** P0

**Historia:**
Como **Administrador SuperPago** quiero ver contadores de transacciones y TPS que se actualizan en tiempo real para monitorear la actividad de la plataforma sin tener que refrescar la pagina.

**Criterios de Aceptacion:**
- [ ] Widget de TPS en vivo: numero grande con animacion de incremento/decremento
- [ ] Contador de transacciones del dia: se incrementa cada vez que llega un `new_transaction`
- [ ] Monto acumulado del dia: se incrementa con cada transaccion
- [ ] Mini sparkline de TPS ultimos 5 minutos (grafica pequena inline)
- [ ] Indicador de tendencia: flecha arriba/abajo comparando ultimo minuto vs promedio
- [ ] Conexion SSE con reconexion automatica (EventSource con retry)

**Tareas Tecnicas:**
1. Crear `LiveCountersComponent` standalone con animaciones de conteo
2. Crear `TpsSparklineComponent` con mini grafica de 5 min
3. Crear `SseConnectionService` (singleton) que gestiona EventSource
4. Tests: 4+ unit tests

**Dependencias:** US-DB-028 (endpoint SSE)
**Estimacion:** 3 dev-days

---

#### US-DB-030: Feed de transacciones en tiempo real

**ID:** US-DB-030
**Epica:** EP-DB-006
**Prioridad:** P1

**Historia:**
Como **Administrador SuperPago** quiero ver un feed de transacciones que se actualiza en tiempo real (nuevas transacciones aparecen arriba de la lista con animacion) para monitorear la actividad sin latencia.

**Criterios de Aceptacion:**
- [ ] Feed tipo "ticker": nuevas transacciones aparecen en la parte superior con animacion de slide-in
- [ ] Cada item muestra: hora, tipo (icono), monto, organizacion (Tier 1), estado
- [ ] Maximo 50 items visibles (las mas antiguas se eliminan del DOM)
- [ ] Indicador visual por tipo de transaccion (color + icono)
- [ ] Pause/resume del feed (boton para pausar el scroll automatico)
- [ ] Click en item navega al detalle de la transaccion
- [ ] Solo disponible para Tier 1 y Tier 2

**Tareas Tecnicas:**
1. Crear `LiveTransactionFeedComponent` standalone con animaciones Angular
2. Integrar con `SseConnectionService` (US-DB-029)
3. Implementar virtual scrolling para rendimiento (CDK ScrollingModule)
4. Tests: 4+ unit tests

**Dependencias:** US-DB-028
**Estimacion:** 3 dev-days

---

#### US-DB-031: Status de servicios del ecosistema

**ID:** US-DB-031
**Epica:** EP-DB-006
**Prioridad:** P1

**Historia:**
Como **Administrador SuperPago** quiero ver el estado de salud de cada servicio del ecosistema (backends, bases de datos, colas) en el dashboard para detectar problemas de infraestructura rapidamente.

**Criterios de Aceptacion:**
- [ ] Panel de status con indicadores por servicio:
  - covacha-core: verde/amarillo/rojo
  - covacha-transaction: verde/amarillo/rojo
  - covacha-payment: verde/amarillo/rojo
  - covacha-notification: verde/amarillo/rojo
  - covacha-webhook: verde/amarillo/rojo
  - DynamoDB: verde/amarillo/rojo
  - SQS queues depth: numero de mensajes en cola
  - Redis: verde/amarillo/rojo
- [ ] Health check cada 30 segundos via SSE `service_status` event
- [ ] Historico de ultimas 24 horas de uptime por servicio (mini barra de colores)
- [ ] Click en servicio muestra detalle: latencia promedio, error rate, ultimo error
- [ ] Solo disponible para Tier 1
- [ ] Backend: endpoint `/api/v1/dashboard/health` que agrega health checks de todos los servicios

**Tareas Tecnicas:**
1. Crear `ServiceStatusComponent` standalone con indicadores de color
2. Crear `UptimeBarComponent` con mini barra historica
3. Endpoint backend que agrega health checks (llama a /health de cada servicio)
4. Persistir status historico en DynamoDB (TTL 48h)
5. Tests: 4+ unit tests

**Dependencias:** US-DB-028
**Estimacion:** 4 dev-days

---

#### US-DB-032: Reconexion automatica de SSE

**ID:** US-DB-032
**Epica:** EP-DB-006
**Prioridad:** P1

**Historia:**
Como **Usuario del dashboard** quiero que la conexion en tiempo real se reconecte automaticamente cuando se pierda (por red inestable o deploy del backend) para no perder visibilidad de los datos en vivo.

**Criterios de Aceptacion:**
- [ ] EventSource con retry automatico (exponential backoff: 1s, 2s, 4s, 8s, max 30s)
- [ ] Indicador visual de estado de conexion: conectado (verde), reconectando (amarillo), desconectado (rojo)
- [ ] Al reconectar: solicitar estado actual para sincronizar (no solo esperar nuevos eventos)
- [ ] Si se pierde conexion por mas de 60 segundos: fallback a polling cada 30 segundos
- [ ] Notificacion sutil al usuario: "Conexion restaurada" al reconectar

**Tareas Tecnicas:**
1. Implementar logica de reconexion en `SseConnectionService`
2. Crear `ConnectionStatusComponent` indicador visual
3. Implementar fallback a polling con `interval()` de RxJS
4. Tests: 4+ unit tests

**Dependencias:** US-DB-028
**Estimacion:** 2 dev-days

---

### EP-DB-007: Alertas y Notificaciones en Dashboard

---

#### US-DB-033: Centro de notificaciones en header

**ID:** US-DB-033
**Epica:** EP-DB-007
**Prioridad:** P0

**Historia:**
Como **Usuario del dashboard** (cualquier tier) quiero un icono de campana en el header con badge que indique notificaciones no leidas para estar al tanto de eventos importantes sin tener que revisar manualmente.

**Criterios de Aceptacion:**
- [ ] Icono de campana en header del dashboard (posicion superior derecha)
- [ ] Badge numerico con conteo de notificaciones no leidas
- [ ] Click en campana abre panel desplegable con lista de ultimas 20 notificaciones
- [ ] Cada notificacion muestra: icono de severidad, titulo, mensaje corto, tiempo relativo
- [ ] Severidad visual: INFO (azul), WARNING (amarillo), CRITICAL (rojo con pulso)
- [ ] Click en notificacion navega al contexto relevante (ej: transaccion, alerta, reporte)
- [ ] Boton "Marcar todas como leidas"
- [ ] Notificaciones llegan via SSE (EP-DB-006) en tiempo real
- [ ] Endpoint: `GET /api/v1/dashboard/notifications?org_id=X&unread=true&limit=20`

**Tareas Tecnicas:**
1. Crear `NotificationBellComponent` standalone en header
2. Crear `NotificationPanelComponent` (overlay/dropdown)
3. Crear `NotificationItemComponent` con severidad visual
4. Crear `NotificationAdapter` (infrastructure)
5. Endpoint backend de notificaciones con filtro de leidas/no leidas
6. Tests: 5+ unit tests

**Dependencias:** US-DB-028 (SSE para recibir notificaciones en vivo)
**Estimacion:** 4 dev-days

---

#### US-DB-034: Reglas de alerta configurables

**ID:** US-DB-034
**Epica:** EP-DB-007
**Prioridad:** P0

**Historia:**
Como **Cliente Empresa** quiero configurar reglas de alerta basadas en metricas (ej: "si el monto de una transaccion supera $50,000 MXN, alertar") para recibir notificaciones proactivas cuando algo requiere mi atencion.

**Criterios de Aceptacion:**
- [ ] Pagina `/dashboard/{tier}/alerts/rules` con lista de reglas configuradas
- [ ] Formulario de creacion de regla:
  - Nombre de la regla (texto libre)
  - Metrica: seleccionar del catalogo (US-DB-018) o metrica de transaccion individual
  - Operador: mayor que, menor que, igual a, mayor o igual, menor o igual
  - Umbral: valor numerico
  - Severidad: INFO, WARNING, CRITICAL
  - Canales: in-app (siempre), email (opcional), webhook (opcional, solo Tier 2)
  - Cooldown: tiempo minimo entre alertas repetidas (1h, 4h, 24h)
- [ ] Persistencia: `PK: ORG#{org_id}#ALERT_RULE`, `SK: ALERT#{alert_id}`
- [ ] Toggle de habilitado/deshabilitado por regla
- [ ] Tier 1: reglas globales del ecosistema
- [ ] Tier 2: reglas de su organizacion (maximo 10)
- [ ] Endpoint CRUD: `POST/GET/PUT/DELETE /api/v1/dashboard/alerts/rules`

**Tareas Tecnicas:**
1. Crear `AlertRulesComponent` standalone con lista y formulario
2. Crear `AlertRuleFormComponent` con reactive forms
3. Crear `AlertRuleAdapter` (infrastructure)
4. Endpoint backend CRUD de reglas de alerta
5. Crear `AlertRuleRepository` en covacha-libs
6. Tests: 6+ unit tests

**Dependencias:** US-DB-018 (catalogo de metricas)
**Estimacion:** 4 dev-days

---

#### US-DB-035: Evaluacion de reglas y generacion de alertas

**ID:** US-DB-035
**Epica:** EP-DB-007
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero que cada vez que se actualice una metrica se evaluen las reglas de alerta configuradas y se genere una notificacion si se cumple la condicion para que los usuarios reciban alertas proactivas sin delay.

**Criterios de Aceptacion:**
- [ ] Lambda `alert-evaluator` que se ejecuta:
  - Cada vez que `metrics-aggregator` actualiza una metrica
  - Cada vez que llega una transaccion individual que tiene regla de monto
- [ ] Flujo:
  1. Recibe evento de metrica actualizada
  2. Consulta reglas activas de la organizacion
  3. Evalua cada regla contra el valor actual
  4. Si se cumple y no esta en cooldown → genera alerta
  5. Publica alerta en Redis (para SSE) y en SQS (para email/webhook)
- [ ] Cooldown respetado: si una regla ya genero alerta y no ha pasado el cooldown, no genera otra
- [ ] Persistencia de alerta: `PK: ORG#{org_id}#ALERT_LOG`, `SK: {timestamp}#{alert_id}`
- [ ] Integracion con EP-SP-029: publica en cola `sp-notification-events` para canales email/webhook

**Tareas Tecnicas:**
1. Implementar Lambda `alert-evaluator`
2. Logica de evaluacion de reglas con soporte de operadores
3. Implementar cooldown con DynamoDB (last_triggered_at)
4. Publicacion a Redis + SQS
5. Integracion con dispatcher de EP-SP-029
6. Tests: 6+ unit tests

**Dependencias:** US-DB-034, US-DB-028
**Estimacion:** 5 dev-days

---

#### US-DB-036: Acciones sobre alertas (acknowledge, snooze, dismiss)

**ID:** US-DB-036
**Epica:** EP-DB-007
**Prioridad:** P1

**Historia:**
Como **Cliente Empresa** quiero poder actuar sobre las alertas recibidas (confirmar lectura, posponer, descartar) para gestionar mis notificaciones y evitar ruido de alertas que ya conozco.

**Criterios de Aceptacion:**
- [ ] En el panel de notificaciones y en la pagina de historial:
  - Acknowledge: marca como leida (icono de check)
  - Snooze: posponer alerta por 1h, 4h o 24h (la alerta reaparece despues)
  - Dismiss: descartar permanentemente (no reaparece, queda en historial)
- [ ] Swipe actions en mobile (swipe izquierda: dismiss, swipe derecha: snooze)
- [ ] Endpoint: `PUT /api/v1/dashboard/notifications/{notification_id}/action`
- [ ] Body: `{ action: "acknowledge|snooze|dismiss", snooze_until: "ISO 8601" }`
- [ ] Snooze: Lambda que re-publica la alerta cuando vence el snooze

**Tareas Tecnicas:**
1. Actualizar `NotificationItemComponent` con botones de accion
2. Implementar swipe en mobile (HammerJS o CDK gesture)
3. Endpoint backend de acciones sobre notificaciones
4. Lambda de snooze con scheduling (EventBridge)
5. Tests: 4+ unit tests

**Dependencias:** US-DB-033
**Estimacion:** 3 dev-days

---

#### US-DB-037: Historial de alertas con filtros

**ID:** US-DB-037
**Epica:** EP-DB-007
**Prioridad:** P1

**Historia:**
Como **Cliente Empresa** quiero ver el historial completo de alertas con filtros por severidad, fecha y tipo para auditar que alertas se generaron y como fueron gestionadas.

**Criterios de Aceptacion:**
- [ ] Pagina `/dashboard/{tier}/alerts/history`
- [ ] Tabla con columnas: fecha, severidad (icono+color), regla, metrica, valor, accion tomada
- [ ] Filtros: severidad (INFO, WARNING, CRITICAL), rango de fechas, regla especifica, estado (activa, acknowledged, snoozed, dismissed)
- [ ] Paginacion server-side (cursor-based)
- [ ] Detalle expandible: muestra contexto completo de la alerta (metrica, umbral, valor, timestamp exacto)
- [ ] Endpoint: `GET /api/v1/dashboard/alerts/history?org_id=X&severity=CRITICAL&cursor=Y`

**Tareas Tecnicas:**
1. Crear `AlertHistoryComponent` standalone con tabla y filtros
2. Crear `AlertHistoryAdapter` (infrastructure)
3. Endpoint backend de historial con filtros y paginacion cursor
4. Tests: 4+ unit tests

**Dependencias:** US-DB-035, US-DB-036
**Estimacion:** 3 dev-days

---

### EP-DB-008: Dashboard de Conciliacion y Salud Financiera

---

#### US-DB-038: Vista de conciliacion diaria

**ID:** US-DB-038
**Epica:** EP-DB-008
**Prioridad:** P0

**Historia:**
Como **Administrador SuperPago** quiero ver un resumen de conciliacion diaria que muestre la cantidad de transacciones esperadas vs procesadas por dia para detectar rapidamente dias con discrepancias.

**Criterios de Aceptacion:**
- [ ] Tabla de conciliacion: fecha, transacciones esperadas, transacciones procesadas, delta, status (OK/pendiente/discrepancia)
- [ ] Color de fila: verde (OK, delta=0), amarillo (pendiente, dia en curso), rojo (discrepancia, delta != 0)
- [ ] Rango de fechas: ultimos 30 dias por defecto
- [ ] Click en fila expande detalle del dia (transacciones con discrepancia)
- [ ] Tier 1: ve conciliacion de todas las organizaciones (agrupable por org)
- [ ] Tier 2: ve solo conciliacion de su organizacion
- [ ] Endpoint: `GET /api/v1/dashboard/reconciliation/daily?org_id=X&from=Y&to=Z`
- [ ] Datos provienen del motor de reconciliacion de EP-SP-009

**Tareas Tecnicas:**
1. Crear `ReconciliationDailyComponent` standalone con tabla coloreada
2. Crear `ReconciliationAdapter` (infrastructure)
3. Endpoint backend que consulta resultados de reconciliacion
4. Tests: 5+ unit tests

**Dependencias:** EP-SP-009 (motor de reconciliacion)
**Estimacion:** 4 dev-days

---

#### US-DB-039: Balance general por organizacion

**ID:** US-DB-039
**Epica:** EP-DB-008
**Prioridad:** P0

**Historia:**
Como **Administrador SuperPago** quiero ver el balance general de cada organizacion (saldos de todas sus cuentas con totales) para tener visibilidad sobre la posicion financiera de cada cliente.

**Criterios de Aceptacion:**
- [ ] Vista de balance con tabla: organizacion, tipo de cuenta, nombre de cuenta, saldo actual, moneda
- [ ] Agrupacion por organizacion con subtotales
- [ ] Total general del ecosistema (suma de saldos de todas las cuentas)
- [ ] Indicador visual si el saldo es negativo (rojo, no deberia ocurrir)
- [ ] Filtro por organizacion (Tier 1) o automatico (Tier 2)
- [ ] Endpoint: `GET /api/v1/dashboard/balance?org_id=X`
- [ ] Datos directos del ledger (EP-SP-003), query en tiempo real (no pre-calculado)

**Tareas Tecnicas:**
1. Crear `BalanceSheetComponent` standalone con tabla agrupada
2. Endpoint backend que consulta saldos actuales de cuentas del ledger
3. Tests: 4+ unit tests

**Dependencias:** EP-SP-003 (ledger de partida doble)
**Estimacion:** 3 dev-days

---

#### US-DB-040: Verificacion de integridad del ledger

**ID:** US-DB-040
**Epica:** EP-DB-008
**Prioridad:** P0

**Historia:**
Como **Administrador SuperPago** quiero una verificacion automatica de que la suma de debitos es igual a la suma de creditos en el ledger de cada organizacion para garantizar la integridad contable del sistema.

**Criterios de Aceptacion:**
- [ ] Indicador de integridad por organizacion: checkmark verde (integro) o X roja (discrepancia)
- [ ] Tabla: organizacion, total debitos, total creditos, diferencia, status
- [ ] Si diferencia != 0: fila en rojo con alerta automatica
- [ ] Verificacion ejecutada diariamente a las 2am (Lambda programada)
- [ ] Tambien ejecutable on-demand con boton "Verificar ahora"
- [ ] Historico de verificaciones: fecha, resultado, diferencia detectada (si hubo)
- [ ] Endpoint: `GET /api/v1/dashboard/ledger-integrity?org_id=X`
- [ ] Endpoint: `POST /api/v1/dashboard/ledger-integrity/verify` (ejecutar on-demand)

**Tareas Tecnicas:**
1. Crear `LedgerIntegrityComponent` standalone con tabla e indicadores
2. Lambda `ledger-integrity-checker` que ejecuta verificacion
3. EventBridge rule para ejecucion diaria a las 2am
4. Endpoint de consulta y de ejecucion on-demand
5. Persistencia de resultados en DynamoDB
6. Tests: 5+ unit tests

**Dependencias:** EP-SP-003 (ledger)
**Estimacion:** 4 dev-days

---

#### US-DB-041: Lista de discrepancias detectadas

**ID:** US-DB-041
**Epica:** EP-DB-008
**Prioridad:** P1

**Historia:**
Como **Administrador SuperPago** quiero ver una lista detallada de todas las discrepancias detectadas (conciliacion o integridad) con opcion de marcarlas como resueltas para llevar un control de incidentes financieros.

**Criterios de Aceptacion:**
- [ ] Tabla de discrepancias: ID, fecha deteccion, tipo (conciliacion/integridad), organizacion, descripcion, monto discrepante, estado (abierta/resuelta)
- [ ] Filtros: tipo, organizacion, estado, rango de fechas
- [ ] Accion "Resolver": marca como resuelta con nota explicativa obligatoria
- [ ] Historico de resoluciones: quien resolvio, cuando, nota
- [ ] Alerta automatica cuando se detecta nueva discrepancia (integracion con EP-DB-007)
- [ ] Endpoint: `GET /api/v1/dashboard/discrepancies?status=open`
- [ ] Endpoint: `PUT /api/v1/dashboard/discrepancies/{id}/resolve` con body `{ note }`

**Tareas Tecnicas:**
1. Crear `DiscrepancyListComponent` standalone con tabla y filtros
2. Crear `ResolveDialogComponent` con campo de nota
3. Endpoints backend de listado y resolucion
4. Crear `DiscrepancyRepository` en covacha-libs
5. Tests: 5+ unit tests

**Dependencias:** US-DB-038, US-DB-040
**Estimacion:** 4 dev-days

---

#### US-DB-042: Health check del sistema financiero

**ID:** US-DB-042
**Epica:** EP-DB-008
**Prioridad:** P1

**Historia:**
Como **Administrador SuperPago** quiero un panel de health check financiero que muestre metricas de consistencia (tasa de reconciliacion, integridad del ledger, settlements pendientes) para evaluar la salud general del sistema financiero de un vistazo.

**Criterios de Aceptacion:**
- [ ] Panel de health con indicadores tipo semaforo:
  - Ledger Integrity: % de organizaciones con ledger integro
  - Reconciliation Rate: % de dias sin discrepancias (ultimos 30 dias)
  - Pending Settlements: numero de transacciones pendientes de settlement (>24h)
  - Failed Transactions Rate: % de transacciones fallidas (ultimas 24h)
  - Queue Depth: mensajes en colas SQS (si > umbral → amarillo/rojo)
- [ ] Gauge chart por cada metrica (0-100% con zonas de color)
- [ ] Timestamp de ultima actualizacion por metrica
- [ ] Refresh automatico cada 5 minutos
- [ ] Solo disponible para Tier 1
- [ ] Endpoint: `GET /api/v1/dashboard/financial-health`

**Tareas Tecnicas:**
1. Crear `FinancialHealthComponent` standalone con gauges
2. Crear `GaugeChartComponent` reutilizable
3. Endpoint backend que agrega multiples health checks financieros
4. Tests: 4+ unit tests

**Dependencias:** US-DB-038, US-DB-040
**Estimacion:** 3 dev-days

---

#### US-DB-043: Reporte de conciliacion exportable con timestamp firmado

**ID:** US-DB-043
**Epica:** EP-DB-008
**Prioridad:** P2

**Historia:**
Como **Administrador SuperPago** quiero exportar el reporte de conciliacion diaria como PDF con timestamp firmado para tener un registro auditable de la conciliacion financiera.

**Criterios de Aceptacion:**
- [ ] Boton "Exportar conciliacion" en vista de conciliacion diaria
- [ ] PDF incluye:
  - Header: logo, "Reporte de Conciliacion", fecha de generacion
  - Tabla de conciliacion del periodo seleccionado
  - Resumen: total esperado, total procesado, discrepancias
  - Resultado de integridad del ledger
  - Firma: hash SHA-256 del contenido + timestamp ISO 8601
  - Footer: "Generado automaticamente por SuperPago. Hash: {hash}"
- [ ] Generacion asincrona reutilizando Lambda de EP-DB-005
- [ ] Almacenamiento en S3 con retencion de 5 anos

**Tareas Tecnicas:**
1. Template de PDF de conciliacion (reutilizar infra de US-DB-023)
2. Agregar firma SHA-256 al contenido del PDF
3. Configurar retencion de 5 anos en bucket S3
4. Tests: 3+ unit tests

**Dependencias:** US-DB-023, US-DB-038
**Estimacion:** 3 dev-days

---

#### US-DB-044: Vista de conciliacion para Tier 2 (B2B)

**ID:** US-DB-044
**Epica:** EP-DB-008
**Prioridad:** P1

**Historia:**
Como **Cliente Empresa** quiero ver la conciliacion de mis transacciones comparando mis registros internos con los de SuperPago para verificar que todas mis operaciones se procesaron correctamente.

**Criterios de Aceptacion:**
- [ ] Vista simplificada de conciliacion para Tier 2: `/dashboard/business/reconciliation`
- [ ] Tabla: fecha, mis transacciones enviadas, transacciones procesadas en SuperPago, delta
- [ ] Indicador por dia: OK (match), pendiente (dia en curso), discrepancia (mismatch)
- [ ] Detalle por dia: lista de transacciones con status de matching
- [ ] Filtro por rango de fechas y tipo de transaccion
- [ ] No puede resolver discrepancias (solo ver), debe contactar soporte
- [ ] Reutiliza componentes de US-DB-038 con permisos reducidos

**Tareas Tecnicas:**
1. Adaptar `ReconciliationDailyComponent` para Tier 2 (permisos reducidos)
2. Filtro automatico por org_id del usuario
3. Ocultar acciones de resolucion
4. Tests: 3+ unit tests

**Dependencias:** US-DB-038
**Estimacion:** 2 dev-days

---

#### US-DB-045: Pagina consolidada de Salud Financiera

**ID:** US-DB-045
**Epica:** EP-DB-008
**Prioridad:** P1

**Historia:**
Como **Administrador SuperPago** quiero una pagina consolidada de salud financiera que agrupe conciliacion, integridad del ledger, discrepancias y health checks en una sola vista para tener la imagen completa del estado financiero del ecosistema.

**Criterios de Aceptacion:**
- [ ] Pagina `/dashboard/admin/financial-health` con secciones:
  - Seccion 1: Health gauges (US-DB-042) en la parte superior
  - Seccion 2: Conciliacion diaria resumida (US-DB-038) con link a detalle
  - Seccion 3: Integridad del ledger por org (US-DB-040) con link a detalle
  - Seccion 4: Discrepancias abiertas (US-DB-041) con link a lista completa
- [ ] Cada seccion muestra maximo 5 items con boton "Ver todo"
- [ ] Indicador general de salud en el header: "Saludable" (verde), "Atencion requerida" (amarillo), "Critico" (rojo)
- [ ] Solo disponible para Tier 1

**Tareas Tecnicas:**
1. Crear `FinancialHealthPageComponent` standalone que compone los sub-componentes
2. Logica de calculo de indicador general de salud
3. Links de navegacion a vistas de detalle
4. Tests: 4+ unit tests

**Dependencias:** US-DB-038, US-DB-040, US-DB-041, US-DB-042
**Estimacion:** 3 dev-days

---

## Roadmap

### Fase 1: Fundacion (Sprints 1-3)

| Sprint | Epica | User Stories | Entregable |
|--------|-------|-------------|------------|
| Sprint 1 | EP-DB-001 | US-DB-001, US-DB-005 | Scaffold mf-dashboard + motor de metricas backend |
| Sprint 2 | EP-DB-001 | US-DB-002, US-DB-003, US-DB-004 | Vistas principales de los 3 tiers |
| Sprint 3 | EP-DB-001, EP-DB-002 | US-DB-006, US-DB-007, US-DB-008 | Feed de actividad + tabla de transacciones con filtros |

### Fase 2: Reportes y Analytics (Sprints 4-6)

| Sprint | Epica | User Stories | Entregable |
|--------|-------|-------------|------------|
| Sprint 4 | EP-DB-002, EP-DB-003 | US-DB-009, US-DB-010, US-DB-011, US-DB-012 | Detalle de transacciones + time series |
| Sprint 5 | EP-DB-003 | US-DB-013, US-DB-014, US-DB-015, US-DB-016, US-DB-017 | Graficas completas + pagina de analytics |
| Sprint 6 | EP-DB-004 | US-DB-018, US-DB-019, US-DB-020, US-DB-021, US-DB-022 | KPIs configurables con drag-and-drop |

### Fase 3: Exportacion y Tiempo Real (Sprints 7-9)

| Sprint | Epica | User Stories | Entregable |
|--------|-------|-------------|------------|
| Sprint 7 | EP-DB-005 | US-DB-023, US-DB-024, US-DB-025 | Exportacion + historial + reportes programados |
| Sprint 8 | EP-DB-005, EP-DB-006 | US-DB-026, US-DB-027, US-DB-028, US-DB-029 | Templates + SSE + contadores en vivo |
| Sprint 9 | EP-DB-006 | US-DB-030, US-DB-031, US-DB-032 | Feed en vivo + status servicios + reconexion |

### Fase 4: Alertas y Conciliacion (Sprints 10-12)

| Sprint | Epica | User Stories | Entregable |
|--------|-------|-------------|------------|
| Sprint 10 | EP-DB-007 | US-DB-033, US-DB-034, US-DB-035 | Centro de notificaciones + reglas + evaluador |
| Sprint 11 | EP-DB-007, EP-DB-008 | US-DB-036, US-DB-037, US-DB-038, US-DB-039 | Acciones alertas + conciliacion + balance |
| Sprint 12 | EP-DB-008 | US-DB-040, US-DB-041, US-DB-042, US-DB-043, US-DB-044, US-DB-045 | Integridad + discrepancias + health + pagina consolidada |

---

## Grafo de Dependencias

```
EP-SP-003 (Ledger)
    |
    v
EP-DB-001 (Dashboard Principal) -----> EP-DB-002 (Reportes) -----> EP-DB-005 (Exportacion)
    |                                       |
    |                                       v
    +--------------------------------> EP-DB-003 (Analytics) -----> EP-DB-004 (KPIs)
    |
    |   EP-SP-029 (Notificaciones Backend)
    |       |
    v       v
EP-DB-006 (Tiempo Real) -----> EP-DB-007 (Alertas)
    |
    |   EP-SP-009 (Reconciliacion)
    |       |
    v       v
EP-DB-008 (Conciliacion y Salud Financiera)
```

### Dependencias entre User Stories (criticas)

```
US-DB-001 (scaffold) --> US-DB-002, US-DB-003, US-DB-004, US-DB-006
US-DB-005 (metricas backend) --> US-DB-002, US-DB-012, US-DB-015, US-DB-028
US-DB-007 (tabla) --> US-DB-008, US-DB-009, US-DB-010, US-DB-011, US-DB-023
US-DB-018 (catalogo) --> US-DB-019, US-DB-034
US-DB-019 (builder KPI) --> US-DB-020 --> US-DB-021, US-DB-022
US-DB-023 (exportacion) --> US-DB-024, US-DB-025, US-DB-026, US-DB-043
US-DB-028 (SSE) --> US-DB-029, US-DB-030, US-DB-031, US-DB-032, US-DB-033
US-DB-033 (notificaciones) --> US-DB-036
US-DB-034 (reglas) --> US-DB-035 --> US-DB-037
US-DB-038 (conciliacion) --> US-DB-041, US-DB-043, US-DB-044, US-DB-045
US-DB-040 (integridad) --> US-DB-041, US-DB-042, US-DB-045
```

---

## Riesgos y Mitigaciones

| # | Riesgo | Probabilidad | Impacto | Mitigacion |
|---|--------|-------------|---------|------------|
| R1 | Alto volumen de transacciones satura queries en tiempo real | Alta | Alto | Pre-calculo de metricas con Lambda + cache Redis (TTL 5 min). Nunca hacer queries de agregacion en tiempo real contra DynamoDB |
| R2 | Conexiones SSE saturan el servidor Flask (single-threaded) | Media | Alto | Usar Redis Pub/Sub para distribuir. Limitar conexiones por org. Considerar migrar SSE a servicio dedicado (Go/Node) si escala |
| R3 | Exportacion de reportes grandes (100K+ filas) falla por timeout | Media | Medio | Generacion asincrona via Lambda con timeout de 15 min. Limite maximo de 100K filas. Reportes mas grandes se fragmentan |
| R4 | Discrepancias de conciliacion por eventual consistency de DynamoDB | Baja | Alto | Usar lecturas consistentes (ConsistentRead=true) para queries de conciliacion. Retry con backoff si hay discrepancia |
| R5 | KPIs personalizados con formulas complejas consumen mucho CPU | Baja | Medio | Formulas predefinidas evaluadas en backend (no custom code). Limitar a metricas del catalogo |
| R6 | Drag-and-drop de widgets no funciona bien en tablets/touch | Media | Bajo | Testing en dispositivos touch. Angular CDK DragDrop soporta touch nativamente. Fallback: lista de widgets sin DnD |
| R7 | Reportes programados acumulan archivos en S3 incrementando costos | Media | Medio | Lifecycle policy en S3: mover a Glacier despues de 90 dias, eliminar despues de 365 dias (excepto conciliacion: 5 anos) |
| R8 | Multiples dashboards abiertos en tabs generan conexiones SSE duplicadas | Media | Bajo | SharedWorker o BroadcastChannel para compartir conexion SSE entre tabs. Misma estrategia que el estado compartido del ecosistema |
| R9 | Latencia entre evento de transaccion y actualizacion en dashboard | Baja | Medio | Arquitectura event-driven con SQS + Lambda. Latencia esperada < 5 segundos. Metricas de CloudWatch para monitorear |
| R10 | Dependencia circular entre EP-DB-007 y EP-SP-029 (alertas y notificaciones) | Media | Alto | Interfaz clara: EP-DB-007 define reglas y evalua, EP-SP-029 despacha. La integracion es via SQS (acoplamiento bajo) |

---

## Definition of Done Global

### Para cada User Story
- [ ] Codigo implementado siguiendo arquitectura hexagonal (domain, application, infrastructure, presentation)
- [ ] Tests unitarios >= 98% coverage
- [ ] Tests E2E para flujos criticos (Playwright)
- [ ] Code review aprobado (Copilot + peer)
- [ ] Ningun archivo > 1000 lineas
- [ ] Ninguna funcion > 50 lineas
- [ ] Documentacion de API actualizada (si aplica)
- [ ] Responsive design verificado (desktop + tablet + mobile)
- [ ] Multi-tenancy verificado (datos aislados por org)

### Para cada Epica
- [ ] Todas las User Stories completadas
- [ ] Integracion entre componentes verificada
- [ ] Performance verificado: endpoints < 200ms (p99)
- [ ] Accesibilidad basica (ARIA labels, keyboard navigation)
- [ ] Deploy exitoso en ambiente de staging

### Para el Producto Dashboard
- [ ] Las 8 epicas completadas y desplegadas
- [ ] Los 3 tiers funcionando correctamente con datos reales
- [ ] SSE funcionando sin degradacion por 24h continuas
- [ ] Reportes programados ejecutandose sin fallos por 7 dias consecutivos
- [ ] Conciliacion diaria ejecutandose automaticamente
- [ ] Metricas de uso del dashboard monitoreadas en Grafana
