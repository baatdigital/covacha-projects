# SuperPago - BillPay, Onboarding y Conciliacion (EP-SP-021 a EP-SP-028)

**Fecha**: 2026-02-14
**Product Owner**: SuperPago
**Estado**: Planificacion
**Continua desde**: SPEI-EXPANSION-EPICS.md (EP-SP-014 a EP-SP-020, US-SP-052 a US-SP-084)
**User Stories**: US-SP-085 en adelante (continua desde US-SP-084)

---

## Tabla de Contenidos

1. [Contexto y Motivacion](#contexto-y-motivacion)
2. [Relacion con Epicas Existentes](#relacion-con-epicas-existentes)
3. [Modelo de Cuentas por Producto](#modelo-de-cuentas-por-producto)
4. [Mapa de Epicas Nuevas](#mapa-de-epicas-nuevas)
5. [Epicas Detalladas](#epicas-detalladas)
6. [User Stories Detalladas](#user-stories-detalladas)
7. [Roadmap](#roadmap)
8. [Grafo de Dependencias](#grafo-de-dependencias)
9. [Riesgos y Mitigaciones](#riesgos-y-mitigaciones)

---

## Contexto y Motivacion

El plan SPEI original (EP-SP-001 a EP-SP-013) y su expansion (EP-SP-014 a EP-SP-020) cubren el motor de cuentas, ledger, SPEI in/out, movimientos internos, cash, subasta de efectivo, agente IA WhatsApp, y los 3 portales frontend. Sin embargo, hay 3 capacidades nuevas que necesitan epicas dedicadas:

| Capacidad | Problema que Resuelve |
|-----------|----------------------|
| **BillPay Backend** | Pago de servicios (CFE, Telmex, agua, gas, TV, internet, recargas, SAT, IMSS) via Monato como agregador |
| **Onboarding de Cliente Empresa** | Automatizar la contratacion de productos (SPEI, BillPay, Openpay) con creacion automatica de cuentas |
| **Conciliacion BillPay** | Verificar automaticamente que los pagos de servicios se aplicaron correctamente, detectar discrepancias |
| **Frontend mf-sp** | Nuevas pantallas multi-tier para BillPay, onboarding, conciliacion y pagos de servicios |

### Diferencia con EP-SP-018 (BillPay via WhatsApp)

EP-SP-018 ya define la integracion con un agregador de BillPay generico (US-SP-071) y el pago de servicios via WhatsApp (US-SP-072). Las nuevas epicas extienden esto con:

- **EP-SP-021**: Driver concreto para Monato BillPay (no generico), con flujo Query -> Pay -> Confirm -> Conciliate
- **EP-SP-022**: Operacion BILLPAY con bloques de transacciones en covacha-transaction (no solo ledger entries)
- **EP-SP-023**: Conciliacion automatica diaria especifica para BillPay
- **EP-SP-024**: Onboarding de clientes empresa (nuevo flujo completo)
- **EP-SP-025 a EP-SP-028**: Pantallas frontend multi-tier

### Relacion con EP-SP-018

EP-SP-018 (US-SP-071) define la interface abstracta `BillPayProvider`. Las nuevas epicas la IMPLEMENTAN concretamente con Monato y agregan todo lo que falta: operaciones transaccionales, conciliacion, onboarding, y frontend.

```
EP-SP-018 (interface BillPayProvider)
    |
    v
EP-SP-021 (MonatoBillPayDriver implementa BillPayProvider)
    |
    v
EP-SP-022 (Operacion BILLPAY en covacha-transaction)
    |
    v
EP-SP-023 (Conciliacion automatica)
    |
    v
EP-SP-025-028 (Frontend multi-tier)
```

---

## Relacion con Epicas Existentes

| Epica Existente | Relacion con Nuevas Epicas |
|-----------------|---------------------------|
| EP-SP-001 (Account Core Engine) | Base: el motor de cuentas que EP-SP-024 extiende para crear cuentas automaticamente |
| EP-SP-002 (Monato Driver) | Pattern: Strategy Pattern que EP-SP-021 sigue para BillPay |
| EP-SP-003 (Double-Entry Ledger) | Prerequisito: EP-SP-022 genera asientos de partida doble para BILLPAY |
| EP-SP-009 (Reconciliacion) | Pattern: EP-SP-023 sigue el mismo patron pero para BillPay |
| EP-SP-018 (BillPay WhatsApp) | Interface: EP-SP-021 implementa BillPayProvider definido en US-SP-071 |
| EP-SP-007 (mf-sp Scaffold) | Base: EP-SP-025-028 agregan pantallas al MF ya scaffolded |

---

## Modelo de Cuentas por Producto

Cuando un cliente empresa contrata productos con SuperPago, se crean automaticamente las siguientes cuentas:

### Producto SPEI

```
Cliente Empresa (ej: Boxito)
+-- CONCENTRADORA_SPEI (pool de fondos SPEI)
|   +-- CLABE_PRIVADA (cuenta operativa con CLABE)
|   +-- CLABE_PRIVADA (segunda cuenta si se necesita)
+-- RESERVADA_COMISIONES_SPEI (comisiones de SuperPago por SPEI)
```

### Producto BillPay

```
Cliente Empresa (ej: Boxito)
+-- CONCENTRADORA_BILLPAY (pool de fondos para pago de servicios)
+-- RESERVADA_COMISIONES_BILLPAY (comisiones de SuperPago por BillPay)
+-- RESERVADA_FONDEO_BILLPAY (fondeo pre-pagado para servicios)
```

### Producto Openpay

```
Cliente Empresa (ej: Boxito)
+-- CONCENTRADORA_OPENPAY (pool de fondos cobros con tarjeta)
+-- RESERVADA_COMISIONES_OPENPAY (comisiones de SuperPago por Openpay)
```

### Cuentas Globales del Cliente (siempre se crean)

```
Cliente Empresa (ej: Boxito)
+-- RESERVADA_IVA (retencion de IVA sobre comisiones)
+-- RESERVADA_RETENCIONES (otras retenciones fiscales)
```

### Ejemplo Completo: Boxito contrata SPEI + BillPay

```
Boxito (Organization)
|
+-- CONCENTRADORA_SPEI          [Monato provisionada]
|   +-- CLABE_PRIVADA           [Monato provisionada, CLABE asignada]
+-- RESERVADA_COMISIONES_SPEI   [Interna]
|
+-- CONCENTRADORA_BILLPAY       [Interna]
+-- RESERVADA_COMISIONES_BILLPAY [Interna]
+-- RESERVADA_FONDEO_BILLPAY    [Interna]
|
+-- RESERVADA_IVA               [Interna]
+-- RESERVADA_RETENCIONES       [Interna]
```

---

## Mapa de Epicas Nuevas

| ID | Epica | Complejidad | Sprint Sugerido | Dependencias | Estado |
|----|-------|-------------|-----------------|--------------|--------|
| EP-SP-021 | Monato BillPay Driver ✅ | L | 8-9 | EP-SP-002, EP-SP-018 (US-SP-071) | COMPLETADO (backend) |
| EP-SP-022 | Operacion BILLPAY (Transaccional) ✅ | L | 9-10 | EP-SP-021, EP-SP-003, EP-SP-001 | COMPLETADO (backend) |
| EP-SP-023 | Conciliacion Automatica BillPay ✅ | L | 10-11 | EP-SP-022 | COMPLETADO (backend) |
| EP-SP-024 | Onboarding de Cliente Empresa ✅ | XL | 8-10 | EP-SP-001, EP-SP-002 | COMPLETADO (backend) |
| EP-SP-025 | mf-sp - Admin: Onboarding y Catalogo (Tier 1) | L | 10-11 | EP-SP-024, EP-SP-007 | **COMPLETADO (frontend stub)** |
| EP-SP-026 | mf-sp - Admin: BillPay Conciliacion y Monitoreo (Tier 1) | L | 11-12 | EP-SP-023, EP-SP-007 | **COMPLETADO (frontend stub)** |
| EP-SP-027 | mf-sp - Business: Pago de Servicios (Tier 2) | L | 10-11 | EP-SP-022, EP-SP-007, EP-SP-011 | **COMPLETADO (frontend stub)** |
| EP-SP-028 | mf-sp - Personal: Mis Servicios (Tier 3) | M | 11-12 | EP-SP-027, EP-SP-012 | **COMPLETADO (frontend stub)** |

**Totales:**
- 8 epicas nuevas
- 32 user stories nuevas (US-SP-085 a US-SP-116)
- Estimacion total: ~138 dev-days

---

## Epicas Detalladas

---

### EP-SP-021: Monato BillPay Driver

> **Estado: COMPLETADO (backend)** — PayBillService + BillerController.pay() + ruta `POST /billers/{id}/pay`. 18 tests. Branch: feature/ISS-017-bill-pay-pago-servicios.

**Descripcion:**
Implementacion concreta del driver de BillPay usando Monato como agregador de pago de servicios. Sigue el Strategy Pattern establecido en EP-SP-002 (SPEIProvider/MonatoDriver). El driver `MonatoBillPayDriver` implementa la interface `BillPayProvider` definida en US-SP-071 (EP-SP-018) y agrega el flujo completo: Query deuda -> Pay -> Confirm. Soporta servicios: CFE (luz), Telmex, agua, gas, TV por cable, internet, recargas telefonicas, SAT, IMSS.

**Diferencia con US-SP-071:**
US-SP-071 define la interface abstracta y un driver stub. EP-SP-021 implementa el driver CONCRETO contra la API real de Monato BillPay, con manejo de errores, reintentos, y catalogo real de servicios.

**User Stories:**
- US-SP-085, US-SP-086, US-SP-087, US-SP-088

**Criterios de Aceptacion de la Epica:**
- [ ] `MonatoBillPayDriver` implementa `BillPayProvider` completamente
- [ ] Flujo Query deuda -> Pay -> Confirm funcional contra API Monato
- [ ] Catalogo de servicios cacheado desde Monato (CFE, Telmex, agua, gas, TV, internet, recargas, SAT, IMSS)
- [ ] Soporte para consulta de adeudo (balance check) en servicios que lo permiten
- [ ] Manejo de errores especificos de Monato (timeout, rechazo, servicio no disponible)
- [ ] Idempotencia estricta con `idempotency_key`
- [ ] Retry con backoff exponencial para fallos transitorios
- [ ] Strategy Pattern: futuro driver SIPREL puede agregarse sin cambiar logica de negocio
- [ ] Tests >= 98% con mocks de API Monato

**Dependencias:** EP-SP-002 (Strategy Pattern), EP-SP-018/US-SP-071 (interface BillPayProvider)

**Complejidad:** L (4 user stories, integracion con API externa real)

**Repositorios:** `covacha-payment`

---

### EP-SP-022: Operacion BILLPAY (Transaccional)

> **Estado: COMPLETADO (backend)** — BillPayOperation model + SavedReference model + BillPayOperationRepository + BillPayOrchestrator (idempotencia, hold de fondos, rollback). 16 tests. Branch: feature/ISS-022-billpay-operacion-transaccional.

**Descripcion:**
Orquestacion transaccional completa de un pago de servicios. Crea una Operacion tipo `BILLPAY` en `modspei_operations_prod` con sus Transacciones hijas en `modspei_transactions_prod`. Sigue la maquina de estados: `CREATED -> PENDING -> PROCESSING -> COMPLETED/FAILED`. Genera asientos de partida doble: DEBIT en cuenta del pagador, CREDIT en concentradora BillPay, CREDIT en cuenta de comisiones.

**User Stories:**
- US-SP-089, US-SP-090, US-SP-091, US-SP-092

**Criterios de Aceptacion de la Epica:**
- [x] Operacion BILLPAY con status machine completa
- [x] Transacciones hijas: DEBIT cuenta pagador + CREDIT concentradora BillPay + CREDIT comisiones
- [x] Validacion de saldo suficiente antes de iniciar
- [x] Hold de fondos durante PROCESSING (available_balance -= amount)
- [x] Rollback automatico si Monato rechaza el pago
- [x] Endpoints REST: query deuda, pagar servicio, ver estado, historial
- [x] Soporte multi-canal: PORTAL (web) y WHATSAPP
- [x] Idempotencia end-to-end
- [x] Tests >= 98%

**Dependencias:** EP-SP-021 (driver), EP-SP-003 (ledger), EP-SP-001 (cuentas)

**Complejidad:** L (4 user stories, logica transaccional compleja)

**Repositorios:** `covacha-transaction`, `covacha-payment`

---

### EP-SP-023: Conciliacion Automatica BillPay

> **Estado: COMPLETADO (backend)** — BillPayConciliation model + BillPayConciliationRepository + BillPayConciliationService (6 tipos de discrepancias, alertas SNS, resolucion manual + audit trail, metricas). 17 tests. Branch: feature/ISS-023-conciliacion-automatica-billpay.

**Descripcion:**
Sistema de conciliacion automatica que compara los pagos de servicios ejecutados en SuperPago contra los confirmados por Monato. Detecta discrepancias: pagos pendientes de confirmacion, rechazados post-pago, parcialmente aplicados, o no registrados en Monato. Incluye Lambda programada, dashboard de conciliacion, alertas automaticas, y flujo de resolucion manual con audit trail.

**User Stories:**
- US-SP-093, US-SP-094, US-SP-095, US-SP-096

**Criterios de Aceptacion de la Epica:**
- [x] Lambda programada (configurable: cada hora o diaria)
- [x] Endpoint Monato: `GET /billpay/conciliation` integrado
- [x] Comparacion automatica: pagos locales COMPLETED vs confirmados en Monato
- [x] Deteccion de discrepancias: PENDING_CONFIRMATION, REJECTED_POST_PAY, PARTIAL, NOT_FOUND_IN_PROVIDER, NOT_FOUND_LOCAL
- [x] Modelo `BillPayConciliation` en DynamoDB
- [x] Alertas automaticas (SNS/email) cuando hay discrepancias
- [x] API para resolucion manual con audit trail
- [ ] Dashboard de conciliacion en mf-sp (EP-SP-026)
- [x] Metricas: tasa de conciliacion exitosa, tiempo promedio de resolucion
- [x] Tests >= 98%

**Dependencias:** EP-SP-022 (operaciones BILLPAY existentes para conciliar)

**Complejidad:** L (4 user stories, Lambda + comparacion + alertas)

**Repositorios:** `covacha-transaction`, `covacha-payment` (Lambda)

---

### EP-SP-024: Onboarding de Cliente Empresa

> **Estado: COMPLETADO (backend)** — ClientOnboarding model + ClientOnboardingRepository + ClientOnboardingService (wizard 4 pasos, catalogo de productos, creacion automatica de cuentas, provisionamiento Monato, rollback parcial, audit trail). 22 tests. Branch: feature/ISS-024-onboarding-cliente-empresa.

**Descripcion:**
Flujo automatizado para cuando un nuevo cliente empresa (ej: Boxito) contrata servicios con SuperPago. El admin selecciona que productos contrata el cliente (SPEI, BillPay, Openpay -- cualquier combinacion) y el sistema automaticamente crea todas las cuentas necesarias por producto, las provisiona en Monato cuando aplica, y deja al cliente listo para operar. Incluye catalogo de productos, wizard de contratacion, y provisionamiento automatico.

**User Stories:**
- US-SP-097, US-SP-098, US-SP-099, US-SP-100, US-SP-101, US-SP-102

**Criterios de Aceptacion de la Epica:**
- [x] Catalogo de productos contratables (SPEI, BillPay, Openpay) con definicion de cuentas por producto
- [x] Wizard de onboarding en 4 pasos: Datos cliente -> Seleccion productos -> Confirmacion -> Provisionamiento
- [x] Creacion automatica de estructura de cuentas por producto contratado:
  - SPEI: Concentradora SPEI + Reservada Comisiones SPEI + al menos 1 CLABE
  - BillPay: Concentradora BillPay + Reservada Comisiones BillPay + Reservada Fondeo BillPay
  - Openpay: Concentradora Openpay + Reservada Comisiones Openpay
- [x] Cuentas globales siempre creadas: Reservada IVA + Reservada Retenciones
- [x] Provisionamiento automatico en Monato para cuentas SPEI (CLABE, concentradora)
- [x] Estado de onboarding: DRAFT -> SUBMITTED -> PROVISIONING -> ACTIVE -> FAILED
- [x] Rollback parcial: si falla la creacion de una cuenta, revertir las ya creadas
- [x] Audit trail completo del onboarding
- [ ] Solo Tier 1 (Admin SuperPago) puede ejecutar onboarding
- [x] Tests >= 98%

**Dependencias:** EP-SP-001 (Account Core Engine), EP-SP-002 (Monato Driver para provisioning)

**Complejidad:** XL (6 user stories, flujo complejo multi-paso con provisionamiento externo)

**Repositorios:** `covacha-payment`, `covacha-core`

---

### EP-SP-025: mf-sp - Admin: Onboarding y Catalogo (Tier 1)

**Descripcion:**
Pantallas de Tier 1 (Admin SuperPago) para el wizard de onboarding de clientes empresa y la gestion del catalogo de productos contratables. Incluye el formulario multi-paso de alta de cliente, la visualizacion del estado de provisionamiento, y el CRUD del catalogo de productos.

**User Stories:**
- US-SP-103, US-SP-104, US-SP-105

**Criterios de Aceptacion de la Epica:**
- [ ] Wizard de onboarding: 4 pasos con stepper visual
- [ ] Catalogo de productos: CRUD con definicion de cuentas por producto
- [ ] Vista de clientes onboarded con estado de provisionamiento
- [ ] Detalle de cliente: ver estructura de cuentas creadas
- [ ] Responsive design
- [ ] Tests >= 98%

**Dependencias:** EP-SP-024 (API), EP-SP-007 (mf-sp scaffold)

**Complejidad:** L (3 user stories, wizard complejo)

**Repositorio:** `mf-sp`

---

### EP-SP-026: mf-sp - Admin: BillPay Conciliacion y Monitoreo (Tier 1)

**Descripcion:**
Pantallas de Tier 1 (Admin SuperPago) para el dashboard de conciliacion BillPay global y el monitoreo de pagos de servicios de todos los clientes. Incluye dashboard de discrepancias, flujo de resolucion manual, metricas de conciliacion, y monitoreo en tiempo real de pagos.

**User Stories:**
- US-SP-106, US-SP-107, US-SP-108

**Criterios de Aceptacion de la Epica:**
- [ ] Dashboard de conciliacion: discrepancias, estado global, tendencias
- [ ] Tabla de discrepancias con filtros y acciones de resolucion
- [ ] Monitoreo de pagos de servicios: volumen, tasa de exito, fallos
- [ ] Graficas de tendencia de conciliacion
- [ ] Acciones de resolucion manual con formulario de justificacion
- [ ] Auto-refresh
- [ ] Tests >= 98%

**Dependencias:** EP-SP-023 (API conciliacion), EP-SP-007 (mf-sp scaffold)

**Complejidad:** L (3 user stories, dashboard complejo)

**Repositorio:** `mf-sp`

---

### EP-SP-027: mf-sp - Business: Pago de Servicios (Tier 2)

**Descripcion:**
Pantallas de Tier 2 (Cliente Empresa) para pagar servicios, ver historial de pagos, configurar servicios recurrentes, y ver el estado de conciliacion de sus pagos. Es la vista operativa diaria del cliente que usa BillPay.

**User Stories:**
- US-SP-109, US-SP-110, US-SP-111, US-SP-112

**Criterios de Aceptacion de la Epica:**
- [ ] Formulario de pago de servicios: query deuda -> confirmar -> pagar
- [ ] Catalogo visual de servicios disponibles (CFE, Telmex, agua, etc.)
- [ ] Historial de pagos con filtros por servicio, fecha, estado
- [ ] Configuracion de servicios recurrentes (guardar referencias)
- [ ] Vista de conciliacion de SUS pagos
- [ ] Responsive design (mobile-first para operadores)
- [ ] Tests >= 98%

**Dependencias:** EP-SP-022 (API pagos), EP-SP-007 (scaffold), EP-SP-011 (Tier 2 base)

**Complejidad:** L (4 user stories, formularios + historial)

**Repositorio:** `mf-sp`

---

### EP-SP-028: mf-sp - Personal: Mis Servicios (Tier 3)

**Descripcion:**
Pantallas de Tier 3 (Usuario Final) para pagar sus servicios de forma simple, ver historial de pagos, y gestionar sus servicios guardados. Es una version simplificada de Tier 2, enfocada en la experiencia movil de un usuario persona natural.

**User Stories:**
- US-SP-113, US-SP-114, US-SP-115, US-SP-116

**Criterios de Aceptacion de la Epica:**
- [ ] Formulario simple de pago: "Pagar un servicio" con flujo guiado
- [ ] Servicios guardados: "Mis servicios" con pago rapido
- [ ] Historial de pagos simple con recibos descargables
- [ ] Notificaciones de pago exitoso/fallido
- [ ] Mobile-first design
- [ ] Tests >= 98%

**Dependencias:** EP-SP-027 (comparte adapters y servicios), EP-SP-012 (Tier 3 base)

**Complejidad:** M (4 user stories, reutiliza componentes de Tier 2)

**Repositorio:** `mf-sp`

---

## User Stories Detalladas

---

### EP-SP-021: Monato BillPay Driver

---

#### US-SP-085: MonatoBillPayDriver - Catalogo de Servicios

**ID:** US-SP-085
**Epica:** EP-SP-021
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero obtener el catalogo de servicios pagables desde Monato BillPay para que los usuarios vean que servicios pueden pagar (CFE, Telmex, agua, gas, TV, internet, recargas, SAT, IMSS).

**Criterios de Aceptacion:**
- [ ] `MonatoBillPayDriver` implementa `BillPayProvider.get_services()`
- [ ] Llama a endpoint Monato: `GET /billpay/services` (o equivalente segun API Monato)
- [ ] Mapea respuesta Monato a modelo interno `BillPayService`:
  - `service_id`: ID del servicio en Monato
  - `name`: Nombre legible ("CFE - Comision Federal de Electricidad")
  - `category`: ELECTRICITY | WATER | PHONE | GAS | TV | INTERNET | MOBILE_TOPUP | TAX | SOCIAL_SECURITY | OTHER
  - `requires_reference`: boolean (si necesita numero de contrato/servicio)
  - `reference_label`: string ("Numero de servicio", "Numero de contrato", etc.)
  - `supports_balance_check`: boolean
  - `min_amount`, `max_amount`: limites del servicio
  - `commission`: Decimal (comision de Monato por este servicio)
  - `provider_service_id`: ID original en Monato
- [ ] Cache del catalogo en DynamoDB con TTL de 24 horas
  - `PK: BILLPAY_CATALOG`, `SK: SVC#{service_id}`
  - `GSI: BILLPAY_CATEGORY`, `SK: category#name`
- [ ] Endpoint interno: `GET /api/v1/billpay/services` con filtro por categoria
- [ ] Endpoint interno: `GET /api/v1/billpay/services/{service_id}` detalle
- [ ] Manejo de error si Monato no responde: servir cache aunque este expirado con warning
- [ ] Job de refresco: Lambda o cron que actualiza el catalogo cada 6 horas

**Tareas Tecnicas:**
1. Crear dataclass `BillPayService` con validaciones
2. Implementar `MonatoBillPayDriver.get_services()`
3. Capa de cache en DynamoDB con TTL
4. Endpoints REST internos (Flask Blueprint)
5. Job de refresco del catalogo
6. Tests con mock de API Monato

**Dependencias:** US-SP-071 (interface BillPayProvider)
**Estimacion:** 4 dev-days

---

#### US-SP-086: MonatoBillPayDriver - Query de Deuda

**ID:** US-SP-086
**Epica:** EP-SP-021
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero consultar el adeudo de un servicio en Monato BillPay para mostrar al usuario cuanto debe antes de pagar (ej: "Tu recibo de CFE es de $850.00").

**Criterios de Aceptacion:**
- [ ] `MonatoBillPayDriver` implementa `BillPayProvider.get_balance(service_id, reference)`
- [ ] Llama a endpoint Monato: `POST /billpay/query` (o equivalente)
  - Body: `{ service_id, reference_number }`
- [ ] Respuesta mapeada a modelo `BillPayBalance`:
  - `service_id`, `service_name`
  - `reference`: numero de contrato/servicio consultado
  - `account_holder`: nombre del titular (si Monato lo devuelve)
  - `amount_due`: monto adeudado
  - `due_date`: fecha de vencimiento (si disponible)
  - `period`: periodo de facturacion (ej: "Enero 2026")
  - `partial_payment_allowed`: boolean
  - `min_payment`: monto minimo si permite pago parcial
  - `provider_query_id`: ID de la consulta en Monato
  - `queried_at`: timestamp de la consulta
- [ ] Si el servicio no soporta balance check (`supports_balance_check: false`), retornar error claro
- [ ] Timeout de 10 segundos para la consulta a Monato
- [ ] Reintentos: 2 intentos con backoff exponencial (1s, 3s) para errores transitorios
- [ ] Errores especificos: REFERENCE_NOT_FOUND, SERVICE_UNAVAILABLE, TIMEOUT, INVALID_REFERENCE
- [ ] Endpoint: `POST /api/v1/billpay/query`
  - Body: `{ service_id, reference }`
  - Response: `BillPayBalance` o error

**Tareas Tecnicas:**
1. Crear dataclass `BillPayBalance` con validaciones
2. Implementar `MonatoBillPayDriver.get_balance()`
3. Logica de reintentos con backoff
4. Mapeo de errores Monato a errores internos
5. Endpoint REST
6. Tests: happy path, timeout, servicio no encontrado, referencia invalida

**Dependencias:** US-SP-085 (catalogo)
**Estimacion:** 3 dev-days

---

#### US-SP-087: MonatoBillPayDriver - Pago (Pay + Confirm)

**ID:** US-SP-087
**Epica:** EP-SP-021
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero ejecutar un pago de servicio en Monato BillPay y confirmar su aplicacion para que el adeudo del usuario quede liquidado en el proveedor del servicio.

**Criterios de Aceptacion:**
- [ ] `MonatoBillPayDriver` implementa `BillPayProvider.make_payment(service_id, reference, amount)`
- [ ] Flujo de 2 pasos contra Monato:
  1. **Pay**: `POST /billpay/pay`
     - Body: `{ service_id, reference, amount, idempotency_key }`
     - Response: `{ payment_id, status: "PROCESSING", provider_ref }`
  2. **Confirm**: `GET /billpay/payments/{payment_id}/status` (polling o webhook)
     - Response: `{ payment_id, status: "COMPLETED"|"FAILED"|"PENDING", confirmation_code, applied_at }`
- [ ] Modelo `BillPayPaymentResult`:
  - `payment_id`: ID del pago en SuperPago
  - `provider_payment_id`: ID del pago en Monato
  - `status`: COMPLETED | FAILED | PENDING
  - `confirmation_code`: codigo de confirmacion del proveedor del servicio
  - `applied_at`: cuando se aplico el pago
  - `receipt_data`: datos para generar recibo (folio, autorizacion)
- [ ] Idempotencia: mismo `idempotency_key` retorna el mismo resultado sin ejecutar doble pago
- [ ] Timeout de 30 segundos para la ejecucion del pago
- [ ] Si Pay exitoso pero Confirm timeout: marcar como PENDING_CONFIRMATION (para conciliacion)
- [ ] Si Pay falla: retornar error con codigo especifico (INSUFFICIENT_FUNDS_PROVIDER, SERVICE_DOWN, INVALID_AMOUNT, etc.)
- [ ] Reintentos: SOLO en confirm (nunca reintentar pay - riesgo de doble pago)

**Tareas Tecnicas:**
1. Crear dataclass `BillPayPaymentResult`
2. Implementar `MonatoBillPayDriver.make_payment()` con flujo Pay + Confirm
3. Implementar `MonatoBillPayDriver.get_payment_status()` para polling
4. Logica de idempotencia
5. Manejo de timeout en confirmacion
6. Tests: pago exitoso, pago fallido, timeout en confirm, idempotencia

**Dependencias:** US-SP-086 (query)
**Estimacion:** 5 dev-days

---

#### US-SP-088: MonatoBillPayDriver - Manejo de Errores y Health Check

**ID:** US-SP-088
**Epica:** EP-SP-021
**Prioridad:** P1

**Historia:**
Como **Sistema** quiero manejar gracefully los errores de Monato BillPay y tener un health check del driver para que el sistema degrade sin caer cuando Monato tiene problemas.

**Criterios de Aceptacion:**
- [ ] Mapeo exhaustivo de errores Monato a errores internos:
  - `MONATO_TIMEOUT` -> `BillPayError.PROVIDER_TIMEOUT`
  - `MONATO_500` -> `BillPayError.PROVIDER_ERROR`
  - `MONATO_INVALID_REF` -> `BillPayError.INVALID_REFERENCE`
  - `MONATO_SERVICE_SUSPENDED` -> `BillPayError.SERVICE_UNAVAILABLE`
  - `MONATO_INSUFFICIENT_BALANCE` -> `BillPayError.PROVIDER_INSUFFICIENT_FUNDS`
  - `MONATO_DUPLICATE` -> `BillPayError.DUPLICATE_PAYMENT`
- [ ] Circuit breaker: si Monato falla 5 veces consecutivas, abrir circuito por 60 segundos
  - Estado del circuito en DynamoDB: `PK: CIRCUIT_BREAKER`, `SK: MONATO_BILLPAY`
  - Al abrir: retornar error `SERVICE_TEMPORARILY_UNAVAILABLE` sin intentar llamada
  - Despues de 60s: half-open, permitir 1 intento
  - Si exitoso: cerrar circuito; si falla: mantener abierto otros 60s
- [ ] Health check endpoint: `GET /api/v1/billpay/health`
  - Response: `{ status: "healthy"|"degraded"|"down", circuit_breaker: "closed"|"open"|"half-open", last_successful_call, uptime_percentage_24h }`
- [ ] Logging estructurado (sin datos sensibles):
  - Nivel INFO: consulta exitosa, pago exitoso
  - Nivel WARN: retry, circuit breaker half-open
  - Nivel ERROR: pago fallido, circuit breaker open
- [ ] Metricas: total calls, success rate, avg latency, circuit breaker opens (para Grafana)
- [ ] Strategy Pattern: si se agrega un segundo driver (SIPREL), la logica de circuit breaker y error handling se reutiliza

**Tareas Tecnicas:**
1. Crear enum `BillPayError` con todos los codigos
2. Implementar circuit breaker con DynamoDB state
3. Health check endpoint
4. Logging estructurado
5. Metricas exportables
6. Tests: circuit breaker open/close/half-open, mapeo de errores

**Dependencias:** US-SP-087 (pago)
**Estimacion:** 4 dev-days

---

### EP-SP-022: Operacion BILLPAY (Transaccional)

---

#### US-SP-089: Modelo de Operacion BILLPAY

**ID:** US-SP-089
**Epica:** EP-SP-022
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero registrar cada pago de servicio como una Operacion tipo `BILLPAY` en `modspei_operations_prod` para que quede en el historial transaccional del cliente con trazabilidad completa.

**Criterios de Aceptacion:**
- [ ] Operacion tipo `BILLPAY` en `modspei_operations_prod`:
  - `PK: {sp_organization_id}`, `SK: OP#{operation_id}`
  - `operation_type`: `BILLPAY`
  - `status`: CREATED -> PENDING -> PROCESSING -> COMPLETED | FAILED | CANCELLED
  - `amount`: monto del pago al servicio
  - `fee_amount`: comision de SuperPago
  - `total_amount`: amount + fee_amount
  - `source_account_id`: cuenta del pagador (CLABE o concentradora BillPay)
  - `destination_account_id`: null (pago a proveedor externo)
  - `metadata`:
    ```json
    {
      "service_id": "cfe-luz",
      "service_name": "CFE - Comision Federal de Electricidad",
      "reference": "123456789",
      "account_holder": "Juan Perez",
      "period": "Enero 2026",
      "provider_payment_id": "monato-pay-xyz",
      "confirmation_code": "ABC123",
      "channel": "PORTAL|WHATSAPP"
    }
    ```
  - `idempotency_key`: hash de (org_id + service_id + reference + amount + date)
  - `initiated_by`: user_id del que paga
- [ ] GSI existentes aplican: OperationStatusIndex, OperationTypeIndex, IdempotencyIndex
- [ ] Nuevo GSI `BillPayServiceIndex`:
  - `GSIPK: BILLPAY#{sp_organization_id}`, `GSISK: #{service_id}##{created_at}`
  - Para historial de pagos de un servicio especifico
- [ ] La operacion se crea en estado CREATED al iniciar el flujo de pago

**Tareas Tecnicas:**
1. Extender modelo de Operation para BILLPAY con metadata especifica
2. Crear GSI BillPayServiceIndex
3. Dataclass BillPayOperation con validaciones
4. Estado machine para BILLPAY
5. Tests del modelo

**Dependencias:** Modelo de Operations existente (EP-SP-003)
**Estimacion:** 3 dev-days

---

#### US-SP-090: Transacciones Hijas del Pago de Servicio

**ID:** US-SP-090
**Epica:** EP-SP-022
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero que cada pago de servicio genere sus transacciones contables hijas (DEBIT pagador, CREDIT concentradora BillPay, CREDIT comisiones) para mantener la contabilidad de partida doble.

**Criterios de Aceptacion:**
- [ ] Al completar un pago BILLPAY, se crean las siguientes transacciones en `modspei_transactions_prod`:
  1. `DECREMENT` en cuenta del pagador por `total_amount` (monto + comision)
  2. `INCREMENT` en concentradora BillPay por `amount` (monto del servicio)
  3. `INCREMENT` en cuenta RESERVADA_COMISIONES_BILLPAY por `fee_amount` (comision SP)
- [ ] Todas las transacciones en la misma operacion: `PK: OP#{operation_id}`
- [ ] Secuencia: TXN#1 (DECREMENT pagador), TXN#2 (INCREMENT concentradora), TXN#3 (INCREMENT comisiones)
- [ ] Validacion de partida doble: SUM(DECREMENTS) == SUM(INCREMENTS) dentro de la operacion
- [ ] Balance atomico: actualizar `balance` y `available_balance` de las 3 cuentas en transaccion DynamoDB
- [ ] `balance_before` y `balance_after` registrados en cada transaccion
- [ ] Optimistic locking: `version` de cada cuenta se incrementa; si hay conflicto, reintentar
- [ ] Si comision es $0 (servicio sin comision), solo generar 2 transacciones (sin la de comisiones)

**Tareas Tecnicas:**
1. Crear funcion `create_billpay_transactions(operation_id, accounts)`
2. Logica de actualizacion atomica de saldos (DynamoDB TransactWriteItems)
3. Validacion de partida doble
4. Manejo de caso sin comision
5. Tests: 3 transacciones, 2 transacciones sin comision, conflicto de version

**Dependencias:** US-SP-089 (modelo operacion), modelo de Transactions existente
**Estimacion:** 4 dev-days

---

#### US-SP-091: Orquestador de Pago de Servicios

**ID:** US-SP-091
**Epica:** EP-SP-022
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero un servicio orquestador que coordine el flujo completo de pago de servicios (validar saldo -> hold -> llamar Monato -> registrar transacciones -> liberar hold) para garantizar consistencia transaccional.

**Criterios de Aceptacion:**
- [ ] `BillPayOrchestrator` con flujo:
  1. Recibir request: `{ org_id, account_id, service_id, reference, amount?, idempotency_key }`
  2. Verificar idempotencia (si ya existe, retornar resultado existente)
  3. Crear Operacion BILLPAY en estado CREATED
  4. Validar: cuenta activa, saldo suficiente (available_balance >= total_amount)
  5. Hold de fondos: `available_balance -= total_amount` (estado PENDING)
  6. Si `amount` no proporcionado: query de deuda via MonatoBillPayDriver
  7. Llamar a `MonatoBillPayDriver.make_payment()` (estado PROCESSING)
  8. Si exitoso:
     - Crear transacciones hijas (US-SP-090)
     - Actualizar saldos reales
     - Liberar hold
     - Operacion -> COMPLETED
  9. Si fallido:
     - Liberar hold: `available_balance += total_amount`
     - Operacion -> FAILED con error_code y error_message
- [ ] Endpoint: `POST /api/v1/organizations/{org_id}/billpay/pay`
  - Body: `{ account_id, service_id, reference, amount?, idempotency_key }`
  - Response 200: `{ operation_id, status: "COMPLETED", confirmation_code, transactions: [...] }`
  - Response 202: `{ operation_id, status: "PROCESSING" }` (si la confirmacion tarda)
  - Response 400: `{ error: "INSUFFICIENT_BALANCE"|"INVALID_REFERENCE"|... }`
- [ ] Endpoint: `GET /api/v1/organizations/{org_id}/billpay/operations/{operation_id}`
  - Para consultar estado de un pago en proceso
- [ ] Canal se infiere del request header o parametro: `channel: "PORTAL"|"WHATSAPP"`
- [ ] Logging completo del flujo sin datos sensibles

**Tareas Tecnicas:**
1. Crear `BillPayOrchestrator` service
2. Flujo completo con hold/release
3. Endpoints REST (Blueprint)
4. Integracion con MonatoBillPayDriver
5. Integracion con creacion de transacciones
6. Manejo de PROCESSING timeout (retornar 202)
7. Tests: flujo exitoso, saldo insuficiente, fallo Monato con rollback, idempotencia

**Dependencias:** US-SP-089 (modelo), US-SP-090 (transacciones), US-SP-087 (driver pago)
**Estimacion:** 5 dev-days

---

#### US-SP-092: Historial y Estado de Pagos de Servicios

**ID:** US-SP-092
**Epica:** EP-SP-022
**Prioridad:** P1

**Historia:**
Como **Cliente Empresa** quiero ver el historial de pagos de servicios de mi organizacion y consultar el estado de pagos en proceso para tener visibilidad de mis gastos en servicios.

**Criterios de Aceptacion:**
- [ ] `GET /api/v1/organizations/{org_id}/billpay/history`
  - Filtros: `service_id`, `status`, `date_from`, `date_to`, `channel`, `reference`
  - Paginacion: `cursor`, `limit` (max 100)
  - Ordenamiento: `created_at` DESC (mas recientes primero)
  - Response: lista de operaciones BILLPAY con metadata de servicio
- [ ] `GET /api/v1/organizations/{org_id}/billpay/history/{operation_id}`
  - Detalle completo: operacion + transacciones hijas + metadata
- [ ] `GET /api/v1/organizations/{org_id}/billpay/summary`
  - Resumen por periodo (mes actual, mes anterior):
    - Total pagado por servicio
    - Numero de pagos por servicio
    - Comisiones totales
    - Pagos fallidos
- [ ] `GET /api/v1/organizations/{org_id}/billpay/saved-references`
  - Referencias guardadas por el cliente para pagos recurrentes
  - Response: `[{ service_id, service_name, reference, alias, last_paid_at, last_amount }]`
- [ ] `POST /api/v1/organizations/{org_id}/billpay/saved-references`
  - Body: `{ service_id, reference, alias }`
  - Maximo 50 referencias guardadas por organizacion
- [ ] `DELETE /api/v1/organizations/{org_id}/billpay/saved-references/{id}`
- [ ] Los pagos BILLPAY tambien aparecen en el endpoint general de operaciones (`GET /api/v1/organizations/{org_id}/operations`)

**Tareas Tecnicas:**
1. Query de historial con filtros usando GSIs existentes
2. Endpoint de detalle con join operacion + transacciones
3. Endpoint de resumen con agregaciones
4. CRUD de referencias guardadas (modelo en DynamoDB)
5. Tests: historial con filtros, paginacion, resumen, referencias

**Dependencias:** US-SP-089 (modelo operaciones BILLPAY)
**Estimacion:** 4 dev-days

---

### EP-SP-023: Conciliacion Automatica BillPay

---

#### US-SP-093: Modelo de Conciliacion BillPay

**ID:** US-SP-093
**Epica:** EP-SP-023
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero un modelo de datos para registrar resultados de conciliacion de BillPay para que cada ejecucion quede documentada con sus discrepancias y resoluciones.

**Criterios de Aceptacion:**
- [ ] Modelo `BillPayConciliation` en DynamoDB:
  - `PK: BILLPAY_CONCILIATION`, `SK: RUN#{run_id}`
  - `run_id`: UUID de la ejecucion de conciliacion
  - `run_date`: fecha/hora de la ejecucion
  - `period_start`, `period_end`: periodo conciliado
  - `trigger`: SCHEDULED | MANUAL | POST_DEPLOY
  - `status`: RUNNING | COMPLETED | COMPLETED_WITH_DISCREPANCIES | FAILED
  - `total_operations_local`: numero de pagos en SuperPago en el periodo
  - `total_operations_provider`: numero de pagos en Monato en el periodo
  - `matched`: numero de pagos que coinciden
  - `discrepancies`: numero de discrepancias encontradas
  - `auto_resolved`: numero de discrepancias resueltas automaticamente
  - `pending_resolution`: numero pendientes de resolucion manual
  - `execution_time_ms`: tiempo de ejecucion
  - `created_at`, `completed_at`
- [ ] Modelo `BillPayDiscrepancy`:
  - `PK: CONCILIATION_RUN#{run_id}`, `SK: DISC#{discrepancy_id}`
  - `discrepancy_id`: UUID
  - `operation_id`: ID de la operacion en SuperPago (puede ser null si NOT_FOUND_LOCAL)
  - `provider_payment_id`: ID del pago en Monato (puede ser null si NOT_FOUND_IN_PROVIDER)
  - `type`: PENDING_CONFIRMATION | REJECTED_POST_PAY | AMOUNT_MISMATCH | NOT_FOUND_IN_PROVIDER | NOT_FOUND_LOCAL | STATUS_MISMATCH
  - `severity`: CRITICAL | HIGH | MEDIUM | LOW
  - `local_status`: estado en SuperPago
  - `provider_status`: estado en Monato
  - `local_amount`, `provider_amount`: montos para detectar diferencias
  - `service_name`, `reference`: datos del servicio
  - `resolution_status`: PENDING | AUTO_RESOLVED | MANUALLY_RESOLVED | ESCALATED
  - `resolution_notes`: notas de resolucion
  - `resolved_by`: user_id que resolvio
  - `resolved_at`: timestamp de resolucion
- [ ] GSI `DiscrepancyStatusIndex`: `PK: DISC_STATUS#{resolution_status}`, `SK: #{severity}##{created_at}`
- [ ] GSI `DiscrepancyOrgIndex`: `PK: ORG_DISC#{sp_organization_id}`, `SK: #{created_at}`

**Tareas Tecnicas:**
1. Crear modelos en DynamoDB con GSIs
2. Dataclasses con validaciones
3. Enum DiscrepancyType con severidad asociada
4. Tests del modelo

**Dependencias:** Ninguna (modelo puro)
**Estimacion:** 3 dev-days

---

#### US-SP-094: Lambda de Conciliacion Programada

**ID:** US-SP-094
**Epica:** EP-SP-023
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero una Lambda que se ejecute automaticamente (cada hora o diariamente configurable) para conciliar los pagos de BillPay del periodo comparando lo registrado en SuperPago con lo confirmado por Monato.

**Criterios de Aceptacion:**
- [ ] Lambda `billpay-conciliation` en AWS:
  - Trigger: EventBridge rule configurable (default: cada 6 horas, override: cada hora o diaria)
  - Input: `{ period_hours?: 24, force_full_day?: false }`
- [ ] Flujo de la Lambda:
  1. Crear registro de `BillPayConciliation` en estado RUNNING
  2. Obtener pagos locales COMPLETED del periodo: query `modspei_operations_prod` con `operation_type = BILLPAY` y `status = COMPLETED`
  3. Obtener pagos del periodo en Monato: `GET /billpay/conciliation?date_from={}&date_to={}`
  4. Comparar por `provider_payment_id`:
     - **Match**: operacion local COMPLETED + Monato COMPLETED + montos iguales -> OK
     - **PENDING_CONFIRMATION**: local COMPLETED pero Monato dice PENDING -> discrepancia MEDIUM
     - **REJECTED_POST_PAY**: local COMPLETED pero Monato dice REJECTED -> discrepancia CRITICAL
     - **AMOUNT_MISMATCH**: ambos COMPLETED pero montos difieren -> discrepancia HIGH
     - **NOT_FOUND_IN_PROVIDER**: local COMPLETED pero no existe en Monato -> discrepancia CRITICAL
     - **NOT_FOUND_LOCAL**: existe en Monato pero no en SuperPago -> discrepancia HIGH
     - **STATUS_MISMATCH**: cualquier otra diferencia de estado -> discrepancia MEDIUM
  5. Crear registros de `BillPayDiscrepancy` por cada discrepancia
  6. Auto-resolver discrepancias triviales:
     - PENDING_CONFIRMATION con mas de 5 min: reintentar confirm
     - Si confirm ahora dice COMPLETED -> AUTO_RESOLVED
  7. Actualizar `BillPayConciliation` con totales y estado final
- [ ] Si la Lambda falla a mitad del proceso: status FAILED con error_message
- [ ] Timeout de Lambda: 5 minutos (suficiente para ~10,000 operaciones)
- [ ] DLQ para invocaciones fallidas

**Tareas Tecnicas:**
1. Crear Lambda handler en Python
2. Logica de comparacion con hash join por provider_payment_id
3. Creacion batch de discrepancias
4. Auto-resolucion de PENDING_CONFIRMATION
5. EventBridge rule configurable
6. DLQ y alertas
7. Tests: conciliacion limpia, con discrepancias de cada tipo, auto-resolucion

**Dependencias:** US-SP-093 (modelo), US-SP-087 (driver para confirm)
**Estimacion:** 5 dev-days

---

#### US-SP-095: Alertas Automaticas de Discrepancias

**ID:** US-SP-095
**Epica:** EP-SP-023
**Prioridad:** P1

**Historia:**
Como **Administrador SuperPago** quiero recibir alertas automaticas cuando la conciliacion detecta discrepancias criticas para poder actuar rapidamente y evitar perdidas financieras.

**Criterios de Aceptacion:**
- [ ] Al completar conciliacion con discrepancias CRITICAL o HIGH:
  - Publicar mensaje a SNS topic `billpay-conciliation-alerts`
  - Suscripciones: email del equipo de operaciones + webhook a Slack
- [ ] Contenido de la alerta:
  ```
  [BILLPAY CONCILIATION] Discrepancias detectadas
  Run ID: {run_id}
  Periodo: {period_start} - {period_end}
  Total operaciones: {total}
  Coincidencias: {matched}
  Discrepancias: {discrepancies} (CRITICAL: X, HIGH: Y)
  Pendientes de resolucion manual: {pending}

  Top discrepancias:
  - OP-123: REJECTED_POST_PAY - CFE $850.00 (ref: 123456)
  - OP-456: NOT_FOUND_IN_PROVIDER - Telmex $350.00 (ref: 789012)
  ```
- [ ] Umbral configurable: alertar solo si discrepancies > N o porcentaje > X%
- [ ] No alertar si la conciliacion es limpia (solo INFO en logs)
- [ ] Endpoint: `GET /api/v1/admin/billpay/conciliation/alerts/config`
- [ ] Endpoint: `PUT /api/v1/admin/billpay/conciliation/alerts/config`
  - Body: `{ critical_threshold: 1, high_threshold: 5, percentage_threshold: 2.0, notify_email: [...], notify_slack_webhook: "..." }`
- [ ] Historico de alertas enviadas (para no duplicar)

**Tareas Tecnicas:**
1. Integracion con SNS
2. Template de alerta con datos relevantes
3. Configuracion de umbrales en DynamoDB
4. Logica de deduplicacion de alertas
5. Endpoints de configuracion
6. Tests: alerta enviada, umbral no alcanzado, deduplicacion

**Dependencias:** US-SP-094 (Lambda que detecta discrepancias)
**Estimacion:** 3 dev-days

---

#### US-SP-096: Resolucion Manual de Discrepancias

**ID:** US-SP-096
**Epica:** EP-SP-023
**Prioridad:** P1

**Historia:**
Como **Administrador SuperPago** quiero poder resolver manualmente discrepancias de conciliacion (aprobar, revertir, o escalar) con un formulario de justificacion para mantener la integridad financiera con audit trail completo.

**Criterios de Aceptacion:**
- [ ] `POST /api/v1/admin/billpay/conciliation/discrepancies/{id}/resolve`
  - Body: `{ action: "APPROVE"|"REVERSE"|"ESCALATE"|"DISMISS", notes: "justificacion...", evidence_urls?: [...] }`
  - Solo Tier 1 (Admin SuperPago) puede resolver
- [ ] Acciones de resolucion:
  - **APPROVE**: Confirmar que el pago es correcto a pesar de la discrepancia. Marca como MANUALLY_RESOLVED.
  - **REVERSE**: Revertir el pago en SuperPago. Crea operacion REFUND_BILLPAY:
    - CREDIT en cuenta del pagador (devolucion)
    - DEBIT en concentradora BillPay
    - DEBIT en comisiones (devolucion comision)
    - Actualiza operacion original a REVERSED
  - **ESCALATE**: Marcar para revision del equipo financiero. Crea ticket interno.
  - **DISMISS**: Descartar como falso positivo. Requiere justificacion obligatoria.
- [ ] Audit trail en cada discrepancia:
  ```json
  {
    "audit": [
      { "action": "CREATED", "by": "SYSTEM", "at": "2026-02-14T10:00:00Z" },
      { "action": "MANUALLY_RESOLVED", "by": "admin-user-123", "at": "2026-02-14T14:30:00Z", "notes": "Verificado con Monato por telefono" }
    ]
  }
  ```
- [ ] `GET /api/v1/admin/billpay/conciliation/discrepancies`
  - Filtros: `resolution_status`, `severity`, `type`, `date_from`, `date_to`, `org_id`
  - Paginacion server-side
- [ ] `GET /api/v1/admin/billpay/conciliation/discrepancies/{id}`
  - Detalle con audit trail completo
- [ ] `GET /api/v1/admin/billpay/conciliation/runs`
  - Historial de ejecuciones de conciliacion
- [ ] `GET /api/v1/admin/billpay/conciliation/runs/{run_id}`
  - Detalle de una ejecucion con sus discrepancias

**Tareas Tecnicas:**
1. Endpoints CRUD de discrepancias
2. Logica de REVERSE (crear operacion REFUND_BILLPAY con transacciones inversas)
3. Audit trail append-only
4. Listado con filtros y paginacion
5. Historial de runs
6. Tests: cada tipo de resolucion, REVERSE con transacciones, audit trail

**Dependencias:** US-SP-093 (modelo), US-SP-090 (transacciones para REVERSE)
**Estimacion:** 5 dev-days

---

### EP-SP-024: Onboarding de Cliente Empresa

---

#### US-SP-097: Catalogo de Productos Contratables

**ID:** US-SP-097
**Epica:** EP-SP-024
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero un catalogo de productos contratables (SPEI, BillPay, Openpay) con la definicion de que cuentas se crean por cada producto para que el onboarding sea automatizado y consistente.

**Criterios de Aceptacion:**
- [ ] Modelo `ContractableProduct` en DynamoDB:
  - `PK: PRODUCT_CATALOG`, `SK: PROD#{product_id}`
  - `product_id`: SPEI | BILLPAY | OPENPAY
  - `name`: "Transferencias SPEI" | "Pago de Servicios (BillPay)" | "Cobros con Tarjeta (Openpay)"
  - `description`: descripcion comercial
  - `status`: ACTIVE | INACTIVE | COMING_SOON
  - `monthly_fee`: Decimal (costo mensual base)
  - `setup_fee`: Decimal (costo de activacion)
  - `accounts_template`: definicion de cuentas a crear:
    ```json
    {
      "SPEI": [
        { "type": "CONCENTRADORA", "subtype": "SPEI", "alias_template": "Concentradora SPEI {org_name}", "provider": "monato", "provision_external": true },
        { "type": "RESERVADA_COMISIONES", "subtype": "SPEI", "alias_template": "Comisiones SPEI {org_name}", "provider": "internal", "provision_external": false },
        { "type": "CLABE_PRIVADA", "subtype": "SPEI", "alias_template": "Cuenta Principal {org_name}", "provider": "monato", "provision_external": true, "count": 1 }
      ],
      "BILLPAY": [
        { "type": "CONCENTRADORA", "subtype": "BILLPAY", "alias_template": "Concentradora BillPay {org_name}", "provider": "internal", "provision_external": false },
        { "type": "RESERVADA_COMISIONES", "subtype": "BILLPAY", "alias_template": "Comisiones BillPay {org_name}", "provider": "internal", "provision_external": false },
        { "type": "RESERVADA_FONDEO", "subtype": "BILLPAY", "alias_template": "Fondeo BillPay {org_name}", "provider": "internal", "provision_external": false }
      ],
      "OPENPAY": [
        { "type": "CONCENTRADORA", "subtype": "OPENPAY", "alias_template": "Concentradora Openpay {org_name}", "provider": "internal", "provision_external": false },
        { "type": "RESERVADA_COMISIONES", "subtype": "OPENPAY", "alias_template": "Comisiones Openpay {org_name}", "provider": "internal", "provision_external": false }
      ]
    }
    ```
  - `global_accounts`: cuentas que se crean siempre (independiente del producto):
    ```json
    [
      { "type": "RESERVADA_IVA", "alias_template": "IVA {org_name}", "provider": "internal" },
      { "type": "RESERVADA_RETENCIONES", "alias_template": "Retenciones {org_name}", "provider": "internal" }
    ]
    ```
- [ ] Endpoints:
  - `GET /api/v1/admin/products` - Catalogo completo
  - `GET /api/v1/admin/products/{product_id}` - Detalle con template de cuentas
  - `PUT /api/v1/admin/products/{product_id}` - Actualizar producto (solo Admin)
- [ ] Seed inicial con los 3 productos y sus templates
- [ ] Las cuentas globales (IVA, Retenciones) se crean UNA VEZ por organizacion, no por producto

**Tareas Tecnicas:**
1. Modelo ContractableProduct en DynamoDB
2. Dataclass con validaciones
3. Endpoints REST
4. Seed data para los 3 productos
5. Tests: CRUD, validacion de templates

**Dependencias:** Ninguna (modelo puro)
**Estimacion:** 3 dev-days

---

#### US-SP-098: Modelo de Onboarding Request

**ID:** US-SP-098
**Epica:** EP-SP-024
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero un modelo para representar el proceso de onboarding de un cliente empresa (desde solicitud hasta activacion completa) para rastrear el estado de cada paso del provisionamiento.

**Criterios de Aceptacion:**
- [ ] Modelo `OnboardingRequest` en DynamoDB:
  - `PK: ONBOARDING`, `SK: REQ#{request_id}`
  - `request_id`: UUID
  - `sp_organization_id`: organizacion del nuevo cliente
  - `organization_name`: nombre comercial
  - `organization_rfc`: RFC de la empresa
  - `organization_legal_name`: razon social
  - `contact_email`, `contact_phone`, `contact_name`: datos de contacto
  - `products_requested`: lista de product_ids contratados (ej: ["SPEI", "BILLPAY"])
  - `status`: DRAFT | SUBMITTED | VALIDATING | PROVISIONING | ACTIVE | FAILED | CANCELLED
  - `initiated_by`: user_id del Admin que inicio
  - `approved_by`: user_id que aprobo (si requiere aprobacion)
  - `provisioning_progress`: progreso detallado:
    ```json
    {
      "global_accounts": { "status": "COMPLETED", "accounts_created": ["acc-iva-123", "acc-ret-456"] },
      "SPEI": { "status": "PROVISIONING", "accounts_created": ["acc-conc-789"], "accounts_pending": ["clabe-pending"], "error": null },
      "BILLPAY": { "status": "PENDING", "accounts_created": [], "accounts_pending": ["conc-bp", "com-bp", "fond-bp"], "error": null }
    }
    ```
  - `total_accounts_expected`: numero total de cuentas a crear
  - `total_accounts_created`: numero de cuentas ya creadas
  - `error_log`: lista de errores durante provisionamiento
  - `created_at`, `updated_at`, `completed_at`
- [ ] GSI `OnboardingStatusIndex`: `PK: ONBOARDING_STATUS#{status}`, `SK: #{created_at}`
- [ ] GSI `OnboardingOrgIndex`: `PK: ONBOARDING_ORG#{sp_organization_id}`, `SK: #{created_at}`
- [ ] Status machine:
  ```
  DRAFT --> SUBMITTED --> VALIDATING --> PROVISIONING --> ACTIVE
  DRAFT --> CANCELLED
  SUBMITTED --> CANCELLED
  VALIDATING --> FAILED (datos invalidos)
  PROVISIONING --> FAILED (error de provisionamiento)
  PROVISIONING --> ACTIVE (parcial: algunos productos fallaron pero otros OK, con warning)
  ```

**Tareas Tecnicas:**
1. Modelo OnboardingRequest en DynamoDB con GSIs
2. Dataclass con validaciones
3. Status machine con transiciones validas
4. Tests del modelo y transiciones

**Dependencias:** US-SP-097 (catalogo de productos)
**Estimacion:** 3 dev-days

---

#### US-SP-099: Servicio de Creacion Automatica de Cuentas por Producto

**ID:** US-SP-099
**Epica:** EP-SP-024
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero crear automaticamente la estructura de cuentas financieras necesarias para cada producto contratado por el cliente para que no haya intervencion manual en el provisionamiento.

**Criterios de Aceptacion:**
- [ ] `AccountProvisioningService` con metodo `provision_product_accounts(org_id, product_id, onboarding_request_id)`:
  1. Leer template de cuentas del producto (US-SP-097)
  2. Por cada cuenta en el template:
     - Si `provision_external: true`: llamar a MonatoDriver para crear cuenta en Monato
     - Si `provision_external: false`: crear solo en DynamoDB (cuenta interna)
     - Reemplazar `{org_name}` en alias_template con nombre de la organizacion
     - Establecer relacion padre-hijo (concentradora -> hijas)
  3. Registrar cada cuenta creada en `provisioning_progress`
  4. Si una cuenta falla: registrar error y continuar con las demas (parcial OK)
- [ ] Creacion de cuentas globales (IVA, Retenciones):
  - Solo si la organizacion NO tiene ya estas cuentas (evitar duplicados en onboarding de segundo producto)
  - Check: `GET accounts by org_id and type = RESERVADA_IVA`
- [ ] Para producto SPEI con `provision_external: true`:
  - Llamar `MonatoDriver.create_account()` para concentradora y CLABE
  - Guardar `provider_account_id` y `clabe` asignada por Monato
  - Si Monato falla: reintentar 3 veces con backoff, luego marcar como FAILED
- [ ] Para cuentas internas:
  - Crear directamente en `modspei_accounts_prod`
  - Generar ID interno (UUID)
  - Balance inicial: $0.00
- [ ] Retornar: `{ accounts_created: [...], accounts_failed: [...], status: "COMPLETED"|"PARTIAL"|"FAILED" }`

**Tareas Tecnicas:**
1. Crear `AccountProvisioningService`
2. Logica de iteracion sobre templates
3. Integracion con MonatoDriver para cuentas externas
4. Logica de cuentas globales (evitar duplicados)
5. Manejo de errores parciales
6. Reintentos para Monato
7. Tests: provision completa, parcial, fallo Monato, duplicado de cuentas globales

**Dependencias:** US-SP-097 (templates), EP-SP-001 (Account Core), EP-SP-002 (Monato Driver)
**Estimacion:** 5 dev-days

---

#### US-SP-100: Orquestador de Onboarding

**ID:** US-SP-100
**Epica:** EP-SP-024
**Prioridad:** P0

**Historia:**
Como **Administrador SuperPago** quiero un flujo orquestado de onboarding que valide datos del cliente, cree la organizacion, provisione cuentas de todos los productos contratados, y active al cliente cuando todo este listo.

**Criterios de Aceptacion:**
- [ ] `OnboardingOrchestrator` con flujo:
  1. **SUBMITTED**: Admin envia solicitud con datos del cliente + productos
  2. **VALIDATING**: Validar datos:
     - RFC valido (formato y SAT si aplica)
     - Email valido
     - Productos solicitados estan ACTIVE en catalogo
     - Organizacion no existe ya (por RFC)
  3. **PROVISIONING**: Para cada producto contratado:
     - Llamar `AccountProvisioningService.provision_product_accounts()`
     - Actualizar `provisioning_progress` en tiempo real
     - Si un producto falla: continuar con los demas (resiliencia)
  4. **ACTIVE**: Cuando todos los productos estan provisionados
     - Configurar permisos de la organizacion segun productos contratados
     - Enviar email de bienvenida al contacto
  5. **FAILED**: Si validacion falla o todos los productos fallan
- [ ] Endpoint: `POST /api/v1/admin/onboarding`
  - Body:
    ```json
    {
      "organization_name": "Boxito",
      "organization_rfc": "BOX123456789",
      "organization_legal_name": "Boxito SA de CV",
      "contact_email": "admin@boxito.com",
      "contact_phone": "+521234567890",
      "contact_name": "Juan Perez",
      "products": ["SPEI", "BILLPAY"]
    }
    ```
  - Response: `{ request_id, status: "SUBMITTED" }`
- [ ] Endpoint: `GET /api/v1/admin/onboarding/{request_id}`
  - Detalle con provisioning_progress en tiempo real
- [ ] Endpoint: `GET /api/v1/admin/onboarding`
  - Lista de todos los onboardings con filtros por status
- [ ] Endpoint: `POST /api/v1/admin/onboarding/{request_id}/cancel`
  - Solo si status es DRAFT o SUBMITTED
- [ ] Endpoint: `POST /api/v1/admin/onboarding/{request_id}/retry`
  - Reintentar provisionamiento de productos que fallaron
  - Solo si status es FAILED
- [ ] Solo Tier 1 (Admin SuperPago) puede ejecutar

**Tareas Tecnicas:**
1. Crear `OnboardingOrchestrator`
2. Flujo completo con status machine
3. Integracion con AccountProvisioningService
4. Endpoints REST (Blueprint)
5. Validacion de datos de empresa
6. Email de bienvenida (integracion con covacha-notifications)
7. Retry de productos fallidos
8. Tests: flujo completo, validacion fallida, producto parcial, retry

**Dependencias:** US-SP-098 (modelo), US-SP-099 (provisioning)
**Estimacion:** 5 dev-days

---

#### US-SP-101: Rollback de Onboarding Fallido

**ID:** US-SP-101
**Epica:** EP-SP-024
**Prioridad:** P1

**Historia:**
Como **Sistema** quiero poder revertir un onboarding fallido (eliminar cuentas creadas, desactivar organizacion) para no dejar datos huerfanos cuando el provisionamiento falla irrecuperablemente.

**Criterios de Aceptacion:**
- [ ] `POST /api/v1/admin/onboarding/{request_id}/rollback`
  - Solo si status es FAILED
  - Solo Tier 1
- [ ] Flujo de rollback:
  1. Por cada cuenta creada en `provisioning_progress`:
     - Si cuenta externa (Monato): llamar a API de desactivacion (si disponible) o marcar como CLOSED
     - Si cuenta interna: marcar como CLOSED (soft delete)
     - Verificar que la cuenta tiene balance $0.00 (no se puede rollback si hay fondos)
  2. Actualizar OnboardingRequest status a CANCELLED
  3. Registrar rollback en audit trail
- [ ] Si alguna cuenta tiene balance > 0: rechazar rollback con error descriptivo
- [ ] Rollback parcial: si una cuenta no se puede cerrar, continuar con las demas y reportar
- [ ] Audit trail:
  ```json
  { "action": "ROLLBACK", "by": "admin-123", "at": "...", "accounts_closed": [...], "accounts_failed": [...] }
  ```

**Tareas Tecnicas:**
1. Endpoint de rollback
2. Logica de cierre de cuentas (internas y externas)
3. Validacion de balance $0
4. Audit trail
5. Tests: rollback completo, parcial, cuenta con fondos

**Dependencias:** US-SP-100 (orquestador)
**Estimacion:** 3 dev-days

---

#### US-SP-102: Agregar Producto a Cliente Existente

**ID:** US-SP-102
**Epica:** EP-SP-024
**Prioridad:** P2

**Historia:**
Como **Administrador SuperPago** quiero poder agregar un nuevo producto (ej: BillPay) a un cliente empresa que ya esta activo y tiene otros productos (ej: SPEI) para escalar la oferta sin re-onboardear.

**Criterios de Aceptacion:**
- [ ] `POST /api/v1/admin/onboarding/{org_id}/add-product`
  - Body: `{ product_id: "BILLPAY" }`
  - Response: `{ request_id, status: "PROVISIONING" }`
- [ ] Validaciones:
  - Organizacion existe y esta ACTIVE
  - Producto no esta ya contratado por la organizacion
  - Producto esta ACTIVE en catalogo
- [ ] Reutilizar `AccountProvisioningService.provision_product_accounts()` para crear solo las cuentas del nuevo producto
- [ ] NO crear cuentas globales si ya existen (IVA, Retenciones)
- [ ] Actualizar permisos de la organizacion para incluir nuevo producto
- [ ] Registrar como un nuevo OnboardingRequest de tipo `ADD_PRODUCT`
- [ ] Audit trail: "Producto BILLPAY agregado a organizacion Boxito por admin-123"

**Tareas Tecnicas:**
1. Endpoint de agregar producto
2. Validaciones de organizacion y producto
3. Reutilizacion de AccountProvisioningService
4. Actualizacion de permisos
5. Tests: agregar producto, producto duplicado, org no existe

**Dependencias:** US-SP-100 (orquestador), US-SP-099 (provisioning)
**Estimacion:** 3 dev-days

---

### EP-SP-025: mf-sp - Admin: Onboarding y Catalogo (Tier 1)

---

#### US-SP-103: Wizard de Onboarding de Cliente Empresa

**ID:** US-SP-103
**Epica:** EP-SP-025
**Prioridad:** P0

**Historia:**
Como **Administrador SuperPago** quiero un wizard de 4 pasos en mf-sp para dar de alta nuevos clientes empresa y seleccionar que productos contratan para ejecutar el onboarding desde la interfaz.

**Criterios de Aceptacion:**
- [ ] Nueva ruta: `/sp/admin/onboarding/new`
- [ ] Stepper visual de 4 pasos:
  1. **Datos del Cliente**: Nombre comercial, RFC, razon social, contacto (email, telefono, nombre). Validaciones en tiempo real.
  2. **Seleccion de Productos**: Cards de SPEI, BillPay, Openpay con toggle on/off. Muestra precio mensual y de setup. Al menos 1 producto requerido.
  3. **Resumen y Confirmacion**: Preview de datos + productos + cuentas que se crearan (lista visual de la estructura). Checkbox de "He verificado los datos".
  4. **Provisionamiento**: Barra de progreso en tiempo real. Por cada producto: indicador verde/amarillo/rojo. Al completar: boton "Ver detalle del cliente".
- [ ] Componentes:
  - `OnboardingWizardComponent` (page, stepper)
  - `ClientDataFormComponent` (step 1)
  - `ProductSelectionComponent` (step 2)
  - `OnboardingSummaryComponent` (step 3)
  - `ProvisioningProgressComponent` (step 4, polling al API cada 2 segundos)
- [ ] Responsive design
- [ ] `data-cy` attributes para E2E testing
- [ ] Tests >= 98%

**Tareas Tecnicas:**
1. Crear 5 componentes (page + 4 steps)
2. OnboardingAdapter para comunicacion con API
3. Formulario reactivo con validaciones
4. Polling de estado de provisionamiento
5. Tests unitarios de cada componente
6. Tests E2E del flujo completo

**Dependencias:** US-SP-100 (API onboarding), EP-SP-007 (mf-sp scaffold)
**Estimacion:** 5 dev-days

---

#### US-SP-104: Catalogo de Productos (Admin)

**ID:** US-SP-104
**Epica:** EP-SP-025
**Prioridad:** P1

**Historia:**
Como **Administrador SuperPago** quiero ver y gestionar el catalogo de productos contratables para saber que productos estan disponibles, modificar precios, y activar/desactivar productos.

**Criterios de Aceptacion:**
- [ ] Nueva ruta: `/sp/admin/products`
- [ ] Tabla de productos con: nombre, descripcion, estado, precio mensual, precio setup, cuentas asociadas
- [ ] Click en producto abre drawer/modal de edicion:
  - Modificar precios (mensual, setup)
  - Cambiar estado (ACTIVE, INACTIVE, COMING_SOON)
  - Ver template de cuentas (solo lectura)
- [ ] Badge de estado con color: verde (ACTIVE), gris (INACTIVE), azul (COMING_SOON)
- [ ] NO se puede eliminar un producto (solo desactivar)
- [ ] Componentes:
  - `ProductCatalogComponent` (page)
  - `ProductEditDrawerComponent`
- [ ] Tests >= 98%

**Tareas Tecnicas:**
1. Crear componentes de catalogo
2. ProductAdapter para comunicacion con API
3. Formulario de edicion
4. Tests

**Dependencias:** US-SP-097 (API catalogo)
**Estimacion:** 3 dev-days

---

#### US-SP-105: Lista de Clientes Onboarded

**ID:** US-SP-105
**Epica:** EP-SP-025
**Prioridad:** P1

**Historia:**
Como **Administrador SuperPago** quiero ver la lista de todos los clientes empresa onboarded con su estado de provisionamiento y productos contratados para monitorear el pipeline de onboarding.

**Criterios de Aceptacion:**
- [ ] Nueva ruta: `/sp/admin/onboarding`
- [ ] Tabla de onboardings con: nombre empresa, RFC, productos, estado, fecha, acciones
- [ ] Filtros: por estado, por producto, por fecha
- [ ] Acciones por fila:
  - Ver detalle (ruta: `/sp/admin/onboarding/{id}`)
  - Retry (si FAILED)
  - Rollback (si FAILED)
  - Agregar producto (si ACTIVE)
- [ ] Detalle de onboarding (`/sp/admin/onboarding/{id}`):
  - Datos del cliente
  - Productos contratados con estado de cada uno
  - Estructura de cuentas creadas (arbol visual)
  - Timeline de eventos (audit trail)
- [ ] KPIs en la parte superior: Total clientes, Activos, En proceso, Fallidos
- [ ] Componentes:
  - `OnboardingListComponent` (page)
  - `OnboardingDetailComponent` (page)
  - `AccountTreeComponent` (visualizacion de estructura de cuentas)
  - `OnboardingTimelineComponent`
- [ ] Tests >= 98%

**Tareas Tecnicas:**
1. Crear 4 componentes
2. Adapter con endpoints de onboarding
3. Arbol visual de cuentas
4. Timeline de audit trail
5. Tests

**Dependencias:** US-SP-100 (API onboarding)
**Estimacion:** 4 dev-days

---

### EP-SP-026: mf-sp - Admin: BillPay Conciliacion y Monitoreo (Tier 1)

---

#### US-SP-106: Dashboard de Conciliacion BillPay

**ID:** US-SP-106
**Epica:** EP-SP-026
**Prioridad:** P0

**Historia:**
Como **Administrador SuperPago** quiero un dashboard de conciliacion BillPay que muestre el estado global de la conciliacion, discrepancias pendientes, y tendencias para detectar problemas financieros rapidamente.

**Criterios de Aceptacion:**
- [ ] Nueva ruta: `/sp/admin/billpay/conciliation`
- [ ] KPIs principales:
  - Tasa de conciliacion (% de operaciones conciliadas exitosamente)
  - Discrepancias abiertas (PENDING) con badge de severidad
  - Ultima ejecucion (timestamp + resultado)
  - Monto total en discrepancias CRITICAL
- [ ] Graficas:
  - Tendencia de conciliacion ultimos 30 dias (linea: % conciliado por dia)
  - Distribucion de discrepancias por tipo (dona)
  - Discrepancias por organizacion (barras horizontales, top 10)
  - Tiempo promedio de resolucion (linea)
- [ ] Tabla de ultimas ejecuciones (runs):
  - Run ID, fecha, periodo, total operaciones, coincidencias, discrepancias, estado
  - Click para ver detalle del run
- [ ] Auto-refresh cada 60 segundos
- [ ] Boton "Ejecutar conciliacion manual" (trigger Lambda on-demand)
- [ ] Componentes:
  - `ConciliationDashboardComponent` (page)
  - `ConciliationKpisComponent`
  - `ConciliationTrendChartComponent`
  - `DiscrepancyDistributionChartComponent`
  - `ConciliationRunsTableComponent`
- [ ] Tests >= 98%

**Tareas Tecnicas:**
1. Crear 5 componentes
2. ConciliationAdapter para APIs de conciliacion
3. Graficas con Chart.js o similar
4. Auto-refresh con Signals
5. Trigger manual de Lambda
6. Tests

**Dependencias:** US-SP-093-096 (APIs de conciliacion)
**Estimacion:** 5 dev-days

---

#### US-SP-107: Tabla de Discrepancias con Resolucion

**ID:** US-SP-107
**Epica:** EP-SP-026
**Prioridad:** P0

**Historia:**
Como **Administrador SuperPago** quiero una tabla interactiva de discrepancias de BillPay con filtros y acciones de resolucion (aprobar, revertir, escalar) para resolver problemas de conciliacion eficientemente.

**Criterios de Aceptacion:**
- [ ] Nueva ruta: `/sp/admin/billpay/conciliation/discrepancies`
- [ ] Tabla con columnas: ID, tipo, severidad, servicio, referencia, monto local, monto proveedor, organizacion, estado resolucion, fecha, acciones
- [ ] Filtros: tipo de discrepancia, severidad, estado de resolucion, organizacion, fecha
- [ ] Badge de severidad: CRITICAL (rojo), HIGH (naranja), MEDIUM (amarillo), LOW (gris)
- [ ] Acciones por fila (boton desplegable):
  - **Aprobar**: modal con textarea de justificacion -> confirmar
  - **Revertir**: modal con confirmacion doble ("Esta seguro? Se devolvera $X.XX al cliente") -> confirmar
  - **Escalar**: modal con notas -> confirmar
  - **Descartar**: modal con textarea obligatoria -> confirmar
- [ ] Detalle de discrepancia (expandible o drawer):
  - Datos de la operacion original
  - Comparacion lado a lado: SuperPago vs Monato
  - Timeline de audit trail
- [ ] Paginacion server-side
- [ ] Componentes:
  - `DiscrepancyListComponent` (page)
  - `DiscrepancyDetailDrawerComponent`
  - `ResolutionModalComponent`
- [ ] Tests >= 98%

**Tareas Tecnicas:**
1. Crear 3 componentes
2. ConciliationAdapter (reutilizar de US-SP-106)
3. Modales de resolucion con formularios
4. Comparacion lado a lado
5. Tests

**Dependencias:** US-SP-096 (API resolucion)
**Estimacion:** 4 dev-days

---

#### US-SP-108: Monitoreo de Pagos de Servicios (Admin)

**ID:** US-SP-108
**Epica:** EP-SP-026
**Prioridad:** P1

**Historia:**
Como **Administrador SuperPago** quiero un dashboard de monitoreo de pagos de servicios de todos los clientes para ver volumen, tasa de exito, servicios mas usados, y detectar anomalias.

**Criterios de Aceptacion:**
- [ ] Nueva ruta: `/sp/admin/billpay/monitoring`
- [ ] KPIs en tiempo real:
  - Pagos hoy / esta semana / este mes
  - Volumen monetario total procesado
  - Tasa de exito (% COMPLETED)
  - Comisiones generadas
  - Pagos en PROCESSING (en vuelo)
- [ ] Graficas:
  - Volumen de pagos ultimos 30 dias (barras por dia)
  - Distribucion por servicio (dona: CFE X%, Telmex Y%, agua Z%)
  - Top 10 clientes por volumen de BillPay
  - Tasa de exito por servicio (barras horizontales)
- [ ] Tabla de pagos recientes (ultimas 100 operaciones BILLPAY):
  - Organizacion, servicio, referencia, monto, estado, canal, fecha
  - Click para ver detalle completo
- [ ] Filtro global por organizacion
- [ ] Auto-refresh cada 30 segundos
- [ ] Componentes:
  - `BillPayMonitoringComponent` (page)
  - `BillPayKpisComponent`
  - `BillPayVolumeChartComponent`
  - `ServiceDistributionChartComponent`
  - `RecentPaymentsTableComponent`
- [ ] Tests >= 98%

**Tareas Tecnicas:**
1. Crear 5 componentes
2. BillPayMonitoringAdapter
3. Graficas
4. Auto-refresh
5. Tests

**Dependencias:** US-SP-092 (API historial)
**Estimacion:** 4 dev-days

---

### EP-SP-027: mf-sp - Business: Pago de Servicios (Tier 2)

---

#### US-SP-109: Formulario de Pago de Servicios (Tier 2)

**ID:** US-SP-109
**Epica:** EP-SP-027
**Prioridad:** P0

**Historia:**
Como **Cliente Empresa** quiero un formulario para pagar servicios (luz, agua, telefono, etc.) desde mi portal donde consulto el adeudo y confirmo el pago para operar sin llamar a soporte.

**Criterios de Aceptacion:**
- [ ] Nueva ruta: `/sp/business/billpay/pay`
- [ ] Flujo de 4 pasos (stepper):
  1. **Seleccionar Servicio**: Grid de cards con icono por servicio (CFE, Telmex, agua, gas, TV, internet, recargas). Search/filter. Click selecciona.
  2. **Ingresar Referencia**: Campo de referencia (numero de contrato/servicio) con label dinamico segun servicio. Opcion: seleccionar referencia guardada.
  3. **Consultar Adeudo**: Boton "Consultar" -> muestra adeudo, titular, periodo. Si no soporta consulta: campo de monto libre. Selector de cuenta pagadora (dropdown de cuentas con saldo).
  4. **Confirmar y Pagar**: Resumen: servicio, referencia, titular, monto, comision, total, cuenta pagadora, saldo despues del pago. Boton "Pagar" con confirmacion.
- [ ] Post-pago:
  - Si COMPLETED: pantalla de exito con folio, boton "Descargar recibo" (PDF), boton "Pagar otro servicio"
  - Si PROCESSING: pantalla de "En proceso" con auto-refresh
  - Si FAILED: pantalla de error con mensaje claro y boton "Reintentar"
- [ ] Solo muestra cuentas de SU organizacion con saldo suficiente
- [ ] Componentes:
  - `BillPayWizardComponent` (page, stepper)
  - `ServiceSelectorComponent`
  - `ReferenceInputComponent`
  - `BalanceCheckComponent`
  - `PaymentConfirmComponent`
  - `PaymentResultComponent`
- [ ] Mobile-first (operadores en campo)
- [ ] `data-cy` attributes
- [ ] Tests >= 98%

**Tareas Tecnicas:**
1. Crear 6 componentes
2. BillPayAdapter para APIs
3. Formularios reactivos
4. Generacion de PDF de recibo (o descarga desde API)
5. Polling de estado para PROCESSING
6. Tests unitarios + E2E del flujo

**Dependencias:** US-SP-091 (API orquestador pago), EP-SP-011 (Tier 2 base)
**Estimacion:** 6 dev-days

---

#### US-SP-110: Historial de Pagos de Servicios (Tier 2)

**ID:** US-SP-110
**Epica:** EP-SP-027
**Prioridad:** P0

**Historia:**
Como **Cliente Empresa** quiero ver el historial de pagos de servicios de mi organizacion con filtros por servicio, fecha, y estado para tener control de mis gastos en servicios.

**Criterios de Aceptacion:**
- [ ] Nueva ruta: `/sp/business/billpay/history`
- [ ] Tabla de pagos con: fecha, servicio, referencia, monto, comision, total, estado, canal, acciones
- [ ] Filtros: servicio (dropdown), estado (multi-select), fecha desde/hasta, referencia (busqueda)
- [ ] Badge de estado: COMPLETED (verde), PROCESSING (amarillo), FAILED (rojo), REVERSED (gris)
- [ ] Acciones: Ver detalle, Descargar recibo (solo COMPLETED)
- [ ] Detalle de pago (drawer o pagina):
  - Datos completos del pago
  - Transacciones contables (debito/credito)
  - Timeline de estados
  - Comprobante descargable
- [ ] Resumen en cards encima de la tabla:
  - Total pagado este mes
  - Numero de pagos este mes
  - Comisiones este mes
  - Servicio mas pagado
- [ ] Paginacion server-side (cursor-based)
- [ ] Exportar a CSV/Excel
- [ ] Componentes:
  - `BillPayHistoryComponent` (page)
  - `PaymentDetailDrawerComponent`
  - `BillPaySummaryCardsComponent`
- [ ] Tests >= 98%

**Tareas Tecnicas:**
1. Crear 3 componentes
2. Reutilizar BillPayAdapter
3. Generacion de CSV/Excel
4. Tests

**Dependencias:** US-SP-092 (API historial)
**Estimacion:** 4 dev-days

---

#### US-SP-111: Servicios Recurrentes y Referencias Guardadas (Tier 2)

**ID:** US-SP-111
**Epica:** EP-SP-027
**Prioridad:** P1

**Historia:**
Como **Cliente Empresa** quiero guardar mis referencias de servicios (ej: mi numero de contrato de CFE) y configurar pagos como favoritos para pagar rapidamente sin ingresar datos cada vez.

**Criterios de Aceptacion:**
- [ ] Nueva ruta: `/sp/business/billpay/services`
- [ ] Grid de "Mis Servicios" (referencias guardadas):
  - Card por referencia: icono del servicio, nombre, referencia, alias personalizado, ultimo pago, monto
  - Boton "Pagar" directo (salta al paso 3 del wizard con datos pre-cargados)
  - Boton "Editar" (cambiar alias)
  - Boton "Eliminar" (con confirmacion)
- [ ] Boton "Agregar servicio" -> mini-wizard: seleccionar servicio -> ingresar referencia -> dar alias -> guardar
- [ ] Limite: 50 referencias por organizacion (mostrar contador)
- [ ] Orden configurable (drag & drop o prioridad numerica)
- [ ] Componentes:
  - `SavedServicesComponent` (page)
  - `SavedServiceCardComponent`
  - `AddServiceModalComponent`
- [ ] Tests >= 98%

**Tareas Tecnicas:**
1. Crear 3 componentes
2. Integracion con API de saved-references
3. Drag & drop para ordenamiento
4. Tests

**Dependencias:** US-SP-092 (API saved-references)
**Estimacion:** 3 dev-days

---

#### US-SP-112: Conciliacion de Mis Pagos (Tier 2)

**ID:** US-SP-112
**Epica:** EP-SP-027
**Prioridad:** P2

**Historia:**
Como **Cliente Empresa** quiero ver el estado de conciliacion de mis pagos de servicios para saber si todos mis pagos fueron aplicados correctamente por los proveedores.

**Criterios de Aceptacion:**
- [ ] Nueva ruta: `/sp/business/billpay/conciliation`
- [ ] Vista simplificada (no es la vista admin completa):
  - Indicador general: "Todos tus pagos estan conciliados" (verde) o "X pagos con observaciones" (amarillo/rojo)
  - Solo muestra pagos de SU organizacion
- [ ] Tabla de pagos con observaciones:
  - Fecha, servicio, referencia, monto, estado en SuperPago, estado en proveedor, tipo de discrepancia
  - Solo muestra pagos con discrepancias (no los conciliados)
- [ ] Detalle de discrepancia (expandible):
  - Explicacion en lenguaje simple: "Tu pago de $850.00 a CFE fue registrado pero el proveedor aun no confirma la aplicacion"
  - Recomendacion: "Si tu recibo no refleja el pago despues de 24 horas, contacta a soporte"
- [ ] El cliente NO puede resolver discrepancias (solo Tier 1)
- [ ] Componentes:
  - `MyPaymentsConciliationComponent` (page)
  - `DiscrepancyExplanationComponent`
- [ ] Tests >= 98%

**Tareas Tecnicas:**
1. Crear 2 componentes
2. Reutilizar ConciliationAdapter con filtro por org_id
3. Mensajes de explicacion en lenguaje simple
4. Tests

**Dependencias:** US-SP-096 (API discrepancias por org)
**Estimacion:** 3 dev-days

---

### EP-SP-028: mf-sp - Personal: Mis Servicios (Tier 3)

---

#### US-SP-113: Pagar Mis Servicios (Tier 3)

**ID:** US-SP-113
**Epica:** EP-SP-028
**Prioridad:** P0

**Historia:**
Como **Usuario Final** quiero un formulario simple para pagar mis servicios (luz, agua, telefono) desde mi portal personal para no tener que ir a una tienda o usar otro medio.

**Criterios de Aceptacion:**
- [ ] Nueva ruta: `/sp/personal/billpay`
- [ ] Flujo simplificado (todo en una pantalla, no wizard):
  1. Mis servicios guardados en la parte superior (cards grandes con boton "Pagar")
  2. "Pagar otro servicio" debajo: seleccionar servicio -> referencia -> consultar adeudo -> pagar
- [ ] Quick pay: click en servicio guardado -> muestra adeudo -> confirmar y pagar (2 clicks)
- [ ] Post-pago: pantalla de exito con recibo descargable
- [ ] Solo 1 cuenta (su cuenta privada), no hay selector de cuenta
- [ ] Validacion de saldo: si no tiene saldo suficiente, mostrar mensaje claro con saldo actual
- [ ] Mobile-first design (optimizado para telefono)
- [ ] Componentes:
  - `PersonalBillPayComponent` (page)
  - `QuickPayCardComponent`
  - `SimplePaymentFormComponent`
- [ ] Tests >= 98%

**Tareas Tecnicas:**
1. Crear 3 componentes
2. Reutilizar BillPayAdapter
3. Mobile-first CSS
4. Tests

**Dependencias:** US-SP-109 (comparte adapters), EP-SP-012 (Tier 3 base)
**Estimacion:** 4 dev-days

---

#### US-SP-114: Historial de Mis Pagos (Tier 3)

**ID:** US-SP-114
**Epica:** EP-SP-028
**Prioridad:** P0

**Historia:**
Como **Usuario Final** quiero ver el historial de mis pagos de servicios con recibos descargables para tener evidencia de mis pagos.

**Criterios de Aceptacion:**
- [ ] Nueva ruta: `/sp/personal/billpay/history`
- [ ] Lista simple (no tabla compleja):
  - Cards por pago: fecha, servicio (con icono), referencia, monto, estado
  - Click abre detalle con boton "Descargar recibo"
  - Scroll infinito (no paginacion explicita)
- [ ] Filtros simples: "Todos" | "Este mes" | "Ultimos 3 meses" (tabs)
- [ ] Resumen en la parte superior: "Este mes has pagado $X,XXX.XX en N servicios"
- [ ] Componentes:
  - `PersonalPaymentHistoryComponent` (page)
  - `PaymentCardComponent`
- [ ] Tests >= 98%

**Tareas Tecnicas:**
1. Crear 2 componentes
2. Reutilizar BillPayAdapter con filtro de usuario
3. Scroll infinito con IntersectionObserver
4. Tests

**Dependencias:** US-SP-092 (API historial)
**Estimacion:** 3 dev-days

---

#### US-SP-115: Gestionar Mis Servicios Guardados (Tier 3)

**ID:** US-SP-115
**Epica:** EP-SP-028
**Prioridad:** P1

**Historia:**
Como **Usuario Final** quiero guardar mis servicios frecuentes (mi numero de luz, mi telefono) para pagar rapidamente la proxima vez sin ingresar datos.

**Criterios de Aceptacion:**
- [ ] Integrado en `/sp/personal/billpay` (no ruta separada)
- [ ] Seccion "Mis servicios" en la pagina principal de BillPay personal
- [ ] Agregar servicio: seleccionar tipo -> ingresar referencia -> dar nombre corto -> guardar
- [ ] Editar: cambiar nombre/alias
- [ ] Eliminar con confirmacion
- [ ] Maximo 10 servicios guardados (personas naturales, no necesitan 50)
- [ ] Iconos grandes y claros para cada tipo de servicio
- [ ] Componentes:
  - `ManageSavedServicesComponent` (seccion, no page)
  - `AddServiceBottomSheetComponent` (bottom sheet en mobile)
- [ ] Tests >= 98%

**Tareas Tecnicas:**
1. Crear 2 componentes
2. Reutilizar API de saved-references
3. Bottom sheet mobile pattern
4. Tests

**Dependencias:** US-SP-111 (comparte API)
**Estimacion:** 2 dev-days

---

#### US-SP-116: Notificaciones de Pago (Tier 3)

**ID:** US-SP-116
**Epica:** EP-SP-028
**Prioridad:** P2

**Historia:**
Como **Usuario Final** quiero recibir notificaciones cuando mis pagos de servicios se completen o fallen para saber el resultado sin tener que entrar al portal.

**Criterios de Aceptacion:**
- [ ] Al completar un pago BILLPAY de un usuario Tier 3:
  - Push notification (si la app soporta)
  - Email al usuario con resumen del pago
  - Notificacion in-app (badge en el icono de campana)
- [ ] Al fallar un pago:
  - Email: "Tu pago de $X a CFE no se pudo procesar. Razon: [mensaje]. Intenta de nuevo."
  - Notificacion in-app con link a reintentar
- [ ] Preferencias de notificacion configurables:
  - `/sp/personal/settings/notifications`
  - Toggles: email si/no, push si/no, in-app siempre activo
- [ ] Componentes:
  - `PaymentNotificationBannerComponent` (in-app, toast o badge)
  - `NotificationPreferencesComponent`
- [ ] Tests >= 98%

**Tareas Tecnicas:**
1. Crear 2 componentes
2. Integracion con covacha-notifications para email
3. Notificacion in-app via SharedState o BroadcastChannel
4. Preferencias en localStorage o API
5. Tests

**Dependencias:** US-SP-113 (contexto de pagos Tier 3), EP-SP-010 (Notificaciones)
**Estimacion:** 3 dev-days

---

## Roadmap

### Fase 1: BillPay Backend (Sprint 8-10)

| Sprint | Epica | User Stories | Dev-Days |
|--------|-------|-------------|----------|
| 8-9 | EP-SP-021 (Monato BillPay Driver) | US-SP-085, 086, 087, 088 | 16 |
| 9-10 | EP-SP-022 (Operacion BILLPAY) | US-SP-089, 090, 091, 092 | 16 |

**Razonamiento:** El driver de Monato BillPay es prerequisito de todo lo demas. La operacion BILLPAY necesita el driver funcional. Ambas pueden solaparse: el driver se completa en sprint 8-9 y la operacion transaccional arranca en sprint 9.

### Fase 2: Onboarding + Conciliacion (Sprint 8-11, paralela)

| Sprint | Epica | User Stories | Dev-Days |
|--------|-------|-------------|----------|
| 8-10 | EP-SP-024 (Onboarding) | US-SP-097, 098, 099, 100, 101, 102 | 22 |
| 10-11 | EP-SP-023 (Conciliacion) | US-SP-093, 094, 095, 096 | 16 |

**Razonamiento:** El onboarding es independiente de BillPay (es un flujo de provisionamiento de cuentas). Puede desarrollarse en paralelo por un equipo diferente. La conciliacion requiere que haya operaciones BILLPAY para conciliar, asi que va despues de EP-SP-022.

### Fase 3: Frontend (Sprint 10-12)

| Sprint | Epica | User Stories | Dev-Days |
|--------|-------|-------------|----------|
| 10-11 | EP-SP-025 (Admin Onboarding) | US-SP-103, 104, 105 | 12 |
| 10-11 | EP-SP-027 (Business BillPay) | US-SP-109, 110, 111, 112 | 16 |
| 11-12 | EP-SP-026 (Admin Conciliacion) | US-SP-106, 107, 108 | 13 |
| 11-12 | EP-SP-028 (Personal BillPay) | US-SP-113, 114, 115, 116 | 12 |

**Razonamiento:** El frontend se construye cuando las APIs estan listas. EP-SP-025 y EP-SP-027 pueden desarrollarse en paralelo (diferentes tiers). EP-SP-026 espera a que la conciliacion este implementada. EP-SP-028 reutiliza componentes de EP-SP-027.

### Resumen de Estimaciones

| Epica | User Stories | Dev-Days | Sprint |
|-------|-------------|----------|--------|
| EP-SP-021 | 4 (US-SP-085 a 088) | 16 | 8-9 |
| EP-SP-022 | 4 (US-SP-089 a 092) | 16 | 9-10 |
| EP-SP-023 | 4 (US-SP-093 a 096) | 16 | 10-11 |
| EP-SP-024 | 6 (US-SP-097 a 102) | 22 | 8-10 |
| EP-SP-025 | 3 (US-SP-103 a 105) | 12 | 10-11 |
| EP-SP-026 | 3 (US-SP-106 a 108) | 13 | 11-12 |
| EP-SP-027 | 4 (US-SP-109 a 112) | 16 | 10-11 |
| EP-SP-028 | 4 (US-SP-113 a 116) | 12 | 11-12 |
| **TOTAL** | **32** | **123** | 8-12 |

### Paralelismo Sugerido (2 equipos)

```
Sprint 8:  [Equipo A: EP-SP-021 Driver]  [Equipo B: EP-SP-024 Onboarding]
Sprint 9:  [Equipo A: EP-SP-021 + 022]   [Equipo B: EP-SP-024 cont.]
Sprint 10: [Equipo A: EP-SP-022 + 023]   [Equipo B: EP-SP-025 + 027 Frontend]
Sprint 11: [Equipo A: EP-SP-023 cont.]   [Equipo B: EP-SP-026 + 027 + 028]
Sprint 12: [Buffer + EP-SP-028]           [Buffer + QA + Deploy]
```

---

## Grafo de Dependencias

```
EXISTENTES:
EP-SP-001 (Account) ─────────+
EP-SP-002 (Monato Driver) ───+──> EP-SP-024 (Onboarding)
EP-SP-003 (Ledger) ──────────+         |
                              |         v
EP-SP-018/US-SP-071 ─────────+──> EP-SP-021 (Monato BillPay Driver)
(BillPayProvider interface)   |         |
                              |         v
                              +──> EP-SP-022 (Operacion BILLPAY)
                                        |
                                        v
                                  EP-SP-023 (Conciliacion)
                                        |
                                        v
                                  EP-SP-026 (Frontend Admin Conciliacion)

EP-SP-007 (Scaffold) ───+──> EP-SP-025 (Frontend Admin Onboarding)
EP-SP-011 (Tier 2) ─────+──> EP-SP-027 (Frontend Business BillPay)
EP-SP-012 (Tier 3) ─────+──> EP-SP-028 (Frontend Personal BillPay)
EP-SP-013 (Shared) ─────+

ENTRE LAS NUEVAS:
EP-SP-021 ──> EP-SP-022 ──> EP-SP-023 ──> EP-SP-026
EP-SP-024 ──> EP-SP-025
EP-SP-022 ──> EP-SP-027 ──> EP-SP-028
```

---

## Riesgos y Mitigaciones

### R1: API de Monato BillPay cambia o tiene limitaciones no documentadas

**Probabilidad:** Media
**Impacto:** Alto
**Mitigacion:**
- Strategy Pattern permite cambiar driver sin impacto en negocio
- Implementar mock completo de Monato para desarrollo y testing
- Tener comunicacion directa con equipo de Monato durante implementacion
- Plan B: driver SIPREL como alternativa

### R2: Conciliacion encuentra muchas discrepancias inicialmente

**Probabilidad:** Alta (en las primeras semanas)
**Impacto:** Medio
**Mitigacion:**
- Ejecutar conciliacion en modo "dry-run" primero (sin alertas)
- Umbrales altos inicialmente, bajar gradualmente
- Equipo de operaciones informado para resolver manualmente los primeros dias
- Auto-resolucion de PENDING_CONFIRMATION reduce ruido

### R3: Provisionamiento en Monato falla durante onboarding

**Probabilidad:** Media
**Impacto:** Alto
**Mitigacion:**
- Retry automatico con backoff exponencial
- Rollback parcial: cerrar lo que se creo
- Estado FAILED con retry manual disponible
- Alertas al equipo cuando un onboarding falla

### R4: Performance de conciliacion con alto volumen

**Probabilidad:** Baja (inicialmente), Alta (a escala)
**Impacto:** Medio
**Mitigacion:**
- Lambda con timeout de 5 minutos (suficiente para ~10K operaciones)
- Si crece: dividir en batches por organizacion
- Hash join para comparacion O(n) en lugar de nested loop O(n^2)
- Indices DynamoDB optimizados para queries de periodo

### R5: Complejidad del wizard de onboarding

**Probabilidad:** Media
**Impacto:** Medio
**Mitigacion:**
- Wizard divide la complejidad en 4 pasos simples
- Validacion en cada paso antes de avanzar
- Polling de progreso para feedback en tiempo real
- Boton de retry para no empezar de cero

### R6: Sobrecarga del equipo con 8 epicas simultaneas

**Probabilidad:** Alta
**Impacto:** Alto
**Mitigacion:**
- Paralelismo con 2 equipos (backend + frontend)
- Sprint 12 como buffer
- Priorizar P0 stories primero, diferir P2 si es necesario
- EP-SP-028 (Tier 3) puede diferirse completamente al siguiente ciclo si es necesario

---

## Prioridades de Corte (si hay que reducir scope)

### Must Have (P0) - 76 dev-days

| Epica | Stories P0 | Dev-Days |
|-------|-----------|----------|
| EP-SP-021 | US-SP-085, 086, 087 | 12 |
| EP-SP-022 | US-SP-089, 090, 091 | 12 |
| EP-SP-023 | US-SP-093, 094 | 8 |
| EP-SP-024 | US-SP-097, 098, 099, 100 | 16 |
| EP-SP-025 | US-SP-103 | 5 |
| EP-SP-026 | US-SP-106, 107 | 9 |
| EP-SP-027 | US-SP-109, 110 | 10 |
| EP-SP-028 | US-SP-113, 114 | 7 |

### Should Have (P1) - 34 dev-days

US-SP-088, US-SP-092, US-SP-095, US-SP-096, US-SP-101, US-SP-104, US-SP-105, US-SP-108, US-SP-111, US-SP-115

### Nice to Have (P2) - 13 dev-days

US-SP-102, US-SP-112, US-SP-116

### Si hay que cortar: eliminar EP-SP-028 completo (-12 days) y diferir P2 stories (-13 days)

**Scope minimo viable: 76 dev-days (P0 only)**

---

## Definition of Done (Global)

- [ ] Codigo implementado y commiteado
- [ ] Tests unitarios >= 98% coverage
- [ ] Tests E2E para flujos criticos (pagos, onboarding)
- [ ] Ningun archivo > 1000 lineas
- [ ] Ninguna funcion > 50 lineas
- [ ] Build de produccion exitoso (`yarn build:prod` para frontend, `pytest -v` para backend)
- [ ] Revisado por al menos 1 persona (PR aprobado)
- [ ] Documentacion de API actualizada (Swagger/OpenAPI)
- [ ] Sin datos sensibles en logs
- [ ] Idempotencia verificada en operaciones financieras
- [ ] Responsive design verificado en mobile
