# Inventario - Plan de Epicas Completo

**Producto**: Inventario (Gestion de Inventario Multi-Cliente)
**Repositorios**: `covacha-inventory` (backend) + `mf-inventory` (frontend)
**Estado**: Planificacion
**Prioridad**: P2
**Fecha**: 2026-02-17
**Epicas**: EP-INV-001 a EP-INV-012 (12 epicas)
**User Stories**: US-INV-001 a US-INV-065 (65 user stories)
**Estimacion total**: ~195 dev-days

---

## Mapa de Epicas

| ID | Nombre | US | Tipo | Estado |
|----|--------|----|------|--------|
| EP-INV-001 | Infraestructura Backend - Activacion y Correccion de Base | 6 | Backend | Pendiente |
| EP-INV-002 | Gestion de Clientes - Hub Central del Modulo | 7 | Full-stack | Pendiente |
| EP-INV-003 | Catalogo de Productos y Categorias | 6 | Full-stack | Pendiente |
| EP-INV-004 | Venues y Sucursales por Cliente | 5 | Full-stack | Pendiente |
| EP-INV-005 | Proveedores por Cliente | 5 | Full-stack | Pendiente |
| EP-INV-006 | Stock e Inventario Operativo | 6 | Full-stack | Pendiente |
| EP-INV-007 | Sistema de Cotizaciones Inteligente | 6 | Full-stack | Pendiente |
| EP-INV-008 | Ventas y Cierre Diario por Cliente | 6 | Full-stack (NEW) | Pendiente |
| EP-INV-009 | Reportes y Analitica de Inventario | 5 | Full-stack | Pendiente |
| EP-INV-010 | Auditorias, Centros de Costo y Tareas | 5 | Full-stack | Pendiente |
| EP-INV-011 | Testing Backend - Cobertura Completa | 4 | Backend/QA | Pendiente |
| EP-INV-012 | Testing Frontend - Cobertura Completa | 4 | Frontend/QA | Pendiente |

---

## Diagnostico del Estado Actual

### Backend (covacha-inventory)

**Hallazgos criticos de la investigacion:**

| Aspecto | Estado | Detalle |
|---------|--------|---------|
| Endpoints definidos | 47 | En 6 archivos de rutas |
| Endpoints conectados | 3 | Solo organizations (1) y categories (2 GET) |
| Blueprints registrados en app.py | 2 de 7 | Faltan: products, stock, venues, warehouses |
| Servicios implementados | 18 | Categories (5), Organizations (2), Products (6), Stock (3), Codes (2) |
| Tests escritos | 99 | En 7 archivos |
| Tests ejecutables | 0 | conftest.py VACIO - sin fixtures |
| Modelos locales | 8 | Pydantic models en models/entities/ |
| Modelos covacha_libs | 4+ | Usados por servicios nuevos (products, stock) |
| Alineacion modelos | DESALINEADOS | Tests importan locales, servicios usan libs |
| Bugs conocidos | 3 | CategoryRepo.index(), BrandRepo.index(), server.py import |

**Funcionalidades NO existentes en backend:**
- Gestion de Clientes (`sp_client`) — no hay modelo, servicio ni rutas
- Ventas y Cierre Diario — no hay modelo ni servicio
- Reportes de ventas por cliente — no hay servicio
- Proveedores (backend) — no hay servicio ni rutas (solo existe en frontend)
- Cotizaciones (backend) — no hay servicio ni rutas (solo existe en frontend)
- Auditorias (backend) — no hay servicio ni rutas (solo existe en frontend)
- Centros de Costo (backend) — no hay servicio ni rutas (solo existe en frontend)

### Frontend (mf-inventory)

**Hallazgos criticos de la investigacion:**

| Aspecto | Estado | Detalle |
|---------|--------|---------|
| Arquitectura | Hexagonal | domain/application/infrastructure/presentation |
| Federation name | mfInventory | Puerto 4211 |
| Adaptadores (infra) | 12 | Product, Inventory, Venue, Category, Warehouse, Supplier, CostCenter, Quotation, Audit, StockMovement, Task |
| Use Cases (app) | 10 + TaskService | Signal-based state management |
| Modelos (domain) | 12 | Con interfaces completas |
| Ports (domain) | 11 | Interfaces Observable-based |
| Componentes funcionales | 6 | Dashboard, ProductsList, SuppliersList, QuotationForm, QuotationDetail, Layout |
| Componentes stub | 9+ | ProductForm, ProductDetail, Categories, VenuesList, StockOverview, StockAdjust, StockAlerts, Reports, Settings |
| Unit tests | 0 | Ninguno |
| E2E tests | 3 | Solo smoke tests basicos |
| API key hardcoded | SI | `MASTER-SuperSecretKey123456789` en HttpService y ProductAdapter |
| Archivos > 1000 lineas | 2 | QuotationForm (~1845), QuotationDetail (~1934) |
| SharedStateService | 640 lin | Lee covacha:auth, covacha:user, covacha:tenant, covacha:current_organization |

**Funcionalidades NO existentes en frontend:**
- Pantalla de Clientes — no hay componente ni use case
- current_sp_client_id — no hay manejo en SharedState
- Vista super admin multi-cliente — no existe
- Ventas y Cierre Diario — no hay componentes ni use case
- Reportes de ventas — componente stub sin logica

### Dependencias y Prerequisitos

| Dependencia | Tipo | Notas |
|------------|------|-------|
| covacha-libs | Modelos compartidos | Provee ModinvProduct, ModInvVenue, ModInvWarehouse, ModInvStockMovement |
| covacha-core | API de organizaciones | Validacion de current_organization_id |
| mf-marketing | Clientes existentes | Importar catalogo de clientes via API |
| Cognito | Autenticacion | Bearer token + roles (super_admin) |
| localStorage | Estado compartido | covacha:current_organization, covacha:auth, covacha:user |

---

## Orden de Implementacion Recomendado

```
Fase 1 - Cimientos (EP-INV-001)
  └── Registrar blueprints, fix conftest, alinear modelos, fix bugs

Fase 2 - Hub de Clientes (EP-INV-002)
  └── Modelo Cliente, primera pantalla, import, current_sp_client_id

Fase 3 - Catalogo (EP-INV-003 + EP-INV-004 + EP-INV-005) [paralelo]
  ├── Productos y Categorias
  ├── Venues y Sucursales
  └── Proveedores

Fase 4 - Operaciones (EP-INV-006 + EP-INV-007) [paralelo]
  ├── Stock e Inventario
  └── Cotizaciones

Fase 5 - Ventas (EP-INV-008 + EP-INV-009) [paralelo]
  ├── Ventas y Cierre Diario
  └── Reportes y Analitica

Fase 6 - Control (EP-INV-010)
  └── Auditorias, Centros de Costo

Fase 7 - Quality Assurance (EP-INV-011 + EP-INV-012) [paralelo]
  ├── Testing Backend >= 98%
  └── Testing Frontend >= 98%
```

---

## EP-INV-001: Infraestructura Backend - Activacion y Correccion de Base

> **Estado: Pendiente**

**Objetivo**: Activar toda la funcionalidad backend existente que esta implementada pero no conectada. Corregir bugs, alinear modelos y establecer la base para que el resto de epicas funcione correctamente.

**Repos**: `covacha-inventory`
**Estimacion**: 8 dev-days

### Criterios de Aceptacion

- [ ] Los 6 blueprints estan registrados en app.py (organizations, categories, products, stock, venues, warehouses)
- [ ] Categories routes expone todos los endpoints CRUD (GET, POST, PUT, DELETE)
- [ ] Los 47 endpoints responden correctamente con autenticacion
- [ ] conftest.py tiene fixtures funcionales: app, mock_aws, mock_product, mock_repository, sample_product_data
- [ ] Los 99 tests existentes se ejecutan (pueden fallar por logica, pero no por fixtures)
- [ ] Bug de `filter` en CategoryRepository y BrandRepository corregido
- [ ] API key se lee de variable de entorno, no hardcoded
- [ ] Modelos locales alineados con covacha_libs o eliminados si son redundantes
- [ ] server.py import corregido

### User Stories

#### US-INV-001: Registrar Blueprints Faltantes en app.py

**Como** desarrollador,
**Quiero** que todos los blueprints de rutas esten registrados en la aplicacion Flask,
**Para que** los 47 endpoints definidos sean accesibles via HTTP.

**Tareas Backend:**
- Agregar `register_blueprint` en `app.py` para: `products_routes`, `stock_routes`, `venues_routes`, `warehouses_routes`
- Completar rutas CRUD de categories (POST, PUT/PATCH, DELETE ademas de los GET existentes)
- Verificar que cada blueprint responde con `curl` o Postman
- Corregir import en `server.py`: `from mipay_inventory.app import create_app`

**Criterios de Aceptacion:**
- [ ] `GET /api/v1/inventory/products` retorna 200 con auth valida
- [ ] `POST /api/v1/inventory/products` retorna 201 con datos validos
- [ ] `GET /api/v1/inventory/stock/summary` retorna 200
- [ ] `GET /api/v1/inventory/venues` retorna 200
- [ ] `GET /api/v1/inventory/warehouses` retorna 200
- [ ] `POST /api/v1/categories` retorna 201
- [ ] `PUT /api/v1/categories/<id>` retorna 200
- [ ] `DELETE /api/v1/categories/<id>` retorna 204

---

#### US-INV-002: Corregir conftest.py y Habilitar Suite de Tests

**Como** desarrollador,
**Quiero** que conftest.py tenga todas las fixtures necesarias,
**Para que** los 99 tests existentes puedan ejecutarse.

**Tareas Backend:**
- Crear fixture `app` que instancie Flask app con `ConfigTest`
- Crear fixture `mock_aws` que mockee DynamoDB con `moto` o `unittest.mock`
- Crear fixture `mock_product` con datos de ejemplo de `ModinvProduct` (covacha_libs)
- Crear fixture `mock_repository` que mockee BaseRepository
- Crear fixture `sample_product_data` con dict de datos de producto valido
- Ejecutar `pytest -v` y documentar cuantos tests pasan/fallan

**Criterios de Aceptacion:**
- [ ] `pytest --collect-only` muestra 99 tests recolectados
- [ ] `pytest -v` ejecuta todos los tests sin `FixtureError`
- [ ] Al menos 80% de los 99 tests pasan en primera ejecucion
- [ ] Tests que fallan se documentan como issues para resolver

---

#### US-INV-003: Alinear Modelos Locales con covacha_libs

**Como** desarrollador,
**Quiero** que los modelos locales y los de covacha_libs esten alineados,
**Para que** no haya conflictos de importacion entre servicios y tests.

**Tareas Backend:**
- Auditar cada modelo local vs su equivalente en covacha_libs
- Si covacha_libs tiene el modelo: eliminar modelo local, actualizar imports
- Si covacha_libs NO tiene el modelo: mantener local o crear en covacha_libs
- Actualizar todos los imports en tests para usar los modelos correctos
- Verificar que `ModInvStockMovement`, `MovementType`, `MovementStatus` existen en covacha_libs
- Si faltan en covacha_libs: crearlos con PR a covacha-libs

**Criterios de Aceptacion:**
- [ ] No hay modelos duplicados (local + libs) para la misma entidad
- [ ] Todos los imports en tests/ apuntan a la fuente correcta
- [ ] `pytest -v` no muestra `ImportError` en ningun test
- [ ] covacha_libs tiene todos los modelos necesarios para inventario

---

#### US-INV-004: Corregir Bugs Conocidos en Repositorios

**Como** desarrollador,
**Quiero** que los bugs identificados en CategoryRepository y BrandRepository esten corregidos,
**Para que** las operaciones de listado funcionen sin errores.

**Tareas Backend:**
- Corregir `CategoryRepository.index()`: variable `filter` sin definir en `self._list_all(filter=filter)` — reemplazar con parametro del metodo o dict vacio
- Corregir `BrandRepository.index()`: mismo bug de variable `filter`
- Agregar tests unitarios para ambos metodos corregidos
- Verificar que `GET /api/v1/categories` retorna listado completo

**Criterios de Aceptacion:**
- [ ] `CategoryRepository.index()` retorna lista de categorias sin error
- [ ] `BrandRepository.index()` retorna lista de marcas sin error
- [ ] Tests unitarios verifican ambos metodos
- [ ] No hay variables undefined en ningun repositorio

