# Legacy MiPay - Plan de Migracion (EP-LM-001 a EP-LM-008)

**Fecha**: 2026-02-16
**Product Owner**: SuperPago
**Estado**: Migracion activa
**Prioridad**: P5 (deprecating)
**Prefijo Epicas**: EP-LM
**Prefijo User Stories**: US-LM
**Deadline sugerido**: Completar antes de que SuperPago SPEI entre en produccion
**Regla critica**: No crear features nuevos en repos legacy. Solo migracion.

---

## Tabla de Contenidos

1. [Contexto y Motivacion](#contexto-y-motivacion)
2. [Inventario Legacy](#inventario-legacy)
3. [Arquitectura de Migracion](#arquitectura-de-migracion)
4. [Mapa de Epicas](#mapa-de-epicas)
5. [Epicas Detalladas](#epicas-detalladas)
6. [User Stories Detalladas](#user-stories-detalladas)
7. [Roadmap (Fases de Migracion)](#roadmap)
8. [Grafo de Dependencias](#grafo-de-dependencias)
9. [Riesgos y Mitigaciones](#riesgos-y-mitigaciones)
10. [Plan de Rollback](#plan-de-rollback)
11. [Criterios de Exito](#criterios-de-exito)

---

## Contexto y Motivacion

### Por que migrar

MiPay fue el sistema original de pagos de la plataforma, construido antes de la arquitectura SuperPago. Tiene clientes activos procesando transacciones reales. Sin embargo, mantener dos sistemas en paralelo genera:

| Problema | Impacto |
|----------|---------|
| Deuda tecnica duplicada | Cada fix debe aplicarse en legacy Y en nuevo sistema |
| Costos de infraestructura dobles | 2 sets de EC2, DynamoDB tables, API Gateway |
| Inconsistencia de datos | Usuarios y transacciones en 2 esquemas diferentes |
| Bloqueo de features nuevos | No se pueden agregar capacidades SPEI/BillPay a clientes legacy |
| Riesgo de seguridad | Codigo legacy sin actualizaciones de dependencias |
| Complejidad operativa | 2 pipelines de deploy, 2 sets de monitoreo, 2 runbooks |

### Riesgos de NO migrar

1. **Regulatorio**: Sistema legacy no cumple con nuevos requisitos de auditoria financiera
2. **Seguridad**: Dependencias desactualizadas con CVEs conocidos
3. **Negocio**: Clientes legacy no pueden acceder a SPEI, BillPay, ni agente IA
4. **Operativo**: Equipo debe mantener conocimiento de 2 arquitecturas diferentes
5. **Costo**: Infraestructura legacy cuesta ~30% del presupuesto total de infra

### Principios de migracion

1. **ZERO DOWNTIME** - Ningun cliente debe experimentar interrupcion de servicio
2. **Rollback safety** - Cada paso debe ser reversible en menos de 15 minutos
3. **Migracion incremental** - No big-bang; migrar por modulo y por cliente
4. **Validacion continua** - Shadow traffic y comparacion de respuestas en cada fase
5. **Comunicacion proactiva** - Clientes informados antes, durante y despues

---

## Inventario Legacy

### Repositorios Legacy

| Repo | Tipo | Lenguaje | Estado | Target |
|------|------|----------|--------|--------|
| `mipay_service` | Backend | Python 3.9 / Flask | Deprecating | `covacha-core` |
| `mipay_payment` | Backend | Python 3.9 / Flask | Deprecating | `covacha-payment` |
| `mipay_web` | Frontend | Angular (legacy) | Deprecating | `mf-core` |

### Endpoints Legacy - mipay_service

| Metodo | Endpoint Legacy | Descripcion | Equivalente Nuevo |
|--------|----------------|-------------|-------------------|
| POST | `/api/v1/mipay/auth/login` | Login de usuario | `/api/v1/auth/login` (Cognito) |
| POST | `/api/v1/mipay/auth/register` | Registro de usuario | `/api/v1/auth/register` (Cognito) |
| POST | `/api/v1/mipay/auth/refresh` | Refresh token | `/api/v1/auth/refresh` (Cognito) |
| GET | `/api/v1/mipay/users/me` | Perfil del usuario | `/api/v1/users/me` |
| PUT | `/api/v1/mipay/users/me` | Actualizar perfil | `/api/v1/users/me` |
| GET | `/api/v1/mipay/users/{id}` | Detalle de usuario (admin) | `/api/v1/users/{id}` |
| GET | `/api/v1/mipay/organizations` | Listar organizaciones | `/api/v1/organizations` |
| POST | `/api/v1/mipay/organizations` | Crear organizacion | `/api/v1/organizations` |
| GET | `/api/v1/mipay/organizations/{id}` | Detalle organizacion | `/api/v1/organizations/{id}` |
| GET | `/api/v1/mipay/dashboard/stats` | Metricas generales | `/api/v1/dashboard/stats` |
| GET | `/api/v1/mipay/dashboard/recent` | Actividad reciente | `/api/v1/dashboard/recent` |
| GET | `/api/v1/mipay/reports/transactions` | Reporte de transacciones | `/api/v1/reports/transactions` |
| GET | `/api/v1/mipay/reports/revenue` | Reporte de ingresos | `/api/v1/reports/revenue` |
| GET | `/api/v1/mipay/config/settings` | Configuracion global | `/api/v1/config/settings` |
| PUT | `/api/v1/mipay/config/settings` | Actualizar configuracion | `/api/v1/config/settings` |

### Endpoints Legacy - mipay_payment

| Metodo | Endpoint Legacy | Descripcion | Equivalente Nuevo |
|--------|----------------|-------------|-------------------|
| POST | `/api/v1/mipay/payments/charge` | Cobro con tarjeta (Openpay) | `/api/v1/payments/charge` |
| POST | `/api/v1/mipay/payments/transfer` | Transferencia entre cuentas | `/api/v1/payments/transfer` |
| GET | `/api/v1/mipay/payments/{id}` | Detalle de pago | `/api/v1/payments/{id}` |
| GET | `/api/v1/mipay/payments` | Listar pagos | `/api/v1/payments` |
| POST | `/api/v1/mipay/payments/refund` | Devolucion | `/api/v1/payments/refund` |
| GET | `/api/v1/mipay/payments/balance` | Consulta de saldo | `/api/v1/accounts/{id}/balance` |
| POST | `/api/v1/mipay/cards/register` | Registrar tarjeta | `/api/v1/cards/register` |
| GET | `/api/v1/mipay/cards` | Listar tarjetas | `/api/v1/cards` |
| DELETE | `/api/v1/mipay/cards/{id}` | Eliminar tarjeta | `/api/v1/cards/{id}` |
| POST | `/api/v1/mipay/webhooks/openpay` | Webhook Openpay | `/api/v1/webhooks/openpay` |
| GET | `/api/v1/mipay/transactions` | Historial transacciones | `/api/v1/transactions` |
| GET | `/api/v1/mipay/transactions/{id}` | Detalle transaccion | `/api/v1/transactions/{id}` |

### Pantallas Legacy - mipay_web

| Pantalla | Ruta Legacy | Descripcion | Target Nuevo |
|----------|-------------|-------------|--------------|
| Login | `/login` | Autenticacion | `mf-auth /login` |
| Registro | `/register` | Registro de usuario | `mf-auth /register` |
| Dashboard | `/dashboard` | Panel principal | `mf-core /dashboard` |
| Pagos | `/payments` | Lista de pagos | `mf-payment /payments` |
| Nuevo Pago | `/payments/new` | Crear cobro | `mf-payment /payments/new` |
| Tarjetas | `/cards` | Gestion de tarjetas | `mf-payment-card /cards` |
| Transacciones | `/transactions` | Historial | `mf-core /transactions` |
| Perfil | `/profile` | Datos del usuario | `mf-settings /profile` |
| Configuracion | `/settings` | Config de org | `mf-settings /settings` |
| Reportes | `/reports` | Reportes y metricas | `mf-dashboard /reports` |

### Tablas DynamoDB Legacy

| Tabla Legacy | Descripcion | PK/SK Legacy | Tabla Nueva | PK/SK Nuevo |
|-------------|-------------|--------------|-------------|-------------|
| `mipay_users` | Usuarios del sistema | `PK: USER#{email}` / `SK: PROFILE` | `covacha_users_prod` | `PK: USER#{user_id}` / `SK: PROFILE` |
| `mipay_organizations` | Organizaciones | `PK: ORG#{org_id}` / `SK: META` | `covacha_organizations_prod` | `PK: ORG#{org_id}` / `SK: META` |
| `mipay_payments` | Pagos y cobros | `PK: ORG#{org_id}` / `SK: PAY#{pay_id}` | `modspei_operations_prod` | `PK: ORG#{org_id}` / `SK: OP#{operation_id}` |
| `mipay_transactions` | Transacciones | `PK: ORG#{org_id}` / `SK: TXN#{txn_id}` | `modspei_transactions_prod` | `PK: OP#{operation_id}` / `SK: TXN#{txn_id}` |
| `mipay_cards` | Tarjetas registradas | `PK: USER#{user_id}` / `SK: CARD#{card_id}` | `covacha_cards_prod` | `PK: USER#{user_id}` / `SK: CARD#{card_id}` |
| `mipay_config` | Configuracion global | `PK: CONFIG` / `SK: GLOBAL` | `covacha_config_prod` | `PK: TENANT#{tenant_id}` / `SK: CONFIG#{key}` |
| `mipay_webhooks` | Log de webhooks | `PK: WEBHOOK#{date}` / `SK: #{timestamp}` | `covacha_webhooks_prod` | `PK: WEBHOOK#{date}` / `SK: #{event_id}` |

### Integraciones Legacy

| Integracion | Proveedor | Uso en Legacy | Target Nuevo |
|-------------|-----------|---------------|--------------|
| Cobros tarjeta | Openpay | `mipay_payment` directo | `covacha-payment` via Strategy Pattern |
| Webhooks Openpay | Openpay | `mipay_payment /webhooks/openpay` | `covacha-webhook /webhook/openpay/` |
| Autenticacion | JWT propio | `mipay_service` genera tokens | Cognito (gestionado por `covacha-core`) |
| Storage | S3 directo | Bucket `mipay-files` | Bucket `covacha-files-prod` via `covacha-core` |
| Notificaciones | Email directo (SES) | Hardcoded en `mipay_service` | `covacha-notification` via SQS |

---

## Arquitectura de Migracion

### Diagrama General

```
FASE 1-2: Inventario + Datos
===========================

  [Clientes Legacy]
        |
        v
  [mipay_service]  ------>  [mipay_users]
  [mipay_payment]  ------>  [mipay_payments]
                            [mipay_transactions]
        |                          |
        |     SCRIPTS DE           |
        |     MIGRACION            v
        |     (EP-LM-002)   [covacha_users_prod]
        |                   [modspei_operations_prod]
        +--- validacion --> [modspei_transactions_prod]


FASE 3: Proxy de Compatibilidad
================================

  [Clientes Legacy]
        |
        v
  +--[API PROXY (EP-LM-003)]--+
  |                            |
  |  /api/v1/mipay/*           |
  |     |                      |
  |     | traduce formato      |
  |     v                      |
  |  /api/v1/*                 |
  +------|---------------------+
         |
    +----+----+
    |         |
    v         v
  [covacha   [covacha
   -core]    -payment]
    |         |
    v         v
  [DynamoDB nuevas tablas]


FASE 4-6: Migracion Completa
=============================

  [Clientes Migrados]        [Clientes en Transicion]
        |                           |
        v                           v
  [app.superpago.com.mx]    [API PROXY] (se apaga gradualmente)
        |                           |
   +----+----+                 +----+----+
   |         |                 |         |
   v         v                 v         v
  [mf-core] [mf-payment]    [covacha  [covacha
   Angular   Angular          -core]   -payment]
   21        21


FASE 7-8: Cutover Final
========================

  [TODOS los Clientes]
        |
        v
  [app.superpago.com.mx]
        |
   +----+----+----+
   |    |    |    |
   v    v    v    v
  [mf  [mf  [mf  [mf
  core] pay] auth] ...]
        |
        v
  [covacha-core]
  [covacha-payment]
  [covacha-transaction]
        |
        v
  [DynamoDB - esquema nuevo unico]

  [mipay_service]     -> ARCHIVADO
  [mipay_payment]     -> ARCHIVADO
  [mipay_web]         -> ARCHIVADO
  [mipay_* tables]    -> ARCHIVADO (read-only 90 dias, luego eliminar)
```

### Estrategia: Strangler Fig Pattern

Se usa el patron **Strangler Fig** (estrangulador): el nuevo sistema crece alrededor del legacy, absorbiendo funcionalidad gradualmente hasta que el legacy se puede desconectar.

1. **Proxy**: Intercepta trafico legacy y lo redirige al nuevo sistema
2. **Dual-write**: Durante transicion, escrituras van a ambos sistemas
3. **Shadow traffic**: Requests legacy se envian tambien al nuevo sistema para comparar respuestas
4. **Feature flags**: Cada cliente se migra individualmente via feature flag
5. **Cutover**: Cuando todos los clientes estan en el nuevo sistema, se apaga el legacy

---

## Mapa de Epicas

| ID | Epica | Complejidad | Fase | Dependencias |
|----|-------|-------------|------|--------------|
| EP-LM-001 | Inventario y Mapping de Legacy | M | 1 | Ninguna |
| EP-LM-002 | Migracion de Datos (DynamoDB) | XL | 2 | EP-LM-001 |
| EP-LM-003 | Capa de Compatibilidad API (Proxy) | L | 3 | EP-LM-001 |
| EP-LM-004 | Migracion de Integracion Openpay | L | 3-4 | EP-LM-002, EP-LM-003 |
| EP-LM-005 | Migracion de Frontend (mipay_web a mf-core) | L | 4 | EP-LM-003 |
| EP-LM-006 | Migracion de Usuarios y Autenticacion | XL | 2-3 | EP-LM-001 |
| EP-LM-007 | Testing y Validacion de Paridad | L | 3-5 | EP-LM-002, EP-LM-003 |
| EP-LM-008 | Cutover y Decommission | M | 5-6 | EP-LM-001 a EP-LM-007 |

**Total**: 8 epicas, 42 user stories

---

## Epicas Detalladas

---

### EP-LM-001: Inventario y Mapping de Legacy

**Descripcion:**
Documentar exhaustivamente todos los endpoints, tablas, integraciones y features del sistema legacy. Crear un mapa 1:1 entre legacy y nuevo sistema. Identificar gaps donde el sistema nuevo no tiene equivalente. Este inventario es el fundamento de toda la migracion; sin el, se corre el riesgo de dejar funcionalidades sin migrar.

**User Stories:**
- US-LM-001, US-LM-002, US-LM-003, US-LM-004, US-LM-005

**Criterios de Aceptacion de la Epica:**
- [ ] Documento con 100% de endpoints de mipay_service catalogados
- [ ] Documento con 100% de endpoints de mipay_payment catalogados
- [ ] Mapping endpoint legacy -> endpoint nuevo para cada uno
- [ ] Lista de gaps (funcionalidad sin equivalente en el nuevo sistema)
- [ ] Plan de cierre de cada gap (implementar, deprecar, o migrar como esta)
- [ ] Catalogo de tablas DynamoDB legacy con schemas completos
- [ ] Mapping de schema legacy -> schema nuevo para cada tabla
- [ ] Inventario de integraciones externas (Openpay, S3, SES)
- [ ] Lista de clientes activos con volumen de transacciones mensual
- [ ] Aprobacion del inventario por equipo de producto

**Dependencias:** Ninguna (puede empezar de inmediato)

**Complejidad:** M (investigacion y documentacion, no codigo)

**Repositorios:** `mipay_service`, `mipay_payment`, `mipay_web` (lectura), `covacha-projects` (escritura)

---

### EP-LM-002: Migracion de Datos (DynamoDB)

**Descripcion:**
Scripts de migracion de datos desde tablas DynamoDB legacy al nuevo esquema. La migracion es incremental: se ejecuta por lotes, con validacion post-lote, y capacidad de rollback. Incluye migracion de usuarios, organizaciones, transacciones historicas, tarjetas registradas y configuraciones. Los datos deben transformarse al nuevo formato (nuevos PK/SK, campos renombrados, IDs regenerados donde aplique).

**User Stories:**
- US-LM-006, US-LM-007, US-LM-008, US-LM-009, US-LM-010, US-LM-011

**Criterios de Aceptacion de la Epica:**
- [ ] Script de migracion para cada tabla legacy (7 tablas)
- [ ] Transformacion de PK/SK al nuevo formato
- [ ] Migracion de usuarios con mapping de IDs
- [ ] Migracion de organizaciones con nueva estructura multi-tenant
- [ ] Migracion de transacciones historicas con referencia cruzada
- [ ] Migracion de tarjetas registradas (datos tokenizados, nunca PAN)
- [ ] Validacion post-migracion: count, checksums, muestreo aleatorio
- [ ] Capacidad de rollback (borrar datos migrados y re-ejecutar)
- [ ] Modo dry-run (simula sin escribir)
- [ ] Log de migracion con errores y warnings
- [ ] Migracion incremental (puede re-ejecutarse sin duplicar datos)
- [ ] Performance: migrar 100K registros en menos de 30 minutos

**Dependencias:** EP-LM-001 (necesita el mapping de schemas)

**Complejidad:** XL (7 tablas, transformacion de datos, validacion critica)

**Repositorios:** `covacha-core` (scripts en `/scripts/migration/`)

---

### EP-LM-003: Capa de Compatibilidad API (Proxy)

**Descripcion:**
API proxy que intercepta requests en formato legacy (`/api/v1/mipay/*`) y los traduce al formato del nuevo sistema (`/api/v1/*`). Esto permite que clientes legacy sigan operando sin cambios mientras se migran gradualmente. El proxy registra metricas de uso para saber que endpoints legacy siguen activos y cuando es seguro desactivarlos.

**User Stories:**
- US-LM-012, US-LM-013, US-LM-014, US-LM-015, US-LM-016

**Criterios de Aceptacion de la Epica:**
- [ ] Proxy desplegado en API Gateway como ruta `/api/v1/mipay/*`
- [ ] Traduccion de request body del formato legacy al nuevo
- [ ] Traduccion de response body del formato nuevo al legacy
- [ ] Traduccion de headers de autenticacion (JWT legacy -> Cognito token)
- [ ] Metricas por endpoint: requests/minuto, latencia, errores
- [ ] Dashboard de metricas del proxy en Grafana
- [ ] Feature flags por cliente: proxy activo/inactivo por organization_id
- [ ] Logging de requests legacy con correlation ID
- [ ] Latencia del proxy < 50ms adicionales sobre la request directa
- [ ] Rate limiting especifico para rutas proxy
- [ ] Endpoint de health check del proxy

**Dependencias:** EP-LM-001 (necesita el mapping de endpoints)

**Complejidad:** L (traduccion bidireccional, metricas, feature flags)

**Repositorios:** `covacha-core` (proxy routes)

---

### EP-LM-004: Migracion de Integracion Openpay

**Descripcion:**
Migrar la integracion con Openpay desde mipay_payment al nuevo covacha-payment usando Strategy Pattern. Incluye redireccion de webhooks, verificacion de todas las operaciones (cobros, transferencias, tokenizacion de tarjetas), y testing exhaustivo en sandbox. La integracion legacy usa llamadas directas a Openpay; la nueva usa el Strategy Pattern definido en la arquitectura SuperPago.

**User Stories:**
- US-LM-017, US-LM-018, US-LM-019, US-LM-020, US-LM-021

**Criterios de Aceptacion de la Epica:**
- [ ] `OpenpayDriver` implementa interface `PaymentProvider` en covacha-payment
- [ ] Cobro con tarjeta funcional via nuevo sistema
- [ ] Transferencia Openpay funcional via nuevo sistema
- [ ] Devolucion (refund) funcional via nuevo sistema
- [ ] Tokenizacion de tarjetas migrada
- [ ] Webhooks de Openpay redirigidos a covacha-webhook
- [ ] Webhook handler procesa eventos de Openpay correctamente
- [ ] Idempotency keys en todas las operaciones mutativas
- [ ] Configuracion de Openpay (API keys, merchant ID) en Parameter Store
- [ ] Tests en sandbox de Openpay con 100% de operaciones verificadas
- [ ] Rollback: capacidad de redirigir webhooks de vuelta a legacy en 5 minutos

**Dependencias:** EP-LM-002 (datos migrados), EP-LM-003 (proxy activo)

**Complejidad:** L (integracion financiera critica, zero-error tolerance)

**Repositorios:** `covacha-payment` (driver), `covacha-webhook` (handler)

---

### EP-LM-005: Migracion de Frontend (mipay_web a mf-core)

**Descripcion:**
Migrar las pantallas de mipay_web al ecosistema de micro-frontends. Las pantallas se re-implementan en Angular 21 con arquitectura hexagonal, componentes standalone, signals y OnPush. Las URLs legacy se redirigen a las nuevas rutas. Se comunica a los usuarios sobre el cambio de interfaz con anticipacion.

**User Stories:**
- US-LM-022, US-LM-023, US-LM-024, US-LM-025, US-LM-026

**Criterios de Aceptacion de la Epica:**
- [ ] Todas las pantallas legacy re-implementadas en micro-frontends
- [ ] Paridad funcional: cada pantalla nueva hace lo mismo que la legacy
- [ ] Redirects 301 de URLs legacy a nuevas URLs
- [ ] Responsive design en todas las pantallas migradas
- [ ] Componentes standalone, signals, OnPush change detection
- [ ] Arquitectura hexagonal (adapters, ports, domain)
- [ ] Tests >= 98% en cada micro-frontend modificado
- [ ] Pagina de transicion con FAQ para usuarios
- [ ] Email de comunicacion enviado 2 semanas antes del cambio
- [ ] Periodo de 30 dias con link "volver a la version anterior"

**Dependencias:** EP-LM-003 (APIs accesibles via proxy o directo)

**Complejidad:** L (10 pantallas a migrar, re-implementacion en Angular 21)

**Repositorios:** `mf-core`, `mf-payment`, `mf-payment-card`, `mf-auth`, `mf-settings`, `mf-dashboard`

---

### EP-LM-006: Migracion de Usuarios y Autenticacion

**Descripcion:**
Migrar todos los usuarios del sistema de autenticacion legacy (JWT propio en mipay_service) a AWS Cognito (gestionado por covacha-core). Incluye mapeo de roles legacy al nuevo RBAC, estrategia para passwords (force reset o migracion de hashes), comunicacion a usuarios, y periodo de autenticacion dual donde ambos sistemas aceptan tokens.

**User Stories:**
- US-LM-027, US-LM-028, US-LM-029, US-LM-030, US-LM-031

**Criterios de Aceptacion de la Epica:**
- [ ] Todos los usuarios legacy creados en Cognito User Pool
- [ ] Roles legacy mapeados a grupos de Cognito (RBAC nuevo)
- [ ] Estrategia de passwords definida e implementada (migration trigger en Cognito)
- [ ] Dual-auth: ambos tokens aceptados durante periodo de transicion
- [ ] Email de comunicacion a usuarios sobre cambio de login
- [ ] Pagina de migracion de cuenta con instrucciones claras
- [ ] Soporte para usuarios que no completan migracion (reminder emails)
- [ ] Audit log de migracion por usuario (estado: pending, migrated, failed)
- [ ] Metricas: % de usuarios migrados, tiempo promedio de migracion
- [ ] Rollback: reactivar auth legacy si Cognito falla
- [ ] Zero-downtime: usuario puede operar durante toda la transicion

**Dependencias:** EP-LM-001 (inventario de usuarios y roles)

**Complejidad:** XL (autenticacion critica, impacto directo en todos los usuarios)

**Repositorios:** `covacha-core` (Cognito config, auth service), `mf-auth` (pantallas)

---

### EP-LM-007: Testing y Validacion de Paridad

**Descripcion:**
Suite completa de tests que verifica que el nuevo sistema produce resultados identicos al legacy para todas las operaciones. Incluye shadow traffic (enviar requests reales a ambos sistemas y comparar respuestas), comparacion de montos y transacciones, smoke tests automatizados, y monitoreo continuo de discrepancias.

**User Stories:**
- US-LM-032, US-LM-033, US-LM-034, US-LM-035, US-LM-036, US-LM-037

**Criterios de Aceptacion de la Epica:**
- [ ] Suite de parity tests para cada endpoint migrado
- [ ] Shadow traffic runner que duplica requests al nuevo sistema
- [ ] Comparador de respuestas con tolerancia configurable
- [ ] Dashboard de discrepancias en Grafana
- [ ] Alerta automatica cuando discrepancia > 0.1% de requests
- [ ] Validacion de montos: legacy vs nuevo deben coincidir al centavo
- [ ] Smoke tests automatizados ejecutandose cada hora
- [ ] Reporte diario de paridad enviado al equipo
- [ ] Tests de carga: nuevo sistema soporta al menos 2x el trafico legacy
- [ ] Tests de failover: proxy redirige a legacy si nuevo sistema falla
- [ ] Documentacion de todas las discrepancias encontradas y resueltas

**Dependencias:** EP-LM-002 (datos migrados), EP-LM-003 (proxy activo)

**Complejidad:** L (testing exhaustivo, shadow traffic, monitoreo)

**Repositorios:** `covacha-core` (tests), `covacha-payment` (tests)

---

### EP-LM-008: Cutover y Decommission

**Descripcion:**
Plan de cutover final: apagar el sistema legacy y redirigir todo el trafico al nuevo sistema. Incluye DNS switchover, periodo de dual-running con monitoreo intensivo, decommission de repositorios legacy, archivado de datos historicos, y comunicacion final a todos los stakeholders.

**User Stories:**
- US-LM-038, US-LM-039, US-LM-040, US-LM-041, US-LM-042

**Criterios de Aceptacion de la Epica:**
- [ ] Runbook de cutover documentado paso a paso
- [ ] Ventana de cutover acordada con stakeholders (horario de menor trafico)
- [ ] DNS switchover ejecutado
- [ ] Periodo de dual-running de 72 horas con monitoreo 24/7
- [ ] Metricas de salud del nuevo sistema en verde durante 72 horas
- [ ] Zero requests al proxy legacy durante 24 horas consecutivas
- [ ] Repos legacy archivados en GitHub (read-only)
- [ ] Tablas DynamoDB legacy en modo read-only por 90 dias
- [ ] Backup final de todas las tablas legacy en S3
- [ ] Infraestructura legacy (EC2, API Gateway) decomisionada
- [ ] Comunicacion final a stakeholders: "migracion completada"
- [ ] Post-mortem documentado con lecciones aprendidas

**Dependencias:** EP-LM-001 a EP-LM-007 (todas las epicas anteriores completadas)

**Complejidad:** M (coordinacion operativa, no codigo nuevo significativo)

**Repositorios:** `covacha-projects` (documentacion), todos los repos involucrados

---

## User Stories Detalladas

---

### EP-LM-001: Inventario y Mapping de Legacy

---

#### US-LM-001: Catalogo de Endpoints de mipay_service

**ID:** US-LM-001
**Epica:** EP-LM-001
**Prioridad:** P0

**Historia:**
Como **Ingeniero de Migracion** quiero tener un catalogo completo de todos los endpoints de mipay_service para poder mapear cada uno a su equivalente en covacha-core.

**Criterios de Aceptacion:**
- [ ] Lista de todos los endpoints (metodo, ruta, descripcion)
- [ ] Request body y response body documentados para cada endpoint
- [ ] Codigos de error legacy documentados
- [ ] Autenticacion requerida por endpoint (publica, user, admin)
- [ ] Volumetria: requests/dia promedio por endpoint (ultimos 30 dias)
- [ ] Mapping a endpoint equivalente en covacha-core (o "GAP" si no existe)

**Tareas Tecnicas:**
1. Extraer rutas de Flask blueprints en mipay_service
2. Documentar schemas de request/response por endpoint
3. Consultar logs de API Gateway para volumetria
4. Crear tabla de mapping legacy -> nuevo
5. Identificar y listar gaps

**Dependencias:** Ninguna
**Estimacion:** 2 dev-days

---

#### US-LM-002: Catalogo de Endpoints de mipay_payment

**ID:** US-LM-002
**Epica:** EP-LM-001
**Prioridad:** P0

**Historia:**
Como **Ingeniero de Migracion** quiero tener un catalogo completo de todos los endpoints de mipay_payment para poder mapear cada uno a su equivalente en covacha-payment.

**Criterios de Aceptacion:**
- [ ] Lista de todos los endpoints de pago (metodo, ruta, descripcion)
- [ ] Flujos de pago documentados (cobro, transferencia, devolucion)
- [ ] Formato de webhooks recibidos de Openpay documentado
- [ ] Volumetria de transacciones: cantidad y monto promedio mensual
- [ ] Mapping a endpoint equivalente en covacha-payment (o "GAP")

**Tareas Tecnicas:**
1. Extraer rutas de Flask blueprints en mipay_payment
2. Documentar flujos de pago end-to-end
3. Exportar metricas de transacciones de los ultimos 6 meses
4. Crear tabla de mapping legacy -> nuevo

**Dependencias:** Ninguna
**Estimacion:** 2 dev-days

---

#### US-LM-003: Inventario de Tablas DynamoDB Legacy

**ID:** US-LM-003
**Epica:** EP-LM-001
**Prioridad:** P0

**Historia:**
Como **Ingeniero de Migracion** quiero un inventario completo de las tablas DynamoDB legacy con sus schemas para poder disenar los scripts de transformacion de datos.

**Criterios de Aceptacion:**
- [ ] Lista de todas las tablas DynamoDB usadas por mipay_*
- [ ] Schema de cada tabla: PK, SK, GSIs, campos, tipos de datos
- [ ] Cantidad de items en cada tabla (count actual)
- [ ] Tamano en GB de cada tabla
- [ ] Throughput actual (RCU/WCU provisioned y consumido)
- [ ] Mapping de schema legacy -> schema nuevo para cada tabla
- [ ] Documento de transformaciones necesarias (renombrar campos, cambiar PK/SK, etc.)

**Tareas Tecnicas:**
1. Describir tablas via AWS CLI (describe-table)
2. Escanear schemas con muestreo de 100 items por tabla
3. Documentar cada campo con tipo y ejemplo
4. Disenar mapping de transformacion

**Dependencias:** Ninguna
**Estimacion:** 3 dev-days

---

#### US-LM-004: Inventario de Integraciones Externas

**ID:** US-LM-004
**Epica:** EP-LM-001
**Prioridad:** P1

**Historia:**
Como **Ingeniero de Migracion** quiero un inventario de todas las integraciones externas del sistema legacy para poder planificar la migracion de cada una sin interrumpir el servicio.

**Criterios de Aceptacion:**
- [ ] Lista de integraciones: Openpay, S3, SES, servicios internos
- [ ] Credenciales requeridas por integracion (sin exponer valores, solo keys necesarias)
- [ ] URLs de webhooks registrados en servicios externos
- [ ] Volumetria de cada integracion (calls/dia)
- [ ] Plan de migracion por integracion (redirigir, re-implementar, o deprecar)

**Tareas Tecnicas:**
1. Grep en codebase legacy por URLs externas y API keys
2. Verificar webhooks registrados en panel de Openpay
3. Listar buckets S3 y politicas de acceso
4. Documentar cada integracion con plan de migracion

**Dependencias:** Ninguna
**Estimacion:** 1 dev-day

---

#### US-LM-005: Lista de Clientes Activos y Plan de Migracion por Cliente

**ID:** US-LM-005
**Epica:** EP-LM-001
**Prioridad:** P1

**Historia:**
Como **Administrador SuperPago** quiero una lista de todos los clientes activos en el sistema legacy con su volumen de transacciones para poder priorizar el orden de migracion y comunicarme con cada uno.

**Criterios de Aceptacion:**
- [ ] Lista de organizaciones activas con datos de contacto
- [ ] Volumen de transacciones mensuales por organizacion
- [ ] Monto total procesado mensual por organizacion
- [ ] Clasificacion: high-volume, medium-volume, low-volume
- [ ] Orden sugerido de migracion (empezar por low-volume para validar)
- [ ] Template de comunicacion a clientes sobre la migracion

**Tareas Tecnicas:**
1. Query a mipay_organizations con filtro status=active
2. Agregar transacciones por organizacion (ultimos 3 meses)
3. Clasificar por volumen y crear orden de prioridad
4. Redactar template de comunicacion

**Dependencias:** Ninguna
**Estimacion:** 2 dev-days

---

### EP-LM-002: Migracion de Datos (DynamoDB)

---

#### US-LM-006: Script de Migracion de Usuarios

**ID:** US-LM-006
**Epica:** EP-LM-002
**Prioridad:** P0

**Historia:**
Como **Ingeniero de Migracion** quiero un script que migre usuarios de `mipay_users` a `covacha_users_prod` para que los usuarios legacy existan en el nuevo sistema.

**Criterios de Aceptacion:**
- [ ] Script Python que lee de `mipay_users` y escribe a `covacha_users_prod`
- [ ] Transformacion de PK: `USER#{email}` -> `USER#{user_id}` (genera UUID)
- [ ] Tabla de mapping: `email -> user_id` para referencias cruzadas
- [ ] Campos legacy mapeados a campos nuevos (nombres normalizados)
- [ ] Campo `migration_source: "mipay"` en cada registro migrado
- [ ] Modo dry-run: imprime transformaciones sin escribir
- [ ] Modo incremental: solo migra usuarios no migrados previamente
- [ ] Validacion post-migracion: count legacy == count migrados
- [ ] Log de errores con detalle del registro fallido

**Tareas Tecnicas:**
1. Crear script `/scripts/migration/migrate_users.py`
2. Implementar transformacion de schema
3. Implementar modo dry-run e incremental
4. Crear tabla de mapping en DynamoDB (`mipay_migration_mapping`)
5. Tests con datos de prueba
6. Ejecutar en staging y validar

**Dependencias:** US-LM-003 (schema documentado)
**Estimacion:** 3 dev-days

---

#### US-LM-007: Script de Migracion de Organizaciones

**ID:** US-LM-007
**Epica:** EP-LM-002
**Prioridad:** P0

**Historia:**
Como **Ingeniero de Migracion** quiero un script que migre organizaciones de `mipay_organizations` a `covacha_organizations_prod` para que la estructura multi-tenant se preserve en el nuevo sistema.

**Criterios de Aceptacion:**
- [ ] Script Python que lee de `mipay_organizations` y escribe a `covacha_organizations_prod`
- [ ] Asignacion de tenant_id a cada organizacion (default: SuperPago tenant)
- [ ] Campos de configuracion legacy migrados a nueva estructura
- [ ] Relacion organizacion-usuario preservada via mapping table
- [ ] Campo `migration_source: "mipay"` en cada registro migrado
- [ ] Modo dry-run e incremental
- [ ] Validacion post-migracion: count y muestreo de campos criticos

**Tareas Tecnicas:**
1. Crear script `/scripts/migration/migrate_organizations.py`
2. Implementar transformacion de schema con tenant_id
3. Vincular con mapping de usuarios
4. Tests con datos de prueba
5. Ejecutar en staging y validar

**Dependencias:** US-LM-003, US-LM-006 (mapping de usuarios)
**Estimacion:** 2 dev-days

---

#### US-LM-008: Script de Migracion de Transacciones Historicas

**ID:** US-LM-008
**Epica:** EP-LM-002
**Prioridad:** P1

**Historia:**
Como **Cliente Legacy** quiero que mi historial completo de transacciones este disponible en el nuevo sistema para poder consultar movimientos anteriores sin perder informacion.

**Criterios de Aceptacion:**
- [ ] Script que migra `mipay_payments` y `mipay_transactions` al nuevo esquema
- [ ] Transacciones historicas mapeadas a operaciones en `modspei_operations_prod`
- [ ] Detalle de transacciones en `modspei_transactions_prod`
- [ ] Montos preservados exactamente (sin perdida de precision)
- [ ] Fechas preservadas en formato ISO 8601
- [ ] Referencias a usuario y organizacion actualizadas con nuevos IDs
- [ ] Campo `migration_source: "mipay"` y `legacy_id` para trazabilidad
- [ ] Batch processing: procesar en lotes de 25 (limite DynamoDB batch_write)
- [ ] Estimacion de tiempo basada en cantidad de registros
- [ ] Validacion: SUM(montos legacy) == SUM(montos migrados) por organizacion

**Tareas Tecnicas:**
1. Crear script `/scripts/migration/migrate_transactions.py`
2. Implementar transformacion de payments -> operations
3. Implementar transformacion de transactions -> transactions
4. Batch write con reintentos exponenciales
5. Validacion de checksums por organizacion
6. Tests con datos de prueba (1000+ registros)

**Dependencias:** US-LM-006, US-LM-007 (mapping de usuarios y orgs)
**Estimacion:** 5 dev-days

---

#### US-LM-009: Script de Migracion de Tarjetas Tokenizadas

**ID:** US-LM-009
**Epica:** EP-LM-002
**Prioridad:** P1

**Historia:**
Como **Cliente Legacy** quiero que mis tarjetas registradas esten disponibles en el nuevo sistema para no tener que volver a registrarlas.

**Criterios de Aceptacion:**
- [ ] Script que migra `mipay_cards` a `covacha_cards_prod`
- [ ] Solo se migran tokens de Openpay (NUNCA datos de tarjeta en claro)
- [ ] Token de Openpay preservado (funciona en ambos sistemas)
- [ ] Ultimos 4 digitos y tipo de tarjeta preservados
- [ ] Referencia a usuario actualizada con nuevo user_id
- [ ] Validacion: count de tarjetas por usuario coincide pre/post migracion
- [ ] Log que confirma que NINGUN PAN, CVV o fecha de expiracion fue procesado

**Tareas Tecnicas:**
1. Crear script `/scripts/migration/migrate_cards.py`
2. Verificar que solo se leen campos tokenizados
3. Transformar schema con nuevo user_id
4. Validar con query a Openpay sandbox que tokens siguen activos
5. Audit log de seguridad

**Dependencias:** US-LM-006 (mapping de usuarios)
**Estimacion:** 2 dev-days

---

#### US-LM-010: Script de Migracion de Configuraciones

**ID:** US-LM-010
**Epica:** EP-LM-002
**Prioridad:** P2

**Historia:**
Como **Administrador SuperPago** quiero que las configuraciones de cada organizacion se migren al nuevo sistema para que los clientes no tengan que re-configurar sus preferencias.

**Criterios de Aceptacion:**
- [ ] Script que migra `mipay_config` a `covacha_config_prod`
- [ ] Configuraciones globales mapeadas a configuraciones por tenant
- [ ] Configuraciones por organizacion preservadas
- [ ] Valores default aplicados para campos nuevos que no existian en legacy
- [ ] Modo dry-run para revision antes de ejecutar

**Tareas Tecnicas:**
1. Crear script `/scripts/migration/migrate_config.py`
2. Mapear config global a tenant config
3. Aplicar defaults para campos nuevos
4. Validar integridad post-migracion

**Dependencias:** US-LM-007 (organizaciones migradas)
**Estimacion:** 1 dev-day

---

#### US-LM-011: Framework de Validacion Post-Migracion

**ID:** US-LM-011
**Epica:** EP-LM-002
**Prioridad:** P0

**Historia:**
Como **Ingeniero de Migracion** quiero un framework de validacion que verifique la integridad de todos los datos migrados para tener confianza de que la migracion fue exitosa.

**Criterios de Aceptacion:**
- [ ] Script de validacion que compara counts entre tablas legacy y nuevas
- [ ] Checksum de montos totales por organizacion (debe coincidir al centavo)
- [ ] Muestreo aleatorio: toma N registros legacy y verifica su equivalente migrado
- [ ] Reporte HTML/JSON con resultados de validacion
- [ ] Categorias de resultado: PASS, WARNING, FAIL
- [ ] Si FAIL: lista detallada de registros con discrepancias
- [ ] Ejecutable como CI job (exit code 0 = pass, 1 = fail)

**Tareas Tecnicas:**
1. Crear script `/scripts/migration/validate_migration.py`
2. Implementar comparador de counts
3. Implementar checksum de montos
4. Implementar muestreo aleatorio con comparacion campo a campo
5. Generar reporte en JSON
6. Tests del framework de validacion

**Dependencias:** US-LM-006 a US-LM-010 (scripts de migracion)
**Estimacion:** 3 dev-days

---

### EP-LM-003: Capa de Compatibilidad API (Proxy)

---

#### US-LM-012: Proxy de Traduccion de Requests Legacy

**ID:** US-LM-012
**Epica:** EP-LM-003
**Prioridad:** P0

**Historia:**
Como **Sistema Legacy** quiero que mis requests a `/api/v1/mipay/*` se traduzcan y ejecuten en el nuevo sistema para que los clientes no migrados sigan operando sin cambios.

**Criterios de Aceptacion:**
- [ ] Blueprint Flask en covacha-core que captura rutas `/api/v1/mipay/*`
- [ ] Traduccion de URL: `/api/v1/mipay/payments/charge` -> servicio interno de cobro
- [ ] Traduccion de request body: campos legacy renombrados al formato nuevo
- [ ] Traduccion de response body: campos nuevos renombrados al formato legacy
- [ ] Error codes legacy preservados en las respuestas
- [ ] Correlation ID propagado entre proxy y servicio destino
- [ ] Tests para cada ruta del proxy

**Tareas Tecnicas:**
1. Crear blueprint `legacy_proxy_bp` en covacha-core
2. Implementar route handlers para cada endpoint legacy
3. Crear funciones de traduccion request/response
4. Mapear error codes legacy -> nuevo -> legacy
5. Tests unitarios para cada traduccion

**Dependencias:** US-LM-001, US-LM-002 (catalogo de endpoints)
**Estimacion:** 5 dev-days

---

#### US-LM-013: Traduccion de Autenticacion en Proxy

**ID:** US-LM-013
**Epica:** EP-LM-003
**Prioridad:** P0

**Historia:**
Como **Sistema Legacy** quiero que mis tokens JWT legacy sean aceptados por el proxy y traducidos a tokens Cognito para poder autenticar requests sin forzar migracion de auth.

**Criterios de Aceptacion:**
- [ ] Proxy acepta JWT legacy en header `Authorization`
- [ ] Valida JWT legacy con clave del sistema anterior
- [ ] Extrae user_id del JWT legacy
- [ ] Busca mapping legacy_user_id -> cognito_user_id
- [ ] Genera o recupera token Cognito temporal para el request interno
- [ ] Si el usuario ya migro a Cognito, acepta token Cognito directamente
- [ ] Dual-auth: ambos tipos de token funcionan durante la transicion

**Tareas Tecnicas:**
1. Implementar middleware de dual-auth en proxy blueprint
2. Crear servicio de traduccion de tokens
3. Cache de tokens traducidos (TTL 5 minutos)
4. Tests con JWT legacy y Cognito tokens

**Dependencias:** US-LM-006 (mapping de usuarios)
**Estimacion:** 3 dev-days

---

#### US-LM-014: Metricas de Uso del Proxy

**ID:** US-LM-014
**Epica:** EP-LM-003
**Prioridad:** P1

**Historia:**
Como **Administrador SuperPago** quiero ver metricas de uso del proxy legacy para saber cuantos clientes siguen usando endpoints legacy y cuando es seguro desactivar el proxy.

**Criterios de Aceptacion:**
- [ ] Metricas por endpoint: requests/minuto, latencia p50/p95/p99, tasa de error
- [ ] Metricas por organizacion: que clientes usan el proxy
- [ ] Dashboard en Grafana con paneles por endpoint y por cliente
- [ ] Alerta cuando un endpoint no recibe trafico por 7 dias (candidato a deprecar)
- [ ] Reporte semanal automatico con tendencias de uso

**Tareas Tecnicas:**
1. Instrumentar proxy con CloudWatch custom metrics
2. Crear dashboard en Grafana
3. Configurar alertas de inactividad
4. Script de reporte semanal

**Dependencias:** US-LM-012 (proxy funcional)
**Estimacion:** 2 dev-days

---

#### US-LM-015: Feature Flags por Cliente en Proxy

**ID:** US-LM-015
**Epica:** EP-LM-003
**Prioridad:** P1

**Historia:**
Como **Administrador SuperPago** quiero poder activar/desactivar el proxy por organizacion para migrar clientes de forma gradual y controlada.

**Criterios de Aceptacion:**
- [ ] Tabla de feature flags: `organization_id -> proxy_enabled (boolean)`
- [ ] Si proxy_enabled=true, requests se traducen y pasan al nuevo sistema
- [ ] Si proxy_enabled=false, requests retornan 410 Gone con mensaje de migracion
- [ ] API para cambiar el flag: `PUT /api/v1/admin/migration/flags/{org_id}`
- [ ] Cambio de flag en tiempo real (sin redeploy)
- [ ] Log de cada cambio de flag con timestamp y quien lo cambio

**Tareas Tecnicas:**
1. Crear tabla de flags en DynamoDB
2. Implementar middleware de feature flag en proxy
3. Crear endpoint admin para gestionar flags
4. Cache de flags con TTL 60 segundos
5. Tests de cambio de flag en caliente

**Dependencias:** US-LM-012 (proxy funcional)
**Estimacion:** 2 dev-days

---

#### US-LM-016: Rate Limiting y Logging del Proxy

**ID:** US-LM-016
**Epica:** EP-LM-003
**Prioridad:** P2

**Historia:**
Como **Ingeniero de Migracion** quiero rate limiting y logging detallado en el proxy para proteger el nuevo sistema de abuso y poder debuggear problemas de traduccion.

**Criterios de Aceptacion:**
- [ ] Rate limit por organizacion: 100 requests/minuto (configurable)
- [ ] Rate limit global del proxy: 1000 requests/minuto
- [ ] Response 429 cuando se excede el limite
- [ ] Log de cada request: timestamp, org_id, endpoint legacy, endpoint nuevo, status, latencia
- [ ] Logs en formato JSON estructurado para busqueda en CloudWatch
- [ ] Retencion de logs: 90 dias

**Tareas Tecnicas:**
1. Implementar rate limiter con DynamoDB o Redis
2. Configurar logging JSON estructurado
3. Configurar retencion en CloudWatch
4. Tests de rate limiting

**Dependencias:** US-LM-012 (proxy funcional)
**Estimacion:** 2 dev-days

---

### EP-LM-004: Migracion de Integracion Openpay

---

#### US-LM-017: OpenpayDriver con Strategy Pattern

**ID:** US-LM-017
**Epica:** EP-LM-004
**Prioridad:** P0

**Historia:**
Como **Sistema Nuevo** quiero un driver de Openpay que implemente la interface `PaymentProvider` para procesar pagos con tarjeta de credito/debito via el Strategy Pattern de covacha-payment.

**Criterios de Aceptacion:**
- [ ] Clase `OpenpayDriver` implementa interface `PaymentProvider`
- [ ] Metodos: `charge()`, `refund()`, `get_payment()`, `list_payments()`
- [ ] Configuracion via Parameter Store (API key, merchant ID, sandbox mode)
- [ ] Idempotency key en cada operacion mutativa
- [ ] Manejo de errores con retry (max 3 intentos, backoff exponencial)
- [ ] Logging estructurado de cada operacion
- [ ] Tests con mocks de API Openpay >= 98% coverage

**Tareas Tecnicas:**
1. Crear `src/drivers/openpay/openpay_driver.py` en covacha-payment
2. Implementar interface PaymentProvider
3. Implementar retry con backoff
4. Configurar credenciales via Parameter Store
5. Tests unitarios con mocks

**Dependencias:** Ninguna (puede iniciar cuando el codigo de strategy pattern exista)
**Estimacion:** 4 dev-days

---

#### US-LM-018: Migracion de Webhooks de Openpay

**ID:** US-LM-018
**Epica:** EP-LM-004
**Prioridad:** P0

**Historia:**
Como **Ingeniero de Migracion** quiero redirigir los webhooks de Openpay al nuevo handler en covacha-webhook para que las confirmaciones de pago se procesen en el nuevo sistema.

**Criterios de Aceptacion:**
- [ ] Handler en covacha-webhook para eventos de Openpay (`/webhook/openpay/`)
- [ ] Validacion de firma/token del webhook de Openpay
- [ ] Procesamiento idempotente de eventos (mismo evento 2 veces = 1 operacion)
- [ ] Eventos soportados: charge.completed, charge.failed, refund.completed
- [ ] Actualizacion de estado de operacion en `modspei_operations_prod`
- [ ] Redireccion de URL en panel de Openpay: legacy -> nuevo
- [ ] Plan de rollback: volver a URL legacy en menos de 5 minutos
- [ ] Response 200 en menos de 500ms, procesamiento async via SQS

**Tareas Tecnicas:**
1. Crear handler en covacha-webhook
2. Implementar validacion de firma Openpay
3. Implementar procesamiento idempotente
4. Actualizar URL en panel de Openpay (staging primero)
5. Tests de integracion con payloads reales de Openpay

**Dependencias:** US-LM-017 (driver funcional)
**Estimacion:** 3 dev-days

---

#### US-LM-019: Migracion de Tokenizacion de Tarjetas

**ID:** US-LM-019
**Epica:** EP-LM-004
**Prioridad:** P1

**Historia:**
Como **Cliente Legacy** quiero que mis tarjetas tokenizadas sigan funcionando en el nuevo sistema para poder hacer pagos sin re-registrar tarjetas.

**Criterios de Aceptacion:**
- [ ] Tokens de Openpay migrados funcionan para nuevos cobros
- [ ] Endpoint de registro de nuevas tarjetas usa covacha-payment (no legacy)
- [ ] Endpoint de listado de tarjetas lee de tabla nueva
- [ ] Endpoint de eliminacion de tarjeta elimina en nuevo sistema Y en Openpay
- [ ] Verificacion: cobro de prueba con token migrado en sandbox de Openpay

**Tareas Tecnicas:**
1. Verificar que tokens de Openpay son reutilizables entre sistemas
2. Implementar CRUD de tarjetas en covacha-payment
3. Test de cobro con token migrado en sandbox
4. Documentar limitaciones si las hay

**Dependencias:** US-LM-009 (tarjetas migradas), US-LM-017 (driver Openpay)
**Estimacion:** 2 dev-days

---

#### US-LM-020: Testing de Operaciones Openpay en Sandbox

**ID:** US-LM-020
**Epica:** EP-LM-004
**Prioridad:** P0

**Historia:**
Como **Ingeniero de Migracion** quiero ejecutar todas las operaciones de Openpay en sandbox a traves del nuevo sistema para verificar paridad funcional antes de migrar trafico real.

**Criterios de Aceptacion:**
- [ ] Cobro con tarjeta exitoso en sandbox
- [ ] Cobro con tarjeta rechazado (fondos insuficientes) maneja error correctamente
- [ ] Devolucion total exitosa en sandbox
- [ ] Devolucion parcial exitosa en sandbox
- [ ] Webhook de cobro exitoso procesado correctamente
- [ ] Webhook de cobro fallido procesado correctamente
- [ ] Webhook de devolucion procesado correctamente
- [ ] Comparacion de respuestas: nuevo sistema vs legacy (mismos campos, mismos valores)

**Tareas Tecnicas:**
1. Configurar credenciales sandbox en Parameter Store (staging)
2. Crear test suite de integracion con sandbox Openpay
3. Ejecutar cada operacion y comparar con legacy
4. Documentar diferencias encontradas
5. Aprobar con equipo de producto

**Dependencias:** US-LM-017, US-LM-018 (driver y webhook handler)
**Estimacion:** 3 dev-days

---

#### US-LM-021: Switchover de Openpay a Produccion

**ID:** US-LM-021
**Epica:** EP-LM-004
**Prioridad:** P0

**Historia:**
Como **Administrador SuperPago** quiero ejecutar el switchover de Openpay de legacy a nuevo sistema en produccion de forma controlada y reversible.

**Criterios de Aceptacion:**
- [ ] Checklist pre-switchover verificado (tests sandbox pasan, metricas ok)
- [ ] Webhook URL actualizada en panel de Openpay produccion
- [ ] Primer cobro real procesado por nuevo sistema exitosamente
- [ ] Monitoreo intensivo durante primeras 2 horas post-switchover
- [ ] Metricas de cobros: tasa de exito >= tasa legacy (baseline de ultimos 30 dias)
- [ ] Plan de rollback probado: volver a legacy en menos de 5 minutos
- [ ] Comunicacion al equipo de soporte sobre el cambio

**Tareas Tecnicas:**
1. Ejecutar checklist pre-switchover
2. Actualizar webhook URL en Openpay produccion
3. Monitorear primeros cobros en Grafana
4. Comparar tasa de exito con baseline
5. Documentar resultado del switchover

**Dependencias:** US-LM-020 (tests sandbox exitosos)
**Estimacion:** 1 dev-day (ejecucion) + 1 dev-day (monitoreo)

---

### EP-LM-005: Migracion de Frontend (mipay_web a mf-core)

---

#### US-LM-022: Mapping de Pantallas Legacy a Micro-Frontends

**ID:** US-LM-022
**Epica:** EP-LM-005
**Prioridad:** P0

**Historia:**
Como **Ingeniero de Migracion** quiero un mapping completo de pantallas legacy a micro-frontends para saber donde re-implementar cada funcionalidad.

**Criterios de Aceptacion:**
- [ ] Lista de todas las pantallas de mipay_web con capturas de pantalla
- [ ] Mapping: pantalla legacy -> micro-frontend destino (mf-core, mf-payment, etc.)
- [ ] Lista de componentes por pantalla (formularios, tablas, graficas)
- [ ] Identificacion de features legacy que NO se migraran (deprecated)
- [ ] Prioridad de migracion por pantalla (P0-P3)

**Tareas Tecnicas:**
1. Navegar mipay_web y documentar cada pantalla
2. Capturar screenshots de cada vista
3. Crear mapping a micro-frontends
4. Clasificar por prioridad con equipo de producto

**Dependencias:** Ninguna
**Estimacion:** 1 dev-day

---

#### US-LM-023: Re-implementacion de Pantallas de Pago en mf-payment

**ID:** US-LM-023
**Epica:** EP-LM-005
**Prioridad:** P0

**Historia:**
Como **Cliente Legacy** quiero que las pantallas de pagos, cobros y tarjetas esten disponibles en el nuevo sistema con la misma funcionalidad para poder operar sin interrupcion.

**Criterios de Aceptacion:**
- [ ] Lista de pagos con filtros y paginacion en mf-payment
- [ ] Formulario de nuevo cobro en mf-payment
- [ ] Detalle de pago con estado y timeline en mf-payment
- [ ] Gestion de tarjetas (lista, agregar, eliminar) en mf-payment-card
- [ ] Paridad funcional con pantallas legacy verificada
- [ ] Componentes standalone con signals y OnPush
- [ ] Tests >= 98%

**Tareas Tecnicas:**
1. Implementar componente de lista de pagos
2. Implementar formulario de nuevo cobro
3. Implementar vista de detalle de pago
4. Implementar CRUD de tarjetas
5. Tests unitarios y de integracion

**Dependencias:** US-LM-022 (mapping), EP-LM-003 (APIs accesibles)
**Estimacion:** 5 dev-days

---

#### US-LM-024: Re-implementacion de Dashboard y Reportes

**ID:** US-LM-024
**Epica:** EP-LM-005
**Prioridad:** P1

**Historia:**
Como **Administrador SuperPago** quiero que el dashboard y los reportes del sistema legacy esten disponibles en el nuevo sistema para poder monitorear operaciones.

**Criterios de Aceptacion:**
- [ ] Dashboard con metricas principales en mf-dashboard
- [ ] Reporte de transacciones con filtros y export en mf-dashboard
- [ ] Reporte de ingresos por periodo en mf-dashboard
- [ ] Actividad reciente en mf-core
- [ ] Datos historicos migrados visibles en los reportes
- [ ] Tests >= 98%

**Tareas Tecnicas:**
1. Implementar componentes de dashboard
2. Implementar reportes con export CSV
3. Verificar que datos migrados se muestran correctamente
4. Tests unitarios

**Dependencias:** US-LM-008 (transacciones historicas migradas)
**Estimacion:** 4 dev-days

---

#### US-LM-025: Redirects de URLs Legacy

**ID:** US-LM-025
**Epica:** EP-LM-005
**Prioridad:** P1

**Historia:**
Como **Cliente Legacy** quiero que las URLs que tengo guardadas (bookmarks, links en emails) me redirijan a la nueva interfaz para no perder acceso a funcionalidades.

**Criterios de Aceptacion:**
- [ ] Redirect 301 de cada ruta legacy a su equivalente nueva
- [ ] `/login` -> `app.superpago.com.mx/auth/login`
- [ ] `/dashboard` -> `app.superpago.com.mx/dashboard`
- [ ] `/payments` -> `app.superpago.com.mx/payment/payments`
- [ ] `/transactions` -> `app.superpago.com.mx/transactions`
- [ ] `/settings` -> `app.superpago.com.mx/settings`
- [ ] Redirects configurados en CloudFront (no en aplicacion)
- [ ] Redirects activos por al menos 12 meses post-migracion

**Tareas Tecnicas:**
1. Configurar redirects en CloudFront distribution de mipay_web
2. Crear mapping de rutas legacy -> nuevas
3. Tests de cada redirect
4. Documentar para equipo de soporte

**Dependencias:** US-LM-023, US-LM-024 (pantallas nuevas disponibles)
**Estimacion:** 1 dev-day

---

#### US-LM-026: Pagina de Transicion y Comunicacion a Usuarios

**ID:** US-LM-026
**Epica:** EP-LM-005
**Prioridad:** P1

**Historia:**
Como **Cliente Legacy** quiero recibir comunicacion clara sobre el cambio de interfaz y tener una pagina de ayuda para poder adaptarme al nuevo sistema sin confusion.

**Criterios de Aceptacion:**
- [ ] Email de comunicacion enviado 2 semanas antes del cambio de interfaz
- [ ] Pagina de transicion con: que cambia, que no cambia, FAQ, soporte
- [ ] Guia visual: "antes vs despues" para cada pantalla principal
- [ ] Link "Necesitas ayuda?" visible en todas las pantallas nuevas (30 dias)
- [ ] Canal de soporte dedicado para preguntas de migracion
- [ ] Segundo email recordatorio 3 dias antes del cambio

**Tareas Tecnicas:**
1. Disenar y construir pagina de transicion
2. Redactar emails de comunicacion
3. Crear guia visual antes/despues
4. Configurar canal de soporte
5. Programar envio de emails

**Dependencias:** US-LM-023 (pantallas nuevas listas para mostrar)
**Estimacion:** 3 dev-days

---

### EP-LM-006: Migracion de Usuarios y Autenticacion

---

#### US-LM-027: Crear Usuarios Legacy en Cognito

**ID:** US-LM-027
**Epica:** EP-LM-006
**Prioridad:** P0

**Historia:**
Como **Ingeniero de Migracion** quiero crear todos los usuarios legacy en Cognito User Pool para que puedan autenticarse en el nuevo sistema.

**Criterios de Aceptacion:**
- [ ] Script que crea usuarios en Cognito a partir de datos migrados
- [ ] Email verificado marcado como `email_verified: true` (ya validado en legacy)
- [ ] Atributos custom: `custom:legacy_id`, `custom:migration_date`
- [ ] Usuario creado con status `FORCE_CHANGE_PASSWORD` o migration trigger
- [ ] Batch creation: procesar 50 usuarios por minuto (rate limit Cognito)
- [ ] Log de creacion: exito, error, ya existente
- [ ] Rollback: script para eliminar usuarios creados si algo falla

**Tareas Tecnicas:**
1. Crear script `/scripts/migration/create_cognito_users.py`
2. Implementar batch creation con rate limiting
3. Configurar custom attributes en Cognito
4. Implementar rollback
5. Tests en User Pool de staging

**Dependencias:** US-LM-006 (usuarios migrados en DynamoDB)
**Estimacion:** 3 dev-days

---

#### US-LM-028: Mapping de Roles Legacy a RBAC Cognito

**ID:** US-LM-028
**Epica:** EP-LM-006
**Prioridad:** P0

**Historia:**
Como **Administrador SuperPago** quiero que los roles y permisos del sistema legacy se mapeen correctamente al RBAC de Cognito para que los usuarios mantengan su nivel de acceso.

**Criterios de Aceptacion:**
- [ ] Tabla de mapping: rol legacy -> grupo Cognito
- [ ] Roles legacy documentados: admin, manager, operator, viewer
- [ ] Grupos Cognito correspondientes creados
- [ ] Cada usuario asignado al grupo correcto segun su rol legacy
- [ ] Permisos del nuevo sistema cubren todas las acciones del rol legacy
- [ ] Validacion: usuario con rol X en legacy puede hacer lo mismo en nuevo sistema

**Tareas Tecnicas:**
1. Documentar roles legacy con permisos detallados
2. Crear grupos en Cognito User Pool
3. Crear mapping table roles -> grupos
4. Script para asignar usuarios a grupos
5. Tests de permisos por rol

**Dependencias:** US-LM-027 (usuarios en Cognito)
**Estimacion:** 2 dev-days

---

#### US-LM-029: Estrategia de Migracion de Passwords

**ID:** US-LM-029
**Epica:** EP-LM-006
**Prioridad:** P0

**Historia:**
Como **Ingeniero de Migracion** quiero una estrategia para manejar los passwords de usuarios legacy de forma que la transicion sea lo mas transparente posible.

**Criterios de Aceptacion:**
- [ ] Opcion A evaluada: Cognito User Migration Lambda Trigger
  - Al primer login, Lambda valida contra sistema legacy
  - Si valido, Cognito almacena el password y el usuario queda migrado
  - Transparente para el usuario (no se entera del cambio)
- [ ] Opcion B evaluada: Force password reset para todos
  - Email con link de "Establece tu nueva contrasena"
  - Mas seguro pero peor experiencia de usuario
- [ ] Decision documentada con justificacion
- [ ] Implementacion de la opcion elegida
- [ ] Flujo de fallback si el usuario no puede migrar su password
- [ ] Metricas: % de usuarios que completan migracion de password

**Tareas Tecnicas:**
1. Investigar Cognito User Migration Lambda Trigger
2. Prototipar ambas opciones en staging
3. Decidir con equipo de producto
4. Implementar opcion elegida
5. Tests end-to-end del flujo de migracion

**Dependencias:** US-LM-027 (usuarios en Cognito)
**Estimacion:** 4 dev-days

---

#### US-LM-030: Periodo de Autenticacion Dual

**ID:** US-LM-030
**Epica:** EP-LM-006
**Prioridad:** P0

**Historia:**
Como **Cliente Legacy** quiero poder autenticarme con mi token JWT actual o con Cognito durante el periodo de transicion para no quedarme sin acceso en ningun momento.

**Criterios de Aceptacion:**
- [ ] Middleware de dual-auth en covacha-core
- [ ] Acepta JWT legacy en header `Authorization: Bearer <legacy_jwt>`
- [ ] Acepta Cognito token en header `Authorization: Bearer <cognito_token>`
- [ ] Identifica tipo de token automaticamente (por estructura/issuer)
- [ ] Ambos tokens resuelven al mismo user_id interno
- [ ] Periodo de dual-auth configurable (default: 90 dias)
- [ ] Alerta cuando se acerca el fin del periodo dual
- [ ] Despues del periodo: solo Cognito tokens aceptados

**Tareas Tecnicas:**
1. Implementar middleware de deteccion de tipo de token
2. Implementar validador de JWT legacy
3. Implementar validador de Cognito token
4. Resolver ambos al user_id unificado
5. Configurar periodo dual via feature flag
6. Tests con ambos tipos de token

**Dependencias:** US-LM-027 (usuarios en Cognito), US-LM-013 (traduccion auth en proxy)
**Estimacion:** 3 dev-days

---

#### US-LM-031: Comunicacion y Soporte de Migracion de Auth

**ID:** US-LM-031
**Epica:** EP-LM-006
**Prioridad:** P1

**Historia:**
Como **Cliente Legacy** quiero recibir instrucciones claras sobre como migrar mi autenticacion y tener soporte si encuentro problemas para no perder acceso a mi cuenta.

**Criterios de Aceptacion:**
- [ ] Email de comunicacion explicando el cambio de autenticacion
- [ ] Pagina de ayuda con instrucciones paso a paso
- [ ] FAQ: "Mi password no funciona", "No recibo el email", etc.
- [ ] Canal de soporte dedicado (email o WhatsApp)
- [ ] Reminder emails automaticos para usuarios que no han migrado (cada 7 dias)
- [ ] Dashboard interno: % de usuarios migrados por organizacion
- [ ] Escalation plan si > 10% de usuarios no migran en 30 dias

**Tareas Tecnicas:**
1. Redactar comunicaciones
2. Construir pagina de ayuda
3. Configurar reminder emails automaticos
4. Crear dashboard de monitoreo de migracion
5. Definir escalation plan

**Dependencias:** US-LM-029 (estrategia de passwords definida)
**Estimacion:** 3 dev-days

---

### EP-LM-007: Testing y Validacion de Paridad

---

#### US-LM-032: Suite de Parity Tests por Endpoint

**ID:** US-LM-032
**Epica:** EP-LM-007
**Prioridad:** P0

**Historia:**
Como **Ingeniero de Migracion** quiero una suite de tests que envie el mismo request al sistema legacy y al nuevo y compare las respuestas para verificar paridad funcional.

**Criterios de Aceptacion:**
- [ ] Test para cada endpoint migrado (minimo 27 endpoints)
- [ ] Cada test envia request identico a legacy y nuevo
- [ ] Comparacion de: status code, estructura de response, valores de campos criticos
- [ ] Tolerancia configurable (ignorar campos como timestamps, ids generados)
- [ ] Reporte de discrepancias con detalle del campo diferente
- [ ] Ejecutable como pytest suite: `pytest tests/parity/ -v`

**Tareas Tecnicas:**
1. Crear directorio `tests/parity/` en covacha-core
2. Implementar base class `ParityTest` con logica de comparacion
3. Crear test por endpoint
4. Configurar tolerancias
5. Generar reporte de discrepancias

**Dependencias:** EP-LM-002 (datos migrados), EP-LM-003 (proxy activo)
**Estimacion:** 5 dev-days

---

#### US-LM-033: Shadow Traffic Runner

**ID:** US-LM-033
**Epica:** EP-LM-007
**Prioridad:** P0

**Historia:**
Como **Ingeniero de Migracion** quiero duplicar trafico real del sistema legacy al nuevo sistema (sin afectar al usuario) para validar paridad con datos y patrones de uso reales.

**Criterios de Aceptacion:**
- [ ] Componente que intercepta requests al sistema legacy
- [ ] Copia del request se envia al nuevo sistema de forma asincrona
- [ ] Response del nuevo sistema se registra pero NO se envia al cliente
- [ ] Comparacion automatica: response legacy vs response nuevo
- [ ] Discrepancias se registran en tabla de discrepancias
- [ ] Impacto en latencia del sistema legacy < 5ms
- [ ] Activable/desactivable via feature flag
- [ ] Sampling rate configurable (ej: 10% del trafico)

**Tareas Tecnicas:**
1. Implementar interceptor de requests en API Gateway (Lambda@Edge o similar)
2. Envio asincrono via SQS al nuevo sistema
3. Worker que compara respuestas y registra discrepancias
4. Feature flag y sampling rate
5. Tests del runner

**Dependencias:** US-LM-012 (proxy funcional)
**Estimacion:** 5 dev-days

---

#### US-LM-034: Dashboard de Discrepancias

**ID:** US-LM-034
**Epica:** EP-LM-007
**Prioridad:** P1

**Historia:**
Como **Administrador SuperPago** quiero un dashboard que muestre discrepancias entre el sistema legacy y el nuevo en tiempo real para poder tomar decisiones de migracion informadas.

**Criterios de Aceptacion:**
- [ ] Dashboard en Grafana con paneles:
  - Total de requests comparados
  - % de paridad (requests identicos / total)
  - Top 10 endpoints con mas discrepancias
  - Tendencia de discrepancias en el tiempo
  - Detalle de ultimas discrepancias
- [ ] Alerta cuando % de paridad < 99.9%
- [ ] Drill-down por endpoint y por organizacion

**Tareas Tecnicas:**
1. Crear metricas en CloudWatch para discrepancias
2. Crear dashboard en Grafana
3. Configurar alertas
4. Documentar interpretacion de metricas

**Dependencias:** US-LM-033 (shadow traffic generando datos)
**Estimacion:** 2 dev-days

---

#### US-LM-035: Validacion de Montos y Transacciones

**ID:** US-LM-035
**Epica:** EP-LM-007
**Prioridad:** P0

**Historia:**
Como **Administrador SuperPago** quiero una validacion especifica de que todos los montos y transacciones son identicos entre legacy y nuevo sistema para tener certeza de integridad financiera.

**Criterios de Aceptacion:**
- [ ] Script que compara SUM de montos por organizacion (legacy vs nuevo)
- [ ] Tolerancia: $0.00 MXN (debe ser exacto al centavo)
- [ ] Comparacion de COUNT de transacciones por estado por organizacion
- [ ] Comparacion de saldos de cuentas (legacy vs nuevo)
- [ ] Reporte de reconciliacion con resultado PASS/FAIL por organizacion
- [ ] Si FAIL: lista de transacciones con discrepancia y monto de diferencia

**Tareas Tecnicas:**
1. Crear script `/scripts/migration/validate_financial_parity.py`
2. Implementar comparacion de sumas por organizacion
3. Implementar comparacion de counts por estado
4. Generar reporte de reconciliacion
5. Tests del validador

**Dependencias:** US-LM-008 (transacciones migradas)
**Estimacion:** 3 dev-days

---

#### US-LM-036: Smoke Tests Automatizados Post-Migracion

**ID:** US-LM-036
**Epica:** EP-LM-007
**Prioridad:** P1

**Historia:**
Como **Ingeniero de Migracion** quiero smoke tests que se ejecuten automaticamente cada hora para detectar regresiones rapidamente despues de cada fase de migracion.

**Criterios de Aceptacion:**
- [ ] Suite de smoke tests que validan operaciones criticas:
  - Login con usuario migrado
  - Consulta de saldo
  - Lista de transacciones
  - Cobro con tarjeta (sandbox)
  - Consulta de tarjetas registradas
- [ ] Ejecucion automatica cada hora via cron/CloudWatch Events
- [ ] Alerta inmediata si algun smoke test falla
- [ ] Resultado publicado en canal de Slack/Teams del equipo
- [ ] Historico de resultados para ver tendencia

**Tareas Tecnicas:**
1. Crear suite de smoke tests en `tests/smoke/`
2. Configurar ejecucion periodica via CloudWatch Events + Lambda
3. Configurar alertas en SNS
4. Publicar resultados en canal de comunicacion

**Dependencias:** EP-LM-002, EP-LM-003, EP-LM-004 (sistemas migrados)
**Estimacion:** 3 dev-days

---

#### US-LM-037: Tests de Carga del Nuevo Sistema

**ID:** US-LM-037
**Epica:** EP-LM-007
**Prioridad:** P1

**Historia:**
Como **Ingeniero de Migracion** quiero verificar que el nuevo sistema soporta al menos 2x el trafico actual del sistema legacy para tener margen de seguridad post-migracion.

**Criterios de Aceptacion:**
- [ ] Script de carga que simula trafico tipico del sistema legacy
- [ ] Baseline: trafico actual del legacy (requests/minuto pico)
- [ ] Target: 2x el baseline sin degradacion de latencia
- [ ] Metricas: latencia p50, p95, p99, tasa de error, CPU, memoria
- [ ] Resultado: PASS si latencia p99 < 2s y error rate < 0.1% a 2x baseline
- [ ] Reporte de capacidad con recomendaciones

**Tareas Tecnicas:**
1. Crear script de carga con locust o k6
2. Definir escenarios de carga basados en trafico real
3. Ejecutar contra staging
4. Documentar resultados y recomendaciones
5. Ajustar infra si es necesario

**Dependencias:** EP-LM-003 (nuevo sistema funcional)
**Estimacion:** 3 dev-days

---

### EP-LM-008: Cutover y Decommission

---

#### US-LM-038: Runbook de Cutover

**ID:** US-LM-038
**Epica:** EP-LM-008
**Prioridad:** P0

**Historia:**
Como **Administrador SuperPago** quiero un runbook detallado paso a paso del cutover final para ejecutar la migracion de forma ordenada y reversible.

**Criterios de Aceptacion:**
- [ ] Documento con cada paso numerado del cutover
- [ ] Responsable asignado para cada paso
- [ ] Tiempo estimado para cada paso
- [ ] Checklist pre-cutover (condiciones que deben cumplirse)
- [ ] Decision gates: puntos de "go/no-go" durante el cutover
- [ ] Plan de comunicacion: que decir, a quien, en que momento
- [ ] Contactos de emergencia para cada sistema involucrado
- [ ] Rehearsal: cutover de practica ejecutado en staging exitosamente

**Tareas Tecnicas:**
1. Redactar runbook de cutover
2. Revisar con equipo de infraestructura
3. Ejecutar rehearsal en staging
4. Ajustar runbook basado en rehearsal
5. Aprobar con stakeholders

**Dependencias:** EP-LM-001 a EP-LM-007 completadas
**Estimacion:** 3 dev-days

---

#### US-LM-039: DNS Switchover

**ID:** US-LM-039
**Epica:** EP-LM-008
**Prioridad:** P0

**Historia:**
Como **Ingeniero de Migracion** quiero ejecutar el switchover de DNS para redirigir todo el trafico de dominios legacy a la nueva infraestructura de forma controlada.

**Criterios de Aceptacion:**
- [ ] TTL de DNS reducido a 60 segundos 48 horas antes del cutover
- [ ] Switchover de A/CNAME records a nueva infraestructura
- [ ] Verificacion de propagacion DNS (multiples regiones)
- [ ] Monitoreo de trafico: 100% llega a nuevo sistema
- [ ] Rollback: revertir DNS a legacy en menos de 5 minutos
- [ ] Zero requests fallidos durante el switchover

**Tareas Tecnicas:**
1. Reducir TTL 48 horas antes
2. Preparar cambios DNS (no aplicar)
3. Ejecutar cambio en ventana de cutover
4. Verificar propagacion
5. Monitorear durante 2 horas

**Dependencias:** US-LM-038 (runbook aprobado)
**Estimacion:** 1 dev-day

---

#### US-LM-040: Periodo de Dual-Running y Monitoreo Intensivo

**ID:** US-LM-040
**Epica:** EP-LM-008
**Prioridad:** P0

**Historia:**
Como **Administrador SuperPago** quiero un periodo de dual-running con monitoreo 24/7 despues del cutover para detectar y resolver cualquier problema antes de apagar el sistema legacy.

**Criterios de Aceptacion:**
- [ ] Sistema legacy activo en modo read-only durante 72 horas post-cutover
- [ ] Monitoreo 24/7 con rotacion de on-call
- [ ] Dashboard especifico de post-cutover en Grafana
- [ ] Criterios de exito definidos para cada hora:
  - Hora 1-2: error rate < 0.5%, latencia normal
  - Hora 2-24: error rate < 0.1%, cero tickets de soporte
  - Hora 24-72: operacion normal, zero incidents
- [ ] Escalation path claro si se detectan problemas
- [ ] Decision de "apagar legacy" tomada al final de las 72 horas

**Tareas Tecnicas:**
1. Configurar sistema legacy en modo read-only
2. Crear dashboard post-cutover
3. Definir rotacion de on-call
4. Documentar escalation path
5. Ejecutar monitoreo

**Dependencias:** US-LM-039 (DNS switchover completado)
**Estimacion:** 3 dev-days (monitoreo)

---

#### US-LM-041: Decommission de Infraestructura Legacy

**ID:** US-LM-041
**Epica:** EP-LM-008
**Prioridad:** P2

**Historia:**
Como **Administrador SuperPago** quiero decomisionar la infraestructura legacy de forma segura y ordenada para dejar de pagar por recursos que ya no se usan.

**Criterios de Aceptacion:**
- [ ] Repos GitHub archivados (read-only): mipay_service, mipay_payment, mipay_web
- [ ] Tablas DynamoDB legacy en modo read-only por 90 dias
- [ ] Backup final de tablas legacy exportado a S3 (Parquet/JSON)
- [ ] EC2 instances legacy terminadas
- [ ] API Gateway legacy eliminado
- [ ] CloudFront distribution legacy deshabilitada
- [ ] Credenciales de servicios legacy rotadas/revocadas
- [ ] Verificacion: ningun sistema depende de infra legacy
- [ ] Ahorro de costos documentado

**Tareas Tecnicas:**
1. Archivar repos en GitHub
2. Exportar tablas a S3
3. Poner tablas en read-only
4. Terminar EC2 instances
5. Eliminar API Gateway y CloudFront
6. Rotar credenciales
7. Documentar ahorro

**Dependencias:** US-LM-040 (dual-running exitoso)
**Estimacion:** 2 dev-days

---

#### US-LM-042: Post-Mortem y Comunicacion Final

**ID:** US-LM-042
**Epica:** EP-LM-008
**Prioridad:** P2

**Historia:**
Como **Administrador SuperPago** quiero documentar las lecciones aprendidas y comunicar a todos los stakeholders que la migracion se completo exitosamente.

**Criterios de Aceptacion:**
- [ ] Documento post-mortem con:
  - Timeline de la migracion completa
  - Que salio bien
  - Que salio mal y como se resolvio
  - Metricas finales (downtime, errores, tiempo total)
  - Lecciones aprendidas
  - Recomendaciones para futuras migraciones
- [ ] Email final a clientes: "Migracion completada exitosamente"
- [ ] Comunicacion interna al equipo con metricas de exito
- [ ] Actualizacion de documentacion en covacha-projects
- [ ] Cierre formal de todas las epicas EP-LM

**Tareas Tecnicas:**
1. Redactar post-mortem
2. Compilar metricas finales
3. Enviar comunicaciones
4. Actualizar covacha-projects (CLAUDE.md, dependency-graph.yml)
5. Cerrar epicas e issues

**Dependencias:** US-LM-041 (decommission completado)
**Estimacion:** 2 dev-days

---

## Roadmap

### Fases de Migracion

```
FASE 1: Descubrimiento (Semana 1-2)
=====================================
EP-LM-001: Inventario y Mapping
  US-LM-001 ──┐
  US-LM-002 ──┤ (paralelo)
  US-LM-003 ──┤
  US-LM-004 ──┘
  US-LM-005 ──── (despues de completar inventario)

Entregable: Documento de inventario completo y aprobado


FASE 2: Preparacion de Datos y Auth (Semana 3-6)
=================================================
EP-LM-002: Migracion de Datos        EP-LM-006: Migracion de Auth
  US-LM-006 (usuarios)  ──────┐       US-LM-027 (crear en Cognito)
  US-LM-007 (orgs) ───────────┤       US-LM-028 (roles -> RBAC)
  US-LM-008 (transacciones) ──┤       US-LM-029 (passwords)
  US-LM-009 (tarjetas) ───────┤
  US-LM-010 (config) ─────────┘
  US-LM-011 (validacion) ──── (al final de fase 2)

Entregable: Datos migrados y validados, usuarios en Cognito


FASE 3: Proxy y Dual-Auth (Semana 5-8)
=======================================
EP-LM-003: Proxy de Compatibilidad   EP-LM-006 (cont.)
  US-LM-012 (proxy core) ─────┐       US-LM-030 (dual-auth)
  US-LM-013 (auth en proxy) ──┤       US-LM-031 (comunicacion)
  US-LM-014 (metricas) ───────┤
  US-LM-015 (feature flags) ──┤
  US-LM-016 (rate limit) ─────┘

Entregable: Proxy activo, dual-auth funcional


FASE 4: Migracion de Integraciones y Frontend (Semana 7-12)
============================================================
EP-LM-004: Openpay                    EP-LM-005: Frontend
  US-LM-017 (driver) ─────────┐       US-LM-022 (mapping) ─────┐
  US-LM-018 (webhooks) ───────┤       US-LM-023 (pagos UI) ────┤
  US-LM-019 (tokenizacion) ───┤       US-LM-024 (dashboard) ───┤
  US-LM-020 (sandbox tests) ──┤       US-LM-025 (redirects) ───┤
  US-LM-021 (switchover) ─────┘       US-LM-026 (comunicacion)─┘

Entregable: Openpay en nuevo sistema, frontend migrado


FASE 5: Validacion Completa (Semana 10-14)
===========================================
EP-LM-007: Testing y Validacion
  US-LM-032 (parity tests) ───┐
  US-LM-033 (shadow traffic) ─┤
  US-LM-034 (dashboard) ──────┤
  US-LM-035 (montos) ─────────┤
  US-LM-036 (smoke tests) ────┤
  US-LM-037 (carga) ──────────┘

Entregable: Paridad >= 99.9%, carga 2x verificada


FASE 6: Cutover y Cierre (Semana 14-16)
========================================
EP-LM-008: Cutover y Decommission
  US-LM-038 (runbook) ────────┐
  US-LM-039 (DNS) ────────────┤
  US-LM-040 (dual-running) ───┤
  US-LM-041 (decommission) ───┤
  US-LM-042 (post-mortem) ────┘

Entregable: Legacy apagado, migracion completada
```

### Timeline Resumen

| Fase | Semanas | Epicas | Hito |
|------|---------|--------|------|
| 1: Descubrimiento | 1-2 | EP-LM-001 | Inventario aprobado |
| 2: Datos y Auth | 3-6 | EP-LM-002, EP-LM-006 | Datos migrados, Cognito listo |
| 3: Proxy y Dual-Auth | 5-8 | EP-LM-003, EP-LM-006 | Proxy activo, dual-auth |
| 4: Integraciones y Frontend | 7-12 | EP-LM-004, EP-LM-005 | Openpay y UI migrados |
| 5: Validacion | 10-14 | EP-LM-007 | Paridad >= 99.9% |
| 6: Cutover | 14-16 | EP-LM-008 | Legacy apagado |

**Duracion total estimada:** 16 semanas (4 meses)

**Nota:** Las fases se solapan intencionalmente. La fase 3 puede iniciar antes de que la fase 2 termine completamente.

---

## Grafo de Dependencias

```
EP-LM-001 (Inventario)
    |
    +---> EP-LM-002 (Datos)
    |         |
    |         +---> EP-LM-004 (Openpay) --+
    |         |                            |
    |         +---> EP-LM-007 (Testing) ---+---> EP-LM-008 (Cutover)
    |                    ^                 |
    +---> EP-LM-003 (Proxy) ----+---------+
    |         |                 |
    |         +---> EP-LM-005 (Frontend) --+
    |
    +---> EP-LM-006 (Auth)
              |
              +---> EP-LM-003 (Proxy - auth)
              |
              +---> EP-LM-007 (Testing - auth)
```

### Dependencias Criticas (Path Critico)

```
EP-LM-001 -> EP-LM-002 -> EP-LM-007 -> EP-LM-008
    |                          ^
    +-> EP-LM-003 -> EP-LM-004 -+
```

El path critico pasa por: Inventario -> Datos -> Testing -> Cutover. Cualquier retraso en estas epicas retrasa todo el proyecto.

### Dependencias entre Repositorios

| Repo | Lee de | Escribe en | Epicas |
|------|--------|-----------|--------|
| `mipay_service` | - | - | EP-LM-001 (lectura) |
| `mipay_payment` | - | - | EP-LM-001 (lectura) |
| `mipay_web` | - | - | EP-LM-001 (lectura) |
| `covacha-core` | mipay_* (migracion) | covacha_* tables | EP-LM-002, EP-LM-003, EP-LM-006 |
| `covacha-payment` | mipay_payment (migracion) | modspei_* tables | EP-LM-002, EP-LM-004 |
| `covacha-webhook` | - | - | EP-LM-004 |
| `mf-core` | - | - | EP-LM-005 |
| `mf-payment` | - | - | EP-LM-005 |
| `mf-auth` | - | - | EP-LM-005, EP-LM-006 |
| `mf-dashboard` | - | - | EP-LM-005 |
| `mf-settings` | - | - | EP-LM-005 |
| `covacha-projects` | - | documentacion | EP-LM-001, EP-LM-008 |

---

## Riesgos y Mitigaciones

| # | Riesgo | Probabilidad | Impacto | Mitigacion |
|---|--------|-------------|---------|------------|
| R1 | Perdida de datos durante migracion | Media | Critico | Validacion post-migracion con checksums, dry-run obligatorio, rollback script |
| R2 | Downtime durante cutover | Baja | Critico | Proxy de compatibilidad, dual-running, DNS con TTL bajo |
| R3 | Discrepancia en montos financieros | Media | Critico | Validacion al centavo, shadow traffic, reconciliacion diaria |
| R4 | Usuarios no pueden autenticarse | Media | Alto | Dual-auth por 90 dias, migration trigger en Cognito, soporte dedicado |
| R5 | Tokens Openpay no funcionan en nuevo sistema | Baja | Alto | Validar en sandbox antes de produccion, mantener legacy como fallback |
| R6 | Volumen de datos mayor al estimado | Media | Medio | Scripts incrementales con batch processing, estimacion antes de ejecutar |
| R7 | Clientes se resisten al cambio de UI | Alta | Medio | Comunicacion temprana, periodo de "volver atras", soporte dedicado |
| R8 | Webhook duplicados durante switchover | Media | Medio | Idempotency keys en todo handler, deduplicacion por event_id |
| R9 | Performance del nuevo sistema inferior al legacy | Baja | Alto | Tests de carga a 2x baseline, tuning antes de cutover |
| R10 | Integraciones no documentadas en legacy | Media | Medio | Inventario exhaustivo (EP-LM-001), grep de codebase, revision con equipo original |

### Estrategias Globales de Mitigacion

1. **Canary deployment**: Migrar primero organizaciones de bajo volumen para validar
2. **Feature flags**: Cada cliente se migra individualmente, reversible al instante
3. **Shadow traffic**: Validar con trafico real antes de switchover
4. **Comunicacion proactiva**: Clientes informados en cada fase
5. **Monitoreo 24/7**: Durante cutover y 72 horas post-cutover

---

## Plan de Rollback

### Rollback por Fase

| Fase | Que se revierte | Como | Tiempo estimado |
|------|----------------|------|-----------------|
| Datos (EP-LM-002) | Borrar datos migrados | Script de rollback elimina registros con `migration_source: "mipay"` | 30 min |
| Proxy (EP-LM-003) | Desactivar proxy | Feature flag: proxy_enabled=false para todos | 1 min |
| Openpay (EP-LM-004) | Revertir webhook URL | Cambiar URL en panel de Openpay a endpoint legacy | 5 min |
| Frontend (EP-LM-005) | Reactivar mipay_web | Revertir redirects en CloudFront | 10 min |
| Auth (EP-LM-006) | Reactivar JWT legacy | Feature flag: dual_auth=legacy_only | 1 min |
| Cutover (EP-LM-008) | Revertir DNS | Cambiar DNS records a infra legacy (TTL 60s) | 5 min |

### Procedimiento de Rollback de Emergencia

```
1. DETECTAR: Alerta de Grafana o reporte de usuario
   Criterio: error rate > 1% O latencia p99 > 5s O reporte de perdida de datos

2. EVALUAR (max 5 minutos):
   - Afecta a 1 cliente o a todos?
   - Es tema de datos, auth, pagos, o UI?
   - Se puede resolver sin rollback?

3. DECIDIR: Go/No-Go de rollback
   Aprobadores: Lead de Ingenieria + Product Owner

4. EJECUTAR rollback de la fase afectada (ver tabla arriba)

5. COMUNICAR: Notificar a equipo y clientes afectados

6. INVESTIGAR: Root cause analysis en las siguientes 24 horas

7. REMEDIAR: Corregir el problema y re-intentar la fase
```

### Criterio de No-Rollback

Una vez que se verifica:
- 72 horas de dual-running sin incidentes
- 0 requests al proxy legacy por 24 horas
- Todos los clientes confirmaron operacion normal
- Post-mortem completado

Se toma la decision de **no-rollback** y se procede con decommission. Despues de este punto, rollback requiere re-deploy completo del sistema legacy (estimado: 4-8 horas).

---

## Criterios de Exito

### Por Epica

| Epica | Criterio de Exito |
|-------|-------------------|
| EP-LM-001 | Inventario 100% completo y aprobado por equipo de producto |
| EP-LM-002 | Validacion post-migracion PASS para todas las tablas, checksums coinciden |
| EP-LM-003 | Proxy funcional, 100% de endpoints legacy traducidos, latencia < 50ms overhead |
| EP-LM-004 | Todas las operaciones Openpay funcionan en produccion via nuevo sistema |
| EP-LM-005 | Paridad funcional de todas las pantallas, redirects activos, cero quejas de UI |
| EP-LM-006 | 100% de usuarios pueden autenticarse, roles correctos, dual-auth funcional |
| EP-LM-007 | Paridad >= 99.9%, tests de carga a 2x exitosos, smoke tests verdes 24 horas |
| EP-LM-008 | Cutover exitoso, 72h sin incidentes, legacy decomisionado, ahorro documentado |

### Criterios Globales

| Criterio | Valor Objetivo |
|----------|---------------|
| Downtime total durante migracion | 0 minutos |
| Perdida de datos | 0 registros |
| Discrepancia de montos | $0.00 MXN |
| Usuarios que no pueden autenticarse | 0 (al final de fase 6) |
| Transacciones fallidas por migracion | 0 |
| Tiempo total de migracion | <= 16 semanas |
| Ahorro de infra post-migracion | >= 25% del costo legacy |
| Satisfaccion de clientes (encuesta) | >= 4/5 |

### Definition of Done Global

La migracion se considera **COMPLETADA** cuando:

1. Todos los clientes operan en el nuevo sistema
2. Zero requests al sistema legacy por 7 dias consecutivos
3. Tablas legacy en modo read-only
4. Repos legacy archivados
5. Infraestructura legacy decomisionada
6. Post-mortem documentado y compartido
7. Ahorro de costos verificado
8. Todos los issues EP-LM cerrados

---

## Resumen de User Stories

| Epica | User Stories | IDs | Total |
|-------|-------------|-----|-------|
| EP-LM-001: Inventario y Mapping | 5 | US-LM-001 a US-LM-005 | 5 |
| EP-LM-002: Migracion de Datos | 6 | US-LM-006 a US-LM-011 | 6 |
| EP-LM-003: Proxy de Compatibilidad | 5 | US-LM-012 a US-LM-016 | 5 |
| EP-LM-004: Migracion Openpay | 5 | US-LM-017 a US-LM-021 | 5 |
| EP-LM-005: Migracion Frontend | 5 | US-LM-022 a US-LM-026 | 5 |
| EP-LM-006: Migracion Auth | 5 | US-LM-027 a US-LM-031 | 5 |
| EP-LM-007: Testing y Paridad | 6 | US-LM-032 a US-LM-037 | 6 |
| EP-LM-008: Cutover y Decommission | 5 | US-LM-038 a US-LM-042 | 5 |
| **TOTAL** | | | **42** |

### Estimacion Total

| Metrica | Valor |
|---------|-------|
| Epicas | 8 |
| User Stories | 42 |
| Dev-days estimados | ~115 dev-days |
| Duracion (2 devs full-time) | ~16 semanas |
| Duracion (3 devs full-time) | ~11 semanas |
