# SuperPago BillPay - Product Plan Completo

**Fecha**: 2026-02-14
**Product Owner**: SuperPago
**Proveedor BillPay**: Monato BillPay (https://docs.monato.com/products/billpay)
**Proveedor SPEI**: Monato Fincore
**Estado**: Planificacion
**Continua desde**: ARCHITECTURE_OPERATIONS_TRANSACTIONS.md (modelo base), SPEI-PRODUCT-PLAN.md (Account Core Engine)

---

## Tabla de Contenidos

1. [Vision del Producto](#1-vision-del-producto)
2. [Relacion con la Arquitectura Existente](#2-relacion-con-la-arquitectura-existente)
3. [Onboarding de Cliente (Provisionamiento de Productos)](#3-onboarding-de-cliente)
4. [Producto BillPay - Diseno Completo](#4-producto-billpay)
5. [Flujo Completo de Pago de Servicio](#5-flujo-completo-de-pago-de-servicio)
6. [Operacion BILLPAY - Bloques de Transacciones](#6-operacion-billpay-bloques-de-transacciones)
7. [Conciliacion BillPay](#7-conciliacion-billpay)
8. [Modelo DynamoDB Expandido](#8-modelo-dynamodb-expandido)
9. [Strategy Pattern para BillPay](#9-strategy-pattern-para-billpay)
10. [Estructura de Cuentas por Producto](#10-estructura-de-cuentas-por-producto)
11. [API Endpoints](#11-api-endpoints)
12. [Mapa de Epicas](#12-mapa-de-epicas)
13. [Riesgos y Mitigaciones](#13-riesgos-y-mitigaciones)

---

## 1. Vision del Producto

SuperPago ofrece **BillPay** como producto de pago de servicios a sus clientes empresariales. A traves de Monato BillPay, los usuarios finales pueden pagar electricidad (CFE), agua, telefono, internet, TV de paga, gas, recargas telefonicas, SAT, IMSS, INFONAVIT, peajes y mas de 500 proveedores de servicios en Mexico.

### Propuesta de valor

| Actor | Beneficio |
|-------|-----------|
| Cliente Empresa (Boxito) | Ofrece pago de servicios a sus propios usuarios sin integrarse directo con cada biller |
| Usuario Final (empleado de Boxito) | Paga sus recibos desde la app de su empresa, con cargo a su cuenta digital |
| SuperPago (plataforma) | Cobra comision por cada pago ejecutado, expande el uso de cuentas digitales |
| Agente IA WhatsApp | Permite pagar servicios via conversacion: "Paga mi recibo de luz" |

### Alcance del MVP

- Consulta de deuda/saldo por referencia + proveedor
- Pago de servicio con cargo a cuenta digital del usuario
- Catalogo de categorias y proveedores de servicio
- Comision configurable por organizacion
- Comprobante de pago digital
- Conciliacion automatica diaria
- Integracion con Agente IA WhatsApp (EP-SP-017/EP-SP-018)

---

## 2. Relacion con la Arquitectura Existente

BillPay NO es un sistema aislado. Se monta sobre el **Account Core Engine** ya disenado en `ARCHITECTURE_OPERATIONS_TRANSACTIONS.md`.

### Lo que ya existe (disenado)

| Componente | Documento | Estado |
|------------|-----------|--------|
| Modelo de Cuentas (`modspei_accounts_prod`) | ARCHITECTURE_OPERATIONS_TRANSACTIONS.md seccion 3 | Disenado |
| Modelo de Operaciones (`modspei_operations_prod`) | ARCHITECTURE_OPERATIONS_TRANSACTIONS.md seccion 4 | Disenado |
| Modelo de Transacciones (`modspei_transactions_prod`) | ARCHITECTURE_OPERATIONS_TRANSACTIONS.md seccion 5 | Disenado |
| OperationType.BILLPAY | ARCHITECTURE_OPERATIONS_TRANSACTIONS.md seccion 4 enum | Disenado |
| Bloque de TXN para BILLPAY | ARCHITECTURE_OPERATIONS_TRANSACTIONS.md seccion 6.11 | Disenado |
| TransactWriteItems BILLPAY (2 fases) | ARCHITECTURE_OPERATIONS_TRANSACTIONS.md seccion 7.10 | Disenado |
| Strategy Pattern (SPEIProvider) | SPEI-PRODUCT-PLAN.md EP-SP-002 | Disenado |
| Maquina de estados BILLPAY | ARCHITECTURE_OPERATIONS_TRANSACTIONS.md seccion 4 | Disenado |

### Lo que agrega este documento

| Componente | Descripcion |
|------------|-------------|
| Onboarding multi-producto | Provisionamiento automatico de cuentas por producto contratado |
| Tabla `modspei_billpay_payments` | Registro detallado de cada pago de servicio (biller, referencia, etc.) |
| Tabla `modspei_billpay_providers` | Catalogo local de proveedores de servicio sincronizado con Monato |
| Interface `BillPayProvider` | Strategy Pattern separado para proveedores de BillPay |
| `MonatoBillPayDriver` | Implementacion concreta para Monato BillPay |
| Flujo de consulta de deuda | Query al proveedor antes de pagar |
| Conciliacion BillPay | Lambda/Job que reconcilia pagos vs Monato diariamente |
| Expansion de `AccountType` | Nuevos tipos de cuenta especificos para BillPay |

---

## 3. Onboarding de Cliente

### 3.1 Concepto: Producto como Unidad de Provisionamiento

Cuando un admin de SuperPago registra un nuevo cliente empresa (organizacion), le asigna uno o mas **productos**. Cada producto define automaticamente que cuentas se crean.

### 3.2 Catalogo de Productos

```
ProductType (enum):
  SPEI         - Transferencias bancarias (SPEI in/out, CLABEs, dispersion)
  BILLPAY      - Pago de servicios (luz, agua, telefono, recargas, etc.)
  OPENPAY      - Cobros con tarjeta (Openpay como procesador)
  CASH         - Red de puntos de pago (Cash-In / Cash-Out)
  MARKETPLACE  - Subasta de efectivo
```

### 3.3 Cuentas Generadas por Producto

Cada producto tiene una receta de cuentas que se crean automaticamente al activarlo para una organizacion.

#### SPEI

```
CONCENTRADORA_SPEI              - Cuenta raiz para operaciones SPEI
RESERVADA_COMISIONES_SPEI       - Fees que cobra SuperPago por SPEI
CLABE_PRINCIPAL                 - Primera CLABE operativa (se provee en Monato)
```

#### BILLPAY

```
CONCENTRADORA_BILLPAY           - Cuenta raiz para pagos de servicios
RESERVADA_COMISIONES_BILLPAY    - Fees que cobra SuperPago por cada pago
RESERVADA_FONDEO_BILLPAY        - Pool de fondos disponibles para ejecutar pagos
```

#### OPENPAY

```
CONCENTRADORA_OPENPAY           - Cuenta raiz para cobros con tarjeta
RESERVADA_COMISIONES_OPENPAY    - Fees de SuperPago sobre cobros Openpay
```

#### CASH

```
TRANSIT_CASH                    - Cuenta transitoria por punto de venta
RESERVADA_COMISIONES_CASH       - Fees por operaciones de efectivo
```

#### Cuentas Globales (se crean siempre, independiente del producto)

```
RESERVADA_IVA                   - 16% de todas las comisiones cobradas
RESERVADA_RETENCIONES           - Retenciones fiscales si aplica
```

### 3.4 Expansion del Enum AccountType

El enum existente en `ARCHITECTURE_OPERATIONS_TRANSACTIONS.md` seccion 3 se expande:

```
AccountType (enum expandido):

# --- Existentes ---
CONCENTRADORA               - Cuenta madre generica
CLABE_PRIVADA               - Cuenta con CLABE asignada
DISPERSION                  - Cuenta para dispersion de pagos
TRANSIT_CASH                - Cuenta transitoria punto de venta
RESERVADA_COMISIONES        - Cuenta de comisiones generica
VIRTUAL                     - Cuenta virtual sin CLABE

# --- Nuevos (especificos por producto) ---
CONCENTRADORA_SPEI          - Concentradora exclusiva para SPEI
CONCENTRADORA_BILLPAY       - Concentradora exclusiva para BillPay
CONCENTRADORA_OPENPAY       - Concentradora exclusiva para Openpay
RESERVADA_COMISIONES_SPEI   - Comisiones de operaciones SPEI
RESERVADA_COMISIONES_BILLPAY - Comisiones de pagos de servicios
RESERVADA_COMISIONES_OPENPAY - Comisiones de cobros con tarjeta
RESERVADA_COMISIONES_CASH   - Comisiones de operaciones de efectivo
RESERVADA_FONDEO_BILLPAY    - Pool de fondos para ejecutar pagos de servicios
RESERVADA_IVA               - IVA sobre comisiones cobradas
RESERVADA_RETENCIONES       - Retenciones fiscales
```

**Nota sobre decision de diseno**: Se prefiere tener tipos de cuenta granulares (por producto) en lugar de una sola `CONCENTRADORA` generica por varias razones:
1. Aislamiento contable: el saldo de BillPay no se mezcla con SPEI
2. Limites independientes: cada producto tiene sus propias politicas
3. Reconciliacion simplificada: cada concentradora se reconcilia contra su proveedor
4. Auditoria clara: se sabe exactamente de donde viene cada movimiento

### 3.5 Ejemplo Completo: Onboarding de "Boxito"

```
Paso 1: Admin SuperPago crea organizacion "Boxito" (org_boxito)
Paso 2: Admin asigna productos: [SPEI, BILLPAY]

Resultado automatico:

Boxito (org_boxito)
|
+-- PRODUCTO SPEI:
|   +-- Concentradora SPEI (account_type: CONCENTRADORA_SPEI)
|   |     alias: "Boxito - Concentradora SPEI"
|   |     provider: "monato"
|   |     provider_account_id: (creada en Monato Fincore)
|   |
|   +-- Reservada Comisiones SPEI (account_type: RESERVADA_COMISIONES_SPEI)
|   |     alias: "Boxito - Comisiones SPEI"
|   |     parent_account_id: concentradora_spei.id
|   |
|   +-- CLABE Principal (account_type: CLABE_PRIVADA)
|         alias: "Boxito - CLABE Principal"
|         clabe: "646180XXXXXXXXXXXX" (generada por Monato)
|         parent_account_id: concentradora_spei.id
|
+-- PRODUCTO BILLPAY:
|   +-- Concentradora BillPay (account_type: CONCENTRADORA_BILLPAY)
|   |     alias: "Boxito - Concentradora BillPay"
|   |     provider: "monato_billpay"
|   |
|   +-- Reservada Comisiones BillPay (account_type: RESERVADA_COMISIONES_BILLPAY)
|   |     alias: "Boxito - Comisiones BillPay"
|   |     parent_account_id: concentradora_billpay.id
|   |
|   +-- Reservada Fondeo BillPay (account_type: RESERVADA_FONDEO_BILLPAY)
|         alias: "Boxito - Fondeo BillPay"
|         parent_account_id: concentradora_billpay.id
|
+-- CUENTAS GLOBALES:
    +-- Reservada IVA (account_type: RESERVADA_IVA)
    |     alias: "Boxito - IVA"
    |
    +-- Reservada Retenciones (account_type: RESERVADA_RETENCIONES)
          alias: "Boxito - Retenciones"
```

### 3.6 Cuentas de SuperPago (Plataforma)

SuperPago como organizacion (`org_superpago`) tiene su propio arbol de cuentas que reciben comisiones de TODOS los clientes:

```
SuperPago (org_superpago = 39c56b2b-cbec-4645-b4b3-7b618e5a8888)
|
+-- Concentradora Master SPEI
|     account_type: CONCENTRADORA_SPEI
|     Proposito: Pool maestro de fondos SPEI, fondea a Monato Fincore
|
+-- Concentradora Master BillPay
|     account_type: CONCENTRADORA_BILLPAY
|     Proposito: Pool maestro para pagos de servicios, fondea a Monato BillPay
|
+-- Revenue SPEI
|     account_type: RESERVADA_COMISIONES_SPEI
|     Proposito: TODAS las comisiones SPEI cobradas a TODOS los clientes
|
+-- Revenue BillPay
|     account_type: RESERVADA_COMISIONES_BILLPAY
|     Proposito: TODAS las comisiones BillPay cobradas a TODOS los clientes
|
+-- Revenue Openpay
|     account_type: RESERVADA_COMISIONES_OPENPAY
|     Proposito: TODAS las comisiones Openpay cobradas
|
+-- Revenue Cash
|     account_type: RESERVADA_COMISIONES_CASH
|     Proposito: TODAS las comisiones Cash cobradas
|
+-- IVA Plataforma
|     account_type: RESERVADA_IVA
|     Proposito: IVA acumulado sobre TODAS las comisiones
|
+-- Transit Cash Global
      account_type: TRANSIT_CASH
      Proposito: Efectivo total en la red de puntos de venta
```

### 3.7 Flujo de Onboarding - Secuencia Tecnica

```
POST /api/v1/organizations/{org_id}/products
Body: {
  "products": ["SPEI", "BILLPAY"],
  "initiated_by": "admin_user_id"
}
```

**Secuencia interna:**

```
1. Validar organizacion existe y esta ACTIVE
2. Validar que no tiene los productos ya activados (idempotencia)
3. Para cada producto en el array:
   |
   +-- SPEI:
   |   a) Crear cuenta en Monato Fincore (POST /api/monato/fincore/accounts)
   |   b) Obtener CLABE generada
   |   c) Crear instrumento de pago en Monato
   |   d) Crear registros en modspei_accounts_prod:
   |      - CONCENTRADORA_SPEI (provider_account_id = monato_account_id)
   |      - RESERVADA_COMISIONES_SPEI (parent = concentradora)
   |      - CLABE_PRIVADA (clabe = monato_clabe, parent = concentradora)
   |   e) Registrar webhook de SPEI In en Monato
   |
   +-- BILLPAY:
       a) Registrar cliente en Monato BillPay (POST /auth/register o provision)
       b) Obtener credenciales/token de BillPay para esta org
       c) Crear registros en modspei_accounts_prod:
          - CONCENTRADORA_BILLPAY
          - RESERVADA_COMISIONES_BILLPAY (parent = concentradora_bp)
          - RESERVADA_FONDEO_BILLPAY (parent = concentradora_bp)
       d) Registrar webhook de BillPay en Monato

4. Crear cuentas globales (si no existen):
   - RESERVADA_IVA
   - RESERVADA_RETENCIONES

5. Registrar en tabla modspei_org_products_prod:
   - PK: org_id, SK: PRODUCT#SPEI, status: ACTIVE, provisioned_at, accounts: [...]
   - PK: org_id, SK: PRODUCT#BILLPAY, status: ACTIVE, provisioned_at, accounts: [...]

6. Retornar resumen:
   {
     "organization_id": "org_boxito",
     "products_provisioned": [
       {
         "product": "SPEI",
         "status": "ACTIVE",
         "accounts": [
           {"type": "CONCENTRADORA_SPEI", "id": "...", "alias": "..."},
           {"type": "RESERVADA_COMISIONES_SPEI", "id": "...", "alias": "..."},
           {"type": "CLABE_PRIVADA", "id": "...", "clabe": "646180...", "alias": "..."}
         ]
       },
       {
         "product": "BILLPAY",
         "status": "ACTIVE",
         "accounts": [
           {"type": "CONCENTRADORA_BILLPAY", "id": "...", "alias": "..."},
           {"type": "RESERVADA_COMISIONES_BILLPAY", "id": "...", "alias": "..."},
           {"type": "RESERVADA_FONDEO_BILLPAY", "id": "...", "alias": "..."}
         ]
       }
     ],
     "global_accounts": [
       {"type": "RESERVADA_IVA", "id": "..."},
       {"type": "RESERVADA_RETENCIONES", "id": "..."}
     ]
   }
```

### 3.8 Tabla de Productos por Organizacion

**Tabla: `modspei_org_products_prod`**

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| **PK** | `sp_organization_id` | Partition key |
| **SK** | `PRODUCT#{product_type}` | Sort key: ej. `PRODUCT#SPEI`, `PRODUCT#BILLPAY` |
| `product_type` | `str (enum)` | SPEI, BILLPAY, OPENPAY, CASH, MARKETPLACE |
| `status` | `str` | PROVISIONING, ACTIVE, SUSPENDED, DEACTIVATED |
| `accounts` | `list[dict]` | Array de cuentas creadas `[{account_id, account_type, alias}]` |
| `provider` | `str` | Proveedor para este producto ("monato_fincore", "monato_billpay") |
| `provider_credentials` | `dict` | Credenciales del proveedor para esta org (encriptadas) |
| `pricing` | `dict` | Configuracion de comisiones para esta org |
| `limits` | `dict` | Limites operativos para esta org |
| `provisioned_at` | `str (ISO8601)` | Cuando se activo |
| `provisioned_by` | `str` | Admin que lo activo |
| `updated_at` | `str (ISO8601)` | Ultima actualizacion |

**GSI-1: ProductStatusIndex**
```
GSIPK: product_type
GSISK: status#sp_organization_id
Projection: ALL
```
Uso: "Dame todas las organizaciones con BillPay activo"

### 3.9 Pricing por Producto por Organizacion

Cada organizacion puede tener tarifas diferentes segun su acuerdo comercial:

```json
{
  "pricing": {
    "fee_type": "FIXED_PLUS_PERCENT",
    "fixed_fee_mxn": "3.50",
    "percent_fee": "0.5",
    "min_fee_mxn": "3.50",
    "max_fee_mxn": "50.00",
    "iva_rate": "0.16",
    "fee_payer": "END_USER",
    "effective_from": "2026-03-01T00:00:00Z"
  }
}
```

| Campo | Descripcion |
|-------|-------------|
| `fee_type` | FIXED, PERCENT, FIXED_PLUS_PERCENT |
| `fixed_fee_mxn` | Monto fijo por operacion |
| `percent_fee` | Porcentaje sobre el monto del pago (0.5 = 0.5%) |
| `min_fee_mxn` | Comision minima (floor) |
| `max_fee_mxn` | Comision maxima (cap) |
| `iva_rate` | Tasa de IVA (0.16 = 16%) |
| `fee_payer` | Quien paga: END_USER (se suma al monto) u ORGANIZATION (se descuenta del saldo org) |

---

## 4. Producto BillPay

### 4.1 Monato BillPay - API Inferida

Basado en la documentacion de Monato y el patron estandar de agregadores de servicios en Mexico:

```
Autenticacion:
  POST   /auth/token                          - Obtener token JWT

Catalogo:
  GET    /billpay/categories                  - Categorias de servicio
  GET    /billpay/providers                   - Proveedores por categoria
  GET    /billpay/providers/{provider_id}     - Detalle del proveedor

Operaciones:
  POST   /billpay/query                       - Consultar deuda/saldo
  POST   /billpay/pay                         - Ejecutar pago
  GET    /billpay/transactions/{tx_id}        - Status de un pago
  GET    /billpay/transactions                - Listar pagos (con filtros)

Conciliacion:
  GET    /billpay/conciliation                - Reporte de conciliacion
  GET    /billpay/conciliation/detail/{id}    - Detalle de discrepancia

Webhooks:
  POST   /billpay/webhooks                    - Registrar webhook
  DELETE /billpay/webhooks/{id}               - Eliminar webhook
```

### 4.2 Categorias de Servicios en Mexico

| Categoria | Ejemplos de Proveedores | Requiere Query Previo |
|-----------|------------------------|----------------------|
| Electricidad | CFE | Si (consulta saldo pendiente) |
| Telefonia Fija | Telmex | Si |
| Internet | Telmex, Izzi, Totalplay, Megacable | Si |
| TV de Paga | Sky, Dish, Star TV | Si |
| Gas Natural | Gas Natural, diversas por region | Si |
| Agua | SAPAS, SIAPA, CAEM (por municipio) | Si |
| Recargas Telefonicas | Telcel, AT&T, Movistar, Unefon | No (monto libre) |
| SAT | Impuestos federales | Si (linea de captura) |
| IMSS | Cuotas patronales | Si |
| INFONAVIT | Creditos hipotecarios | Si |
| Peajes y Casetas | CAPUFE, TAG, Pase | No (monto fijo) |
| Seguros | Diversos | Si |
| Colegiaturas | Universidades, escuelas | Si |

### 4.3 Estructura de un Proveedor de Servicio (Biller)

```json
{
  "biller_id": "biller-cfe-domestico",
  "name": "CFE - Servicio Domestico",
  "category": "ELECTRICITY",
  "sub_category": "DOMESTIC",
  "logo_url": "https://cdn.monato.com/billers/cfe.png",
  "required_fields": [
    {
      "field_name": "service_number",
      "label": "Numero de servicio",
      "type": "STRING",
      "pattern": "^[0-9]{12}$",
      "help_text": "12 digitos del recibo CFE"
    }
  ],
  "supports_query": true,
  "supports_partial_payment": false,
  "min_amount": "1.00",
  "max_amount": "99999.99",
  "currency": "MXN",
  "processing_time": "INSTANT",
  "availability": {
    "days": ["MON","TUE","WED","THU","FRI","SAT","SUN"],
    "hours": "00:00-23:59"
  },
  "status": "ACTIVE"
}
```

---

## 5. Flujo Completo de Pago de Servicio

### 5.1 Vista General

```
[1. Catalogo]  ->  [2. Query]  ->  [3. Pay]  ->  [4. Confirm]  ->  [5. Conciliate]
  Que puedo       Cuanto debo     Ejecutar       Webhook/Poll       Verificar
  pagar?          de CFE?         el pago        confirmacion       diario
```

### 5.2 Paso 1: Catalogo (categorias y proveedores)

**Caso de uso**: El usuario abre la seccion de pago de servicios y ve las categorias disponibles.

```
Usuario -> SuperPago API -> Cache Local (DynamoDB)
                              |
                              v (cache miss o expirado)
                         Monato BillPay API
```

**Endpoint SuperPago:**
```
GET /api/v1/organizations/{org_id}/billpay/categories
GET /api/v1/organizations/{org_id}/billpay/providers?category=ELECTRICITY
GET /api/v1/organizations/{org_id}/billpay/providers/{biller_id}
```

**Logica:**
1. Verificar que la org tiene producto BILLPAY activo
2. Buscar en cache local (`modspei_billpay_providers_prod`)
3. Si cache expirado (>24h) o no existe: llamar a Monato, actualizar cache
4. Retornar catalogo filtrado por categoria

**Por que cache local**: El catalogo de proveedores cambia con poca frecuencia (dias/semanas). Llamar a Monato en cada request seria desperdicio. Se sincroniza diariamente via Lambda scheduled.

### 5.3 Paso 2: Query (consultar deuda)

**Caso de uso**: El usuario selecciona CFE, ingresa su numero de servicio, y consulta cuanto debe.

```
Usuario ingresa:
  - biller_id: "biller-cfe-domestico"
  - service_number: "123456789012"
```

**Endpoint SuperPago:**
```
POST /api/v1/organizations/{org_id}/billpay/query
Body: {
  "biller_id": "biller-cfe-domestico",
  "reference_fields": {
    "service_number": "123456789012"
  },
  "account_id": "cuenta_privada_usuario"
}
```

**Secuencia:**

```
1. Validar org tiene BILLPAY activo
2. Validar biller_id existe en catalogo local
3. Validar reference_fields cumplen con required_fields del biller
4. Validar account_id pertenece a la org y esta ACTIVE

5. Llamar a Monato BillPay:
   POST /billpay/query
   Body: {
     "provider_id": "biller-cfe-domestico",
     "reference": "123456789012",
     "external_id": "{idempotency_key}"
   }

6. Monato responde:
   {
     "query_id": "qry-abc-123",
     "provider_id": "biller-cfe-domestico",
     "reference": "123456789012",
     "customer_name": "JUAN PEREZ GARCIA",
     "balances": [
       {
         "balance_id": "bal-001",
         "concept": "Periodo Ene-Feb 2026",
         "amount": "850.00",
         "due_date": "2026-02-28",
         "is_overdue": false
       },
       {
         "balance_id": "bal-002",
         "concept": "Periodo Nov-Dic 2025 (vencido)",
         "amount": "720.00",
         "due_date": "2025-12-31",
         "is_overdue": true
       }
     ],
     "total_amount": "1570.00",
     "min_payment": "850.00",
     "supports_partial": false,
     "query_expires_at": "2026-02-14T12:30:00Z"
   }

7. Calcular fee de SuperPago:
   fee = max(min(amount * 0.005 + 3.50, 50.00), 3.50)
   iva = fee * 0.16

8. Guardar query en modspei_billpay_payments_prod con status QUERIED

9. Retornar al usuario:
   {
     "query_id": "qry-abc-123",
     "biller_name": "CFE - Servicio Domestico",
     "customer_name": "JUAN PEREZ GARCIA",
     "balances": [...],
     "total_amount": "850.00",
     "fee": "7.75",
     "iva_on_fee": "1.24",
     "total_to_charge": "859.00",
     "query_expires_at": "2026-02-14T12:30:00Z",
     "payment_id": "pay-xxx-pending"
   }
```

**Nota sobre el fee calculado (ejemplo con monto $850):**
```
fee_bruto = $850 * 0.5% + $3.50 = $4.25 + $3.50 = $7.75
fee_bruto esta entre min($3.50) y max($50.00) -> $7.75
iva = $7.75 * 16% = $1.24
total_fee = $7.75 + $1.24 = $8.99
total_cobro = $850.00 + $8.99 = $858.99 (redondeado a $859.00)
```

### 5.4 Paso 3: Pay (ejecutar pago)

**Caso de uso**: El usuario confirma el pago. Se debita su cuenta y se envia a Monato.

```
POST /api/v1/organizations/{org_id}/billpay/pay
Body: {
  "payment_id": "pay-xxx-pending",
  "query_id": "qry-abc-123",
  "balance_id": "bal-001",
  "amount": "850.00",
  "account_id": "cuenta_privada_usuario",
  "idempotency_key": "bp-boxito-cfe-123456-20260214-001",
  "confirmed_by": "user_id"
}
```

**Secuencia:**

```
FASE 1 - Reservar fondos (atomica, TransactWriteItems):
=======================================================

1. Verificar idempotencia (IdempotencyIndex)
2. Verificar query no ha expirado
3. Calcular montos:
   - amount = $850.00
   - fee_sp = $7.75 (comision SuperPago sin IVA)
   - iva_fee = $1.24 (IVA sobre comision)
   - total_fee = $8.99
   - total_debit = $858.99

4. TransactWriteItems FASE 1:
   a) Crear operacion BILLPAY (status: PENDING)
   b) Hold en cuenta_privada por $858.99
   c) Hold en concentradora_billpay por $858.99
   d) Actualizar payment record a status: PROCESSING

5. Si TransactWriteItems falla por saldo insuficiente:
   -> Retornar error INSUFFICIENT_BALANCE
   -> No se llama a Monato

FASE 2 - Enviar a Monato:
==========================

6. Actualizar operacion a PROCESSING
7. Llamar a Monato BillPay:
   POST /billpay/pay
   Body: {
     "query_id": "qry-abc-123",
     "balance_id": "bal-001",
     "amount": "850.00",
     "external_id": "bp-boxito-cfe-123456-20260214-001"
   }

8. Monato responde con estado inicial:
   {
     "transaction_id": "monato-tx-789",
     "status": "PROCESSING",
     "estimated_completion": "2026-02-14T10:05:00Z"
   }

9. Guardar monato_transaction_id en la operacion

FASE 3 - Confirmacion (webhook o polling):
==========================================

10. Esperar webhook de Monato:
    POST /webhook/billpay/monato/
    Body: {
      "event": "payment.completed",
      "transaction_id": "monato-tx-789",
      "external_id": "bp-boxito-cfe-123456-20260214-001",
      "status": "COMPLETED",
      "authorization_code": "AUTH-CFE-456",
      "completed_at": "2026-02-14T10:04:30Z"
    }

11. Si COMPLETED: TransactWriteItems FASE 3:
    a) Operacion -> COMPLETED
    b) Crear TXN-1: DECREMENT concentradora_billpay -$858.99
    c) Crear TXN-2: DECREMENT cuenta_privada -$858.99
    d) Crear TXN-3: INCREMENT reservada_comisiones_billpay_sp +$7.75
    e) Crear TXN-4: INCREMENT reservada_iva_sp +$1.24
    f) Liberar holds y actualizar balances de todas las cuentas
    g) Actualizar payment record a status: COMPLETED

12. Si FAILED: TransactWriteItems FASE 3 (rollback):
    a) Operacion -> FAILED
    b) Liberar holds sin decrementar balances
    c) Actualizar payment record a status: FAILED
    d) Notificar al usuario
```

### 5.5 Paso 4: Confirmacion y Comprobante

Despues del webhook COMPLETED:

```
1. Generar comprobante digital:
   {
     "receipt_id": "RCP-20260214-001",
     "biller": "CFE - Servicio Domestico",
     "reference": "123456789012",
     "customer_name": "JUAN PEREZ GARCIA",
     "concept": "Periodo Ene-Feb 2026",
     "amount": "$850.00",
     "fee": "$7.75",
     "iva": "$1.24",
     "total_charged": "$858.99",
     "authorization_code": "AUTH-CFE-456",
     "paid_at": "2026-02-14T10:04:30Z",
     "operation_id": "op-xxx"
   }

2. Notificar al usuario:
   - Push notification en la app
   - Email con comprobante PDF
   - WhatsApp (si tiene agente IA activo)

3. Comprobante disponible via API:
   GET /api/v1/organizations/{org_id}/billpay/payments/{payment_id}/receipt
```

### 5.6 Paso 5: Conciliacion (ver seccion 7)

---

## 6. Operacion BILLPAY - Bloques de Transacciones

### 6.1 Composicion Detallada con Separacion de IVA

La operacion BILLPAY en `ARCHITECTURE_OPERATIONS_TRANSACTIONS.md` seccion 6.11 define 3 transacciones. Este documento expande a 4 para separar el IVA correctamente:

```
Operacion: BILLPAY
  operation_type: BILLPAY
  status: CREATED -> PENDING -> PROCESSING -> COMPLETED
  amount: $850.00 (monto del servicio)
  fee_amount: $8.99 (comision SP + IVA)
  total_amount: $858.99
  metadata: {
    "biller_id": "biller-cfe-domestico",
    "biller_name": "CFE - Servicio Domestico",
    "reference": "123456789012",
    "customer_name": "JUAN PEREZ GARCIA",
    "balance_id": "bal-001",
    "concept": "Periodo Ene-Feb 2026",
    "query_id": "qry-abc-123",
    "payment_id": "pay-xxx",
    "monato_transaction_id": "monato-tx-789",
    "authorization_code": "AUTH-CFE-456",
    "fee_breakdown": {
      "fee_base": "7.75",
      "iva_on_fee": "1.24",
      "total_fee": "8.99"
    }
  }

  TXN-1: DECREMENT concentradora_billpay (org_boxito)
    amount: $858.99
    description: "Pago de servicio CFE ref:123456789012 - concentradora"
    balance_before: $50,000.00
    balance_after: $49,141.01

  TXN-2: DECREMENT cuenta_privada (org_boxito)
    amount: $858.99
    description: "Pago de servicio CFE ref:123456789012"
    balance_before: $5,000.00
    balance_after: $4,141.01

  TXN-3: INCREMENT reservada_comisiones_billpay (org_superpago)
    amount: $7.75
    description: "Comision BillPay - CFE ref:123456789012"
    balance_before: $10,000.00
    balance_after: $10,007.75

  TXN-4: INCREMENT reservada_iva (org_superpago)
    amount: $1.24
    description: "IVA sobre comision BillPay - CFE ref:123456789012"
    balance_before: $1,600.00
    balance_after: $1,601.24
```

### 6.2 Validacion de Integridad

```
SUM(DECREMENT) = $858.99 + $858.99 = $1,717.98
SUM(INCREMENT) = $7.75 + $1.24 = $8.99

Diferencia (neto que sale al mundo externo) = $1,717.98 - $8.99 = $1,708.99

Desglose del neto:
  - $850.00 x 2 cuentas = $1,700.00 (pago al biller, sale del sistema via Monato)
  - $8.99 x 2 cuentas = $17.98 (fee, se queda en el sistema)
  - $17.98 - $8.99 (INCREMENT) = $8.99 (fee neto que sale de cuenta_privada+concentradora)

Verificacion: la cuenta del usuario baja $858.99.
  De eso: $850.00 va al biller, $7.75 a comisiones SP, $1.24 a IVA SP.
  $850.00 + $7.75 + $1.24 = $858.99. Cuadra.
```

### 6.3 Flujo de Fondeo BillPay (como llega el dinero a Monato)

El pago al biller NO sale directamente de la cuenta del usuario a CFE. El flujo real es:

```
1. SuperPago pre-fondea a Monato BillPay:
   - Periodicamente (diario o cuando el saldo baja de umbral)
   - SuperPago transfiere fondos a la cuenta de deposito en Monato
   - Esto es una operacion INTERNAL: concentradora_billpay_sp -> deposito Monato

2. Cuando un usuario paga CFE:
   - La cuenta del usuario baja $858.99
   - La concentradora BillPay del cliente baja $858.99
   - Monato ejecuta el pago con fondos pre-depositados
   - Las comisiones van a cuentas reservadas de SP

3. Reconciliacion diaria:
   - SuperPago verifica que fondos consumidos por Monato == pagos ejecutados
   - Si el saldo en Monato baja de umbral -> alertar para re-fondear
```

**Operacion de Fondeo (pre-deposito a Monato):**

```
Operacion: BILLPAY_FUND (nuevo tipo)
  operation_type: BILLPAY_FUND
  status: COMPLETED (instantanea internamente, luego SPEI a Monato)
  amount: $100,000.00
  description: "Fondeo de pool BillPay a Monato"

  TXN-1: DECREMENT concentradora_billpay_sp
    amount: $100,000.00

  TXN-2: INCREMENT reservada_fondeo_billpay_sp (o se refleja como saldo en Monato)
    amount: $100,000.00
```

**Nuevo OperationType para el enum existente:**
```
BILLPAY_FUND    - Fondeo de pool BillPay hacia proveedor (Monato)
BILLPAY_REFUND  - Devolucion de un pago de servicio fallido
```

### 6.4 Maquina de Estados BILLPAY (expansion)

```
BILLPAY:
  CREATED --> PENDING --> PROCESSING --> COMPLETED
  CREATED --> PENDING --> PROCESSING --> FAILED
  CREATED --> PENDING --> CANCELLED (usuario cancela antes de enviar a Monato)
  COMPLETED --> REVERSED (pago aplicado pero biller rechaza post-facto, raro)

BILLPAY_FUND:
  CREATED --> PROCESSING --> COMPLETED (transferencia a Monato confirmada)
  CREATED --> PROCESSING --> FAILED

BILLPAY_REFUND:
  CREATED --> COMPLETED (instantaneo, credito a cuenta del usuario)
```

---

## 7. Conciliacion BillPay

### 7.1 Objetivo

Verificar que CADA pago ejecutado por SuperPago fue efectivamente aplicado por el proveedor de servicios (biller) a traves de Monato. Detectar discrepancias y resolverlas.

### 7.2 Tipos de Discrepancia

| Tipo | Descripcion | Accion |
|------|-------------|--------|
| `MISSING_AT_PROVIDER` | SuperPago marca COMPLETED pero Monato no tiene registro | Investigar, posible REVERSAL |
| `MISSING_LOCALLY` | Monato reporta un pago que SuperPago no tiene | Error de webhook, crear registro |
| `AMOUNT_MISMATCH` | Montos difieren entre SuperPago y Monato | Investigar, posible cobro parcial |
| `STATUS_MISMATCH` | SuperPago dice COMPLETED, Monato dice FAILED (o viceversa) | Corregir estado, posible REFUND |
| `DUPLICATE_PAYMENT` | Mismo pago registrado 2 veces en SuperPago | Investigar idempotencia |
| `PENDING_TOO_LONG` | Pago en PROCESSING por mas de X horas | Consultar Monato, resolver |

### 7.3 Lambda de Conciliacion - Flujo

```
Trigger: EventBridge Rule (CloudWatch Events)
  - Diario a las 02:00 UTC (20:00 CST) -> conciliacion completa del dia anterior
  - Cada hora -> conciliacion de pagos PROCESSING pendientes

Lambda: billpay-conciliation

Flujo:
  1. Obtener fecha/rango a conciliar
  2. Query pagos internos:
     - modspei_operations_prod: operation_type = BILLPAY, fecha = rango
     - modspei_billpay_payments_prod: status IN (COMPLETED, PROCESSING, FAILED)
  3. Query pagos en Monato:
     - GET /billpay/conciliation?date=YYYY-MM-DD
     - Retorna: lista de pagos con {monato_tx_id, external_id, amount, status}
  4. Cruzar:
     - Para cada pago interno, buscar su match en Monato por monato_transaction_id
     - Para cada pago en Monato, buscar su match interno por external_id
  5. Clasificar discrepancias
  6. Generar reporte de conciliacion
  7. Acciones automaticas:
     - PENDING_TOO_LONG: re-consultar status en Monato, actualizar si cambio
     - STATUS_MISMATCH (interno=PROCESSING, monato=COMPLETED): completar operacion
     - STATUS_MISMATCH (interno=COMPLETED, monato=FAILED): generar BILLPAY_REFUND
  8. Acciones manuales (crear alerta):
     - MISSING_AT_PROVIDER: alerta CRITICAL
     - AMOUNT_MISMATCH: alerta WARNING
     - DUPLICATE_PAYMENT: alerta CRITICAL
  9. Guardar reporte en modspei_billpay_conciliation_prod
```

### 7.4 Tabla de Conciliacion

**Tabla: `modspei_billpay_conciliation_prod`**

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| **PK** | `CONCILIATION#{date}` | Partition key: fecha de conciliacion |
| **SK** | `ORG#{org_id}#{run_id}` | Sort key: org + ejecucion |
| `run_id` | `str (UUID)` | ID unico de esta ejecucion |
| `date` | `str (YYYY-MM-DD)` | Fecha conciliada |
| `sp_organization_id` | `str` | Organizacion conciliada (o "ALL") |
| `total_payments_internal` | `int` | Pagos encontrados en SuperPago |
| `total_payments_provider` | `int` | Pagos encontrados en Monato |
| `total_amount_internal` | `str (Decimal)` | Monto total interno |
| `total_amount_provider` | `str (Decimal)` | Monto total en Monato |
| `matched` | `int` | Pagos que coinciden |
| `discrepancies` | `list[dict]` | Lista de discrepancias encontradas |
| `auto_resolved` | `int` | Discrepancias resueltas automaticamente |
| `pending_review` | `int` | Discrepancias pendientes de revision manual |
| `status` | `str` | CLEAN (0 discrepancias), RESOLVED, PENDING_REVIEW |
| `started_at` | `str (ISO8601)` | Inicio de la ejecucion |
| `completed_at` | `str (ISO8601)` | Fin de la ejecucion |

### 7.5 Estructura de Discrepancia

```json
{
  "discrepancy_id": "disc-001",
  "type": "STATUS_MISMATCH",
  "severity": "WARNING",
  "payment_id": "pay-xxx",
  "operation_id": "op-xxx",
  "monato_transaction_id": "monato-tx-789",
  "internal_status": "PROCESSING",
  "provider_status": "COMPLETED",
  "internal_amount": "850.00",
  "provider_amount": "850.00",
  "auto_action_taken": "COMPLETE_OPERATION",
  "resolved": true,
  "resolved_at": "2026-02-14T02:05:30Z",
  "notes": "Webhook de confirmacion no llego, resuelto por conciliacion"
}
```

### 7.6 Dashboard de Conciliacion

Metricas clave visibles para Admin SuperPago:

```
+----------------------------------+
| Conciliacion BillPay - 2026-02-13|
+----------------------------------+
| Pagos ejecutados:    1,247       |
| Monto total:         $847,320.50 |
| Coincidentes:        1,241 (99.5%)|
| Discrepancias:       6           |
|   Auto-resueltas:    4           |
|   Pendientes review: 2           |
| Estado: PENDING_REVIEW           |
+----------------------------------+
```

---

## 8. Modelo DynamoDB Expandido

### 8.1 Tabla: `modspei_billpay_payments_prod`

Registro detallado de cada pago de servicio. Complementa la operacion en `modspei_operations_prod` con datos especificos del biller.

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| **PK** | `sp_organization_id` | Partition key |
| **SK** | `BPAY#{payment_id}` | Sort key |
| `Id` | `str (UUID)` | ID canonico del pago |
| `operation_id` | `str (UUID)` | FK a modspei_operations_prod |
| `sp_organization_id` | `str` | Organizacion que ejecuta |
| `account_id` | `str (UUID)` | Cuenta del usuario que paga |
| `biller_id` | `str` | ID del proveedor de servicio |
| `biller_name` | `str` | Nombre legible del biller |
| `category` | `str` | Categoria (ELECTRICITY, WATER, etc.) |
| `reference_fields` | `dict` | Campos de referencia enviados `{"service_number": "123..."}` |
| `customer_name` | `str` | Nombre del titular segun biller |
| `query_id` | `str` | ID del query previo en Monato |
| `balance_id` | `str` | ID del balance/deuda seleccionado |
| `concept` | `str` | Concepto del pago (periodo, etc.) |
| `amount` | `str (Decimal)` | Monto del servicio |
| `fee_base` | `str (Decimal)` | Comision sin IVA |
| `fee_iva` | `str (Decimal)` | IVA sobre comision |
| `fee_total` | `str (Decimal)` | Comision total (base + IVA) |
| `total_charged` | `str (Decimal)` | Total cobrado al usuario (amount + fee_total) |
| `currency` | `str` | MXN |
| `status` | `str (enum)` | QUERIED, PENDING, PROCESSING, COMPLETED, FAILED, REFUNDED |
| `monato_query_id` | `str` | ID del query en Monato |
| `monato_transaction_id` | `str or None` | ID de la transaccion en Monato |
| `authorization_code` | `str or None` | Codigo de autorizacion del biller |
| `idempotency_key` | `str` | Clave de idempotencia |
| `initiated_by` | `str` | User ID o "AGENT_IA" |
| `channel` | `str` | APP, WHATSAPP, API |
| `error_code` | `str or None` | Codigo de error si fallo |
| `error_message` | `str or None` | Mensaje de error |
| `query_expires_at` | `str (ISO8601)` | Expiracion del query |
| `created_at` | `str (ISO8601)` | Timestamp de creacion |
| `updated_at` | `str (ISO8601)` | Ultima actualizacion |
| `completed_at` | `str or None` | Timestamp de completado |
| `receipt_url` | `str or None` | URL del comprobante PDF |

**GSIs:**

**GSI-1: BillerPaymentsIndex** - Pagos por biller y fecha
```
GSIPK: biller_id
GSISK: created_at
Projection: Id, sp_organization_id, amount, status, reference_fields
```
Uso: "Cuantos pagos de CFE hicimos hoy?"

**GSI-2: StatusPaymentsIndex** - Pagos por org y status
```
GSIPK: sp_organization_id
GSISK: status#created_at
Projection: ALL
```
Uso: "Dame todos los pagos PROCESSING de Boxito"

**GSI-3: MonatoTxIndex** - Buscar por ID de Monato (para webhooks)
```
GSIPK: monato_transaction_id
GSISK: sp_organization_id
Projection: ALL
```
Uso: "Webhook de Monato con tx_id X, a que pago corresponde?"

**GSI-4: AccountPaymentsIndex** - Pagos por cuenta del usuario
```
GSIPK: account_id
GSISK: created_at
Projection: Id, biller_name, amount, status, created_at
```
Uso: "Historial de pagos de servicios de la cuenta de Juan"

**GSI-5: IdempotencyBPIndex** - Verificar duplicados
```
GSIPK: idempotency_key
GSISK: sp_organization_id
Projection: KEYS_ONLY + status
```

### 8.2 Tabla: `modspei_billpay_providers_prod`

Cache local del catalogo de proveedores de servicio de Monato.

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| **PK** | `CATEGORY#{category}` | Partition key: categoria |
| **SK** | `BILLER#{biller_id}` | Sort key: ID del proveedor |
| `biller_id` | `str` | ID unico del proveedor |
| `name` | `str` | Nombre legible |
| `category` | `str` | ELECTRICITY, WATER, GAS, PHONE, INTERNET, TV, RECHARGE, TAX, etc. |
| `sub_category` | `str or None` | Sub-categoria (DOMESTIC, COMMERCIAL, etc.) |
| `logo_url` | `str` | URL del logo |
| `required_fields` | `list[dict]` | Campos requeridos para query/pago |
| `supports_query` | `bool` | Soporta consulta de deuda previa |
| `supports_partial_payment` | `bool` | Soporta pago parcial |
| `min_amount` | `str (Decimal)` | Monto minimo |
| `max_amount` | `str (Decimal)` | Monto maximo |
| `currency` | `str` | MXN |
| `processing_time` | `str` | INSTANT, SAME_DAY, NEXT_DAY |
| `availability` | `dict` | Dias y horarios disponibles |
| `status` | `str` | ACTIVE, INACTIVE, MAINTENANCE |
| `popularity_rank` | `int` | Ranking de popularidad (para ordenar en UI) |
| `synced_at` | `str (ISO8601)` | Ultima sincronizacion con Monato |
| `ttl` | `int` | TTL en epoch seconds (auto-expire en 48h) |

**GSI-1: BillerNameIndex** - Buscar por nombre (barra de busqueda)
```
GSIPK: name_lowercase (primera palabra en minusculas)
GSISK: BILLER#{biller_id}
Projection: biller_id, name, category, logo_url, status
```

**GSI-2: AllBillersIndex** - Listar todos los billers activos
```
GSIPK: status
GSISK: popularity_rank
Projection: biller_id, name, category, logo_url
```

### 8.3 Expansion de `modspei_operations_prod`

No se crea nueva tabla. Se usan los mismos campos con nuevos valores de `operation_type`:

```
operation_type = "BILLPAY"
operation_type = "BILLPAY_FUND"
operation_type = "BILLPAY_REFUND"
```

El campo `metadata` de la operacion BILLPAY contiene los datos del biller y referencia (ver seccion 6.1).

### 8.4 Expansion de `modspei_accounts_prod`

No se crea nueva tabla. Se agregan nuevos valores al enum `account_type` (ver seccion 3.4).

---

## 9. Strategy Pattern para BillPay

### 9.1 Separacion de Concerns: SPEIProvider vs BillPayProvider

El Strategy Pattern existente (`SPEIProvider` en EP-SP-002) es para operaciones SPEI. BillPay tiene un contrato diferente, por lo que se crea una interface separada.

```
strategies/
├── spei/
│   ├── base_spei_provider.py         # Interface SPEIProvider (ya disenada)
│   ├── monato_fincore_driver.py      # Monato Fincore para SPEI
│   └── stp_driver.py                 # (futuro) STP para SPEI
│
├── billpay/
│   ├── base_billpay_provider.py      # Interface BillPayProvider (NUEVO)
│   ├── monato_billpay_driver.py      # Monato BillPay (NUEVO)
│   └── siprel_billpay_driver.py      # (futuro) SIPREL como alternativa
│
├── operations/
│   ├── base_operation_strategy.py    # (ya disenada)
│   ├── billpay_strategy.py           # (ya disenada, usa BillPayProvider)
│   ├── billpay_fund_strategy.py      # (NUEVO)
│   ├── billpay_refund_strategy.py    # (NUEVO)
│   └── ... (demas strategies existentes)
│
└── factory.py                        # ProviderFactory (expande para BillPay)
```

### 9.2 Interface BillPayProvider

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


# --- Request/Response Dataclasses ---

@dataclass
class BillerCategory:
    """Categoria de servicio."""
    category_id: str
    name: str
    icon_url: Optional[str] = None
    biller_count: int = 0


@dataclass
class BillerInfo:
    """Informacion de un proveedor de servicio."""
    biller_id: str
    name: str
    category: str
    required_fields: list[dict]
    supports_query: bool
    min_amount: Decimal
    max_amount: Decimal
    status: str


@dataclass
class BillerQueryRequest:
    """Request para consultar deuda."""
    biller_id: str
    reference_fields: dict
    external_id: str  # idempotency key


@dataclass
class BillerBalance:
    """Un balance/deuda individual."""
    balance_id: str
    concept: str
    amount: Decimal
    due_date: Optional[str] = None
    is_overdue: bool = False


@dataclass
class BillerQueryResult:
    """Resultado de consulta de deuda."""
    query_id: str
    biller_id: str
    customer_name: str
    balances: list[BillerBalance]
    total_amount: Decimal
    min_payment: Optional[Decimal] = None
    supports_partial: bool = False
    expires_at: Optional[str] = None
    raw_response: Optional[dict] = None


@dataclass
class BillPaymentRequest:
    """Request para ejecutar pago."""
    query_id: str
    balance_id: str
    amount: Decimal
    external_id: str  # idempotency key
    metadata: Optional[dict] = None


@dataclass
class BillPaymentResult:
    """Resultado de pago ejecutado."""
    provider_transaction_id: str
    status: str  # PROCESSING, COMPLETED, FAILED
    authorization_code: Optional[str] = None
    estimated_completion: Optional[str] = None
    raw_response: Optional[dict] = None


@dataclass
class BillPaymentStatus:
    """Status de un pago consultado."""
    provider_transaction_id: str
    external_id: str
    status: str
    authorization_code: Optional[str] = None
    completed_at: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class ConciliationReport:
    """Reporte de conciliacion del proveedor."""
    date: str
    total_transactions: int
    total_amount: Decimal
    transactions: list[dict]  # Lista de {tx_id, external_id, amount, status}


# --- Interface ---

class BillPayProvider(ABC):
    """
    Interface abstracta para proveedores de pago de servicios.
    Cada proveedor (Monato, SIPREL, etc.) implementa esta interface.
    """

    @abstractmethod
    def authenticate(self) -> str:
        """Obtener token de autenticacion. Retorna token JWT."""
        ...

    @abstractmethod
    def get_categories(self) -> list[BillerCategory]:
        """Obtener catalogo de categorias de servicio."""
        ...

    @abstractmethod
    def get_billers(self, category: Optional[str] = None) -> list[BillerInfo]:
        """Obtener proveedores de servicio, opcionalmente filtrados por categoria."""
        ...

    @abstractmethod
    def get_biller_detail(self, biller_id: str) -> BillerInfo:
        """Obtener detalle de un proveedor especifico."""
        ...

    @abstractmethod
    def query_balance(self, request: BillerQueryRequest) -> BillerQueryResult:
        """Consultar deuda/saldo de un servicio. Retorna balances pendientes."""
        ...

    @abstractmethod
    def execute_payment(self, request: BillPaymentRequest) -> BillPaymentResult:
        """Ejecutar pago de servicio. Retorna resultado inicial (puede ser async)."""
        ...

    @abstractmethod
    def get_payment_status(self, provider_transaction_id: str) -> BillPaymentStatus:
        """Consultar status de un pago ejecutado."""
        ...

    @abstractmethod
    def get_conciliation_report(
        self, date: str, page: int = 1, page_size: int = 100
    ) -> ConciliationReport:
        """Obtener reporte de conciliacion para una fecha."""
        ...

    @abstractmethod
    def register_webhook(self, url: str, events: list[str]) -> str:
        """Registrar URL de webhook. Retorna webhook_id."""
        ...
```

### 9.3 Factory Expandida

```python
class ProviderFactory:
    """Factory que provee implementaciones de SPEIProvider y BillPayProvider."""

    _spei_registry: dict[str, type[SPEIProvider]] = {}
    _billpay_registry: dict[str, type[BillPayProvider]] = {}

    @classmethod
    def register_spei(cls, name: str, provider_class: type[SPEIProvider]):
        cls._spei_registry[name] = provider_class

    @classmethod
    def register_billpay(cls, name: str, provider_class: type[BillPayProvider]):
        cls._billpay_registry[name] = provider_class

    @classmethod
    def get_spei_provider(cls, name: str) -> SPEIProvider:
        if name not in cls._spei_registry:
            raise ValueError(f"SPEI provider '{name}' no registrado")
        return cls._spei_registry[name]()

    @classmethod
    def get_billpay_provider(cls, name: str) -> BillPayProvider:
        if name not in cls._billpay_registry:
            raise ValueError(f"BillPay provider '{name}' no registrado")
        return cls._billpay_registry[name]()


# Registro al iniciar la app
ProviderFactory.register_spei("monato_fincore", MonatoFincoreDriver)
ProviderFactory.register_billpay("monato_billpay", MonatoBillPayDriver)
# Futuro:
# ProviderFactory.register_billpay("siprel", SIPRELBillPayDriver)
```

### 9.4 MonatoBillPayDriver (implementacion)

```python
class MonatoBillPayDriver(BillPayProvider):
    """Implementacion de BillPayProvider para Monato BillPay."""

    def __init__(self):
        self.base_url = os.getenv("MONATO_BILLPAY_BASE_URL")
        self.client_id = os.getenv("MONATO_BILLPAY_CLIENT_ID")
        self.client_secret = os.getenv("MONATO_BILLPAY_CLIENT_SECRET")
        self._token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

    def authenticate(self) -> str:
        """POST /auth/token con client credentials."""
        ...

    def get_categories(self) -> list[BillerCategory]:
        """GET /billpay/categories"""
        ...

    def get_billers(self, category=None) -> list[BillerInfo]:
        """GET /billpay/providers?category={category}"""
        ...

    def get_biller_detail(self, biller_id) -> BillerInfo:
        """GET /billpay/providers/{biller_id}"""
        ...

    def query_balance(self, request) -> BillerQueryResult:
        """POST /billpay/query"""
        ...

    def execute_payment(self, request) -> BillPaymentResult:
        """POST /billpay/pay"""
        ...

    def get_payment_status(self, provider_transaction_id) -> BillPaymentStatus:
        """GET /billpay/transactions/{tx_id}"""
        ...

    def get_conciliation_report(self, date, page=1, page_size=100) -> ConciliationReport:
        """GET /billpay/conciliation?date={date}&page={page}"""
        ...

    def register_webhook(self, url, events) -> str:
        """POST /billpay/webhooks"""
        ...
```

### 9.5 Futuro: SIPRELBillPayDriver

SIPREL es otro agregador de pago de servicios comun en Mexico. La interface permite agregar este proveedor sin cambiar la logica de negocio:

```python
class SIPRELBillPayDriver(BillPayProvider):
    """Implementacion alternativa usando SIPREL."""
    # Misma interface, diferente implementacion HTTP
    ...
```

Incluso se podria usar un patron Composite donde se consultan multiples proveedores y se selecciona el mas barato o el que tenga mejor cobertura para un biller especifico.

---

## 10. Estructura de Cuentas por Producto

### 10.1 Diagrama Completo de Cuentas (Ejemplo con 2 clientes)

```
SUPERPAGO (org_superpago)
|
+-- Concentradora Master SPEI         balance: $2,500,000.00
+-- Concentradora Master BillPay      balance: $500,000.00
+-- Revenue SPEI                      balance: $45,320.00
+-- Revenue BillPay                   balance: $12,870.50
+-- Revenue Openpay                   balance: $8,210.00
+-- IVA Plataforma                    balance: $10,624.08
+-- Transit Cash Global               balance: $180,000.00


BOXITO (org_boxito) - Productos: SPEI + BILLPAY
|
+-- [SPEI]
|   +-- Concentradora SPEI            balance: $150,000.00
|   +-- Reservada Comisiones SPEI     balance: $0.00 (se mueve a Revenue SP)
|   +-- CLABE Principal               balance: $85,000.00
|   +-- CLABE Nomina                  balance: $40,000.00
|   +-- Dispersion Proveedores        balance: $25,000.00
|
+-- [BILLPAY]
|   +-- Concentradora BillPay         balance: $30,000.00
|   +-- Reservada Comisiones BillPay  balance: $0.00
|   +-- Reservada Fondeo BillPay      balance: $20,000.00
|
+-- [GLOBAL]
    +-- Reservada IVA                  balance: $0.00
    +-- Reservada Retenciones          balance: $0.00


TIENDA_MARIA (org_maria) - Productos: SPEI + BILLPAY + CASH
|
+-- [SPEI]
|   +-- Concentradora SPEI            balance: $25,000.00
|   +-- CLABE Principal               balance: $15,000.00
|
+-- [BILLPAY]
|   +-- Concentradora BillPay         balance: $8,000.00
|   +-- Reservada Fondeo BillPay      balance: $5,000.00
|
+-- [CASH]
|   +-- Transit Cash Sucursal Centro  balance: $12,000.00
|   +-- Transit Cash Sucursal Norte   balance: $8,500.00
|
+-- [GLOBAL]
    +-- Reservada IVA                  balance: $0.00
```

### 10.2 Flujo de Dinero en BillPay (diagrama de flujo de fondos)

```
FONDEO INICIAL:
===============
SuperPago fondea a Monato BillPay:
  Concentradora Master BillPay (SP)  --SPEI-->  Monato BillPay Account
  (-$100,000)                                    (+$100,000)

PAGO DE SERVICIO (usuario de Boxito paga CFE $850):
====================================================

1. Cuenta usuario (Boxito)     -$858.99   (monto + fee + IVA)
2. Concentradora BP (Boxito)   -$858.99   (reflejo contable)
3. Revenue BillPay (SP)        +$7.75     (comision SP)
4. IVA Plataforma (SP)         +$1.24     (IVA de la comision)
5. Monato ejecuta pago a CFE   -$850.00   (del pool pre-fondeado)

Neto en Monato: pool baja $850
Neto en SuperPago: comision +$8.99
Neto para usuario: -$858.99 (pago su recibo + fee)
Neto para CFE: +$850 (recibio su pago)
```

---

## 11. API Endpoints

### 11.1 Onboarding (covacha-payment o covacha-core)

```
POST   /api/v1/organizations/{org_id}/products
       Body: { "products": ["SPEI", "BILLPAY"] }
       Provisiona cuentas y activa productos

GET    /api/v1/organizations/{org_id}/products
       Lista productos activos con sus cuentas

GET    /api/v1/organizations/{org_id}/products/{product_type}
       Detalle de un producto (cuentas, pricing, limites)

PATCH  /api/v1/organizations/{org_id}/products/{product_type}
       Actualizar pricing, limites, o suspender

DELETE /api/v1/organizations/{org_id}/products/{product_type}
       Desactivar producto (soft-delete, cuentas se congelan)
```

### 11.2 BillPay - Catalogo (covacha-payment)

```
GET    /api/v1/organizations/{org_id}/billpay/categories
       Lista categorias de servicios

GET    /api/v1/organizations/{org_id}/billpay/providers
       Query params: ?category=ELECTRICITY&search=CFE
       Lista proveedores de servicio

GET    /api/v1/organizations/{org_id}/billpay/providers/{biller_id}
       Detalle: campos requeridos, montos min/max, horarios
```

### 11.3 BillPay - Operaciones (covacha-payment)

```
POST   /api/v1/organizations/{org_id}/billpay/query
       Body: { biller_id, reference_fields, account_id }
       Consulta deuda/saldo

POST   /api/v1/organizations/{org_id}/billpay/pay
       Body: { payment_id, query_id, balance_id, amount, account_id, idempotency_key }
       Ejecuta pago de servicio

GET    /api/v1/organizations/{org_id}/billpay/payments
       Query params: ?status=COMPLETED&biller_id=cfe&from=2026-02-01&to=2026-02-14
       Lista pagos con filtros y paginacion

GET    /api/v1/organizations/{org_id}/billpay/payments/{payment_id}
       Detalle completo de un pago

GET    /api/v1/organizations/{org_id}/billpay/payments/{payment_id}/receipt
       Comprobante PDF del pago
```

### 11.4 BillPay - Conciliacion (covacha-payment, admin only)

```
GET    /api/v1/admin/billpay/conciliation
       Query params: ?date=2026-02-13&org_id=optional
       Reporte de conciliacion

GET    /api/v1/admin/billpay/conciliation/{run_id}
       Detalle de una ejecucion de conciliacion

POST   /api/v1/admin/billpay/conciliation/run
       Body: { date, org_id? }
       Ejecutar conciliacion manualmente

PATCH  /api/v1/admin/billpay/conciliation/{run_id}/discrepancies/{disc_id}
       Body: { action: "RESOLVE", notes: "..." }
       Resolver discrepancia manualmente
```

### 11.5 Webhook Handler (covacha-webhook)

```
POST   /api/v1/webhook/billpay/monato/
       Recibe eventos de Monato BillPay:
       - payment.completed
       - payment.failed
       - payment.reversed
       - provider.maintenance (biller en mantenimiento)
```

### 11.6 Headers Requeridos (todos los endpoints)

```
Authorization: Bearer {token}
X-API-KEY: {api_key}
X-Tenant-Id: {tenant}
X-SP-Organization-Id: {org_id}
X-SP-Project-Id: {project_id}
Content-Type: application/json
X-Idempotency-Key: {key}          (solo en POST mutativos)
```

---

## 12. Mapa de Epicas

### 12.1 Epicas BillPay

| ID | Epica | Complejidad | Sprint | Dependencias |
|----|-------|-------------|--------|--------------|
| EP-BP-001 | Onboarding Multi-Producto | L | 1-2 | EP-SP-001 (Account Core Engine) |
| EP-BP-002 | BillPay Provider Strategy Pattern | M | 1-2 | Ninguna (paralela) |
| EP-BP-003 | Catalogo de Proveedores de Servicio | S | 2 | EP-BP-002 |
| EP-BP-004 | Consulta de Deuda (Query) | M | 2-3 | EP-BP-002, EP-BP-003 |
| EP-BP-005 | Ejecucion de Pago (Pay) | XL | 3-4 | EP-BP-001, EP-BP-002, EP-BP-004, EP-SP-003 (Ledger) |
| EP-BP-006 | Webhook Handler BillPay | M | 3-4 | EP-BP-005 |
| EP-BP-007 | Conciliacion BillPay | L | 4-5 | EP-BP-005, EP-BP-006 |
| EP-BP-008 | Frontend BillPay (mf-sp) | L | 3-5 | EP-BP-004, EP-BP-005, EP-SP-007 (scaffold mf-sp) |

### 12.2 Grafo de Dependencias

```
EP-SP-001 (Account Core Engine) ──────────┐
                                          v
EP-BP-001 (Onboarding Multi-Producto) ──> EP-BP-005 (Pay)
                                          ^
EP-BP-002 (Strategy Pattern) ──────────> EP-BP-004 (Query)
         |                                ^
         v                                |
EP-BP-003 (Catalogo) ────────────────────┘
                                          |
EP-SP-003 (Ledger) ──────────────────────>|
                                          |
                                          v
                                    EP-BP-006 (Webhook)
                                          |
                                          v
                                    EP-BP-007 (Conciliacion)

EP-SP-007 (mf-sp scaffold) ──> EP-BP-008 (Frontend BillPay)
```

### 12.3 Epicas Detalladas

#### EP-BP-001: Onboarding Multi-Producto

**Descripcion:** Sistema de provisionamiento automatico de cuentas por producto. Cuando un admin asigna productos a una organizacion, se crean las cuentas necesarias, se provisionan en proveedores externos, y se activa el producto.

**User Stories:**
- US-BP-001: Modelo de Producto por Organizacion (tabla `modspei_org_products_prod`)
- US-BP-002: API de asignacion de productos `POST /organizations/{org_id}/products`
- US-BP-003: Provisionamiento automatico de cuentas por producto
- US-BP-004: Provisionamiento en Monato (Fincore + BillPay)
- US-BP-005: Desactivacion de producto (congelar cuentas)

**Criterios de Aceptacion:**
- [ ] Se pueden asignar multiples productos a una organizacion
- [ ] Cada producto genera las cuentas correctas automaticamente
- [ ] Cuentas globales (IVA, retenciones) se crean una sola vez
- [ ] Idempotencia: asignar el mismo producto 2 veces no duplica cuentas
- [ ] Desactivar producto congela sus cuentas sin afectar otros productos
- [ ] Tests >= 98%

**Repositorio:** `covacha-payment`
**Estimacion:** 15 dev-days

---

#### EP-BP-002: BillPay Provider Strategy Pattern

**Descripcion:** Interface `BillPayProvider` y primera implementacion `MonatoBillPayDriver`. Factory expandida para resolver providers de BillPay.

**User Stories:**
- US-BP-006: Interface BillPayProvider con dataclasses
- US-BP-007: MonatoBillPayDriver - autenticacion y catalogo
- US-BP-008: MonatoBillPayDriver - query y payment
- US-BP-009: MonatoBillPayDriver - conciliacion y webhooks
- US-BP-010: Factory expandida y registro de providers

**Criterios de Aceptacion:**
- [ ] Interface completa con type hints y dataclasses
- [ ] MonatoBillPayDriver implementa todos los metodos
- [ ] Autenticacion con refresh automatico de token
- [ ] Retry con backoff exponencial para errores transitorios
- [ ] Idempotency key en todas las operaciones mutativas
- [ ] Logs estructurados sin datos sensibles
- [ ] Tests >= 98% con mocks de API Monato

**Repositorio:** `covacha-payment` (modulo `strategies/billpay/`)
**Estimacion:** 12 dev-days

---

#### EP-BP-003: Catalogo de Proveedores de Servicio

**Descripcion:** Cache local del catalogo de billers. Lambda de sincronizacion diaria. Endpoints de consulta.

**User Stories:**
- US-BP-011: Tabla `modspei_billpay_providers_prod` con TTL
- US-BP-012: Lambda de sincronizacion diaria de catalogo
- US-BP-013: Endpoints de categorias y proveedores

**Criterios de Aceptacion:**
- [ ] Catalogo sincronizado diariamente desde Monato
- [ ] TTL de 48h para auto-limpieza de registros no actualizados
- [ ] Busqueda por categoria, por nombre, por popularidad
- [ ] Si cache frio: consulta en tiempo real a Monato y actualiza
- [ ] Tests >= 98%

**Repositorio:** `covacha-payment`
**Estimacion:** 5 dev-days

---

#### EP-BP-004: Consulta de Deuda (Query)

**Descripcion:** Flujo de consulta de deuda/saldo de un servicio. Valida campos, consulta a Monato, calcula fees, guarda registro.

**User Stories:**
- US-BP-014: Endpoint de query con validacion de campos
- US-BP-015: Calculo de fees con pricing configurable por org
- US-BP-016: Registro de query en `modspei_billpay_payments_prod`

**Criterios de Aceptacion:**
- [ ] Validacion de campos requeridos segun biller
- [ ] Fee calculado correctamente segun pricing de la org
- [ ] IVA separado sobre el fee
- [ ] Query expira segun lo que indique Monato
- [ ] Tests >= 98%

**Repositorio:** `covacha-payment`
**Estimacion:** 8 dev-days

---

#### EP-BP-005: Ejecucion de Pago (Pay)

**Descripcion:** Flujo completo de pago en 3 fases: reservar fondos, enviar a Monato, confirmar. Es el corazon del sistema BillPay.

**User Stories:**
- US-BP-017: FASE 1 - TransactWriteItems para hold de fondos
- US-BP-018: FASE 2 - Envio a Monato BillPay
- US-BP-019: FASE 3 - Confirmacion (TransactWriteItems para completar o revertir)
- US-BP-020: Generacion de comprobante digital
- US-BP-021: Notificaciones post-pago

**Criterios de Aceptacion:**
- [ ] Atomicidad en Fase 1 (hold) y Fase 3 (confirmar/revertir)
- [ ] Idempotencia estricta en todo el flujo
- [ ] Rollback automatico si Monato falla
- [ ] Comprobante digital con datos del biller + autorizacion
- [ ] Notificacion al usuario por los canales configurados
- [ ] Tests >= 98% incluyendo escenarios de fallo

**Repositorio:** `covacha-payment`
**Estimacion:** 20 dev-days

---

#### EP-BP-006: Webhook Handler BillPay

**Descripcion:** Endpoint para recibir webhooks de Monato BillPay. Procesa confirmaciones de pago, fallos, y reversiones.

**User Stories:**
- US-BP-022: Endpoint webhook con validacion de firma
- US-BP-023: Procesamiento de payment.completed
- US-BP-024: Procesamiento de payment.failed y payment.reversed
- US-BP-025: Dead letter queue para webhooks fallidos

**Criterios de Aceptacion:**
- [ ] Response 200 en < 500ms (procesamiento async via SQS)
- [ ] Idempotencia (mismo webhook 2 veces = 1 sola operacion)
- [ ] Validacion de firma/token del webhook
- [ ] Dead letter queue para reintentos
- [ ] Tests >= 98%

**Repositorio:** `covacha-webhook`
**Estimacion:** 10 dev-days

---

#### EP-BP-007: Conciliacion BillPay

**Descripcion:** Lambda de conciliacion diaria. Compara pagos internos vs reporte de Monato. Detecta y resuelve discrepancias.

**User Stories:**
- US-BP-026: Lambda de conciliacion con EventBridge trigger
- US-BP-027: Logica de cruce y clasificacion de discrepancias
- US-BP-028: Auto-resolucion de discrepancias comunes
- US-BP-029: Dashboard de conciliacion (API)
- US-BP-030: Alertas automaticas para discrepancias criticas

**Criterios de Aceptacion:**
- [ ] Ejecucion diaria automatica a las 02:00 UTC
- [ ] Ejecucion manual via API admin
- [ ] Auto-resolucion de STATUS_MISMATCH y PENDING_TOO_LONG
- [ ] Alertas CRITICAL para MISSING_AT_PROVIDER y DUPLICATE_PAYMENT
- [ ] Reporte persistido en `modspei_billpay_conciliation_prod`
- [ ] Tests >= 98%

**Repositorio:** `covacha-payment` (Lambda), `covacha-webhook` (alertas)
**Estimacion:** 12 dev-days

---

#### EP-BP-008: Frontend BillPay (mf-sp)

**Descripcion:** Paginas en mf-sp para pago de servicios: catalogo, consulta, pago, historial, comprobantes, conciliacion (admin).

**User Stories:**
- US-BP-031: Pagina de catalogo de servicios (categorias + proveedores)
- US-BP-032: Flujo de consulta y pago de servicio
- US-BP-033: Historial de pagos con filtros
- US-BP-034: Detalle y comprobante de pago
- US-BP-035: Dashboard de conciliacion (admin only)

**Criterios de Aceptacion:**
- [ ] Catalogo con busqueda y filtro por categoria
- [ ] Wizard: seleccionar biller -> ingresar referencia -> ver deuda -> confirmar pago
- [ ] Feedback en tiempo real del status del pago
- [ ] Historial con paginacion server-side y filtros
- [ ] Comprobante descargable en PDF
- [ ] Dashboard de conciliacion para admin
- [ ] Tests >= 98%

**Repositorio:** `mf-sp`
**Estimacion:** 18 dev-days

---

### 12.4 Resumen de Estimaciones

| Epica | Dev-Days | Sprint |
|-------|----------|--------|
| EP-BP-001: Onboarding Multi-Producto | 15 | 1-2 |
| EP-BP-002: Strategy Pattern BillPay | 12 | 1-2 |
| EP-BP-003: Catalogo Proveedores | 5 | 2 |
| EP-BP-004: Consulta de Deuda | 8 | 2-3 |
| EP-BP-005: Ejecucion de Pago | 20 | 3-4 |
| EP-BP-006: Webhook Handler | 10 | 3-4 |
| EP-BP-007: Conciliacion | 12 | 4-5 |
| EP-BP-008: Frontend mf-sp | 18 | 3-5 |
| **TOTAL** | **100 dev-days** | **~5 sprints** |

---

## 13. Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|------------|
| Monato BillPay API cambia sin aviso | Media | Alto | Adapter Pattern con versioning, tests de contrato |
| Webhook de Monato no llega | Media | Alto | Conciliacion cada hora resuelve automaticamente |
| Double-spending por race condition | Baja | Critico | Optimistic locking + holds + idempotency key |
| Biller rechaza pago post-confirmacion | Baja | Alto | BILLPAY_REFUND automatico, alerta a admin |
| Pool de fondos en Monato se agota | Media | Critico | Alerta proactiva al 20% restante, re-fondeo automatico |
| Latencia alta de Monato (>5s) | Media | Medio | Timeout configurable, response 202 + polling |
| Volumen de pagos excede capacidad DynamoDB | Baja | Medio | On-demand scaling, monitoreo de throttling |
| Discrepancia masiva en conciliacion (>5%) | Baja | Critico | Pausa automatica de pagos, alerta CRITICAL al admin |

---

## Apendice A: Resumen de Tablas DynamoDB Nuevas

| Tabla | PK | SK | GSIs | Estimacion Items |
|-------|----|----|------|-----------------|
| `modspei_org_products_prod` | `sp_organization_id` | `PRODUCT#{type}` | 1 | ~5 por org |
| `modspei_billpay_payments_prod` | `sp_organization_id` | `BPAY#{payment_id}` | 5 | ~100-10K por org/mes |
| `modspei_billpay_providers_prod` | `CATEGORY#{cat}` | `BILLER#{id}` | 2 | ~500-1000 total |
| `modspei_billpay_conciliation_prod` | `CONCILIATION#{date}` | `ORG#{org}#{run}` | 0 | ~30 por dia |

## Apendice B: Variables de Configuracion Nuevas

```python
# Monato BillPay
MONATO_BILLPAY_BASE_URL = os.getenv("MONATO_BILLPAY_BASE_URL")
MONATO_BILLPAY_CLIENT_ID = os.getenv("MONATO_BILLPAY_CLIENT_ID")
MONATO_BILLPAY_CLIENT_SECRET = os.getenv("MONATO_BILLPAY_CLIENT_SECRET")
MONATO_BILLPAY_WEBHOOK_SECRET = os.getenv("MONATO_BILLPAY_WEBHOOK_SECRET")

# Tablas DynamoDB
DYNAMODB_ORG_PRODUCTS_TABLE = os.getenv(
    "DYNAMODB_ORG_PRODUCTS_TABLE", "modspei_org_products_prod"
)
DYNAMODB_BILLPAY_PAYMENTS_TABLE = os.getenv(
    "DYNAMODB_BILLPAY_PAYMENTS_TABLE", "modspei_billpay_payments_prod"
)
DYNAMODB_BILLPAY_PROVIDERS_TABLE = os.getenv(
    "DYNAMODB_BILLPAY_PROVIDERS_TABLE", "modspei_billpay_providers_prod"
)
DYNAMODB_BILLPAY_CONCILIATION_TABLE = os.getenv(
    "DYNAMODB_BILLPAY_CONCILIATION_TABLE", "modspei_billpay_conciliation_prod"
)

# Conciliacion
BILLPAY_CONCILIATION_SCHEDULE = os.getenv(
    "BILLPAY_CONCILIATION_SCHEDULE", "cron(0 2 * * ? *)"  # 02:00 UTC diario
)
BILLPAY_CONCILIATION_PENDING_THRESHOLD_HOURS = int(os.getenv(
    "BILLPAY_CONCILIATION_PENDING_THRESHOLD_HOURS", "4"
))

# Fondeo
BILLPAY_FUND_LOW_BALANCE_THRESHOLD = Decimal(os.getenv(
    "BILLPAY_FUND_LOW_BALANCE_THRESHOLD", "50000"  # Alertar cuando pool < $50K
))
BILLPAY_FUND_AUTO_AMOUNT = Decimal(os.getenv(
    "BILLPAY_FUND_AUTO_AMOUNT", "200000"  # Re-fondear $200K automaticamente
))

# Catalogo
BILLPAY_CATALOG_SYNC_SCHEDULE = os.getenv(
    "BILLPAY_CATALOG_SYNC_SCHEDULE", "cron(0 6 * * ? *)"  # 06:00 UTC diario
)
BILLPAY_CATALOG_TTL_HOURS = int(os.getenv("BILLPAY_CATALOG_TTL_HOURS", "48"))
```

## Apendice C: Estructura de Archivos Propuesta

```
covacha-payment/src/mipay_payment/
|
+-- strategies/
|   +-- spei/
|   |   +-- base_spei_provider.py             # (existente)
|   |   +-- monato_fincore_driver.py          # (existente)
|   |
|   +-- billpay/
|   |   +-- __init__.py
|   |   +-- base_billpay_provider.py          # Interface BillPayProvider
|   |   +-- billpay_dataclasses.py            # Request/Response dataclasses
|   |   +-- monato_billpay_driver.py          # MonatoBillPayDriver
|   |
|   +-- operations/
|   |   +-- billpay_strategy.py               # (existente, expandir)
|   |   +-- billpay_fund_strategy.py          # NUEVO
|   |   +-- billpay_refund_strategy.py        # NUEVO
|   |
|   +-- factory.py                            # ProviderFactory (expandir)
|
+-- services/
|   +-- billpay/
|   |   +-- __init__.py
|   |   +-- billpay_service.py                # Orquestador principal
|   |   +-- billpay_query_service.py          # Logica de consulta de deuda
|   |   +-- billpay_payment_service.py        # Logica de ejecucion de pago
|   |   +-- billpay_catalog_service.py        # Logica de catalogo
|   |   +-- billpay_conciliation_service.py   # Logica de conciliacion
|   |   +-- billpay_fee_calculator.py         # Calculo de comisiones
|   |   +-- billpay_receipt_service.py        # Generacion de comprobantes
|   |
|   +-- onboarding/
|       +-- __init__.py
|       +-- product_provisioner.py            # Orquestador de onboarding
|       +-- account_recipe.py                 # Recetas de cuentas por producto
|
+-- repositories/
|   +-- billpay_payment_repository.py         # CRUD modspei_billpay_payments
|   +-- billpay_provider_repository.py        # CRUD modspei_billpay_providers
|   +-- billpay_conciliation_repository.py    # CRUD modspei_billpay_conciliation
|   +-- org_product_repository.py             # CRUD modspei_org_products
|
+-- controllers/
|   +-- billpay_controller.py                 # Endpoints de BillPay
|   +-- onboarding_controller.py              # Endpoints de productos/onboarding
|   +-- conciliation_controller.py            # (expandir para BillPay)
|
+-- lambdas/
    +-- billpay_catalog_sync.py               # Lambda sincronizacion catalogo
    +-- billpay_conciliation.py               # Lambda conciliacion diaria


covacha-webhook/src/mipay_webhook/
|
+-- handlers/
    +-- billpay_monato_handler.py             # Webhook handler BillPay Monato
```

---

**Fin del documento.**

**Siguiente paso recomendado:** Comenzar con EP-BP-001 (Onboarding) y EP-BP-002 (Strategy Pattern) en paralelo, ya que no tienen dependencias entre si.