---

#### US-INV-005: Eliminar API Key Hardcoded (Seguridad)

**Como** administrador de seguridad,
**Quiero** que la API key no este hardcoded en el codigo fuente del frontend,
**Para que** no se exponga en el repositorio publico.

**Tareas Frontend:**
- Remover `MASTER-SuperSecretKey123456789` de `http.service.ts`
- Remover API key hardcoded de `product.adapter.ts`
- Mover API key a `environment.ts` y `environment.prod.ts`
- Actualizar `HttpService` para leer API key desde environment
- Corregir `ProductAdapter` para usar `HttpService` en vez de `HttpClient` directo (alinear con los otros 11 adaptadores)

**Criterios de Aceptacion:**
- [ ] Busqueda `grep -r "SuperSecretKey" src/` retorna 0 resultados
- [ ] API key se lee de `environment.apiKey`
- [ ] ProductAdapter usa HttpService como los demas adaptadores
- [ ] La aplicacion funciona correctamente con la API key desde environment

---

#### US-INV-006: Corregir Navegacion Dual y Consistencia

**Como** usuario del modulo de inventario,
**Quiero** que la navegacion funcione consistentemente tanto en modo standalone como en Module Federation,
**Para que** pueda navegar entre secciones sin errores.

**Tareas Frontend:**
- Unificar sistema de navegacion: Router de Angular + signal-based deben coexistir sin conflicto
- Agregar route guards para validar `current_organization_id` en localStorage antes de permitir acceso
- Si no hay `current_organization_id`, redirigir a pantalla de seleccion de organizacion
- Verificar que la navegacion por tabs en InventoryLayoutComponent sincroniza con las rutas de Angular

**Criterios de Aceptacion:**
- [ ] Navegacion entre secciones funciona en modo standalone (ng serve)
- [ ] Navegacion entre secciones funciona en Module Federation (mf-core shell)
- [ ] Sin `current_organization_id` en localStorage, se muestra mensaje/redireccion
- [ ] Cambiar de seccion actualiza la URL correctamente

---

## EP-INV-002: Gestion de Clientes - Hub Central del Modulo

> **Estado: Pendiente**

**Objetivo**: Implementar la gestion de clientes como primera pantalla del modulo. Cada cliente que accede al modulo de inventario debe ser seleccionado primero, asignando `current_sp_client_id` al localStorage. Los clientes pueden importarse desde mf-marketing o registrarse nuevos.

**Repos**: `covacha-inventory` + `mf-inventory`
**Estimacion**: 20 dev-days
**Prerequisitos**: EP-INV-001

### Contexto de Negocio

El modulo de inventario es multi-cliente. Una organizacion puede tener multiples clientes comerciales, cada uno con su propio inventario, venues, proveedores y cotizaciones. Al entrar al modulo:

1. El usuario ve la lista de clientes de su organizacion
2. Selecciona un cliente → se asigna `current_sp_client_id` al localStorage
3. Todas las operaciones posteriores se filtran por ese cliente
4. Un super_admin puede ver y gestionar todos los clientes

### DynamoDB Design

**Tabla**: `covacha_sp_clients` (nueva)

| PK | SK | Atributos |
|----|-----|-----------|
| `ORG#<org_id>` | `CLIENT#<client_id>` | name, rfc, email, phone, address, contact_name, business_type, status, imported_from, marketing_client_id, created_at, updated_at |
| `ORG#<org_id>` | `CLIENT#<client_id>#CONFIG` | default_venue_id, default_warehouse_id, quotation_settings, payment_terms, credit_limit |

**GSI**: `status-gsi` (PK: status, SK: created_at) para filtrar activos/inactivos

### Criterios de Aceptacion

- [ ] Modelo `SpClient` existe en covacha_libs y covacha-inventory
- [ ] API CRUD de clientes funciona: GET, POST, PUT, DELETE
- [ ] API de importacion desde mf-marketing funciona
- [ ] Primera pantalla de mf-inventory muestra lista de clientes
- [ ] Al seleccionar cliente, `current_sp_client_id` se guarda en localStorage con prefijo `covacha:`
- [ ] Todas las pantallas posteriores filtran por `current_sp_client_id`
- [ ] Super admin ve todos los clientes de todas las organizaciones
- [ ] SharedStateService emite evento cuando cambia el cliente seleccionado
- [ ] BroadcastChannel sincroniza el cambio entre pestanas

### User Stories

#### US-INV-007: Modelo y Servicio de Clientes (Backend)

**Como** desarrollador backend,
**Quiero** crear el modelo SpClient, repositorio y servicios CRUD,
**Para que** el modulo tenga gestion de clientes en el backend.

**Tareas Backend:**
- Crear modelo `SpClient` en covacha_libs (`covacha_libs/models/modinv/sp_client.py`)
- Crear `SpClientRepository` con BaseRepository[SpClient]
- Crear servicios: `CreateSpClientService`, `IndexSpClientService`, `ShowSpClientService`, `UpdateSpClientService`, `DeleteSpClientService`
- Crear `SpClientController` con metodos CRUD
- Crear `SpClientSerializer` con serialize(), serialize_list(), serialize_paginated()
- Crear blueprint `sp_clients_routes.py` con endpoints:
  - `GET /api/v1/inventory/clients` — listar clientes de la org
  - `POST /api/v1/inventory/clients` — crear cliente
  - `GET /api/v1/inventory/clients/<id>` — detalle
  - `PUT /api/v1/inventory/clients/<id>` — actualizar
  - `DELETE /api/v1/inventory/clients/<id>` — eliminar (soft delete)
  - `GET /api/v1/inventory/clients/search?q=` — buscar
- Registrar blueprint en app.py
- Filtrar por `organization_id` del token JWT

**Criterios de Aceptacion:**
- [ ] `GET /api/v1/inventory/clients` retorna lista paginada
- [ ] `POST /api/v1/inventory/clients` crea cliente con todos los campos
- [ ] Clientes se filtran por organization_id automaticamente
- [ ] Soft delete marca status=DELETED, no elimina de DynamoDB
- [ ] Busqueda por nombre, RFC, email funciona

---

#### US-INV-008: Importar Clientes desde mf-marketing (Backend)

**Como** usuario del modulo de inventario,
**Quiero** importar clientes existentes del modulo de marketing,
**Para que** no tenga que registrarlos manualmente de nuevo.

**Tareas Backend:**
- Crear endpoint `POST /api/v1/inventory/clients/import` que reciba lista de IDs de clientes de marketing
- Implementar `ImportSpClientService` que:
  - Llame a covacha-core o tabla de contacts de marketing para obtener datos
  - Mapee campos de contact/lead a SpClient
  - Evite duplicados (por RFC o email)
  - Retorne resumen: importados, duplicados, errores
- Agregar campo `imported_from: "marketing"` y `marketing_client_id` para trazabilidad

**Criterios de Aceptacion:**
- [ ] Endpoint acepta array de marketing_client_ids
- [ ] Clientes duplicados (mismo RFC o email) se reportan sin error
- [ ] Respuesta incluye: `{imported: N, duplicates: N, errors: []}`
- [ ] Clientes importados tienen referencia al ID original de marketing

---

#### US-INV-009: Pantalla de Lista de Clientes (Frontend)

**Como** usuario del modulo de inventario,
**Quiero** ver la lista de clientes al entrar al modulo,
**Para que** pueda seleccionar con cual cliente trabajar.

**Tareas Frontend:**
- Crear modelo `SpClient` en `domain/models/sp-client.model.ts`
- Crear port `SpClientPort` en `domain/ports/sp-client.port.ts`
- Crear `SpClientAdapter` en `infrastructure/adapters/sp-client.adapter.ts`
- Crear `SpClientsUseCase` en `application/use-cases/sp-clients.use-case.ts`
- Crear `ClientsListComponent` en `presentation/pages/clients/clients-list.component.ts`
  - Tabla/grid de clientes con: nombre, RFC, email, telefono, status, fecha creacion
  - Busqueda con debounce
  - Filtros: status (activo/inactivo), tipo de negocio
  - Paginacion
  - Boton "Importar desde Marketing"
  - Boton "Nuevo Cliente"
  - Click en cliente → asignar `current_sp_client_id` y navegar al dashboard de inventario
- Hacer que esta sea la PRIMERA pantalla al entrar al modulo (antes del dashboard actual)
- Actualizar rutas en `entry.routes.ts`:
  - `''` → ClientsListComponent (nueva raiz)
  - `client/:clientId` → InventoryLayoutComponent (dashboard actual)
  - `client/:clientId/products` → ProductsListComponent
  - (etc. para todas las rutas existentes)

**Criterios de Aceptacion:**
- [ ] Al entrar a mf-inventory, se muestra la lista de clientes
- [ ] La tabla muestra nombre, RFC, email, status
- [ ] Busqueda filtra en tiempo real con debounce 300ms
- [ ] Click en cliente navega a `/client/:clientId` (dashboard)
- [ ] Si solo hay 1 cliente, se auto-selecciona

---

#### US-INV-010: Asignar current_sp_client_id al Storage

**Como** sistema,
**Quiero** que al seleccionar un cliente se guarde `current_sp_client_id` en localStorage,
**Para que** todas las operaciones del modulo se filtren por ese cliente.

**Tareas Frontend:**
- Agregar a SharedStateService:
  - Metodo `setCurrentClient(clientId: string, clientName: string)`
  - Metodo `getCurrentClient(): { id: string, name: string } | null`
  - Metodo `clearCurrentClient()`
  - Clave localStorage: `covacha:current_sp_client`
  - Emitir evento BroadcastChannel al cambiar
- En ClientsListComponent: al hacer click en un cliente, llamar `setCurrentClient()`
- En InventoryLayoutComponent: leer `getCurrentClient()` y mostrar nombre del cliente en header
- En TODOS los adaptadores: incluir header `X-SP-Client-Id` con el `current_sp_client_id`
- Agregar `ClientGuard` en route guard: si no hay `current_sp_client_id`, redirigir a lista de clientes

**Criterios de Aceptacion:**
- [ ] `localStorage.getItem('covacha:current_sp_client')` contiene JSON `{id, name}` despues de seleccionar
- [ ] Cambiar de pestana sincroniza el cliente via BroadcastChannel
- [ ] Header del modulo muestra "Inventario - [Nombre Cliente]"
- [ ] Sin cliente seleccionado, todas las rutas redirigen a lista de clientes
- [ ] HttpService incluye `X-SP-Client-Id` en cada request

---

#### US-INV-011: Modal de Importacion desde Marketing (Frontend)

**Como** usuario,
**Quiero** un modal para seleccionar que clientes importar desde marketing,
**Para que** pueda elegir cuales traer sin importar todos.

**Tareas Frontend:**
- Crear `ImportClientsDialogComponent`
  - Conectar con API de marketing (o covacha-core) para listar contacts/leads
  - Mostrar tabla con checkbox de seleccion multiple
  - Busqueda y filtros
  - Boton "Importar Seleccionados"
  - Mostrar resultado: N importados, N duplicados, N errores
  - Al cerrar, refrescar lista de clientes
- Agregar boton "Importar desde Marketing" en ClientsListComponent que abre este modal

**Criterios de Aceptacion:**
- [ ] Modal muestra contactos/leads disponibles de marketing
- [ ] Se pueden seleccionar multiples contactos
- [ ] Importacion muestra progreso y resultado
- [ ] Clientes importados aparecen inmediatamente en la lista
- [ ] Duplicados se indican sin error

---

#### US-INV-012: Formulario de Registro de Cliente Nuevo (Frontend)

**Como** usuario,
**Quiero** registrar un nuevo cliente directamente en el modulo de inventario,
**Para que** no dependa de tener el cliente previamente en marketing.

**Tareas Frontend:**
- Crear `ClientFormComponent` en `presentation/pages/clients/client-form.component.ts`
  - Campos: nombre comercial, razon social, RFC, email, telefono, direccion, tipo de negocio, contacto principal
  - Validaciones: RFC formato valido, email formato valido, campos obligatorios
  - Modo crear y modo editar
- Agregar rutas: `clients/new` y `clients/:id/edit`

