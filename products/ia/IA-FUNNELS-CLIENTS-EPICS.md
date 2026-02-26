# IA/Bots - Funnels de Venta, Gestion de Clientes y Cobertura de Tests (EP-IA-011 a EP-IA-016)

**Fecha**: 2026-02-19
**Product Owner**: SuperPago / BaatDigital
**Estado**: EN PROGRESO (EP-IA-011 y EP-IA-012 completados, EP-IA-013 a 016 pendientes)
**Continua desde**: IA-BOTS-EPICS.md (EP-IA-001 a EP-IA-010, US-IA-001 a US-IA-055)
**User Stories**: US-IA-056 a US-IA-098
**Repos afectados**: covacha-botia, mf-ia, covacha-libs, covacha-core

---

## Tabla de Contenidos

1. [Contexto y Motivacion](#contexto-y-motivacion)
2. [Problemas Actuales a Resolver](#problemas-actuales-a-resolver)
3. [Arquitectura de Funnels de Venta](#arquitectura-de-funnels-de-venta)
4. [Mapa de Epicas](#mapa-de-epicas)
5. [Epicas Detalladas](#epicas-detalladas)
6. [User Stories Detalladas](#user-stories-detalladas)
7. [Estrategia de Testing](#estrategia-de-testing)
8. [Roadmap](#roadmap)
9. [Grafo de Dependencias](#grafo-de-dependencias)
10. [Riesgos y Mitigaciones](#riesgos-y-mitigaciones)

---

## Contexto y Motivacion

La plataforma IA (covacha-botia + mf-ia) es el motor central de automatizacion del ecosistema SuperPago/BaatDigital. Con EP-IA-001 a EP-IA-010 se define la plataforma base (orquestador, motor de conversacion, WhatsApp, web chat, LLM, RAG, flow builder, analytics, mejora continua, multi-canal).

Sin embargo, hay necesidades criticas que no estan cubiertas:

### Problemas Identificados

| Problema | Impacto | Solucion |
|----------|---------|----------|
| **mf-ia no lista clientes correctamente** | Dejo de funcionar la seleccion de clientes del modulo | EP-IA-011: Reparar gestion de clientes |
| **No existe motor de funnels de venta** | No hay automatizacion post-lead | EP-IA-012: Motor de funnels |
| **No hay canal email en funnels** | Solo se puede comunicar por WhatsApp | EP-IA-013: Canal email |
| **Funnels WhatsApp no configurables** | Templates hardcodeados | EP-IA-014: Canal WhatsApp mejorado |
| **current_sp_client_id no se mantiene** | Al cambiar de modulo se pierde el cliente seleccionado | EP-IA-011: Fix variable ambiente |
| **Cobertura de tests baja** | Regresiones frecuentes | EP-IA-015 + EP-IA-016: Tests 100% |

### Repositorios Involucrados

| Repositorio | Funcion | Puerto Dev | Cambios |
|-------------|---------|------------|---------|
| `covacha-botia` | Backend motor IA/funnels | 5005 | Funnels engine, email, WhatsApp |
| `mf-ia` | Frontend configuracion IA | 4208 | Clientes, funnels UI, tests |
| `covacha-libs` | Modelos compartidos | N/A | Modelos de funnels |
| `covacha-core` | Backend principal | 5001 | Endpoints de clientes IA |

---

## Problemas Actuales a Resolver

### 1. Gestion de clientes en mf-ia rota

**Problema**: La lista de clientes que tienen el servicio de IA contratado dejo de funcionar. La sincronizacion desde mf-marketing tampoco funciona.

**Causa probable**: Cambio en el endpoint de covacha-core que lista clientes con servicio IA, o cambio en el adapter de mf-ia que consume ese endpoint.

**Solucion**: Reparar el flujo completo: endpoint → adapter → service → componente. Agregar sincronizacion bidireccional con mf-marketing.

### 2. current_sp_client_id no persiste

**Problema**: Al seleccionar un cliente en mf-ia, la variable `current_sp_client_id` no se mantiene al navegar entre secciones o al cambiar a otro micro-frontend.

**Solucion**: Usar el mismo patron que mf-marketing: `localStorage` con key `covacha:current_sp_client_id` + `BroadcastChannel` para sync entre tabs.

### 3. No existe motor de funnels

**Problema**: covacha-botia no tiene ningun concepto de funnel de venta. Toda la comunicacion con leads es manual.

**Solucion**: Crear motor de funnels completo con scheduler, canales, condiciones, y chaining.

### 4. Cobertura de tests insuficiente

**Problema**: covacha-botia y mf-ia tienen cobertura de tests baja, lo que causa regresiones.

**Solucion**: Llevar cobertura a 100% en backend y 95% en frontend. Agregar E2E con Playwright.

---

## Arquitectura de Funnels de Venta

```
┌──────────────────────────────────────────────────────────────┐
│                    TRIGGERS DE FUNNEL                          │
│                                                                │
│  Lead creado ──┐  Condicion ──┐  Manual ──┐  Cron ──┐        │
│  (formulario)  │  cumplida    │  (admin)  │  (loop) │        │
└────────────────┼─────────────┼───────────┼─────────┼────────┘
                 │             │           │         │
                 ▼             ▼           ▼         ▼
┌══════════════════════════════════════════════════════════════════┐
║                   MOTOR DE FUNNELS (covacha-botia)               ║
║                                                                   ║
║  ┌─────────────────────────────────────────────────────────────┐ ║
║  │                 FUNNEL EXECUTOR                              │ ║
║  │                                                              │ ║
║  │  1. Recibe trigger (lead_id, funnel_id)                     │ ║
║  │  2. Crea FunnelExecution                                    │ ║
║  │  3. Ejecuta steps secuencialmente:                          │ ║
║  │                                                              │ ║
║  │     ┌─────────┐    ┌─────────┐    ┌─────────┐              │ ║
║  │     │  STEP   │───►│  WAIT   │───►│  STEP   │───► ...      │ ║
║  │     │ (send)  │    │ (delay) │    │ (send)  │              │ ║
║  │     └─────────┘    └─────────┘    └─────────┘              │ ║
║  │                                                              │ ║
║  │  4. Evalua condiciones en cada transicion                   │ ║
║  │  5. Si hay chain, mueve lead al funnel destino              │ ║
║  │  6. Si hay recurrencia, re-schedula el step                 │ ║
║  │                                                              │ ║
║  └─────────────────────────────────────────────────────────────┘ ║
║                                                                   ║
║  ┌─────────────────────────────────────────────────────────────┐ ║
║  │                 SCHEDULER                                    │ ║
║  │                                                              │ ║
║  │  - Cron cada 1 minuto: busca executions con next_at <= now  │ ║
║  │  - Valida timezone + horario de envio                       │ ║
║  │  - Si fuera de horario, posterga a proximo slot valido      │ ║
║  │  - Si recurrencia=infinite, re-schedula con delay config    │ ║
║  │  - Dead letter queue para fallos                            │ ║
║  └─────────────────────────────────────────────────────────────┘ ║
║                                                                   ║
║  ┌─────────────────────────────────────────────────────────────┐ ║
║  │              CHANNEL ADAPTERS                                │ ║
║  │                                                              │ ║
║  │  ┌────────────────┐    ┌──────────────────────┐             │ ║
║  │  │  EMAIL ADAPTER  │    │  WHATSAPP ADAPTER     │             │ ║
║  │  │                │    │                      │             │ ║
║  │  │  - SES/SMTP    │    │  - Meta Business API │             │ ║
║  │  │  - Templates   │    │  - Templates aprob.  │             │ ║
║  │  │  - Variables   │    │  - Variables          │             │ ║
║  │  │  - Tracking    │    │  - Bot responde       │             │ ║
║  │  │  - Unsub link  │    │  - STOP handler      │             │ ║
║  │  └────────────────┘    └──────────────────────┘             │ ║
║  └─────────────────────────────────────────────────────────────┘ ║
║                                                                   ║
║  ┌─────────────────────────────────────────────────────────────┐ ║
║  │              FUNNEL TEMPLATES                                │ ║
║  │                                                              │ ║
║  │  DEFAULT_EMAIL_FUNNEL:                                      │ ║
║  │    Step 1: Email bienvenida (0 min)                         │ ║
║  │    Step 2: Email notif equipo (0 min)                       │ ║
║  │    Step 3: Wait 3 dias                                      │ ║
║  │    Step 4: Email follow-up                                  │ ║
║  │    Step 5: Wait 4 dias                                      │ ║
║  │    Step 6: Email info valor                                 │ ║
║  │    Step 7: Loop mensual (recurrence=monthly, infinite=true) │ ║
║  │                                                              │ ║
║  │  DEFAULT_WHATSAPP_FUNNEL:                                   │ ║
║  │    Step 1: Template bienvenida (0 min)                      │ ║
║  │    Step 2: Notif equipo via email (0 min)                   │ ║
║  │    Step 3: Wait 2 dias                                      │ ║
║  │    Step 4: Template follow-up                               │ ║
║  │    Step 5: Wait 5 dias                                      │ ║
║  │    Step 6: Template info valor                              │ ║
║  │    Step 7: Loop mensual (recurrence=monthly, infinite=true) │ ║
║  └─────────────────────────────────────────────────────────────┘ ║
╚══════════════════════════════════════════════════════════════════╝
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│                    mf-ia (Frontend)                               │
│                                                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐ │
│  │ Gestion Clientes │  │ Funnel Builder  │  │ Funnel Dashboard │ │
│  │                  │  │                  │  │                  │ │
│  │ - Lista clientes │  │ - Crear funnel  │  │ - Metricas       │ │
│  │ - Sync marketing │  │ - Steps config  │  │ - Executions     │ │
│  │ - Select client  │  │ - Templates     │  │ - Conversiones   │ │
│  │ - current_sp_id  │  │ - Chain funnels │  │ - Export         │ │
│  └─────────────────┘  └─────────────────┘  └──────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

---

## Mapa de Epicas

| ID | Epica | User Stories | Complejidad | Prioridad | Dependencias |
|----|-------|-------------|-------------|-----------|--------------|
| EP-IA-011 | Gestion de Clientes Multi-Modulo | US-IA-056 a US-IA-062 | M | P1 Critica | COMPLETADO |
| EP-IA-012 | Motor de Funnels de Venta | US-IA-063 a US-IA-072 | XL | P1 Alta | COMPLETADO (backend) |
| EP-IA-013 | Canal Email en Funnels | US-IA-073 a US-IA-079 | L | P1 Alta | EP-IA-012 |
| EP-IA-014 | Canal WhatsApp en Funnels | US-IA-080 a US-IA-086 | L | P1 Alta | EP-IA-012, EP-IA-003 (WhatsApp) |
| EP-IA-015 | Tests 100% covacha-botia | US-IA-087 a US-IA-092 | L | P1 Alta | EP-IA-011 a EP-IA-014 |
| EP-IA-016 | Tests 100% mf-ia + E2E | US-IA-093 a US-IA-098 | L | P1 Alta | EP-IA-011 a EP-IA-014 |

**Totales**:
- 6 epicas
- 43 user stories (US-IA-056 a US-IA-098)
- Estimacion: ~50-70 dev-days

---

## Epicas Detalladas

---

### EP-IA-011: Gestion de Clientes Multi-Modulo

> **Estado: COMPLETADO** — Fix localStorage key mismatch: dual-key (MARKETING_CLIENT_KEY + IA_CLIENT_KEY) para sincronizacion cross-MF. Eliminado ngOnDestroy que borraba el cliente.

**Objetivo**: Reparar y mejorar la gestion de clientes en mf-ia. Los clientes con servicio IA contratado deben listarse correctamente, sincronizarse desde mf-marketing, y mantener `current_sp_client_id` persistente.

**Estado actual**: La lista de clientes dejo de funcionar. La sincronizacion desde mf-marketing no opera. El `current_sp_client_id` se pierde al navegar.

**User Stories**: US-IA-056 a US-IA-062

---

### EP-IA-012: Motor de Funnels de Venta

> **Estado: COMPLETADO (backend)** — FunnelExecutorService + FunnelController + funnel_routes en covacha-botia. Auto-enroll, funnel por defecto 4 pasos (WhatsApp/Email), despacho SQS, avance de leads. 17 tests.

**Objetivo**: Crear el motor de funnels de venta en covacha-botia con executor, scheduler, templates, condiciones y chaining. Este motor es consumido por mf-marketing (EP-MK-028) y mf-ia para configuracion.

**Estado actual**: No existe ningun concepto de funnel en covacha-botia.

**User Stories**: US-IA-063 a US-IA-072

---

### EP-IA-013: Canal Email en Funnels

**Objetivo**: Implementar el canal de email en el motor de funnels: envio via SES/SMTP, templates personalizables, variables dinamicas, tracking de apertura/click, y link de desuscripcion.

**Estado actual**: covacha-botia no tiene capacidad de envio de email.

**User Stories**: US-IA-073 a US-IA-079

---

### EP-IA-014: Canal WhatsApp en Funnels

**Objetivo**: Integrar el canal WhatsApp en el motor de funnels: templates aprobados por Meta, variables dinamicas, handler de respuestas del lead, y bot que atiende en el funnel.

**Estado actual**: covacha-botia tiene integracion WhatsApp basica pero no como canal de funnel automatizado.

**User Stories**: US-IA-080 a US-IA-086

---

### EP-IA-015: Tests 100% covacha-botia

**Objetivo**: Llevar la cobertura de tests de covacha-botia al 100% con tests unitarios, de integracion y E2E. Incluye todo el codigo existente mas el nuevo codigo de funnels.

**User Stories**: US-IA-087 a US-IA-092

---

### EP-IA-016: Tests 100% mf-ia + E2E

**Objetivo**: Llevar la cobertura de tests de mf-ia al 95%+ con tests unitarios (Karma+Jasmine) y E2E (Playwright). Incluye todo el codigo existente mas los componentes nuevos de funnels y clientes.

**User Stories**: US-IA-093 a US-IA-098

---

## User Stories Detalladas

---

### EP-IA-011: Gestion de Clientes Multi-Modulo

---

#### US-IA-056: Reparar listado de clientes con servicio IA

**Como** administrador de la plataforma IA
**Quiero** ver la lista de clientes que tienen el servicio de IA contratado
**Para** gestionar la configuracion de bots de cada cliente

**Criterios de Aceptacion:**
- [ ] Endpoint `GET /api/v1/ia/clients` devuelve clientes con servicio IA activo
- [ ] Lista muestra: nombre, logo, estado del bot, canales activos (web/WhatsApp)
- [ ] Paginacion y busqueda por nombre
- [ ] Si no hay clientes, mensaje: "No hay clientes con servicio IA. Sincroniza desde Marketing."
- [ ] Loading skeleton mientras carga

**Tareas Tecnicas:**
- [ ] Debuggear endpoint en covacha-core/covacha-botia
- [ ] Reparar adapter en mf-ia
- [ ] Tests: 6+ unit tests

---

#### US-IA-057: Sincronizacion de clientes desde mf-marketing

**Como** administrador de la plataforma IA
**Quiero** sincronizar clientes de mf-marketing para que se sumen como clientes del modulo IA
**Para** no tener que dar de alta clientes manualmente en dos lugares

**Criterios de Aceptacion:**
- [ ] Boton "Sincronizar desde Marketing" en pagina de clientes
- [ ] Muestra lista de clientes de marketing que NO estan en IA
- [ ] Checkbox para seleccionar cuales sincronizar
- [ ] Al sincronizar, crea el cliente en covacha-botia con configuracion basica
- [ ] Status de sincronizacion con progress bar
- [ ] Clientes sincronizados aparecen inmediatamente en la lista

**Tareas Tecnicas:**
- [ ] Endpoint `POST /api/v1/ia/clients/sync-from-marketing` en covacha-botia
- [ ] Consumir endpoint de clientes de covacha-core (marketing)
- [ ] UI de sincronizacion en mf-ia
- [ ] Tests: 8+ unit tests

---

#### US-IA-058: current_sp_client_id persistente en variable de ambiente

**Como** usuario de mf-ia
**Quiero** que al seleccionar un cliente, ese cliente se mantenga seleccionado al navegar entre secciones
**Para** no tener que re-seleccionar el cliente cada vez que cambio de pagina

**Criterios de Aceptacion:**
- [ ] Al seleccionar cliente, se guarda en `localStorage` con key `covacha:current_sp_client_id`
- [ ] Se emite via `BroadcastChannel('covacha:client')` para sync entre tabs
- [ ] Al cargar cualquier pagina de mf-ia, se lee de `localStorage` y se carga el cliente
- [ ] Si el cliente guardado ya no existe o no tiene servicio IA, se limpia y muestra selector
- [ ] Patron identico al de mf-marketing para consistencia

**Tareas Tecnicas:**
- [ ] Crear/actualizar `ClientContextService` en mf-ia
- [ ] Integrar con BroadcastChannel API
- [ ] Guard que verifica cliente seleccionado antes de cargar paginas
- [ ] Tests: 6+ unit tests

---

#### US-IA-059: Seleccion de cliente carga su configuracion

**Como** administrador de IA
**Quiero** que al seleccionar un cliente se cargue toda su configuracion de bot
**Para** ver y editar la configuracion especifica del cliente

**Criterios de Aceptacion:**
- [ ] Al seleccionar cliente, se cargan: configuracion de bot, canales activos, templates, knowledge base, funnels
- [ ] Sidebar o header muestra nombre y logo del cliente seleccionado
- [ ] Todas las paginas del modulo usan el client_id seleccionado
- [ ] Si el cliente no tiene bot configurado, mostrar wizard de configuracion inicial
- [ ] Transition suave entre clientes (loading state)

**Tareas Tecnicas:**
- [ ] Servicio `ClientConfigLoader` que carga config completa
- [ ] Resolver o guard por ruta que inyecta config
- [ ] Tests: 5+ unit tests

---

#### US-IA-060: Dashboard de cliente IA

**Como** administrador de IA
**Quiero** ver un dashboard resumen del cliente seleccionado
**Para** tener vision rapida del estado y rendimiento de su bot

**Criterios de Aceptacion:**
- [ ] Metricas: conversaciones hoy, leads capturados, satisfaccion, canales activos
- [ ] Estado del bot: activo/inactivo, ultimo entrenamiento, knowledge base size
- [ ] Funnels activos: cantidad, leads en funnel, conversion rate
- [ ] Accesos rapidos: configurar bot, ver conversaciones, editar funnels, ver knowledge base
- [ ] Graficos: conversaciones por dia (ultimos 30 dias), distribucion por canal

**Tareas Tecnicas:**
- [ ] Componente dashboard en mf-ia
- [ ] Endpoints de metricas en covacha-botia
- [ ] Tests: 5+ unit tests

---

#### US-IA-061: API de clientes IA en covacha-botia

**Como** sistema (mf-ia)
**Quiero** endpoints CRUD completos para gestionar clientes IA en covacha-botia
**Para** listar, crear, actualizar y eliminar configuraciones de clientes

**Criterios de Aceptacion:**
- [ ] `GET /api/v1/ia/clients` - listar clientes con paginacion
- [ ] `GET /api/v1/ia/clients/{id}` - detalle de cliente con config completa
- [ ] `POST /api/v1/ia/clients` - crear cliente IA
- [ ] `PUT /api/v1/ia/clients/{id}` - actualizar configuracion
- [ ] `DELETE /api/v1/ia/clients/{id}` - desactivar cliente (soft delete)
- [ ] Validaciones: nombre requerido, client_id unico, config valida

**Tareas Tecnicas:**
- [ ] Blueprint de Flask con endpoints CRUD
- [ ] Servicio `IAClientService` con logica de negocio
- [ ] Modelo DynamoDB: PK=`IACLIENT#{id}`, SK=`META`
- [ ] Tests: 10+ unit tests

---

#### US-IA-062: Busqueda y filtrado de clientes IA

**Como** administrador con muchos clientes
**Quiero** buscar y filtrar clientes por nombre, estado del bot, y canales activos
**Para** encontrar rapidamente el cliente que necesito configurar

**Criterios de Aceptacion:**
- [ ] Barra de busqueda por nombre (client-side filtering)
- [ ] Filtros: estado del bot (activo/inactivo), canal (web/WhatsApp/ambos), tiene funnels (si/no)
- [ ] Ordenar por: nombre, fecha alta, ultima actividad
- [ ] Resultados se actualizan en tiempo real al escribir/filtrar
- [ ] Persistir filtros en URL query params

**Tareas Tecnicas:**
- [ ] Componente de filtros con reactive forms
- [ ] Pipe o servicio de filtrado
- [ ] Tests: 5+ unit tests

---

### EP-IA-012: Motor de Funnels de Venta

---

#### US-IA-063: Modelos Pydantic de funnels en covacha-libs

**Como** arquitecto del sistema
**Quiero** modelos de datos robustos y compartidos para funnels de venta
**Para** consistencia entre covacha-botia, covacha-core y frontends

**Criterios de Aceptacion:**
- [ ] `SalesFunnel`: id, client_id, name, description, channel (email/whatsapp), status (draft/active/paused/archived), steps[], triggers[], created_at, updated_at
- [ ] `FunnelStep`: id, funnel_id, order, type (send_email/send_whatsapp/wait/condition/chain), config{template_id, subject, body}, delay_config{amount, unit}, schedule{timezone, hours_start, hours_end, days[]}, recurrence (once/daily/weekly/monthly/infinite)
- [ ] `FunnelExecution`: id, funnel_id, lead_id, client_id, current_step_index, status (active/completed/paused/unsubscribed), started_at, next_execution_at, history[]
- [ ] `FunnelChain`: source_funnel_id, target_funnel_id, condition{type, field, operator, value}
- [ ] `FunnelMetrics`: funnel_id, period, leads_entered, leads_completed, leads_unsubscribed, conversion_rate, avg_completion_time
- [ ] Validaciones Pydantic con validators para timezone, horarios, recurrencia

**Tareas Tecnicas:**
- [ ] Crear modelos en covacha-libs/covacha_libs/models/funnels/
- [ ] Exportar en __init__.py
- [ ] Tests: 12+ unit tests (validaciones, serializacion, edge cases)

---

#### US-IA-064: Funnel Executor en covacha-botia

**Como** sistema
**Quiero** un executor que procese funnels paso a paso para cada lead
**Para** automatizar la comunicacion post-lead segun la configuracion del funnel

**Criterios de Aceptacion:**
- [ ] Recibe trigger (lead_id, funnel_id) y crea FunnelExecution
- [ ] Ejecuta el primer step inmediatamente si delay=0
- [ ] Programa el siguiente step segun delay_config
- [ ] Respeta schedule (timezone, horarios, dias de semana)
- [ ] Si step falla (email no enviado), reintenta 3 veces con backoff
- [ ] Si lead se desuscribe, marca execution como `unsubscribed` y para
- [ ] Registra historial de cada step ejecutado

**Tareas Tecnicas:**
- [ ] Crear `FunnelExecutorService` en covacha-botia
- [ ] Usar SQS o DynamoDB streams para async execution
- [ ] Dead letter queue para fallos permanentes
- [ ] Tests: 12+ unit tests (happy path, fallos, desuscripcion, timezone)

---

#### US-IA-065: Funnel Scheduler (cron de ejecuciones)

**Como** sistema
**Quiero** un scheduler que revise cada minuto si hay ejecuciones de funnel pendientes
**Para** enviar comunicaciones en el momento correcto segun la configuracion

**Criterios de Aceptacion:**
- [ ] Cron cada 1 minuto: busca FunnelExecution con `next_execution_at <= now` y `status=active`
- [ ] Valida que la hora actual esta dentro del horario de envio configurado
- [ ] Si fuera de horario, recalcula `next_execution_at` al proximo slot valido
- [ ] Procesa maximo 100 executions por ciclo (batch processing)
- [ ] Lock distribuido para evitar procesamiento duplicado en multi-instancia
- [ ] Logging detallado de cada ejecucion
- [ ] Metricas: executions procesadas, pendientes, fallidas

**Tareas Tecnicas:**
- [ ] Crear `FunnelSchedulerService` con APScheduler o cron de sistema
- [ ] Lock con DynamoDB conditional writes
- [ ] Batch processing con paginacion
- [ ] Tests: 10+ unit tests (horarios, timezone, locks, batch)

---

#### US-IA-066: Templates de funnel predefinidos

**Como** administrador del cliente
**Quiero** plantillas de funnel predefinidas que pueda usar como punto de partida
**Para** crear funnels rapidamente sin disenarlos desde cero

**Criterios de Aceptacion:**
- [ ] Template "Email - Bienvenida y seguimiento" (funnel por defecto)
- [ ] Template "WhatsApp - Contacto rapido"
- [ ] Template "Email - Reactivacion de leads frios"
- [ ] Template "WhatsApp - Recordatorio de cita"
- [ ] Cada template incluye: nombre, descripcion, steps preconfigurados, sugerencias de contenido
- [ ] Boton "Usar template" que crea funnel con los datos pre-llenados
- [ ] Templates editables despues de crear el funnel

**Tareas Tecnicas:**
- [ ] Seed de templates en DynamoDB
- [ ] Endpoint `GET /api/v1/ia/funnel-templates`
- [ ] UI de seleccion de template en mf-ia
- [ ] Tests: 5+ unit tests

---

#### US-IA-067: CRUD de funnels en covacha-botia

**Como** sistema (mf-ia, mf-marketing)
**Quiero** endpoints CRUD completos para gestionar funnels de venta
**Para** crear, editar, activar y archivar funnels desde la UI

**Criterios de Aceptacion:**
- [ ] `GET /api/v1/ia/clients/{client_id}/funnels` - listar funnels del cliente
- [ ] `GET /api/v1/ia/funnels/{id}` - detalle del funnel con steps
- [ ] `POST /api/v1/ia/clients/{client_id}/funnels` - crear funnel (desde template o custom)
- [ ] `PUT /api/v1/ia/funnels/{id}` - actualizar funnel (solo si status=draft o paused)
- [ ] `POST /api/v1/ia/funnels/{id}/activate` - activar funnel
- [ ] `POST /api/v1/ia/funnels/{id}/pause` - pausar funnel
- [ ] `DELETE /api/v1/ia/funnels/{id}` - archivar funnel (soft delete)
- [ ] Validaciones: steps validos, al menos 1 step de envio, template_id valido

**Tareas Tecnicas:**
- [ ] Blueprint de Flask con endpoints CRUD
- [ ] Servicio `FunnelService` con validaciones
- [ ] Tests: 12+ unit tests

---

#### US-IA-068: UI de creacion de funnel en mf-ia

**Como** administrador del cliente
**Quiero** un wizard para crear y configurar funnels de venta paso a paso
**Para** disenar flujos de comunicacion sin necesidad de codigo

**Criterios de Aceptacion:**
- [ ] Wizard de 4 pasos:
  1. Seleccionar template o empezar desde cero
  2. Configurar canal (email/WhatsApp) + datos generales (nombre, descripcion)
  3. Configurar steps: agregar/eliminar/reordenar steps, configurar delay, horario, recurrencia
  4. Preview del funnel completo + activar
- [ ] Drag and drop para reordenar steps
- [ ] Preview de email/WhatsApp en cada step
- [ ] Validacion en tiempo real (step sin template, delay negativo, etc.)
- [ ] Guardar como borrador en cualquier paso

**Tareas Tecnicas:**
- [ ] Componentes standalone por cada paso del wizard
- [ ] Angular CDK drag-drop para steps
- [ ] Reactive forms con validacion
- [ ] Tests: 8+ unit tests

---

#### US-IA-069: Funnel chaining con condiciones

**Como** administrador del cliente
**Quiero** conectar funnels entre si con condiciones de transicion
**Para** crear flujos de conversion complejos (ej: funnel pagina → funnel promociones)

**Criterios de Aceptacion:**
- [ ] En cada step, opcion "Si condicion → enviar a otro funnel"
- [ ] Condiciones disponibles: email abierto, click en link, respondio WhatsApp, tiempo transcurrido, custom field
- [ ] Solo se puede chain entre funnels del mismo canal
- [ ] Limite de 5 chains en cadena (anti-loop)
- [ ] Vista visual simplificada de chains (grafo)
- [ ] El lead mantiene historial de todos los funnels por los que paso

**Tareas Tecnicas:**
- [ ] Modelo FunnelChain con condiciones
- [ ] Evaluador de condiciones en executor
- [ ] UI de configuracion de chains
- [ ] Detector de loops
- [ ] Tests: 10+ unit tests

---

#### US-IA-070: Desuscripcion y opt-out por canal

**Como** lead que recibe comunicaciones
**Quiero** poder desuscribirme facilmente
**Para** dejar de recibir mensajes si no me interesan

**Criterios de Aceptacion:**
- [ ] Email: link de desuscripcion en footer de cada email
- [ ] WhatsApp: escribir "STOP" o "DESUSCRIBIRME" para dejar de recibir
- [ ] Al desuscribirse, se marca la FunnelExecution como `unsubscribed`
- [ ] No se puede reactivar automaticamente (requiere accion manual del admin)
- [ ] Dashboard muestra tasa de desuscripcion por funnel
- [ ] Cumplimiento de CAN-SPAM y regulaciones de email marketing

**Tareas Tecnicas:**
- [ ] Endpoint de desuscripcion con token unico
- [ ] Handler de STOP en bot WhatsApp
- [ ] Tests: 6+ unit tests

---

#### US-IA-071: Dashboard de funnels en mf-ia

**Como** administrador del cliente
**Quiero** ver el estado y metricas de todos los funnels del cliente
**Para** optimizar la estrategia de conversion

**Criterios de Aceptacion:**
- [ ] Lista de funnels con: nombre, canal, status, leads activos, conversion rate
- [ ] Por funnel: grafico de embudo (leads por step), timeline de ejecuciones
- [ ] Metricas globales: total leads en funnels, tasa conversion, desuscripciones
- [ ] Filtros por periodo, canal, status
- [ ] Acciones rapidas: activar, pausar, archivar, duplicar

**Tareas Tecnicas:**
- [ ] Componentes de dashboard con graficos
- [ ] Endpoints de metricas en covacha-botia
- [ ] Tests: 6+ unit tests

---

#### US-IA-072: Log de ejecuciones de funnel

**Como** administrador del cliente
**Quiero** ver el log detallado de cada ejecucion de funnel
**Para** debuggear problemas y entender el flujo de cada lead

**Criterios de Aceptacion:**
- [ ] Lista de ejecuciones con: lead, funnel, step actual, status, timestamps
- [ ] Click en ejecucion muestra timeline completa: step ejecutados, timestamps, resultados
- [ ] Filtros: por lead, por funnel, por status, por fecha
- [ ] Acciones: pausar ejecucion, reiniciar desde step N, cancelar
- [ ] Export a CSV

**Tareas Tecnicas:**
- [ ] Endpoint `GET /api/v1/ia/funnels/{id}/executions`
- [ ] Componente de log con timeline
- [ ] Tests: 5+ unit tests

---

### EP-IA-013: Canal Email en Funnels

---

#### US-IA-073: Servicio de envio de email (SES/SMTP)

**Como** sistema (motor de funnels)
**Quiero** un servicio que envie emails transaccionales y de marketing
**Para** ejecutar los steps de email en los funnels

**Criterios de Aceptacion:**
- [ ] Soporte para AWS SES y SMTP generico
- [ ] Configuracion por cliente: from_address, reply_to, provider (SES/SMTP)
- [ ] Envio con templates HTML + texto plano
- [ ] Variables dinamicas: {nombre}, {email}, {promo_titulo}, {link_landing}, {link_unsub}
- [ ] Tracking de apertura (pixel) y clicks (link wrapping)
- [ ] Rate limiting por cuenta SES/SMTP
- [ ] Retry con exponential backoff (3 intentos)

**Tareas Tecnicas:**
- [ ] Crear `EmailService` en covacha-botia
- [ ] Adapter para SES y SMTP
- [ ] Template engine con variables
- [ ] Tests: 10+ unit tests

---

#### US-IA-074: Templates de email configurables

**Como** administrador del cliente
**Quiero** crear y editar templates de email para usar en funnels
**Para** personalizar la comunicacion sin necesidad de HTML

**Criterios de Aceptacion:**
- [ ] Editor visual simple (WYSIWYG) para templates
- [ ] Templates predefinidos: bienvenida, follow-up, info valor, nueva promocion
- [ ] Variables dinamicas visibles como chips editables
- [ ] Preview en desktop y mobile
- [ ] Guardar/duplicar templates
- [ ] Templates del brand kit del cliente (colores, logo)

**Tareas Tecnicas:**
- [ ] Componente editor de email en mf-ia
- [ ] Almacenamiento de templates en DynamoDB
- [ ] Tests: 6+ unit tests

---

#### US-IA-075: Email de bienvenida al lead

**Como** lead que lleno formulario de promocion
**Quiero** recibir un email de bienvenida inmediatamente
**Para** saber que mi solicitud fue recibida y que esperar

**Criterios de Aceptacion:**
- [ ] Se envia automaticamente al crear el lead (trigger del funnel por defecto)
- [ ] Incluye: nombre del lead, nombre de la promocion, datos de contacto del equipo
- [ ] Diseño profesional con brand kit del cliente
- [ ] Boton CTA: "Ver la promocion" (link a landing)
- [ ] Link de desuscripcion en footer
- [ ] Personalizado con nombre del lead

**Tareas Tecnicas:**
- [ ] Template por defecto "welcome" en seed
- [ ] Integracion con trigger del funnel executor
- [ ] Tests: 5+ unit tests

---

#### US-IA-076: Email de notificacion al equipo

**Como** miembro del equipo de ventas
**Quiero** recibir una notificacion cuando llega un nuevo lead desde una promocion
**Para** contactar al prospecto rapidamente

**Criterios de Aceptacion:**
- [ ] Se envia a las personas configuradas como "equipo de notificacion" del cliente
- [ ] Incluye: datos del lead (nombre, email, telefono), promocion de origen, mensaje del lead
- [ ] Boton CTA: "Ver lead en CRM" (link a mf-marketing)
- [ ] Se envia como step del funnel por defecto (step 2, delay=0)
- [ ] Configurable: a quienes se notifica, si se notifica o no

**Tareas Tecnicas:**
- [ ] Configuracion de equipo de notificacion por cliente
- [ ] Template "team_notification" en seed
- [ ] Tests: 5+ unit tests

---

#### US-IA-077: Configuracion de correo de salida por cliente

**Como** administrador del cliente
**Quiero** configurar el correo de salida (from address) para emails del funnel
**Para** que los leads reciban emails desde el dominio del cliente

**Criterios de Aceptacion:**
- [ ] Campo "Email de salida" en configuracion del cliente IA
- [ ] Validacion de dominio: verificar que el dominio esta configurado en SES
- [ ] Si no hay dominio verificado, usar dominio por defecto del sistema
- [ ] Campo "Reply-to" configurable
- [ ] Nombre del remitente configurable (ej: "Equipo BaatDigital")
- [ ] Test de envio para verificar configuracion

**Tareas Tecnicas:**
- [ ] UI de configuracion en mf-ia
- [ ] Verificacion de dominio SES via API
- [ ] Tests: 5+ unit tests

---

#### US-IA-078: Tracking de apertura y clicks en emails

**Como** administrador del cliente
**Quiero** saber cuantos leads abrieron los emails y hicieron click en links
**Para** medir la efectividad de cada step del funnel

**Criterios de Aceptacion:**
- [ ] Pixel de tracking invisible en cada email (1x1 gif)
- [ ] Links envueltos para tracking de clicks
- [ ] Metricas por step: tasa apertura, tasa click, tiempo hasta apertura
- [ ] Metricas agregadas por funnel
- [ ] Los datos de tracking se usan como condiciones para funnel chaining
- [ ] Respeta Do-Not-Track si el lead lo solicita

**Tareas Tecnicas:**
- [ ] Endpoint de pixel tracking
- [ ] Servicio de link wrapping
- [ ] Almacenamiento de eventos en DynamoDB
- [ ] Tests: 8+ unit tests

---

#### US-IA-079: Programacion de envio con timezone y horarios

**Como** administrador del cliente
**Quiero** que los emails se envien dentro de un horario y timezone especifico
**Para** no enviar emails a horas inapropiadas (ej: 3am)

**Criterios de Aceptacion:**
- [ ] Configurar timezone por funnel (dropdown con todas las zonas horarias)
- [ ] Configurar ventana de envio: hora inicio, hora fin (ej: 9:00 - 18:00)
- [ ] Configurar dias de la semana (ej: lunes a viernes)
- [ ] Si el envio cae fuera de ventana, postergar al proximo slot valido
- [ ] Preview del calendario de envio para los proximos 30 dias
- [ ] Soporte para multiples timezones en el mismo funnel (si leads de diferentes zonas)

**Tareas Tecnicas:**
- [ ] Logica de timezone en scheduler (pytz/zoneinfo)
- [ ] Calculo de proximo slot valido
- [ ] Componente de preview de calendario
- [ ] Tests: 10+ unit tests (DST, edge cases, multiples zonas)

---

### EP-IA-014: Canal WhatsApp en Funnels

---

#### US-IA-080: Adapter WhatsApp para funnels

**Como** sistema (motor de funnels)
**Quiero** un adapter que envie mensajes WhatsApp usando templates aprobados por Meta
**Para** ejecutar los steps de WhatsApp en los funnels

**Criterios de Aceptacion:**
- [ ] Usa la integracion WhatsApp Business existente de covacha-botia
- [ ] Envio de templates con variables dinamicas
- [ ] Soporte para templates con botones, imagenes, videos
- [ ] Manejo de errores: template no aprobado, numero invalido, limite de envio
- [ ] Retry con backoff (3 intentos)
- [ ] Logging de envios exitosos y fallidos

**Tareas Tecnicas:**
- [ ] Crear `WhatsAppFunnelAdapter` que reutiliza logica existente
- [ ] Mapping de variables del funnel a variables del template
- [ ] Tests: 8+ unit tests

---

#### US-IA-081: Seleccion de templates WhatsApp en funnel steps

**Como** administrador del cliente
**Quiero** seleccionar templates de WhatsApp aprobados para cada step del funnel
**Para** usar mensajes pre-aprobados por Meta en la comunicacion automatizada

**Criterios de Aceptacion:**
- [ ] Dropdown con templates aprobados del cliente (sincronizados de Meta)
- [ ] Preview del template con variables resaltadas
- [ ] Mapping de variables: cuales campos del lead llenan cada variable
- [ ] Warning si el template no esta aprobado o esta en revision
- [ ] Si no hay templates aprobados, instrucciones para crear y aprobar en Meta

**Tareas Tecnicas:**
- [ ] Endpoint de listado de templates aprobados
- [ ] UI de seleccion con preview
- [ ] Tests: 6+ unit tests

---

#### US-IA-082: Bot atiende respuestas del lead en funnel WhatsApp

**Como** lead que recibe un mensaje de WhatsApp del funnel
**Quiero** que si respondo, el bot del cliente me atienda
**Para** tener una conversacion natural en lugar de solo recibir mensajes unidireccionales

**Criterios de Aceptacion:**
- [ ] Si el lead responde a un mensaje del funnel, el bot de covacha-botia atiende
- [ ] El bot tiene contexto del funnel activo y la promocion asociada
- [ ] El bot puede: responder preguntas, capturar datos adicionales, escalar a humano
- [ ] La respuesta del lead se registra en la FunnelExecution como evento
- [ ] Si el lead pide hablar con humano, se notifica al equipo

**Tareas Tecnicas:**
- [ ] Context injection de funnel activo en sesion de bot
- [ ] Handler de respuestas en funnel execution
- [ ] Tests: 8+ unit tests

---

#### US-IA-083: Handler de STOP en WhatsApp

**Como** lead que no quiere recibir mas mensajes
**Quiero** escribir "STOP" y dejar de recibir mensajes del funnel
**Para** desuscribirme facilmente

**Criterios de Aceptacion:**
- [ ] Keywords de desuscripcion: "STOP", "PARAR", "DESUSCRIBIRME", "NO MAS"
- [ ] Bot confirma: "Has sido desuscrito. No recibiras mas mensajes de esta promocion."
- [ ] FunnelExecution se marca como `unsubscribed`
- [ ] No se envian mas mensajes de ningun funnel a ese numero (para esa promocion)
- [ ] Admin puede ver leads desuscritos en dashboard

**Tareas Tecnicas:**
- [ ] NLU intent para desuscripcion
- [ ] Logica de desuscripcion en executor
- [ ] Tests: 5+ unit tests

---

#### US-IA-084: Templates WhatsApp predefinidos para funnels

**Como** administrador del cliente
**Quiero** plantillas de WhatsApp listas para aprobar en Meta Business
**Para** empezar rapidamente con funnels de WhatsApp

**Criterios de Aceptacion:**
- [ ] Plantillas predefinidas: bienvenida, follow-up, info de valor, nueva promocion, recordatorio
- [ ] Formato compatible con Meta Business (header, body, footer, botones)
- [ ] Variables marcadas como {{1}}, {{2}} con descripcion de que va en cada una
- [ ] Instrucciones paso a paso para aprobar en Meta Business Manager
- [ ] Boton "Copiar plantilla" para pegar en Meta

**Tareas Tecnicas:**
- [ ] Seed de plantillas en DynamoDB
- [ ] UI de visualizacion y copia
- [ ] Tests: 4+ unit tests

---

#### US-IA-085: Estrategia de comunicacion WhatsApp (misma que email)

**Como** administrador del cliente
**Quiero** que los funnels de WhatsApp tengan la misma logica de configuracion que email
**Para** consistencia en la experiencia de configuracion

**Criterios de Aceptacion:**
- [ ] Misma configuracion de frecuencia, timezone, horarios, dias
- [ ] Misma logica de recurrencia (once, weekly, monthly, infinite)
- [ ] Misma logica de funnel chaining (solo WhatsApp → WhatsApp)
- [ ] Mismo dashboard de metricas con datos de WhatsApp
- [ ] Funnel por defecto de WhatsApp (template bienvenida + notif equipo + follow-up)

**Tareas Tecnicas:**
- [ ] Reutilizar componentes de configuracion de email
- [ ] Adapter pattern para abstraccion de canal
- [ ] Tests: 5+ unit tests

---

#### US-IA-086: Metricas de WhatsApp en funnels

**Como** administrador del cliente
**Quiero** ver metricas especificas de WhatsApp en los funnels
**Para** medir la efectividad del canal WhatsApp

**Criterios de Aceptacion:**
- [ ] Metricas por step: mensajes enviados, entregados, leidos, respondidos
- [ ] Tasa de respuesta por template
- [ ] Leads que respondieron vs leads silenciosos
- [ ] Costo de mensajes (si aplica por volumen)
- [ ] Comparativa WhatsApp vs Email (si hay funnels de ambos canales)

**Tareas Tecnicas:**
- [ ] Tracking de eventos de WhatsApp (webhook de Meta)
- [ ] Endpoints de metricas
- [ ] Tests: 5+ unit tests

---

### EP-IA-015: Tests 100% covacha-botia

---

#### US-IA-087: Tests unitarios para todos los servicios existentes de covacha-botia

**Como** equipo de desarrollo
**Quiero** tests unitarios para cada servicio que existe actualmente en covacha-botia
**Para** tener coverage de 100% antes de agregar funcionalidad nueva

**Criterios de Aceptacion:**
- [ ] Coverage actual medido y reportado como baseline
- [ ] Test para cada metodo publico de cada servicio
- [ ] Happy path + al menos 1 error case + edge cases
- [ ] Mocks para dependencias externas (WhatsApp API, DynamoDB, LLM)
- [ ] Coverage >= 100% en servicios

**Tareas Tecnicas:**
- [ ] Auditoria de servicios existentes sin tests
- [ ] Crear test suites por servicio
- [ ] Tests: variable (depende de codigo existente)

---

#### US-IA-088: Tests unitarios para motor de funnels

**Como** equipo de desarrollo
**Quiero** tests completos para el motor de funnels (executor, scheduler, adapters)
**Para** garantizar que la logica critica de funnels es correcta

**Criterios de Aceptacion:**
- [ ] FunnelExecutor: 15+ tests (happy path, fallos, retry, desuscripcion, chain)
- [ ] FunnelScheduler: 10+ tests (timezone, horarios, batch, locks)
- [ ] EmailAdapter: 8+ tests (envio, tracking, retry, variables)
- [ ] WhatsAppAdapter: 8+ tests (template, envio, respuesta, stop)
- [ ] FunnelService CRUD: 12+ tests
- [ ] Coverage >= 100%

**Tareas Tecnicas:**
- [ ] Fixtures de funnels de prueba
- [ ] Mocks de SES, WhatsApp API, DynamoDB
- [ ] Tests: 53+ unit tests

---

#### US-IA-089: Tests de integracion para flujos de funnel

**Como** equipo de QA
**Quiero** tests de integracion que validen flujos completos de funnel
**Para** detectar problemas en la interaccion entre componentes

**Criterios de Aceptacion:**
- [ ] Test: crear funnel → activar → trigger con lead → ejecutar steps → completar
- [ ] Test: funnel con chain → condicion cumplida → transicion a otro funnel
- [ ] Test: recurrencia infinita → 3 ciclos → desuscripcion → parar
- [ ] Test: timezone y horarios → envio fuera de ventana → postergar
- [ ] Test: WhatsApp → lead responde → bot atiende → captura datos
- [ ] Usar DynamoDB local o mocks realistas

**Tareas Tecnicas:**
- [ ] Setup de DynamoDB local para tests de integracion
- [ ] Fixtures complejas de funnels multi-step
- [ ] Tests: 15+ integracion

---

#### US-IA-090: Tests unitarios para endpoints/controllers existentes

**Como** equipo de desarrollo
**Quiero** tests para cada endpoint de la API de covacha-botia
**Para** garantizar que las respuestas son correctas y los errores manejados

**Criterios de Aceptacion:**
- [ ] Test para cada endpoint: request valido → response correcta
- [ ] Test para cada endpoint: request invalido → error apropiado (400, 404, 422)
- [ ] Test de autenticacion: sin token → 401
- [ ] Test de paginacion, filtros, sorting
- [ ] Coverage >= 100% en controllers

**Tareas Tecnicas:**
- [ ] Flask test client con fixtures
- [ ] Tests: variable (depende de endpoints existentes)

---

#### US-IA-091: Tests unitarios para modelos y utilidades

**Como** equipo de desarrollo
**Quiero** tests para todos los modelos Pydantic y utilidades de covacha-botia
**Para** garantizar validaciones correctas y serializacion confiable

**Criterios de Aceptacion:**
- [ ] Modelos: validaciones, serializacion/deserializacion, defaults
- [ ] Utilidades: funciones helper, formatters, parsers
- [ ] Edge cases: valores nulos, strings vacios, fechas invalidas, timezones incorrectas
- [ ] Coverage >= 100%

**Tareas Tecnicas:**
- [ ] Tests por archivo de modelo
- [ ] Tests: variable

---

#### US-IA-092: CI/CD con coverage gate

**Como** equipo de desarrollo
**Quiero** que el CI/CD falle si la cobertura de tests baja del umbral
**Para** mantener la calidad a lo largo del tiempo

**Criterios de Aceptacion:**
- [ ] GitHub Action que corre `pytest --cov` en cada push
- [ ] Coverage minimo: 98% para merge a develop
- [ ] Reporte de coverage como comentario en PR
- [ ] Badge de coverage en README
- [ ] Coverage per-file visible en el reporte

**Tareas Tecnicas:**
- [ ] Configurar pytest-cov
- [ ] GitHub Action con coverage gate
- [ ] Tests: N/A (es configuracion)

---

### EP-IA-016: Tests 100% mf-ia + E2E

---

#### US-IA-093: Tests unitarios para componentes existentes de mf-ia

**Como** equipo de desarrollo
**Quiero** tests Karma+Jasmine para cada componente que existe en mf-ia
**Para** tener coverage de 95%+ antes de agregar funcionalidad nueva

**Criterios de Aceptacion:**
- [ ] Coverage actual medido y reportado como baseline
- [ ] Test para cada componente: render, inputs/outputs, user interactions
- [ ] Test para cada servicio: metodos publicos, observables, error handling
- [ ] Test para pipes y guards
- [ ] Coverage >= 95%

**Tareas Tecnicas:**
- [ ] Auditoria de componentes sin tests
- [ ] Crear test suites por componente/servicio
- [ ] Tests: variable

---

#### US-IA-094: Tests unitarios para componentes nuevos (funnels, clientes)

**Como** equipo de desarrollo
**Quiero** tests para todos los componentes nuevos de gestion de clientes y funnels
**Para** garantizar que la nueva funcionalidad es robusta

**Criterios de Aceptacion:**
- [ ] ClientListComponent: 6+ tests
- [ ] ClientSyncComponent: 5+ tests
- [ ] FunnelWizardComponent: 8+ tests
- [ ] FunnelDashboardComponent: 5+ tests
- [ ] FunnelExecutionLogComponent: 5+ tests
- [ ] EmailTemplateEditorComponent: 5+ tests
- [ ] Coverage >= 95% en componentes nuevos

**Tareas Tecnicas:**
- [ ] Test suites por componente nuevo
- [ ] Mocks de servicios HTTP
- [ ] Tests: 34+ unit tests

---

#### US-IA-095: Tests E2E de gestion de clientes

**Como** QA
**Quiero** tests E2E que validen el flujo completo de gestion de clientes en mf-ia
**Para** garantizar que la funcionalidad critica funciona end-to-end

**Criterios de Aceptacion:**
- [ ] E2E: Navegar a mf-ia → ver lista de clientes → buscar → seleccionar
- [ ] E2E: Sincronizar cliente desde marketing → aparece en lista
- [ ] E2E: Seleccionar cliente → ver dashboard → navegar a otra seccion → cliente persiste
- [ ] E2E: Cliente sin bot → mostrar wizard de configuracion
- [ ] Playwright con CI integration

**Tareas Tecnicas:**
- [ ] Configurar Playwright para mf-ia
- [ ] Page objects para paginas principales
- [ ] Tests: 5+ E2E scenarios

---

#### US-IA-096: Tests E2E de funnels de venta

**Como** QA
**Quiero** tests E2E del flujo completo de funnels: crear → configurar → activar → verificar ejecucion
**Para** garantizar que los funnels funcionan de punta a punta

**Criterios de Aceptacion:**
- [ ] E2E: Crear funnel desde template → configurar steps → activar
- [ ] E2E: Lead llena formulario → funnel se activa → primer email se programa
- [ ] E2E: Pausar funnel → verificar que no se ejecutan mas steps
- [ ] E2E: Desuscripcion → verificar que se para el funnel para ese lead
- [ ] E2E: Funnel chaining → condicion cumplida → lead pasa al siguiente funnel

**Tareas Tecnicas:**
- [ ] Fixtures de funnels para E2E
- [ ] Mock de email/WhatsApp para verificar envios
- [ ] Tests: 6+ E2E scenarios

---

#### US-IA-097: Tests E2E de integracion chatbot + promociones

**Como** QA
**Quiero** tests E2E que validen que el chatbot entiende promociones
**Para** garantizar la integracion entre promociones y el bot

**Criterios de Aceptacion:**
- [ ] E2E: Sync promocion a knowledge base → preguntar al bot → responde correctamente
- [ ] E2E: Bot en landing → preguntar por la promocion → datos correctos
- [ ] E2E: Bot por WhatsApp → "que promociones tienen?" → lista vigentes
- [ ] E2E: Promocion vence → bot ya no la menciona

**Tareas Tecnicas:**
- [ ] Mock de API de bot para E2E
- [ ] Tests: 4+ E2E scenarios

---

#### US-IA-098: CI/CD con coverage gate para mf-ia

**Como** equipo de desarrollo
**Quiero** que el CI/CD falle si la cobertura de tests de mf-ia baja del umbral
**Para** mantener la calidad del frontend a lo largo del tiempo

**Criterios de Aceptacion:**
- [ ] GitHub Action que corre `ng test --code-coverage` en cada push
- [ ] Coverage minimo: 90% para merge a develop
- [ ] Reporte de coverage como comentario en PR
- [ ] Coverage per-component visible en el reporte
- [ ] E2E ejecutados en PR (Playwright en headless mode)

**Tareas Tecnicas:**
- [ ] Configurar karma-coverage
- [ ] Configurar Playwright en CI
- [ ] GitHub Action con coverage gate + E2E
- [ ] Tests: N/A (es configuracion)

---

## Estrategia de Testing

### Backend (covacha-botia)

| Tipo | Framework | Coverage | Enfoque |
|------|-----------|---------|---------|
| Unitarios | pytest + pytest-cov | 100% | Servicios, endpoints, modelos, utilidades |
| Integracion | pytest + DynamoDB local | 95% | Flujos de funnel completos |
| E2E | pytest + requests | N/A | API end-to-end |

### Frontend (mf-ia)

| Tipo | Framework | Coverage | Enfoque |
|------|-----------|---------|---------|
| Unitarios | Karma + Jasmine | 95% | Componentes, servicios, pipes, guards |
| E2E | Playwright | N/A | Flujos de usuario completos |

### Prioridad de Tests

1. **Motor de funnels** (critico, logica compleja)
2. **Endpoints CRUD** (integracion con frontend)
3. **Componentes de UI** (experiencia de usuario)
4. **Scheduling y timezone** (edge cases peligrosos)
5. **Integracion email/WhatsApp** (servicios externos)

---

## Roadmap

### Sprint 1 (6 dias): EP-IA-011 - Clientes
- Dia 1-2: Reparar listado + API CRUD
- Dia 3: Sync desde marketing + current_sp_client_id
- Dia 4: Dashboard de cliente
- Dia 5: Busqueda y filtrado
- Dia 6: Tests unitarios completos

### Sprint 2 (6 dias): EP-IA-012 - Motor de Funnels (parte 1)
- Dia 1-2: Modelos Pydantic + DynamoDB
- Dia 3-4: Funnel Executor + Scheduler
- Dia 5: Templates predefinidos + CRUD endpoints
- Dia 6: Tests unitarios

### Sprint 3 (6 dias): EP-IA-012 (parte 2) + EP-IA-013 Email
- Dia 1-2: UI wizard de funnel + drag-drop steps
- Dia 3: Funnel chaining + desuscripcion
- Dia 4: Servicio email SES/SMTP + templates
- Dia 5: Tracking + timezone scheduling
- Dia 6: Tests unitarios + integracion

### Sprint 4 (6 dias): EP-IA-014 WhatsApp + EP-IA-015/016 Tests
- Dia 1-2: Adapter WhatsApp + templates + bot respuestas
- Dia 3: Dashboard de funnels + metricas
- Dia 4-5: Tests unitarios 100% covacha-botia
- Dia 6: Tests E2E mf-ia + CI/CD coverage gates

---

## Grafo de Dependencias

```
EP-IA-001 (Orquestador - planificada)
    │
    ▼
EP-IA-011 (Gestion Clientes)
    │
    ├──► EP-IA-012 (Motor de Funnels)
    │       │
    │       ├──► EP-IA-013 (Canal Email)
    │       │       │
    │       │       └──► EP-MK-028 (Funnels en Marketing)
    │       │
    │       ├──► EP-IA-014 (Canal WhatsApp)
    │       │       │
    │       │       └──► EP-MK-028 (Funnels en Marketing)
    │       │
    │       └──► EP-MK-029 (Chatbot + Promociones)
    │
    ├──► EP-IA-015 (Tests covacha-botia)
    │
    └──► EP-IA-016 (Tests mf-ia + E2E)

EP-MK-026 (Promociones BD)
    │
    ├──► EP-MK-027 (Landing Ventas)
    │       │
    │       └──► EP-MK-029 (Chatbot + Promociones)
    │
    └──► EP-MK-028 (Funnels Marketing)
            │
            └──► EP-IA-012 + EP-IA-013 + EP-IA-014
```

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|------------|
| SES sandbox limita envios | Alta | Bloquea funnels email en dev | Solicitar produccion SES temprano |
| Templates WhatsApp no aprobados | Media | Bloquea funnels WhatsApp | Templates genericos pre-aprobados |
| Timezone bugs con DST | Media | Envios a horas incorrectas | Usar zoneinfo (no pytz deprecated), tests exhaustivos |
| Funnel loops infinitos | Baja | CPU/costos excesivos | Limite de 5 chains + rate limiting |
| Cobertura 100% inalcanzable | Baja | Meta no cumplida | Exclusiones documentadas (generated code, config) |
| Performance con muchas executions | Media | Scheduler lento | Batch processing + indices DynamoDB |
| mf-ia clientes roto por cambio en API | Alta | Feature no funciona | Reparar como primera prioridad |
