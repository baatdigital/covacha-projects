# SuperPago SPEI - Epicas de Expansion (EP-SP-014 a EP-SP-020)

**Fecha**: 2026-02-14
**Product Owner**: SuperPago
**Estado**: En Desarrollo (EP-SP-019 completada backend, resto en planificacion)
**Continua desde**: SPEI-PRODUCT-PLAN.md (EP-SP-001 a EP-SP-010) y SPEI-FRONTEND-EPICS-MULTI-TIER.md (EP-SP-011 a EP-SP-013)
**User Stories**: US-SP-052 en adelante (continua desde US-SP-051)

---

## Tabla de Contenidos

1. [Contexto y Motivacion](#contexto-y-motivacion)
2. [Nuevos Roles](#nuevos-roles)
3. [Mapa de Epicas de Expansion](#mapa-de-epicas-de-expansion)
4. [Epicas Detalladas](#epicas-detalladas)
5. [User Stories Detalladas](#user-stories-detalladas)
6. [Roadmap de Expansion](#roadmap-de-expansion)
7. [Grafo de Dependencias](#grafo-de-dependencias)
8. [Riesgos y Mitigaciones](#riesgos-y-mitigaciones)

---

## Contexto y Motivacion

El plan SPEI original (EP-SP-001 a EP-SP-013, US-SP-001 a US-SP-051) cubre el motor de cuentas, el ledger de partida doble, SPEI in/out via Monato, movimientos internos intra-organizacion, y los 3 portales frontend. Este documento extiende ese plan con 5 nuevas capacidades:

| Capacidad | Problema que Resuelve |
|-----------|----------------------|
| **Transferencias Inter-Org** | Mover dinero entre organizaciones de SuperPago sin costo SPEI (movimiento contable interno) |
| **Cash-In / Cash-Out** | Permitir depositos y retiros de efectivo en red de puntos fisicos |
| **Subasta de Efectivo** | Mercado interno para digitalizar efectivo fisico de la red de puntos |
| **Agente IA WhatsApp** | Operar cuentas SPEI via conversacion en WhatsApp (consulta saldo, transfiere, paga servicios) |
| **Integridad de Datos** | Garantizar consistencia financiera: idempotencia, prevencion de double-spending, sp_organization_id obligatorio |

---

## Nuevos Roles

Ademas de los roles existentes (R1: Admin SuperPago, R2: Cliente Empresa, R3: Sistema), se agregan:

### R4: Usuario Final B2C (Persona Natural)

Ya definido implicitamente en EP-SP-012 pero ahora opera como actor en Cash-In/Cash-Out y WhatsApp.

**Responsabilidades adicionales:**
- Depositar efectivo en puntos autorizados (Cash-In)
- Retirar efectivo en puntos autorizados (Cash-Out)
- Consultar saldo y hacer transferencias via WhatsApp
- Pagar servicios (BillPay) via WhatsApp

### R5: Agente IA (covacha-botia)

Chatbot conversacional en WhatsApp que opera como intermediario entre el usuario y las APIs financieras.

**Responsabilidades:**
- Autenticar al usuario via WhatsApp (vincular numero telefonico a cuenta)
- Ejecutar consultas de saldo
- Ejecutar transferencias SPEI con confirmacion 2FA
- Ejecutar pagos de servicios (BillPay) con confirmacion
- Enviar notificaciones proactivas de movimientos
- Respetar limites y politicas de la organizacion del usuario

### R6: Operador de Punto de Pago

Persona fisica o sistema en un punto autorizado (tipo OXXO) que procesa Cash-In/Cash-Out.

**Responsabilidades:**
- Recibir efectivo del usuario y acreditar via terminal/API
- Entregar efectivo al usuario y debitar via terminal/API
- Generar comprobantes de operacion
- Cuadrar caja al final del turno

---

## Mapa de Epicas de Expansion

| ID | Epica | Complejidad | Sprint Sugerido | Dependencias Existentes | Estado |
|----|-------|-------------|-----------------|------------------------|--------|
| EP-SP-014 | Transferencias Internas Inter-Organizacion ✅ | M | 4-5 | EP-SP-001, EP-SP-003, EP-SP-006 | COMPLETADO (backend) |
| EP-SP-015 | Cash-In / Cash-Out (Red de Puntos) ✅ | XL | 5-7 | EP-SP-001, EP-SP-003, EP-SP-010 | COMPLETADO (backend) |
| EP-SP-016 | Subasta de Efectivo (Mercado de Liquidez) ✅ | L | 7-8 | EP-SP-014, EP-SP-015 | COMPLETADO (backend) |
| EP-SP-017 | Agente IA WhatsApp - Core (covacha-botia) ✅ | XL | 5-7 | EP-SP-001, EP-SP-004, EP-SP-005 | COMPLETADO (backend) |
| EP-SP-018 | Agente IA WhatsApp - BillPay y Notificaciones | L | 7-8 | EP-SP-017 | PENDIENTE |
| EP-SP-019 | Reglas de Integridad de Datos (Cross-cutting) | L | 1-2 (paralela) | EP-SP-001, EP-SP-003 | COMPLETADO (backend) |
| EP-SP-020 | mf-sp - Pantallas de Cash, Subasta y Config IA | L | 7-9 | EP-SP-007, EP-SP-015, EP-SP-016, EP-SP-017 | PENDIENTE |

**Totales de expansion:**
- 7 epicas nuevas
- 33 user stories nuevas (US-SP-052 a US-SP-084)
- Estimacion total: ~145 dev-days

---

## Epicas Detalladas

---

### EP-SP-014: Transferencias Internas Inter-Organizacion

> **Estado: COMPLETADO (backend)** - Implementado en `covacha-payment` branch `develop` (2026-02-17). 4 US completadas (US-SP-052 a US-SP-055). 27 tests nuevos, 761 total.

**Descripcion:**
Mover dinero entre cuentas de DIFERENTES organizaciones dentro de SuperPago sin usar SPEI. Es un movimiento contable puro: la cuenta de SuperPago (concentradora) actua como intermediario. No hay costo de SPEI, no sale dinero del ecosistema, y la operacion es instantanea. Ejemplo: SuperPago transfiere a la sub-concentradora de Boxito.

**Diferencia con EP-SP-006 (Movimientos Internos):**
EP-SP-006 mueve dinero dentro de la MISMA organizacion. EP-SP-014 mueve dinero ENTRE organizaciones, lo cual requiere:
- Validacion de que ambas organizaciones estan activas
- Permiso explicito del Admin SuperPago (Tier 1) o politica configurada
- Asientos contables que cruzan boundaries de organizacion
- Audit trail especial (movimiento cross-org)

**User Stories:**
- US-SP-052, US-SP-053, US-SP-054, US-SP-055

**Criterios de Aceptacion de la Epica:**
- [ ] Transferencia inter-org entre cuentas CONCENTRADORA de diferentes organizaciones
- [ ] Transferencia inter-org desde cuenta de SuperPago a cuenta de cualquier organizacion hija
- [ ] Operacion instantanea, sin costo SPEI
- [ ] Asientos de partida doble que cruzan boundaries de organizacion
- [ ] Solo Admin SuperPago (Tier 1) puede iniciar transferencias inter-org (o via politica pre-aprobada)
- [ ] Idempotencia estricta
- [ ] Audit trail especial con tag `CROSS_ORG`
- [ ] El saldo total del ecosistema no cambia (es un movimiento de suma cero)
- [ ] Tests >= 98%

**Dependencias:** EP-SP-001 (cuentas), EP-SP-003 (ledger), EP-SP-006 (base de movimientos internos)

**Complejidad:** M (4 user stories, extiende la logica de EP-SP-006 con validaciones cross-org)

**Repositorio:** `covacha-payment`

---

### EP-SP-015: Cash-In / Cash-Out (Red de Puntos)

> **Estado: COMPLETADO (backend)** - Implementado en `covacha-payment` branch `develop` (2026-02-17). US-SP-056 a US-SP-059 completadas. 25 tests nuevos, 786 total.

**Descripcion:**
Sistema de depositos y retiros de efectivo en una red de puntos de pago fisicos (similar a OXXO Pay). Un usuario se presenta en un punto autorizado, deposita efectivo (Cash-In) y se acredita a su cuenta digital, o solicita un retiro (Cash-Out) y se le entrega efectivo debitando de su cuenta.

Cada punto de pago es una entidad registrada con su propia cuenta de liquidacion en SuperPago. El efectivo depositado genera un asiento contable: DEBIT en la cuenta del punto (tiene mas efectivo) y CREDIT en la cuenta del usuario (tiene mas saldo digital).

**User Stories:**
- US-SP-056, US-SP-057, US-SP-058, US-SP-059, US-SP-060, US-SP-061

**Criterios de Aceptacion de la Epica:**
- [ ] Modelo de Punto de Pago (PaymentPoint) con cuenta de liquidacion propia
- [ ] Registro y gestion de puntos de pago (CRUD)
- [ ] Cash-In: deposito de efectivo -> acreditacion en cuenta del usuario
- [ ] Cash-Out: retiro de efectivo -> debito en cuenta del usuario
- [ ] Asientos de partida doble para cada operacion cash
- [ ] Limites por operacion, por dia, por punto
- [ ] Generacion de referencia unica para cada operacion (codigo QR o numerico)
- [ ] Comprobante digital de operacion
- [ ] Reconciliacion de puntos (efectivo fisico vs saldo digital)
- [ ] Nuevas categorias de ledger: CASH_IN, CASH_OUT
- [ ] Comision configurable por operacion cash
- [ ] Tests >= 98%

**Dependencias:** EP-SP-001 (cuentas), EP-SP-003 (ledger), EP-SP-010 (limites y politicas)

**Complejidad:** XL (6 user stories, nueva infraestructura de puntos de pago, flujos bidireccionales)

**Repositorios:** `covacha-payment`, `covacha-webhook` (notificaciones)

---

### EP-SP-016: Subasta de Efectivo (Mercado de Liquidez)

> **Estado: COMPLETADO (backend)**

**Descripcion:**
Mercado interno de liquidez dentro de SuperPago. Los puntos de pago acumulan efectivo fisico que necesitan digitalizar. Las empresas (Tier 2) necesitan efectivo fisico en ubicaciones especificas. La subasta permite a las empresas "comprar" el efectivo de los puntos via transferencia interna: la empresa transfiere saldo digital al punto, y el punto asigna el efectivo fisico para retiro/uso.

**Flujo:**
1. Punto de pago tiene $100K en efectivo fisico -> publica oferta en el mercado
2. Empresa Boxito necesita efectivo -> ve la oferta y la compra
3. SuperPago ejecuta transferencia interna: cuenta Boxito -> cuenta del punto
4. Efectivo queda asignado a Boxito para retiro en el punto
5. Boxito (o sus empleados) retiran el efectivo fisicamente

**User Stories:**
- US-SP-062, US-SP-063, US-SP-064, US-SP-065

**Criterios de Aceptacion de la Epica:**
- [ ] Modelo de Oferta de Efectivo (CashOffer) con monto, ubicacion, vigencia
- [ ] Publicacion de ofertas por puntos de pago (o automatico cuando superan umbral)
- [ ] Marketplace visible para empresas Tier 2 y Admin Tier 1
- [ ] Compra de oferta = transferencia inter-org automatica
- [ ] Asignacion de efectivo al comprador con referencia de retiro
- [ ] Expiracion de ofertas no compradas
- [ ] Comision de SuperPago por la intermediacion (configurable)
- [ ] Dashboard de liquidez para Admin (efectivo total en red, ofertas activas, tendencias)
- [ ] Tests >= 98%

**Dependencias:** EP-SP-014 (transferencias inter-org), EP-SP-015 (puntos de pago y cash)

**Complejidad:** L (4 user stories, marketplace interno, orquestacion de transferencias)

**Repositorio:** `covacha-payment`

---

### EP-SP-017: Agente IA WhatsApp - Core (covacha-botia)

> **Estado: COMPLETADO (backend)** - Implementado en `covacha-botia` branch `develop` (2026-02-17)

**Descripcion:**
Agente conversacional en WhatsApp que permite a usuarios operar sus cuentas SPEI via chat. El agente vive en `covacha-botia` y se comunica con `covacha-payment` via API interna. Soporta: vinculacion de cuenta, consulta de saldo, transferencias SPEI, y confirmacion 2FA antes de mover dinero. Cada agente esta atado a un `sp_organization_id`.

**User Stories:**
- US-SP-066, US-SP-067, US-SP-068, US-SP-069, US-SP-070

**Criterios de Aceptacion de la Epica:**
- [x] Vinculacion de numero WhatsApp con cuenta SPEI del usuario
- [x] Consulta de saldo via mensaje: "Cual es mi saldo?" -> responde con saldo actual
- [x] Transferencia SPEI via conversacion con flujo guiado:
  - "Envia $500 a CLABE 072180..." -> confirma datos -> solicita PIN/2FA -> ejecuta
- [x] Confirmacion 2FA obligatoria antes de toda operacion que mueve dinero
- [x] Contexto de sesion conversacional (recuerda que estaba haciendo el usuario)
- [x] Respuestas en lenguaje natural, no menus rigidos
- [x] Manejo de errores amigable ("No tienes saldo suficiente. Tu saldo es $X")
- [x] Rate limiting por usuario (max N operaciones por hora via WhatsApp)
- [x] Logs y audit trail de todas las operaciones via WhatsApp
- [x] El agente hereda los limites/politicas de la organizacion del usuario
- [x] Tests >= 98% con mocks de WhatsApp API y covacha-payment API

**Dependencias:** EP-SP-001 (cuentas), EP-SP-004 (SPEI out), EP-SP-005 (SPEI in para notif), EP-SP-010 (limites)

**Complejidad:** XL (5 user stories, integracion WhatsApp + payments, NLU, 2FA, sesiones)

**Repositorios:** `covacha-botia` (agente), `covacha-payment` (APIs consultadas), `covacha-webhook` (webhook WhatsApp)

---

### EP-SP-018: Agente IA WhatsApp - BillPay y Notificaciones

**Descripcion:**
Extension del agente IA para pago de servicios (BillPay) y notificaciones proactivas. BillPay permite pagar servicios como CFE (luz), agua, telefono, gas, internet via agregadores de servicios. Las notificaciones proactivas informan al usuario de depositos recibidos, transferencias completadas, y alertas de seguridad directamente en su WhatsApp.

**User Stories:**
- US-SP-071, US-SP-072, US-SP-073, US-SP-074

**Criterios de Aceptacion de la Epica:**
- [ ] Catalogo de servicios pagables (CFE, Telmex, etc.) via agregador
- [ ] Flujo conversacional: "Paga mi recibo de luz" -> pide referencia -> confirma monto -> 2FA -> paga
- [ ] Consulta de adeudo antes de pagar (si el agregador lo soporta)
- [ ] Comprobante de pago enviado como mensaje/PDF por WhatsApp
- [ ] Notificacion proactiva de deposito recibido: "Recibiste $X de [banco] [concepto]"
- [ ] Notificacion proactiva de transferencia completada/fallida
- [ ] Notificaciones configurables por usuario (activar/desactivar por tipo)
- [ ] Integracion con al menos 1 agregador de BillPay (Openpay, Arcus, o similar)
- [ ] Asientos contables para pagos de servicios (nueva categoria BILL_PAY)
- [ ] Tests >= 98%

**Dependencias:** EP-SP-017 (core del agente), EP-SP-003 (ledger), EP-SP-005 (webhooks para triggers de notif)

**Complejidad:** L (4 user stories, integracion con agregador externo, notificaciones event-driven)

**Repositorios:** `covacha-botia`, `covacha-payment`, `covacha-webhook`

---

### EP-SP-019: Reglas de Integridad de Datos (Cross-cutting)

> **Estado: COMPLETADO (backend)** - Implementado en `covacha-payment` branch `develop` (2026-02-17)

**Descripcion:**
Capa transversal de proteccion de integridad financiera. Se implementa en PARALELO con las demas epicas (Sprint 1-2) porque afecta a TODOS los servicios. Incluye: sp_organization_id obligatorio en toda tabla y operacion, prevencion de race conditions con DynamoDB ConditionExpressions y TransactWriteItems, idempotencia estricta con tabla dedicada, y prevencion de double-spending con locks optimistas.

**User Stories:**
- US-SP-075, US-SP-076, US-SP-077, US-SP-078, US-SP-079

**Criterios de Aceptacion de la Epica:**
- [x] `sp_organization_id` presente y validado en TODA operacion y TODA tabla
- [x] Middleware que rechaza requests sin `X-SP-Organization-Id` header
- [x] Tabla de idempotencia dedicada con TTL configurable
- [x] Toda operacion mutativa requiere `idempotency_key`
- [x] DynamoDB TransactWriteItems para operaciones multi-entry
- [x] ConditionExpressions para prevenir saldo negativo
- [x] Lock optimista en saldo para prevenir double-spending
- [ ] Tests de concurrencia (simular N requests simultaneos)
- [ ] Documentacion de patrones de integridad para desarrolladores
- [x] Tests >= 98%

**Dependencias:** EP-SP-001, EP-SP-003 (se aplica a ambos desde el inicio)

**Complejidad:** L (5 user stories, cross-cutting, impacta a todos los servicios)

**Repositorios:** `covacha-payment`, `covacha-webhook`, `covacha-botia` (todos)

---

### EP-SP-020: mf-sp - Pantallas de Cash, Subasta y Config IA

**Descripcion:**
Extension del micro-frontend `mf-sp` con pantallas para las nuevas funcionalidades: gestion de puntos de pago y operaciones Cash-In/Cash-Out (Tier 1 y Tier 2), marketplace de subasta de efectivo (Tier 1 y Tier 2), y configuracion del agente IA WhatsApp (Tier 1 y Tier 2). Se integra con la arquitectura multi-tier existente de EP-SP-007.

**User Stories:**
- US-SP-080, US-SP-081, US-SP-082, US-SP-083, US-SP-084

**Criterios de Aceptacion de la Epica:**
- [ ] Pantallas de gestion de puntos de pago (Admin Tier 1)
- [ ] Historial de operaciones Cash-In/Cash-Out (Admin + Business)
- [ ] Marketplace de subasta de efectivo (Admin + Business)
- [ ] Configuracion del agente IA WhatsApp por organizacion (Admin + Business)
- [ ] Dashboard de operaciones del agente IA (Admin)
- [ ] Nuevas rutas integradas en la estructura multi-tier existente
- [ ] Componentes reutilizables con mismos patrones de EP-SP-013
- [ ] Tests >= 98%

**Dependencias:** EP-SP-007 (scaffold), EP-SP-015 (API Cash), EP-SP-016 (API Subasta), EP-SP-017 (API Agente IA)

**Complejidad:** L (5 user stories, extension de MF existente)

**Repositorio:** `mf-sp`

---

## User Stories Detalladas

---

### EP-SP-014: Transferencias Internas Inter-Organizacion

---

#### US-SP-052: Modelo de Transferencia Inter-Organizacion

**ID:** US-SP-052
**Epica:** EP-SP-014
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero un modelo de transferencia inter-organizacion para representar movimientos de dinero entre diferentes organizaciones dentro de SuperPago sin usar SPEI.

**Criterios de Aceptacion:**
- [x] Modelo `InterOrgTransfer` en DynamoDB:
  - `PK: ORG#{source_org_id}`, `SK: INTERORG_TXN#{transfer_id}`
  - `transfer_id` (UUID)
  - `source_organization_id`
  - `destination_organization_id`
  - `source_account_id` (cuenta concentradora o CLABE de la org origen)
  - `destination_account_id` (cuenta concentradora o CLABE de la org destino)
  - `amount` (Decimal, 2 decimales)
  - `concept` (descripcion del movimiento)
  - `status`: PENDING | COMPLETED | FAILED | REVERSED
  - `initiated_by` (user_id del admin que inicia, o "SYSTEM" si es automatico)
  - `approval_policy`: NONE | ADMIN_REQUIRED
  - `idempotency_key`
  - `created_at`, `completed_at`
- [x] GSI `GSI-DEST-ORG`: `PK: DEST_ORG#{dest_org_id}`, `SK: INTERORG_TXN#{id}` para consultar transferencias recibidas
- [x] GSI `GSI-INTERORG-STATUS`: `PK: INTERORG_STATUS#{status}`, `SK: #{created_at}` para listar por estado
- [x] Categoria de ledger nueva: `INTER_ORG_TRANSFER`
- [x] Validacion: ambas organizaciones deben existir y estar activas
- [x] Validacion: solo se permite entre cuentas CONCENTRADORA o CLABE

**Tareas Tecnicas:**
1. Crear modelo DynamoDB con PK/SK y GSIs
2. Crear dataclass de Python con validaciones
3. Crear repository con operaciones CRUD
4. Agregar categoria `INTER_ORG_TRANSFER` al LedgerEntry
5. Tests unitarios del modelo y validaciones

**Dependencias:** US-SP-001, US-SP-010
**Estimacion:** 3 dev-days

---

#### US-SP-053: Servicio de Transferencia Inter-Org

**ID:** US-SP-053
**Epica:** EP-SP-014
**Prioridad:** P0

**Historia:**
Como **Administrador SuperPago** quiero ejecutar transferencias de dinero entre organizaciones del ecosistema para mover fondos internamente sin costo SPEI.

**Criterios de Aceptacion:**
- [x] `POST /api/v1/admin/transfers/inter-org`
  - Body: `{ source_org_id, source_account_id, dest_org_id, dest_account_id, amount, concept, idempotency_key }`
  - Requiere permiso `sp:admin`
- [x] Validaciones pre-ejecucion:
  - Ambas organizaciones existen y estan activas
  - Ambas cuentas existen, estan ACTIVE, y son tipo CONCENTRADORA o CLABE
  - Saldo disponible en cuenta origen >= monto
  - Cuenta origen pertenece a source_org_id
  - Cuenta destino pertenece a dest_org_id
- [x] Flujo atomico:
  1. Crear registro InterOrgTransfer con status PENDING
  2. Crear asientos en ledger via TransactWriteItems:
     - DEBIT en cuenta origen (org A)
     - CREDIT en cuenta destino (org B)
  3. Si escritura exitosa: status -> COMPLETED
  4. Si falla: status -> FAILED, no se crean entries
- [x] Operacion instantanea (no pasa por SPEI, no hay latencia de proveedor)
- [x] Sin comision (configurable para futuro)
- [x] Idempotencia: misma `idempotency_key` retorna resultado anterior
- [x] Audit trail con tag `CROSS_ORG` y ambos org_ids

**Tareas Tecnicas:**
1. Crear `InterOrgTransferService` con logica de validacion y ejecucion
2. Endpoint REST protegido con decorator de admin
3. Integracion con LedgerService para asientos atomicos
4. Integracion con tabla de idempotencia
5. Audit logging con tag cross-org
6. Tests del flujo completo: happy path, saldo insuficiente, org inactiva, idempotencia

**Dependencias:** US-SP-052, US-SP-011, US-SP-002
**Estimacion:** 4 dev-days

---

#### US-SP-054: Transferencia Inter-Org con Politica de Pre-Aprobacion

**ID:** US-SP-054
**Epica:** EP-SP-014
**Prioridad:** P1

**Historia:**
Como **Administrador SuperPago** quiero configurar politicas de transferencia inter-org automaticas para que ciertos movimientos recurrentes no requieran aprobacion manual cada vez.

**Criterios de Aceptacion:**
- [x] Modelo `InterOrgPolicy` en DynamoDB:
  - `PK: ORG#{source_org_id}`, `SK: INTERORG_POLICY#{policy_id}`
  - `source_organization_id`, `destination_organization_id`
  - `max_amount_per_transfer` (limite por operacion)
  - `max_amount_daily` (limite diario acumulado)
  - `allowed_initiators` (lista de user_ids o "ANY_ADMIN")
  - `auto_approve`: boolean (si true, no requiere aprobacion manual)
  - `status`: ACTIVE | SUSPENDED
  - `created_by`, `created_at`
- [x] `POST /api/v1/admin/transfers/inter-org/policies` - Crear politica
- [x] `GET /api/v1/admin/transfers/inter-org/policies` - Listar politicas
- [x] `PATCH /api/v1/admin/transfers/inter-org/policies/{id}` - Modificar
- [x] Al ejecutar transferencia inter-org:
  - Si existe politica activa y auto_approve=true y dentro de limites: ejecutar directamente
  - Si existe politica pero excede limites: rechazar con mensaje descriptivo
  - Si no existe politica: solo admin puede ejecutar manualmente
- [x] Audit trail de cambios a politicas

**Tareas Tecnicas:**
1. Crear modelo InterOrgPolicy en DynamoDB
2. CRUD endpoints para politicas
3. Integrar validacion de politica en InterOrgTransferService
4. Tests de politicas: con auto_approve, excediendo limites, sin politica

**Dependencias:** US-SP-053
**Estimacion:** 3 dev-days

---

#### US-SP-055: Historial y Reporte de Transferencias Inter-Org

**ID:** US-SP-055
**Epica:** EP-SP-014
**Prioridad:** P1

**Historia:**
Como **Administrador SuperPago** quiero ver el historial de todas las transferencias inter-organizacion para auditar y conciliar los movimientos entre organizaciones del ecosistema.

**Criterios de Aceptacion:**
- [x] `GET /api/v1/admin/transfers/inter-org`
  - Query params: `source_org_id`, `dest_org_id`, `status`, `from_date`, `to_date`, `page`, `page_size`
  - Response incluye: datos de la transferencia + nombres de organizaciones + saldos resultantes
- [x] `GET /api/v1/admin/transfers/inter-org/{transfer_id}` - Detalle
  - Incluye los entries del ledger asociados
- [x] `GET /api/v1/admin/transfers/inter-org/summary`
  - Resumen por periodo: total transferido, numero de operaciones, top pares org-a-org
- [x] Paginacion server-side
- [x] Export a CSV
- [x] Solo accesible con permiso `sp:admin`

**Tareas Tecnicas:**
1. Endpoints de listado con filtros y paginacion
2. Endpoint de detalle con entries del ledger
3. Endpoint de resumen agregado
4. Export CSV
5. Tests de filtros, paginacion, y resumen

**Dependencias:** US-SP-053
**Estimacion:** 3 dev-days

---

### EP-SP-015: Cash-In / Cash-Out (Red de Puntos)

---

#### US-SP-056: Modelo de Punto de Pago (PaymentPoint)

**ID:** US-SP-056
**Epica:** EP-SP-015
**Prioridad:** P0

**Historia:**
Como **Administrador SuperPago** quiero registrar puntos de pago fisicos en el sistema para crear una red donde los usuarios puedan depositar y retirar efectivo.

**Criterios de Aceptacion:**
- [ ] Modelo `PaymentPoint` en DynamoDB:
  - `PK: ORG#{org_id}`, `SK: POINT#{point_id}`
  - `point_id` (UUID)
  - `organization_id` (la org que opera el punto)
  - `name` (nombre del punto, ej: "Tienda OXXO Reforma 123")
  - `address` (direccion fisica completa)
  - `coordinates` (lat/lng para geolocalizacion futura)
  - `settlement_account_id` (cuenta de liquidacion del punto en SuperPago)
  - `cash_balance` (efectivo fisico estimado en el punto)
  - `status`: ACTIVE | SUSPENDED | CLOSED
  - `daily_limit_cash_in` (limite diario de depositos)
  - `daily_limit_cash_out` (limite diario de retiros)
  - `per_transaction_limit` (limite por operacion)
  - `commission_cash_in` (porcentaje o fijo)
  - `commission_cash_out` (porcentaje o fijo)
  - `operating_hours` (JSON con horarios)
  - `operator_user_id` (usuario responsable del punto)
  - `created_at`, `updated_at`
- [ ] GSI `GSI-POINT-STATUS`: `PK: POINT_STATUS#{status}`, `SK: POINT#{id}` para listar por estado
- [ ] El punto tiene su propia cuenta de liquidacion (tipo CLABE o DISPERSION)
- [ ] Al registrar punto, se crea automaticamente la cuenta de liquidacion si no existe
- [ ] `POST /api/v1/admin/payment-points` - Registrar punto (solo admin)
- [ ] `GET /api/v1/admin/payment-points` - Listar puntos con filtros
- [ ] `PATCH /api/v1/admin/payment-points/{id}` - Actualizar punto
- [ ] `GET /api/v1/admin/payment-points/{id}` - Detalle del punto

**Tareas Tecnicas:**
1. Crear modelo PaymentPoint en DynamoDB con GSIs
2. Crear dataclass de Python con validaciones
3. CRUD endpoints para puntos de pago
4. Logica de creacion automatica de cuenta de liquidacion
5. Tests del modelo y endpoints

**Dependencias:** US-SP-001, US-SP-002
**Estimacion:** 4 dev-days

---

#### US-SP-057: Flujo de Cash-In (Deposito de Efectivo)

**ID:** US-SP-057
**Epica:** EP-SP-015
**Prioridad:** P0

**Historia:**
Como **Usuario Final B2C** quiero depositar efectivo en un punto de pago autorizado para que el monto se acredite a mi cuenta digital y pueda usarlo para transferencias o pagos.

**Criterios de Aceptacion:**
- [ ] `POST /api/v1/organizations/{org_id}/cash/deposit`
  - Body: `{ point_id, user_account_id, amount, operator_user_id, idempotency_key }`
  - Requiere autenticacion del operador del punto
- [ ] Validaciones pre-deposito:
  - Punto de pago existe, esta ACTIVE, y dentro de horario operativo
  - Cuenta del usuario existe y esta ACTIVE
  - Monto > 0 y <= per_transaction_limit del punto
  - No excede daily_limit_cash_in del punto
  - No excede limite diario de depositos del usuario (si configurado)
- [ ] Flujo:
  1. Crear registro `CashTransaction` con status PENDING, type CASH_IN
  2. Generar referencia unica de operacion (8 caracteres alfanumericos)
  3. Crear asientos en ledger via TransactWriteItems:
     - DEBIT en cuenta de liquidacion del punto (el punto "recibe" un pasivo)
     - CREDIT en cuenta del usuario (se acredita el deposito)
  4. Si se configura comision:
     - DEBIT adicional en cuenta del usuario por comision
     - CREDIT en cuenta de comisiones de SuperPago
  5. Status -> COMPLETED
  6. Actualizar `cash_balance` del punto (+= amount)
  7. Notificar al usuario (deposito recibido)
- [ ] Response: `{ transaction_id, reference, amount, commission, net_amount, new_balance }`
- [ ] Generar comprobante digital (PDF o JSON) accesible via URL
- [ ] Idempotencia estricta

**Tareas Tecnicas:**
1. Crear modelo CashTransaction en DynamoDB
2. Crear CashService con flujo de Cash-In
3. Integracion con LedgerService para asientos
4. Generacion de referencia unica
5. Calculo de comision
6. Generacion de comprobante
7. Notificacion al usuario via covacha-notifications
8. Tests del flujo completo: happy path, limites, comision, idempotencia

**Dependencias:** US-SP-056, US-SP-011
**Estimacion:** 5 dev-days

---

#### US-SP-058: Flujo de Cash-Out (Retiro de Efectivo)

**ID:** US-SP-058
**Epica:** EP-SP-015
**Prioridad:** P0

**Historia:**
Como **Usuario Final B2C** quiero retirar efectivo en un punto de pago autorizado para convertir mi saldo digital en dinero fisico.

**Criterios de Aceptacion:**
- [ ] `POST /api/v1/organizations/{org_id}/cash/withdrawal`
  - Body: `{ point_id, user_account_id, amount, authorization_code, operator_user_id, idempotency_key }`
- [ ] Flujo previo (usuario solicita retiro desde app o WhatsApp):
  1. `POST /api/v1/organizations/{org_id}/cash/withdrawal/request`
     - Body: `{ user_account_id, amount, point_id? }`
     - Genera `authorization_code` (6 digitos, valido por 30 minutos)
     - Valida saldo suficiente
     - Crea hold en el saldo (DEBIT con status PENDING en ledger)
  2. Usuario muestra `authorization_code` al operador del punto
  3. Operador ejecuta el retiro con el authorization_code
- [ ] Validaciones del retiro:
  - `authorization_code` valido y no expirado
  - Punto de pago activo y con cash_balance suficiente
  - No excede daily_limit_cash_out del punto
  - Monto coincide con el de la solicitud
- [ ] Flujo de ejecucion:
  1. Confirmar entries PENDING -> CONFIRMED en ledger:
     - DEBIT en cuenta del usuario (se debita el retiro)
     - CREDIT en cuenta de liquidacion del punto (el punto "entrega" efectivo)
  2. Si comision: entries adicionales
  3. Actualizar cash_balance del punto (-= amount)
  4. Status -> COMPLETED
  5. Notificar al usuario
- [ ] Si authorization_code expira sin ejecutar: revertir hold (PENDING -> REVERSED)
- [ ] Comprobante digital generado

**Tareas Tecnicas:**
1. Crear flujo de solicitud de retiro con authorization_code
2. Crear flujo de ejecucion de retiro por operador
3. Logica de expiracion de authorization_code (TTL en DynamoDB)
4. Integracion con LedgerService (hold -> confirm/reverse)
5. Actualizacion de cash_balance del punto
6. Generacion de comprobante
7. Tests: solicitud, ejecucion, expiracion, saldo insuficiente, punto sin efectivo

**Dependencias:** US-SP-056, US-SP-057 (comparte CashTransaction model)
**Estimacion:** 5 dev-days

---

#### US-SP-059: Modelo de Transaccion Cash y API de Historial

**ID:** US-SP-059
**Epica:** EP-SP-015
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero un modelo unificado de transacciones cash con historial consultable para tener trazabilidad completa de depositos y retiros.

**Criterios de Aceptacion:**
- [ ] Modelo `CashTransaction` (si no se creo en US-SP-057, consolidar aqui):
  - `PK: ORG#{org_id}`, `SK: CASH_TXN#{transaction_id}`
  - `transaction_id`, `type`: CASH_IN | CASH_OUT
  - `point_id`, `user_account_id`, `amount`, `commission`
  - `authorization_code` (solo CASH_OUT)
  - `reference` (codigo de operacion)
  - `status`: PENDING | COMPLETED | FAILED | REVERSED | EXPIRED
  - `operator_user_id`
  - `receipt_url` (URL del comprobante)
  - `created_at`, `completed_at`, `expires_at`
- [ ] GSI `GSI-USER-CASH`: `PK: USER_ACCOUNT#{account_id}`, `SK: CASH_TXN#{created_at}` para historial por usuario
- [ ] GSI `GSI-POINT-CASH`: `PK: POINT#{point_id}`, `SK: CASH_TXN#{created_at}` para historial por punto
- [ ] `GET /api/v1/organizations/{org_id}/cash/transactions`
  - Filtros: type, status, point_id, user_account_id, from_date, to_date
  - Paginacion server-side
- [ ] `GET /api/v1/organizations/{org_id}/cash/transactions/{id}` - Detalle
- [ ] `GET /api/v1/admin/cash/summary` - Resumen global:
  - Total Cash-In del periodo, Total Cash-Out, neto
  - Por punto, por organizacion
  - Comisiones generadas

**Tareas Tecnicas:**
1. Consolidar modelo CashTransaction
2. Crear GSIs para consultas
3. Endpoints de historial con filtros y paginacion
4. Endpoint de resumen para admin
5. Tests de queries, filtros, y resumen

**Dependencias:** US-SP-057, US-SP-058
**Estimacion:** 3 dev-days

---

#### US-SP-060: Reconciliacion de Puntos de Pago

**ID:** US-SP-060
**Epica:** EP-SP-015
**Prioridad:** P1

**Historia:**
Como **Administrador SuperPago** quiero reconciliar el efectivo fisico de cada punto de pago contra su saldo digital para detectar discrepancias y fraude.

**Criterios de Aceptacion:**
- [ ] `POST /api/v1/admin/payment-points/{id}/reconcile`
  - Body: `{ physical_cash_counted, counted_by, counted_at }`
  - Compara `physical_cash_counted` vs `cash_balance` del sistema
  - Si coinciden: registro de reconciliacion exitosa
  - Si difieren: genera discrepancia con monto de diferencia
- [ ] Modelo `PointReconciliation`:
  - `point_id`, `expected_balance`, `actual_balance`, `difference`
  - `status`: MATCHED | DISCREPANCY_MINOR | DISCREPANCY_MAJOR
  - `resolution`: PENDING | ADJUSTED | INVESTIGATED | RESOLVED
- [ ] Umbral configurable: MINOR (< $1,000), MAJOR (>= $1,000)
- [ ] Alerta automatica para discrepancias MAJOR
- [ ] `GET /api/v1/admin/payment-points/{id}/reconciliations` - Historial
- [ ] Job diario que lista puntos sin reconciliacion en las ultimas 24h

**Tareas Tecnicas:**
1. Modelo PointReconciliation en DynamoDB
2. Endpoint de reconciliacion con logica de comparacion
3. Sistema de alertas para discrepancias
4. Job diario para detectar puntos sin reconciliar
5. Tests: coincide, discrepancia minor, discrepancia major

**Dependencias:** US-SP-056, US-SP-059
**Estimacion:** 3 dev-days

---

#### US-SP-061: Limites y Comisiones para Operaciones Cash

**ID:** US-SP-061
**Epica:** EP-SP-015
**Prioridad:** P1

**Historia:**
Como **Administrador SuperPago** quiero configurar limites y comisiones para operaciones de Cash-In/Cash-Out por punto, por organizacion, y por usuario para controlar el riesgo y generar ingresos.

**Criterios de Aceptacion:**
- [ ] Modelo de configuracion de limites Cash:
  - Por punto: `per_transaction_limit`, `daily_limit_cash_in`, `daily_limit_cash_out`
  - Por organizacion: `org_daily_cash_in_limit`, `org_daily_cash_out_limit`
  - Por usuario: `user_daily_cash_in_limit`, `user_daily_cash_out_limit`
  - Global: `global_per_transaction_max`, `global_daily_max`
- [ ] Jerarquia de limites: el mas restrictivo gana
  - Ej: punto permite $50K/dia, org permite $100K/dia, usuario permite $10K/dia -> limite efectivo: $10K/dia
- [ ] Comisiones configurables:
  - Por tipo (Cash-In / Cash-Out)
  - Fija o porcentual o ambas (ej: $15 + 1%)
  - Por rango de monto (escalonada)
  - Por punto (puntos premium pueden tener comision diferente)
- [ ] `GET /api/v1/organizations/{org_id}/cash/commission-preview`
  - Calcula comision sin ejecutar la operacion
- [ ] `PATCH /api/v1/admin/payment-points/{id}/limits` - Actualizar limites de punto
- [ ] Validacion de limites integrada en flujos de Cash-In y Cash-Out

**Tareas Tecnicas:**
1. Modelo de configuracion de limites Cash
2. Servicio de calculo de limites con jerarquia
3. Modelo de comisiones Cash (escalonada)
4. Servicio de calculo de comision
5. Endpoint de preview de comision
6. Integracion en CashService
7. Tests de jerarquia de limites y calculo de comisiones

**Dependencias:** US-SP-057, US-SP-058
**Estimacion:** 4 dev-days

---

### EP-SP-016: Subasta de Efectivo (Mercado de Liquidez)

---

#### US-SP-062: Modelo de Oferta de Efectivo (CashOffer)

**ID:** US-SP-062
**Epica:** EP-SP-016
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero un modelo para representar ofertas de efectivo en el mercado interno de liquidez para que los puntos de pago puedan publicar su exceso de efectivo y las empresas puedan comprarlo.

**Criterios de Aceptacion:**
- [x] Modelo `CashOffer` en DynamoDB:
  - `PK: MARKETPLACE`, `SK: OFFER#{offer_id}`
  - `offer_id` (UUID)
  - `point_id` (punto que ofrece el efectivo)
  - `point_organization_id` (org que opera el punto)
  - `amount` (monto de efectivo ofrecido)
  - `remaining_amount` (monto aun disponible, puede comprarse parcialmente)
  - `location` (direccion del punto, para que el comprador sepa donde retirar)
  - `coordinates` (lat/lng)
  - `status`: ACTIVE | PARTIALLY_SOLD | SOLD | EXPIRED | CANCELLED
  - `expires_at` (vigencia de la oferta, default 24h)
  - `commission_rate` (comision de SuperPago por la intermediacion)
  - `created_at`
- [x] GSI `GSI-OFFER-STATUS`: `PK: OFFER_STATUS#{status}`, `SK: #{created_at}` para listar activas
- [x] GSI `GSI-POINT-OFFERS`: `PK: POINT#{point_id}`, `SK: OFFER#{created_at}` para ofertas de un punto
- [x] Las ofertas se pueden crear manualmente o automaticamente cuando el cash_balance del punto supera un umbral
- [ ] Las ofertas expiran automaticamente (TTL o job)

**Tareas Tecnicas:**
1. Crear modelo CashOffer en DynamoDB con GSIs
2. Crear dataclass con validaciones
3. Logica de creacion automatica por umbral de cash_balance
4. Job/TTL de expiracion
5. Tests del modelo

**Dependencias:** US-SP-056
**Estimacion:** 3 dev-days

---

#### US-SP-063: Publicacion y Gestion de Ofertas

**ID:** US-SP-063
**Epica:** EP-SP-016
**Prioridad:** P0

**Historia:**
Como **Operador de Punto de Pago** quiero publicar ofertas de efectivo en el marketplace para que las empresas puedan comprar el exceso de efectivo de mi punto.

**Criterios de Aceptacion:**
- [x] `POST /api/v1/organizations/{org_id}/marketplace/offers`
  - Body: `{ point_id, amount, expires_in_hours? }`
  - Valida: punto pertenece a la org, cash_balance >= amount, punto esta activo
- [x] `GET /api/v1/marketplace/offers` (accesible por Tier 1 y Tier 2)
  - Filtros: location (radio en km, futuro), amount_min, amount_max, status
  - Ordena por: mas recientes, monto mayor, mas cercano (futuro)
  - Paginacion server-side
- [x] `GET /api/v1/marketplace/offers/{id}` - Detalle de oferta
- [x] `DELETE /api/v1/organizations/{org_id}/marketplace/offers/{id}` - Cancelar oferta
  - Solo si status == ACTIVE (no se puede cancelar si ya se vendio parcialmente con comprador en proceso)
- [ ] Auto-publicacion configurable:
  - `POST /api/v1/admin/payment-points/{id}/auto-offer`
  - Body: `{ threshold_amount, offer_amount, auto_publish: true }`
  - Cuando cash_balance > threshold, se publica oferta automaticamente

**Tareas Tecnicas:**
1. Endpoints CRUD de ofertas
2. Listado con filtros y paginacion
3. Logica de auto-publicacion
4. Validaciones de cash_balance
5. Tests de publicacion, cancelacion, auto-publish

**Dependencias:** US-SP-062
**Estimacion:** 4 dev-days

---

#### US-SP-064: Compra de Efectivo (Ejecucion de Subasta)

**ID:** US-SP-064
**Epica:** EP-SP-016
**Prioridad:** P0

**Historia:**
Como **Cliente Empresa B2B** quiero comprar efectivo del marketplace para obtener liquidez fisica en ubicaciones especificas donde la necesito.

**Criterios de Aceptacion:**
- [x] `POST /api/v1/organizations/{org_id}/marketplace/offers/{offer_id}/buy`
  - Body: `{ buyer_account_id, amount?, idempotency_key }`
  - `amount` es opcional: si no se especifica, compra todo el remaining_amount
  - Si se especifica: compra parcial (remaining_amount -= amount)
- [x] Flujo de compra:
  1. Validar: oferta activa, buyer_account tiene saldo suficiente
  2. Ejecutar transferencia inter-org (reutiliza US-SP-053):
     - DEBIT en cuenta del comprador
     - CREDIT en cuenta de liquidacion del punto
  3. Cobrar comision de SuperPago:
     - DEBIT adicional en cuenta del comprador por comision
     - CREDIT en cuenta de comisiones de SuperPago
  4. Generar `CashPickupTicket` (ticket de retiro):
     - `ticket_id`, `offer_id`, `buyer_org_id`, `point_id`
     - `amount`, `authorization_code` (para retirar)
     - `expires_at` (72h para retirar)
     - `status`: PENDING_PICKUP | PICKED_UP | EXPIRED
  5. Actualizar oferta: remaining_amount, status
  6. Notificar al punto (nueva venta) y al comprador (ticket generado)
- [x] Si remaining_amount == 0: status -> SOLD
- [x] Si remaining_amount > 0: status -> PARTIALLY_SOLD
- [x] Idempotencia estricta

**Tareas Tecnicas:**
1. Crear modelo CashPickupTicket en DynamoDB
2. Endpoint de compra con orquestacion
3. Reutilizar InterOrgTransferService para la transferencia
4. Generar authorization_code para retiro
5. Notificaciones a punto y comprador
6. Tests: compra total, compra parcial, saldo insuficiente, oferta expirada

**Dependencias:** US-SP-062, US-SP-063, US-SP-053
**Estimacion:** 5 dev-days

---

#### US-SP-065: Dashboard de Liquidez y Metricas de Marketplace

**ID:** US-SP-065
**Epica:** EP-SP-016
**Prioridad:** P1

**Historia:**
Como **Administrador SuperPago** quiero ver metricas del marketplace de efectivo para entender los patrones de liquidez de la red y optimizar la operacion.

**Criterios de Aceptacion:**
- [x] `GET /api/v1/admin/marketplace/dashboard`
  - Metricas:
    - Efectivo total en la red (suma de cash_balance de todos los puntos)
    - Ofertas activas (cantidad y monto total)
    - Ventas del periodo (cantidad, monto, comisiones)
    - Tickets pendientes de retiro
    - Tickets expirados (posible problema)
    - Puntos con exceso de efectivo (> umbral)
    - Puntos con deficit de efectivo (< umbral minimo)
  - Graficas:
    - Tendencia de efectivo en red ultimos 30 dias
    - Top 10 puntos por volumen
    - Distribucion geografica (futuro)
- [x] `GET /api/v1/admin/marketplace/tickets`
  - Lista de tickets con filtros: status, buyer_org, point, rango de fechas
- [x] `POST /api/v1/organizations/{org_id}/marketplace/tickets/{id}/confirm-pickup`
  - Operador del punto confirma que el comprador retiro el efectivo
  - Requiere authorization_code del ticket
  - Status -> PICKED_UP
  - Actualiza cash_balance del punto (-= amount)

**Tareas Tecnicas:**
1. Endpoint de dashboard con metricas agregadas
2. Endpoint de listado de tickets
3. Endpoint de confirmacion de retiro
4. Queries eficientes para metricas
5. Tests de metricas y confirmacion de retiro

**Dependencias:** US-SP-064
**Estimacion:** 4 dev-days

---

### EP-SP-017: Agente IA WhatsApp - Core (covacha-botia)

---

#### US-SP-066: Vinculacion de Cuenta SPEI con WhatsApp

**ID:** US-SP-066
**Epica:** EP-SP-017
**Prioridad:** P0

**Historia:**
Como **Usuario Final B2C** quiero vincular mi numero de WhatsApp con mi cuenta SPEI en SuperPago para poder operar mi cuenta via chat.

**Criterios de Aceptacion:**
- [ ] Flujo de vinculacion iniciado desde el portal (mf-sp Tier 3) o desde WhatsApp:
  **Desde portal:**
  1. Usuario va a configuracion -> "Vincular WhatsApp"
  2. Ingresa su numero de telefono
  3. `POST /api/v1/organizations/{org_id}/users/{user_id}/whatsapp/link`
  4. Sistema envia codigo OTP de 6 digitos al WhatsApp del usuario
  5. Usuario ingresa OTP en el portal
  6. `POST /api/v1/organizations/{org_id}/users/{user_id}/whatsapp/verify`
  7. Si OTP correcto: vinculacion exitosa, se guarda en perfil
  **Desde WhatsApp:**
  1. Usuario envia "Hola" al numero de WhatsApp del bot
  2. Bot responde: "Para vincular tu cuenta, necesito tu email y CLABE registrados"
  3. Usuario proporciona datos
  4. Sistema verifica que existe cuenta con esos datos
  5. Envia OTP al email registrado
  6. Usuario responde con OTP en WhatsApp
  7. Vinculacion exitosa
- [ ] Modelo `WhatsAppLink` en DynamoDB:
  - `PK: WA#{phone_number}`, `SK: LINK#{org_id}`
  - `phone_number`, `user_id`, `organization_id`, `account_id`
  - `status`: PENDING_VERIFICATION | ACTIVE | SUSPENDED | REVOKED
  - `linked_at`, `last_activity_at`
  - `pin_hash` (PIN de 4 digitos para 2FA, hasheado)
- [ ] Un numero de telefono puede estar vinculado a multiples organizaciones
- [ ] Endpoint para desvincular: `DELETE /api/v1/.../whatsapp/link`
- [ ] PIN de 4 digitos configurado durante la vinculacion (para confirmar operaciones)

**Tareas Tecnicas:**
1. Crear modelo WhatsAppLink en DynamoDB
2. Endpoints de vinculacion y verificacion
3. Generacion y validacion de OTP (TTL 5 minutos)
4. Flujo conversacional en covacha-botia para vinculacion desde WhatsApp
5. Hash seguro del PIN (bcrypt)
6. Tests de ambos flujos de vinculacion

**Dependencias:** US-SP-001 (cuentas), infraestructura de covacha-botia existente
**Estimacion:** 5 dev-days

---

#### US-SP-067: Consulta de Saldo via WhatsApp

**ID:** US-SP-067
**Epica:** EP-SP-017
**Prioridad:** P0

**Historia:**
Como **Usuario Final B2C** quiero consultar el saldo de mi cuenta enviando un mensaje de WhatsApp para no tener que abrir el portal cada vez.

**Criterios de Aceptacion:**
- [ ] Intents soportados (NLU):
  - "Cual es mi saldo"
  - "Cuanto tengo"
  - "Saldo"
  - "Cuanto dinero tengo en mi cuenta"
  - Variaciones con errores ortograficos comunes
- [ ] Flujo:
  1. Usuario envia mensaje con intent de saldo
  2. Bot identifica numero de WhatsApp -> busca WhatsAppLink activo
  3. Si no vinculado: "Tu numero no esta vinculado. Escribe VINCULAR para comenzar."
  4. Si vinculado a 1 org: consulta saldo directo
  5. Si vinculado a multiples orgs: "Tienes cuentas en: 1) SuperPago 2) Boxito. Cual quieres consultar?"
  6. Llama a `GET /api/v1/organizations/{org_id}/accounts/{account_id}/balance` (via API interna)
  7. Responde: "Tu saldo disponible es $X,XXX.XX MXN. Tu CLABE es 072180XXXXXXXX."
- [ ] No requiere PIN para consulta de saldo (es solo lectura)
- [ ] Rate limiting: max 10 consultas de saldo por hora por usuario
- [ ] Logging de cada consulta (audit trail)
- [ ] Tiempo de respuesta < 3 segundos

**Tareas Tecnicas:**
1. Crear intent handler para saldo en covacha-botia
2. Logica de lookup de WhatsAppLink por numero
3. Llamada a API de covacha-payment (saldo)
4. Formateo de respuesta amigable
5. Rate limiting por usuario
6. Tests con diferentes escenarios: vinculado, no vinculado, multi-org

**Dependencias:** US-SP-066, US-SP-005
**Estimacion:** 3 dev-days

---

#### US-SP-068: Transferencia SPEI via WhatsApp

**ID:** US-SP-068
**Epica:** EP-SP-017
**Prioridad:** P0

**Historia:**
Como **Usuario Final B2C** quiero hacer transferencias SPEI enviando un mensaje de WhatsApp para poder pagar o enviar dinero sin abrir el portal.

**Criterios de Aceptacion:**
- [ ] Intents soportados:
  - "Envia $500 a CLABE 072180001234567890"
  - "Transfiere 1000 pesos a 072180001234567890"
  - "Quiero hacer una transferencia"
  - "Enviar dinero"
- [ ] Flujo conversacional guiado:
  1. **Deteccion de intent**: Si el usuario ya incluyo monto y CLABE, ir a paso 4
  2. **Pedir CLABE** (si no la incluyo): "A que CLABE quieres enviar?"
  3. **Pedir monto** (si no lo incluyo): "Cuanto quieres enviar?"
  4. **Validacion**:
     - CLABE formato valido (18 digitos + checksum)
     - Saldo suficiente (monto + comision)
     - Dentro de limites
     - Auto-detectar banco por CLABE
  5. **Confirmacion**: "Vas a enviar $500.00 a CLABE 072180... (BBVA). Comision: $7.00. Total: $507.00. Escribe tu PIN para confirmar."
  6. **PIN (2FA)**: Usuario envia su PIN de 4 digitos
  7. **Ejecucion**: Llama a `POST /api/v1/organizations/{org_id}/transfers/spei-out`
  8. **Resultado**:
     - Exito: "Transferencia enviada. Clave de rastreo: ABC123. Tu nuevo saldo: $X,XXX.XX"
     - Error: "No se pudo enviar. [razon]. Tu saldo no fue afectado."
- [ ] PIN tiene 3 intentos maximos, luego se bloquea por 30 minutos
- [ ] Sesion conversacional con timeout de 5 minutos (si el usuario no responde, cancelar)
- [ ] Si hay beneficiarios guardados: "Quieres enviar a un contacto guardado? 1) Juan (BBVA) 2) Maria (Santander)"
- [ ] Audit trail completo de la conversacion y la operacion
- [ ] Rate limiting: max 5 transferencias por hora via WhatsApp

**Tareas Tecnicas:**
1. Crear intent handler para transferencia en covacha-botia
2. Implementar flujo conversacional con estado de sesion
3. Validacion de CLABE con checksum
4. Integracion con catalogo de participantes SPEI (banco por CLABE)
5. Validacion de PIN con rate limiting de intentos
6. Llamada a API de covacha-payment (SPEI out)
7. Manejo de timeout de sesion
8. Lookup de beneficiarios frecuentes
9. Tests de flujo completo: con datos completos, conversacional, PIN incorrecto, timeout

**Dependencias:** US-SP-066, US-SP-014, US-SP-009 (catalogo SPEI)
**Estimacion:** 6 dev-days

---

#### US-SP-069: Gestion de Sesiones Conversacionales

**ID:** US-SP-069
**Epica:** EP-SP-017
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero gestionar sesiones conversacionales del agente IA para mantener contexto durante flujos multi-paso (transferencias, pagos) y evitar conflictos entre conversaciones simultaneas.

**Criterios de Aceptacion:**
- [ ] Modelo `ConversationSession` en DynamoDB:
  - `PK: WA_SESSION#{phone_number}`, `SK: SESSION#{session_id}`
  - `session_id`, `phone_number`, `organization_id`
  - `current_flow`: NONE | TRANSFER | BILL_PAY | LINKING | CASH_OUT
  - `flow_state` (JSON con el estado actual del flujo):
    - Ej para transferencia: `{ step: "awaiting_pin", clabe: "072...", amount: 500, bank: "BBVA" }`
  - `created_at`, `last_activity_at`, `expires_at`
  - `pin_attempts` (contador de intentos de PIN en la sesion)
- [ ] TTL automatico: sesiones expiran despues de 5 minutos de inactividad
- [ ] Solo 1 sesion activa por numero de telefono
  - Si el usuario inicia un nuevo flujo mientras hay uno activo: "Tienes una transferencia en proceso. Quieres cancelarla e iniciar una nueva?"
- [ ] Al completar flujo: limpiar sesion
- [ ] Al fallar/cancelar: limpiar sesion y reversar cualquier hold
- [ ] Mensajes fuera de flujo (sin sesion activa): interpretacion libre (saldo, ayuda, etc.)
- [ ] Comando "cancelar" en cualquier momento cancela el flujo activo

**Tareas Tecnicas:**
1. Crear modelo ConversationSession en DynamoDB con TTL
2. Servicio de gestion de sesiones (create, update, expire, clear)
3. Middleware en handler de WhatsApp que inyecta sesion activa
4. Logica de conflicto (nuevo flujo vs sesion existente)
5. Comando "cancelar" universal
6. Tests de ciclo de vida de sesion, timeout, conflicto

**Dependencias:** US-SP-066
**Estimacion:** 4 dev-days

---

#### US-SP-070: Seguridad y Rate Limiting del Agente IA

**ID:** US-SP-070
**Epica:** EP-SP-017
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero aplicar medidas de seguridad robustas al agente IA de WhatsApp para prevenir fraude, abuso, y operaciones no autorizadas.

**Criterios de Aceptacion:**
- [ ] **Autenticacion**:
  - Solo numeros vinculados pueden operar (WhatsAppLink activo)
  - PIN de 4 digitos requerido para toda operacion que mueve dinero
  - PIN hasheado con bcrypt (nunca en texto plano)
  - 3 intentos de PIN fallidos -> bloqueo 30 minutos
  - 10 bloqueos en 24h -> suspension de la vinculacion (requiere re-vincular)
- [ ] **Rate limiting por usuario**:
  - Consultas de saldo: 10/hora
  - Transferencias: 5/hora, 20/dia
  - Pagos de servicios: 5/hora, 10/dia
  - Mensajes totales: 100/hora (anti-spam)
- [ ] **Rate limiting global**:
  - Total de operaciones financieras via WhatsApp: configurable por Admin
  - Circuit breaker: si tasa de error > 50% en 5 minutos, suspender operaciones y alertar
- [ ] **Montos**:
  - El agente hereda los limites de la organizacion/usuario
  - Limite adicional de seguridad para WhatsApp: max $10,000 por transferencia via chat (configurable)
  - Monto diario acumulado via WhatsApp: configurable
- [ ] **Logging y auditoria**:
  - Cada mensaje procesado se loggea (sin datos sensibles de PIN)
  - Cada operacion financiera se registra en audit trail con `channel: WHATSAPP`
  - Alertas para: multiples PINs fallidos, volumenes inusuales, horarios inusuales
- [ ] **Comandos de emergencia**:
  - "BLOQUEAR" -> suspende inmediatamente la vinculacion y congela operaciones
  - Notifica al equipo de seguridad

**Tareas Tecnicas:**
1. Implementar rate limiting con DynamoDB counters (sliding window)
2. Logica de bloqueo de PIN con escalacion
3. Circuit breaker para operaciones financieras
4. Limite de monto especifico para canal WhatsApp
5. Logging estructurado sin datos sensibles
6. Sistema de alertas para patrones sospechosos
7. Comando "BLOQUEAR" con notificacion
8. Tests de rate limiting, bloqueo de PIN, circuit breaker

**Dependencias:** US-SP-066, US-SP-068
**Estimacion:** 5 dev-days

---

### EP-SP-018: Agente IA WhatsApp - BillPay y Notificaciones

---

#### US-SP-071: Integracion con Agregador de BillPay

**ID:** US-SP-071
**Epica:** EP-SP-018
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero integrarme con un agregador de pago de servicios (BillPay) para que los usuarios puedan pagar luz, agua, telefono y otros servicios desde SuperPago.

**Criterios de Aceptacion:**
- [ ] Interface `BillPayProvider` (Strategy Pattern, similar a SPEIProvider):
  - `get_services() -> list[BillPayService]` (catalogo de servicios)
  - `get_balance(service_id, reference) -> BillPayBalance` (consultar adeudo)
  - `make_payment(service_id, reference, amount) -> BillPayResult` (pagar)
  - `get_payment_status(payment_id) -> BillPayStatus` (consultar estado)
- [ ] Implementacion concreta para al menos 1 agregador (Openpay Paynet, Arcus, o similar)
- [ ] Modelo `BillPayService`:
  - `service_id`, `name` (ej: "CFE Luz"), `category` (ELECTRICITY, WATER, PHONE, GAS, INTERNET)
  - `requires_reference`: boolean (numero de servicio/contrato)
  - `supports_balance_check`: boolean
  - `min_amount`, `max_amount`
- [ ] Modelo `BillPayTransaction`:
  - `PK: ORG#{org_id}`, `SK: BILLPAY_TXN#{txn_id}`
  - `service_id`, `service_name`, `reference` (numero de servicio)
  - `amount`, `commission`, `status`
  - `provider_payment_id`
  - `user_account_id` (cuenta que paga)
  - `channel`: PORTAL | WHATSAPP
- [ ] Asientos de ledger:
  - DEBIT en cuenta del usuario por monto + comision
  - CREDIT en cuenta de SuperPago por monto (para enviar al agregador)
  - CREDIT en cuenta de comisiones por comision
  - Nueva categoria: `BILL_PAY`
- [ ] Idempotencia y retry para pagos al agregador
- [ ] Catalogo de servicios cacheado (TTL 24h)

**Tareas Tecnicas:**
1. Definir interface BillPayProvider
2. Implementar driver concreto para agregador elegido
3. Modelos BillPayService y BillPayTransaction en DynamoDB
4. Integracion con LedgerService
5. Cache de catalogo de servicios
6. Tests con mocks del agregador

**Dependencias:** US-SP-011 (ledger), EP-SP-002 (patron de Strategy Pattern ya establecido)
**Estimacion:** 5 dev-days

---

#### US-SP-072: Pago de Servicios via WhatsApp

**ID:** US-SP-072
**Epica:** EP-SP-018
**Prioridad:** P0

**Historia:**
Como **Usuario Final B2C** quiero pagar mis servicios (luz, agua, telefono) enviando un mensaje de WhatsApp para no tener que ir a una tienda o abrir otro portal.

**Criterios de Aceptacion:**
- [ ] Intents soportados:
  - "Paga mi recibo de luz"
  - "Quiero pagar CFE"
  - "Pagar servicio"
  - "Paga mi telefono Telmex"
- [ ] Flujo conversacional guiado:
  1. **Deteccion de servicio**: Si menciona servicio especifico (CFE, Telmex), ir al paso 3
  2. **Seleccion de servicio**: "Que servicio quieres pagar? 1) Luz (CFE) 2) Agua 3) Telefono (Telmex) 4) Gas 5) Internet 6) Otro"
  3. **Referencia**: "Cual es tu numero de servicio/contrato de [servicio]?"
  4. **Consulta de adeudo** (si soportado): "Tu adeudo de CFE es $850.00. Quieres pagar el total?"
     - Si no soporta consulta: "Cuanto quieres pagar?"
  5. **Confirmacion**: "Vas a pagar $850.00 a CFE (contrato #123456). Comision: $10.00. Total: $860.00. Escribe tu PIN para confirmar."
  6. **PIN (2FA)**: Validacion de PIN
  7. **Ejecucion**: Llama al BillPayProvider
  8. **Resultado**:
     - Exito: "Pago realizado. Folio: ABC123. Tu nuevo saldo: $X,XXX.XX"
     - Error: "No se pudo procesar el pago. [razon]"
- [ ] Enviar comprobante como imagen o PDF por WhatsApp
- [ ] Guardar referencia para pagos recurrentes: "La proxima vez puedes decir 'paga mi luz' y usare el mismo contrato"

**Tareas Tecnicas:**
1. Crear intent handler para BillPay en covacha-botia
2. Flujo conversacional con seleccion de servicio
3. Integracion con BillPayProvider (consulta adeudo + pago)
4. Integracion con LedgerService (asientos)
5. Generacion de comprobante (PDF/imagen)
6. Almacenamiento de referencias recurrentes
7. Tests del flujo completo

**Dependencias:** US-SP-071, US-SP-069 (sesiones), US-SP-070 (seguridad)
**Estimacion:** 5 dev-days

---

#### US-SP-073: Notificaciones Proactivas via WhatsApp

**ID:** US-SP-073
**Epica:** EP-SP-018
**Prioridad:** P1

**Historia:**
Como **Usuario Final B2C** quiero recibir notificaciones en mi WhatsApp cuando recibo un deposito, se completa una transferencia, o hay una alerta de seguridad para estar informado en tiempo real.

**Criterios de Aceptacion:**
- [ ] Tipos de notificacion:
  - **Deposito recibido**: "Recibiste $X,XXX.XX de [banco origen] - [concepto]. Tu nuevo saldo: $Y,YYY.YY"
  - **Transferencia completada**: "Tu transferencia de $X a [banco destino] fue exitosa. Clave de rastreo: ABC123"
  - **Transferencia fallida**: "Tu transferencia de $X fallo. Razon: [motivo]. Tu saldo fue restaurado."
  - **Cash-In confirmado**: "Tu deposito de $X en [punto] fue acreditado. Nuevo saldo: $Y"
  - **Pago de servicio confirmado**: "Tu pago de $X a [servicio] fue procesado. Folio: ABC123"
  - **Alerta de seguridad**: "Se intento acceder a tu cuenta desde un nuevo dispositivo. Si no fuiste tu, escribe BLOQUEAR"
  - **Saldo bajo** (configurable): "Tu saldo bajo de $X. Saldo actual: $Y"
- [ ] Trigger: Eventos de covacha-webhook y covacha-payment publican a SQS
  - Consumer en covacha-botia lee eventos y envia mensajes de WhatsApp
- [ ] Configuracion por usuario:
  - `PATCH /api/v1/organizations/{org_id}/users/{user_id}/whatsapp/notifications`
  - Body: `{ deposit_received: true, transfer_completed: true, security_alerts: true, low_balance: { enabled: true, threshold: 1000 } }`
- [ ] Solo se envian a usuarios con WhatsAppLink activo
- [ ] Respetan horarios (no enviar de 10pm a 7am, configurable)
- [ ] Rate limiting: max 20 notificaciones por dia por usuario (prevenir spam)
- [ ] Usa templates de WhatsApp Business API (pre-aprobados por Meta)

**Tareas Tecnicas:**
1. Crear consumer SQS en covacha-botia para eventos financieros
2. Mapear eventos a templates de notificacion
3. Modelo de preferencias de notificacion por usuario
4. Logica de horarios permitidos
5. Templates de WhatsApp Business API
6. Rate limiting de notificaciones
7. Tests de cada tipo de notificacion, horarios, rate limiting

**Dependencias:** US-SP-066, US-SP-019 (webhook events), US-SP-020 (status updates)
**Estimacion:** 5 dev-days

---

#### US-SP-074: Pago de Servicios via Portal (API REST)

**ID:** US-SP-074
**Epica:** EP-SP-018
**Prioridad:** P1

**Historia:**
Como **Usuario Final B2C** quiero pagar servicios desde el portal web (mf-sp Tier 3) ademas de WhatsApp para tener multiples canales de pago.

**Criterios de Aceptacion:**
- [ ] `GET /api/v1/organizations/{org_id}/billpay/services` - Catalogo de servicios
- [ ] `POST /api/v1/organizations/{org_id}/billpay/balance-check`
  - Body: `{ service_id, reference }`
  - Response: `{ amount_due, due_date, service_name, reference }`
- [ ] `POST /api/v1/organizations/{org_id}/billpay/pay`
  - Body: `{ service_id, reference, amount, user_account_id, idempotency_key }`
  - Response: `{ transaction_id, status, receipt_url, new_balance }`
- [ ] `GET /api/v1/organizations/{org_id}/billpay/transactions` - Historial de pagos
  - Filtros: service_id, status, from_date, to_date
- [ ] `GET /api/v1/organizations/{org_id}/billpay/saved-references` - Referencias guardadas
- [ ] `POST /api/v1/organizations/{org_id}/billpay/saved-references` - Guardar referencia
- [ ] Todos los endpoints validan sp_organization_id y scoping por usuario
- [ ] Las transacciones BillPay aparecen en el historial general de movimientos

**Tareas Tecnicas:**
1. Endpoints REST para catalogo, consulta, pago, historial
2. Integracion con BillPayProvider
3. Modelo de referencias guardadas
4. Integracion con LedgerService
5. Tests de cada endpoint

**Dependencias:** US-SP-071
**Estimacion:** 4 dev-days

---

### EP-SP-019: Reglas de Integridad de Datos (Cross-cutting)

---

#### US-SP-075: sp_organization_id Obligatorio en Toda Operacion

**ID:** US-SP-075
**Epica:** EP-SP-019
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero que `sp_organization_id` sea obligatorio en toda tabla y toda operacion para garantizar aislamiento de datos entre organizaciones y prevenir fugas de informacion.

**Criterios de Aceptacion:**
- [ ] Middleware Flask que valida `X-SP-Organization-Id` header en TODA request:
  - Si falta: retorna 400 `{"error": "X-SP-Organization-Id header is required"}`
  - Si presente: lo inyecta en el contexto de la request (`g.sp_organization_id`)
  - Excepciones: endpoints publicos (health check, webhook de Monato con su propia auth)
- [ ] Toda tabla DynamoDB incluye `organization_id` como parte del PK o como atributo obligatorio:
  - FinancialAccount: PK incluye ORG#{org_id} (ya cumple)
  - LedgerEntry: agregar `organization_id` como atributo requerido
  - Transfer: agregar `organization_id` como atributo requerido
  - CashTransaction: agregar organization_id
  - BillPayTransaction: agregar organization_id
  - InterOrgTransfer: tiene source y dest org
- [ ] Toda query incluye filtro por organization_id (no se puede leer datos de otra org)
- [ ] Validacion en repository layer: rechazar operaciones sin org_id
- [ ] Test de penetracion: intentar acceder a datos de org A con header de org B -> debe fallar
- [ ] Documentacion de regla para desarrolladores

**Tareas Tecnicas:**
1. Crear middleware Flask de validacion de org_id
2. Auditar todas las tablas y agregar org_id donde falte
3. Auditar todos los queries y agregar filtro por org_id
4. Validacion en cada repository
5. Tests de aislamiento: cross-org access debe fallar

**Dependencias:** Ninguna (comenzar en Sprint 1)
**Estimacion:** 4 dev-days

---

#### US-SP-076: Tabla de Idempotencia Dedicada

**ID:** US-SP-076
**Epica:** EP-SP-019
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero una tabla de idempotencia centralizada para garantizar que ninguna operacion mutativa se ejecute mas de una vez, incluso ante reintentos o fallos de red.

**Criterios de Aceptacion:**
- [ ] Tabla `IdempotencyKeys` en DynamoDB:
  - `PK: IDEM#{idempotency_key}`
  - `SK: ORG#{org_id}`
  - `operation_type`: SPEI_OUT | INTERNAL_TRANSFER | INTER_ORG | CASH_IN | CASH_OUT | BILL_PAY | etc.
  - `request_hash` (hash del body para detectar misma key con diferente payload)
  - `response` (resultado de la operacion original, serializado)
  - `status`: PROCESSING | COMPLETED | FAILED
  - `created_at`
  - TTL: 48 horas (configurable)
- [ ] Flujo de idempotencia:
  1. Antes de ejecutar: buscar key en tabla
  2. Si existe y status COMPLETED: retornar response guardado (no re-ejecutar)
  3. Si existe y status PROCESSING: retornar 409 Conflict "Operation in progress"
  4. Si existe y request_hash diferente: retornar 422 "Idempotency key reused with different payload"
  5. Si no existe: crear registro con status PROCESSING, ejecutar operacion, actualizar a COMPLETED/FAILED
- [ ] Toda operacion mutativa REQUIERE `idempotency_key` en el body
  - Si falta: retornar 400 "idempotency_key is required"
- [ ] Decorator `@idempotent` para aplicar en endpoints de forma declarativa
- [ ] TTL configurable por tipo de operacion

**Tareas Tecnicas:**
1. Crear tabla IdempotencyKeys en DynamoDB con TTL
2. Crear servicio IdempotencyService con logica de check/create/update
3. Crear decorator @idempotent para Flask
4. Aplicar decorator a todos los endpoints mutativos existentes y nuevos
5. Tests: primera ejecucion, retry, key reutilizada con payload diferente, PROCESSING conflict

**Dependencias:** Ninguna (comenzar en Sprint 1)
**Estimacion:** 4 dev-days

---

#### US-SP-077: Prevencion de Double-Spending con Locks Optimistas

**ID:** US-SP-077
**Epica:** EP-SP-019
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero prevenir double-spending (gastar el mismo saldo dos veces) usando locks optimistas en DynamoDB para garantizar consistencia financiera bajo concurrencia.

**Criterios de Aceptacion:**
- [ ] Cada cuenta tiene un campo `balance_version` (numero secuencial)
- [ ] Al calcular saldo y ejecutar operacion:
  1. Leer saldo actual + balance_version
  2. Validar que saldo >= monto + comision
  3. Crear entries en ledger CON ConditionExpression:
     ```python
     ConditionExpression = "balance_version = :expected_version"
     UpdateExpression = "SET balance_version = balance_version + :one"
     ```
  4. Si la condition falla (otro proceso modifico el saldo): retry con backoff
  5. Max 3 retries, luego retornar error "Concurrent operation, please retry"
- [ ] TransactWriteItems para operaciones multi-entry:
  - Usar DynamoDB Transactions para que DEBIT y CREDIT se creen atomicamente
  - Si alguna condicion falla: toda la transaccion se revierte
- [ ] ConditionExpression adicional para prevenir saldo negativo:
  ```python
  # Antes de DEBIT, verificar que el saldo resultante no sera negativo
  # Esto se implementa como version check + validacion previa
  ```
- [ ] Test de concurrencia:
  - Simular N threads ejecutando transferencias simultaneas desde la misma cuenta
  - Verificar que el saldo final es consistente
  - Verificar que no hay entries fantasma

**Tareas Tecnicas:**
1. Agregar campo balance_version a FinancialAccount
2. Modificar LedgerService para usar ConditionExpression
3. Implementar retry con backoff exponencial
4. Usar TransactWriteItems para atomicidad
5. Tests de concurrencia con threading/asyncio
6. Benchmark de performance bajo concurrencia

**Dependencias:** US-SP-001, US-SP-011
**Estimacion:** 5 dev-days

---

#### US-SP-078: Validacion de Integridad en Transacciones DynamoDB

**ID:** US-SP-078
**Epica:** EP-SP-019
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero usar DynamoDB TransactWriteItems con ConditionExpressions en todas las operaciones financieras para garantizar atomicidad y consistencia.

**Criterios de Aceptacion:**
- [ ] Toda operacion que modifica saldo usa `TransactWriteItems`:
  - SPEI Out: crear Transfer + DEBIT entry + CREDIT entry + comision entries (4 writes atomicos)
  - Internal Transfer: DEBIT + CREDIT (2 writes atomicos)
  - Cash-In: CashTransaction + DEBIT punto + CREDIT usuario (3+ writes)
  - Cash-Out: CashTransaction + DEBIT usuario + CREDIT punto (3+ writes)
  - BillPay: BillPayTransaction + DEBIT usuario + CREDIT SuperPago (3+ writes)
- [ ] Limite de DynamoDB: max 100 items por TransactWriteItems
  - Dispersion masiva (EP-SP-006) con >50 destinos: dividir en batches de 50 con compensacion
- [ ] ConditionExpressions aplicadas:
  - Cuenta existe y esta ACTIVE
  - Balance version matches (optimistic lock)
  - Entry no existe (prevenir duplicados)
  - Idempotency key no esta PROCESSING
- [ ] Si TransactWriteItems falla:
  - Log detallado de cual condicion fallo
  - Error message descriptivo al caller
  - No se ejecuta ninguna de las operaciones del batch (atomicidad)
- [ ] Metricas: tasa de TransactWriteItems fallidos por ConditionCheckFailure

**Tareas Tecnicas:**
1. Refactorizar LedgerService para usar TransactWriteItems en todas las operaciones
2. Agregar ConditionExpressions a cada tipo de operacion
3. Manejo de errores de TransactWriteItems
4. Metricas de fallos por condicion
5. Tests de atomicidad: forzar fallos y verificar que no hay escrituras parciales
6. Tests de cada ConditionExpression

**Dependencias:** US-SP-077
**Estimacion:** 5 dev-days

---

#### US-SP-079: Audit Trail de Integridad y Alertas de Anomalias

**ID:** US-SP-079
**Epica:** EP-SP-019
**Prioridad:** P1

**Historia:**
Como **Administrador SuperPago** quiero un sistema de deteccion de anomalias de integridad para identificar inmediatamente situaciones como saldos negativos, transacciones huerfanas, o desbalances contables.

**Criterios de Aceptacion:**
- [ ] Job periodico (cada 5 minutos) que verifica:
  - Ninguna cuenta tiene saldo negativo (SUM credits - SUM debits >= 0)
  - Balance trial: SUM(todos los debits) == SUM(todos los credits) globalmente
  - No hay entries con status PENDING por mas de 1 hora (posible transaccion colgada)
  - No hay TransactWriteItems con condicion fallida sin retry exitoso
- [ ] Si detecta anomalia:
  - Crear registro `IntegrityAlert` en DynamoDB
  - Enviar notificacion a Slack/email del equipo de operaciones
  - Log critico (nivel CRITICAL)
- [ ] Modelo `IntegrityAlert`:
  - `alert_type`: NEGATIVE_BALANCE | BALANCE_TRIAL_MISMATCH | STALE_PENDING | ORPHAN_ENTRY
  - `severity`: CRITICAL | HIGH | MEDIUM
  - `details` (JSON con informacion de la anomalia)
  - `status`: ACTIVE | INVESTIGATING | RESOLVED
  - `resolved_by`, `resolved_at`, `resolution_notes`
- [ ] `GET /api/v1/admin/integrity/alerts` - Listar alertas con filtros
- [ ] `PATCH /api/v1/admin/integrity/alerts/{id}` - Actualizar estado de alerta
- [ ] Dashboard de integridad (se integra en mf-sp Admin):
  - Status actual: verde (todo ok) / rojo (hay alertas activas)
  - Historial de alertas
  - Tiempo desde ultima verificacion
  - Balance trial result

**Tareas Tecnicas:**
1. Crear job de verificacion de integridad (Lambda o cron)
2. Implementar cada tipo de check
3. Modelo IntegrityAlert en DynamoDB
4. Sistema de notificaciones (Slack + email)
5. Endpoints de gestion de alertas
6. Tests de cada tipo de anomalia

**Dependencias:** US-SP-075, US-SP-077, US-SP-013 (balance trial)
**Estimacion:** 5 dev-days

---

### EP-SP-020: mf-sp - Pantallas de Cash, Subasta y Config IA

---

#### US-SP-080: Pantallas de Gestion de Puntos de Pago (Admin Tier 1)

**ID:** US-SP-080
**Epica:** EP-SP-020
**Prioridad:** P1

**Historia:**
Como **Administrador SuperPago** quiero gestionar los puntos de pago de la red desde el portal para registrar, monitorear, y reconciliar puntos fisicos.

**Criterios de Aceptacion:**
- [ ] Nuevas rutas en Tier 1 Admin:
  - `/sp/admin/payment-points` - Lista de puntos
  - `/sp/admin/payment-points/new` - Registrar punto
  - `/sp/admin/payment-points/:id` - Detalle de punto
  - `/sp/admin/payment-points/:id/reconcile` - Reconciliar punto
- [ ] Pagina de lista:
  - Tabla: nombre, direccion, cash_balance, status, org operadora, ultimo reconciliacion
  - Filtros: status, organizacion, rango de cash_balance
  - Busqueda por nombre
  - Badge rojo si cash_balance > umbral (exceso de efectivo)
  - Badge amarillo si sin reconciliacion en 24h+
- [ ] Pagina de detalle:
  - Info del punto (nombre, direccion, limites, comisiones, horarios)
  - Cash balance con grafica de tendencia (ultimos 30 dias)
  - Historial de transacciones Cash-In/Cash-Out del punto
  - Historial de reconciliaciones
  - Acciones: suspender, reactivar, modificar limites
- [ ] Formulario de registro de punto
- [ ] Formulario de reconciliacion: ingresar efectivo contado, comparar con sistema
- [ ] Componentes reutilizables con OnPush + Signals
- [ ] Tests >= 98%

**Tareas Tecnicas:**
1. Crear `PaymentPointsListComponent` (page)
2. Crear `PaymentPointDetailComponent` (page)
3. Crear `PaymentPointFormComponent` (formulario de registro)
4. Crear `ReconcileFormComponent` (formulario de reconciliacion)
5. Crear `PaymentPointsAdapter` en infrastructure/adapters
6. Integrar en routing de AdminLayout
7. Tests

**Dependencias:** US-SP-025 (scaffold), US-SP-026 (routing), EP-SP-015 (API de puntos)
**Estimacion:** 5 dev-days

---

#### US-SP-081: Historial de Operaciones Cash (Admin + Business)

**ID:** US-SP-081
**Epica:** EP-SP-020
**Prioridad:** P1

**Historia:**
Como **Administrador SuperPago** y como **Cliente Empresa** quiero ver el historial de operaciones Cash-In/Cash-Out para monitorear la actividad de efectivo.

**Criterios de Aceptacion:**
- [ ] Nuevas rutas:
  - Admin: `/sp/admin/cash/transactions` (ve todas las orgs)
  - Business: `/sp/business/cash/transactions` (ve solo su org)
- [ ] Reutiliza `MovementsTableComponent` de EP-SP-013 con columnas adicionales:
  - Tipo (CASH_IN / CASH_OUT)
  - Punto de pago
  - Operador
  - Referencia de operacion
  - Comision
- [ ] Filtros: tipo, punto, rango de fechas, monto, status
- [ ] Paginacion server-side
- [ ] Click en transaccion -> detalle con comprobante
- [ ] Resumen del periodo: total cash-in, total cash-out, comisiones, neto
- [ ] Export CSV
- [ ] Tests >= 98%

**Tareas Tecnicas:**
1. Crear `CashTransactionsPageComponent` (page, reutilizable Admin + Business)
2. Crear `CashTransactionsAdapter`
3. Extender MovementsTableComponent para columnas Cash (o crear wrapper)
4. Integrar en routing de ambos tiers
5. Tests

**Dependencias:** US-SP-047 (MovementsTableComponent), EP-SP-015 (API cash)
**Estimacion:** 3 dev-days

---

#### US-SP-082: Marketplace de Subasta de Efectivo (Admin + Business)

**ID:** US-SP-082
**Epica:** EP-SP-020
**Prioridad:** P2

**Historia:**
Como **Cliente Empresa** quiero ver las ofertas de efectivo disponibles en el marketplace y comprar efectivo para obtener liquidez fisica donde la necesito.

**Criterios de Aceptacion:**
- [ ] Nuevas rutas:
  - Admin: `/sp/admin/marketplace` (ve todo + dashboard de liquidez)
  - Business: `/sp/business/marketplace` (ve ofertas y puede comprar)
- [ ] Pagina de marketplace (Business):
  - Lista de ofertas activas con: monto, ubicacion, punto, vigencia restante
  - Filtros: rango de monto, ubicacion (futuro: radio km)
  - Click en oferta -> detalle con mapa (futuro), monto, comision estimada
  - Boton "Comprar" con confirmacion (monto, comision, cuenta origen)
  - Mis compras: lista de tickets de retiro pendientes/completados
- [ ] Dashboard de liquidez (Admin):
  - Efectivo total en la red
  - Ofertas activas (cantidad, monto total)
  - Tickets pendientes de retiro
  - Graficas de tendencia
  - Top puntos por exceso de efectivo
- [ ] Componentes OnPush + Signals
- [ ] Tests >= 98%

**Tareas Tecnicas:**
1. Crear `MarketplacePageComponent` (Business)
2. Crear `MarketplaceDashboardComponent` (Admin)
3. Crear `OfferCardComponent`
4. Crear `BuyOfferModalComponent`
5. Crear `PickupTicketsListComponent`
6. Crear `MarketplaceAdapter`
7. Integrar en routing de ambos tiers
8. Tests

**Dependencias:** US-SP-025 (scaffold), EP-SP-016 (API marketplace)
**Estimacion:** 5 dev-days

---

#### US-SP-083: Configuracion del Agente IA WhatsApp por Organizacion

**ID:** US-SP-083
**Epica:** EP-SP-020
**Prioridad:** P1

**Historia:**
Como **Administrador SuperPago** y como **Cliente Empresa** quiero configurar el agente IA de WhatsApp para mi organizacion para controlar que operaciones estan habilitadas, limites, y comportamiento del bot.

**Criterios de Aceptacion:**
- [ ] Nuevas rutas:
  - Admin: `/sp/admin/whatsapp-agent` (configuracion global + por org)
  - Business: `/sp/business/settings/whatsapp` (configuracion de mi org)
- [ ] Configuracion por organizacion:
  - **Habilitado**: si/no (activar/desactivar agente para la org)
  - **Operaciones permitidas**:
    - Consulta de saldo: si/no
    - Transferencia SPEI: si/no
    - Pago de servicios: si/no
    - Cash-Out request: si/no
  - **Limites via WhatsApp**:
    - Monto maximo por transferencia via WhatsApp
    - Monto maximo diario via WhatsApp
    - Numero maximo de operaciones por dia
  - **Notificaciones**:
    - Depositos recibidos: si/no
    - Transferencias completadas: si/no
    - Alertas de seguridad: si/no (siempre si por defecto)
    - Horario de notificaciones: desde-hasta
  - **Mensaje de bienvenida personalizado** (texto libre)
  - **Numero de WhatsApp del bot** (configurado por Admin, read-only para Business)
- [ ] Admin ve configuracion de TODAS las organizaciones en una tabla
- [ ] Business solo ve y edita la configuracion de SU organizacion
- [ ] `POST /api/v1/organizations/{org_id}/whatsapp-agent/config` - Guardar config
- [ ] `GET /api/v1/organizations/{org_id}/whatsapp-agent/config` - Obtener config
- [ ] Tests >= 98%

**Tareas Tecnicas:**
1. Crear `WhatsAppAgentConfigComponent` (page, reutilizable Admin + Business)
2. Crear `AgentConfigFormComponent` (formulario con tabs)
3. Crear `WhatsAppAgentAdapter`
4. Integrar en routing de ambos tiers
5. Tests

**Dependencias:** US-SP-025, EP-SP-017 (API agente)
**Estimacion:** 4 dev-days

---

#### US-SP-084: Dashboard de Operaciones del Agente IA (Admin)

**ID:** US-SP-084
**Epica:** EP-SP-020
**Prioridad:** P2

**Historia:**
Como **Administrador SuperPago** quiero ver metricas de uso del agente IA de WhatsApp para entender la adopcion, detectar problemas, y optimizar el servicio.

**Criterios de Aceptacion:**
- [ ] Nueva ruta: `/sp/admin/whatsapp-agent/dashboard`
- [ ] Metricas:
  - Usuarios vinculados (total, nuevos esta semana/mes)
  - Operaciones hoy/semana/mes por tipo (saldo, transferencia, BillPay)
  - Volumen monetario procesado via WhatsApp (monto total)
  - Tasa de exito de operaciones (% completadas vs fallidas)
  - Tiempo promedio de respuesta del bot
  - Sesiones activas en este momento
  - Errores y fallos (ultimas 24h)
  - PINs bloqueados (posible fraude)
  - Rate limiting triggers (usuarios que chocan con limites)
- [ ] Graficas:
  - Volumen de operaciones ultimos 30 dias (linea)
  - Distribucion por tipo de operacion (dona)
  - Horas pico de uso (heatmap)
  - Top 10 usuarios por volumen
- [ ] Tabla de conversaciones recientes (auditoria):
  - Usuario (phone number parcial), timestamp, tipo de operacion, resultado
  - Click para ver detalle de la conversacion
- [ ] Auto-refresh cada 60 segundos
- [ ] Tests >= 98%

**Tareas Tecnicas:**
1. Crear `WhatsAppAgentDashboardComponent` (page)
2. Crear `AgentKpisComponent`
3. Crear `AgentOperationsChartComponent`
4. Crear `AgentUsageHeatmapComponent`
5. Crear `AgentConversationsTableComponent`
6. Crear `AgentDashboardAdapter`
7. Tests

**Dependencias:** US-SP-083, EP-SP-017 (API metricas del agente)
**Estimacion:** 4 dev-days

---

## Roadmap de Expansion

### Fase 1: Fundamentos (Sprint 1-2, paralela al plan SPEI original)

| Sprint | Epica | User Stories | Dev-Days |
|--------|-------|-------------|----------|
| 1-2 | EP-SP-019 (Integridad) | US-SP-075, US-SP-076, US-SP-077, US-SP-078 | 18 |

**Razonamiento:** Las reglas de integridad se implementan en PARALELO con EP-SP-001 a EP-SP-003 porque son cross-cutting y deben estar listas ANTES de que las demas epicas generen transacciones financieras reales.

### Fase 2: Transferencias Inter-Org (Sprint 4-5)

| Sprint | Epica | User Stories | Dev-Days |
|--------|-------|-------------|----------|
| 4-5 | EP-SP-014 (Inter-Org) | US-SP-052, US-SP-053, US-SP-054, US-SP-055 | 13 |

**Razonamiento:** Depende de que el Account Engine (EP-SP-001), Ledger (EP-SP-003), y Movimientos Internos (EP-SP-006) esten implementados. Es la base para la subasta de efectivo.

### Fase 3: Cash-In/Cash-Out + Agente IA (Sprint 5-7)

| Sprint | Epica | User Stories | Dev-Days |
|--------|-------|-------------|----------|
| 5-7 | EP-SP-015 (Cash) | US-SP-056-061 | 24 |
| 5-7 | EP-SP-017 (Agente IA Core) | US-SP-066-070 | 23 |
| 5-7 | EP-SP-019 cont. (Alertas) | US-SP-079 | 5 |

**Razonamiento:** Cash y Agente IA son independientes entre si y pueden desarrollarse en paralelo por equipos diferentes. Ambos dependen del core financiero ya implementado.

### Fase 4: Subasta + BillPay + Frontend (Sprint 7-9)

| Sprint | Epica | User Stories | Dev-Days |
|--------|-------|-------------|----------|
| 7-8 | EP-SP-016 (Subasta) | US-SP-062-065 | 16 |
| 7-8 | EP-SP-018 (BillPay + Notif) | US-SP-071-074 | 19 |
| 7-9 | EP-SP-020 (Frontend Cash/Subasta/IA) | US-SP-080-084 | 21 |

**Razonamiento:** La subasta requiere Cash (EP-SP-015) e Inter-Org (EP-SP-014). BillPay requiere el agente IA core (EP-SP-017). El frontend se construye cuando las APIs estan listas.

### Resumen de Estimaciones

| Epica | User Stories | Dev-Days | Sprint |
|-------|-------------|----------|--------|
| EP-SP-014 | 4 (US-SP-052 a 055) | 13 | 4-5 |
| EP-SP-015 | 6 (US-SP-056 a 061) | 24 | 5-7 |
| EP-SP-016 | 4 (US-SP-062 a 065) | 16 | 7-8 |
| EP-SP-017 | 5 (US-SP-066 a 070) | 23 | 5-7 |
| EP-SP-018 | 4 (US-SP-071 a 074) | 19 | 7-8 |
| EP-SP-019 | 5 (US-SP-075 a 079) | 23 | 1-2 (paralela) |
| EP-SP-020 | 5 (US-SP-080 a 084) | 21 | 7-9 |
| **TOTAL** | **33** | **139** | - |

---

## Grafo de Dependencias

```
EP-SP-019 (Integridad) ─────────────────────────────────────── Se aplica a TODO
     |
     v
EP-SP-001 (Account) ──+──> EP-SP-014 (Inter-Org) ──+
EP-SP-003 (Ledger) ───+                             |
EP-SP-006 (Internos) ─+                             |
                                                     |
EP-SP-010 (Limites) ──+──> EP-SP-015 (Cash) ────────+──> EP-SP-016 (Subasta)
EP-SP-001 (Account) ──+                             |
EP-SP-003 (Ledger) ───+                             |
                                                     |
EP-SP-004 (SPEI Out) ─+──> EP-SP-017 (Agente IA) ──+──> EP-SP-018 (BillPay)
EP-SP-005 (SPEI In) ──+                                      |
EP-SP-001 (Account) ──+                                      |
                                                              |
EP-SP-007 (Scaffold) ─+──> EP-SP-020 (Frontend Expansion) <──+
EP-SP-013 (Shared) ───+          (depende de APIs de 015, 016, 017, 018)
```

---

## Riesgos y Mitigaciones

### R1: Complejidad de Integracion con Agregador BillPay

**Riesgo:** Los agregadores de pago de servicios (Openpay, Arcus) tienen APIs variables en calidad y documentacion. La integracion puede tomar mas tiempo del esperado.

**Mitigacion:**
- Comenzar con 1 solo agregador (el mejor documentado)
- Interface abstracta (BillPayProvider) permite cambiar sin impacto
- Limitar catalogo inicial a 5 servicios (CFE, Telmex, Agua, Gas, Internet)
- Tener plan B: si el agregador falla, desactivar BillPay sin afectar transferencias

### R2: Seguridad del Agente IA WhatsApp

**Riesgo:** El canal WhatsApp es inherentemente menos seguro que el portal web. Un telefono robado o SIM swap podria dar acceso a la cuenta.

**Mitigacion:**
- PIN obligatorio para toda operacion financiera
- Limites de monto reducidos para canal WhatsApp (configurable)
- Comando "BLOQUEAR" para emergencias
- Alertas por volumenes inusuales
- Capacidad de desactivar agente por org instantaneamente
- Limites diarios acumulados via WhatsApp

### R3: Reconciliacion de Efectivo Fisico

**Riesgo:** El efectivo fisico en puntos de pago es dificil de rastrear. Pueden haber discrepancias por robo, errores, o fraude que son dificiles de detectar en tiempo real.

**Mitigacion:**
- Reconciliacion obligatoria diaria (alertas si no se hace)
- Umbrales de discrepancia configurables con alertas automaticas
- Cash balance en el sistema es "estimado" (no garantizado)
- Limite de Cash-Out por punto basado en cash_balance del sistema
- Auditoria presencial periodica (fuera de scope del software pero habilitada por los datos)

### R4: Race Conditions en Subasta de Efectivo

**Riesgo:** Dos empresas pueden intentar comprar la misma oferta simultaneamente, resultando en sobre-venta de efectivo.

**Mitigacion:**
- TransactWriteItems con ConditionExpression en remaining_amount
- Solo una compra puede ejecutarse a la vez por oferta (lock optimista)
- Si falla: retry con remaining_amount actualizado
- Tests de concurrencia obligatorios

### R5: Limites de DynamoDB TransactWriteItems

**Riesgo:** DynamoDB permite max 100 items por TransactWriteItems. Operaciones complejas (dispersion masiva + comisiones + ledger) pueden exceder el limite.

**Mitigacion:**
- Dividir en batches de 50 items max (dejar margen)
- Implementar compensacion si un batch falla (saga pattern)
- Monitorear tamano de transacciones
- Para subasta: cada compra es 1 transaccion, no se agrupan

### R6: Costo de WhatsApp Business API

**Riesgo:** WhatsApp Business API cobra por mensaje enviado. Notificaciones proactivas masivas pueden generar costos significativos.

**Mitigacion:**
- Rate limiting de notificaciones (max 20/dia/usuario)
- Horarios permitidos (no enviar de noche)
- Configuracion granular: usuario puede desactivar tipos de notificacion
- Monitorear costo por mensaje y por organizacion
- Presupuesto de mensajes por org (futuro)

---

## Definition of Done por User Story

Aplican las mismas reglas del plan SPEI original:

- [ ] Codigo implementado y funcionando
- [ ] Tests unitarios >= 98% coverage
- [ ] Tests de integracion para endpoints
- [ ] Sin errores de lint (ruff para Python, ng lint para Angular)
- [ ] Ningun archivo excede 1000 lineas
- [ ] Documentacion OpenAPI para endpoints nuevos
- [ ] Revisado por al menos 1 desarrollador
- [ ] Desplegable en ambiente de staging
- [ ] Criterios de aceptacion verificados

---

## Resumen Ejecutivo

Este plan de expansion agrega **7 epicas** y **33 user stories** al plan SPEI existente, llevando el total del ecosistema a:

| Metrica | Plan Original | Expansion | Total |
|---------|--------------|-----------|-------|
| Epicas | 13 (EP-SP-001 a 013) | 7 (EP-SP-014 a 020) | 20 |
| User Stories | 51 (US-SP-001 a 051) | 33 (US-SP-052 a 084) | 84 |
| Dev-Days (estimado) | ~190 | ~139 | ~329 |
| Repositorios | 4 (payment, webhook, mf-sp, mf-core) | +1 (covacha-botia) | 5 |

**Prioridad de implementacion:**
1. **P0 - Inmediato (paralelo al SPEI)**: EP-SP-019 (Integridad) - sin esto, nada es seguro
2. **P0 - Post-SPEI core**: EP-SP-014 (Inter-Org) - habilita la subasta
3. **P0 - Alto impacto**: EP-SP-015 (Cash) + EP-SP-017 (Agente IA) - en paralelo
4. **P1 - Extension**: EP-SP-016 (Subasta) + EP-SP-018 (BillPay) - dependen de los anteriores
5. **P1 - Frontend**: EP-SP-020 (Pantallas) - cuando las APIs estan listas