**Criterios de Aceptacion:**
- [ ] Formulario valida RFC con formato mexicano
- [ ] Campos obligatorios: nombre, RFC, email
- [ ] Al guardar exitosamente, redirige a lista de clientes
- [ ] Modo editar pre-llena los campos del cliente existente
- [ ] Validacion de email duplicado antes de guardar

---

#### US-INV-013: Vista Super Admin - Todos los Clientes

**Como** super_admin,
**Quiero** ver todos los clientes de todas las organizaciones,
**Para que** pueda gestionar y supervisar el inventario global.

**Tareas Backend:**
- Agregar endpoint `GET /api/v1/inventory/clients/all` (solo super_admin)
- Decorar con `@requires_role('super_admin')` o validar rol en el controller
- Retornar clientes con su organization_name para distinguirlos

**Tareas Frontend:**
- En ClientsListComponent: si el usuario tiene rol `super_admin`:
  - Mostrar columna extra "Organizacion"
  - Mostrar toggle "Mis clientes" / "Todos los clientes"
  - Filtro por organizacion
- Agregar badge visual para distinguir vista admin

**Criterios de Aceptacion:**
- [ ] Super admin ve boton/toggle "Todos los clientes"
- [ ] La tabla incluye columna de organizacion en modo admin
- [ ] Filtro por organizacion funciona
- [ ] Usuario normal NO ve el toggle ni puede acceder al endpoint `/all`

---

## EP-INV-003: Catalogo de Productos y Categorias

> **Estado: Pendiente**

**Objetivo**: Activar y completar la gestion de productos y categorias que ya tienen backend implementado pero no conectado, y frontend con componentes stub. Todos los productos pertenecen a un cliente (`sp_client_id`).

**Repos**: `covacha-inventory` + `mf-inventory`
**Estimacion**: 18 dev-days
**Prerequisitos**: EP-INV-001, EP-INV-002

### Criterios de Aceptacion

- [ ] CRUD completo de productos funciona end-to-end (backend + frontend)
- [ ] CRUD completo de categorias funciona end-to-end
- [ ] Productos se filtran por `current_sp_client_id`
- [ ] Busqueda por nombre, SKU, codigo de barras funciona
- [ ] Generacion de codigos (SKU, EAN13, QR) funciona
- [ ] Scan de codigo de barras funciona (camara o input manual)
- [ ] Formulario de producto con todos los campos (precios, stock, proveedor, impuestos)
- [ ] Detalle de producto con historial de movimientos

### User Stories

#### US-INV-014: Filtrado de Productos por Cliente (Backend)

**Como** sistema,
**Quiero** que todos los endpoints de productos filtren por `sp_client_id`,
**Para que** cada cliente solo vea sus propios productos.

**Tareas Backend:**
- Agregar campo `sp_client_id` al modelo `ModinvProduct` en covacha_libs
- Modificar `ProductsController` para leer `sp_client_id` del header `X-SP-Client-Id`
- Modificar todos los servicios de products para filtrar por `sp_client_id`
- Agregar indice GSI en DynamoDB: `sp_client_id-gsi` (PK: sp_client_id, SK: created_at)
- Actualizar `CreateProductService` para asignar `sp_client_id` automaticamente

**Criterios de Aceptacion:**
- [ ] `GET /api/v1/inventory/products` retorna solo productos del cliente actual
- [ ] `POST /api/v1/inventory/products` asigna `sp_client_id` automaticamente
- [ ] Sin header `X-SP-Client-Id`, retorna 400 Bad Request
- [ ] Busqueda y filtros tambien restringen por `sp_client_id`

---

#### US-INV-015: Formulario de Producto Completo (Frontend)

**Como** usuario,
**Quiero** un formulario completo para crear y editar productos,
**Para que** pueda gestionar todo el catalogo de un cliente.

**Tareas Frontend:**
- Reemplazar stub `ProductFormComponent` con formulario funcional:
  - **Seccion basica**: nombre, descripcion, SKU, codigo de barras, codigo interno
  - **Seccion clasificacion**: categoria (selector con arbol), marca, tipo (simple/variable/kit/service)
  - **Seccion precios**: precio base, precio venta, precio mayoreo, impuestos (IVA, IEPS)
  - **Seccion stock**: stock inicial, stock minimo, stock maximo, unidad de medida
  - **Seccion proveedor**: proveedor (selector), costo, tiempo de entrega
  - **Seccion media**: imagen (upload a S3), URL de producto
  - **Seccion codigos**: boton "Generar Codigos" que llama a CodeGeneratorService
- Validaciones reactivas con FormGroup
- Modo crear y modo editar
- Preview de codigo de barras/QR generado

**Criterios de Aceptacion:**
- [ ] Formulario tiene todas las secciones con campos correspondientes
- [ ] Validaciones: nombre obligatorio, SKU unico, precio >= 0
- [ ] Selector de categoria muestra arbol jerarquico
- [ ] Generacion de SKU y codigos funciona desde el formulario
- [ ] Upload de imagen funciona
- [ ] Modo editar pre-llena todos los campos

---

#### US-INV-016: Detalle de Producto con Historial (Frontend)

**Como** usuario,
**Quiero** ver el detalle completo de un producto incluyendo su historial de stock,
**Para que** pueda tomar decisiones informadas sobre reabastecimiento.

**Tareas Frontend:**
- Reemplazar stub `ProductDetailComponent` con vista funcional:
  - **Header**: nombre, imagen, SKU, status badge
  - **Tabs**: Informacion General, Stock, Movimientos, Precios
  - **Tab Info**: todos los campos del producto en formato lectura
  - **Tab Stock**: stock actual, minimo, maximo, grafico de tendencia
  - **Tab Movimientos**: tabla de movimientos de stock (entradas, salidas, ajustes)
  - **Tab Precios**: historial de cambios de precio
  - Botones de accion: Editar, Activar/Desactivar, Eliminar
- Conectar con servicios existentes de stock y movimientos

**Criterios de Aceptacion:**
- [ ] Detalle muestra toda la informacion del producto
- [ ] Tab de Stock muestra cantidades actuales con indicadores visuales
- [ ] Tab de Movimientos muestra historial paginado
- [ ] Boton Editar navega al formulario en modo edicion
- [ ] Boton Eliminar pide confirmacion antes de ejecutar

---

#### US-INV-017: Gestion de Categorias con Arbol Jerarquico (Frontend)

**Como** usuario,
**Quiero** gestionar categorias en estructura de arbol,
**Para que** pueda organizar los productos del cliente de forma jerarquica.

**Tareas Frontend:**
- Reemplazar stub `CategoriesComponent` con vista funcional:
  - Vista de arbol expandible/colapsable
  - Drag-and-drop para reordenar (opcional, puede ser v2)
  - CRUD inline: crear subcategoria, editar nombre, eliminar
  - Contador de productos por categoria
  - Filtro/busqueda rapida
- Conectar con `CategoriesUseCase` existente (ya tiene loadTree, moveCategory, reorder)

**Criterios de Aceptacion:**
- [ ] Arbol muestra jerarquia de categorias expandible
- [ ] Se pueden crear categorias y subcategorias
- [ ] Editar nombre de categoria funciona inline
- [ ] Eliminar categoria muestra warning si tiene productos asociados
- [ ] Contador de productos es preciso

---

#### US-INV-018: Busqueda y Scan de Productos (Full-stack)

**Como** usuario,
**Quiero** buscar productos por nombre, SKU o escaneando un codigo de barras,
**Para que** pueda encontrar productos rapidamente en el punto de venta o almacen.

**Tareas Backend:**
- Verificar que `SearchProductService` funciona correctamente con filtros de `sp_client_id`
- Verificar que `scan()` endpoint parsea correctamente EAN13, UPC, QR

**Tareas Frontend:**
- Agregar barra de busqueda unificada en ProductsListComponent:
  - Input con icono de scan
  - Al hacer click en scan: activar camara del dispositivo (si hay) o input manual
  - Busqueda por nombre, SKU, codigo de barras
  - Resultados en tiempo real (debounce 300ms)
  - Auto-redirigir a detalle si el scan encuentra exactamente 1 producto
- Usar `quick_search` para sugerencias y `search` para resultados completos

**Criterios de Aceptacion:**
- [ ] Busqueda por nombre retorna resultados parciales
- [ ] Busqueda por SKU exacto retorna el producto
- [ ] Scan de codigo de barras (input manual) encuentra el producto
- [ ] Si scan tiene 1 resultado, auto-navega a detalle
- [ ] Busqueda respeta filtro por `sp_client_id`

---

#### US-INV-019: Exportar e Importar Catalogo de Productos

**Como** usuario,
**Quiero** exportar mi catalogo a CSV/Excel e importar productos masivamente,
**Para que** pueda migrar datos facilmente.

**Tareas Backend:**
- Crear endpoint `GET /api/v1/inventory/products/export?format=csv` que genere archivo CSV
- Crear endpoint `POST /api/v1/inventory/products/import` que acepte CSV con productos
- Validar formato, campos obligatorios, SKUs duplicados
- Retornar resumen: importados, errores por fila

**Tareas Frontend:**
- Implementar boton "Exportar" en ProductsListComponent (reemplazar console.log actual)
  - Descargar CSV con todos los productos del cliente
- Implementar boton "Importar" que abra modal:
  - Drag-and-drop de archivo CSV
  - Preview de primeras 5 filas
  - Mapeo de columnas (opcional)
  - Resultado de importacion con errores detallados

**Criterios de Aceptacion:**
- [ ] Export genera CSV valido con headers correctos
- [ ] Import acepta CSV con campos: nombre, sku, precio, categoria, stock_inicial
- [ ] Errores de importacion se reportan por fila
- [ ] SKUs duplicados no causan error fatal sino skip con reporte

---

## EP-INV-004: Venues y Sucursales por Cliente

> **Estado: Pendiente**

**Objetivo**: Completar la gestion de venues (sucursales/puntos de venta) por cliente. Cada cliente puede tener multiples venues con sus propios almacenes y modos de inventario.

**Repos**: `covacha-inventory` + `mf-inventory`
**Estimacion**: 12 dev-days
**Prerequisitos**: EP-INV-001, EP-INV-002

### Criterios de Aceptacion

- [ ] CRUD completo de venues funciona end-to-end filtrado por cliente
- [ ] CRUD de warehouses por venue funciona
- [ ] Cada venue tiene su modo de inventario (propio/centralizado/mixto)
- [ ] Mapa o lista de venues con stats de inventario
- [ ] Asociacion venue-warehouse funciona

### User Stories

#### US-INV-020: Filtrado de Venues y Warehouses por Cliente (Backend)

**Como** sistema,
**Quiero** que venues y warehouses se filtren por `sp_client_id`,
**Para que** cada cliente gestione solo sus propias sucursales.

**Tareas Backend:**
- Agregar `sp_client_id` a modelos `ModInvVenue` y `ModInvWarehouse` en covacha_libs
- Modificar `VenuesController` y `WarehousesController` para leer `sp_client_id` del header
- Agregar GSI `sp_client_id-gsi` en ambas tablas
- Actualizar create services para asignar `sp_client_id` automaticamente

**Criterios de Aceptacion:**
- [ ] Venues se filtran por `sp_client_id`
- [ ] Warehouses se filtran por `sp_client_id`
- [ ] Sin `X-SP-Client-Id`, retorna 400

---

#### US-INV-021: Listado y CRUD de Venues (Frontend)

**Como** usuario,
**Quiero** gestionar las sucursales de un cliente,
**Para que** pueda configurar donde opera el inventario.

**Tareas Frontend:**
- Reemplazar stub `VenuesListComponent` con vista funcional:
  - Grid de cards con: nombre, tipo, direccion, status, stats de inventario
  - Boton "Nueva Sucursal"
  - Click en venue → detalle con warehouses asociados
  - Toggle de modo inventario (propio/centralizado/mixto)
- Implementar `VenueFormComponent` y `VenueDetailComponent`
  - Formulario: nombre, tipo (tienda/almacen/popup/online/hibrido), direccion, contacto, telefono, email
  - Detalle: info general + lista de warehouses + stats

**Criterios de Aceptacion:**
- [ ] Grid muestra venues del cliente actual
- [ ] Crear venue con todos los campos funciona
- [ ] Detalle muestra warehouses asociados
- [ ] Cambiar modo de inventario se refleja inmediatamente

