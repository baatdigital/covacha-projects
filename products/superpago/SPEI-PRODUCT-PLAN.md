# SuperPago SPEI - Product Plan Completo

**Fecha**: 2026-02-14
**Product Owner**: SuperPago
**Proveedor SPEI**: Monato Fincore
**Estado**: Planificacion

---

## Tabla de Contenidos

1. [Vision del Producto](#vision-del-producto)
2. [Roles Involucrados](#roles-involucrados)
3. [Modelo de Cuentas](#modelo-de-cuentas)
4. [Mapa de Epicas](#mapa-de-epicas)
5. [Epicas Detalladas](#epicas-detalladas)
6. [User Stories Detalladas](#user-stories-detalladas)
7. [Orden de Implementacion (Roadmap)](#orden-de-implementacion)
8. [Grafo de Dependencias](#grafo-de-dependencias)
9. [Riesgos y Mitigaciones](#riesgos-y-mitigaciones)
10. [Definition of Done Global](#definition-of-done-global)

---

## Vision del Producto

SuperPago revende servicios SPEI a traves de Monato Fincore, ofreciendo a clientes empresariales la capacidad de:

- Abrir cuentas CLABE para recibir y enviar dinero via SPEI
- Gestionar una estructura jerarquica de cuentas (concentradora, dispersion, CLABE, reservada)
- Realizar transferencias SPEI out a cualquier banco en Mexico
- Recibir depositos SPEI in con reconciliacion automatica
- Mantener contabilidad de partida doble (double-entry) para cada movimiento
- Escalar a multiples proveedores SPEI en el futuro (STP, Arcus, Mastercard)

### Repositorios Involucrados

| Repositorio | Funcion | Puerto Dev |
|-------------|---------|------------|
| `covacha-payment` | Account Core Engine + Monato Driver | 5004 |
| `covacha-webhook` | Webhook handler SPEI (money_in, status) | 5006 |
| `mf-sp` | Micro-frontend Angular 21 (nuevo MF) | 4212 |
| `mf-core` | Shell - registrar remote mfSP | N/A |

---

## Roles Involucrados

### R1: Administrador de Plataforma (SuperPago)

Persona interna de SuperPago que gestiona la infraestructura financiera.

**Responsabilidades:**
- Crear y configurar cuentas concentradoras
- Monitorear todas las transacciones del ecosistema
- Gestionar limites y politicas globales
- Ver reconciliacion y auditoria
- Registrar y gestionar proveedores SPEI

### R2: Cliente Empresarial

Empresa que usa SuperPago para operar sus finanzas via SPEI.

**Responsabilidades:**
- Solicitar apertura de cuentas CLABE
- Enviar transferencias SPEI out
- Ver historial de movimientos y saldos
- Configurar cuentas de dispersion y reservadas
- Aprobar transferencias que requieran autorizacion

### R3: Sistema (Operaciones Automaticas)

Procesos automatizados que operan sin intervencion humana.

**Responsabilidades:**
- Procesar webhooks de money_in
- Ejecutar reconciliacion automatica
- Registrar asientos contables de partida doble
- Notificar eventos (depositos, transferencias, errores)
- Reintentar operaciones fallidas con idempotencia

---

## Modelo de Cuentas

### Jerarquia

```
CONCENTRADORA (Organization-level)
|
+-- CLABE (cuenta operativa, SPEI in + out)
|   |
|   +-- RESERVADA (IVA, retenciones - SPEI out a 1 destino fijo)
|
+-- DISPERSION (no SPEI in, SI SPEI out a externos)
|
+-- CLABE (otra cuenta operativa)
```

### Tipos de Cuenta

| Tipo | SPEI In | SPEI Out | Alimentacion | Proposito |
|------|---------|----------|--------------|-----------|
| CONCENTRADORA | No | No | Recibe de CLABEs hijas (interno) | Pool de fondos, opera como nodo raiz |
| CLABE | Si | Si | SPEI in externo | Cuenta operativa completa |
| DISPERSION | No | Si (a cualquier externo) | Movimiento interno desde concentradora/CLABE | Pagos a proveedores, nomina |
| RESERVADA | No | Si (1 destino fijo) | Movimiento interno | IVA, retenciones, reservas |

### Reglas de Negocio del Grafo

1. Toda cuenta pertenece a una `organization_id`
2. Una CONCENTRADORA puede tener N hijas (CLABE, DISPERSION, RESERVADA)
3. Una CLABE puede tener N sub-cuentas (RESERVADA)
4. Los movimientos internos (entre cuentas de la misma org) son instantaneos y sin costo
5. Los movimientos SPEI out pasan por Monato y tienen costo
6. Cada movimiento genera 2 asientos contables (debito + credito)
7. El saldo de una cuenta = SUM(creditos) - SUM(debitos) en el ledger

---

## Mapa de Epicas

| ID | Epica | Complejidad | Sprint | Dependencias |
|----|-------|-------------|--------|--------------|
| EP-SP-001 | Account Core Engine | XL | 1-2 | Ninguna |
| EP-SP-002 | Monato Driver (Strategy Pattern) | L | 1-2 | Ninguna (paralela a EP-001) |
| EP-SP-003 | Double-Entry Ledger | L | 2-3 | EP-SP-001 |
| EP-SP-004 | SPEI Out (Transferencias Salientes) | L | 3 | EP-SP-001, EP-SP-002, EP-SP-003 |
| EP-SP-005 | Webhook Handler SPEI In | L | 3 | EP-SP-001, EP-SP-002, EP-SP-003 |
| EP-SP-006 | Movimientos Internos (Grafo) | M | 3-4 | EP-SP-001, EP-SP-003 |
| EP-SP-007 | mf-sp - Scaffold y Dashboard | L | 2-3 | EP-SP-001 (API lista) |
| EP-SP-008 | mf-sp - Transferencias y Movimientos | L | 4 | EP-SP-004, EP-SP-007 |
| EP-SP-009 | Reconciliacion y Auditoria | M | 4-5 | EP-SP-003, EP-SP-004, EP-SP-005 |
| EP-SP-010 | Limites, Politicas y Notificaciones | M | 5-6 | EP-SP-004, EP-SP-005 |

---

## Epicas Detalladas

---

### EP-SP-001: Account Core Engine

**Descripcion:**
Motor de cuentas financieras en `covacha-payment`. Modela la jerarquia de cuentas (CONCENTRADORA, CLABE, DISPERSION, RESERVADA) como un grafo dirigido con relaciones padre-hijo. Cada cuenta tiene tipo, estado, saldo calculado, y metadata. Este es el corazon del sistema SPEI.

**User Stories:**
- US-SP-001, US-SP-002, US-SP-003, US-SP-004, US-SP-005

**Criterios de Aceptacion de la Epica:**
- [ ] Se pueden crear los 4 tipos de cuenta con validaciones de jerarquia
- [ ] El grafo de relaciones padre-hijo se persiste en DynamoDB
- [ ] Cada cuenta tiene un estado (PENDING, ACTIVE, FROZEN, CLOSED)
- [ ] Las transiciones de estado siguen reglas de negocio validadas
- [ ] El saldo se calcula desde el ledger (no se almacena como campo directo)
- [ ] API REST CRUD completa con paginacion y filtros
- [ ] Cobertura de tests >= 98%
- [ ] Documentacion OpenAPI de todos los endpoints

**Dependencias:** Ninguna (puede empezar de inmediato)

**Complejidad:** XL (5+ user stories, modelado de dominio complejo)

**Repositorio:** `covacha-payment`

---

### EP-SP-002: Monato Driver (Strategy Pattern)

**Descripcion:**
Capa de abstraccion multi-proveedor para operaciones SPEI. Usa Strategy Pattern para que el sistema sea agnostico al proveedor. Hoy implementa Monato Fincore, manana puede agregar STP, Arcus, Mastercard sin cambiar la logica de negocio. Se construye como workspace separado o modulo independiente dentro de `covacha-payment`.

**User Stories:**
- US-SP-006, US-SP-007, US-SP-008, US-SP-009

**Criterios de Aceptacion de la Epica:**
- [ ] Interface `SPEIProvider` definida con todos los metodos necesarios
- [ ] `MonatoDriver` implementa `SPEIProvider` completamente
- [ ] Crear cuenta privada en Monato y obtener CLABE
- [ ] Crear instrumento de pago en Monato
- [ ] Ejecutar money_out via Monato
- [ ] Registrar webhook en Monato
- [ ] Consultar catalogo de participantes SPEI
- [ ] Penny validation funcional
- [ ] Manejo de errores con retry y circuit breaker
- [ ] Idempotency key en todas las operaciones mutativas
- [ ] Logs estructurados para debugging de integracion
- [ ] Tests con mocks del API de Monato >= 98% coverage

**Dependencias:** Ninguna (puede empezar en paralelo con EP-SP-001)

**Complejidad:** L (integracion con API externa, error handling critico)

**Repositorio:** `covacha-payment` (modulo `drivers/monato/`)

---

### EP-SP-003: Double-Entry Ledger

**Descripcion:**
Sistema contable de partida doble. Cada movimiento financiero (SPEI in, SPEI out, movimiento interno, comision) genera exactamente 2 asientos: un debito y un credito. El saldo de cualquier cuenta se calcula sumando sus asientos. Esto garantiza consistencia financiera y audit trail completo.

**User Stories:**
- US-SP-010, US-SP-011, US-SP-012, US-SP-013

**Criterios de Aceptacion de la Epica:**
- [ ] Modelo `LedgerEntry` con debito/credito, cuenta, monto, referencia
- [ ] Toda transaccion genera exactamente 2 entries (SUM debitos = SUM creditos)
- [ ] Saldo de cuenta = SUM(creditos) - SUM(debitos) del ledger
- [ ] No se puede editar ni eliminar un entry (append-only)
- [ ] Soporte para reversos (genera entries inversos, no borra)
- [ ] Query de estado de cuenta por rango de fechas
- [ ] Balance trial: verificacion de que el sistema esta balanceado
- [ ] Performance: calculo de saldo en < 200ms para cuentas con 10k+ entries
- [ ] Tests >= 98% con escenarios de concurrencia

**Dependencias:** EP-SP-001 (necesita el modelo de cuentas)

**Complejidad:** L (logica contable precisa, performance critica)

**Repositorio:** `covacha-payment`

---

### EP-SP-004: SPEI Out (Transferencias Salientes)

**Descripcion:**
Flujo completo de transferencias SPEI out. Un usuario o sistema inicia una transferencia desde una cuenta CLABE o DISPERSION hacia una cuenta externa en cualquier banco de Mexico. El flujo incluye: validacion de saldo, creacion de asientos contables, envio via Monato, tracking de estado, y notificacion del resultado.

**User Stories:**
- US-SP-014, US-SP-015, US-SP-016, US-SP-017

**Criterios de Aceptacion de la Epica:**
- [ ] Transferencia SPEI out desde cuenta CLABE a cuenta externa
- [ ] Transferencia SPEI out desde cuenta DISPERSION a cuenta externa
- [ ] Cuenta RESERVADA solo permite SPEI out al destino fijo configurado
- [ ] Cuenta CONCENTRADORA no permite SPEI out (bloqueado)
- [ ] Validacion de saldo suficiente antes de enviar
- [ ] Idempotency key para evitar transferencias duplicadas
- [ ] Estados de transferencia: PENDING -> PROCESSING -> COMPLETED/FAILED/REVERSED
- [ ] Asientos contables se crean al iniciar (hold) y se confirman/reversan al completar
- [ ] Penny validation antes de primera transferencia a cuenta nueva
- [ ] Registro de beneficiarios frecuentes
- [ ] Comision SPEI se registra como asiento separado

**Dependencias:** EP-SP-001, EP-SP-002, EP-SP-003

**Complejidad:** L (flujo financiero critico, muchos edge cases)

**Repositorio:** `covacha-payment`

---

### EP-SP-005: Webhook Handler SPEI In

**Descripcion:**
Handler de webhooks de Monato para depositos entrantes (money_in). Cuando alguien envia dinero via SPEI a una CLABE de SuperPago, Monato notifica via webhook. El handler valida la firma, identifica la cuenta destino, crea asientos contables, y notifica al usuario. Se implementa en `covacha-webhook` en la ruta `/webhook/spei/monato/`.

**User Stories:**
- US-SP-018, US-SP-019, US-SP-020, US-SP-021

**Criterios de Aceptacion de la Epica:**
- [ ] Endpoint POST `/webhook/spei/monato/` recibe eventos de Monato
- [ ] Validacion de firma/token del webhook
- [ ] Procesamiento idempotente (mismo evento 2 veces = 1 sola operacion)
- [ ] Identifica cuenta CLABE destino en el sistema
- [ ] Crea asientos contables de credito en la cuenta CLABE
- [ ] Si la CLABE tiene concentradora padre, propaga saldo
- [ ] Notifica al usuario (push, email, o webhook interno)
- [ ] Manejo de eventos desconocidos (log + ignore, no falla)
- [ ] Retry queue para procesamiento fallido (SQS dead letter)
- [ ] Logs detallados para debugging de integracion
- [ ] Response 200 rapido (< 500ms), procesamiento async

**Dependencias:** EP-SP-001, EP-SP-002, EP-SP-003

**Complejidad:** L (integracion asincrona, idempotencia critica)

**Repositorio:** `covacha-webhook`

---

### EP-SP-006: Movimientos Internos (Grafo)

**Descripcion:**
Transferencias entre cuentas de la misma organizacion. Son instantaneas, sin costo, y siguen las reglas del grafo de cuentas. Ejemplos: mover fondos de CLABE a CONCENTRADORA, dispersar de CONCENTRADORA a DISPERSION, alimentar cuenta RESERVADA.

**User Stories:**
- US-SP-022, US-SP-023, US-SP-024

**Criterios de Aceptacion de la Epica:**
- [ ] Transferencia interna entre cuentas de la misma organizacion
- [ ] Validacion de reglas del grafo (solo movimientos permitidos por tipo)
- [ ] Operacion instantanea (no pasa por SPEI)
- [ ] Sin costo (comision = 0)
- [ ] Asientos contables de partida doble se generan
- [ ] Soporte para dispersion masiva (1 origen -> N destinos en 1 operacion)
- [ ] Rollback si alguna transferencia del batch falla
- [ ] Reglas de movimiento validadas:
  - CLABE -> CONCENTRADORA (subida de fondos)
  - CONCENTRADORA -> DISPERSION (alimentacion)
  - CONCENTRADORA -> RESERVADA (alimentacion)
  - CLABE -> RESERVADA (alimentacion directa)
- [ ] Movimientos no permitidos devuelven error descriptivo

**Dependencias:** EP-SP-001, EP-SP-003

**Complejidad:** M (logica de grafo, reglas de validacion)

**Repositorio:** `covacha-payment`

---

### EP-SP-007: mf-sp - Scaffold y Dashboard

**Descripcion:**
Creacion del nuevo micro-frontend `mf-sp` (SuperPago SPEI) con Angular 21 y Native Federation. Incluye scaffold del proyecto, registro en el Shell (mf-core), y las paginas fundamentales: dashboard de cuentas, detalle de cuenta, y creacion de cuenta.

**User Stories:**
- US-SP-025, US-SP-026, US-SP-027, US-SP-028

**Criterios de Aceptacion de la Epica:**
- [ ] Proyecto Angular 21 creado con estructura hexagonal
- [ ] Native Federation configurado (puerto 4212, remote name mfSP)
- [ ] Registrado en mf-core como remote
- [ ] SharedStateService implementado (lectura de covacha:auth, covacha:user)
- [ ] HttpService implementado con headers requeridos
- [ ] Layout base con sidebar de navegacion SPEI
- [ ] Dashboard: lista de cuentas con saldo, tipo, estado
- [ ] Detalle de cuenta: info, saldo, ultimos movimientos
- [ ] Formulario de creacion de cuenta con wizard
- [ ] Visualizacion del grafo de cuentas (arbol jerarquico)
- [ ] Responsive design
- [ ] Tests >= 98%

**Dependencias:** EP-SP-001 (necesita API de cuentas)

**Complejidad:** L (nuevo MF completo, multiples paginas)

**Repositorio:** `mf-sp` (nuevo), `mf-core` (registro del remote)

---

### EP-SP-008: mf-sp - Transferencias y Movimientos

**Descripcion:**
UI para ejecutar transferencias SPEI out, movimientos internos, y ver historial de movimientos. Incluye formularios de transferencia con validaciones, confirmacion, tracking de estado, y tabla de movimientos con filtros y paginacion.

**User Stories:**
- US-SP-029, US-SP-030, US-SP-031, US-SP-032

**Criterios de Aceptacion de la Epica:**
- [ ] Formulario de transferencia SPEI out con:
  - Seleccion de cuenta origen
  - CLABE destino con validacion de formato
  - Busqueda de banco por CLABE (catalogo de participantes)
  - Concepto de pago
  - Monto con validacion de saldo
  - Confirmacion con resumen antes de enviar
- [ ] Formulario de movimiento interno con:
  - Seleccion de cuenta origen y destino (filtrado por reglas del grafo)
  - Monto y concepto
- [ ] Tabla de movimientos con:
  - Filtros por tipo, estado, fecha, cuenta
  - Paginacion server-side
  - Export a CSV/Excel
- [ ] Estado de transferencia en tiempo real (polling o SSE)
- [ ] Registro de beneficiarios frecuentes
- [ ] Tests >= 98%

**Dependencias:** EP-SP-004, EP-SP-006, EP-SP-007

**Complejidad:** L (formularios complejos, multiples validaciones)

**Repositorio:** `mf-sp`

---

### EP-SP-009: Reconciliacion y Auditoria

**Descripcion:**
Sistema de reconciliacion automatica que compara los registros internos del ledger con los reportes de Monato. Detecta discrepancias, genera alertas, y provee herramientas de auditoria para el equipo de operaciones.

**User Stories:**
- US-SP-033, US-SP-034, US-SP-035

**Criterios de Aceptacion de la Epica:**
- [ ] Job de reconciliacion diaria (compara ledger vs Monato)
- [ ] Detecta discrepancias: montos diferentes, transacciones faltantes, estados inconsistentes
- [ ] Dashboard de reconciliacion en mf-sp (vista admin)
- [ ] Alerta automatica cuando hay discrepancia > umbral configurable
- [ ] Audit trail: quien hizo que, cuando, desde donde
- [ ] Reporte de balance trial (debitos = creditos en todo el sistema)
- [ ] Export de reportes para contabilidad
- [ ] Resolucion manual de discrepancias con registro

**Dependencias:** EP-SP-003, EP-SP-004, EP-SP-005

**Complejidad:** M (logica de comparacion, reportes)

**Repositorio:** `covacha-payment`, `mf-sp`

---

### EP-SP-010: Limites, Politicas y Notificaciones

**Descripcion:**
Capa de politicas de negocio: limites de transaccion (diario, mensual, por operacion), politicas de aprobacion (montos altos requieren autorizacion), notificaciones en tiempo real (depositos, transferencias completadas/fallidas), y rate limiting para proteccion contra abuso.

**User Stories:**
- US-SP-036, US-SP-037, US-SP-038, US-SP-039

**Criterios de Aceptacion de la Epica:**
- [ ] Limites configurables por cuenta y por organizacion:
  - Monto maximo por transferencia
  - Monto maximo diario
  - Monto maximo mensual
  - Numero maximo de operaciones por dia
- [ ] Politica de aprobacion: transferencias > umbral requieren autorizacion
- [ ] Notificaciones:
  - Deposito SPEI recibido (email + push)
  - Transferencia completada
  - Transferencia fallida
  - Limite alcanzado (warning al 80%)
  - Limite excedido (bloqueo)
- [ ] Rate limiting en API de transferencias
- [ ] Configuracion de politicas via UI en mf-sp
- [ ] Audit log de cambios a politicas

**Dependencias:** EP-SP-004, EP-SP-005

**Complejidad:** M (configuracion, notificaciones, validacion)

**Repositorio:** `covacha-payment`, `covacha-webhook` (notificaciones), `mf-sp`

---

## User Stories Detalladas

---

### EP-SP-001: Account Core Engine

---

#### US-SP-001: Modelo de Dominio de Cuentas

**ID:** US-SP-001
**Epica:** EP-SP-001
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero tener un modelo de dominio robusto para cuentas financieras para poder representar los 4 tipos de cuenta con sus reglas de negocio.

**Criterios de Aceptacion:**
- [ ] Modelo `FinancialAccount` en DynamoDB con campos:
  - `PK: ORG#{org_id}`, `SK: ACCOUNT#{account_id}`
  - `account_id` (UUID)
  - `organization_id`
  - `account_type`: CONCENTRADORA | CLABE | DISPERSION | RESERVADA
  - `status`: PENDING | ACTIVE | FROZEN | CLOSED
  - `clabe` (solo tipo CLABE, generada por Monato)
  - `parent_account_id` (referencia al padre en el grafo)
  - `display_name` (nombre legible, ej: "Cuenta Principal", "IVA Q1")
  - `currency`: MXN (default)
  - `metadata`: JSON flexible (destino fijo para RESERVADA, etc.)
  - `provider_account_id` (ID en Monato)
  - `provider_instrument_id` (ID del instrumento en Monato)
  - `created_at`, `updated_at`, `created_by`
- [ ] GSI `GSI-PARENT`: `PK: PARENT#{parent_id}`, `SK: ACCOUNT#{id}` para consultar hijas
- [ ] GSI `GSI-CLABE`: `PK: CLABE#{clabe}`, `SK: ACCOUNT#{id}` para buscar por CLABE
- [ ] GSI `GSI-TYPE`: `PK: ORG#{org_id}#TYPE#{type}`, `SK: ACCOUNT#{id}` para filtrar por tipo
- [ ] Validacion: RESERVADA requiere `metadata.fixed_destination_clabe`
- [ ] Validacion: solo CLABE tiene campo `clabe` (no null)

**Tareas Tecnicas:**
1. Crear modelo DynamoDB con PK/SK y GSIs
2. Crear dataclass/schema de Python con validaciones
3. Crear repository con CRUD basico
4. Tests unitarios del modelo y validaciones
5. Documentar esquema de tabla

**Dependencias:** Ninguna
**Estimacion:** 3 dev-days

---

#### US-SP-002: CRUD de Cuentas via API

**ID:** US-SP-002
**Epica:** EP-SP-001
**Prioridad:** P0

**Historia:**
Como **Administrador de Plataforma** quiero poder crear, leer, actualizar y listar cuentas financieras via API REST para gestionar la estructura de cuentas de cada organizacion.

**Criterios de Aceptacion:**
- [ ] `POST /api/v1/organizations/{org_id}/accounts` - Crear cuenta
  - Body: `{ account_type, display_name, parent_account_id?, metadata? }`
  - Si tipo CLABE: llama a Monato para crear cuenta privada y obtener CLABE
  - Si tipo RESERVADA: requiere `metadata.fixed_destination_clabe`
  - Response: cuenta creada con status PENDING (o ACTIVE si no requiere Monato)
- [ ] `GET /api/v1/organizations/{org_id}/accounts` - Listar cuentas
  - Query params: `type`, `status`, `parent_id`, `page`, `page_size`
  - Incluye saldo calculado del ledger
- [ ] `GET /api/v1/organizations/{org_id}/accounts/{account_id}` - Detalle
  - Incluye saldo, ultimos N movimientos, cuentas hijas
- [ ] `PATCH /api/v1/organizations/{org_id}/accounts/{account_id}` - Actualizar
  - Solo `display_name`, `metadata`, `status` (con validacion de transiciones)
- [ ] `DELETE` no existe (las cuentas se CIERRAN, no se borran)
- [ ] Todos los endpoints requieren `X-SP-Organization-Id` header
- [ ] Paginacion estandar en listados

**Tareas Tecnicas:**
1. Crear Blueprint Flask `/organizations/<org_id>/accounts`
2. Implementar service layer con logica de negocio
3. Validaciones de input (marshmallow o pydantic)
4. Integracion con Monato para crear cuentas CLABE
5. Tests de integracion de cada endpoint
6. Documentar en OpenAPI

**Dependencias:** US-SP-001
**Estimacion:** 5 dev-days

---

#### US-SP-003: Grafo de Relaciones Padre-Hijo

**ID:** US-SP-003
**Epica:** EP-SP-001
**Prioridad:** P0

**Historia:**
Como **Administrador de Plataforma** quiero que las cuentas formen un grafo jerarquico para poder modelar relaciones concentradora-hijas y aplicar reglas de negocio basadas en la posicion en el arbol.

**Criterios de Aceptacion:**
- [ ] Al crear una cuenta, se valida que el `parent_account_id` sea valido:
  - CONCENTRADORA: puede ser raiz (sin padre) o hija de otra CONCENTRADORA
  - CLABE: padre debe ser CONCENTRADORA
  - DISPERSION: padre debe ser CONCENTRADORA
  - RESERVADA: padre debe ser CONCENTRADORA o CLABE
- [ ] Endpoint `GET /api/v1/organizations/{org_id}/accounts/{id}/children` retorna hijas directas
- [ ] Endpoint `GET /api/v1/organizations/{org_id}/accounts/tree` retorna el arbol completo
- [ ] No se permite crear ciclos en el grafo
- [ ] No se puede cerrar una cuenta que tiene hijas activas
- [ ] Mover cuenta de padre (reparentar) requiere validacion de reglas

**Tareas Tecnicas:**
1. Implementar validaciones de jerarquia en el servicio de cuentas
2. Query de arbol completo usando GSI-PARENT con recursion
3. Deteccion de ciclos en el grafo
4. Endpoint de arbol con formato nested JSON
5. Tests de todas las reglas de validacion

**Dependencias:** US-SP-001, US-SP-002
**Estimacion:** 3 dev-days

---

#### US-SP-004: Transiciones de Estado de Cuenta

**ID:** US-SP-004
**Epica:** EP-SP-001
**Prioridad:** P1

**Historia:**
Como **Administrador de Plataforma** quiero que las cuentas sigan una maquina de estados controlada para evitar operaciones en cuentas invalidas y mantener consistencia.

**Criterios de Aceptacion:**
- [ ] Estados: PENDING, ACTIVE, FROZEN, CLOSED
- [ ] Transiciones validas:
  - PENDING -> ACTIVE (activacion, confirmacion de Monato)
  - PENDING -> CLOSED (cancelacion antes de activar)
  - ACTIVE -> FROZEN (suspension temporal)
  - ACTIVE -> CLOSED (cierre definitivo, saldo debe ser 0)
  - FROZEN -> ACTIVE (reactivacion)
  - FROZEN -> CLOSED (cierre desde frozen)
- [ ] `PATCH /api/v1/organizations/{org_id}/accounts/{id}/status`
  - Body: `{ new_status, reason }`
- [ ] Registro de cada cambio de estado en audit log
- [ ] No se puede operar (transferir, recibir) en cuenta FROZEN o CLOSED
- [ ] Para cerrar: saldo debe ser exactamente 0

**Tareas Tecnicas:**
1. Implementar state machine con validaciones
2. Endpoint de cambio de estado
3. Registro en audit log (DynamoDB)
4. Validacion pre-operacion en servicios de transferencia
5. Tests de todas las transiciones validas e invalidas

**Dependencias:** US-SP-002
**Estimacion:** 2 dev-days

---

#### US-SP-005: Consulta de Saldo (Balance from Ledger)

**ID:** US-SP-005
**Epica:** EP-SP-001
**Prioridad:** P0

**Historia:**
Como **Cliente Empresarial** quiero consultar el saldo actual de mis cuentas para saber cuanto dinero tengo disponible en cada una.

**Criterios de Aceptacion:**
- [ ] `GET /api/v1/organizations/{org_id}/accounts/{id}/balance`
  - Response: `{ available_balance, pending_balance, total_balance, currency, as_of }`
- [ ] `available_balance` = total creditos confirmados - total debitos confirmados
- [ ] `pending_balance` = monto en transferencias PENDING/PROCESSING
- [ ] El saldo se calcula en tiempo real desde el ledger (no cache)
- [ ] Para cuentas con muchos movimientos, usar snapshot + delta (optimizacion futura)
- [ ] El saldo de una CONCENTRADORA NO incluye el saldo de sus hijas (es independiente)
- [ ] Performance: < 200ms para cuentas con hasta 10,000 entries

**Tareas Tecnicas:**
1. Implementar query de saldo desde ledger
2. Separar available vs pending
3. Benchmark de performance
4. Cache strategy (evaluar si es necesario para MVP)
5. Tests con volumenes grandes

**Dependencias:** US-SP-001, US-SP-010 (ledger)
**Estimacion:** 2 dev-days

---

### EP-SP-002: Monato Driver (Strategy Pattern)

---

#### US-SP-006: Interface SPEIProvider y MonatoDriver Base

**ID:** US-SP-006
**Epica:** EP-SP-002
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero una interfaz abstracta para proveedores SPEI para poder cambiar de proveedor sin modificar la logica de negocio.

**Criterios de Aceptacion:**
- [ ] Interface `SPEIProvider` (abstract class en Python) con metodos:
  - `create_account(org_id, account_type, metadata) -> ProviderAccountResult`
  - `create_instrument(account_id, instrument_type) -> ProviderInstrumentResult`
  - `send_money(transfer_request) -> ProviderTransferResult`
  - `refund(transaction_id, amount, reason) -> ProviderRefundResult`
  - `get_accounts(org_id, filters) -> list[ProviderAccount]`
  - `get_spei_participants() -> list[SPEIParticipant]`
  - `validate_account(clabe) -> PennyValidationResult`
  - `register_webhook(url, events) -> WebhookRegistrationResult`
- [ ] `MonatoDriver` implementa `SPEIProvider` con stubs iniciales
- [ ] Factory `SPEIProviderFactory.get_provider(provider_name) -> SPEIProvider`
- [ ] Configuracion del provider activo via environment variable
- [ ] Todos los metodos usan type hints y dataclasses para request/response

**Tareas Tecnicas:**
1. Definir abstract class `SPEIProvider` con todos los metodos
2. Definir dataclasses para request/response de cada operacion
3. Implementar `MonatoDriver` como clase concreta con stubs
4. Implementar factory con registry de providers
5. Tests de la factory y de los contratos de la interfaz

**Dependencias:** Ninguna
**Estimacion:** 3 dev-days

---

#### US-SP-007: Monato - Crear Cuenta y Obtener CLABE

**ID:** US-SP-007
**Epica:** EP-SP-002
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero crear cuentas privadas en Monato Fincore para obtener CLABEs que los usuarios puedan usar para recibir SPEI.

**Criterios de Aceptacion:**
- [ ] `MonatoDriver.create_account()` llama a `POST /api/monato/create-private-account`
- [ ] Mapea la respuesta de Monato al modelo interno `ProviderAccountResult`
- [ ] Extrae la CLABE generada automaticamente
- [ ] Crea instrumento de pago asociado (`POST /api/monato/create-instrument`)
- [ ] Manejo de errores: timeout, 4xx, 5xx con mensajes descriptivos
- [ ] Retry con backoff exponencial para errores transitorios (5xx, timeout)
- [ ] Idempotency key basada en `org_id + account_type + timestamp_hash`
- [ ] Logging estructurado de request/response (sin datos sensibles)

**Tareas Tecnicas:**
1. Implementar HTTP client para Monato con autenticacion
2. Implementar `create_account` con mapping de request/response
3. Implementar `create_instrument` encadenado
4. Retry logic con tenacity o similar
5. Tests con mocks de respuestas de Monato (happy path + errores)

**Dependencias:** US-SP-006
**Estimacion:** 3 dev-days

---

#### US-SP-008: Monato - Money Out (SPEI Saliente)

**ID:** US-SP-008
**Epica:** EP-SP-002
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero enviar transferencias SPEI out via Monato para que los usuarios puedan pagar a cuentas externas.

**Criterios de Aceptacion:**
- [ ] `MonatoDriver.send_money()` llama a `POST /api/monato/money-out`
- [ ] Request incluye: cuenta origen (instrument_id), CLABE destino, monto, concepto, referencia
- [ ] Idempotency key obligatoria (generada por el caller)
- [ ] Mapea respuesta a `ProviderTransferResult` con estado y tracking_id
- [ ] Manejo de errores especificos de Monato:
  - Saldo insuficiente en Monato
  - CLABE destino invalida
  - Limite excedido en Monato
  - Cuenta destino no existe
- [ ] No retry en errores de negocio (4xx), si en transitorios (5xx)
- [ ] Timeout configurable (default 30s)

**Tareas Tecnicas:**
1. Implementar `send_money` con mapping completo
2. Mapear errores de Monato a errores internos descriptivos
3. Implementar idempotency key passthrough
4. Tests con todos los escenarios de error de Monato

**Dependencias:** US-SP-006
**Estimacion:** 3 dev-days

---

#### US-SP-009: Monato - Utilidades (Catalogo, Penny Validation, Webhook Registration)

**ID:** US-SP-009
**Epica:** EP-SP-002
**Prioridad:** P1

**Historia:**
Como **Sistema** quiero acceder al catalogo de participantes SPEI, validar cuentas con penny validation, y registrar webhooks en Monato para completar la integracion.

**Criterios de Aceptacion:**
- [ ] `get_spei_participants()` retorna lista de bancos con nombre, codigo, status
  - Cache en memoria con TTL de 24 horas (el catalogo cambia poco)
- [ ] `validate_account(clabe)` ejecuta penny validation
  - Envia $0.01 MXN y verifica que la cuenta exista
  - Retorna: nombre del titular, banco, estado de validacion
- [ ] `register_webhook(url, events)` registra URL de webhook en Monato
  - Eventos: money_in, money_out_status, refund_status
- [ ] `MonatoDriver.refund()` ejecuta devolucion SPEI

**Tareas Tecnicas:**
1. Implementar `get_spei_participants` con cache
2. Implementar `validate_account` (penny validation)
3. Implementar `register_webhook`
4. Implementar `refund`
5. Tests para cada operacion

**Dependencias:** US-SP-006
**Estimacion:** 3 dev-days

---

### EP-SP-003: Double-Entry Ledger

---

#### US-SP-010: Modelo de Ledger Entry

**ID:** US-SP-010
**Epica:** EP-SP-003
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero un modelo de asiento contable inmutable para registrar cada movimiento financiero con partida doble.

**Criterios de Aceptacion:**
- [ ] Modelo `LedgerEntry` en DynamoDB:
  - `PK: ACCOUNT#{account_id}`, `SK: ENTRY#{timestamp}#{entry_id}`
  - `entry_id` (UUID)
  - `account_id` (cuenta afectada)
  - `transaction_id` (agrupa los 2+ entries de una transaccion)
  - `entry_type`: DEBIT | CREDIT
  - `amount`: Decimal con 2 decimales (siempre positivo)
  - `currency`: MXN
  - `status`: PENDING | CONFIRMED | REVERSED
  - `category`: SPEI_IN | SPEI_OUT | INTERNAL_TRANSFER | COMMISSION | REFUND | REVERSAL
  - `counterpart_account_id` (la otra cuenta del asiento)
  - `description` (concepto)
  - `reference` (referencia bancaria, clave de rastreo)
  - `metadata`: JSON (datos adicionales, proveedor, etc.)
  - `created_at` (timestamp de creacion, immutable)
  - `created_by` (user_id o "SYSTEM")
- [ ] GSI `GSI-TXN`: `PK: TXN#{transaction_id}` para obtener todos los entries de una transaccion
- [ ] Las entries son append-only (no UPDATE, no DELETE)
- [ ] Para reversar: se crean entries inversos (DEBIT se reversa con CREDIT y viceversa)

**Tareas Tecnicas:**
1. Crear modelo DynamoDB con PK/SK y GSIs
2. Crear dataclass de Python con validaciones
3. Crear repository con metodos write-only (no update/delete)
4. Tests de inmutabilidad y validaciones

**Dependencias:** US-SP-001
**Estimacion:** 2 dev-days

---

#### US-SP-011: Servicio de Registro de Transacciones

**ID:** US-SP-011
**Epica:** EP-SP-003
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero un servicio que registre transacciones financieras creando automaticamente los asientos de partida doble para mantener la integridad contable.

**Criterios de Aceptacion:**
- [ ] `LedgerService.record_transaction(from_account, to_account, amount, category, metadata)`
  - Crea 2 entries atomicamente:
    - DEBIT en `from_account` por `amount`
    - CREDIT en `to_account` por `amount`
  - Ambos entries comparten el mismo `transaction_id`
  - Si una de las 2 escrituras falla, se reversa la otra (atomicidad)
- [ ] Soporte para transacciones con mas de 2 legs (ej: transferencia + comision):
  - `record_multi_leg_transaction([{account, type, amount}])`
  - Validacion: SUM(DEBITS) == SUM(CREDITS) o error
- [ ] Idempotencia: si se llama 2 veces con el mismo `idempotency_key`, retorna resultado anterior
- [ ] Tabla de idempotencia con TTL de 48 horas

**Tareas Tecnicas:**
1. Implementar `LedgerService` con `record_transaction`
2. Implementar `record_multi_leg_transaction`
3. Usar DynamoDB TransactWriteItems para atomicidad
4. Implementar tabla de idempotencia
5. Tests de atomicidad, idempotencia, y multi-leg

**Dependencias:** US-SP-010
**Estimacion:** 4 dev-days

---

#### US-SP-012: Calculo de Saldo desde Ledger

**ID:** US-SP-012
**Epica:** EP-SP-003
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero calcular el saldo de cualquier cuenta sumando sus entries del ledger para tener un saldo siempre consistente con la realidad contable.

**Criterios de Aceptacion:**
- [ ] `LedgerService.get_balance(account_id) -> AccountBalance`
  - `total_credits` = SUM de entries CREDIT con status CONFIRMED
  - `total_debits` = SUM de entries DEBIT con status CONFIRMED
  - `available_balance` = total_credits - total_debits
  - `pending_balance` = SUM de entries con status PENDING
- [ ] Query eficiente usando PK del ledger (ACCOUNT#{id})
- [ ] Para cuentas con muchos entries (>10k), evaluar balance snapshots:
  - Snapshot periodico del saldo (diario/semanal)
  - Saldo = snapshot + delta (entries posteriores al snapshot)
- [ ] `LedgerService.get_statement(account_id, from_date, to_date, page, page_size)`
  - Retorna entries paginados para estado de cuenta

**Tareas Tecnicas:**
1. Implementar `get_balance` con query al ledger
2. Implementar `get_statement` con paginacion
3. Evaluar y documentar estrategia de snapshots
4. Benchmark con 10k+ entries
5. Tests de calculo correcto en multiples escenarios

**Dependencias:** US-SP-010, US-SP-011
**Estimacion:** 3 dev-days

---

#### US-SP-013: Balance Trial (Verificacion de Integridad)

**ID:** US-SP-013
**Epica:** EP-SP-003
**Prioridad:** P1

**Historia:**
Como **Administrador de Plataforma** quiero verificar que el sistema contable esta balanceado para detectar inconsistencias antes de que se conviertan en problemas.

**Criterios de Aceptacion:**
- [ ] `GET /api/v1/admin/ledger/balance-trial`
  - Suma global: SUM(todos los DEBITS) == SUM(todos los CREDITS)
  - Si no balancea: retorna la diferencia y las transacciones sospechosas
- [ ] `GET /api/v1/admin/ledger/balance-trial/{org_id}`
  - Balance trial por organizacion
- [ ] Job programado (diario) que ejecuta balance trial y envia alerta si falla
- [ ] Endpoint protegido (solo admin de plataforma)

**Tareas Tecnicas:**
1. Implementar query de balance trial global
2. Implementar balance trial por organizacion
3. Job programado con CloudWatch Events o cron
4. Notificacion de discrepancias (email/Slack)
5. Tests con escenarios balanceados y desbalanceados

**Dependencias:** US-SP-011, US-SP-012
**Estimacion:** 2 dev-days

---

### EP-SP-004: SPEI Out (Transferencias Salientes)

---

#### US-SP-014: Flujo de Transferencia SPEI Out

**ID:** US-SP-014
**Epica:** EP-SP-004
**Prioridad:** P0

**Historia:**
Como **Cliente Empresarial** quiero enviar dinero via SPEI a cualquier cuenta bancaria en Mexico para pagar a proveedores, empleados, o terceros.

**Criterios de Aceptacion:**
- [ ] `POST /api/v1/organizations/{org_id}/transfers/spei-out`
  - Body: `{ source_account_id, destination_clabe, destination_name, amount, concept, reference?, idempotency_key }`
- [ ] Validaciones pre-envio:
  - Cuenta origen existe, esta ACTIVE, y es tipo CLABE o DISPERSION
  - CLABE destino tiene formato valido (18 digitos, checksum correcto)
  - Saldo disponible >= monto + comision
  - Dentro de limites de transferencia (si EP-SP-010 esta implementada)
- [ ] Flujo:
  1. Crear registro de transferencia con status PENDING
  2. Crear entries en ledger: DEBIT en cuenta origen (status PENDING)
  3. Llamar a MonatoDriver.send_money()
  4. Si Monato acepta: status -> PROCESSING, entries -> CONFIRMED
  5. Si Monato rechaza: status -> FAILED, entries se reversan
  6. Webhook posterior confirma COMPLETED o FAILED
- [ ] Idempotency key previene transferencias duplicadas
- [ ] Response incluye `transfer_id` y `tracking_code` (clave de rastreo SPEI)

**Tareas Tecnicas:**
1. Crear modelo `Transfer` en DynamoDB
2. Implementar TransferService con flujo completo
3. Integracion con LedgerService para asientos
4. Integracion con MonatoDriver para envio
5. Endpoint REST con validaciones
6. Tests del flujo completo (happy path + errores)

**Dependencias:** US-SP-002, US-SP-008, US-SP-011
**Estimacion:** 5 dev-days

---

#### US-SP-015: Transferencia desde Cuenta RESERVADA

**ID:** US-SP-015
**Epica:** EP-SP-004
**Prioridad:** P1

**Historia:**
Como **Cliente Empresarial** quiero que mi cuenta RESERVADA (ej: IVA) solo pueda enviar SPEI al destino fijo configurado para cumplir con reglas fiscales y de control interno.

**Criterios de Aceptacion:**
- [ ] Cuando `source_account.type == RESERVADA`:
  - Solo permite SPEI out si `destination_clabe == metadata.fixed_destination_clabe`
  - Cualquier otro destino retorna error 400: "Cuenta reservada solo permite envios al destino fijo: {clabe}"
- [ ] El destino fijo se configura al crear la cuenta y no se puede cambiar (immutable)
- [ ] Para cambiar el destino: cerrar cuenta y crear nueva RESERVADA

**Tareas Tecnicas:**
1. Agregar validacion en TransferService
2. Validar immutabilidad del destino fijo
3. Tests de validacion positivos y negativos

**Dependencias:** US-SP-014
**Estimacion:** 1 dev-day

---

#### US-SP-016: Comisiones SPEI

**ID:** US-SP-016
**Epica:** EP-SP-004
**Prioridad:** P1

**Historia:**
Como **Administrador de Plataforma** quiero que cada transferencia SPEI out genere un cargo de comision para que SuperPago tenga ingresos por el servicio.

**Criterios de Aceptacion:**
- [ ] Tabla de comisiones configurables:
  - Por tipo de cuenta
  - Por volumen (descuentos por cantidad)
  - Por organizacion (precios especiales)
- [ ] Al ejecutar SPEI out, se crea una transaccion adicional en el ledger:
  - DEBIT en cuenta del cliente por monto de comision
  - CREDIT en cuenta de comisiones de SuperPago
- [ ] La comision se descuenta del saldo antes de enviar (saldo >= monto + comision)
- [ ] Endpoint `GET /api/v1/organizations/{org_id}/commissions/preview`
  - Calcula la comision sin ejecutar la transferencia
- [ ] Comision incluye IVA (desglosado en metadata)

**Tareas Tecnicas:**
1. Modelo de tabla de comisiones
2. Servicio de calculo de comision
3. Integracion en flujo de transferencia
4. Cuenta interna "COMISIONES_SUPERPAGO" para acumular ingresos
5. Tests con diferentes esquemas de comision

**Dependencias:** US-SP-014
**Estimacion:** 3 dev-days

---

#### US-SP-017: Beneficiarios Frecuentes

**ID:** US-SP-017
**Epica:** EP-SP-004
**Prioridad:** P2

**Historia:**
Como **Cliente Empresarial** quiero guardar cuentas destino frecuentes para no tener que escribir la CLABE cada vez que hago una transferencia.

**Criterios de Aceptacion:**
- [ ] `POST /api/v1/organizations/{org_id}/beneficiaries`
  - Body: `{ clabe, alias, holder_name, bank_name, email? }`
- [ ] `GET /api/v1/organizations/{org_id}/beneficiaries` - Listar
- [ ] `DELETE /api/v1/organizations/{org_id}/beneficiaries/{id}` - Eliminar
- [ ] Al hacer primera transferencia a un nuevo beneficiario, ofrecer guardarlo
- [ ] Penny validation requerida antes de guardar beneficiario
- [ ] Limite de 100 beneficiarios por organizacion (configurable)

**Tareas Tecnicas:**
1. Modelo de beneficiario en DynamoDB
2. CRUD endpoints
3. Integracion con penny validation
4. Autoguardar beneficiario despues de primera transferencia exitosa
5. Tests

**Dependencias:** US-SP-009 (penny validation), US-SP-014
**Estimacion:** 2 dev-days

---

### EP-SP-005: Webhook Handler SPEI In

---

#### US-SP-018: Endpoint de Webhook Monato

**ID:** US-SP-018
**Epica:** EP-SP-005
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero recibir eventos de Monato via webhook para procesar depositos SPEI entrantes y actualizaciones de estado de transferencias.

**Criterios de Aceptacion:**
- [ ] `POST /api/v1/webhook/spei/monato/` recibe eventos
- [ ] Validacion de firma (header `X-Monato-Signature` o similar)
- [ ] Response 200 inmediato (< 500ms), procesamiento asincrono via SQS
- [ ] Tipos de evento soportados:
  - `money_in`: deposito SPEI recibido
  - `money_out_completed`: transferencia saliente completada
  - `money_out_failed`: transferencia saliente fallida
  - `refund_completed`: devolucion completada
- [ ] Eventos desconocidos: log warning + response 200 (no falla)
- [ ] Body del webhook se guarda raw en S3 para auditoria

**Tareas Tecnicas:**
1. Crear Blueprint Flask en covacha-webhook
2. Implementar validacion de firma
3. Publicar evento a SQS para procesamiento async
4. Guardar raw body en S3
5. Consumer SQS que procesa cada tipo de evento
6. Tests con payloads reales de Monato

**Dependencias:** Ninguna (endpoint standalone)
**Estimacion:** 3 dev-days

---

#### US-SP-019: Procesamiento de Money In

**ID:** US-SP-019
**Epica:** EP-SP-005
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero procesar depositos SPEI entrantes para acreditar el monto en la cuenta CLABE correspondiente.

**Criterios de Aceptacion:**
- [ ] Al recibir evento `money_in`:
  1. Extraer CLABE destino del payload
  2. Buscar cuenta interna por CLABE (GSI-CLABE)
  3. Si no existe: log error + alerta (deposito huerfano)
  4. Si existe y esta ACTIVE: crear entries en ledger (CREDIT en la CLABE)
  5. Si cuenta esta FROZEN/CLOSED: retener deposito en cuenta temporal + alerta
- [ ] Registrar metadata del deposito: banco origen, nombre ordenante, concepto, clave rastreo
- [ ] Idempotencia: usar `monato_transaction_id` como idempotency key
  - Si ya procesado: log info + skip
- [ ] Notificar al usuario del deposito (via covacha-notifications)

**Tareas Tecnicas:**
1. Implementar consumer de SQS para money_in
2. Busqueda de cuenta por CLABE
3. Registro en ledger via LedgerService
4. Idempotencia con tabla de eventos procesados
5. Notificacion via servicio de notificaciones
6. Tests con escenarios: happy path, CLABE no encontrada, duplicado, cuenta frozen

**Dependencias:** US-SP-010, US-SP-011, US-SP-018
**Estimacion:** 4 dev-days

---

#### US-SP-020: Procesamiento de Status Updates (Money Out)

**ID:** US-SP-020
**Epica:** EP-SP-005
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero procesar actualizaciones de estado de transferencias SPEI out para confirmar o reversar los asientos contables correspondientes.

**Criterios de Aceptacion:**
- [ ] Al recibir evento `money_out_completed`:
  1. Buscar transferencia interna por `provider_transaction_id`
  2. Actualizar status: PROCESSING -> COMPLETED
  3. Confirmar entries del ledger: PENDING -> CONFIRMED
- [ ] Al recibir evento `money_out_failed`:
  1. Buscar transferencia interna
  2. Actualizar status: PROCESSING -> FAILED
  3. Reversar entries del ledger (crear entries inversos)
  4. Saldo vuelve a estar disponible
- [ ] Notificar al usuario del resultado
- [ ] Si la transferencia no se encuentra internamente: log error + alerta

**Tareas Tecnicas:**
1. Consumer de SQS para money_out_completed y money_out_failed
2. Actualizacion de modelo Transfer
3. Confirmacion/reverso en LedgerService
4. Notificaciones
5. Tests de ambos flujos (completed + failed)

**Dependencias:** US-SP-014, US-SP-018
**Estimacion:** 3 dev-days

---

#### US-SP-021: Dead Letter Queue y Reintentos

**ID:** US-SP-021
**Epica:** EP-SP-005
**Prioridad:** P1

**Historia:**
Como **Sistema** quiero que los webhooks fallidos se reintenten automaticamente y los irrecuperables vayan a una dead letter queue para no perder ningun evento financiero.

**Criterios de Aceptacion:**
- [ ] SQS queue principal con retry policy: 3 intentos con backoff
- [ ] Dead Letter Queue (DLQ) para mensajes que fallan 3 veces
- [ ] Dashboard de DLQ en mf-sp (vista admin):
  - Ver mensajes en DLQ
  - Reintentar manualmente
  - Marcar como resuelto
- [ ] Alerta automatica cuando hay mensajes en DLQ (email/Slack)
- [ ] Metricas: tasa de exito, tasa de fallo, tiempo promedio de procesamiento

**Tareas Tecnicas:**
1. Configurar SQS con DLQ
2. Implementar retry logic con backoff
3. Lambda o consumer para monitorear DLQ
4. Endpoint para listar y gestionar DLQ
5. Alertas
6. Tests de retry y DLQ

**Dependencias:** US-SP-018
**Estimacion:** 3 dev-days

---

### EP-SP-006: Movimientos Internos (Grafo)

---

#### US-SP-022: Transferencia Interna entre Cuentas

**ID:** US-SP-022
**Epica:** EP-SP-006
**Prioridad:** P0

**Historia:**
Como **Cliente Empresarial** quiero mover dinero entre mis cuentas (de la misma organizacion) de forma instantanea y sin costo para gestionar mi flujo de fondos.

**Criterios de Aceptacion:**
- [ ] `POST /api/v1/organizations/{org_id}/transfers/internal`
  - Body: `{ source_account_id, destination_account_id, amount, concept, idempotency_key }`
- [ ] Validaciones:
  - Ambas cuentas pertenecen a la misma organizacion
  - Ambas cuentas estan ACTIVE
  - Saldo disponible en origen >= monto
  - El movimiento esta permitido segun reglas del grafo
- [ ] Reglas de movimiento permitidas:
  - CLABE -> CONCENTRADORA (subida de fondos)
  - CONCENTRADORA -> CLABE (distribucion)
  - CONCENTRADORA -> DISPERSION (alimentacion)
  - CONCENTRADORA -> RESERVADA (alimentacion)
  - CLABE -> RESERVADA (alimentacion directa)
  - DISPERSION -> CONCENTRADORA (devolucion de fondos no usados)
- [ ] Movimientos NO permitidos:
  - RESERVADA -> cualquier cuenta (fondos reservados no se mueven internamente)
  - Cuenta a si misma
  - Entre cuentas de diferentes organizaciones
- [ ] Operacion instantanea (sin pasar por SPEI)
- [ ] Sin comision
- [ ] Asientos de partida doble en el ledger

**Tareas Tecnicas:**
1. Implementar InternalTransferService con validaciones de grafo
2. Definir matriz de movimientos permitidos
3. Endpoint REST
4. Integracion con LedgerService
5. Tests de todas las combinaciones validas e invalidas

**Dependencias:** US-SP-002, US-SP-011
**Estimacion:** 4 dev-days

---

#### US-SP-023: Dispersion Masiva

**ID:** US-SP-023
**Epica:** EP-SP-006
**Prioridad:** P1

**Historia:**
Como **Cliente Empresarial** quiero dispersar fondos desde una cuenta concentradora a multiples cuentas hijas en una sola operacion para procesar nomina o pagos masivos de forma eficiente.

**Criterios de Aceptacion:**
- [ ] `POST /api/v1/organizations/{org_id}/transfers/bulk-internal`
  - Body: `{ source_account_id, destinations: [{ account_id, amount, concept }], idempotency_key }`
- [ ] Validacion previa: saldo de origen >= SUM(todos los montos destino)
- [ ] Ejecucion atomica: si una transferencia falla, se revierten todas (transaccion)
- [ ] Limite: maximo 100 destinos por operacion
- [ ] Response incluye resultado individual de cada transferencia
- [ ] Asientos de partida doble para cada par origen-destino

**Tareas Tecnicas:**
1. Implementar bulk transfer con DynamoDB TransactWriteItems
2. Validacion de saldo total antes de ejecutar
3. Rollback atomico si falla alguna
4. Response detallado por destino
5. Tests con N destinos (1, 50, 100, >100)

**Dependencias:** US-SP-022
**Estimacion:** 3 dev-days

---

#### US-SP-024: Reglas de Movimiento del Grafo (Validador)

**ID:** US-SP-024
**Epica:** EP-SP-006
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero un validador centralizado de reglas de movimiento del grafo para garantizar que solo se permitan transferencias internas validas segun el tipo de cuenta.

**Criterios de Aceptacion:**
- [ ] Clase `TransferRuleValidator` con metodo:
  - `validate(source_account, destination_account) -> ValidationResult`
- [ ] Matriz de reglas definida como constante (facil de auditar y modificar):
  ```python
  ALLOWED_INTERNAL_TRANSFERS = {
      'CONCENTRADORA': ['CLABE', 'DISPERSION', 'RESERVADA'],
      'CLABE': ['CONCENTRADORA', 'RESERVADA'],
      'DISPERSION': ['CONCENTRADORA'],
      'RESERVADA': [],  # No puede mover fondos internamente
  }
  ```
- [ ] Error messages descriptivos: "No se permite mover fondos de RESERVADA a CLABE. Las cuentas reservadas no permiten movimientos internos salientes."
- [ ] Validacion adicional: cuentas deben estar en la misma organizacion
- [ ] Extensible: la matriz se puede cambiar sin tocar logica

**Tareas Tecnicas:**
1. Implementar `TransferRuleValidator`
2. Definir matriz como configuracion
3. Integrar en InternalTransferService y TransferService
4. Tests exhaustivos de cada combinacion
5. Documentar reglas

**Dependencias:** US-SP-001
**Estimacion:** 2 dev-days

---

### EP-SP-007: mf-sp - Scaffold y Dashboard

---

#### US-SP-025: Scaffold del Micro-frontend mf-sp

**ID:** US-SP-025
**Epica:** EP-SP-007
**Prioridad:** P0

**Historia:**
Como **Desarrollador** quiero un micro-frontend Angular 21 nuevo llamado mf-sp con la misma estructura que mf-marketing para tener una base solida donde construir las pantallas de SPEI.

**Criterios de Aceptacion:**
- [ ] Proyecto Angular 21 standalone con estructura hexagonal:
  ```
  mf-sp/src/app/
  ├── domain/models/          # Modelos de cuentas, transferencias, ledger
  ├── domain/ports/           # Interfaces
  ├── infrastructure/adapters/ # Adapters HTTP
  ├── application/use-cases/  # Logica de aplicacion
  ├── core/http/              # HttpService (copiado de mf-marketing)
  ├── core/services/          # Servicios base
  ├── presentation/pages/     # Paginas lazy-loaded
  ├── presentation/components/ # Componentes reutilizables
  ├── presentation/layout/    # Layout SPEI
  ├── shared-state/           # SharedStateService
  └── remote-entry/           # Entry point para Federation
  ```
- [ ] `federation.config.js`:
  - name: `mfSP`
  - puerto: 4212
  - exposes: `./Component`, `./routes`
- [ ] Registrado en `mf-core` como remote
- [ ] `SharedStateService` funcional (lee covacha:auth, covacha:user)
- [ ] `HttpService` funcional (headers, tenant, auth)
- [ ] Path aliases configurados (@app, @core, @domain, @infrastructure, @presentation, @shared-state, @env)
- [ ] Build y serve funcionan

**Tareas Tecnicas:**
1. Crear proyecto Angular 21 con `ng new`
2. Configurar Native Federation
3. Copiar y adaptar SharedStateService y HttpService de mf-marketing
4. Configurar tsconfig con path aliases
5. Registrar remote en mf-core federation.config.js
6. Verificar carga desde Shell
7. Tests basicos de que el MF carga

**Dependencias:** Ninguna
**Estimacion:** 3 dev-days

---

#### US-SP-026: Dashboard de Cuentas

**ID:** US-SP-026
**Epica:** EP-SP-007
**Prioridad:** P0

**Historia:**
Como **Cliente Empresarial** quiero ver un dashboard con todas mis cuentas, sus saldos, y estado para tener una vision general de mis finanzas en SuperPago.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/accounts` (ruta en mf-sp)
- [ ] Lista de cuentas mostrando:
  - Nombre (display_name)
  - Tipo (con icono visual: concentradora, CLABE, dispersion, reservada)
  - CLABE (si aplica, con boton de copiar)
  - Saldo disponible (formatted con $ y separadores de miles)
  - Estado (badge: activa, pendiente, congelada)
- [ ] Filtros: por tipo, por estado
- [ ] Busqueda por nombre o CLABE
- [ ] Orden: por nombre, saldo, fecha de creacion
- [ ] Card con totales:
  - Saldo total (suma de todas las cuentas)
  - Numero de cuentas activas
  - Cuentas con alerta (saldo bajo, congeladas)
- [ ] Responsive: cards en mobile, tabla en desktop
- [ ] Skeleton loaders mientras carga
- [ ] OnPush change detection + Signals

**Tareas Tecnicas:**
1. Crear AccountsAdapter (HTTP calls)
2. Crear AccountsDashboardComponent (page)
3. Crear AccountCardComponent (sub-componente)
4. Crear AccountsStatsComponent (totales)
5. Crear AccountFiltersComponent (filtros)
6. Tests de renderizado y logica

**Dependencias:** US-SP-025, US-SP-002 (API lista)
**Estimacion:** 4 dev-days

---

#### US-SP-027: Detalle de Cuenta

**ID:** US-SP-027
**Epica:** EP-SP-007
**Prioridad:** P1

**Historia:**
Como **Cliente Empresarial** quiero ver el detalle de una cuenta especifica con su saldo, ultimos movimientos, y cuentas hijas para entender la actividad de esa cuenta.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/accounts/:accountId`
- [ ] Seccion de informacion:
  - Nombre, tipo, CLABE, estado
  - Fecha de creacion
  - Cuenta padre (si tiene)
  - Destino fijo (si es RESERVADA)
- [ ] Seccion de saldo:
  - Saldo disponible (grande, prominente)
  - Saldo pendiente
  - Grafica de saldo ultimos 30 dias
- [ ] Seccion de ultimos movimientos:
  - Tabla con: fecha, tipo, concepto, monto (+/-), saldo resultante
  - Paginacion
  - Filtro por tipo (entrada, salida, comision)
- [ ] Seccion de cuentas hijas (si es CONCENTRADORA):
  - Lista de hijas con saldo
  - Link a detalle de cada hija
- [ ] Acciones rapidas:
  - "Transferir SPEI" (link al formulario)
  - "Mover fondos" (link a movimiento interno)
  - "Ver estado de cuenta completo"

**Tareas Tecnicas:**
1. Crear AccountDetailComponent (page)
2. Crear AccountInfoComponent
3. Crear AccountBalanceComponent (con grafica)
4. Crear AccountMovementsTableComponent
5. Crear AccountChildrenComponent
6. Tests

**Dependencias:** US-SP-025, US-SP-026
**Estimacion:** 4 dev-days

---

#### US-SP-028: Visualizacion del Grafo de Cuentas

**ID:** US-SP-028
**Epica:** EP-SP-007
**Prioridad:** P2

**Historia:**
Como **Administrador de Plataforma** quiero ver la estructura de cuentas como un arbol visual para entender rapidamente la jerarquia de cuentas de una organizacion.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/accounts/tree`
- [ ] Arbol visual con nodos por cuenta:
  - Color por tipo (concentradora: azul, CLABE: verde, dispersion: naranja, reservada: gris)
  - Icono por tipo
  - Saldo en cada nodo
  - Estado (opacidad para frozen/closed)
- [ ] Interactivo: click en nodo abre detalle de cuenta
- [ ] Zoom y pan para arboles grandes
- [ ] Opcion de layout: arbol vertical u horizontal
- [ ] Implementar con CSS Grid + SVG (sin dependencia pesada de libreria)
  - Alternativa: evaluar ngx-graph si es necesario

**Tareas Tecnicas:**
1. Crear AccountTreeComponent
2. Implementar renderizado de arbol con SVG
3. Logica de layout automatico
4. Interactividad (click, hover, zoom)
5. Tests de renderizado

**Dependencias:** US-SP-026, US-SP-003 (API de arbol)
**Estimacion:** 4 dev-days

---

### EP-SP-008: mf-sp - Transferencias y Movimientos

---

#### US-SP-029: Formulario de Transferencia SPEI Out

**ID:** US-SP-029
**Epica:** EP-SP-008
**Prioridad:** P0

**Historia:**
Como **Cliente Empresarial** quiero un formulario para enviar dinero via SPEI a cuentas externas para poder hacer pagos desde la plataforma.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/transfers/spei-out`
- [ ] Wizard de 3 pasos:
  1. **Seleccionar origen**: dropdown de cuentas CLABE y DISPERSION activas, mostrando saldo
  2. **Datos destino**: CLABE (18 digitos, formato validado), nombre del titular, banco (auto-detect por primeros digitos), concepto, referencia numerica (opcional)
  3. **Confirmar**: resumen completo, monto, comision desglosada, total a debitar, boton "Enviar"
- [ ] Si el beneficiario ya esta guardado: autocompletar al seleccionarlo
- [ ] Validacion en tiempo real:
  - CLABE: formato, checksum
  - Monto: > 0, <= saldo disponible - comision
  - Concepto: requerido, max 40 caracteres
- [ ] Despues de enviar:
  - Modal de confirmacion con clave de rastreo
  - Opcion "Guardar beneficiario" si es nuevo
  - Boton "Hacer otra transferencia"
- [ ] Feedback de estado: spinner durante envio, resultado claro

**Tareas Tecnicas:**
1. Crear TransferSPEIOutComponent (wizard)
2. Crear TransferAdapter (HTTP calls)
3. Validaciones reactivas con FormGroup
4. Integracion con catalogo de participantes SPEI
5. Integracion con beneficiarios guardados
6. Tests del wizard y validaciones

**Dependencias:** US-SP-025, US-SP-014 (API)
**Estimacion:** 5 dev-days

---

#### US-SP-030: Formulario de Movimiento Interno

**ID:** US-SP-030
**Epica:** EP-SP-008
**Prioridad:** P0

**Historia:**
Como **Cliente Empresarial** quiero mover dinero entre mis cuentas de forma rapida para gestionar mi flujo de fondos internamente.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/transfers/internal`
- [ ] Formulario simplificado (no wizard, todo en 1 paso):
  - Cuenta origen: dropdown filtrado por tipo (solo las que pueden enviar internamente)
  - Cuenta destino: dropdown filtrado por reglas del grafo (solo destinos validos para el tipo de origen)
  - Monto: validado contra saldo disponible
  - Concepto: opcional
- [ ] Al seleccionar cuenta origen, la lista de destinos se filtra automaticamente
- [ ] Preview: "Mover $X de [Cuenta A] a [Cuenta B]"
- [ ] Operacion instantanea: feedback inmediato de exito/error
- [ ] Acceso rapido desde detalle de cuenta (boton "Mover fondos")

**Tareas Tecnicas:**
1. Crear InternalTransferComponent
2. Logica de filtrado de destinos por reglas del grafo
3. Validaciones reactivas
4. Integracion con API
5. Tests

**Dependencias:** US-SP-025, US-SP-022 (API)
**Estimacion:** 3 dev-days

---

#### US-SP-031: Historial de Movimientos

**ID:** US-SP-031
**Epica:** EP-SP-008
**Prioridad:** P0

**Historia:**
Como **Cliente Empresarial** quiero ver el historial completo de movimientos de mis cuentas para tener control de todas las operaciones financieras.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/movements`
- [ ] Tabla con columnas: Fecha/Hora, Tipo, Cuenta, Concepto, Referencia, Monto, Saldo resultante, Estado
- [ ] Filtros:
  - Cuenta (dropdown o "Todas")
  - Tipo: SPEI In, SPEI Out, Interno, Comision, Reverso
  - Estado: Completado, Pendiente, Fallido
  - Rango de fechas (date picker)
  - Busqueda por referencia o concepto
- [ ] Paginacion server-side (50 por pagina)
- [ ] Colores: verde para entradas, rojo para salidas, gris para comisiones
- [ ] Click en movimiento abre drawer con detalle completo
- [ ] Export a CSV y PDF
- [ ] Subtotales: total entradas, total salidas, neto del periodo

**Tareas Tecnicas:**
1. Crear MovementsHistoryComponent (page)
2. Crear MovementsTableComponent
3. Crear MovementDetailDrawerComponent
4. Crear MovementsFiltersComponent
5. Implementar export CSV/PDF
6. Tests

**Dependencias:** US-SP-025, US-SP-012 (API de estado de cuenta)
**Estimacion:** 5 dev-days

---

#### US-SP-032: Estado de Transferencia en Tiempo Real

**ID:** US-SP-032
**Epica:** EP-SP-008
**Prioridad:** P2

**Historia:**
Como **Cliente Empresarial** quiero ver el estado de mis transferencias SPEI en tiempo real para saber cuando se completan o si fallan.

**Criterios de Aceptacion:**
- [ ] Despues de enviar una transferencia, la UI muestra el progreso:
  - PENDING: "Transferencia creada, validando..."
  - PROCESSING: "Enviando via SPEI..." (con spinner)
  - COMPLETED: "Transferencia completada" (con checkmark verde)
  - FAILED: "Transferencia fallida" (con icono rojo y motivo)
- [ ] Polling cada 5 segundos mientras este en PENDING/PROCESSING (max 60s)
- [ ] Toast notification cuando cambia de estado
- [ ] Pagina `/sp/transfers/:transferId` con detalle de la transferencia
- [ ] Lista de transferencias recientes en el dashboard

**Tareas Tecnicas:**
1. Implementar polling con RxJS timer + switchMap
2. Crear TransferStatusComponent
3. Crear TransferDetailComponent
4. Toast notifications
5. Tests

**Dependencias:** US-SP-029
**Estimacion:** 2 dev-days

---

### EP-SP-009: Reconciliacion y Auditoria

---

#### US-SP-033: Job de Reconciliacion Diaria

**ID:** US-SP-033
**Epica:** EP-SP-009
**Prioridad:** P1

**Historia:**
Como **Administrador de Plataforma** quiero que el sistema compare automaticamente el ledger interno con los reportes de Monato para detectar discrepancias.

**Criterios de Aceptacion:**
- [ ] Job diario (02:00 AM) que:
  1. Obtiene transacciones del dia anterior de Monato (via API)
  2. Obtiene entries del ledger del mismo dia
  3. Compara monto a monto, status a status
  4. Detecta: montos diferentes, transacciones faltantes (en uno pero no en otro), estados inconsistentes
  5. Genera reporte de reconciliacion
- [ ] Si hay discrepancias:
  - Alerta automatica (email a equipo de ops)
  - Registro en tabla de discrepancias
- [ ] Si todo cuadra: registro de reconciliacion exitosa

**Tareas Tecnicas:**
1. Crear ReconciliationService
2. Implementar comparacion ledger vs Monato
3. Modelo de discrepancia
4. Job programado (Lambda + CloudWatch Events)
5. Notificaciones de alerta
6. Tests con escenarios: match perfecto, monto diferente, faltante, estado diferente

**Dependencias:** US-SP-011, US-SP-014
**Estimacion:** 4 dev-days

---

#### US-SP-034: Dashboard de Reconciliacion

**ID:** US-SP-034
**Epica:** EP-SP-009
**Prioridad:** P2

**Historia:**
Como **Administrador de Plataforma** quiero un dashboard de reconciliacion para ver el estado de la reconciliacion diaria y resolver discrepancias.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/admin/reconciliation` (solo admins)
- [ ] Vista de calendario con color por dia:
  - Verde: reconciliacion exitosa
  - Rojo: discrepancias encontradas
  - Gris: no ejecutado
- [ ] Detalle por dia: lista de discrepancias con accion de resolucion
- [ ] Resolucion manual:
  - "Ajustar ledger" (crea entry de ajuste)
  - "Ignorar" (con justificacion)
  - "Escalar" (notifica a supervisor)
- [ ] Metricas: tasa de discrepancia, tendencia, tiempo promedio de resolucion

**Tareas Tecnicas:**
1. Crear ReconciliationDashboardComponent
2. Crear ReconciliationCalendarComponent
3. Crear DiscrepancyDetailComponent
4. Adapter para API de reconciliacion
5. Tests

**Dependencias:** US-SP-033, US-SP-025
**Estimacion:** 4 dev-days

---

#### US-SP-035: Audit Trail Completo

**ID:** US-SP-035
**Epica:** EP-SP-009
**Prioridad:** P1

**Historia:**
Como **Administrador de Plataforma** quiero un registro completo de todas las acciones del sistema para cumplir con regulaciones y poder investigar incidentes.

**Criterios de Aceptacion:**
- [ ] Cada operacion registra en tabla de audit:
  - `who`: user_id o "SYSTEM"
  - `what`: accion (CREATE_ACCOUNT, SEND_TRANSFER, CHANGE_STATUS, etc.)
  - `when`: timestamp preciso
  - `where`: IP, user-agent, session_id
  - `details`: JSON con datos relevantes (before/after para updates)
- [ ] `GET /api/v1/admin/audit-log` con filtros: usuario, accion, recurso, fecha
- [ ] Pagina `/sp/admin/audit` en mf-sp
- [ ] Registros son append-only (no se pueden editar ni borrar)
- [ ] Retencion: 7 anos (configurable)

**Tareas Tecnicas:**
1. Modelo de AuditEntry en DynamoDB
2. AuditService con metodo `log(action, details)`
3. Integrar en todos los servicios existentes
4. Endpoint de consulta con filtros
5. UI de visualizacion
6. Tests

**Dependencias:** US-SP-002, US-SP-014
**Estimacion:** 4 dev-days

---

### EP-SP-010: Limites, Politicas y Notificaciones

---

#### US-SP-036: Limites de Transaccion Configurables

**ID:** US-SP-036
**Epica:** EP-SP-010
**Prioridad:** P1

**Historia:**
Como **Administrador de Plataforma** quiero configurar limites de transaccion por cuenta y por organizacion para controlar el riesgo y cumplir con regulaciones.

**Criterios de Aceptacion:**
- [ ] Modelo `TransactionLimits`:
  - `max_per_transaction`: monto maximo por operacion
  - `max_daily`: monto maximo acumulado en 24 horas
  - `max_monthly`: monto maximo acumulado en 30 dias
  - `max_operations_daily`: numero maximo de operaciones por dia
- [ ] Limites se configuran a 3 niveles (orden de prioridad):
  1. Cuenta especifica (override mas alto)
  2. Organizacion
  3. Global (default del sistema)
- [ ] `PATCH /api/v1/organizations/{org_id}/accounts/{id}/limits` - Configurar limites de cuenta
- [ ] `PATCH /api/v1/organizations/{org_id}/limits` - Configurar limites de organizacion
- [ ] Validacion en TransferService antes de cada operacion
- [ ] Warning al 80% del limite (notificacion)
- [ ] Bloqueo al 100% del limite (error 429)

**Tareas Tecnicas:**
1. Modelo de limites en DynamoDB
2. Servicio de evaluacion de limites
3. Integracion en TransferService
4. Endpoints de configuracion
5. Logica de acumulado diario/mensual
6. Tests de todos los niveles y escenarios

**Dependencias:** US-SP-014
**Estimacion:** 4 dev-days

---

#### US-SP-037: Politica de Aprobacion de Transferencias

**ID:** US-SP-037
**Epica:** EP-SP-010
**Prioridad:** P2

**Historia:**
Como **Cliente Empresarial** quiero que transferencias por encima de un monto configurable requieran aprobacion de otro usuario para tener control dual sobre movimientos grandes.

**Criterios de Aceptacion:**
- [ ] Configuracion de politica por organizacion:
  - `approval_threshold`: monto a partir del cual se requiere aprobacion
  - `required_approvers`: numero de aprobaciones necesarias (default 1)
  - `approver_roles`: roles que pueden aprobar
- [ ] Flujo con aprobacion:
  1. Usuario crea transferencia -> status: PENDING_APPROVAL
  2. Notificacion a aprobadores
  3. Aprobador aprueba en mf-sp -> status: PENDING -> continua flujo normal
  4. Si rechazada: status: REJECTED, notificacion al creador
- [ ] `POST /api/v1/organizations/{org_id}/transfers/{id}/approve`
- [ ] `POST /api/v1/organizations/{org_id}/transfers/{id}/reject`
- [ ] Pagina de aprobaciones pendientes en mf-sp
- [ ] Timeout configurable: si no se aprueba en X horas, se cancela automaticamente

**Tareas Tecnicas:**
1. Modelo de politica de aprobacion
2. Flujo de aprobacion en TransferService
3. Endpoints approve/reject
4. Notificaciones a aprobadores
5. UI de aprobaciones pendientes
6. Tests del flujo completo

**Dependencias:** US-SP-014
**Estimacion:** 4 dev-days

---

#### US-SP-038: Notificaciones de Eventos SPEI

**ID:** US-SP-038
**Epica:** EP-SP-010
**Prioridad:** P1

**Historia:**
Como **Cliente Empresarial** quiero recibir notificaciones cuando recibo un deposito SPEI, cuando mi transferencia se completa o falla, y cuando alcanzo limites, para estar informado de la actividad de mis cuentas.

**Criterios de Aceptacion:**
- [ ] Eventos que generan notificacion:
  - Deposito SPEI recibido (money_in)
  - Transferencia SPEI out completada
  - Transferencia SPEI out fallida
  - Transferencia pendiente de aprobacion
  - Limite al 80% alcanzado
  - Limite excedido (operacion bloqueada)
  - Cuenta congelada/descongelada
- [ ] Canales de notificacion:
  - Email (via covacha-notifications)
  - Notificacion in-app (toast + badge en sidebar)
  - Webhook externo (configurable por organizacion)
- [ ] Preferencias de notificacion configurables por usuario
- [ ] Template de email profesional con detalle de la operacion

**Tareas Tecnicas:**
1. Definir eventos de notificacion y templates
2. Integrar con covacha-notifications
3. Implementar webhook externo
4. UI de preferencias de notificacion
5. Tests

**Dependencias:** US-SP-019, US-SP-020
**Estimacion:** 4 dev-days

---

#### US-SP-039: Configuracion de Politicas via UI

**ID:** US-SP-039
**Epica:** EP-SP-010
**Prioridad:** P2

**Historia:**
Como **Administrador de Plataforma** quiero configurar limites y politicas desde la interfaz grafica para no depender de cambios en base de datos o despliegues.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/admin/policies`
- [ ] Secciones:
  - Limites globales (default del sistema)
  - Limites por organizacion (override)
  - Limites por cuenta (override especifico)
  - Politica de aprobacion
  - Configuracion de comisiones
- [ ] Formularios con validacion en tiempo real
- [ ] Preview del efecto: "Con estos limites, la organizacion X podria transferir hasta $Y diarios"
- [ ] Historial de cambios a politicas (quien cambio que, cuando)
- [ ] Confirmacion antes de aplicar cambios criticos

**Tareas Tecnicas:**
1. Crear PoliciesPageComponent
2. Crear LimitsConfigComponent
3. Crear ApprovalConfigComponent
4. Crear CommissionConfigComponent
5. Adapter para API de politicas
6. Tests

**Dependencias:** US-SP-036, US-SP-037, US-SP-025
**Estimacion:** 4 dev-days

---

## Orden de Implementacion

### Roadmap Visual

```
Semana 1-2:  [EP-SP-001 Account Core Engine    ]  [EP-SP-002 Monato Driver          ]
                         |                                    |
Semana 2-3:  [EP-SP-003 Double-Entry Ledger    ]  [EP-SP-007 mf-sp Scaffold+Dashboard]
                    |              |                           |
Semana 3:    [EP-SP-004 SPEI Out  ]  [EP-SP-005 Webhook In ]  [EP-SP-006 Internos]
                    |              |            |              |
Semana 4:    [EP-SP-008 mf-sp Transfers UI                                        ]
                         |
Semana 4-5:  [EP-SP-009 Reconciliacion                ]
                                                       |
Semana 5-6:  [EP-SP-010 Limites + Politicas + Notif                               ]
```

### Fase 1: Fundamentos (Semanas 1-2) -- MVP Backend

**Objetivo:** Tener el motor de cuentas y la integracion con Monato funcionando.

| Orden | Epica | User Stories | Razon |
|-------|-------|-------------|-------|
| 1a | EP-SP-001 | US-SP-001, US-SP-002, US-SP-003, US-SP-004 | Modelo de dominio es la base de todo |
| 1b | EP-SP-002 | US-SP-006, US-SP-007, US-SP-008, US-SP-009 | Integracion Monato se puede hacer en paralelo |

**Criterio de salida de Fase 1:**
- Se pueden crear los 4 tipos de cuenta via API
- Se puede crear una cuenta CLABE y obtener CLABE de Monato
- El grafo de relaciones funciona
- Hay tests cubriendo happy path y errores principales

**Riesgo principal:** Integracion con API de Monato (validar acceso y formato de respuestas lo antes posible)

---

### Fase 2: Contabilidad + UI Base (Semanas 2-3)

**Objetivo:** Sistema contable funcional y primera version visible del frontend.

| Orden | Epica | User Stories | Razon |
|-------|-------|-------------|-------|
| 2a | EP-SP-003 | US-SP-010, US-SP-011, US-SP-012, US-SP-013 | Ledger es prerequisito de transferencias |
| 2b | EP-SP-007 | US-SP-025, US-SP-026, US-SP-027 | Frontend puede empezar con API de cuentas |
| 2c | EP-SP-001 | US-SP-005 | Saldo requiere ledger listo |

**Criterio de salida de Fase 2:**
- Ledger registra transacciones de partida doble
- Saldo se calcula desde ledger correctamente
- mf-sp carga en el Shell y muestra dashboard de cuentas
- Balance trial pasa

---

### Fase 3: Flujos Financieros Core (Semana 3)

**Objetivo:** Las 3 operaciones financieras principales funcionan end-to-end.

| Orden | Epica | User Stories | Razon |
|-------|-------|-------------|-------|
| 3a | EP-SP-004 | US-SP-014, US-SP-015, US-SP-016 | SPEI Out es la feature mas critica |
| 3b | EP-SP-005 | US-SP-018, US-SP-019, US-SP-020 | SPEI In completa el ciclo financiero |
| 3c | EP-SP-006 | US-SP-022, US-SP-024 | Movimientos internos son fundamentales |

**Criterio de salida de Fase 3:**
- Se puede enviar SPEI out y el dinero llega
- Se pueden recibir depositos SPEI y el saldo se actualiza
- Se pueden mover fondos entre cuentas internas
- Partida doble se mantiene correcta en los 3 flujos

**Riesgo principal:** Timing de webhooks de Monato, comportamiento en errores reales

---

### Fase 4: UI de Operaciones (Semana 4)

**Objetivo:** Usuarios pueden operar desde la interfaz grafica.

| Orden | Epica | User Stories | Razon |
|-------|-------|-------------|-------|
| 4a | EP-SP-008 | US-SP-029, US-SP-030, US-SP-031 | UI de transferencias es el valor visible al usuario |
| 4b | EP-SP-004 | US-SP-017 | Beneficiarios mejoran UX |
| 4c | EP-SP-005 | US-SP-021 | DLQ protege contra perdida de eventos |
| 4d | EP-SP-006 | US-SP-023 | Dispersion masiva es feature de alto valor |

**Criterio de salida de Fase 4:**
- Un usuario puede enviar SPEI out desde la UI
- Un usuario puede mover fondos internamente desde la UI
- Historial de movimientos funciona con filtros y paginacion
- Beneficiarios frecuentes funcionan

---

### Fase 5: Reconciliacion y Auditoria (Semanas 4-5)

**Objetivo:** El sistema es auditable y detecta inconsistencias.

| Orden | Epica | User Stories | Razon |
|-------|-------|-------------|-------|
| 5a | EP-SP-009 | US-SP-033, US-SP-035 | Reconciliacion y audit trail son criticos para operacion |
| 5b | EP-SP-009 | US-SP-034 | Dashboard de reconciliacion es nice-to-have |

**Criterio de salida de Fase 5:**
- Reconciliacion diaria automatica funciona
- Audit trail registra todas las operaciones
- Balance trial se ejecuta diariamente
- Se detectan y alertan discrepancias

---

### Fase 6: Hardening y Politicas (Semanas 5-6)

**Objetivo:** Sistema listo para produccion con controles de riesgo.

| Orden | Epica | User Stories | Razon |
|-------|-------|-------------|-------|
| 6a | EP-SP-010 | US-SP-036, US-SP-038 | Limites y notificaciones son P1 para produccion |
| 6b | EP-SP-010 | US-SP-037, US-SP-039 | Aprobaciones y UI de config son P2 |
| 6c | EP-SP-007 | US-SP-028 | Visualizacion del grafo es nice-to-have |
| 6d | EP-SP-008 | US-SP-032 | Estado en tiempo real mejora UX |

**Criterio de salida de Fase 6:**
- Limites de transaccion configurados y funcionando
- Notificaciones de eventos clave enviandose
- Politicas de aprobacion opcionales
- UI de administracion de politicas

---

### MVP (Minimo Producto Viable)

El MVP se alcanza al completar **Fases 1-4**, que incluye:

| Capacidad | User Stories |
|-----------|-------------|
| Crear 4 tipos de cuenta | US-SP-001, US-SP-002, US-SP-003, US-SP-004 |
| Integracion Monato completa | US-SP-006, US-SP-007, US-SP-008, US-SP-009 |
| Contabilidad de partida doble | US-SP-010, US-SP-011, US-SP-012 |
| Consulta de saldo | US-SP-005 |
| Enviar SPEI out | US-SP-014, US-SP-015 |
| Recibir SPEI in | US-SP-018, US-SP-019, US-SP-020 |
| Movimientos internos | US-SP-022, US-SP-024 |
| UI: Dashboard de cuentas | US-SP-025, US-SP-026, US-SP-027 |
| UI: Formulario de transferencia | US-SP-029, US-SP-030, US-SP-031 |

**Estimacion MVP:** ~4 semanas con 2 desarrolladores (1 backend, 1 frontend)

---

## Grafo de Dependencias

```
US-SP-001 (Modelo Cuentas)
  |
  +-> US-SP-002 (CRUD API) --> US-SP-003 (Grafo) --> US-SP-028 (UI Arbol)
  |     |                        |
  |     +-> US-SP-004 (Estados)  |
  |     |                        |
  |     +-> US-SP-024 (Reglas) --+-> US-SP-022 (Transfer Interno) --> US-SP-023 (Bulk)
  |                                        |
  +-> US-SP-010 (Modelo Ledger)            +-> US-SP-030 (UI Interno)
        |
        +-> US-SP-011 (Servicio Ledger) --> US-SP-012 (Calculo Saldo)
              |                                   |
              |                             US-SP-005 (API Saldo)
              |                                   |
              +-> US-SP-013 (Balance Trial)       +-> US-SP-026 (UI Dashboard)
              |                                         |
              +-> US-SP-014 (SPEI Out) ----+            +-> US-SP-027 (UI Detalle)
                    |            |         |
                    |            |    US-SP-033 (Reconciliacion)
                    |            |         |
                    |            |    US-SP-034 (UI Reconciliacion)
                    |            |
                    +-> US-SP-015 (Reservada)
                    +-> US-SP-016 (Comisiones)
                    +-> US-SP-017 (Beneficiarios) --> US-SP-029 (UI SPEI Out)
                    +-> US-SP-020 (Webhook Status)
                    +-> US-SP-036 (Limites)
                    +-> US-SP-037 (Aprobaciones)

US-SP-006 (Interface SPEIProvider)
  |
  +-> US-SP-007 (Monato Create Account)
  +-> US-SP-008 (Monato Money Out)
  +-> US-SP-009 (Monato Utils)

US-SP-018 (Webhook Endpoint)
  |
  +-> US-SP-019 (Money In Processing) --> US-SP-038 (Notificaciones)
  +-> US-SP-020 (Status Updates)
  +-> US-SP-021 (DLQ + Retries)

US-SP-025 (Scaffold mf-sp)
  |
  +-> US-SP-026 (UI Dashboard)
  +-> US-SP-029 (UI SPEI Out)
  +-> US-SP-030 (UI Interno)
  +-> US-SP-031 (UI Movimientos)
  +-> US-SP-032 (UI Status Real-time)
  +-> US-SP-034 (UI Reconciliacion)
  +-> US-SP-039 (UI Politicas)
```

---

## Riesgos y Mitigaciones

| # | Riesgo | Probabilidad | Impacto | Mitigacion |
|---|--------|-------------|---------|------------|
| R1 | API de Monato no funciona como esperado | Alta | Alto | Validar integracion en Semana 1 con spike tecnico. Tener sandbox de Monato accesible. |
| R2 | Webhooks de Monato llegan tarde o desordenados | Media | Alto | Disenar para eventual consistency. Idempotencia en todo. Reconciliacion diaria. |
| R3 | Performance del ledger con alto volumen | Media | Medio | Implementar snapshots de saldo. Benchmark temprano (US-SP-012). |
| R4 | Concurrencia en saldo (double spending) | Media | Critico | Usar DynamoDB conditional writes o TransactWriteItems. Test de concurrencia. |
| R5 | Regulacion CNBV/Banxico requiere cambios | Baja | Alto | Consultar con compliance antes de lanzar. Disenar con flexibilidad. |
| R6 | Monato cambia su API sin aviso | Baja | Medio | Strategy Pattern permite cambiar proveedor. Versionado de driver. |
| R7 | Scaffold de mf-sp toma mas tiempo del esperado | Baja | Medio | Reusar estructura de mf-marketing al maximo. Copiar HttpService y SharedState. |
| R8 | Perdida de webhook (Monato no entrega) | Media | Alto | Polling de respaldo cada 5 minutos para transferencias PENDING > 10 min. |

### Spike Tecnico Recomendado (Pre-Sprint)

Antes de iniciar el Sprint 1, dedicar 2-3 dias a:

1. **Validar acceso a API de Monato**: Crear cuenta, obtener CLABE, hacer money out de prueba
2. **Validar webhook delivery**: Registrar URL, provocar un money_in, verificar que llega
3. **Benchmark DynamoDB**: Simular 10k entries en ledger y medir tiempo de calculo de saldo
4. **Definir esquema de tabla DynamoDB**: Single table design para cuentas + ledger + transfers

---

## Definition of Done Global

Cada User Story se considera terminada cuando:

- [ ] Codigo implementado y funcionando
- [ ] Tests unitarios con cobertura >= 98%
- [ ] Tests de integracion para endpoints (happy path + errores)
- [ ] Sin errores de lint (ruff check para Python, ng lint para Angular)
- [ ] Build de produccion exitoso
- [ ] Ningun archivo excede 1000 lineas
- [ ] Ninguna funcion excede 50 lineas
- [ ] Documentacion de API actualizada (OpenAPI para backend, JSDoc para frontend)
- [ ] Code review aprobado (PR automatico via GitHub Actions)
- [ ] Commit messages siguen formato: `tipo(ISS-XXX): descripcion`
- [ ] Logs estructurados para operaciones financieras (sin datos sensibles)
- [ ] Idempotency key implementada en operaciones mutativas

### Criterios Especificos Financieros

- [ ] Partida doble verificada: SUM(debits) == SUM(credits) para cada transaccion
- [ ] No se pueden eliminar entries del ledger (append-only verificado)
- [ ] Audit trail registra la operacion
- [ ] Manejo de decimales con precision (no usar float, usar Decimal)
- [ ] Montos siempre en centavos internamente (evitar errores de redondeo)
- [ ] CLABE validada con algoritmo de checksum
- [ ] Datos sensibles NO aparecen en logs (CLABEs truncadas, sin tokens)

---

## Resumen de Estimaciones

| Epica | User Stories | Dev-Days Estimados |
|-------|-------------|-------------------|
| EP-SP-001 | 5 stories | 15 dev-days |
| EP-SP-002 | 4 stories | 12 dev-days |
| EP-SP-003 | 4 stories | 11 dev-days |
| EP-SP-004 | 4 stories | 11 dev-days |
| EP-SP-005 | 4 stories | 13 dev-days |
| EP-SP-006 | 3 stories | 9 dev-days |
| EP-SP-007 | 4 stories | 15 dev-days |
| EP-SP-008 | 4 stories | 15 dev-days |
| EP-SP-009 | 3 stories | 12 dev-days |
| EP-SP-010 | 4 stories | 16 dev-days |
| **TOTAL** | **39 stories** | **129 dev-days** |

**Con buffer de 20% para imprevistos:** ~155 dev-days

**Con 2 desarrolladores full-time:** ~16 semanas (4 meses)

**Solo MVP (Fases 1-4):** ~80 dev-days = ~10 semanas (2.5 meses) con 2 devs

---

## Notas para la Implementacion

### DynamoDB Single Table Design

Se recomienda una sola tabla `superpago-spei` con particiones claras:

| Entidad | PK | SK |
|---------|----|----|
| Account | `ORG#{org_id}` | `ACCOUNT#{account_id}` |
| Account by Parent | `PARENT#{parent_id}` | `ACCOUNT#{account_id}` |
| Account by CLABE | `CLABE#{clabe}` | `ACCOUNT#{account_id}` |
| Ledger Entry | `ACCOUNT#{account_id}` | `ENTRY#{timestamp}#{entry_id}` |
| Transaction | `TXN#{transaction_id}` | `ENTRY#{entry_id}` |
| Transfer | `ORG#{org_id}` | `TRANSFER#{transfer_id}` |
| Beneficiary | `ORG#{org_id}` | `BENEFICIARY#{beneficiary_id}` |
| Limit | `ORG#{org_id}` | `LIMIT#{scope}#{id}` |
| Audit | `ORG#{org_id}` | `AUDIT#{timestamp}#{audit_id}` |
| Idempotency | `IDEMPOTENCY#{key}` | `#` |
| Reconciliation | `RECON#{date}` | `ORG#{org_id}` |
| Discrepancy | `RECON#{date}` | `DISCREPANCY#{id}` |

### Precision Numerica

- **Interno:** Todos los montos en centavos (enteros). $100.50 MXN = 10050 centavos.
- **API:** Acepta y retorna montos en pesos con 2 decimales. Conversion en la capa de servicio.
- **DynamoDB:** Stored como Number (centavos).
- **Python:** Usar `Decimal` para calculos, nunca `float`.

### Idempotency Keys

- Formato: UUID v4 generado por el cliente
- TTL: 48 horas
- Tabla: `IDEMPOTENCY#{key}` con response cacheado
- Si la key ya existe: retornar response anterior sin re-ejecutar

### Integracion con Ecosistema Existente

| Componente | Como se integra |
|------------|----------------|
| mf-core (Shell) | Registra mfSP como remote en federation.config.js |
| covacha-webhook | Nueva Blueprint /webhook/spei/monato/ |
| covacha-notifications | Envio de emails y notificaciones de eventos SPEI |
| SharedState | mf-sp lee auth, user, org desde localStorage (igual que mf-marketing) |
| API Gateway | Nueva ruta /api/v1/organizations/{id}/accounts/* apuntando a covacha-payment |
