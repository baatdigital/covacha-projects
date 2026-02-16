# mf-sp Frontend - Epicas Multi-Tier (Reemplazo de EP-SP-007 y EP-SP-008)

**Fecha**: 2026-02-14
**Product Owner**: SuperPago
**Estado**: Planificacion
**Reemplaza**: EP-SP-007 (Scaffold y Dashboard) y EP-SP-008 (Transferencias y Movimientos)
**Nuevas Epicas**: EP-SP-007, EP-SP-008, EP-SP-011, EP-SP-012, EP-SP-013

---

## Tabla de Contenidos

1. [Vision Multi-Tier](#vision-multi-tier)
2. [Arquitectura de 3 Niveles](#arquitectura-de-3-niveles)
3. [Mapa de Epicas Frontend](#mapa-de-epicas-frontend)
4. [Epicas Detalladas](#epicas-detalladas)
5. [User Stories Detalladas](#user-stories-detalladas)
6. [Roadmap Frontend](#roadmap-frontend)
7. [Grafo de Dependencias Frontend](#grafo-de-dependencias-frontend)
8. [Resumen de Estimaciones](#resumen-de-estimaciones)

---

## Vision Multi-Tier

El micro-frontend `mf-sp` debe servir a 3 tipos de usuario con vistas, permisos y funcionalidades diferenciadas:

```
SuperPago (Tier 1 - Admin)
|-- Cuenta Concentradora SuperPago
|-- Cuenta Reservada IVA
|-- Cuenta Reservada Comisiones
|-- Cuentas Privadas internas
|
|-- Boxito (Tier 2 - Cliente Empresa)
|   |-- Sub-Concentradora Boxito
|   |-- Cuenta Dispersion Nomina
|   |-- Cuenta Reservada IVA-Boxito
|   |-- CLABE operativa Boxito
|   +-- Clientes de Boxito (Tier 3 - B2C)
|       |-- Juan Perez -> Cuenta Privada + CLABE
|       +-- Maria Lopez -> Cuenta Privada + CLABE
|
+-- Pedro Garcia (Tier 3 - B2C directo de SuperPago)
    +-- Cuenta Privada + CLABE
```

---

## Arquitectura de 3 Niveles

### Tier 1: Portal Admin SuperPago (Nosotros)

| Propiedad | Valor |
|-----------|-------|
| **Rol** | Administrador de plataforma SuperPago |
| **Ruta base** | `/sp/admin` |
| **Permiso** | `sp:admin` o `role:platform_admin` |

**Funciones:**
- Dashboard global: todas las cuentas de todos los clientes
- Auditoria de proveedores SPEI (Monato y futuros)
- Monitoreo del comportamiento de clientes empresa
- Gestion de cuentas propias de SuperPago (concentradora, reservadas, privadas internas)
- Reconciliacion y reportes globales
- Configuracion de politicas y limites globales
- Visualizacion del grafo completo de cuentas del ecosistema
- Alertas y anomalias
- Dead Letter Queue (DLQ) management

### Tier 2: Portal Cliente Empresa (B2B)

| Propiedad | Valor |
|-----------|-------|
| **Rol** | Cliente empresarial (ej: "Boxito") |
| **Ruta base** | `/sp/business` |
| **Permiso** | `sp:business` o `role:org_admin` |

**Funciones:**
- Dashboard de SUS cuentas (sub-concentradora, dispersion, reservadas, CLABEs)
- Gestion de su estructura de cuentas (crear sub-cuentas)
- Transferencias SPEI out desde sus cuentas
- Movimientos internos entre sus cuentas
- Gestion de sus clientes persona natural (Tier 3)
- Historial de movimientos y estados de cuenta
- Configuracion de politicas para sus sub-cuentas
- Aprobacion de transferencias de alto monto

### Tier 3: Portal Usuario Final (B2C)

| Propiedad | Valor |
|-----------|-------|
| **Rol** | Persona natural (cliente de SuperPago o de una empresa) |
| **Ruta base** | `/sp/personal` |
| **Permiso** | `sp:personal` o `role:end_user` |

**Funciones:**
- Dashboard simple: saldo de su cuenta privada
- Historial de movimientos (depositos, retiros)
- Datos de su CLABE para recibir SPEI
- Transferencias SPEI out (si permitido por la empresa o SuperPago)
- Informacion de su cuenta

---

## Mapa de Epicas Frontend

| ID | Epica | Complejidad | Sprint | Dependencias |
|----|-------|-------------|--------|--------------|
| EP-SP-007 | mf-sp Scaffold + Arquitectura Multi-Tier | L | 2-3 | Ninguna (frontend) |
| EP-SP-008 | Portal Admin SuperPago (Tier 1) | XL | 3-4 | EP-SP-007, EP-SP-001 (API), EP-SP-003 (Ledger API) |
| EP-SP-011 | Portal Cliente Empresa B2B (Tier 2) | XL | 4-5 | EP-SP-007, EP-SP-013, EP-SP-001, EP-SP-004, EP-SP-006 |
| EP-SP-012 | Portal Usuario Final B2C (Tier 3) | M | 5 | EP-SP-007, EP-SP-013, EP-SP-001 |
| EP-SP-013 | Componentes Compartidos entre Tiers | L | 3-4 | EP-SP-007 |

---

## Epicas Detalladas

---

### EP-SP-007: mf-sp Scaffold + Arquitectura Multi-Tier

**Descripcion:**
Creacion del nuevo micro-frontend `mf-sp` (SuperPago SPEI) con Angular 21 y Native Federation. Incluye scaffold del proyecto, registro en el Shell (mf-core), arquitectura de routing con 3 portales (admin, business, personal), guards de acceso por rol, layouts diferenciados por tier, y servicios base (HTTP, shared state, tier detection).

**User Stories:**
- US-SP-025, US-SP-026, US-SP-027, US-SP-028

**Criterios de Aceptacion de la Epica:**
- [ ] Proyecto Angular 21 creado con estructura hexagonal
- [ ] Native Federation configurado (puerto 4212, remote name mfSP)
- [ ] Registrado en mf-core como remote
- [ ] SharedStateService implementado (lectura de covacha:auth, covacha:user, covacha:tenant)
- [ ] HttpService implementado con headers requeridos
- [ ] TierDetectionService que determina el tier del usuario actual por permisos/rol
- [ ] 3 layouts diferenciados: AdminLayout, BusinessLayout, PersonalLayout
- [ ] Routing con guards por tier: `tierGuard('admin')`, `tierGuard('business')`, `tierGuard('personal')`
- [ ] Redirect inteligente: al entrar a `/sp/`, redirige al portal del tier del usuario
- [ ] Path aliases configurados (@app, @core, @domain, @infrastructure, @presentation, @shared-state, @env)
- [ ] Modelos de dominio base (FinancialAccount, LedgerEntry, Transfer)
- [ ] Adapters base (accounts, transfers, ledger)
- [ ] Responsive design base
- [ ] Tests >= 98%

**Dependencias:** Ninguna (puede empezar cuando el equipo frontend este disponible)

**Complejidad:** L (nuevo MF completo, routing multi-tier, 3 layouts)

**Repositorio:** `mf-sp` (nuevo), `mf-core` (registro del remote)

---

### EP-SP-008: Portal Admin SuperPago (Tier 1)

**Descripcion:**
Portal de administracion de la plataforma para el equipo interno de SuperPago. Proporciona vision global de todas las cuentas de todos los clientes, herramientas de monitoreo y auditoria, gestion de cuentas propias de SuperPago, reconciliacion, configuracion de politicas globales, y visualizacion del grafo completo del ecosistema. Este es el centro de control financiero.

**User Stories:**
- US-SP-029, US-SP-030, US-SP-031, US-SP-032, US-SP-033, US-SP-034, US-SP-035

**Criterios de Aceptacion de la Epica:**
- [ ] Dashboard global con metricas del ecosistema completo
- [ ] Vista de todas las organizaciones con sus cuentas y saldos
- [ ] Grafo visual del ecosistema completo (todas las orgs, todas las cuentas)
- [ ] Panel de monitoreo de proveedores SPEI (Monato status, latencia, errores)
- [ ] Dashboard de reconciliacion con calendario y detalle de discrepancias
- [ ] Gestion de cuentas propias de SuperPago (concentradora, reservadas, internas)
- [ ] Configuracion de politicas y limites globales
- [ ] Audit trail viewer con filtros avanzados
- [ ] Panel de alertas y anomalias
- [ ] DLQ management (ver, reintentar, resolver)
- [ ] Export de reportes (CSV, PDF)
- [ ] Solo accesible con permiso `sp:admin`
- [ ] Tests >= 98%

**Dependencias:** EP-SP-007 (scaffold), EP-SP-001 (API cuentas), EP-SP-003 (Ledger API), EP-SP-009 (Reconciliacion API)

**Complejidad:** XL (7 user stories, dashboard complejo, grafos, reportes)

**Repositorio:** `mf-sp`

---

### EP-SP-011: Portal Cliente Empresa B2B (Tier 2)

**Descripcion:**
Portal para clientes empresariales (como "Boxito") que usan SuperPago para operar sus finanzas via SPEI. Proporciona dashboard de sus cuentas, formularios de transferencia SPEI out y movimientos internos, gestion de su estructura de cuentas, gestion de sus usuarios finales (Tier 3), historial de movimientos, y configuracion de politicas para sus sub-cuentas.

**User Stories:**
- US-SP-036, US-SP-037, US-SP-038, US-SP-039, US-SP-040, US-SP-041, US-SP-042

**Criterios de Aceptacion de la Epica:**
- [ ] Dashboard de cuentas de la organizacion con saldos y estados
- [ ] Formulario de transferencia SPEI out (wizard de 3 pasos)
- [ ] Formulario de movimiento interno (con filtrado por reglas del grafo)
- [ ] Creacion y gestion de estructura de cuentas (wizard)
- [ ] Historial de movimientos con filtros y paginacion server-side
- [ ] Gestion de usuarios finales (Tier 3) de la organizacion
- [ ] Panel de aprobaciones pendientes (transferencias de alto monto)
- [ ] Configuracion de politicas propias (limites, notificaciones)
- [ ] Export a CSV/PDF
- [ ] Solo accesible con permiso `sp:business` y scoped a la organizacion del usuario
- [ ] Tests >= 98%

**Dependencias:** EP-SP-007 (scaffold), EP-SP-013 (shared components), EP-SP-001 (API cuentas), EP-SP-004 (API SPEI out), EP-SP-006 (API internos)

**Complejidad:** XL (7 user stories, formularios complejos, multiples validaciones)

**Repositorio:** `mf-sp`

---

### EP-SP-012: Portal Usuario Final B2C (Tier 3)

**Descripcion:**
Portal simplificado para personas naturales que son clientes de SuperPago directamente o clientes de una empresa que usa SuperPago. Muestra saldo de su cuenta privada, historial de movimientos, datos de su CLABE para recibir SPEI, y opcionalmente permite transferencias salientes si la empresa o SuperPago lo permite.

**User Stories:**
- US-SP-043, US-SP-044, US-SP-045, US-SP-046

**Criterios de Aceptacion de la Epica:**
- [ ] Dashboard simple: saldo prominente, CLABE con boton copiar
- [ ] Historial de movimientos (depositos y retiros)
- [ ] Detalle de cada movimiento
- [ ] Transferencia SPEI out (si habilitado por politica de la org)
- [ ] Informacion de la cuenta (tipo, estado, CLABE, empresa propietaria)
- [ ] Interfaz optimizada para mobile
- [ ] Solo accesible con permiso `sp:personal`
- [ ] Datos scoped: solo ve SU cuenta, nada mas
- [ ] Tests >= 98%

**Dependencias:** EP-SP-007 (scaffold), EP-SP-013 (shared components), EP-SP-001 (API cuentas)

**Complejidad:** M (4 user stories, interfaz simple pero con restricciones de seguridad)

**Repositorio:** `mf-sp`

---

### EP-SP-013: Componentes Compartidos entre Tiers

**Descripcion:**
Biblioteca de componentes reutilizables que se comparten entre los 3 portales (Tier 1, 2 y 3). Incluye tabla de movimientos, grafico de cuentas (arbol jerarquico), formulario de transferencia SPEI out, visor de detalle de cuenta, y estado de transferencia en tiempo real. Estos componentes se parametrizan por tier para mostrar mas o menos informacion segun el nivel de acceso.

**User Stories:**
- US-SP-047, US-SP-048, US-SP-049, US-SP-050, US-SP-051

**Criterios de Aceptacion de la Epica:**
- [ ] MovementsTableComponent reutilizable con @Input para configurar columnas visibles por tier
- [ ] AccountTreeComponent visualizacion de grafo/arbol de cuentas (SVG interactivo)
- [ ] TransferFormComponent formulario de transferencia SPEI out parametrizable
- [ ] AccountDetailCardComponent visor de detalle de cuenta con nivel de detalle por tier
- [ ] TransferStatusTrackerComponent estado de transferencia en tiempo real (polling)
- [ ] Todos los componentes usan OnPush + Signals
- [ ] Todos exportados via barrel (shared/components/index.ts)
- [ ] Documentacion de uso por tier
- [ ] Tests >= 98%

**Dependencias:** EP-SP-007 (scaffold, modelos, adapters)

**Complejidad:** L (5 componentes complejos, parametrizados, alto potencial de reuso)

**Repositorio:** `mf-sp`

---

## User Stories Detalladas

---

### EP-SP-007: mf-sp Scaffold + Arquitectura Multi-Tier

---

#### US-SP-025: Scaffold del Micro-frontend mf-sp con Estructura Hexagonal

**ID:** US-SP-025
**Epica:** EP-SP-007
**Prioridad:** P0

**Historia:**
Como **Desarrollador** quiero un micro-frontend Angular 21 nuevo llamado mf-sp con estructura hexagonal y Native Federation para tener la base donde construir los 3 portales de SPEI.

**Criterios de Aceptacion:**
- [ ] Proyecto Angular 21 standalone con estructura hexagonal:
  ```
  mf-sp/src/app/
  |-- domain/
  |   |-- models/          # FinancialAccount, Transfer, LedgerEntry, Beneficiary
  |   +-- ports/           # Interfaces de puertos
  |-- infrastructure/
  |   +-- adapters/        # accounts.adapter, transfers.adapter, ledger.adapter
  |-- application/
  |   +-- use-cases/       # Logica de aplicacion por tier
  |-- core/
  |   |-- http/            # HttpService (headers, tenant, auth)
  |   |-- guards/          # TierGuard, AuthGuard
  |   +-- services/        # TierDetectionService, ToastService
  |-- presentation/
  |   |-- layouts/         # AdminLayout, BusinessLayout, PersonalLayout
  |   |-- pages/
  |   |   |-- admin/       # Paginas Tier 1
  |   |   |-- business/    # Paginas Tier 2
  |   |   +-- personal/    # Paginas Tier 3
  |   +-- shared/          # Componentes compartidos (EP-SP-013)
  |-- shared-state/        # SharedStateService
  +-- remote-entry/        # Entry point para Federation
  ```
- [ ] `federation.config.js`:
  - name: `mfSP`
  - puerto: 4212
  - exposes: `./Component`, `./routes`
  - shared: Angular, RxJS (singleton, strictVersion)
- [ ] Registrado en `mf-core` como remote:
  ```javascript
  remotes: { mfSP: 'http://localhost:4212/remoteEntry.json' }
  ```
- [ ] `SharedStateService` funcional (lee covacha:auth, covacha:user, covacha:tenant)
- [ ] `HttpService` funcional con headers:
  - `X-API-KEY`, `Authorization`, `X-Tenant-Id`, `X-SP-Organization-Id`, `X-SP-Project-Id`
- [ ] Path aliases configurados en tsconfig:
  - @app, @core, @domain, @infrastructure, @presentation, @shared-state, @env
- [ ] Modelos de dominio definidos (interfaces TypeScript):
  - `FinancialAccount` (account_type, status, clabe, parent_account_id, etc.)
  - `Transfer` (source, destination, amount, status, tracking_code, etc.)
  - `LedgerEntry` (entry_type, amount, category, status, etc.)
  - `Beneficiary` (clabe, alias, holder_name, bank_name)
- [ ] Build y serve funcionan (`yarn start` en puerto 4212)
- [ ] Se carga correctamente desde el Shell

**Tareas Tecnicas:**
1. `ng new mf-sp --standalone --style=scss --routing`
2. Configurar Native Federation con `@angular-architects/native-federation`
3. Crear estructura de carpetas hexagonal
4. Copiar y adaptar SharedStateService de mf-marketing
5. Copiar y adaptar HttpService de mf-marketing
6. Definir modelos de dominio en `domain/models/`
7. Configurar tsconfig con path aliases
8. Crear adapters stub (accounts, transfers, ledger)
9. Registrar remote en mf-core `federation.config.js`
10. Verificar carga desde Shell
11. Tests basicos (AppComponent carga, HttpService funciona)

**Dependencias:** Ninguna
**Estimacion:** 3 dev-days

---

#### US-SP-026: Routing Multi-Tier con Guards por Rol

**ID:** US-SP-026
**Epica:** EP-SP-007
**Prioridad:** P0

**Historia:**
Como **Sistema** quiero que el routing de mf-sp tenga 3 secciones protegidas por guards segun el rol/permiso del usuario para que cada tipo de usuario solo vea su portal correspondiente.

**Criterios de Aceptacion:**
- [ ] Estructura de rutas:
  ```
  /sp/                          -> Redirect inteligente al portal del tier del usuario
  /sp/admin/                    -> Portal Admin (Tier 1, requiere sp:admin)
  /sp/admin/dashboard           -> Dashboard global
  /sp/admin/organizations       -> Lista de organizaciones
  /sp/admin/organizations/:id   -> Detalle de organizacion
  /sp/admin/accounts/tree       -> Grafo completo de cuentas
  /sp/admin/reconciliation      -> Dashboard de reconciliacion
  /sp/admin/audit               -> Audit trail
  /sp/admin/policies            -> Configuracion de politicas globales
  /sp/admin/alerts              -> Alertas y anomalias
  /sp/admin/dlq                 -> Dead Letter Queue
  /sp/admin/providers           -> Monitoreo de proveedores SPEI
  /sp/business/                 -> Portal Empresa (Tier 2, requiere sp:business)
  /sp/business/dashboard        -> Dashboard de cuentas
  /sp/business/accounts         -> Lista de cuentas
  /sp/business/accounts/new     -> Crear cuenta (wizard)
  /sp/business/accounts/:id     -> Detalle de cuenta
  /sp/business/accounts/tree    -> Arbol de mis cuentas
  /sp/business/transfers/spei   -> Transferencia SPEI out
  /sp/business/transfers/internal -> Movimiento interno
  /sp/business/movements        -> Historial de movimientos
  /sp/business/beneficiaries    -> Beneficiarios frecuentes
  /sp/business/approvals        -> Aprobaciones pendientes
  /sp/business/users            -> Gestion de usuarios finales
  /sp/business/settings         -> Configuracion (limites, politicas)
  /sp/personal/                 -> Portal Personal (Tier 3, requiere sp:personal)
  /sp/personal/dashboard        -> Mi saldo y CLABE
  /sp/personal/movements        -> Mis movimientos
  /sp/personal/transfer         -> Enviar SPEI (si habilitado)
  /sp/personal/account          -> Info de mi cuenta
  ```
- [ ] `TierDetectionService` determina el tier del usuario:
  ```typescript
  // Logica de deteccion:
  // 1. Leer permisos de covacha:user
  // 2. Si tiene sp:admin -> Tier 1
  // 3. Si tiene sp:business -> Tier 2
  // 4. Si tiene sp:personal -> Tier 3
  // 5. Si tiene multiples -> prioridad: admin > business > personal
  // 6. Fallback: redirect a /unauthorized
  ```
- [ ] `tierGuard(requiredTier: 'admin' | 'business' | 'personal')`:
  - Functional guard (no clase)
  - Verifica permisos del usuario via SharedStateService
  - Si no tiene permiso: redirige a `/sp/` (que a su vez redirige al tier correcto)
  - Logging de intentos de acceso no autorizado
- [ ] Redirect raiz `/sp/` analiza el tier y redirige:
  - Admin -> `/sp/admin/dashboard`
  - Business -> `/sp/business/dashboard`
  - Personal -> `/sp/personal/dashboard`
- [ ] Cada seccion de tier usa su propio layout (lazy loaded)
- [ ] Todas las paginas son lazy loaded

**Tareas Tecnicas:**
1. Crear `TierDetectionService` en `core/services/`
2. Crear `tierGuard` functional guard en `core/guards/`
3. Crear `entry.routes.ts` con las 3 secciones
4. Implementar redirect inteligente en ruta raiz
5. Tests del guard (admin puede acceder a admin, no a business; business no a admin; etc.)
6. Tests del TierDetectionService con diferentes permisos
7. Tests de redirect raiz

**Dependencias:** US-SP-025
**Estimacion:** 3 dev-days

---

#### US-SP-027: Layouts Diferenciados por Tier

**ID:** US-SP-027
**Epica:** EP-SP-007
**Prioridad:** P0

**Historia:**
Como **Usuario** quiero que el portal de SPEI tenga una interfaz visual diferente segun mi rol para que la experiencia sea adecuada a mi nivel de complejidad (admin ve todo, personal ve lo minimo).

**Criterios de Aceptacion:**
- [ ] **AdminLayoutComponent** (`/sp/admin/*`):
  - Sidebar amplio con navegacion completa:
    - Dashboard Global
    - Organizaciones
    - Grafo de Cuentas
    - Reconciliacion
    - Auditoria
    - Politicas
    - Alertas
    - DLQ
    - Proveedores SPEI
  - Header con: nombre "Admin SuperPago SPEI", indicador de entorno (dev/prod), usuario actual
  - Footer con version y status de servicios
  - Colores: palette de admin (tonos oscuros, profesional)
- [ ] **BusinessLayoutComponent** (`/sp/business/*`):
  - Sidebar con navegacion de empresa:
    - Dashboard
    - Mis Cuentas
    - Transferencia SPEI
    - Movimiento Interno
    - Historial
    - Beneficiarios
    - Aprobaciones (con badge de pendientes)
    - Usuarios
    - Configuracion
  - Header con: nombre de la organizacion, saldo total rapido
  - Colores: palette corporativo (azules, verdes)
- [ ] **PersonalLayoutComponent** (`/sp/personal/*`):
  - Navegacion minimal (bottom nav en mobile, sidebar compacto en desktop):
    - Mi Cuenta
    - Movimientos
    - Transferir (si habilitado)
  - Header simple: nombre del usuario, saldo prominente
  - Optimizado para mobile-first
  - Colores: palette amigable (tonos suaves, accesibles)
- [ ] Todos los layouts usan `<router-outlet>` para contenido
- [ ] Todos son OnPush + Signals
- [ ] Responsive: cada layout se adapta a mobile/tablet/desktop
- [ ] Skeleton loaders en sidebar mientras carga datos

**Tareas Tecnicas:**
1. Crear `AdminLayoutComponent` con sidebar completo
2. Crear `BusinessLayoutComponent` con sidebar empresa
3. Crear `PersonalLayoutComponent` con nav minimal
4. Crear componentes de sidebar reutilizables (NavItem, NavGroup)
5. Definir palettes de colores por tier en SCSS variables
6. Tests de renderizado de cada layout
7. Tests de responsive (verificar clases CSS por breakpoint)

**Dependencias:** US-SP-025
**Estimacion:** 4 dev-days

---

#### US-SP-028: Modelos de Dominio y Adapters Base

**ID:** US-SP-028
**Epica:** EP-SP-007
**Prioridad:** P0

**Historia:**
Como **Desarrollador** quiero tener los modelos de dominio TypeScript y los adapters HTTP definidos para poder construir las paginas de los 3 portales conectados a la API real.

**Criterios de Aceptacion:**
- [ ] Modelos en `domain/models/`:
  ```typescript
  // financial-account.model.ts
  interface FinancialAccount {
    id: string;
    organization_id: string;
    account_type: 'CONCENTRADORA' | 'CLABE' | 'DISPERSION' | 'RESERVADA';
    status: 'PENDING' | 'ACTIVE' | 'FROZEN' | 'CLOSED';
    display_name: string;
    clabe?: string;
    parent_account_id?: string;
    available_balance: number;
    pending_balance: number;
    total_balance: number;
    currency: string;
    metadata: Record<string, unknown>;
    provider_account_id?: string;
    children_count?: number;
    created_at: string;
    updated_at: string;
    created_by: string;
  }

  // transfer.model.ts
  interface Transfer {
    id: string;
    organization_id: string;
    transfer_type: 'SPEI_OUT' | 'INTERNAL' | 'BULK_INTERNAL';
    source_account_id: string;
    destination_account_id?: string;
    destination_clabe?: string;
    destination_name?: string;
    destination_bank?: string;
    amount: number;
    commission?: number;
    concept: string;
    reference?: string;
    tracking_code?: string;
    status: 'PENDING' | 'PENDING_APPROVAL' | 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'REJECTED' | 'REVERSED';
    idempotency_key: string;
    created_at: string;
    completed_at?: string;
    created_by: string;
    error_message?: string;
  }

  // ledger-entry.model.ts
  interface LedgerEntry {
    entry_id: string;
    account_id: string;
    transaction_id: string;
    entry_type: 'DEBIT' | 'CREDIT';
    amount: number;
    currency: string;
    status: 'PENDING' | 'CONFIRMED' | 'REVERSED';
    category: 'SPEI_IN' | 'SPEI_OUT' | 'INTERNAL_TRANSFER' | 'COMMISSION' | 'REFUND' | 'REVERSAL';
    counterpart_account_id?: string;
    description: string;
    reference?: string;
    created_at: string;
  }

  // beneficiary.model.ts
  interface Beneficiary {
    id: string;
    organization_id: string;
    clabe: string;
    alias: string;
    holder_name: string;
    bank_name: string;
    bank_code: string;
    email?: string;
    validated: boolean;
    created_at: string;
  }

  // spei-participant.model.ts
  interface SPEIParticipant {
    code: string;
    name: string;
    short_name: string;
    active: boolean;
  }

  // account-tree.model.ts
  interface AccountTreeNode {
    account: FinancialAccount;
    children: AccountTreeNode[];
  }

  // tier.model.ts
  type UserTier = 'admin' | 'business' | 'personal';
  ```
- [ ] Adapters en `infrastructure/adapters/`:
  ```typescript
  // accounts.adapter.ts
  // GET /organizations/{org_id}/accounts
  // GET /organizations/{org_id}/accounts/{id}
  // GET /organizations/{org_id}/accounts/{id}/balance
  // GET /organizations/{org_id}/accounts/{id}/children
  // GET /organizations/{org_id}/accounts/tree
  // POST /organizations/{org_id}/accounts
  // PATCH /organizations/{org_id}/accounts/{id}
  // PATCH /organizations/{org_id}/accounts/{id}/status

  // transfers.adapter.ts
  // POST /organizations/{org_id}/transfers/spei-out
  // POST /organizations/{org_id}/transfers/internal
  // POST /organizations/{org_id}/transfers/bulk-internal
  // GET /organizations/{org_id}/transfers
  // GET /organizations/{org_id}/transfers/{id}

  // ledger.adapter.ts
  // GET /organizations/{org_id}/accounts/{id}/statement
  // GET /admin/ledger/balance-trial
  // GET /admin/ledger/balance-trial/{org_id}

  // beneficiaries.adapter.ts
  // GET /organizations/{org_id}/beneficiaries
  // POST /organizations/{org_id}/beneficiaries
  // DELETE /organizations/{org_id}/beneficiaries/{id}

  // admin.adapter.ts (solo Tier 1)
  // GET /admin/organizations (todas las orgs)
  // GET /admin/accounts/global-tree (grafo completo)
  // GET /admin/reconciliation
  // GET /admin/audit-log
  // GET /admin/dlq
  // POST /admin/dlq/{id}/retry
  // GET /admin/providers/status
  // GET /admin/alerts

  // spei-catalog.adapter.ts
  // GET /spei/participants (catalogo de bancos)
  // POST /spei/validate-clabe (penny validation)
  ```
- [ ] Cada adapter usa `HttpService` y retorna `Observable<T>` tipado
- [ ] Manejo de errores estandarizado con `catchError`
- [ ] Cada adapter tiene su `.spec.ts` con HttpClientTestingModule

**Tareas Tecnicas:**
1. Crear todos los modelos en `domain/models/`
2. Crear `AccountsAdapter` con todos los metodos
3. Crear `TransfersAdapter`
4. Crear `LedgerAdapter`
5. Crear `BeneficiariesAdapter`
6. Crear `AdminAdapter` (solo Tier 1)
7. Crear `SPEICatalogAdapter`
8. Tests de cada adapter (mock HTTP calls)

**Dependencias:** US-SP-025
**Estimacion:** 4 dev-days

---

### EP-SP-008: Portal Admin SuperPago (Tier 1)

---

#### US-SP-029: Dashboard Global del Ecosistema

**ID:** US-SP-029
**Epica:** EP-SP-008
**Prioridad:** P0

**Historia:**
Como **Administrador de Plataforma** quiero ver un dashboard con metricas globales de todo el ecosistema SPEI para tener vision completa del estado financiero de SuperPago y todos sus clientes.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/admin/dashboard`
- [ ] Cards de KPIs principales:
  - Saldo total del ecosistema (suma de todas las cuentas de todas las orgs)
  - Numero total de cuentas activas
  - Volumen de transacciones hoy (cantidad y monto)
  - Transferencias pendientes/en proceso
  - Comisiones generadas hoy
  - Alertas activas (badge rojo si hay)
- [ ] Grafica de volumen de transacciones ultimos 30 dias (linea)
- [ ] Grafica de distribucion por tipo de cuenta (dona/pie)
- [ ] Tabla "Top 5 organizaciones por volumen" con link a detalle
- [ ] Tabla "Ultimas 10 transferencias" con estado en tiempo real
- [ ] Indicador de status de Monato (verde/rojo con latencia)
- [ ] Status de reconciliacion del dia anterior (ok/discrepancias)
- [ ] Auto-refresh cada 60 segundos (configurable)
- [ ] Skeleton loaders mientras cargan datos
- [ ] OnPush + Signals

**Tareas Tecnicas:**
1. Crear `AdminDashboardComponent` (page)
2. Crear `EcosystemKpisComponent` (cards de KPIs)
3. Crear `TransactionVolumeChartComponent` (grafica de linea)
4. Crear `AccountDistributionChartComponent` (dona)
5. Crear `TopOrganizationsTableComponent`
6. Crear `RecentTransfersTableComponent`
7. Crear `ProviderStatusIndicatorComponent`
8. Implementar auto-refresh con RxJS timer
9. Tests de renderizado y logica

**Dependencias:** US-SP-025, US-SP-026, US-SP-027 (scaffold + routing + layout), EP-SP-001 (API)
**Estimacion:** 5 dev-days

---

#### US-SP-030: Vista de Organizaciones y sus Cuentas

**ID:** US-SP-030
**Epica:** EP-SP-008
**Prioridad:** P0

**Historia:**
Como **Administrador de Plataforma** quiero ver la lista de todas las organizaciones con sus cuentas y saldos para monitorear el estado financiero de cada cliente.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/admin/organizations`
- [ ] Tabla con columnas:
  - Nombre de organizacion
  - Numero de cuentas activas
  - Saldo total (suma de todas las cuentas)
  - Volumen del mes (transferencias in + out)
  - Estado (activa, suspendida)
  - Fecha de registro
  - Acciones (ver detalle, ver cuentas, congelar)
- [ ] Filtros: estado, rango de saldo, busqueda por nombre
- [ ] Paginacion server-side
- [ ] Click en organizacion -> `/sp/admin/organizations/:orgId`
- [ ] Pagina de detalle de organizacion:
  - Info general (nombre, contacto, fecha registro)
  - Lista de cuentas con saldos (reutiliza componente compartido)
  - Arbol de cuentas (reutiliza AccountTreeComponent de EP-SP-013)
  - Ultimas transferencias de la org
  - Limites y politicas configurados
  - Acciones: congelar/descongelar org, modificar limites
- [ ] Boton "Crear organizacion" (formulario basico)

**Tareas Tecnicas:**
1. Crear `OrganizationsListComponent` (page)
2. Crear `OrganizationDetailComponent` (page)
3. Crear `OrganizationsTableComponent` (sub-componente)
4. Crear `OrganizationInfoComponent`
5. Integrar con AdminAdapter
6. Tests de renderizado, filtros, paginacion

**Dependencias:** US-SP-029 (dashboard listo), US-SP-028 (adapters)
**Estimacion:** 5 dev-days

---

#### US-SP-031: Grafo Visual del Ecosistema Completo

**ID:** US-SP-031
**Epica:** EP-SP-008
**Prioridad:** P1

**Historia:**
Como **Administrador de Plataforma** quiero ver la estructura completa de cuentas de todo el ecosistema como un arbol visual interactivo para entender rapidamente la jerarquia y detectar anomalias.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/admin/accounts/tree`
- [ ] Vista de arbol multi-nivel:
  ```
  SuperPago (raiz)
  |-- [Concentradora SP] $500,000
  |   |-- [CLABE Operativa] $200,000
  |   |-- [Dispersion Nomina] $50,000
  |   +-- [Reservada IVA] $100,000
  |
  |-- Boxito (org)
  |   |-- [Sub-Concentradora] $300,000
  |   |   |-- [CLABE Boxito] $150,000
  |   |   +-- [Dispersion] $50,000
  |   +-- Usuarios Boxito
  |       |-- Juan [Privada] $5,000
  |       +-- Maria [Privada] $3,000
  ```
- [ ] Nodos con color por tipo (concentradora: azul, CLABE: verde, dispersion: naranja, reservada: gris)
- [ ] Nodos muestran: nombre, tipo, saldo, estado (opacidad para frozen/closed)
- [ ] Interactivo:
  - Click en nodo -> panel lateral con detalle
  - Hover -> tooltip con info rapida
  - Zoom y pan (para ecosistemas grandes)
  - Expandir/colapsar ramas
  - Buscar cuenta por nombre o CLABE
- [ ] Filtro por organizacion (ver arbol de solo 1 org o todas)
- [ ] Selector de layout: vertical, horizontal, radial
- [ ] Reutiliza `AccountTreeComponent` de EP-SP-013 con modo "full ecosystem"

**Tareas Tecnicas:**
1. Crear `EcosystemTreeComponent` (page, wrapper)
2. Extender `AccountTreeComponent` para modo multi-org
3. Implementar panel lateral de detalle
4. Logica de busqueda dentro del arbol
5. Implementar filtro por organizacion
6. Tests de interactividad y renderizado

**Dependencias:** US-SP-048 (AccountTreeComponent de EP-SP-013), US-SP-028 (AdminAdapter)
**Estimacion:** 4 dev-days

---

#### US-SP-032: Monitoreo de Proveedores SPEI

**ID:** US-SP-032
**Epica:** EP-SP-008
**Prioridad:** P1

**Historia:**
Como **Administrador de Plataforma** quiero monitorear el estado y rendimiento de los proveedores SPEI (Monato y futuros) para detectar problemas de integracion rapidamente.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/admin/providers`
- [ ] Card por proveedor (hoy solo Monato, extensible):
  - Estado: Online/Offline (indicador verde/rojo)
  - Latencia promedio (ultimo minuto, ultima hora, ultimo dia)
  - Tasa de exito de operaciones (%, con grafica sparkline)
  - Errores recientes (ultimos 10, con tipo y timestamp)
  - Uptime (%, ultimos 30 dias)
- [ ] Grafica de latencia ultimas 24 horas
- [ ] Grafica de tasa de errores ultimas 24 horas
- [ ] Tabla de eventos recientes:
  - Tipo (money_out, money_in, webhook)
  - Estado (success, error, timeout)
  - Latencia
  - Timestamp
  - Detalle (expandible)
- [ ] Alerta visual si latencia > umbral o tasa de error > umbral
- [ ] Auto-refresh cada 30 segundos

**Tareas Tecnicas:**
1. Crear `ProvidersMonitorComponent` (page)
2. Crear `ProviderCardComponent` (card por proveedor)
3. Crear `LatencyChartComponent` (grafica sparkline)
4. Crear `ProviderEventsTableComponent`
5. Integrar con AdminAdapter para status de proveedor
6. Tests

**Dependencias:** US-SP-029 (dashboard admin), US-SP-028 (adapters)
**Estimacion:** 3 dev-days

---

#### US-SP-033: Dashboard de Reconciliacion

**ID:** US-SP-033
**Epica:** EP-SP-008
**Prioridad:** P1

**Historia:**
Como **Administrador de Plataforma** quiero un dashboard de reconciliacion para ver el estado de la reconciliacion diaria, revisar discrepancias, y resolverlas desde la interfaz.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/admin/reconciliation`
- [ ] Vista de calendario con color por dia:
  - Verde: reconciliacion exitosa, todo cuadra
  - Amarillo: reconciliacion con discrepancias menores (< umbral)
  - Rojo: discrepancias significativas
  - Gris: no ejecutado
- [ ] Click en dia -> panel de detalle:
  - Resumen: transacciones comparadas, matches, discrepancias
  - Tabla de discrepancias:
    - Tipo (monto diferente, faltante en ledger, faltante en Monato, estado inconsistente)
    - Monto esperado vs monto real
    - Referencia/tracking code
    - Status de resolucion
  - Acciones por discrepancia:
    - "Ajustar ledger" (crea entry de ajuste con justificacion)
    - "Ignorar" (requiere justificacion)
    - "Escalar" (notifica a supervisor)
- [ ] KPIs de reconciliacion:
  - Tasa de exito (% de dias sin discrepancias)
  - Monto total de discrepancias pendientes
  - Tiempo promedio de resolucion
  - Tendencia (mejorando/empeorando)
- [ ] Balance trial global: boton "Ejecutar ahora" con resultado inmediato
- [ ] Filtro por organizacion y rango de fechas

**Tareas Tecnicas:**
1. Crear `ReconciliationDashboardComponent` (page)
2. Crear `ReconciliationCalendarComponent` (calendario con colores)
3. Crear `DiscrepancyListComponent` (tabla de discrepancias)
4. Crear `DiscrepancyResolutionModalComponent`
5. Crear `BalanceTrialComponent` (resultado de balance trial)
6. Integrar con AdminAdapter (reconciliation endpoints)
7. Tests de renderizado y acciones

**Dependencias:** US-SP-029, US-SP-028, EP-SP-009 (API de reconciliacion)
**Estimacion:** 5 dev-days

---

#### US-SP-034: Audit Trail Viewer

**ID:** US-SP-034
**Epica:** EP-SP-008
**Prioridad:** P1

**Historia:**
Como **Administrador de Plataforma** quiero revisar el audit trail completo del sistema para investigar incidentes y cumplir con regulaciones.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/admin/audit`
- [ ] Tabla de eventos de auditoria con columnas:
  - Fecha/Hora (precision a milisegundos)
  - Usuario (nombre + ID, o "SYSTEM")
  - Accion (CREATE_ACCOUNT, SEND_TRANSFER, CHANGE_STATUS, APPROVE, REJECT, etc.)
  - Recurso (tipo + ID: "Account abc-123", "Transfer xyz-456")
  - Organizacion
  - IP / User-Agent
  - Detalle (expandible: muestra JSON before/after)
- [ ] Filtros avanzados:
  - Por usuario
  - Por accion
  - Por tipo de recurso
  - Por organizacion
  - Por rango de fechas
  - Busqueda libre (en detalle)
- [ ] Paginacion server-side (100 por pagina)
- [ ] Export a CSV
- [ ] Click en fila -> drawer con detalle completo incluyendo diff (before/after)
- [ ] Solo lectura (no se puede editar ni eliminar registros de auditoria)

**Tareas Tecnicas:**
1. Crear `AuditTrailComponent` (page)
2. Crear `AuditTableComponent` (tabla con expandable rows)
3. Crear `AuditFiltersComponent`
4. Crear `AuditDetailDrawerComponent`
5. Implementar export CSV
6. Integrar con AdminAdapter (audit-log endpoint)
7. Tests

**Dependencias:** US-SP-029, US-SP-028, EP-SP-009 (API audit trail)
**Estimacion:** 4 dev-days

---

#### US-SP-035: Gestion de Politicas y Alertas Globales

**ID:** US-SP-035
**Epica:** EP-SP-008
**Prioridad:** P2

**Historia:**
Como **Administrador de Plataforma** quiero configurar politicas globales (limites, comisiones, aprobaciones) y ver alertas del sistema para controlar el riesgo y resolver problemas rapidamente.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/admin/policies`:
  - **Limites globales**:
    - Monto maximo por transferencia (default)
    - Monto maximo diario (default)
    - Monto maximo mensual (default)
    - Operaciones maximas por dia (default)
    - Formulario de edicion con confirmacion
  - **Comisiones**:
    - Tabla de comisiones por tipo de cuenta
    - Comision default por transferencia SPEI
    - Descuentos por volumen
    - Formulario de edicion
  - **Aprobaciones**:
    - Umbral global de aprobacion (monto)
    - Numero de aprobadores requeridos
    - Timeout de aprobacion
  - Historial de cambios a politicas (quien cambio que, cuando)
- [ ] Pagina `/sp/admin/alerts`:
  - Lista de alertas activas con prioridad (critica, alta, media, baja)
  - Tipos: saldo bajo, transferencia sospechosa, proveedor offline, reconciliacion fallida, limite excedido
  - Acciones: marcar como vista, escalar, resolver
  - Filtros por tipo, prioridad, estado
  - Badge en sidebar con conteo de alertas no vistas
- [ ] Pagina `/sp/admin/dlq`:
  - Lista de mensajes en Dead Letter Queue
  - Detalle del payload de cada mensaje
  - Acciones: reintentar, resolver manualmente, ignorar con justificacion
  - Metricas: cantidad en DLQ, tiempo promedio en cola

**Tareas Tecnicas:**
1. Crear `PoliciesPageComponent` con tabs
2. Crear `LimitsConfigComponent`
3. Crear `CommissionsConfigComponent`
4. Crear `ApprovalsConfigComponent`
5. Crear `AlertsPageComponent`
6. Crear `AlertsListComponent`
7. Crear `DlqPageComponent`
8. Crear `DlqMessageDetailComponent`
9. Integrar con AdminAdapter
10. Tests de formularios y acciones

**Dependencias:** US-SP-029, US-SP-028, EP-SP-010 (API politicas)
**Estimacion:** 5 dev-days

---

### EP-SP-011: Portal Cliente Empresa B2B (Tier 2)

---

#### US-SP-036: Dashboard de Cuentas Empresarial

**ID:** US-SP-036
**Epica:** EP-SP-011
**Prioridad:** P0

**Historia:**
Como **Cliente Empresarial** quiero ver un dashboard con todas mis cuentas, saldos, y estado para tener una vision general de mis finanzas en SuperPago.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/business/dashboard`
- [ ] Cards de KPIs:
  - Saldo total (suma de todas las cuentas de la org)
  - Numero de cuentas activas
  - Transferencias del mes (in + out, monto y cantidad)
  - Comisiones del mes
  - Aprobaciones pendientes (badge)
- [ ] Lista de cuentas mostrando:
  - Nombre (display_name)
  - Tipo (con icono visual: concentradora, CLABE, dispersion, reservada)
  - CLABE (si aplica, con boton de copiar)
  - Saldo disponible (formatted con $ y separadores de miles)
  - Estado (badge: activa, pendiente, congelada)
- [ ] Filtros: por tipo, por estado
- [ ] Busqueda por nombre o CLABE
- [ ] Card de acciones rapidas:
  - "Enviar SPEI" -> `/sp/business/transfers/spei`
  - "Mover fondos" -> `/sp/business/transfers/internal`
  - "Crear cuenta" -> `/sp/business/accounts/new`
  - "Ver historial" -> `/sp/business/movements`
- [ ] Graficas:
  - Saldo historico ultimos 30 dias (linea)
  - Distribucion de saldo por tipo de cuenta (dona)
- [ ] Responsive: cards en mobile, tabla en desktop
- [ ] Skeleton loaders mientras carga
- [ ] OnPush + Signals
- [ ] Solo muestra cuentas de la organizacion del usuario (scoped)

**Tareas Tecnicas:**
1. Crear `BusinessDashboardComponent` (page)
2. Crear `BusinessKpisComponent` (cards de KPIs)
3. Crear `AccountsListComponent` (lista de cuentas) - reutiliza AccountDetailCard de EP-SP-013
4. Crear `QuickActionsComponent`
5. Crear `BalanceHistoryChartComponent`
6. Integrar con AccountsAdapter (scoped a org)
7. Tests de renderizado y logica

**Dependencias:** US-SP-025, US-SP-026, US-SP-027 (scaffold), US-SP-028 (adapters), EP-SP-001 (API)
**Estimacion:** 5 dev-days

---

#### US-SP-037: Formulario de Transferencia SPEI Out (B2B)

**ID:** US-SP-037
**Epica:** EP-SP-011
**Prioridad:** P0

**Historia:**
Como **Cliente Empresarial** quiero un formulario para enviar dinero via SPEI a cuentas externas para poder hacer pagos desde la plataforma.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/business/transfers/spei`
- [ ] Reutiliza `TransferFormComponent` de EP-SP-013 con config B2B:
  - Modo: `business` (muestra todas las cuentas de la org como origen)
  - Cuentas origen: dropdown de cuentas CLABE y DISPERSION activas de la org, mostrando saldo
  - Si cuenta RESERVADA: solo permite destino fijo (auto-fill)
- [ ] Wizard de 3 pasos (definido en componente compartido):
  1. **Seleccionar origen**: dropdown de cuentas de la org
  2. **Datos destino**: CLABE, titular, banco, concepto, referencia
  3. **Confirmar**: resumen, comision desglosada, total a debitar
- [ ] Si el beneficiario ya esta guardado: autocompletar al seleccionarlo
- [ ] Validacion en tiempo real: CLABE format, saldo suficiente (monto + comision)
- [ ] Despues de enviar:
  - Modal de confirmacion con clave de rastreo
  - Opcion "Guardar beneficiario"
  - Boton "Hacer otra transferencia"
  - Redirige a `TransferStatusTracker` para seguimiento
- [ ] Si monto > umbral de aprobacion de la org:
  - Mensaje: "Esta transferencia requiere aprobacion. Se notificara a los aprobadores."
  - Status: PENDING_APPROVAL

**Tareas Tecnicas:**
1. Crear `BusinessSpeiTransferComponent` (page, wrapper)
2. Integrar `TransferFormComponent` de EP-SP-013 con config B2B
3. Integrar con BeneficiariesAdapter para autocompletado
4. Integrar con SPEICatalogAdapter para banco por CLABE
5. Logica de deteccion de umbral de aprobacion
6. Tests del formulario, validaciones, y flujo post-envio

**Dependencias:** US-SP-036, US-SP-049 (TransferFormComponent), EP-SP-004 (API SPEI out)
**Estimacion:** 4 dev-days

---

#### US-SP-038: Formulario de Movimiento Interno (B2B)

**ID:** US-SP-038
**Epica:** EP-SP-011
**Prioridad:** P0

**Historia:**
Como **Cliente Empresarial** quiero mover dinero entre mis cuentas de forma rapida para gestionar mi flujo de fondos internamente.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/business/transfers/internal`
- [ ] Formulario simplificado (no wizard, todo en 1 paso):
  - Cuenta origen: dropdown filtrado por tipo (solo las que pueden enviar internamente)
  - Cuenta destino: dropdown filtrado por reglas del grafo (solo destinos validos para el tipo de origen seleccionado)
  - Monto: validado contra saldo disponible
  - Concepto: opcional
- [ ] Al seleccionar cuenta origen, la lista de destinos se filtra automaticamente:
  - CONCENTRADORA seleccionada -> destinos: CLABE, DISPERSION, RESERVADA
  - CLABE seleccionada -> destinos: CONCENTRADORA, RESERVADA
  - DISPERSION seleccionada -> destinos: CONCENTRADORA
  - RESERVADA -> no puede ser origen (bloqueado)
- [ ] Preview visual: "Mover $X de [Cuenta A] a [Cuenta B]" con iconos de tipo
- [ ] Operacion instantanea: feedback inmediato de exito/error
- [ ] Sin comision (indicar "$0 comision" visualmente)
- [ ] Acceso rapido desde detalle de cuenta (boton "Mover fondos" pre-selecciona origen)

**Tareas Tecnicas:**
1. Crear `BusinessInternalTransferComponent` (page)
2. Implementar logica de filtrado de destinos por reglas del grafo
3. Validaciones reactivas con FormGroup
4. Preview visual con iconos por tipo
5. Integrar con TransfersAdapter
6. Tests del filtrado, validaciones, y flujo

**Dependencias:** US-SP-036, US-SP-028, EP-SP-006 (API internos)
**Estimacion:** 3 dev-days

---

#### US-SP-039: Gestion de Estructura de Cuentas (B2B)

**ID:** US-SP-039
**Epica:** EP-SP-011
**Prioridad:** P1

**Historia:**
Como **Cliente Empresarial** quiero crear y gestionar la estructura de mis cuentas (sub-cuentas) para organizar mis fondos segun mis necesidades operativas.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/business/accounts` - Lista de cuentas (reutiliza componente de dashboard)
- [ ] Pagina `/sp/business/accounts/new` - Wizard de creacion:
  - Paso 1: Tipo de cuenta (CLABE, DISPERSION, RESERVADA) con descripcion de cada tipo
  - Paso 2: Datos (nombre, cuenta padre, destino fijo si RESERVADA)
  - Paso 3: Confirmacion con resumen
  - Si tipo CLABE: indicar que se generara CLABE automaticamente (Monato)
- [ ] Pagina `/sp/business/accounts/:id` - Detalle de cuenta:
  - Reutiliza `AccountDetailCardComponent` de EP-SP-013
  - Informacion completa: nombre, tipo, CLABE, estado, saldo, padre
  - Ultimos movimientos (reutiliza MovementsTableComponent)
  - Cuentas hijas (si es CONCENTRADORA)
  - Acciones: "Transferir SPEI", "Mover fondos", "Congelar" (solo admin de org)
  - Grafica de saldo ultimos 30 dias
- [ ] Pagina `/sp/business/accounts/tree` - Arbol de cuentas de la org:
  - Reutiliza `AccountTreeComponent` de EP-SP-013 con modo "single org"
- [ ] No se puede crear CONCENTRADORA (solo admin de plataforma)
- [ ] Validacion de jerarquia al crear (padre valido segun tipo)

**Tareas Tecnicas:**
1. Crear `AccountsListPageComponent` (page)
2. Crear `AccountCreationWizardComponent` (wizard 3 pasos)
3. Crear `AccountDetailPageComponent` (page con tabs)
4. Crear `BusinessAccountTreeComponent` (wrapper del shared)
5. Integrar con AccountsAdapter
6. Tests del wizard, validaciones de jerarquia, y detalle

**Dependencias:** US-SP-036, US-SP-048 (AccountTreeComponent), US-SP-050 (AccountDetailCard), EP-SP-001 (API)
**Estimacion:** 5 dev-days

---

#### US-SP-040: Historial de Movimientos (B2B)

**ID:** US-SP-040
**Epica:** EP-SP-011
**Prioridad:** P0

**Historia:**
Como **Cliente Empresarial** quiero ver el historial completo de movimientos de mis cuentas para tener control de todas las operaciones financieras.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/business/movements`
- [ ] Reutiliza `MovementsTableComponent` de EP-SP-013 con config B2B:
  - Columnas visibles: Fecha/Hora, Tipo, Cuenta, Concepto, Referencia, Monto (+/-), Saldo resultante, Estado
  - Muestra todas las cuentas de la org
- [ ] Filtros:
  - Cuenta (dropdown de cuentas de la org o "Todas")
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
1. Crear `BusinessMovementsPageComponent` (page, wrapper)
2. Integrar `MovementsTableComponent` de EP-SP-013 con config B2B
3. Crear `MovementDetailDrawerComponent`
4. Implementar export CSV/PDF
5. Integrar con LedgerAdapter (statement endpoint)
6. Tests de filtros, paginacion, y export

**Dependencias:** US-SP-036, US-SP-047 (MovementsTableComponent), US-SP-028 (adapters)
**Estimacion:** 4 dev-days

---

#### US-SP-041: Gestion de Usuarios Finales B2C (desde B2B)

**ID:** US-SP-041
**Epica:** EP-SP-011
**Prioridad:** P1

**Historia:**
Como **Cliente Empresarial** quiero gestionar los usuarios finales (personas naturales) que son mis clientes para poder crearles cuentas privadas con CLABE y monitorear su actividad.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/business/users`
- [ ] Tabla de usuarios finales de la organizacion:
  - Nombre completo
  - Email
  - Telefono
  - CLABE asignada
  - Saldo de su cuenta
  - Estado (activo, inactivo)
  - Fecha de registro
- [ ] Busqueda por nombre, email, o CLABE
- [ ] Paginacion server-side
- [ ] Boton "Agregar usuario":
  - Formulario: nombre, email, telefono
  - Al crear: genera cuenta privada + CLABE automaticamente
  - Muestra la CLABE generada con boton de copiar
- [ ] Click en usuario -> detalle:
  - Info personal
  - Su cuenta y saldo
  - Historial de movimientos (ultimos 20)
  - Acciones: suspender, reactivar
- [ ] Solo se ven usuarios de la organizacion del usuario actual (scoped)

**Tareas Tecnicas:**
1. Crear `BusinessUsersPageComponent` (page)
2. Crear `UsersTableComponent`
3. Crear `CreateUserModalComponent`
4. Crear `UserDetailComponent`
5. Crear `UsersAdapter` (o extender AccountsAdapter para user-level accounts)
6. Tests

**Dependencias:** US-SP-036, US-SP-028
**Estimacion:** 4 dev-days

---

#### US-SP-042: Panel de Aprobaciones y Configuracion (B2B)

**ID:** US-SP-042
**Epica:** EP-SP-011
**Prioridad:** P1

**Historia:**
Como **Cliente Empresarial** quiero aprobar o rechazar transferencias que superan mi umbral configurado y ajustar la configuracion de mi organizacion para mantener control sobre las operaciones financieras.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/business/approvals`:
  - Lista de transferencias pendientes de aprobacion
  - Detalle de cada transferencia: origen, destino, monto, concepto, solicitante, fecha
  - Acciones: Aprobar (con comentario opcional), Rechazar (con motivo obligatorio)
  - Notificacion visual cuando hay aprobaciones pendientes (badge en sidebar)
  - Historial de aprobaciones pasadas (aprobadas + rechazadas)
- [ ] Pagina `/sp/business/settings`:
  - **Limites**: ver y solicitar cambio de limites (el cambio lo aplica admin)
  - **Beneficiarios**: lista de beneficiarios frecuentes con CRUD
  - **Notificaciones**: preferencias (email, in-app) por tipo de evento
  - **Umbral de aprobacion**: configurar monto a partir del cual se requiere aprobacion (solo admin de org)
  - **Usuarios**: invitar/eliminar usuarios de la org (solo admin de org)
- [ ] Pagina `/sp/business/beneficiaries`:
  - Lista de beneficiarios guardados
  - Boton "Agregar beneficiario" con validacion de CLABE
  - Penny validation antes de guardar (si habilitado)
  - Eliminar beneficiario con confirmacion

**Tareas Tecnicas:**
1. Crear `ApprovalsPageComponent` (page)
2. Crear `ApprovalCardComponent` (detalle de cada pendiente)
3. Crear `BusinessSettingsPageComponent` (page con tabs)
4. Crear `BeneficiariesPageComponent` (page)
5. Crear `AddBeneficiaryModalComponent`
6. Integrar con TransfersAdapter (approve/reject endpoints)
7. Integrar con BeneficiariesAdapter
8. Tests de aprobacion, rechazo, y CRUD de beneficiarios

**Dependencias:** US-SP-036, US-SP-028, EP-SP-010 (API politicas), EP-SP-004 (API approve/reject)
**Estimacion:** 5 dev-days

---

### EP-SP-012: Portal Usuario Final B2C (Tier 3)

---

#### US-SP-043: Dashboard Personal (Mi Cuenta)

**ID:** US-SP-043
**Epica:** EP-SP-012
**Prioridad:** P0

**Historia:**
Como **Persona Natural** quiero ver el saldo de mi cuenta y los datos de mi CLABE para saber cuanto dinero tengo y poder compartir mi CLABE para recibir depositos.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/personal/dashboard`
- [ ] Seccion prominente de saldo:
  - Saldo disponible en grande ($X,XXX.XX)
  - Saldo pendiente (si hay, en texto menor)
  - Moneda (MXN)
  - Ultima actualizacion (timestamp)
- [ ] Seccion de CLABE:
  - CLABE completa con formato visual (XXX-XXX-XXXXXXXXX-X)
  - Boton "Copiar CLABE" con feedback visual ("Copiado!")
  - Nombre del banco (auto-detectado por primeros digitos de CLABE)
  - Texto: "Comparte esta CLABE para recibir depositos SPEI"
- [ ] Seccion de ultimos movimientos (5 mas recientes):
  - Fecha, concepto, monto (+/-), tipo (deposito/retiro)
  - Link "Ver todos" -> `/sp/personal/movements`
- [ ] Acciones rapidas (si habilitado):
  - "Enviar dinero" -> `/sp/personal/transfer`
- [ ] Info de la cuenta:
  - Tipo de cuenta: "Cuenta Personal"
  - Estado: badge (Activa)
  - Empresa (si es cliente de empresa): "Tu cuenta es gestionada por Boxito"
- [ ] Mobile-first: optimizado para pantalla de telefono
- [ ] Skeleton loaders
- [ ] OnPush + Signals

**Tareas Tecnicas:**
1. Crear `PersonalDashboardComponent` (page)
2. Crear `BalanceDisplayComponent` (saldo prominente)
3. Crear `ClabeDisplayComponent` (CLABE con copy)
4. Crear `RecentMovementsComponent` (ultimos 5)
5. Integrar con AccountsAdapter (scoped a la cuenta del usuario)
6. Tests de renderizado y copy-to-clipboard

**Dependencias:** US-SP-025, US-SP-026, US-SP-027 (scaffold), US-SP-028 (adapters), EP-SP-001 (API)
**Estimacion:** 3 dev-days

---

#### US-SP-044: Historial de Movimientos Personal

**ID:** US-SP-044
**Epica:** EP-SP-012
**Prioridad:** P0

**Historia:**
Como **Persona Natural** quiero ver el historial completo de mis movimientos para saber que depositos he recibido y que retiros se han hecho.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/personal/movements`
- [ ] Reutiliza `MovementsTableComponent` de EP-SP-013 con config Personal:
  - Columnas visibles: Fecha, Concepto, Monto, Estado (columnas simplificadas vs B2B)
  - Solo muestra movimientos de la cuenta del usuario
  - No muestra columna "Cuenta" (solo tiene una)
- [ ] Filtros simplificados:
  - Tipo: Depositos / Retiros / Todos
  - Rango de fechas (presets: Hoy, Esta semana, Este mes, Personalizado)
- [ ] Paginacion (20 por pagina)
- [ ] Colores: verde para depositos (entradas), rojo para retiros (salidas)
- [ ] Click en movimiento -> detalle:
  - Tipo de operacion
  - Monto
  - Concepto
  - Referencia bancaria
  - Banco origen/destino
  - Fecha y hora exacta
  - Estado
- [ ] Mobile-first con lista de cards en lugar de tabla
- [ ] Subtotales del periodo: total depositos, total retiros, neto

**Tareas Tecnicas:**
1. Crear `PersonalMovementsPageComponent` (page, wrapper)
2. Integrar `MovementsTableComponent` con config minimal
3. Crear `MovementDetailModalComponent` (modal en lugar de drawer para mobile)
4. Implementar vista de cards para mobile
5. Tests

**Dependencias:** US-SP-043, US-SP-047 (MovementsTableComponent)
**Estimacion:** 3 dev-days

---

#### US-SP-045: Transferencia SPEI Personal (Si Habilitado)

**ID:** US-SP-045
**Epica:** EP-SP-012
**Prioridad:** P1

**Historia:**
Como **Persona Natural** quiero enviar dinero a otra cuenta bancaria via SPEI (si mi empresa o SuperPago me lo permite) para poder hacer pagos desde mi cuenta.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/personal/transfer`
- [ ] **Condicional**: solo accesible si la politica de la organizacion permite transferencias B2C:
  - Si no permitido: pagina muestra mensaje "Las transferencias no estan habilitadas para tu cuenta. Contacta a [nombre empresa] para mas informacion."
  - Si permitido: muestra formulario
- [ ] Reutiliza `TransferFormComponent` de EP-SP-013 con config Personal:
  - Modo: `personal` (no muestra selector de cuenta origen, usa la unica cuenta)
  - Formulario simplificado (no wizard, 1 paso):
    - CLABE destino
    - Nombre del titular
    - Monto (con validacion de saldo)
    - Concepto
  - Confirmacion en modal (no paso separado)
  - Monto maximo limitado por politica de la org
- [ ] Despues de enviar:
  - Resultado inmediato (exito/error)
  - Clave de rastreo
  - Redirige a dashboard
- [ ] Limites visibles: "Puedes enviar hasta $X por transferencia, $Y por dia"

**Tareas Tecnicas:**
1. Crear `PersonalTransferPageComponent` (page, wrapper)
2. Integrar `TransferFormComponent` con config minimal
3. Verificacion de politica de org (puede transferir si/no)
4. Mostrar limites del usuario
5. Tests de condicionalidad, validaciones, y flujo

**Dependencias:** US-SP-043, US-SP-049 (TransferFormComponent), EP-SP-004 (API SPEI out), EP-SP-010 (API politicas)
**Estimacion:** 3 dev-days

---

#### US-SP-046: Informacion de Cuenta Personal

**ID:** US-SP-046
**Epica:** EP-SP-012
**Prioridad:** P2

**Historia:**
Como **Persona Natural** quiero ver la informacion completa de mi cuenta para conocer los detalles de mi relacion con SuperPago o con la empresa que gestiona mi cuenta.

**Criterios de Aceptacion:**
- [ ] Pagina `/sp/personal/account`
- [ ] Informacion de la cuenta:
  - Tipo: "Cuenta Personal SPEI"
  - CLABE (con boton copiar)
  - Estado (Activa/Pendiente/Congelada)
  - Fecha de apertura
  - Moneda: MXN
- [ ] Informacion de la organizacion/empresa (si aplica):
  - Nombre de la empresa: "Tu cuenta es gestionada por Boxito"
  - Contacto de soporte de la empresa
- [ ] Limites de la cuenta:
  - Monto maximo por transferencia
  - Monto maximo diario
  - Operaciones maximas por dia
  - "Estos limites son configurados por [empresa/SuperPago]"
- [ ] Informacion del titular:
  - Nombre
  - Email
  - Telefono
- [ ] Notificaciones (preferencias):
  - Notificarme depositos: si/no
  - Notificarme retiros: si/no
  - Canal: email, push, ambos
- [ ] Mobile-first

**Tareas Tecnicas:**
1. Crear `PersonalAccountInfoComponent` (page)
2. Crear `AccountInfoSectionComponent`
3. Crear `OrganizationInfoSectionComponent`
4. Crear `LimitsInfoSectionComponent`
5. Crear `NotificationPreferencesComponent`
6. Integrar con AccountsAdapter y configuracion de org
7. Tests

**Dependencias:** US-SP-043, US-SP-028
**Estimacion:** 2 dev-days

---

### EP-SP-013: Componentes Compartidos entre Tiers

---

#### US-SP-047: MovementsTableComponent (Tabla de Movimientos Compartida)

**ID:** US-SP-047
**Epica:** EP-SP-013
**Prioridad:** P0

**Historia:**
Como **Desarrollador** quiero un componente de tabla de movimientos reutilizable y configurable para usarlo en los 3 portales con diferentes niveles de detalle.

**Criterios de Aceptacion:**
- [ ] Componente `MovementsTableComponent` en `presentation/shared/components/`
- [ ] Inputs configurables:
  ```typescript
  @Input() movements: Signal<LedgerEntry[]>;        // Datos
  @Input() columns: Signal<MovementColumn[]>;        // Columnas visibles
  @Input() tierMode: Signal<'admin' | 'business' | 'personal'>; // Modo de visualizacion
  @Input() showFilters: Signal<boolean>;             // Mostrar/ocultar filtros
  @Input() showExport: Signal<boolean>;              // Mostrar/ocultar export
  @Input() showSubtotals: Signal<boolean>;           // Mostrar/ocultar subtotales
  @Input() pageSize: Signal<number>;                 // Items por pagina
  @Input() loading: Signal<boolean>;                 // Estado de carga
  ```
- [ ] Outputs:
  ```typescript
  @Output() filterChange: EventEmitter<MovementFilters>;
  @Output() pageChange: EventEmitter<PageEvent>;
  @Output() movementClick: EventEmitter<LedgerEntry>;
  @Output() exportRequest: EventEmitter<'csv' | 'pdf'>;
  ```
- [ ] Columnas disponibles (configurables por tier):
  - `date`: Fecha/Hora
  - `type`: Tipo de movimiento (SPEI In, SPEI Out, Interno, Comision, etc.)
  - `account`: Cuenta afectada (oculta en personal)
  - `counterpart`: Cuenta contraparte
  - `concept`: Concepto
  - `reference`: Referencia bancaria
  - `amount`: Monto (+/- con color)
  - `balance`: Saldo resultante
  - `status`: Estado (badge)
  - `organization`: Organizacion (solo admin)
- [ ] Configuracion predefinida por tier:
  - Admin: todas las columnas
  - Business: sin "organization"
  - Personal: solo date, concept, amount, status
- [ ] Monto con formato: +$1,234.56 (verde) / -$1,234.56 (rojo)
- [ ] Estado con badge de color: Completado (verde), Pendiente (amarillo), Fallido (rojo)
- [ ] Skeleton loader para filas mientras carga
- [ ] Empty state: "No hay movimientos" con icono
- [ ] Mobile: vista de cards en lugar de tabla cuando ancho < 768px
- [ ] OnPush change detection
- [ ] Data attribute `data-cy` para E2E

**Tareas Tecnicas:**
1. Crear `MovementsTableComponent` con Inputs/Outputs
2. Crear `MovementRowComponent` (sub-componente para fila)
3. Crear `MovementCardComponent` (sub-componente mobile)
4. Crear `MovementFiltersComponent` (sub-componente de filtros)
5. Crear `MovementSubtotalsComponent` (sub-componente de totales)
6. Barrel export en `shared/components/index.ts`
7. Tests con diferentes configuraciones de tier

**Dependencias:** US-SP-025 (scaffold), US-SP-028 (modelos)
**Estimacion:** 5 dev-days

---

#### US-SP-048: AccountTreeComponent (Grafo de Cuentas Compartido)

**ID:** US-SP-048
**Epica:** EP-SP-013
**Prioridad:** P1

**Historia:**
Como **Desarrollador** quiero un componente de arbol/grafo de cuentas reutilizable para visualizar la jerarquia de cuentas en admin (ecosistema completo) y en business (solo mi organizacion).

**Criterios de Aceptacion:**
- [ ] Componente `AccountTreeComponent` en `presentation/shared/components/`
- [ ] Inputs:
  ```typescript
  @Input() tree: Signal<AccountTreeNode[]>;    // Datos del arbol
  @Input() mode: Signal<'full' | 'org'>;       // Ecosistema completo vs org unica
  @Input() interactive: Signal<boolean>;        // Click/hover habilitado
  @Input() showBalances: Signal<boolean>;       // Mostrar saldos en nodos
  @Input() selectedNodeId: Signal<string | null>; // Nodo seleccionado
  @Input() highlightTypes: Signal<string[]>;    // Tipos a resaltar
  ```
- [ ] Outputs:
  ```typescript
  @Output() nodeClick: EventEmitter<FinancialAccount>;
  @Output() nodeHover: EventEmitter<FinancialAccount | null>;
  ```
- [ ] Visualizacion:
  - Nodos como rectangulos redondeados con:
    - Icono por tipo de cuenta
    - Nombre de la cuenta
    - Tipo (label)
    - Saldo (si showBalances)
    - Estado (opacidad reducida para frozen/closed)
  - Lineas de conexion padre-hijo con SVG
  - Color por tipo:
    - Concentradora: azul (#2563EB)
    - CLABE: verde (#16A34A)
    - Dispersion: naranja (#EA580C)
    - Reservada: gris (#6B7280)
  - Agrupacion por organizacion (en modo `full`)
- [ ] Interactividad:
  - Click en nodo -> emite evento `nodeClick`
  - Hover -> tooltip con info rapida
  - Zoom (scroll wheel) y pan (drag)
  - Expandir/colapsar ramas (click en icono +/-)
  - Buscar cuenta (campo de texto que resalta coincidencias)
- [ ] Layouts:
  - Vertical (top-down, default)
  - Horizontal (left-right)
- [ ] Implementado con CSS Grid + SVG nativo (sin libreria externa pesada)
- [ ] OnPush + Signals
- [ ] Responsive: scroll horizontal en mobile

**Tareas Tecnicas:**
1. Crear `AccountTreeComponent` (contenedor principal con SVG)
2. Crear `TreeNodeComponent` (nodo individual)
3. Crear `TreeConnectorComponent` (lineas SVG)
4. Implementar logica de layout automatico (calculo de posiciones)
5. Implementar zoom y pan con gestos
6. Implementar expand/collapse
7. Implementar busqueda con highlight
8. Tests de renderizado con diferentes arboles
9. Tests de interactividad

**Dependencias:** US-SP-025, US-SP-028 (modelos)
**Estimacion:** 5 dev-days

---

#### US-SP-049: TransferFormComponent (Formulario de Transferencia SPEI Compartido)

**ID:** US-SP-049
**Epica:** EP-SP-013
**Prioridad:** P0

**Historia:**
Como **Desarrollador** quiero un componente de formulario de transferencia SPEI reutilizable y configurable para usarlo en el portal B2B (wizard completo) y B2C (formulario simplificado).

**Criterios de Aceptacion:**
- [ ] Componente `TransferFormComponent` en `presentation/shared/components/`
- [ ] Inputs:
  ```typescript
  @Input() mode: Signal<'business' | 'personal'>;
  @Input() accounts: Signal<FinancialAccount[]>;      // Cuentas origen disponibles
  @Input() beneficiaries: Signal<Beneficiary[]>;       // Beneficiarios guardados
  @Input() participants: Signal<SPEIParticipant[]>;    // Catalogo de bancos
  @Input() commissionPreview: Signal<CommissionPreview | null>;
  @Input() fixedSourceAccount: Signal<FinancialAccount | null>; // Para personal (cuenta unica)
  @Input() maxAmount: Signal<number | null>;           // Limite maximo
  ```
- [ ] Outputs:
  ```typescript
  @Output() submit: EventEmitter<TransferRequest>;
  @Output() commissionRequest: EventEmitter<{ sourceId: string; amount: number }>;
  @Output() saveBeneficiary: EventEmitter<Beneficiary>;
  ```
- [ ] Modo `business` (wizard 3 pasos):
  1. **Seleccionar origen**: dropdown de cuentas, saldo visible
  2. **Datos destino**:
     - Beneficiario guardado (dropdown, autocompletar) O manual
     - CLABE destino (18 digitos, validacion de formato y checksum)
     - Banco (auto-detectado por primeros 3 digitos de CLABE con catalogo)
     - Nombre del titular
     - Concepto (requerido, max 40 chars)
     - Referencia numerica (opcional, max 7 digitos)
  3. **Confirmar**:
     - Resumen de la operacion
     - Monto
     - Comision (con desglose IVA)
     - Total a debitar
     - Boton "Enviar transferencia"
- [ ] Modo `personal` (formulario simple, 1 paso):
  - No muestra selector de cuenta (usa fixedSourceAccount)
  - CLABE, titular, monto, concepto en un solo formulario
  - Confirmacion en modal
- [ ] Validaciones en tiempo real:
  - CLABE: formato 18 digitos + algoritmo de checksum
  - Monto: > 0, <= saldo disponible - comision, <= maxAmount
  - Concepto: requerido, 1-40 caracteres alfanumericos
  - Referencia: numerico, 0-7 digitos
- [ ] Auto-deteccion de banco: al escribir 3+ digitos de CLABE, muestra nombre del banco
- [ ] OnPush + Signals
- [ ] Accesibilidad: labels, aria, tab order

**Tareas Tecnicas:**
1. Crear `TransferFormComponent` (contenedor)
2. Crear `TransferStep1Component` (seleccion de origen)
3. Crear `TransferStep2Component` (datos destino)
4. Crear `TransferStep3Component` (confirmacion)
5. Crear `ClabeInputComponent` (input especializado con validacion y bank detection)
6. Crear `CommissionPreviewComponent` (desglose de comision)
7. Implementar validacion de CLABE (checksum)
8. Integrar con catalogo de participantes para bank auto-detect
9. Tests del wizard, validaciones, y ambos modos

**Dependencias:** US-SP-025, US-SP-028 (modelos y adapters)
**Estimacion:** 5 dev-days

---

#### US-SP-050: AccountDetailCardComponent (Detalle de Cuenta Compartido)

**ID:** US-SP-050
**Epica:** EP-SP-013
**Prioridad:** P0

**Historia:**
Como **Desarrollador** quiero un componente de detalle de cuenta reutilizable que muestre informacion de una cuenta con nivel de detalle configurable por tier.

**Criterios de Aceptacion:**
- [ ] Componente `AccountDetailCardComponent` en `presentation/shared/components/`
- [ ] Inputs:
  ```typescript
  @Input() account: Signal<FinancialAccount>;
  @Input() tier: Signal<'admin' | 'business' | 'personal'>;
  @Input() showActions: Signal<boolean>;
  @Input() showBalance: Signal<boolean>;
  @Input() showChildren: Signal<boolean>;
  @Input() compact: Signal<boolean>;  // Modo compacto para listas
  ```
- [ ] Outputs:
  ```typescript
  @Output() transferClick: EventEmitter<FinancialAccount>;
  @Output() moveClick: EventEmitter<FinancialAccount>;
  @Output() detailClick: EventEmitter<FinancialAccount>;
  @Output() freezeClick: EventEmitter<FinancialAccount>;
  ```
- [ ] Informacion mostrada:
  - **Siempre**: nombre, tipo (con icono y color), estado (badge)
  - **Si CLABE**: CLABE con boton copiar
  - **Si showBalance**: saldo disponible (prominente), saldo pendiente
  - **Si showChildren**: numero de cuentas hijas
  - **Admin extra**: organization_id, provider_account_id, created_by
  - **Compact mode**: fila horizontal en lugar de card
- [ ] Tipo con icono visual:
  - Concentradora: icono de banco + fondo azul
  - CLABE: icono de tarjeta + fondo verde
  - Dispersion: icono de flechas + fondo naranja
  - Reservada: icono de candado + fondo gris
- [ ] Estado con badge:
  - ACTIVE: verde
  - PENDING: amarillo
  - FROZEN: azul hielo
  - CLOSED: gris
- [ ] Acciones (si showActions):
  - "Transferir SPEI" (solo si CLABE o DISPERSION activa)
  - "Mover fondos" (solo si tipo permite internos)
  - "Ver detalle" (siempre)
  - "Congelar/Descongelar" (solo admin o admin de org)
- [ ] OnPush + Signals
- [ ] Accesibilidad: roles, aria-label

**Tareas Tecnicas:**
1. Crear `AccountDetailCardComponent` con variantes por tier
2. Crear `AccountTypeBadgeComponent` (icono + color por tipo)
3. Crear `AccountStatusBadgeComponent` (badge de estado)
4. Crear `ClabeDisplayComponent` (CLABE con copy button) - reutilizable tambien en Tier 3
5. Tests con diferentes configuraciones de tier y tipo de cuenta

**Dependencias:** US-SP-025, US-SP-028 (modelos)
**Estimacion:** 3 dev-days

---

#### US-SP-051: TransferStatusTrackerComponent (Estado en Tiempo Real)

**ID:** US-SP-051
**Epica:** EP-SP-013
**Prioridad:** P1

**Historia:**
Como **Desarrollador** quiero un componente que muestre el estado de una transferencia en tiempo real para usarlo despues de enviar una transferencia en cualquier tier.

**Criterios de Aceptacion:**
- [ ] Componente `TransferStatusTrackerComponent` en `presentation/shared/components/`
- [ ] Inputs:
  ```typescript
  @Input() transferId: Signal<string>;
  @Input() autoRefresh: Signal<boolean>;    // default: true
  @Input() refreshInterval: Signal<number>; // default: 5000ms
  ```
- [ ] Outputs:
  ```typescript
  @Output() statusChange: EventEmitter<Transfer>;
  @Output() completed: EventEmitter<Transfer>;
  @Output() failed: EventEmitter<Transfer>;
  ```
- [ ] Visualizacion de progreso (stepper horizontal):
  ```
  [Creada] --> [Procesando] --> [Completada]
     O                             O
     +---> [Aprobacion] --+       [Fallida]
  ```
  - Cada paso con icono, label, y timestamp (si ya ocurrio)
  - Paso actual pulsante/animado
  - Paso completado con checkmark verde
  - Paso fallido con X roja
- [ ] Estados mapeados:
  - PENDING: "Transferencia creada, validando..."
  - PENDING_APPROVAL: "Esperando aprobacion" (con quien debe aprobar)
  - PROCESSING: "Enviando via SPEI..." (con spinner)
  - COMPLETED: "Transferencia completada" (con clave de rastreo)
  - FAILED: "Transferencia fallida" (con motivo del error)
  - REJECTED: "Transferencia rechazada" (con motivo)
  - REVERSED: "Transferencia reversada"
- [ ] Polling automatico cada `refreshInterval` ms mientras status es PENDING/PROCESSING
- [ ] Detiene polling cuando status es terminal (COMPLETED, FAILED, REJECTED, REVERSED)
- [ ] Toast notification al cambiar de estado
- [ ] Informacion de la transferencia:
  - Monto
  - Origen -> Destino
  - Concepto
  - Clave de rastreo (cuando disponible)
  - Timestamp de cada cambio de estado
- [ ] OnPush + Signals
- [ ] Cleanup del polling en OnDestroy

**Tareas Tecnicas:**
1. Crear `TransferStatusTrackerComponent` con stepper visual
2. Implementar polling con RxJS timer + switchMap + takeUntil
3. Crear `StatusStepComponent` (sub-componente para cada paso)
4. Crear `TransferSummaryComponent` (resumen de la transferencia)
5. Integrar con TransfersAdapter (GET transfer by id)
6. Tests de polling, estados, y cleanup

**Dependencias:** US-SP-025, US-SP-028 (modelos y adapters)
**Estimacion:** 3 dev-days

---

## Roadmap Frontend

### Roadmap Visual

```
Semana 2-3:  [EP-SP-007 Scaffold + Multi-Tier Architecture              ]
                    |
Semana 3-4:  [EP-SP-013 Componentes Compartidos                         ]
                    |                    |                    |
Semana 3-4:  [EP-SP-008 Portal Admin T1 (parcial)           ]
                    |                    |
Semana 4-5:  [EP-SP-008 Portal Admin T1 (completo)  ]  [EP-SP-011 Portal B2B T2                  ]
                                                              |
Semana 5:    [EP-SP-011 Portal B2B (completo)       ]  [EP-SP-012 Portal B2C T3                   ]
                                                              |
Semana 5-6:  [EP-SP-012 Portal B2C (completo)       ]  [Polish + Edge Cases                      ]
```

### Fase Frontend 1: Fundamentos (Semanas 2-3)

**Objetivo:** Scaffold del MF con routing multi-tier, layouts, modelos y adapters. Todo listo para construir paginas.

| Orden | Epica | User Stories | Razon |
|-------|-------|-------------|-------|
| F1a | EP-SP-007 | US-SP-025 (scaffold) | Base del MF, sin esto no hay nada |
| F1b | EP-SP-007 | US-SP-026 (routing + guards) | Estructura de 3 portales |
| F1c | EP-SP-007 | US-SP-027 (layouts) | Cada portal necesita su layout |
| F1d | EP-SP-007 | US-SP-028 (modelos + adapters) | Conexion con APIs backend |

**Criterio de salida:**
- mf-sp carga en el Shell
- 3 rutas base accesibles con guards funcionales
- 3 layouts renderizando con sidebar
- Todos los modelos y adapters definidos y testeados
- Redirect inteligente por tier funciona

**Riesgo:** Deteccion de tier depende de que los permisos esten definidos en el backend.

---

### Fase Frontend 2: Componentes Compartidos + Admin Inicial (Semanas 3-4)

**Objetivo:** Componentes reutilizables listos, primeras paginas del admin.

| Orden | Epica | User Stories | Razon |
|-------|-------|-------------|-------|
| F2a | EP-SP-013 | US-SP-047 (MovementsTable) | Usado en los 3 portales |
| F2b | EP-SP-013 | US-SP-049 (TransferForm) | Usado en B2B y B2C |
| F2c | EP-SP-013 | US-SP-050 (AccountDetailCard) | Usado en los 3 portales |
| F2d | EP-SP-008 | US-SP-029 (Admin Dashboard) | Primera pagina funcional |
| F2e | EP-SP-008 | US-SP-030 (Organizaciones) | Vista de todos los clientes |

**Criterio de salida:**
- 3 componentes compartidos funcionales y testeados
- Dashboard admin muestra KPIs y lista de orgs
- Vista de detalle de organizacion funcional

---

### Fase Frontend 3: Admin Completo + B2B Core (Semanas 4-5)

**Objetivo:** Admin operativo, portal B2B con funcionalidades core.

| Orden | Epica | User Stories | Razon |
|-------|-------|-------------|-------|
| F3a | EP-SP-013 | US-SP-048 (AccountTree) | Necesario para admin y B2B |
| F3b | EP-SP-013 | US-SP-051 (TransferStatusTracker) | Necesario para B2B y B2C |
| F3c | EP-SP-008 | US-SP-031 (Grafo ecosistema) | Admin: vista completa |
| F3d | EP-SP-008 | US-SP-032 (Monitoreo proveedores) | Admin: observabilidad |
| F3e | EP-SP-008 | US-SP-033 (Reconciliacion) | Admin: integridad financiera |
| F3f | EP-SP-008 | US-SP-034 (Audit trail) | Admin: compliance |
| F3g | EP-SP-011 | US-SP-036 (B2B Dashboard) | B2B: pagina principal |
| F3h | EP-SP-011 | US-SP-037 (B2B SPEI out) | B2B: operacion core |
| F3i | EP-SP-011 | US-SP-038 (B2B internos) | B2B: movimientos internos |

**Criterio de salida:**
- Admin 100% funcional (excepto politicas que son P2)
- B2B puede ver cuentas, hacer SPEI out, y mover fondos internos
- Grafo de cuentas visual y funcional

---

### Fase Frontend 4: B2B Completo + B2C (Semana 5)

**Objetivo:** Portal B2B completo, portal B2C funcional.

| Orden | Epica | User Stories | Razon |
|-------|-------|-------------|-------|
| F4a | EP-SP-011 | US-SP-039 (B2B estructura cuentas) | B2B: gestion de cuentas |
| F4b | EP-SP-011 | US-SP-040 (B2B historial) | B2B: movimientos |
| F4c | EP-SP-011 | US-SP-041 (B2B usuarios B2C) | B2B: gestion de sus clientes |
| F4d | EP-SP-011 | US-SP-042 (B2B aprobaciones + config) | B2B: control |
| F4e | EP-SP-012 | US-SP-043 (B2C dashboard) | B2C: pagina principal |
| F4f | EP-SP-012 | US-SP-044 (B2C movimientos) | B2C: historial |

**Criterio de salida:**
- B2B 100% funcional
- B2C dashboard y movimientos funcionales

---

### Fase Frontend 5: B2C Completo + Polish (Semanas 5-6)

**Objetivo:** Todo funcional, edge cases resueltos, listo para produccion.

| Orden | Epica | User Stories | Razon |
|-------|-------|-------------|-------|
| F5a | EP-SP-012 | US-SP-045 (B2C transferencia) | B2C: transferencia condicional |
| F5b | EP-SP-012 | US-SP-046 (B2C info cuenta) | B2C: informacion |
| F5c | EP-SP-008 | US-SP-035 (Admin politicas + alertas) | Admin: P2 features |
| F5d | -- | Polish, edge cases, a11y, mobile testing | Calidad final |

**Criterio de salida:**
- Los 3 portales 100% funcionales
- Todos los tests pasan con >= 98% coverage
- Build de produccion exitoso
- Responsive verificado en mobile/tablet/desktop
- E2E smoke tests pasando

---

### MVP Frontend

El MVP frontend se alcanza al completar **Fases F1-F3**, que incluye:

| Capacidad | User Stories |
|-----------|-------------|
| Scaffold MF con 3 portales | US-SP-025, US-SP-026, US-SP-027, US-SP-028 |
| Componentes compartidos core | US-SP-047, US-SP-049, US-SP-050 |
| Admin Dashboard + Orgs | US-SP-029, US-SP-030 |
| B2B Dashboard + Transferencias | US-SP-036, US-SP-037, US-SP-038 |

**Estimacion MVP Frontend:** ~3 semanas con 1 desarrollador frontend

---

## Grafo de Dependencias Frontend

```
US-SP-025 (Scaffold mf-sp)
  |
  +-> US-SP-026 (Routing + Guards)
  |     |
  |     +-> US-SP-027 (Layouts por Tier)
  |
  +-> US-SP-028 (Modelos + Adapters)
  |
  +-> US-SP-047 (MovementsTable shared) ----> US-SP-040 (B2B Historial)
  |                                     |---> US-SP-044 (B2C Movimientos)
  |
  +-> US-SP-049 (TransferForm shared) ------> US-SP-037 (B2B SPEI out)
  |                                     |---> US-SP-045 (B2C Transfer)
  |
  +-> US-SP-050 (AccountDetailCard shared) -> US-SP-036 (B2B Dashboard)
  |                                     |---> US-SP-039 (B2B Estructura)
  |                                     |---> US-SP-043 (B2C Dashboard)
  |
  +-> US-SP-048 (AccountTree shared) -------> US-SP-031 (Admin Grafo)
  |                                     |---> US-SP-039 (B2B Arbol)
  |
  +-> US-SP-051 (TransferStatusTracker) ----> US-SP-037 (B2B SPEI out)
                                        |---> US-SP-045 (B2C Transfer)

US-SP-026 + US-SP-027
  |
  +-> US-SP-029 (Admin Dashboard)
  |     |
  |     +-> US-SP-030 (Admin Orgs) --> US-SP-031 (Admin Grafo)
  |     +-> US-SP-032 (Admin Proveedores)
  |     +-> US-SP-033 (Admin Reconciliacion)
  |     +-> US-SP-034 (Admin Audit)
  |     +-> US-SP-035 (Admin Politicas + Alertas)
  |
  +-> US-SP-036 (B2B Dashboard)
  |     |
  |     +-> US-SP-037 (B2B SPEI out)
  |     +-> US-SP-038 (B2B Internos)
  |     +-> US-SP-039 (B2B Estructura Cuentas)
  |     +-> US-SP-040 (B2B Historial)
  |     +-> US-SP-041 (B2B Usuarios B2C)
  |     +-> US-SP-042 (B2B Aprobaciones + Config)
  |
  +-> US-SP-043 (B2C Dashboard)
        |
        +-> US-SP-044 (B2C Movimientos)
        +-> US-SP-045 (B2C Transferencia)
        +-> US-SP-046 (B2C Info Cuenta)
```

---

## Resumen de Estimaciones

| Epica | User Stories | Dev-Days Estimados |
|-------|-------------|-------------------|
| EP-SP-007 (Scaffold + Multi-Tier) | 4 stories (US-SP-025 a 028) | 14 dev-days |
| EP-SP-008 (Portal Admin T1) | 7 stories (US-SP-029 a 035) | 31 dev-days |
| EP-SP-011 (Portal B2B T2) | 7 stories (US-SP-036 a 042) | 30 dev-days |
| EP-SP-012 (Portal B2C T3) | 4 stories (US-SP-043 a 046) | 11 dev-days |
| EP-SP-013 (Compartidos) | 5 stories (US-SP-047 a 051) | 21 dev-days |
| **TOTAL FRONTEND** | **27 stories** | **107 dev-days** |

**Con buffer de 20% para imprevistos:** ~128 dev-days

**Con 1 desarrollador frontend full-time:** ~26 semanas (6.5 meses)

**Con 2 desarrolladores frontend full-time:** ~13 semanas (3.2 meses)

**Solo MVP Frontend (Fases F1-F3):** ~60 dev-days = ~8 semanas con 1 dev, ~4 semanas con 2 devs

---

## Comparacion con Plan Original

| Aspecto | Plan Original (EP-007 + EP-008) | Plan Multi-Tier (5 epicas) |
|---------|--------------------------------|---------------------------|
| Epicas | 2 | 5 |
| User Stories | 8 (US-SP-025 a 032) | 27 (US-SP-025 a 051) |
| Dev-Days | 30 | 107 |
| Portales | 1 (generico) | 3 (admin, B2B, B2C) |
| Guards/Roles | Ninguno | tierGuard con 3 roles |
| Layouts | 1 | 3 diferenciados |
| Componentes compartidos | 0 (todo inline) | 5 componentes reutilizables |
| Escalabilidad | Baja | Alta (nuevos tiers posibles) |
| Complejidad de permisos | Ninguna | Por tier, por org, por usuario |

**Justificacion del incremento:** El modelo multi-tier es significativamente mas complejo porque maneja 3 tipos de usuario con diferentes vistas, permisos, y experiencias. Sin embargo, la inversion en componentes compartidos (EP-SP-013) reduce la duplicacion y facilita el mantenimiento a largo plazo.

---

## Numeracion Actualizada del Plan

La siguiente tabla muestra como se reasignan los IDs de US para evitar colisiones con el plan backend existente (US-SP-001 a US-SP-024 son backend y no cambian):

| ID Original (Plan Viejo) | ID Nuevo (Plan Multi-Tier) | Descripcion |
|--------------------------|---------------------------|-------------|
| US-SP-025 | US-SP-025 | Scaffold mf-sp (expandido con multi-tier) |
| US-SP-026 | US-SP-026 | Routing multi-tier (antes: Dashboard de Cuentas) |
| US-SP-027 | US-SP-027 | Layouts por tier (antes: Detalle de Cuenta) |
| US-SP-028 | US-SP-028 | Modelos + Adapters (antes: Grafo Visual) |
| US-SP-029 | US-SP-029 | Admin Dashboard Global (antes: Form SPEI Out) |
| US-SP-030 | US-SP-030 | Admin Organizaciones (antes: Form Interno) |
| US-SP-031 | US-SP-031 | Admin Grafo Ecosistema (antes: Historial) |
| US-SP-032 | US-SP-032 | Admin Monitoreo Proveedores (antes: Status Real-time) |
| US-SP-033 | US-SP-033 | Admin Reconciliacion (NUEVA, antes era backend) |
| US-SP-034 | US-SP-034 | Admin Audit Trail (NUEVA, antes era backend) |
| US-SP-035 | US-SP-035 | Admin Politicas + Alertas (NUEVA, antes era backend) |
| -- | US-SP-036 | B2B Dashboard (NUEVA) |
| -- | US-SP-037 | B2B SPEI Out (NUEVA) |
| -- | US-SP-038 | B2B Movimiento Interno (NUEVA) |
| -- | US-SP-039 | B2B Estructura Cuentas (NUEVA) |
| -- | US-SP-040 | B2B Historial (NUEVA) |
| -- | US-SP-041 | B2B Usuarios B2C (NUEVA) |
| -- | US-SP-042 | B2B Aprobaciones + Config (NUEVA) |
| -- | US-SP-043 | B2C Dashboard (NUEVA) |
| -- | US-SP-044 | B2C Movimientos (NUEVA) |
| -- | US-SP-045 | B2C Transferencia (NUEVA) |
| -- | US-SP-046 | B2C Info Cuenta (NUEVA) |
| -- | US-SP-047 | Shared: MovementsTable (NUEVA) |
| -- | US-SP-048 | Shared: AccountTree (NUEVA) |
| -- | US-SP-049 | Shared: TransferForm (NUEVA) |
| -- | US-SP-050 | Shared: AccountDetailCard (NUEVA) |
| -- | US-SP-051 | Shared: TransferStatusTracker (NUEVA) |

**Nota:** Las US de backend (US-SP-033, US-SP-034, US-SP-035) del plan original de EP-SP-009 y EP-SP-010 conservan sus IDs. Las nuevas US frontend que hacen referencia a reconciliacion, audit, y politicas son las vistas UI de esos backends y usan los mismos IDs por simplicidad. Si hay colision, renumerar las frontend a partir de US-SP-060.