---

#### US-INV-022: Gestion de Almacenes por Venue (Frontend)

**Como** usuario,
**Quiero** gestionar almacenes dentro de cada sucursal,
**Para que** pueda organizar el inventario fisicamente.

**Tareas Frontend:**
- Implementar `WarehousesListComponent`, `WarehouseFormComponent`, `WarehouseDetailComponent`
  - Lista de almacenes con zonas y ubicaciones
  - Formulario: nombre, codigo, descripcion, venue asociado
  - Detalle: zonas (rack, estante, bin), capacidad, stock actual
- Conectar con `WarehousesUseCase` existente (ya tiene zones/locations/capacity)

**Criterios de Aceptacion:**
- [ ] Lista de almacenes muestra por venue
- [ ] Crear almacen con zonas y ubicaciones funciona
- [ ] Capacidad del almacen se calcula y muestra
- [ ] Se puede establecer un almacen como default del venue

---

#### US-INV-023: Estadisticas de Inventario por Venue

**Como** usuario,
**Quiero** ver estadisticas de inventario por sucursal,
**Para que** pueda identificar rapidamente donde hay problemas de stock.

**Tareas Backend:**
- Crear endpoint `GET /api/v1/inventory/venues/<id>/stats` que retorne:
  - Total productos en venue
  - Valor total del inventario
  - Productos con bajo stock
  - Productos agotados
  - Movimientos recientes

**Tareas Frontend:**
- En VenueDetailComponent mostrar dashboard de stats:
  - Cards con KPIs: productos, valor, bajo stock, agotados
  - Grafico de barras de stock por categoria
  - Lista de alertas de bajo stock

**Criterios de Aceptacion:**
- [ ] Stats se calculan correctamente por venue
- [ ] Cards de KPIs muestran datos en tiempo real
- [ ] Alertas de bajo stock son visibles
- [ ] Valor del inventario se calcula con precio de costo

---

#### US-INV-024: Configurar Modo de Inventario por Venue

**Como** usuario,
**Quiero** configurar como cada sucursal maneja su inventario,
**Para que** pueda adaptar el sistema a la operacion real del cliente.

**Tareas Backend:**
- Agregar endpoint `PATCH /api/v1/inventory/venues/<id>/inventory-mode` con body `{ mode: "own_stock" | "centralized" | "mixed" }`
- Implementar logica de modo:
  - `own_stock`: venue maneja su propio stock, transferencias entre venues
  - `centralized`: todo el stock se gestiona desde un venue principal
  - `mixed`: combinacion, algunos productos centralizados, otros locales

**Tareas Frontend:**
- En VenueDetailComponent agregar selector de modo de inventario
- Mostrar explicacion de cada modo
- Pedir confirmacion al cambiar (puede afectar operaciones en curso)

**Criterios de Aceptacion:**
- [ ] Los 3 modos se pueden seleccionar
- [ ] Cambio de modo pide confirmacion
- [ ] Modo se refleja en las operaciones de stock (filtros, transferencias)

---

## EP-INV-005: Proveedores por Cliente

> **Estado: Pendiente**

**Objetivo**: Completar la gestion de proveedores por cliente. El frontend tiene adaptador y use case, pero falta el backend completo y la mayoria de componentes de presentacion.

**Repos**: `covacha-inventory` + `mf-inventory`
**Estimacion**: 14 dev-days
**Prerequisitos**: EP-INV-001, EP-INV-002

### Criterios de Aceptacion

- [ ] Backend: Modelo, repositorio, servicios, controller y rutas de proveedores
- [ ] CRUD completo de proveedores funciona end-to-end filtrado por cliente
- [ ] Gestion de contactos por proveedor
- [ ] Gestion de cuentas bancarias por proveedor
- [ ] Metricas de performance de proveedor
- [ ] Asociacion proveedor-productos funciona

### User Stories

#### US-INV-025: Backend Completo de Proveedores

**Como** desarrollador backend,
**Quiero** implementar toda la capa backend de proveedores,
**Para que** el frontend pueda consumir las APIs.

**Tareas Backend:**
- Crear modelo `ModInvSupplier` en covacha_libs con campos: id, sp_client_id, organization_id, name, rfc, email, phone, address, payment_terms, credit_limit, performance_score, status, contacts[], bank_accounts[]
- Crear `SupplierRepository` con BaseRepository[ModInvSupplier]
- Crear servicios: Create, Index, Show, Update, Delete + ContactsService, BankAccountsService
- Crear `SuppliersController`
- Crear `supplier_routes.py` con endpoints:
  - CRUD: GET, POST, GET/:id, PUT/:id, DELETE/:id
  - `GET /:id/contacts` + `POST /:id/contacts` + `PUT /:id/contacts/:cid` + `DELETE /:id/contacts/:cid`
  - `GET /:id/bank-accounts` + `POST /:id/bank-accounts` + `PUT /:id/bank-accounts/:bid` + `DELETE /:id/bank-accounts/:bid`
  - `GET /:id/performance` — metricas de entregas, calidad, precios
  - `GET /search?q=`
- Registrar blueprint en app.py

**Criterios de Aceptacion:**
- [ ] CRUD de proveedores funciona con auth + sp_client_id
- [ ] CRUD de contactos por proveedor funciona
- [ ] CRUD de cuentas bancarias funciona
- [ ] Performance calcula: entregas a tiempo, calidad, precio promedio
- [ ] Busqueda por nombre/RFC funciona

---

#### US-INV-026: Formulario de Proveedor (Frontend)

**Como** usuario,
**Quiero** registrar y editar proveedores con toda su informacion,
**Para que** pueda gestionar la cadena de suministro del cliente.

**Tareas Frontend:**
- Implementar `SupplierFormComponent` con secciones:
  - Info basica: nombre, RFC, email, telefono, direccion
  - Contactos: tabla editable con nombre, cargo, email, telefono
  - Cuentas bancarias: banco, CLABE, numero de cuenta
  - Terminos: condiciones de pago, limite de credito, dias de credito
  - Categorias: que categorias de productos provee
- Implementar `SupplierDetailComponent` con:
  - Info del proveedor
  - Dashboard de performance (entregas, calidad, precios)
  - Lista de productos asociados
  - Historial de ordenes

**Criterios de Aceptacion:**
- [ ] Formulario crea proveedor con todos los campos
- [ ] Contactos se agregan/editan/eliminan en linea
- [ ] Cuentas bancarias se validan (CLABE 18 digitos)
- [ ] Detalle muestra metricas de performance con graficos

---

#### US-INV-027: Asociar Productos con Proveedores

**Como** usuario,
**Quiero** asociar productos con sus proveedores,
**Para que** sepa a quien pedir cuando necesite reabastecimiento.

**Tareas Backend:**
- Agregar campo `supplier_id` al modelo de producto
- Crear endpoint `GET /api/v1/inventory/suppliers/<id>/products` para listar productos del proveedor
- Agregar logica en UpdateProductService para cambiar proveedor

**Tareas Frontend:**
- En formulario de producto: selector de proveedor
- En detalle de proveedor: lista de productos que provee
- En detalle de producto: mostrar info del proveedor

**Criterios de Aceptacion:**
- [ ] Producto tiene campo proveedor seleccionable
- [ ] Detalle de proveedor lista sus productos
- [ ] Se puede cambiar el proveedor de un producto

---

#### US-INV-028: Metricas de Performance de Proveedores

**Como** usuario,
**Quiero** ver metricas de rendimiento de cada proveedor,
**Para que** pueda tomar decisiones de compra informadas.

**Tareas Backend:**
- Calcular metricas basadas en movimientos de stock tipo "purchase":
  - Entregas a tiempo (%)
  - Entregas completas (%)
  - Precio promedio por producto
  - Tiempo promedio de entrega (dias)

**Tareas Frontend:**
- En SupplierDetailComponent mostrar:
  - Score general (1-5 estrellas o porcentaje)
  - Grafico radar: precio, calidad, tiempo, confiabilidad
  - Timeline de ultimas entregas

**Criterios de Aceptacion:**
- [ ] Score se calcula automaticamente
- [ ] Grafico radar muestra 4 dimensiones
- [ ] Timeline muestra ultimas 10 entregas con status

---

#### US-INV-029: Recomendacion de Reabastecimiento por Proveedor

**Como** usuario,
**Quiero** recibir sugerencias de reabastecimiento basadas en el stock minimo y el proveedor,
**Para que** pueda generar ordenes de compra proactivamente.

**Tareas Backend:**
- Crear endpoint `GET /api/v1/inventory/suppliers/<id>/restock-suggestions`
- Calcular para cada producto del proveedor que este por debajo de stock minimo:
  - Cantidad sugerida = stock_maximo - stock_actual
  - Costo estimado = cantidad * precio_proveedor

**Tareas Frontend:**
- En SupplierDetailComponent agregar tab "Sugerencias de Compra"
- Tabla con: producto, stock actual, stock minimo, cantidad sugerida, costo estimado
- Boton "Generar Cotizacion" que pre-llene una cotizacion de compra

**Criterios de Aceptacion:**
- [ ] Solo aparecen productos bajo stock minimo
- [ ] Cantidad sugerida es la diferencia hasta stock maximo
- [ ] Costo estimado usa precio del proveedor
- [ ] Boton genera cotizacion con productos seleccionados

---

## EP-INV-006: Stock e Inventario Operativo

> **Estado: Pendiente**

**Objetivo**: Activar y completar las operaciones de stock que ya tienen backend implementado pero no conectado. Todas las operaciones se filtran por cliente y venue.

**Repos**: `covacha-inventory` + `mf-inventory`
**Estimacion**: 18 dev-days
**Prerequisitos**: EP-INV-001, EP-INV-002, EP-INV-004

### Criterios de Aceptacion

- [ ] Vista general de stock por venue funciona
- [ ] Entradas de stock (compra, devolucion) funcionan
- [ ] Salidas de stock (venta, dano, merma) funcionan
- [ ] Ajustes de stock (inventario fisico) funcionan
- [ ] Transferencias entre venues/warehouses funcionan
- [ ] Alertas de bajo stock y agotados funcionan
- [ ] Historial de movimientos por producto funciona
- [ ] Scan de barcode para operaciones de stock funciona

### User Stories

#### US-INV-030: Filtrado de Stock por Cliente y Venue (Backend)

**Como** sistema,
**Quiero** que las operaciones de stock se filtren por `sp_client_id` y opcionalmente por `venue_id`,
**Para que** cada cliente gestione solo su inventario.

**Tareas Backend:**
- Agregar `sp_client_id` al modelo `ModInvStockMovement` en covacha_libs
- Modificar `StockController` para leer `sp_client_id` del header
- Agregar filtro opcional por `venue_id` en query params
- Agregar GSI `sp_client_id-gsi` en tabla de stock movements

**Criterios de Aceptacion:**
- [ ] Todos los endpoints de stock filtran por sp_client_id
- [ ] Filtro por venue_id es opcional
- [ ] Sin sp_client_id retorna 400

---

#### US-INV-031: Vista General de Stock (Frontend)

**Como** usuario,
**Quiero** ver un dashboard de stock con todas las metricas clave,
**Para que** tenga visibilidad completa del inventario del cliente.

**Tareas Frontend:**
- Reemplazar stub `StockOverviewComponent` con vista funcional:
  - KPI Cards: total productos, valor total, bajo stock, agotados, en transito
  - Selector de venue (ver stock de una sucursal o de todas)
  - Tabla de stock con columnas: producto, SKU, stock actual, minimo, maximo, status, valor
  - Filtros: categoria, status (ok/bajo/agotado), venue
  - Colores: verde (ok), amarillo (bajo), rojo (agotado)
  - Boton "Descargar Reporte"
- Conectar con `InventoryUseCase` existente

**Criterios de Aceptacion:**
- [ ] KPI cards muestran datos correctos en tiempo real
- [ ] Selector de venue filtra stock
- [ ] Tabla muestra indicadores de color por status
- [ ] Filtros combinados funcionan
- [ ] Total del valor de inventario es preciso

---

#### US-INV-032: Operaciones de Entrada y Salida de Stock (Frontend)

**Como** usuario,
**Quiero** registrar entradas y salidas de stock,
**Para que** el inventario se mantenga actualizado.

**Tareas Frontend:**
- Reemplazar stub `StockAdjustComponent` con vista funcional de operaciones:
  - **Entradas**: compra, devolucion de cliente, transferencia entrante, ajuste positivo
  - **Salidas**: venta, devolucion a proveedor, dano, merma, transferencia saliente, ajuste negativo
  - Formulario: producto (selector o scan), cantidad, tipo de movimiento, warehouse, motivo
  - Scan de barcode: input manual o camara
  - Tabla de movimientos recientes (ultimas 24h)
- Validar que no se genere stock negativo en salidas

**Criterios de Aceptacion:**
- [ ] Entradas incrementan stock del producto
- [ ] Salidas decrementan stock (no permite negativo)
- [ ] Scan de barcode encuentra producto y pre-llena formulario
- [ ] Cada movimiento registra motivo y usuario
- [ ] Tabla de recientes se actualiza al registrar movimiento

---

#### US-INV-033: Transferencias entre Venues/Warehouses (Frontend)

**Como** usuario,
**Quiero** transferir stock entre sucursales o almacenes,
**Para que** pueda redistribuir inventario segun la demanda.

**Tareas Frontend:**
- Implementar `TransferFormComponent`:
  - Selector: venue/warehouse origen y destino
  - Agregar productos: busqueda o scan
  - Cantidad por producto
  - Preview de la transferencia antes de confirmar
  - Status: pendiente → enviado → recibido
- Implementar `TransfersListComponent`:
  - Tabla de transferencias con status, fecha, origen, destino
  - Filtros: status, fecha, venue
- Implementar `TransferDetailComponent`:
  - Detalle de productos, cantidades
  - Botones: Enviar, Recibir, Cancelar (segun status)

**Criterios de Aceptacion:**
- [ ] Crear transferencia con multiples productos funciona
- [ ] Flujo pendiente → enviado → recibido funciona
- [ ] Stock se decrementa en origen al enviar
- [ ] Stock se incrementa en destino al recibir
- [ ] Cancelar devuelve stock al origen

---

#### US-INV-034: Alertas de Stock (Frontend)

**Como** usuario,
**Quiero** ver alertas cuando productos esten bajos o agotados,
**Para que** pueda reabastecerse a tiempo.

**Tareas Frontend:**
- Reemplazar stub `StockAlertsComponent` con vista funcional:
  - Tab "Bajo Stock": productos con stock < stock_minimo
  - Tab "Agotados": productos con stock = 0
  - Tab "Por Vencer" (si aplica): productos con fecha de vencimiento proxima
  - Cada alerta muestra: producto, stock actual, minimo, proveedor, accion sugerida
  - Boton "Generar Orden de Compra" por alerta
  - Filtros por venue, categoria, proveedor

**Criterios de Aceptacion:**
- [ ] Alertas de bajo stock se muestran correctamente
- [ ] Agotados se listan con proveedor y accion sugerida
- [ ] Filtros por venue/categoria funcionan
- [ ] Boton de orden de compra pre-llena formulario de cotizacion

---

#### US-INV-035: Historial de Movimientos (Frontend)

**Como** usuario,
**Quiero** ver el historial completo de movimientos de stock,
**Para que** pueda auditar entradas, salidas y transferencias.

**Tareas Frontend:**
- Implementar `MovementsListComponent`:
  - Tabla paginada con: fecha, tipo, producto, cantidad, origen, destino, usuario, motivo
  - Filtros: rango de fechas, tipo de movimiento, producto, venue
  - Export a CSV
  - Resumen: total entradas, total salidas, neto
- Timeline visual por producto (accesible desde ProductDetail)

**Criterios de Aceptacion:**
- [ ] Tabla muestra todos los tipos de movimiento
- [ ] Filtro por rango de fechas funciona
- [ ] Filtro por tipo (entrada/salida/transferencia/ajuste) funciona
- [ ] Export CSV genera archivo valido
- [ ] Resumen calcula totales correctamente

---

## EP-INV-007: Sistema de Cotizaciones Inteligente

> **Estado: Pendiente**

**Objetivo**: Completar el sistema de cotizaciones que ya tiene frontend avanzado pero sin backend. Las cotizaciones se basan en los productos/servicios que vende el cliente seleccionado.

**Repos**: `covacha-inventory` + `mf-inventory`
**Estimacion**: 18 dev-days
**Prerequisitos**: EP-INV-002, EP-INV-003

### Contexto de Negocio

Una cotizacion es un documento que el cliente del inventario genera para sus propios clientes finales. Ejemplo:
- "Restaurante El Buen Sabor" (sp_client) tiene productos en su inventario
- Genera una cotizacion para "Hotel Marriott" (cliente final) con sus productos
- La cotizacion puede convertirse en venta

### Criterios de Aceptacion

- [ ] Backend: Modelo, repositorio, servicios, controller y rutas de cotizaciones
- [ ] Cotizaciones se crean con productos del cliente actual
- [ ] Envio por email y WhatsApp funciona
- [ ] Conversion de cotizacion a venta funciona
- [ ] Componentes QuotationForm y QuotationDetail divididos en sub-componentes (< 1000 lineas cada uno)
- [ ] PDF de cotizacion generado con branding del tenant

### User Stories

#### US-INV-036: Backend Completo de Cotizaciones

**Como** desarrollador backend,
**Quiero** implementar toda la capa backend de cotizaciones,
**Para que** el frontend pueda crear, enviar y convertir cotizaciones.

**Tareas Backend:**
- Crear modelo `ModInvQuotation` en covacha_libs: id, sp_client_id, organization_id, quotation_number, customer_name, customer_email, customer_phone, items[], subtotal, tax, total, status, valid_until, notes, sent_at, viewed_at, converted_at, created_by
- Crear modelo `ModInvQuotationItem`: product_id, product_name, sku, quantity, unit_price, discount, tax_rate, total
- Crear repositorio, servicios CRUD + envio + conversion
- Crear `quotation_routes.py` con endpoints:
  - CRUD: GET, POST, GET/:id, PUT/:id, DELETE/:id
  - `POST /:id/send` — enviar por email
  - `POST /:id/convert` — convertir a venta
  - `POST /:id/duplicate` — duplicar cotizacion
  - `GET /search?q=`
  - `GET /customer/:name` — cotizaciones por cliente final
  - `GET /status/:status` — filtrar por status
- Generar numero de cotizacion: `COT-{YYYYMMDD}-{SEQ}`
- Registrar blueprint en app.py

**Criterios de Aceptacion:**
- [ ] CRUD funciona con auth + sp_client_id
- [ ] Items referencian productos del catalogo del cliente
- [ ] Calculos de subtotal, tax, total son correctos
- [ ] Status flow: draft → sent → viewed → accepted/rejected → converted/expired
- [ ] Envio por email funciona (integrar con covacha-notification)

---

#### US-INV-037: Dividir Componente QuotationForm (Frontend)

**Como** desarrollador frontend,
**Quiero** dividir `QuotationFormComponent` (~1845 lineas) en sub-componentes,
**Para que** cumpla con el limite de 1000 lineas por archivo.

**Tareas Frontend:**
- Extraer sub-componentes de QuotationFormComponent:
  - `QuotationCustomerSectionComponent` — datos del cliente final (nombre, email, telefono)
  - `QuotationItemsSectionComponent` — tabla de items con selector de productos
  - `QuotationSummarySectionComponent` — subtotal, impuestos, descuento, total
  - `QuotationPreviewComponent` — preview en vivo del documento
  - `ProductSelectorDialogComponent` — modal de seleccion de productos del catalogo
- Mantener QuotationFormComponent como orquestador (< 500 lineas)
- Usar Input/Output para comunicacion entre componentes
- Mantener funcionalidad identica

**Criterios de Aceptacion:**
- [ ] Ningun archivo supera 1000 lineas
- [ ] Funcionalidad del formulario es identica a la anterior
- [ ] Tests unitarios para cada sub-componente
- [ ] Preview en vivo sigue funcionando

---

#### US-INV-038: Dividir Componente QuotationDetail (Frontend)

**Como** desarrollador frontend,
**Quiero** dividir `QuotationDetailComponent` (~1934 lineas) en sub-componentes,
**Para que** cumpla con el limite de 1000 lineas por archivo.

**Tareas Frontend:**
- Extraer sub-componentes de QuotationDetailComponent:
  - `QuotationHeaderComponent` — branding, logo, titulo, numero
  - `QuotationInfoComponent` — datos del emisor y receptor
  - `QuotationItemsTableComponent` — tabla de items con totales
  - `QuotationTimelineComponent` — timeline de estados
  - `QuotationSendDialogComponent` — modal de envio (email/WhatsApp/link)
  - `QuotationPrintStylesComponent` — estilos para impresion/PDF
- Mantener QuotationDetailComponent como orquestador (< 500 lineas)

**Criterios de Aceptacion:**
- [ ] Ningun archivo supera 1000 lineas
- [ ] Vista del detalle es identica a la anterior
- [ ] Impresion/PDF sigue funcionando correctamente
- [ ] Modal de envio funciona con email, WhatsApp y link

---

#### US-INV-039: Cotizaciones Basadas en Catalogo del Cliente

**Como** usuario,
**Quiero** crear cotizaciones seleccionando productos del catalogo del cliente actual,
**Para que** las cotizaciones reflejen precios y disponibilidad reales.

**Tareas Frontend:**
- Modificar ProductSelectorDialogComponent para:
  - Solo mostrar productos del `current_sp_client_id`
  - Mostrar stock disponible de cada producto
  - Alertar si stock es insuficiente para la cantidad solicitada
  - Aplicar precios del catalogo automaticamente
  - Soportar precios por volumen/mayoreo
- Actualizar QuotationItemsSectionComponent para:
  - Mostrar stock disponible al lado de cantidad
  - Highlight en rojo si cantidad > stock
  - Calcular descuento automatico por volumen si aplica

**Criterios de Aceptacion:**
- [ ] Solo productos del cliente actual aparecen en el selector
- [ ] Precios se toman del catalogo automaticamente
- [ ] Stock disponible se muestra por producto
- [ ] Alerta visual si cantidad excede stock
- [ ] Precios por volumen se aplican automaticamente

---

#### US-INV-040: Envio de Cotizacion por Email y WhatsApp

**Como** usuario,
**Quiero** enviar cotizaciones por email y WhatsApp,
**Para que** mis clientes finales las reciban rapidamente.

**Tareas Backend:**
- Crear endpoint `POST /api/v1/inventory/quotations/<id>/send` con body `{ channel: "email" | "whatsapp", recipient: "..." }`
- Para email: integrar con covacha-notification (SES o similar)
- Para WhatsApp: integrar con covacha-webhook (WhatsApp Business API)
- Generar PDF de la cotizacion con branding del tenant
- Registrar fecha de envio y cambiar status a "sent"

**Tareas Frontend:**
- El modal de envio ya existe en QuotationSendDialogComponent
- Conectar con backend para envio real (actualmente es UI only)
- Mostrar confirmacion de envio exitoso
- Actualizar status en la lista de cotizaciones

**Criterios de Aceptacion:**
- [ ] Envio por email entrega la cotizacion al destinatario
- [ ] Envio por WhatsApp envia PDF + mensaje con resumen
- [ ] Status cambia a "sent" despues del envio
- [ ] Se registra fecha y hora de envio

---

#### US-INV-041: Convertir Cotizacion a Venta

**Como** usuario,
**Quiero** convertir una cotizacion aceptada en una venta,
**Para que** el flujo comercial sea continuo.

**Tareas Backend:**
- Crear endpoint `POST /api/v1/inventory/quotations/<id>/convert`
- Crear registro de venta (ver EP-INV-008)
- Decrementar stock de cada producto de la cotizacion
- Cambiar status de cotizacion a "converted"
- Registrar referencia cruzada: venta.quotation_id, cotizacion.sale_id

**Tareas Frontend:**
- Boton "Convertir a Venta" en QuotationDetailComponent
- Confirmar conversion con resumen de impacto en stock
- Redirigir a detalle de venta creada
- Actualizar lista de cotizaciones con nuevo status

**Criterios de Aceptacion:**
- [ ] Conversion crea un registro de venta
- [ ] Stock se decrementa por cada item de la cotizacion
- [ ] Status de cotizacion cambia a "converted"
- [ ] Se puede navegar entre cotizacion y venta creada

---

## EP-INV-008: Ventas y Cierre Diario por Cliente

> **Estado: Pendiente**

**Objetivo**: Implementar el sistema de ventas y cierre diario que NO existe ni en backend ni en frontend. Cada cliente tiene sus propias ventas y puede hacer cierre de ventas diarias.

**Repos**: `covacha-inventory` + `mf-inventory`
**Estimacion**: 22 dev-days
**Prerequisitos**: EP-INV-002, EP-INV-003, EP-INV-007

### DynamoDB Design

**Tabla**: `covacha_inv_sales` (nueva)

| PK | SK | Atributos |
|----|-----|-----------|
| `CLIENT#<client_id>` | `SALE#<sale_id>` | sale_number, venue_id, customer_name, items[], subtotal, tax, discount, total, payment_method, payment_status, quotation_id, notes, cashier_id, created_at |
| `CLIENT#<client_id>` | `CLOSING#<date>#<venue_id>` | total_sales, total_transactions, cash_total, card_total, transfer_total, expected_cash, actual_cash, difference, status, closed_by, closed_at |

**GSI**: `venue-date-gsi` (PK: venue_id, SK: created_at) para filtrar ventas por venue y fecha

### Criterios de Aceptacion

- [ ] Modelo de venta completo con items, pagos, impuestos
- [ ] Registro de venta decrementa stock automaticamente
- [ ] Ventas se filtran por `sp_client_id` y opcionalmente por venue
- [ ] Cierre diario calcula totales por metodo de pago
- [ ] Cierre diario permite registrar efectivo real vs esperado
- [ ] Reporte de cierre generado como PDF
- [ ] Dashboard de ventas con graficos

### User Stories

#### US-INV-042: Modelo y Servicios de Ventas (Backend)

**Como** desarrollador backend,
**Quiero** implementar toda la capa backend de ventas,
**Para que** se puedan registrar transacciones comerciales por cliente.

**Tareas Backend:**
- Crear modelo `ModInvSale` en covacha_libs: id, sp_client_id, organization_id, venue_id, sale_number, customer_name, items[], subtotal, tax, discount, total, payment_method, payment_status, quotation_id, cashier_id, notes, created_at
- Crear modelo `ModInvSaleItem`: product_id, product_name, sku, quantity, unit_price, discount, tax_rate, total
- Crear repositorio, servicios: Create, Index, Show, Cancel, Refund
- Crear `SalesController` y `sales_routes.py`:
  - `GET /api/v1/inventory/sales` — listar ventas (paginado, filtros)
  - `POST /api/v1/inventory/sales` — crear venta
  - `GET /api/v1/inventory/sales/<id>` — detalle
  - `POST /api/v1/inventory/sales/<id>/cancel` — cancelar venta
  - `POST /api/v1/inventory/sales/<id>/refund` — devolucion parcial/total
  - `GET /api/v1/inventory/sales/daily?date=&venue_id=` — ventas del dia
  - `GET /api/v1/inventory/sales/summary?from=&to=` — resumen de ventas
- Generar numero de venta: `VTA-{YYYYMMDD}-{SEQ}`
- Al crear venta: decrementar stock de cada producto
- Registrar blueprint en app.py

**Criterios de Aceptacion:**
- [ ] Crear venta genera numero unico y decrementa stock
- [ ] Cancelar venta revierte stock
- [ ] Devolucion parcial ajusta stock y registra movimiento
- [ ] Filtros: fecha, venue, status, metodo de pago
- [ ] Resumen calcula totales por periodo

---

#### US-INV-043: Punto de Venta Simplificado (Frontend)

**Como** usuario,
**Quiero** una pantalla de punto de venta para registrar ventas rapidamente,
**Para que** pueda atender clientes finales sin fricciones.

**Tareas Frontend:**
- Crear `SaleFormComponent` en `presentation/pages/sales/sale-form.component.ts`:
  - **Panel izquierdo**: busqueda/scan de productos, catalogo rapido por categoria
  - **Panel derecho**: carrito de venta con items, cantidades, precios
  - **Footer**: subtotal, impuestos, descuento, total, boton cobrar
  - Scan de barcode para agregar productos
  - Busqueda rapida por nombre/SKU
  - Editar cantidad en linea
  - Aplicar descuento por item o por venta
  - Modal de pago: efectivo, tarjeta, transferencia, mixto
  - Imprimir ticket (si hay impresora) o mostrar resumen
- Crear ruta `/client/:clientId/sales/new`

**Criterios de Aceptacion:**
- [ ] Agregar productos por busqueda o scan funciona
- [ ] Carrito actualiza totales en tiempo real
- [ ] Descuentos por item y por venta funcionan
- [ ] Modal de pago soporta efectivo, tarjeta, transferencia
- [ ] Al confirmar pago, venta se registra y stock se decrementa
- [ ] Ticket/resumen se puede imprimir

---

#### US-INV-044: Listado de Ventas por Cliente (Frontend)

**Como** usuario,
**Quiero** ver el listado de todas las ventas del cliente,
**Para que** pueda consultar el historial de transacciones.

**Tareas Frontend:**
- Crear `SalesListComponent` en `presentation/pages/sales/sales-list.component.ts`:
  - Tabla paginada: numero, fecha, cliente final, items, total, metodo pago, status
  - Filtros: rango de fechas, venue, metodo de pago, status
  - Resumen: total ventas, total monto, promedio por venta
  - Click en venta → detalle
  - Boton "Descargar Reporte"
- Crear `SaleDetailComponent`:
  - Detalle completo: items, precios, pagos, referencia a cotizacion
  - Acciones: Cancelar, Devolucion
- Agregar rutas: `client/:clientId/sales`, `client/:clientId/sales/:id`

**Criterios de Aceptacion:**
- [ ] Tabla muestra ventas del cliente actual
- [ ] Filtros combinados funcionan
- [ ] Resumen de KPIs es preciso
- [ ] Detalle muestra toda la informacion de la venta
- [ ] Cancelar y devolucion disponibles segun status

---

#### US-INV-045: Sistema de Cierre Diario (Backend)

**Como** desarrollador backend,
**Quiero** implementar el cierre de ventas diario,
**Para que** cada cliente pueda cerrar su caja al final del dia.

**Tareas Backend:**
- Crear modelo `ModInvDailyClosing` en covacha_libs: id, sp_client_id, venue_id, date, total_sales_count, total_sales_amount, cash_sales, card_sales, transfer_sales, other_sales, expected_cash, actual_cash, difference, status, notes, closed_by, closed_at
- Crear servicios: CreateDailyClosing, IndexDailyClosing, ShowDailyClosing
- Crear endpoints:
  - `GET /api/v1/inventory/sales/closing/preview?date=&venue_id=` — preview antes de cerrar
  - `POST /api/v1/inventory/sales/closing` — ejecutar cierre
  - `GET /api/v1/inventory/sales/closings` — listar cierres anteriores
  - `GET /api/v1/inventory/sales/closings/<id>` — detalle de cierre
- Preview calcula automaticamente: ventas del dia, desglose por metodo de pago, efectivo esperado
- Al cerrar: registrar diferencia entre esperado y real, generar resumen

**Criterios de Aceptacion:**
- [ ] Preview muestra resumen correcto del dia
- [ ] Cierre registra diferencia efectivo esperado vs real
- [ ] No se puede cerrar dos veces el mismo dia+venue
- [ ] Historial de cierres es consultable con filtros

---

#### US-INV-046: Pantalla de Cierre Diario (Frontend)

**Como** usuario,
**Quiero** una pantalla para hacer el cierre de caja diario,
**Para que** pueda cuadrar las ventas al final del dia.

**Tareas Frontend:**
- Crear `DailyClosingComponent` en `presentation/pages/sales/daily-closing.component.ts`:
  - Selector de venue (si el cliente tiene multiples)
  - Selector de fecha (default: hoy)
  - Resumen automatico:
    - Total ventas del dia
    - Desglose: efectivo, tarjeta, transferencia
    - Efectivo esperado en caja
  - Input: efectivo real en caja
  - Calculo de diferencia (sobrante/faltante)
  - Campo de notas/observaciones
  - Boton "Cerrar Caja"
  - Confirmacion con password del cajero (opcional)
- Crear `ClosingsListComponent` con historial de cierres:
  - Tabla: fecha, venue, total ventas, diferencia, cerrado por
  - Filtros: rango de fechas, venue
  - Export PDF de cierre individual
- Agregar rutas: `client/:clientId/sales/closing`, `client/:clientId/sales/closings`

**Criterios de Aceptacion:**
- [ ] Preview muestra desglose correcto por metodo de pago
- [ ] Input de efectivo real calcula diferencia automaticamente
- [ ] Cierre exitoso genera resumen imprimible
- [ ] Historial de cierres con filtros funciona
- [ ] No permite cerrar si ya hay cierre del dia/venue

---

#### US-INV-047: Dashboard de Ventas por Cliente (Frontend)

**Como** usuario,
**Quiero** un dashboard de ventas con graficos y KPIs,
**Para que** pueda monitorear el rendimiento comercial del cliente.

**Tareas Frontend:**
- Agregar seccion de ventas al DashboardComponent existente (o crear tab):
  - KPI Cards: ventas hoy, ventas semana, ventas mes, ticket promedio
  - Grafico de linea: ventas diarias (ultimos 30 dias)
  - Grafico de barras: ventas por metodo de pago
  - Top 10 productos mas vendidos
  - Top 5 clientes finales por monto
  - Ventas por venue (si hay multiples)
- Datos se obtienen del endpoint `GET /api/v1/inventory/sales/summary`

**Criterios de Aceptacion:**
- [ ] KPIs muestran datos correctos
- [ ] Grafico de ventas diarias muestra tendencia
- [ ] Top productos se calcula correctamente
- [ ] Dashboard se actualiza al cambiar rango de fechas

---

## EP-INV-009: Reportes y Analitica de Inventario

> **Estado: Pendiente**

**Objetivo**: Implementar reportes completos de inventario, ventas y operaciones. Los reportes se generan por cliente y pueden exportarse a CSV/PDF.

**Repos**: `covacha-inventory` + `mf-inventory`
**Estimacion**: 15 dev-days
**Prerequisitos**: EP-INV-006, EP-INV-008

### Criterios de Aceptacion

- [ ] Reporte de valoracion de inventario funciona
- [ ] Reporte de movimientos de stock funciona
- [ ] Reporte de ventas por periodo funciona
- [ ] Reporte de productos mas/menos vendidos funciona
- [ ] Todos los reportes exportan a CSV y PDF
- [ ] Reportes filtran por cliente, venue, fecha

### User Stories

#### US-INV-048: Backend de Reportes

**Como** desarrollador backend,
**Quiero** endpoints de reportes que agreguen y calculen datos,
**Para que** el frontend pueda mostrar reportes completos.

**Tareas Backend:**
- Crear `ReportsController` y `reports_routes.py`:
  - `GET /api/v1/inventory/reports/inventory-valuation` — valor de inventario por producto, categoria, venue
  - `GET /api/v1/inventory/reports/stock-movements` — resumen de movimientos por tipo, producto, periodo
  - `GET /api/v1/inventory/reports/sales` — ventas por periodo, venue, producto, cliente final
  - `GET /api/v1/inventory/reports/top-products` — productos mas/menos vendidos
  - `GET /api/v1/inventory/reports/profitability` — margen por producto (costo vs venta)
  - Todos aceptan query params: `from`, `to`, `venue_id`, `category_id`, `format` (json/csv)
- Si `format=csv`: retornar archivo CSV descargable
- Filtrar por `sp_client_id` siempre

**Criterios de Aceptacion:**
- [ ] Valuacion de inventario es precisa (stock * costo unitario)
- [ ] Movimientos se resumen correctamente por tipo
- [ ] Ventas se agregan por periodo configurable
- [ ] Top products ordena por cantidad o por monto
- [ ] CSV tiene headers correctos y datos completos

---

#### US-INV-049: Pantalla de Reportes (Frontend)

**Como** usuario,
**Quiero** una pantalla de reportes con multiples tipos de reporte,
**Para que** pueda analizar el negocio del cliente desde diferentes angulos.

**Tareas Frontend:**
- Reemplazar stub `ReportsComponent` con vista funcional:
  - Tabs o sidebar con tipos de reporte:
    - Valuacion de Inventario
    - Movimientos de Stock
    - Reporte de Ventas
    - Productos Mas Vendidos
    - Rentabilidad por Producto
  - Cada reporte tiene:
    - Filtros: rango de fechas, venue, categoria
    - Tabla de datos con totales
    - Grafico relevante
    - Botones: Descargar CSV, Descargar PDF
  - Guardar filtros favoritos en localStorage

**Criterios de Aceptacion:**
- [ ] 5 tipos de reporte accesibles desde tabs/sidebar
- [ ] Cada reporte tiene filtros funcionales
- [ ] Tablas muestran datos paginados con totales
- [ ] Export CSV y PDF funcionan
- [ ] Filtros se guardan como favoritos

---

#### US-INV-050: Reporte de Valuacion de Inventario

**Como** usuario,
**Quiero** un reporte que muestre el valor total de mi inventario,
**Para que** conozca el capital invertido en productos.

**Tareas Frontend (sub-reporte):**
- Tabla: producto, SKU, stock actual, costo unitario, valor total
- Agrupacion por: categoria, venue, proveedor
- Totales: valor total, productos totales, costo promedio
- Grafico de pie: distribucion por categoria
- Comparacion con periodo anterior (si hay datos)

**Criterios de Aceptacion:**
- [ ] Valor total = SUM(stock * costo_unitario) es correcto
- [ ] Agrupacion por categoria muestra subtotales
- [ ] Grafico de pie muestra distribucion visual
- [ ] Export incluye todas las columnas

---

#### US-INV-051: Reporte de Ventas por Periodo

**Como** usuario,
**Quiero** un reporte detallado de ventas por periodo,
**Para que** pueda analizar tendencias y estacionalidad.

**Tareas Frontend (sub-reporte):**
- Selector de periodo: hoy, semana, mes, trimestre, anio, personalizado
- Tabla: fecha, numero ventas, monto total, ticket promedio, metodo pago principal
- Grafico de linea: ventas por dia/semana/mes (segun periodo)
- Comparativa: periodo actual vs periodo anterior
- Top 10 productos del periodo
- Top 5 clientes finales del periodo

**Criterios de Aceptacion:**
- [ ] Selector de periodo funciona con fechas personalizadas
- [ ] Grafico muestra tendencia correcta
- [ ] Comparativa con periodo anterior es precisa
- [ ] Tops se calculan dentro del periodo seleccionado

---

#### US-INV-052: Reporte de Rentabilidad por Producto

**Como** usuario,
**Quiero** un reporte de margen/rentabilidad por producto,
**Para que** pueda identificar productos mas y menos rentables.

**Tareas Frontend (sub-reporte):**
- Tabla: producto, costo, precio venta, margen, margen %, unidades vendidas, ganancia total
- Ordenar por: margen %, ganancia total, unidades vendidas
- Highlight: verde para margen > 30%, amarillo 15-30%, rojo < 15%
- Grafico de barras: top 10 mas rentables vs top 10 menos rentables

**Criterios de Aceptacion:**
- [ ] Margen = (precio_venta - costo) / precio_venta * 100
- [ ] Ganancia total = margen_unitario * unidades_vendidas
- [ ] Colores de indicador son correctos
- [ ] Se puede ordenar por cualquier columna

---

## EP-INV-010: Auditorias, Centros de Costo y Tareas

> **Estado: Pendiente**

**Objetivo**: Completar las funcionalidades de control y gestion que ya tienen frontend scaffolded (adaptadores, use cases) pero sin backend ni UI funcional.

**Repos**: `covacha-inventory` + `mf-inventory`
**Estimacion**: 16 dev-days
**Prerequisitos**: EP-INV-006

### Criterios de Aceptacion

- [ ] Sistema de auditorias de inventario funciona end-to-end
- [ ] Conteo fisico con resolucion de discrepancias funciona
- [ ] Centros de costo con presupuestos funcionan
- [ ] Sistema de tareas por equipo funciona
- [ ] Todo filtrado por `sp_client_id`

### User Stories

#### US-INV-053: Backend de Auditorias de Inventario

**Como** desarrollador backend,
**Quiero** implementar el backend de auditorias,
**Para que** los clientes puedan verificar su inventario fisico.

**Tareas Backend:**
- Crear modelo `ModInvAudit` en covacha_libs: id, sp_client_id, venue_id, type (cycle/full/spot/annual), status, items[], discrepancies[], summary, started_at, completed_at, approved_by
- Crear repositorio, servicios: Create, Start, RecordCount, SubmitForReview, Approve, Reject, ApplyAdjustments
- Crear `audits_routes.py`:
  - CRUD: GET, POST, GET/:id, PUT/:id, DELETE/:id
  - `POST /:id/start` — iniciar conteo
  - `POST /:id/record-count` — registrar conteo de item
  - `POST /:id/submit` — enviar para revision
  - `POST /:id/approve` — aprobar auditoria
  - `POST /:id/apply-adjustments` — aplicar ajustes de stock
  - `GET /:id/discrepancies` — ver discrepancias
- Al aplicar ajustes: crear movimientos de stock tipo "adjustment" para cada discrepancia

**Criterios de Aceptacion:**
- [ ] Flujo completo: crear → iniciar → contar → submit → approve → apply
- [ ] Discrepancias se calculan: esperado vs contado
- [ ] Apply adjustments crea movimientos de stock
- [ ] Filtrado por sp_client_id y venue_id

---

#### US-INV-054: Pantallas de Auditorias (Frontend)

**Como** usuario,
**Quiero** gestionar auditorias de inventario desde el frontend,
**Para que** pueda verificar que el stock fisico coincide con el sistema.

**Tareas Frontend:**
- Implementar `AuditsListComponent`:
  - Tabla de auditorias con: tipo, venue, status, fecha, items contados, discrepancias
  - Filtros: status, tipo, venue, fecha
  - Boton "Nueva Auditoria"
- Implementar `AuditFormComponent`:
  - Seleccionar venue y tipo de auditoria
  - Seleccionar productos a auditar (todos, por categoria, aleatorio)
- Implementar `AuditCountComponent`:
  - Lista de productos a contar
  - Input de cantidad contada por producto
  - Scan de barcode para encontrar producto
  - Indicador de progreso (X de Y contados)
  - Guardar progreso parcial
- Implementar `AuditDetailComponent`:
  - Resumen de la auditoria
  - Tabla de discrepancias: producto, esperado, contado, diferencia
  - Botones: Aprobar, Rechazar, Aplicar Ajustes

**Criterios de Aceptacion:**
- [ ] Crear auditoria seleccionando venue y productos funciona
- [ ] Conteo registra cantidades con scan o manual
- [ ] Progreso se guarda y se puede retomar
- [ ] Discrepancias se muestran claramente
- [ ] Aplicar ajustes actualiza stock y crea movimientos

---

#### US-INV-055: Backend y Frontend de Centros de Costo

**Como** usuario,
**Quiero** gestionar centros de costo para categorizar gastos de inventario,
**Para que** pueda controlar presupuestos por area o departamento.

**Tareas Backend:**
- Crear modelo `ModInvCostCenter` en covacha_libs: id, sp_client_id, name, parent_id, budget, spent, manager_id, venues[], categories[], status
- Crear repositorio, servicios CRUD + budget management
- Crear `cost_centers_routes.py`:
  - CRUD + `GET /tree` + `POST /:id/budget` + `GET /:id/expenses` + `GET /:id/report`

**Tareas Frontend:**
- Implementar `CostCentersComponent` con:
  - Vista de arbol jerarquico
  - CRUD inline
  - Asignar presupuesto y monitorear gasto
  - Alertas de sobre-presupuesto
  - Reporte por centro de costo

**Criterios de Aceptacion:**
- [ ] CRUD de centros de costo funciona
- [ ] Jerarquia padre-hijo funciona
- [ ] Presupuesto y gasto se rastrean
- [ ] Alerta cuando gasto > 80% del presupuesto

---

#### US-INV-056: Configuracion General del Modulo (Frontend)

**Como** usuario,
**Quiero** una pantalla de configuracion del modulo de inventario,
**Para que** pueda personalizar el comportamiento segun las necesidades del cliente.

**Tareas Frontend:**
- Reemplazar stub `InventorySettingsComponent` con vista funcional:
  - **Seccion General**: moneda, formato de numeros, zona horaria
  - **Seccion Stock**: stock minimo default, alerta de bajo stock %, metodo de valuacion (FIFO/LIFO/promedio)
  - **Seccion Cotizaciones**: vigencia default (dias), impuestos default, logo para PDF
  - **Seccion Ventas**: metodos de pago habilitados, impresion automatica de ticket
  - **Seccion Notificaciones**: alertas por email, alertas en app
- Guardar configuracion por cliente en backend

**Criterios de Aceptacion:**
- [ ] Cada seccion guarda su configuracion independientemente
- [ ] Configuracion se aplica en todo el modulo
- [ ] Valores por defecto son razonables
- [ ] Cambios se reflejan inmediatamente

---

#### US-INV-057: Sistema de Tareas (Optimizacion)

**Como** desarrollador,
**Quiero** optimizar el TaskService existente (663 lineas),
**Para que** sea mas mantenible y cumpla con los limites de codigo.

**Tareas Frontend:**
- Dividir `TaskService` en sub-servicios:
  - `TaskCrudService` — CRUD basico
  - `TaskTimerService` — time tracking (startTimer, stopTimer, focus mode)
  - `TaskAssignmentService` — asignacion y equipo
- Mantener funcionalidad identica

**Tareas Backend:**
- Crear endpoints basicos de tareas si no existen:
  - CRUD en `GET /api/v1/inventory/tasks`
  - Asignar: `PATCH /:id/assign`
  - Status: `PATCH /:id/status`

**Criterios de Aceptacion:**
- [ ] TaskService dividido en 3 sub-servicios < 300 lineas cada uno
- [ ] Funcionalidad identica a la anterior
- [ ] Backend soporta CRUD y asignacion de tareas

---

## EP-INV-011: Testing Backend - Cobertura Completa

> **Estado: Pendiente**

**Objetivo**: Llevar la cobertura de tests del backend de 0% funcional a >= 98%, corrigiendo los 99 tests existentes y creando tests nuevos para toda la funcionalidad nueva.

**Repos**: `covacha-inventory`
**Estimacion**: 18 dev-days
**Prerequisitos**: EP-INV-001 (conftest.py funcional)

### Criterios de Aceptacion

- [ ] conftest.py tiene todas las fixtures necesarias
- [ ] Los 99 tests existentes pasan (con correcciones de modelos/fixtures)
- [ ] Cada nuevo servicio tiene tests unitarios: happy path + error + edge cases
- [ ] Cada controller tiene tests de integracion (request lifecycle)
- [ ] Cobertura >= 98% verificada con `pytest --cov`
- [ ] CI (GitHub Actions) valida cobertura automaticamente

### User Stories

#### US-INV-058: Corregir y Ejecutar Tests Existentes (99 tests)

**Como** desarrollador,
**Quiero** que los 99 tests existentes pasen correctamente,
**Para que** la funcionalidad existente este validada.

**Tareas:**
- Completar fixtures en conftest.py (app, mock_aws, mock_product, etc.)
- Corregir imports en todos los archivos de test (usar covacha_libs models)
- Ejecutar `pytest -v` y corregir tests que fallen por logica
- Documentar tests que requieran cambios significativos

**Criterios de Aceptacion:**
- [ ] `pytest -v` muestra 99 tests recolectados
- [ ] >= 95 de 99 tests pasan
- [ ] Tests que no pasan tienen issue documentado
- [ ] No hay `ImportError` ni `FixtureError`

---

#### US-INV-059: Tests para Modulos Nuevos (Clientes, Ventas, Reportes)

**Como** desarrollador,
**Quiero** tests completos para los servicios nuevos de clientes, ventas y reportes,
**Para que** la funcionalidad nueva este validada desde el inicio.

**Tareas:**
- Tests para SpClient services (CRUD + import + search): ~20 tests
- Tests para Sales services (CRUD + cancel + refund + daily closing): ~25 tests
- Tests para Reports services (cada tipo de reporte): ~15 tests
- Tests para Quotation services (CRUD + send + convert): ~20 tests
- Tests para Supplier services (CRUD + contacts + bank accounts): ~15 tests
- Tests para Audit services (flujo completo): ~15 tests
- Tests para CostCenter services (CRUD + budget): ~10 tests

**Criterios de Aceptacion:**
- [ ] ~120 tests nuevos escritos y pasando
- [ ] Happy path + error case + edge case para cada servicio
- [ ] Mocks para DynamoDB, covacha-notification, covacha-core
- [ ] Nombres descriptivos: `test_debe_crear_cliente_cuando_datos_validos`

---

#### US-INV-060: Tests de Integracion (Controllers)

**Como** desarrollador,
**Quiero** tests de integracion que prueben el ciclo request-response completo,
**Para que** valide que middleware, controllers y servicios trabajan juntos.

**Tareas:**
- Crear test client de Flask para cada blueprint
- Tests de autenticacion: sin token → 401, token invalido → 403, token valido → 200
- Tests de validacion: sin sp_client_id → 400, datos invalidos → 422
- Tests de flujos: crear producto → verificar stock → crear cotizacion → convertir a venta → verificar stock decrementado

**Criterios de Aceptacion:**
- [ ] Tests cubren cada endpoint con respuestas exitosas y de error
- [ ] Flujos completos (multi-endpoint) validados
- [ ] Auth middleware testeado: 401, 403, 200
- [ ] Validaciones de input testeadas: 400, 422

---

#### US-INV-061: Coverage >= 98% y CI Pipeline

**Como** equipo de desarrollo,
**Quiero** que el pipeline de CI valide coverage automaticamente,
**Para que** nunca baje de 98%.

**Tareas:**
- Configurar `pytest --cov=mipay_inventory --cov-report=term-missing --cov-fail-under=98`
- Revisar `.github/workflows/auto-pr.yml` o crear si no existe
- Agregar step de coverage en el pipeline
- Identificar y cubrir lineas faltantes hasta llegar a 98%

**Criterios de Aceptacion:**
- [ ] `pytest --cov --cov-fail-under=98` pasa exitosamente
- [ ] CI pipeline ejecuta tests + coverage en cada push
- [ ] Coverage report muestra >= 98%
- [ ] PR automatico se crea solo si coverage pasa

---

## EP-INV-012: Testing Frontend - Cobertura Completa

> **Estado: Pendiente**

**Objetivo**: Llevar la cobertura de tests del frontend de 0% (0 unit tests) a >= 98%, con tests unitarios para componentes y servicios, y tests E2E para flujos criticos.

**Repos**: `mf-inventory`
**Estimacion**: 20 dev-days
**Prerequisitos**: EP-INV-002 a EP-INV-010 (componentes implementados)

### Criterios de Aceptacion

- [ ] Cada componente de presentacion tiene spec file con tests
- [ ] Cada use case tiene tests unitarios
- [ ] Cada adaptador tiene tests unitarios (mock HTTP)
- [ ] SharedStateService tiene tests completos
- [ ] E2E tests cubren flujos criticos (cliente → producto → cotizacion → venta → cierre)
- [ ] Cobertura >= 98% verificada con `ng test --code-coverage`
- [ ] CI pipeline valida cobertura automaticamente

### User Stories

#### US-INV-062: Tests Unitarios para Componentes de Presentacion

**Como** desarrollador frontend,
**Quiero** tests unitarios para cada componente,
**Para que** la UI este validada contra regresiones.

**Tareas:**
- Crear `.spec.ts` para cada componente funcional (~25 componentes):
  - ClientsListComponent, ClientFormComponent
  - ProductsListComponent, ProductFormComponent, ProductDetailComponent
  - SuppliersListComponent, SupplierFormComponent, SupplierDetailComponent
  - VenuesListComponent, VenueFormComponent, VenueDetailComponent
  - WarehousesListComponent, WarehouseFormComponent, WarehouseDetailComponent
  - StockOverviewComponent, StockAdjustComponent, StockAlertsComponent
  - DashboardComponent, InventoryLayoutComponent
  - QuotationFormComponent (y sub-componentes), QuotationDetailComponent (y sub-componentes)
  - SaleFormComponent, SalesListComponent, SaleDetailComponent
  - DailyClosingComponent, ClosingsListComponent
  - CategoriesComponent, ReportsComponent, InventorySettingsComponent
  - AuditsListComponent, AuditFormComponent, AuditCountComponent, AuditDetailComponent
  - MovementsListComponent, TransfersListComponent, TransferFormComponent
- Cada spec debe tener: renderizado, interaccion basica, validaciones

**Criterios de Aceptacion:**
- [ ] ~25 componentes con spec files
- [ ] Cada spec: should create, should render, should handle user interaction
- [ ] Mock de servicios con jasmine spies o TestBed providers
- [ ] `ng test --watch=false` pasa sin errores

---

#### US-INV-063: Tests Unitarios para Use Cases y Servicios

**Como** desarrollador frontend,
**Quiero** tests unitarios para cada use case y servicio,
**Para que** la logica de negocio del frontend este validada.

**Tareas:**
- Crear `.spec.ts` para cada use case (~12):
  - SpClientsUseCase, ProductsUseCase, CategoriesUseCase, VenuesUseCase
  - WarehousesUseCase, SuppliersUseCase, InventoryUseCase, QuotationsUseCase
  - StockMovementsUseCase, AuditsUseCase, CostCentersUseCase
  - SalesUseCase (nuevo)
- Tests: CRUD operations, state management (signals), error handling, pagination
- Crear `.spec.ts` para SharedStateService:
  - localStorage read/write
  - BroadcastChannel sync
  - getCurrentClient() / setCurrentClient()
- Crear `.spec.ts` para HttpService y OrganizationValidatorService

**Criterios de Aceptacion:**
- [ ] ~15 spec files para use cases y servicios
- [ ] Mock de HttpClient con HttpClientTestingModule
- [ ] Signal state changes verificados
- [ ] Error handling paths testeados

---

#### US-INV-064: Tests E2E para Flujos Criticos

**Como** QA,
**Quiero** tests E2E que cubran los flujos criticos del modulo,
**Para que** pueda validar la experiencia completa del usuario.

**Tareas:**
- Expandir tests E2E en Playwright (`tests/e2e/specs/`):
  - **Flujo de Cliente**: login → ver clientes → seleccionar → ver dashboard
  - **Flujo de Producto**: seleccionar cliente → crear producto → editar → buscar → eliminar
  - **Flujo de Cotizacion**: seleccionar cliente → crear cotizacion → agregar items → enviar → convertir a venta
  - **Flujo de Venta**: seleccionar cliente → nueva venta → agregar productos → pagar → verificar stock
  - **Flujo de Cierre**: ver ventas del dia → hacer cierre → verificar resumen
  - **Flujo de Auditoria**: crear auditoria → contar → submit → aprobar → aplicar ajustes
- Usar mocks de API (api-mocks.ts existente) para datos consistentes

**Criterios de Aceptacion:**
- [ ] 6 flujos E2E implementados
- [ ] Tests corren en CI con Playwright
- [ ] Mocks de API proveen datos consistentes
- [ ] Tests no son flaky (reintento automatico si es necesario)

---

#### US-INV-065: Coverage >= 98% y CI Frontend

**Como** equipo de desarrollo,
**Quiero** que el CI del frontend valide coverage automaticamente,
**Para que** nunca baje de 98%.

**Tareas:**
- Configurar `karma.conf.js` con coverage reporter
- Configurar threshold en `angular.json` o `karma.conf.js`: branches 98%, functions 98%, lines 98%, statements 98%
- Verificar `.github/workflows/ci.yml`:
  - Step de `ng test --watch=false --code-coverage`
  - Validacion de coverage >= 98% (no skip si no hay coverage)
  - Step de Playwright E2E
- Corregir el fallback actual que salta coverage cuando no hay `lcov.info`

**Criterios de Aceptacion:**
- [ ] `ng test --watch=false --code-coverage` genera lcov.info
- [ ] Coverage >= 98% en lineas, funciones, branches
- [ ] CI NO se salta validacion de coverage
- [ ] PR automatico solo se crea si todo pasa

---

## Resumen de Metricas

### Conteo por Epica

| Epica | User Stories | Tipo | Estimacion |
|-------|-------------|------|-----------|
| EP-INV-001 | 6 | Backend | 8 days |
| EP-INV-002 | 7 | Full-stack | 20 days |
| EP-INV-003 | 6 | Full-stack | 18 days |
| EP-INV-004 | 5 | Full-stack | 12 days |
| EP-INV-005 | 5 | Full-stack | 14 days |
| EP-INV-006 | 6 | Full-stack | 18 days |
| EP-INV-007 | 6 | Full-stack | 18 days |
| EP-INV-008 | 6 | Full-stack | 22 days |
| EP-INV-009 | 5 | Full-stack | 15 days |
| EP-INV-010 | 5 | Full-stack | 16 days |
| EP-INV-011 | 4 | Backend/QA | 18 days |
| EP-INV-012 | 4 | Frontend/QA | 20 days |
| **TOTAL** | **65** | | **~199 days** |

### Conteo de Tests Esperados

| Capa | Tests actuales | Tests esperados | Delta |
|------|---------------|----------------|-------|
| Backend (unit) | 99 (0 ejecutables) | ~320 | +221 |
| Backend (integration) | 0 | ~60 | +60 |
| Frontend (unit) | 0 | ~200 | +200 |
| Frontend (E2E) | 3 (smoke) | ~25 | +22 |
| **TOTAL** | **102** | **~605** | **+503** |

### Endpoints Esperados (Backend)

| Grupo | Actuales | Nuevos | Total |
|-------|---------|--------|-------|
| Organizations | 1 | 0 | 1 |
| Categories | 2 | 3 | 5 |
| Products | 14 (no conectados) | 2 | 16 |
| Stock | 15 (no conectados) | 0 | 15 |
| Venues | 8 (no conectados) | 2 | 10 |
| Warehouses | 7 (no conectados) | 0 | 7 |
| **Clients** | 0 | 8 | 8 |
| **Suppliers** | 0 | 14 | 14 |
| **Quotations** | 0 | 10 | 10 |
| **Sales** | 0 | 10 | 10 |
| **Reports** | 0 | 6 | 6 |
| **Audits** | 0 | 10 | 10 |
| **CostCenters** | 0 | 8 | 8 |
| **Tasks** | 0 | 5 | 5 |
| **TOTAL** | **47** | **78** | **125** |

### Componentes Frontend Esperados

| Tipo | Actuales funcionales | Stubs a completar | Nuevos | Total |
|------|---------------------|-------------------|--------|-------|
| Paginas | 6 | 9 | ~15 | ~30 |
| Shared | 3 | 0 | ~5 | ~8 |
| Dialogos | 0 | 0 | ~5 | ~5 |
| Sub-componentes | 0 | 0 | ~10 | ~10 |
| **TOTAL** | **9** | **9** | **~35** | **~53** |

---

## Glosario

| Termino | Definicion |
|---------|-----------|
| **sp_client** | Cliente comercial del modulo de inventario. Una organizacion puede tener multiples clientes. |
| **current_sp_client_id** | ID del cliente actualmente seleccionado, guardado en localStorage |
| **venue** | Sucursal o punto de venta fisico de un cliente |
| **warehouse** | Almacen dentro de un venue |
| **stock movement** | Registro de entrada, salida, ajuste o transferencia de inventario |
| **daily closing** | Cierre de caja diario con cuadre de efectivo |
| **super_admin** | Rol con acceso a todos los clientes de todas las organizaciones |
| **quotation** | Cotizacion generada por el cliente para su cliente final |
| **cost center** | Centro de costo para categorizar gastos de inventario |

---

## Referencias

| Documento | Descripcion |
|-----------|-----------|
| `repos/covacha-inventory.yml` | Metadata del repo backend |
| `repos/mf-inventory.yml` | Metadata del repo frontend |
| `products/superpago/superpago.yml` | Producto padre que incluye inventory |
| Backend CLAUDE.md | `/Users/casp/sandboxes/superpago/covacha-inventory/CLAUDE.md` |
| Frontend federation.config | `mf-inventory/federation.config.js` |
