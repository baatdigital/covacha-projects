# AlertaTribunal - Epicas de Alertas Judiciales (EP-AT-001 a EP-AT-008)

**Fecha**: 2026-02-16
**Product Owner**: AlertaTribunal
**Estado**: Planificacion
**Prefijo Epicas**: EP-AT
**Prefijo User Stories**: US-AT
**Prioridad del Producto**: P2
**Dominio**: alertatribunal.com, app.alertatribunal.com
**Tenant**: AlertaTribunal (independiente de SuperPago y BaatDigital)

---

## Tabla de Contenidos

1. [Contexto y Motivacion](#contexto-y-motivacion)
2. [Roles Involucrados](#roles-involucrados)
3. [Arquitectura del Sistema](#arquitectura-del-sistema)
4. [Modelo de Datos DynamoDB](#modelo-de-datos-dynamodb)
5. [Mapa de Epicas](#mapa-de-epicas)
6. [Epicas Detalladas](#epicas-detalladas)
7. [User Stories Detalladas](#user-stories-detalladas)
8. [Roadmap](#roadmap)
9. [Grafo de Dependencias](#grafo-de-dependencias)
10. [Riesgos y Mitigaciones](#riesgos-y-mitigaciones)
11. [Definition of Done Global](#definition-of-done-global)

---

## Contexto y Motivacion

AlertaTribunal es un servicio de alertas judiciales automatizadas para abogados y despachos juridicos en Mexico. El problema que resuelve es critico: los profesionales del derecho deben monitorear manualmente los portales de tribunales para detectar movimientos en sus expedientes (acuerdos, sentencias, audiencias, notificaciones). Este proceso es tedioso, propenso a errores y consume horas de trabajo diario.

AlertaTribunal automatiza este monitoreo mediante:

- **Scraping inteligente** de portales de tribunales (iniciando con Poder Judicial de Nuevo Leon)
- **Deteccion de cambios** en expedientes monitoreados
- **Alertas multi-canal** (email, WhatsApp, in-app) cuando hay movimientos relevantes
- **Suscripciones configurables** por expediente, tipo de evento y frecuencia
- **Analisis IA** de documentos judiciales para extraer informacion clave
- **Monetizacion** con planes de suscripcion escalonados

### Repositorios Involucrados

| Repositorio | Funcion | Puerto Dev |
|-------------|---------|------------|
| `covacha-judicial` | Backend principal (API REST, logica de negocio) | 5009 |
| `mod_scrapper_mty` | Scraper existente para tribunales de Monterrey | N/A (cron) |
| `covacha-libs` | Modelos compartidos, repositorios DynamoDB, utils | N/A (lib) |
| `covacha-botia` | Notificaciones WhatsApp (integracion existente) | 5003 |
| `covacha-notification` | Email via SES (integracion existente) | 5005 |

### Contexto Juridico Mexicano

| Termino | Descripcion |
|---------|-------------|
| **Expediente** | Carpeta judicial que contiene todas las actuaciones de un caso |
| **Acuerdo** | Resolucion del juez sobre un tramite procesal |
| **Sentencia** | Resolucion definitiva que pone fin al juicio |
| **Audiencia** | Sesion programada ante el juez para desahogo de pruebas, alegatos, etc. |
| **Juzgado** | Organo jurisdiccional donde se tramita el expediente |
| **Partes** | Actor (demandante) y demandado en el juicio |
| **Actuario** | Funcionario que realiza notificaciones oficiales |
| **Secretario** | Funcionario que autoriza acuerdos y da fe de actuaciones |
| **Auto** | Resolucion interlocutoria del juez sobre cuestiones incidentales |
| **Emplazamiento** | Notificacion formal al demandado de que existe juicio en su contra |
| **Desahogo** | Ejecucion de una diligencia judicial (pruebas, audiencias) |
| **Proveido** | Resolucion de mero tramite que impulsa el procedimiento |

---

## Roles Involucrados

### R1: Abogado

Profesional del derecho que monitorea expedientes de sus clientes.

**Responsabilidades:**
- Suscribirse a expedientes para recibir alertas
- Consultar el detalle y timeline de movimientos de un expediente
- Configurar preferencias de notificacion (canales, frecuencia, tipos de evento)
- Buscar expedientes por numero, juzgado o partes
- Gestionar su cuenta y plan de suscripcion

### R2: Administrador de Despacho

Socio o director del despacho juridico que gestiona la cuenta empresarial.

**Responsabilidades:**
- Administrar usuarios del despacho (agregar/remover abogados)
- Ver dashboard consolidado de todos los expedientes del despacho
- Gestionar el plan de suscripcion y facturacion
- Configurar alertas globales para todo el despacho
- Asignar expedientes a abogados especificos

### R3: Administrador AlertaTribunal

Operador interno que gestiona la plataforma.

**Responsabilidades:**
- Monitorear el estado de los scrapers y su cobertura
- Gestionar tribunales soportados y sus drivers
- Ver metricas de uso de la plataforma
- Atender incidentes de scraping (bloqueos, cambios de estructura)
- Gestionar planes y facturacion global

### R4: Sistema

Procesos automatizados sin intervencion humana.

**Responsabilidades:**
- Ejecutar scraping programado de tribunales
- Detectar cambios en expedientes y generar alertas
- Despachar notificaciones por los canales configurados
- Reintentar operaciones fallidas con backoff exponencial
- Registrar snapshots y audit trail

---

## Arquitectura del Sistema

```
                            +---------------------+
                            |   alertatribunal.com |
                            |   (Landing publica)  |
                            +----------+----------+
                                       |
                            +----------v----------+
                            | app.alertatribunal   |
                            |   .com (Portal Web)  |
                            +----------+----------+
                                       |
                                       | HTTPS
                                       v
+------------------+       +-----------+-----------+
| mod_scrapper_mty |       |    API Gateway + WAF  |
| (Cron cada 30m)  |       +-----------+-----------+
+--------+---------+                   |
         |                             v
         |  HTTP interno    +----------+----------+
         +----------------->| covacha-judicial     |
                            | (Flask, EC2)         |
                            |                      |
                            | /api/v1/cases/...    |
                            | /api/v1/subs/...     |
                            | /api/v1/alerts/...   |
                            | /api/v1/courts/...   |
                            | /api/v1/plans/...    |
                            +--+------+------+----+
                               |      |      |
              +----------------+      |      +----------------+
              v                       v                       v
    +---------+--------+   +----------+---------+   +---------+---------+
    |    DynamoDB       |   |       SQS          |   |    S3              |
    | CASE#, ALERT#,    |   | alert-dispatch     |   | Snapshots HTML     |
    | COURT#, SUB#,     |   | notification-send  |   | Documentos PDF     |
    | NOTIF#, PLAN#,    |   | scrape-retry       |   |                    |
    | USER#             |   +----+----------+----+   +--------------------+
    +-------------------+        |          |
                                 v          v
                    +------------+--+  +----+---------------+
                    | covacha-botia  |  | covacha-notification|
                    | (WhatsApp)     |  | (Email via SES)     |
                    +----------------+  +---------------------+
```

### Flujo Principal

```
1. SCRAPING
   mod_scrapper_mty (cron cada 30 min)
     -> Descarga paginas de portales de tribunales
     -> Parsea HTML y extrae movimientos
     -> POST /api/v1/internal/scraper/results a covacha-judicial
     -> covacha-judicial almacena snapshot en S3

2. DETECCION DE CAMBIOS
   covacha-judicial (al recibir resultados del scraper)
     -> Compara snapshot actual vs anterior
     -> Si hay diferencias -> genera ALERT# en DynamoDB
     -> Busca suscripciones activas (SUB#) para ese expediente
     -> Publica evento en SQS (alert-dispatch)

3. DESPACHO DE NOTIFICACIONES
   covacha-judicial (consumer SQS alert-dispatch)
     -> Lee preferencias de notificacion del usuario
     -> Para cada canal habilitado:
        - Email: publica en SQS notification-send -> covacha-notification -> SES
        - WhatsApp: llama a covacha-botia API
        - In-app: almacena NOTIF# en DynamoDB (polling desde portal)
     -> Registra NOTIF# con estado (sent/failed/pending)

4. CONSULTA DEL USUARIO
   Portal web (app.alertatribunal.com)
     -> GET /api/v1/cases/{id}/timeline (movimientos)
     -> GET /api/v1/alerts (alertas recientes)
     -> GET /api/v1/subscriptions (suscripciones activas)
     -> PUT /api/v1/subscriptions/{id}/preferences (configurar canales)
```

---

## Modelo de Datos DynamoDB

### Single-Table Design

| Entidad | PK | SK | GSI1-PK | GSI1-SK |
|---------|----|----|---------|---------|
| Expediente | `CASE#{case_id}` | `META` | `COURT#{court_id}` | `CASE#{case_id}` |
| Movimiento | `CASE#{case_id}` | `MOV#{timestamp}#{mov_id}` | `COURT#{court_id}` | `MOV#{timestamp}` |
| Tribunal | `COURT#{court_id}` | `META` | `STATE#{state_code}` | `COURT#{court_id}` |
| Suscripcion | `SUB#{sub_id}` | `META` | `USER#{user_id}` | `SUB#{sub_id}` |
| Suscripcion-Case | `CASE#{case_id}` | `SUB#{sub_id}` | `USER#{user_id}` | `CASE#{case_id}` |
| Alerta | `ALERT#{alert_id}` | `META` | `USER#{user_id}` | `ALERT#{timestamp}` |
| Notificacion | `NOTIF#{notif_id}` | `META` | `USER#{user_id}` | `NOTIF#{timestamp}` |
| Plan | `PLAN#{plan_id}` | `META` | - | - |
| Suscripcion Plan | `USER#{user_id}` | `PLAN_SUB` | `PLAN#{plan_id}` | `USER#{user_id}` |
| Snapshot | `CASE#{case_id}` | `SNAP#{timestamp}` | - | - |

### GSIs Necesarios

| GSI | Proposito | PK | SK |
|-----|-----------|----|----|
| GSI1 | Buscar expedientes por tribunal, suscripciones por usuario, alertas por usuario | Variable | Variable |
| GSI2-UserEmail | Buscar usuario por email | `EMAIL#{email}` | `USER#{user_id}` |
| GSI3-CaseParts | Buscar expedientes por nombre de parte | `PART#{nombre_normalizado}` | `CASE#{case_id}` |

---

## Mapa de Epicas

| ID | Epica | Complejidad | Prioridad | Dependencias |
|----|-------|-------------|-----------|--------------|
| EP-AT-001 | Motor de Scraping de Tribunales | XL | Critica | Ninguna |
| EP-AT-002 | Gestion de Expedientes | L | Critica | EP-AT-001 |
| EP-AT-003 | Sistema de Suscripciones y Alertas | L | Critica | EP-AT-001, EP-AT-002 |
| EP-AT-004 | Notificaciones Multi-Canal | L | Alta | EP-AT-003 |
| EP-AT-005 | Portal Web AlertaTribunal | XL | Alta | EP-AT-002, EP-AT-003 |
| EP-AT-006 | Expansion a Otros Tribunales | L | Media | EP-AT-001 |
| EP-AT-007 | Analisis IA de Documentos Judiciales | L | Baja | EP-AT-001, EP-AT-002 |
| EP-AT-008 | Monetizacion y Planes | M | Alta | EP-AT-005 |

**Totales:**
- 8 epicas
- 46 user stories (US-AT-001 a US-AT-046)
- Estimacion total: ~120-160 dev-days

---

## Epicas Detalladas

---

### EP-AT-001: Motor de Scraping de Tribunales

**Descripcion:**
Scraper robusto y resiliente para portales de tribunales del Poder Judicial. Soporte inicial: Poder Judicial de Nuevo Leon (PJNL). El sistema debe ejecutar scraping programado (cron cada 30 minutos), detectar cambios respecto al snapshot anterior, parsear acuerdos/sentencias/audiencias del HTML, y almacenar snapshots para audit trail. Incluye mecanismos anti-ban (rotacion de user-agents, delays aleatorios, proxy rotation), retry logic con backoff exponencial, y monitoreo de salud del scraper.

Se construye como evolucion de `mod_scrapper_mty` (scraper existente) integrandolo con `covacha-judicial` via API interna.

**User Stories:** US-AT-001 a US-AT-007

**Criterios de Aceptacion de la Epica:**
- [ ] El scraper ejecuta automaticamente cada 30 minutos via cron
- [ ] Parsea correctamente acuerdos, sentencias, audiencias y proveidos del PJNL
- [ ] Detecta cambios comparando snapshot actual vs anterior
- [ ] Almacena snapshots HTML en S3 con timestamp
- [ ] Mecanismos anti-ban: user-agent rotation, delays 2-5s entre requests, respeto a robots.txt
- [ ] Retry con backoff exponencial (3 intentos, 30s/60s/120s)
- [ ] Logs estructurados para debugging y monitoreo
- [ ] Dashboard de salud del scraper (ultimo scrape exitoso, errores, cobertura)
- [ ] Cobertura de tests >= 98%

**Dependencias:** Ninguna (puede empezar de inmediato)

**Complejidad:** XL (integracion con portales externos, parseo HTML fragil, anti-ban, scheduling)

**Repositorio:** `mod_scrapper_mty`, `covacha-judicial`

---

### EP-AT-002: Gestion de Expedientes

**Descripcion:**
CRUD completo de expedientes judiciales monitoreados. Cada expediente contiene metadatos (numero, juzgado, tipo de juicio, partes, juez, secretario), un timeline cronologico de movimientos (acuerdos, sentencias, audiencias, notificaciones), documentos asociados, y estado actual. Los expedientes se alimentan automaticamente del scraper pero tambien pueden registrarse manualmente. La busqueda debe soportar numero de expediente, nombre del juzgado, y nombre de las partes.

**User Stories:** US-AT-008 a US-AT-013

**Criterios de Aceptacion de la Epica:**
- [ ] API CRUD completa para expedientes con paginacion cursor-based
- [ ] Busqueda por numero de expediente (exacta y parcial)
- [ ] Busqueda por juzgado (filtro)
- [ ] Busqueda por nombre de parte (GSI3-CaseParts, busqueda normalizada)
- [ ] Timeline cronologico de movimientos por expediente
- [ ] Metadatos completos: juez, secretario, tipo de juicio, materia, estado procesal
- [ ] Documentos asociados almacenados en S3 con referencia en DynamoDB
- [ ] Estado del expediente: ACTIVO, ARCHIVADO, SENTENCIADO, EN_APELACION
- [ ] Cobertura de tests >= 98%

**Dependencias:** EP-AT-001 (el scraper alimenta los expedientes)

**Complejidad:** L (modelado de dominio juridico, busquedas multiples)

**Repositorio:** `covacha-judicial`

---

### EP-AT-003: Sistema de Suscripciones y Alertas

**Descripcion:**
Motor de suscripciones que permite a usuarios subscribirse a expedientes especificos y configurar que tipos de eventos desean recibir (acuerdos, sentencias, audiencias, todos). Cada suscripcion tiene preferencias de canal (email, WhatsApp, in-app), frecuencia (instantanea, digest diario, digest semanal), y estado (activa, pausada, cancelada). Al detectarse un cambio en un expediente, el sistema genera alertas para todos los suscriptores activos de ese expediente.

**User Stories:** US-AT-014 a US-AT-019

**Criterios de Aceptacion de la Epica:**
- [ ] CRUD de suscripciones a expedientes
- [ ] Configuracion de tipos de evento a monitorear por suscripcion
- [ ] Configuracion de canales de notificacion (email, WhatsApp, in-app)
- [ ] Frecuencia configurable: instantanea, digest diario (8am), digest semanal (lunes 8am)
- [ ] Estados de suscripcion: ACTIVE, PAUSED, CANCELLED
- [ ] Validacion de limite de suscripciones segun plan del usuario
- [ ] Al detectar cambio en expediente, genera alertas para suscriptores activos
- [ ] Alertas con prioridad (ALTA: sentencia/audiencia, MEDIA: acuerdo, BAJA: proveido)
- [ ] Cobertura de tests >= 98%

**Dependencias:** EP-AT-001 (deteccion de cambios), EP-AT-002 (expedientes existen)

**Complejidad:** L (logica de matching suscripcion-evento, configuracion granular)

**Repositorio:** `covacha-judicial`

---

### EP-AT-004: Notificaciones Multi-Canal

**Descripcion:**
Dispatcher de notificaciones que toma alertas generadas y las envia por los canales configurados del usuario. Templates especificos por canal (email HTML rico, WhatsApp texto con emojis, in-app notificacion corta) y por tipo de evento judicial (acuerdo, sentencia, audiencia). Incluye integracion con SES para email, covacha-botia para WhatsApp, y almacenamiento en DynamoDB para in-app. Maneja retry con DLQ, historial completo de notificaciones enviadas, y metricas de entrega.

**User Stories:** US-AT-020 a US-AT-025

**Criterios de Aceptacion de la Epica:**
- [ ] Dispatcher consume cola SQS `alert-dispatch`
- [ ] Templates por canal: email (HTML), WhatsApp (texto plano), in-app (JSON)
- [ ] Templates por tipo de evento: acuerdo, sentencia, audiencia, proveido, emplazamiento
- [ ] Email via SES (a traves de covacha-notification)
- [ ] WhatsApp via covacha-botia API
- [ ] In-app: almacenamiento en DynamoDB con marca de leido/no leido
- [ ] Retry: 3 intentos con backoff exponencial, luego DLQ
- [ ] Historial de notificaciones por usuario con paginacion
- [ ] Metricas: tasa de entrega, tasa de apertura (email), tiempo de entrega
- [ ] Digest: acumula alertas y envia resumen diario/semanal segun preferencia
- [ ] Cobertura de tests >= 98%

**Dependencias:** EP-AT-003 (genera las alertas a despachar)

**Complejidad:** L (multi-canal, templates, retry, digest)

**Repositorio:** `covacha-judicial`, `covacha-botia`, `covacha-notification`

---

### EP-AT-005: Portal Web AlertaTribunal

**Descripcion:**
Aplicacion web completa para usuarios de AlertaTribunal. Incluye landing page publica (alertatribunal.com) con informacion del producto, precios y registro. Dashboard de usuario autenticado (app.alertatribunal.com) con expedientes suscritos, alertas recientes, timeline de movimientos, busqueda de expedientes, configuracion de cuenta y suscripciones. El portal consume la API de covacha-judicial y se despliega como aplicacion standalone (no como micro-frontend del ecosistema SuperPago, ya que es un tenant independiente).

**User Stories:** US-AT-026 a US-AT-031

**Criterios de Aceptacion de la Epica:**
- [ ] Landing page publica con descripcion del producto, precios, FAQ, y formulario de registro
- [ ] Dashboard de usuario: resumen de expedientes, alertas recientes, acciones rapidas
- [ ] Vista de expedientes suscritos con estado y ultimo movimiento
- [ ] Detalle de expediente con timeline completo
- [ ] Busqueda de expedientes (para suscribirse a nuevos)
- [ ] Configuracion de cuenta: perfil, preferencias de notificacion, plan activo
- [ ] Responsive design (mobile-first, abogados consultan desde el juzgado)
- [ ] SEO optimizado para landing publica
- [ ] Autenticacion via Cognito (tenant AlertaTribunal)

**Dependencias:** EP-AT-002 (API de expedientes), EP-AT-003 (API de suscripciones)

**Complejidad:** XL (landing publica + dashboard privado + multiples vistas)

**Repositorio:** Nuevo repositorio frontend (a definir) o subdominio de `mf-core`

---

### EP-AT-006: Expansion a Otros Tribunales

**Descripcion:**
Arquitectura extensible basada en Strategy Pattern para soportar multiples tribunales de Mexico. Cada tribunal tiene un "driver" que encapsula la logica de scraping, parseo y normalizacion especifica de su portal web. Los drivers comparten una interfaz comun (`TribunalDriver`) pero implementan logica diferente segun la estructura del portal. Drivers prioritarios: CDMX (TSJCDMX), Jalisco (STJ), Estado de Mexico (TSJEM). Incluye normalizacion de datos entre tribunales y dashboard de cobertura.

**User Stories:** US-AT-032 a US-AT-037

**Criterios de Aceptacion de la Epica:**
- [ ] Interface `TribunalDriver` definida con metodos estandar (scrape, parse, normalize)
- [ ] Driver PJNL (Nuevo Leon) refactorizado para implementar la interface
- [ ] Al menos 1 driver adicional funcional (CDMX o Jalisco)
- [ ] Normalizacion de datos: movimientos de diferentes tribunales comparten el mismo modelo
- [ ] Dashboard de cobertura: tribunales soportados, estado de cada driver, ultimo scrape exitoso
- [ ] Sistema de registro de drivers (agregar nuevo tribunal = implementar driver + registrar)
- [ ] Auto-deteccion basica de cambios en estructura del portal (alerta a admin si parseo falla)
- [ ] Cobertura de tests >= 98% por driver

**Dependencias:** EP-AT-001 (motor de scraping base)

**Complejidad:** L (Strategy Pattern, parseo de portales heterogeneos)

**Repositorio:** `covacha-judicial`, `mod_scrapper_mty`

---

### EP-AT-007: Analisis IA de Documentos Judiciales

**Descripcion:**
Capa de inteligencia artificial que analiza los textos de acuerdos y sentencias para extraer informacion estructurada. Usa NLP para identificar entidades (fechas clave, montos, plazos, nombres de partes), clasificar automaticamente el tipo de movimiento, generar resumenes ejecutivos de sentencias largas, y predecir el siguiente paso procesal probable. Las alertas inteligentes notifican al abogado no solo que hubo un movimiento, sino que significa ese movimiento para su caso.

**User Stories:** US-AT-038 a US-AT-042

**Criterios de Aceptacion de la Epica:**
- [ ] Extraccion de entidades: fechas, montos, plazos, nombres de partes
- [ ] Clasificacion automatica de tipo de movimiento (acuerdo, sentencia, auto, proveido, audiencia)
- [ ] Resumen automatico de sentencias (max 200 palabras)
- [ ] Deteccion de plazos criticos (ej: "10 dias para apelar" -> fecha limite calculada)
- [ ] Prediccion basica de siguiente paso procesal (basada en tipo de juicio y etapa)
- [ ] Alertas enriquecidas con analisis IA (no solo "hubo acuerdo" sino "acuerdo que otorga plazo de 5 dias para presentar pruebas, vence el 25/02/2026")
- [ ] Modelo entrenenable/ajustable con feedback del usuario (correcto/incorrecto)
- [ ] Cobertura de tests >= 98%

**Dependencias:** EP-AT-001 (textos del scraper), EP-AT-002 (contexto del expediente)

**Complejidad:** L (NLP, extraccion de entidades, dominio juridico especializado)

**Repositorio:** `covacha-judicial`

---

### EP-AT-008: Monetizacion y Planes

**Descripcion:**
Sistema de planes de suscripcion para monetizar el servicio. Tres tiers: Gratis (3 expedientes, solo in-app), Pro (50 expedientes, todos los canales, $299 MXN/mes), Enterprise (ilimitado + API + soporte prioritario, $999 MXN/mes). Incluye periodo de prueba de 14 dias para Pro, facturacion mensual automatica, integracion con pasarela de pago (Openpay o Stripe), y metricas de conversion (free -> pro -> enterprise).

**User Stories:** US-AT-043 a US-AT-046

**Criterios de Aceptacion de la Epica:**
- [ ] 3 planes definidos: Gratis, Pro ($299/mes), Enterprise ($999/mes)
- [ ] Limites por plan: expedientes, canales de notificacion, acceso a IA, API
- [ ] Trial de 14 dias para plan Pro (sin tarjeta)
- [ ] Facturacion mensual automatica con pasarela de pago
- [ ] Upgrade/downgrade de plan con prorrateo
- [ ] Facturacion con CFDI (requisito fiscal mexicano)
- [ ] Dashboard de metricas: usuarios por plan, conversion, churn, MRR
- [ ] Cobertura de tests >= 98%

**Dependencias:** EP-AT-005 (portal web para seleccion de plan)

**Complejidad:** M (integracion de pagos, logica de planes, facturacion)

**Repositorio:** `covacha-judicial`

---

## User Stories Detalladas

---

### EP-AT-001: Motor de Scraping de Tribunales

---

#### US-AT-001: Scheduling de scraping con cron

**Como** Sistema
**Quiero** ejecutar scraping automatico del portal del PJNL cada 30 minutos
**Para** detectar movimientos nuevos en expedientes lo antes posible

**Criterios de Aceptacion:**
- [ ] Cron job configurado para ejecutar cada 30 minutos (configurable via variable de entorno)
- [ ] El scraper se ejecuta como proceso independiente que llama a `POST /api/v1/internal/scraper/trigger`
- [ ] Si un scrape esta en progreso, el nuevo se encola (no ejecucion concurrente)
- [ ] Log de cada ejecucion: hora inicio, hora fin, expedientes procesados, errores
- [ ] Alerta al administrador si el scraper no ejecuta en 2 horas consecutivas

**Tareas Tecnicas:**
- [ ] Configurar cron en EC2 o CloudWatch Events para trigger periodico
- [ ] Crear endpoint `POST /api/v1/internal/scraper/trigger` en covacha-judicial
- [ ] Implementar lock distribuido (DynamoDB) para evitar ejecucion concurrente
- [ ] Tests: 5+ unit tests (scheduling, lock, error handling)

**API:** `POST /api/v1/internal/scraper/trigger`
**DynamoDB:** `COURT#pjnl | SCRAPE_LOCK` (lock distribuido con TTL)

---

#### US-AT-002: Parseo de acuerdos y sentencias del PJNL

**Como** Sistema
**Quiero** parsear correctamente el HTML del portal del Poder Judicial de Nuevo Leon
**Para** extraer movimientos estructurados (acuerdos, sentencias, audiencias) de cada expediente

**Criterios de Aceptacion:**
- [ ] Parsea pagina de consulta de expediente del PJNL
- [ ] Extrae: numero de expediente, juzgado, tipo de juicio, partes (actor, demandado)
- [ ] Extrae lista de movimientos: fecha, tipo (acuerdo/sentencia/audiencia/proveido), texto completo
- [ ] Maneja correctamente acentos, caracteres especiales y encoding del portal
- [ ] Si el HTML no tiene la estructura esperada, registra error y no falla silenciosamente
- [ ] Normaliza fechas al formato ISO 8601

**Tareas Tecnicas:**
- [ ] Refactorizar parser existente en `mod_scrapper_mty` para usar BeautifulSoup/lxml
- [ ] Crear modelos Pydantic para validar datos parseados
- [ ] Crear suite de tests con fixtures HTML del portal PJNL (snapshots reales anonimizados)
- [ ] Tests: 8+ unit tests (happy path, HTML malformado, encoding, edge cases)

---

#### US-AT-003: Deteccion de cambios en expedientes

**Como** Sistema
**Quiero** comparar el resultado del scraping actual contra el snapshot anterior de cada expediente
**Para** identificar movimientos nuevos y generar alertas solo cuando hay cambios reales

**Criterios de Aceptacion:**
- [ ] Compara lista de movimientos actuales vs almacenados en DynamoDB
- [ ] Identifica movimientos nuevos (que no existian en el snapshot anterior)
- [ ] Identifica movimientos modificados (misma fecha/tipo pero texto diferente)
- [ ] No genera alerta si no hay cambios (scrape sin novedades)
- [ ] Registra resultado de deteccion en log: X nuevos, Y modificados, Z sin cambios
- [ ] Genera evento `CASE_UPDATED` con lista de movimientos nuevos

**Tareas Tecnicas:**
- [ ] Implementar comparador de snapshots con hashing de movimientos
- [ ] Crear servicio `ChangeDetectionService` en covacha-judicial
- [ ] Publicar evento en SQS `alert-dispatch` cuando hay cambios
- [ ] Tests: 6+ unit tests (sin cambios, nuevos movimientos, modificados, expediente nuevo)

**DynamoDB:** `CASE#{case_id} | MOV#{timestamp}#{mov_id}`

---

#### US-AT-004: Almacenamiento de snapshots en S3

**Como** Administrador AlertaTribunal
**Quiero** que cada resultado de scraping se almacene como snapshot en S3
**Para** tener un historial completo y poder debuggear problemas de parseo

**Criterios de Aceptacion:**
- [ ] Cada ejecucion del scraper almacena el HTML crudo en S3
- [ ] Path en S3: `snapshots/{court_id}/{case_id}/{timestamp}.html`
- [ ] Metadata del objeto S3: content-type, scrape_id, status (success/error)
- [ ] Retencion de 90 dias (lifecycle policy)
- [ ] El snapshot es accesible via API interna para debugging

**Tareas Tecnicas:**
- [ ] Crear servicio `SnapshotStorageService` con boto3
- [ ] Configurar bucket S3 con lifecycle policy de 90 dias
- [ ] Crear endpoint `GET /api/v1/internal/snapshots/{case_id}` para consulta interna
- [ ] Tests: 4+ unit tests (upload, retrieval, lifecycle, error handling)

---

#### US-AT-005: Mecanismos anti-ban para scraping

**Como** Sistema
**Quiero** implementar tecnicas anti-ban al hacer scraping de portales de tribunales
**Para** evitar que el portal bloquee nuestra IP y el servicio deje de funcionar

**Criterios de Aceptacion:**
- [ ] Rotacion de user-agents (pool de 20+ user-agents reales de navegadores)
- [ ] Delays aleatorios entre requests (2-5 segundos, configurable)
- [ ] Respeto a robots.txt del portal
- [ ] Deteccion de CAPTCHA o bloqueo (HTTP 403, 429, pagina de verificacion)
- [ ] Si se detecta bloqueo: pausa automatica de 15 minutos y alerta al admin
- [ ] Rate limiting configurable por tribunal (max requests/minuto)
- [ ] Headers HTTP que simulan navegador real (Accept, Accept-Language, Referer)

**Tareas Tecnicas:**
- [ ] Crear `AntibanMiddleware` con pool de user-agents y delay configurable
- [ ] Implementar detector de bloqueo (analisis de response code y body)
- [ ] Crear mecanismo de circuit breaker por tribunal
- [ ] Tests: 5+ unit tests (rotation, delay, detection, circuit breaker)

---

#### US-AT-006: Retry logic con backoff exponencial

**Como** Sistema
**Quiero** reintentar automaticamente scrapes fallidos con backoff exponencial
**Para** recuperarme de errores transitorios (timeout, red, portal temporalmente caido)

**Criterios de Aceptacion:**
- [ ] 3 intentos por scrape fallido: 30s, 60s, 120s de espera entre intentos
- [ ] Errores transitorios que activan retry: timeout, connection error, HTTP 500/502/503
- [ ] Errores permanentes que NO activan retry: HTTP 404, parseo invalido, CAPTCHA
- [ ] Si los 3 intentos fallan, envia a DLQ (SQS dead letter queue) y alerta al admin
- [ ] Cada intento se registra en log con motivo de falla y numero de intento
- [ ] Metricas: tasa de exito al primer intento, tasa de recuperacion con retry

**Tareas Tecnicas:**
- [ ] Implementar decorador `@with_retry` con backoff exponencial configurable
- [ ] Configurar SQS DLQ `scrape-retry-dlq`
- [ ] Crear alerta CloudWatch para mensajes en DLQ
- [ ] Tests: 5+ unit tests (retry exitoso, max retries, errores permanentes, DLQ)

---

#### US-AT-007: Dashboard de salud del scraper

**Como** Administrador AlertaTribunal
**Quiero** ver un dashboard con el estado de salud de cada scraper/tribunal
**Para** detectar rapidamente si algun scraper falla y actuar antes de que los usuarios se quejen

**Criterios de Aceptacion:**
- [ ] Vista de estado por tribunal: ultimo scrape exitoso, ultimo error, expedientes monitoreados
- [ ] Indicadores: verde (< 1h desde ultimo scrape), amarillo (1-2h), rojo (> 2h)
- [ ] Metricas: expedientes procesados/hora, movimientos detectados/dia, tasa de error
- [ ] Historial de errores con detalle (ultimos 50 errores)
- [ ] Boton de scrape manual para forzar ejecucion inmediata

**Tareas Tecnicas:**
- [ ] Crear endpoint `GET /api/v1/admin/scraper/health`
- [ ] Crear endpoint `POST /api/v1/admin/scraper/{court_id}/force`
- [ ] Almacenar metricas de scraping en DynamoDB (`COURT#{court_id} | HEALTH`)
- [ ] Tests: 4+ unit tests

**API:** `GET /api/v1/admin/scraper/health`, `POST /api/v1/admin/scraper/{court_id}/force`

---

### EP-AT-002: Gestion de Expedientes

---

#### US-AT-008: CRUD de expedientes monitoreados

**Como** Abogado
**Quiero** consultar y registrar expedientes en AlertaTribunal
**Para** tener un catalogo centralizado de los casos que me interesan

**Criterios de Aceptacion:**
- [ ] `POST /api/v1/cases` - Registrar expediente manualmente (numero, juzgado, partes)
- [ ] `GET /api/v1/cases/{id}` - Detalle completo del expediente con metadatos
- [ ] `GET /api/v1/cases` - Lista paginada de expedientes (cursor-based)
- [ ] `PUT /api/v1/cases/{id}` - Actualizar metadatos del expediente (notas, etiquetas)
- [ ] `DELETE /api/v1/cases/{id}` - Soft delete (marcar como archivado, no eliminar)
- [ ] Validacion de duplicados: no se puede registrar el mismo numero de expediente + juzgado dos veces
- [ ] Expedientes creados por scraper se vinculan automaticamente al registrar manualmente

**Tareas Tecnicas:**
- [ ] Crear Blueprint Flask `cases_bp` con endpoints CRUD
- [ ] Crear servicio `CaseService` con logica de negocio
- [ ] Crear modelo `Case` y `CaseMovement` con Pydantic
- [ ] Crear repositorio DynamoDB para expedientes
- [ ] Tests: 6+ unit tests (create, read, list, update, delete, duplicados)

**API:** `POST/GET/PUT/DELETE /api/v1/cases/...`
**DynamoDB:** `CASE#{case_id} | META`

---

#### US-AT-009: Busqueda de expedientes por multiples criterios

**Como** Abogado
**Quiero** buscar expedientes por numero, juzgado o nombre de las partes
**Para** encontrar rapidamente el expediente que necesito sin navegar listas largas

**Criterios de Aceptacion:**
- [ ] Busqueda por numero de expediente (exacta y parcial con prefijo)
- [ ] Filtro por juzgado (seleccion de juzgado de una lista)
- [ ] Busqueda por nombre de parte (actor o demandado, busqueda normalizada sin acentos)
- [ ] Filtro por tipo de juicio (civil, familiar, mercantil, penal, laboral)
- [ ] Filtro por estado procesal (ACTIVO, ARCHIVADO, SENTENCIADO, EN_APELACION)
- [ ] Combinacion de filtros (ej: juzgado X + tipo civil + activos)
- [ ] Resultados ordenados por fecha de ultimo movimiento (mas reciente primero)

**Tareas Tecnicas:**
- [ ] Implementar busqueda con GSI1 (por tribunal) y GSI3 (por parte)
- [ ] Crear servicio `CaseSearchService` con normalizacion de texto
- [ ] Normalizar nombres: quitar acentos, mayusculas, espacios extra
- [ ] Tests: 6+ unit tests (busqueda exacta, parcial, filtros, combinaciones)

**API:** `GET /api/v1/cases?q={query}&court={court_id}&type={type}&status={status}`

---

#### US-AT-010: Timeline cronologico de movimientos

**Como** Abogado
**Quiero** ver el timeline completo de movimientos de un expediente en orden cronologico
**Para** entender la historia procesal del caso y que ha sucedido recientemente

**Criterios de Aceptacion:**
- [ ] Lista cronologica de todos los movimientos (mas reciente primero por defecto)
- [ ] Cada movimiento muestra: fecha, tipo (icono diferenciado), texto completo, fuente (scraper/manual)
- [ ] Filtro por tipo de movimiento (acuerdo, sentencia, audiencia, proveido)
- [ ] Filtro por rango de fechas
- [ ] Paginacion cursor-based (primeros 20 movimientos, cargar mas on-demand)
- [ ] Indicador visual para movimientos recientes (ultimas 24 horas) - badge "Nuevo"
- [ ] Opcion de expandir/colapsar texto completo del movimiento

**Tareas Tecnicas:**
- [ ] Crear endpoint `GET /api/v1/cases/{id}/timeline`
- [ ] Query DynamoDB con SK prefix `MOV#` ordenado por timestamp desc
- [ ] Implementar cursor-based pagination con last_evaluated_key
- [ ] Tests: 5+ unit tests (paginacion, filtros, ordenamiento, caso vacio)

**API:** `GET /api/v1/cases/{id}/timeline?type={type}&from={date}&to={date}&cursor={cursor}`
**DynamoDB:** `CASE#{case_id} | MOV#{timestamp}#{mov_id}`

---

#### US-AT-011: Detalle de expediente con metadatos completos

**Como** Abogado
**Quiero** ver toda la informacion del expediente en una sola vista
**Para** tener el contexto completo del caso sin tener que consultar el portal del tribunal

**Criterios de Aceptacion:**
- [ ] Informacion basica: numero de expediente, juzgado, materia, tipo de juicio
- [ ] Partes del juicio: actor(es), demandado(s), terceros interesados
- [ ] Funcionarios: juez titular, secretario de acuerdos, actuario asignado
- [ ] Estado procesal actual con fecha de ultimo cambio
- [ ] Estadisticas: total de movimientos, fecha primer movimiento, fecha ultimo movimiento
- [ ] Notas personales del abogado (editables, privadas por usuario)
- [ ] Etiquetas/tags personalizadas para organizar expedientes

**Tareas Tecnicas:**
- [ ] Crear modelo completo `CaseDetail` con todos los campos
- [ ] Enriquecer endpoint `GET /api/v1/cases/{id}` con datos agregados
- [ ] Crear endpoints para notas: `POST/PUT/DELETE /api/v1/cases/{id}/notes`
- [ ] Crear endpoints para etiquetas: `POST/DELETE /api/v1/cases/{id}/tags`
- [ ] Tests: 5+ unit tests

**API:** `GET /api/v1/cases/{id}`, `POST/PUT/DELETE /api/v1/cases/{id}/notes`, `POST/DELETE /api/v1/cases/{id}/tags`

---

#### US-AT-012: Documentos asociados a expedientes

**Como** Abogado
**Quiero** adjuntar y consultar documentos relacionados con un expediente
**Para** tener centralizados los escritos, demandas, contestaciones y resoluciones del caso

**Criterios de Aceptacion:**
- [ ] Upload de documentos PDF, DOCX, JPG, PNG (max 10MB por archivo)
- [ ] Categorias de documentos: demanda, contestacion, prueba, sentencia, recurso, otro
- [ ] Listado de documentos por expediente con metadata (nombre, tipo, fecha, tamano, quien subio)
- [ ] Download de documentos
- [ ] Documentos del scraper (sentencias descargables del portal) se asocian automaticamente
- [ ] Maximo 50 documentos por expediente en plan Pro, ilimitado en Enterprise

**Tareas Tecnicas:**
- [ ] Crear endpoint `POST /api/v1/cases/{id}/documents` con multipart upload
- [ ] Crear endpoint `GET /api/v1/cases/{id}/documents` para listar
- [ ] Almacenar archivos en S3 (`documents/{case_id}/{doc_id}.ext`)
- [ ] Registrar metadata en DynamoDB (`CASE#{case_id} | DOC#{doc_id}`)
- [ ] Tests: 5+ unit tests (upload, list, download, validaciones de tamano/tipo)

**API:** `POST/GET /api/v1/cases/{id}/documents`, `GET /api/v1/cases/{id}/documents/{doc_id}/download`

---

#### US-AT-013: Estado procesal del expediente

**Como** Abogado
**Quiero** ver el estado procesal actual de cada expediente y su progreso
**Para** saber en que etapa se encuentra el juicio y que esperar a continuacion

**Criterios de Aceptacion:**
- [ ] Estados procesales posibles: ADMISION, EMPLAZAMIENTO, CONTESTACION, PRUEBAS, ALEGATOS, SENTENCIA, RECURSO, EJECUCION, ARCHIVADO
- [ ] El estado se actualiza automaticamente cuando el scraper detecta movimientos que indican cambio de etapa
- [ ] Indicador visual de progreso (etapa actual en un pipeline horizontal)
- [ ] Fecha estimada de siguiente paso (basada en plazos legales)
- [ ] Historial de cambios de estado con fechas
- [ ] El abogado puede ajustar el estado manualmente si el automatico es incorrecto

**Tareas Tecnicas:**
- [ ] Definir maquina de estados procesales con transiciones validas
- [ ] Crear servicio `ProcessStatusService` que infiere estado desde movimientos
- [ ] Crear endpoint `PUT /api/v1/cases/{id}/status` para override manual
- [ ] Tests: 5+ unit tests (transiciones validas, inferencia, override)

**API:** `GET /api/v1/cases/{id}/status`, `PUT /api/v1/cases/{id}/status`

---

### EP-AT-003: Sistema de Suscripciones y Alertas

---

#### US-AT-014: Suscripcion a expedientes

**Como** Abogado
**Quiero** suscribirme a un expediente para recibir alertas de movimientos
**Para** no tener que revisar manualmente el portal del tribunal todos los dias

**Criterios de Aceptacion:**
- [ ] `POST /api/v1/subscriptions` - Crear suscripcion a un expediente
- [ ] Validacion de limite segun plan: Gratis (3), Pro (50), Enterprise (ilimitado)
- [ ] Validacion de que el expediente existe en el sistema
- [ ] Estado inicial: ACTIVE
- [ ] Respuesta incluye la suscripcion creada con ID unico
- [ ] Un usuario no puede tener 2 suscripciones activas al mismo expediente

**Tareas Tecnicas:**
- [ ] Crear Blueprint Flask `subscriptions_bp`
- [ ] Crear servicio `SubscriptionService` con validacion de limites
- [ ] Crear repositorio DynamoDB para suscripciones
- [ ] Tests: 5+ unit tests (create, limite, duplicado, expediente inexistente)

**API:** `POST /api/v1/subscriptions`
**DynamoDB:** `SUB#{sub_id} | META`, `CASE#{case_id} | SUB#{sub_id}`

---

#### US-AT-015: Configuracion de alertas por suscripcion

**Como** Abogado
**Quiero** configurar que tipos de eventos quiero monitorear para cada expediente suscrito
**Para** recibir solo las alertas que me interesan y no saturarme de notificaciones

**Criterios de Aceptacion:**
- [ ] Tipos de evento configurables: ACUERDO, SENTENCIA, AUDIENCIA, PROVEIDO, EMPLAZAMIENTO, TODOS
- [ ] Por defecto: TODOS los tipos de evento estan habilitados
- [ ] Se puede cambiar la configuracion en cualquier momento via `PUT /api/v1/subscriptions/{id}/preferences`
- [ ] Prioridad automatica: SENTENCIA y AUDIENCIA siempre alta, ACUERDO media, PROVEIDO baja
- [ ] El usuario puede override la prioridad por tipo de evento

**Tareas Tecnicas:**
- [ ] Crear modelo `SubscriptionPreferences` con tipos de evento y prioridades
- [ ] Crear endpoint `PUT /api/v1/subscriptions/{id}/preferences`
- [ ] Validar que los tipos de evento son validos
- [ ] Tests: 4+ unit tests (configurar, override prioridad, tipos invalidos)

**API:** `GET/PUT /api/v1/subscriptions/{id}/preferences`

---

#### US-AT-016: Configuracion de canales de notificacion

**Como** Abogado
**Quiero** elegir por que canales recibir alertas (email, WhatsApp, in-app)
**Para** recibir notificaciones donde me sea mas comodo

**Criterios de Aceptacion:**
- [ ] Canales disponibles: EMAIL, WHATSAPP, IN_APP
- [ ] Plan Gratis: solo IN_APP
- [ ] Plan Pro: EMAIL + IN_APP + WHATSAPP
- [ ] Plan Enterprise: todos los canales
- [ ] El usuario puede habilitar/deshabilitar canales individualmente
- [ ] Para WhatsApp: validar que el numero esta registrado en covacha-botia
- [ ] Para Email: usar el email de la cuenta (verificado via Cognito)

**Tareas Tecnicas:**
- [ ] Agregar `channels: list[str]` al modelo de preferencias de suscripcion
- [ ] Validar canales disponibles segun plan del usuario
- [ ] Validar numero de WhatsApp contra covacha-botia
- [ ] Tests: 5+ unit tests (canales por plan, validacion WhatsApp, toggle)

**API:** `PUT /api/v1/subscriptions/{id}/channels`

---

#### US-AT-017: Frecuencia de alertas configurable

**Como** Abogado
**Quiero** elegir entre recibir alertas instantaneas o un digest diario/semanal
**Para** controlar la frecuencia de interrupciones segun mi preferencia

**Criterios de Aceptacion:**
- [ ] Frecuencias disponibles: INSTANT (en tiempo real), DAILY_DIGEST (8:00 AM), WEEKLY_DIGEST (lunes 8:00 AM)
- [ ] Frecuencia configurable por suscripcion (no global)
- [ ] INSTANT: la alerta se despacha al momento de detectar el cambio
- [ ] DAILY_DIGEST: acumula alertas del dia y envia resumen a las 8:00 AM
- [ ] WEEKLY_DIGEST: acumula alertas de la semana y envia resumen el lunes a las 8:00 AM
- [ ] Si hay alerta de prioridad ALTA, se envia siempre de forma instantanea (override de frecuencia)

**Tareas Tecnicas:**
- [ ] Agregar `frequency: str` al modelo de preferencias
- [ ] Crear cron job para digest diario (8:00 AM) y semanal (lunes 8:00 AM)
- [ ] Crear servicio `DigestService` que acumula y genera resumen
- [ ] Implementar override de frecuencia para alertas de alta prioridad
- [ ] Tests: 5+ unit tests (instant, daily, weekly, override alta prioridad)

---

#### US-AT-018: Gestion de suscripciones (pausar, cancelar, listar)

**Como** Abogado
**Quiero** ver, pausar y cancelar mis suscripciones a expedientes
**Para** gestionar activamente que expedientes estoy monitoreando

**Criterios de Aceptacion:**
- [ ] `GET /api/v1/subscriptions` - Lista paginada de suscripciones del usuario
- [ ] `PUT /api/v1/subscriptions/{id}/pause` - Pausar suscripcion (deja de generar alertas)
- [ ] `PUT /api/v1/subscriptions/{id}/resume` - Reanudar suscripcion pausada
- [ ] `DELETE /api/v1/subscriptions/{id}` - Cancelar suscripcion (soft delete)
- [ ] Filtro por estado: ACTIVE, PAUSED, CANCELLED
- [ ] Cada suscripcion muestra: expediente, estado, canales, frecuencia, fecha de creacion

**Tareas Tecnicas:**
- [ ] Completar endpoints CRUD en `subscriptions_bp`
- [ ] Implementar transiciones de estado: ACTIVE <-> PAUSED, ACTIVE -> CANCELLED
- [ ] No permitir transicion CANCELLED -> ACTIVE (debe crear nueva suscripcion)
- [ ] Tests: 6+ unit tests (list, pause, resume, cancel, transiciones invalidas)

**API:** `GET /api/v1/subscriptions`, `PUT /api/v1/subscriptions/{id}/pause`, `PUT /api/v1/subscriptions/{id}/resume`, `DELETE /api/v1/subscriptions/{id}`

---

#### US-AT-019: Generacion de alertas al detectar cambios

**Como** Sistema
**Quiero** generar alertas automaticamente cuando se detecta un cambio en un expediente suscrito
**Para** que cada suscriptor activo reciba notificacion de los movimientos relevantes

**Criterios de Aceptacion:**
- [ ] Al detectar cambio en expediente (desde EP-AT-001), busca suscripciones activas
- [ ] Filtra suscripciones por tipo de evento configurado (solo envia si el tipo aplica)
- [ ] Genera `ALERT#` en DynamoDB por cada suscripcion que aplica
- [ ] La alerta contiene: expediente, movimiento nuevo, tipo, prioridad, suscripcion_id, usuario_id
- [ ] Publica evento en SQS `alert-dispatch` para que el notificador procese
- [ ] Si no hay suscriptores para un expediente, no genera alertas (pero si registra el movimiento)

**Tareas Tecnicas:**
- [ ] Crear servicio `AlertGenerationService`
- [ ] Query suscripciones activas por case_id usando GSI (SK prefix `SUB#` en PK `CASE#`)
- [ ] Filtrar por tipo de evento configurado en preferencias
- [ ] Batch write de alertas en DynamoDB
- [ ] Publicar en SQS con deduplication_id para idempotencia
- [ ] Tests: 6+ unit tests (con suscriptores, sin suscriptores, filtro por tipo, prioridad)

**DynamoDB:** `ALERT#{alert_id} | META`, GSI1: `USER#{user_id} | ALERT#{timestamp}`

---

### EP-AT-004: Notificaciones Multi-Canal

---

#### US-AT-020: Dispatcher de notificaciones

**Como** Sistema
**Quiero** un dispatcher que consuma alertas de SQS y las envie por los canales configurados del usuario
**Para** que las alertas lleguen al usuario por sus canales preferidos

**Criterios de Aceptacion:**
- [ ] Consumer SQS lee mensajes de cola `alert-dispatch`
- [ ] Para cada alerta, consulta preferencias del suscriptor (canales habilitados)
- [ ] Despacha a cada canal habilitado (email, WhatsApp, in-app) en paralelo
- [ ] Registra resultado por canal: SENT, FAILED, PENDING
- [ ] Si un canal falla, los otros continuan (falla parcial aceptable)
- [ ] Idempotencia: si el mismo mensaje se procesa dos veces, no duplica notificaciones

**Tareas Tecnicas:**
- [ ] Crear consumer SQS `NotificationDispatcher` con polling continuo
- [ ] Implementar despacho paralelo con ThreadPoolExecutor o asyncio
- [ ] Crear modelo `Notification` con estado por canal
- [ ] Implementar idempotencia con deduplication basada en alert_id + channel
- [ ] Tests: 6+ unit tests (despacho exitoso, falla parcial, idempotencia, canales multiples)

**DynamoDB:** `NOTIF#{notif_id} | META`

---

#### US-AT-021: Templates de notificacion por canal y tipo de evento

**Como** Sistema
**Quiero** templates especificos por canal (email, WhatsApp, in-app) y por tipo de evento judicial
**Para** que cada notificacion tenga el formato adecuado para su canal y sea informativa

**Criterios de Aceptacion:**
- [ ] Templates de email (HTML): header con logo AlertaTribunal, cuerpo con datos del movimiento, CTA al portal
- [ ] Templates de WhatsApp (texto plano): conciso, con datos clave del movimiento, link al portal
- [ ] Templates de in-app (JSON): titulo corto, cuerpo resumido, metadata para render en UI
- [ ] Templates por tipo de evento:
  - ACUERDO: "Nuevo acuerdo en expediente {numero} - {juzgado}: {resumen}"
  - SENTENCIA: "SENTENCIA en expediente {numero}: {resumen}" (marcado como urgente)
  - AUDIENCIA: "Audiencia programada para {fecha} en expediente {numero}"
  - PROVEIDO: "Proveido en expediente {numero}: {resumen}"
  - EMPLAZAMIENTO: "Emplazamiento en expediente {numero}"
- [ ] Variables de template: {numero_expediente}, {juzgado}, {tipo_movimiento}, {fecha}, {resumen}, {url_portal}
- [ ] Templates almacenados como archivos Jinja2, no hardcoded

**Tareas Tecnicas:**
- [ ] Crear directorio `templates/notifications/` con archivos Jinja2
- [ ] Crear servicio `TemplateRenderer` que resuelve template por (canal, tipo_evento)
- [ ] Crear templates email (3+ variantes), WhatsApp (3+ variantes), in-app (3+ variantes)
- [ ] Tests: 5+ unit tests (render por canal, variables, tipo evento desconocido)

---

#### US-AT-022: Notificacion por email via SES

**Como** Abogado
**Quiero** recibir alertas por email cuando hay movimientos en mis expedientes
**Para** estar informado aun cuando no estoy en la plataforma

**Criterios de Aceptacion:**
- [ ] Email enviado desde `alertas@alertatribunal.com` (SES verified domain)
- [ ] Asunto descriptivo: "AlertaTribunal: {tipo} en {expediente} - {juzgado}"
- [ ] Cuerpo HTML con formato profesional y datos del movimiento
- [ ] CTA "Ver expediente" que lleva al detalle en app.alertatribunal.com
- [ ] Footer con link para configurar preferencias y desuscribirse
- [ ] Tracking de apertura (pixel de tracking) si el usuario lo permite

**Tareas Tecnicas:**
- [ ] Integrar con covacha-notification para envio via SES
- [ ] Configurar dominio alertatribunal.com en SES (DKIM, SPF, DMARC)
- [ ] Crear template HTML responsive para email
- [ ] Tests: 4+ unit tests (envio exitoso, template render, error handling)

---

#### US-AT-023: Notificacion por WhatsApp via covacha-botia

**Como** Abogado
**Quiero** recibir alertas por WhatsApp cuando hay movimientos en mis expedientes
**Para** enterarme al instante desde mi celular sin revisar email

**Criterios de Aceptacion:**
- [ ] Mensaje enviado via API de covacha-botia (WhatsApp Business API)
- [ ] Formato de mensaje: texto plano conciso con datos clave
- [ ] Template pre-aprobado por WhatsApp Business (requisito de Meta)
- [ ] Incluye link al detalle del expediente en el portal
- [ ] Para activar WhatsApp, el usuario debe verificar su numero (opt-in explicito)
- [ ] Si el envio falla (numero invalido, opt-out), se registra el error y se notifica al usuario por email

**Tareas Tecnicas:**
- [ ] Crear template de WhatsApp Business para AlertaTribunal y obtener aprobacion de Meta
- [ ] Integrar con endpoint de envio de covacha-botia
- [ ] Implementar verificacion de opt-in para numero de WhatsApp
- [ ] Tests: 4+ unit tests (envio exitoso, numero invalido, opt-out, fallback a email)

---

#### US-AT-024: Notificaciones in-app con marca de lectura

**Como** Abogado
**Quiero** ver mis alertas dentro del portal de AlertaTribunal con indicador de nuevas
**Para** revisar los movimientos pendientes cada vez que entro a la plataforma

**Criterios de Aceptacion:**
- [ ] Campana de notificaciones en el header del portal con badge de no leidas
- [ ] Lista de notificaciones con: titulo, expediente, tipo, fecha, estado (leida/no leida)
- [ ] Click en notificacion navega al detalle del expediente
- [ ] Marcar como leida individual o "marcar todas como leidas"
- [ ] Filtro por tipo de evento y por expediente
- [ ] Paginacion (ultimas 50 notificaciones, cargar mas on-scroll)

**Tareas Tecnicas:**
- [ ] Crear endpoint `GET /api/v1/notifications` con filtros y paginacion
- [ ] Crear endpoint `PUT /api/v1/notifications/{id}/read`
- [ ] Crear endpoint `PUT /api/v1/notifications/mark-all-read`
- [ ] Query DynamoDB con GSI1 (USER#{user_id} | NOTIF#{timestamp})
- [ ] Tests: 5+ unit tests (list, mark read, mark all, filtros, paginacion)

**API:** `GET /api/v1/notifications`, `PUT /api/v1/notifications/{id}/read`, `PUT /api/v1/notifications/mark-all-read`

---

#### US-AT-025: Retry, DLQ y historial de notificaciones

**Como** Administrador AlertaTribunal
**Quiero** que las notificaciones fallidas se reintenten automaticamente y las irrecuperables vayan a DLQ
**Para** garantizar la maxima tasa de entrega y poder diagnosticar problemas

**Criterios de Aceptacion:**
- [ ] 3 intentos por notificacion fallida con backoff: 1m, 5m, 15m
- [ ] Si los 3 intentos fallan, el mensaje va a DLQ `notification-dlq`
- [ ] Historial completo de notificaciones por usuario: enviada, fallida, pendiente, DLQ
- [ ] Dashboard de admin: tasa de entrega por canal, notificaciones en DLQ, errores recientes
- [ ] Opcion de re-procesar mensajes de DLQ manualmente
- [ ] Metricas: tiempo promedio de entrega, tasa de exito por canal, notificaciones/dia

**Tareas Tecnicas:**
- [ ] Configurar SQS DLQ `notification-dlq` con max receive count = 3
- [ ] Crear endpoint `GET /api/v1/admin/notifications/metrics`
- [ ] Crear endpoint `POST /api/v1/admin/notifications/dlq/reprocess`
- [ ] Almacenar historial de intentos en DynamoDB
- [ ] Tests: 5+ unit tests (retry, DLQ, metricas, reprocess)

**API:** `GET /api/v1/admin/notifications/metrics`, `POST /api/v1/admin/notifications/dlq/reprocess`

---

### EP-AT-005: Portal Web AlertaTribunal

---

#### US-AT-026: Landing page publica de AlertaTribunal

**Como** visitante no registrado
**Quiero** ver una pagina publica que explique que es AlertaTribunal, sus beneficios y precios
**Para** decidir si me registro en el servicio

**Criterios de Aceptacion:**
- [ ] URL: alertatribunal.com
- [ ] Secciones: hero con propuesta de valor, como funciona (3 pasos), beneficios, precios, FAQ, formulario de contacto
- [ ] Responsive design (mobile-first)
- [ ] SEO optimizado: title, meta description, Open Graph, structured data (Organization)
- [ ] Velocidad: Lighthouse performance score > 90
- [ ] CTA: "Comienza gratis" que lleva al registro
- [ ] Testimonios de abogados (placeholder inicialmente)
- [ ] Seccion de tribunales cubiertos con mapa de Mexico

**Tareas Tecnicas:**
- [ ] Crear landing con HTML/CSS estatico o Angular SSR
- [ ] Configurar CloudFront + S3 para alertatribunal.com
- [ ] Implementar formulario de contacto (envio a SES)
- [ ] SEO: sitemap.xml, robots.txt, meta tags
- [ ] Tests: 3+ unit tests (render, formulario, responsive)

---

#### US-AT-027: Dashboard de usuario con resumen de actividad

**Como** Abogado
**Quiero** ver un dashboard al entrar a app.alertatribunal.com con resumen de mis expedientes y alertas
**Para** saber de un vistazo si hay novedades en mis casos

**Criterios de Aceptacion:**
- [ ] KPIs principales: expedientes suscritos, alertas no leidas, movimientos esta semana
- [ ] Lista de alertas recientes (ultimas 10) con acceso rapido al expediente
- [ ] Expedientes con movimiento reciente (ultimas 48h) destacados
- [ ] Proximas audiencias programadas (si aplica)
- [ ] Acciones rapidas: buscar expediente, ver todas las alertas, configuracion
- [ ] Estado de salud del scraper (si hay problemas que el usuario deba saber)

**Tareas Tecnicas:**
- [ ] Crear endpoint `GET /api/v1/dashboard` que agrega datos del usuario
- [ ] Frontend: componente dashboard con widgets responsivos
- [ ] Cache de dashboard en DynamoDB (TTL 5 min) para evitar queries pesados
- [ ] Tests: 4+ unit tests

**API:** `GET /api/v1/dashboard`

---

#### US-AT-028: Vista de expedientes suscritos

**Como** Abogado
**Quiero** ver la lista de todos los expedientes a los que estoy suscrito con su estado actual
**Para** monitorear todos mis casos desde un solo lugar

**Criterios de Aceptacion:**
- [ ] Lista de expedientes suscritos con: numero, juzgado, estado procesal, ultimo movimiento, fecha
- [ ] Ordenamiento: por ultimo movimiento (mas reciente primero) o por juzgado
- [ ] Filtro por estado de suscripcion: ACTIVE, PAUSED
- [ ] Filtro por tipo de juicio y juzgado
- [ ] Indicador visual de alertas no leidas por expediente
- [ ] Click en expediente navega al detalle con timeline
- [ ] Acciones rapidas por expediente: pausar/reanudar suscripcion, configurar alertas

**Tareas Tecnicas:**
- [ ] Frontend: componente lista de expedientes con filtros y ordenamiento
- [ ] Combinar datos de suscripciones + expedientes en una sola vista
- [ ] Tests: 4+ unit tests

---

#### US-AT-029: Vista de detalle de expediente con timeline

**Como** Abogado
**Quiero** ver el detalle completo de un expediente con su timeline de movimientos
**Para** entender la situacion actual del caso y revisar movimientos especificos

**Criterios de Aceptacion:**
- [ ] Header: numero de expediente, juzgado, tipo de juicio, estado procesal
- [ ] Sidebar: partes del juicio, funcionarios, datos del expediente
- [ ] Timeline cronologico de movimientos con iconos diferenciados por tipo
- [ ] Expandir/colapsar texto completo de cada movimiento
- [ ] Indicador de movimientos nuevos (desde la ultima visita)
- [ ] Tab de documentos asociados
- [ ] Tab de configuracion de suscripcion (canales, frecuencia, tipos de evento)
- [ ] Boton de desuscribirse

**Tareas Tecnicas:**
- [ ] Frontend: pagina de detalle con tabs (timeline, documentos, configuracion)
- [ ] Consumir APIs de expediente, timeline, documentos, suscripcion
- [ ] Tests: 4+ unit tests

---

#### US-AT-030: Busqueda de expedientes desde el portal

**Como** Abogado
**Quiero** buscar expedientes en AlertaTribunal para suscribirme a los que me interesan
**Para** agregar nuevos casos a mi monitoreo sin tener que registrarlos manualmente

**Criterios de Aceptacion:**
- [ ] Barra de busqueda prominente en el dashboard y en seccion dedicada
- [ ] Busqueda por numero de expediente (resultado inmediato si existe)
- [ ] Busqueda por nombre de parte (resultados con ranking de relevancia)
- [ ] Filtros: tribunal, tipo de juicio, materia
- [ ] Resultados muestran: expediente, juzgado, partes, estado, ultimo movimiento
- [ ] Boton "Suscribirme" en cada resultado (si no esta suscrito)
- [ ] Indicador si ya esta suscrito al expediente
- [ ] Si el expediente no existe en el sistema, opcion de "Solicitar monitoreo"

**Tareas Tecnicas:**
- [ ] Frontend: componente de busqueda con autocomplete y filtros
- [ ] Integrar con API de busqueda `GET /api/v1/cases?q=...`
- [ ] Crear flujo de "solicitar monitoreo" que crea el expediente manualmente
- [ ] Tests: 4+ unit tests

---

#### US-AT-031: Configuracion de cuenta y perfil

**Como** Abogado
**Quiero** configurar mi perfil, preferencias globales de notificacion y ver mi plan activo
**Para** gestionar mi cuenta de AlertaTribunal desde un solo lugar

**Criterios de Aceptacion:**
- [ ] Perfil: nombre, email (no editable, viene de Cognito), telefono, nombre del despacho
- [ ] Preferencias globales de notificacion (aplican como default a nuevas suscripciones)
- [ ] Gestion de numero de WhatsApp: agregar, verificar, cambiar
- [ ] Plan activo: nombre del plan, limites, uso actual (expedientes usados / total)
- [ ] Boton "Cambiar plan" que lleva a la pagina de planes
- [ ] Historial de facturacion (si tiene plan de pago)
- [ ] Opcion de eliminar cuenta (con confirmacion y periodo de gracia de 30 dias)

**Tareas Tecnicas:**
- [ ] Crear endpoints `GET/PUT /api/v1/profile`
- [ ] Frontend: pagina de configuracion con tabs (perfil, notificaciones, plan, facturacion)
- [ ] Integrar con Cognito para datos de autenticacion
- [ ] Tests: 4+ unit tests

**API:** `GET/PUT /api/v1/profile`

---

### EP-AT-006: Expansion a Otros Tribunales

---

#### US-AT-032: Interface TribunalDriver (Strategy Pattern)

**Como** Administrador AlertaTribunal
**Quiero** una interface comun que todos los drivers de tribunal implementen
**Para** poder agregar nuevos tribunales sin modificar el motor de scraping

**Criterios de Aceptacion:**
- [ ] Interface `TribunalDriver` con metodos:
  - `scrape(case_number: str) -> RawScrapingResult`
  - `parse(raw: RawScrapingResult) -> list[CaseMovement]`
  - `normalize(movements: list[CaseMovement]) -> list[NormalizedMovement]`
  - `health_check() -> DriverHealthStatus`
  - `get_supported_search_types() -> list[SearchType]`
- [ ] Modelos estandar: `RawScrapingResult`, `CaseMovement`, `NormalizedMovement`, `DriverHealthStatus`
- [ ] Factory method: `TribunalDriverFactory.get_driver(court_id) -> TribunalDriver`
- [ ] Registro de drivers en configuracion (YAML o variable de entorno)
- [ ] Documentacion de como crear un nuevo driver

**Tareas Tecnicas:**
- [ ] Crear ABC `TribunalDriver` en covacha-judicial
- [ ] Crear modelos Pydantic para datos estandarizados
- [ ] Crear `TribunalDriverFactory` con registry pattern
- [ ] Refactorizar scraper PJNL existente para implementar la interface
- [ ] Tests: 6+ unit tests (interface, factory, registro, driver no encontrado)

---

#### US-AT-033: Driver PJNL refactorizado

**Como** Sistema
**Quiero** que el scraper existente de PJNL se refactorice para implementar TribunalDriver
**Para** que sea el primer driver estandarizado y sirva de referencia para los siguientes

**Criterios de Aceptacion:**
- [ ] El scraper existente `mod_scrapper_mty` se migra a implementar `TribunalDriver`
- [ ] Todos los tests existentes siguen pasando
- [ ] El health check reporta estado del portal PJNL
- [ ] Los movimientos se normalizan al formato estandar
- [ ] El driver se registra en la factory con court_id `pjnl`
- [ ] Performance: misma o mejor velocidad que el scraper original

**Tareas Tecnicas:**
- [ ] Crear `PJNLDriver(TribunalDriver)` que encapsula logica existente
- [ ] Migrar parseo HTML a metodos `parse()` y `normalize()`
- [ ] Registrar driver en factory
- [ ] Tests: 5+ unit tests (scrape, parse, normalize, health_check)

---

#### US-AT-034: Driver TSJCDMX (Tribunal Superior de Justicia CDMX)

**Como** Administrador AlertaTribunal
**Quiero** un driver para el Tribunal Superior de Justicia de la Ciudad de Mexico
**Para** expandir la cobertura al mercado mas grande de abogados en Mexico

**Criterios de Aceptacion:**
- [ ] Driver `TSJCDMXDriver` implementa `TribunalDriver` completamente
- [ ] Parsea correctamente el portal del TSJ CDMX (consulta de expedientes)
- [ ] Extrae: expediente, juzgado, tipo, partes, movimientos
- [ ] Normaliza datos al formato estandar (compartido con PJNL)
- [ ] Health check funcional
- [ ] Manejo de diferencias del portal CDMX vs PJNL (estructura HTML diferente)

**Tareas Tecnicas:**
- [ ] Analizar estructura del portal del TSJ CDMX
- [ ] Implementar `TSJCDMXDriver(TribunalDriver)`
- [ ] Crear fixtures HTML del portal CDMX para tests
- [ ] Registrar driver en factory con court_id `tsjcdmx`
- [ ] Tests: 6+ unit tests (scrape, parse, normalize, edge cases del portal CDMX)

---

#### US-AT-035: Driver STJ Jalisco (Supremo Tribunal de Justicia)

**Como** Administrador AlertaTribunal
**Quiero** un driver para el Supremo Tribunal de Justicia de Jalisco
**Para** cubrir el tercer mercado mas grande de abogados en Mexico

**Criterios de Aceptacion:**
- [ ] Driver `STJJaliscoDriver` implementa `TribunalDriver` completamente
- [ ] Parsea correctamente el portal del STJ Jalisco
- [ ] Extrae y normaliza movimientos al formato estandar
- [ ] Health check funcional
- [ ] Manejo de particularidades del portal de Jalisco

**Tareas Tecnicas:**
- [ ] Analizar estructura del portal del STJ Jalisco
- [ ] Implementar `STJJaliscoDriver(TribunalDriver)`
- [ ] Crear fixtures HTML del portal Jalisco para tests
- [ ] Registrar driver en factory con court_id `stj_jalisco`
- [ ] Tests: 6+ unit tests

---

#### US-AT-036: Normalizacion de datos entre tribunales

**Como** Abogado
**Quiero** que los expedientes de diferentes tribunales se muestren con el mismo formato
**Para** no tener que aprender una interfaz diferente por cada tribunal

**Criterios de Aceptacion:**
- [ ] Modelo `NormalizedMovement` unificado con campos estandar
- [ ] Mapeo de tipos de movimiento: cada tribunal usa nombres diferentes, se normalizan a los mismos tipos
- [ ] Fechas en formato ISO 8601 independiente del formato del tribunal
- [ ] Nombres de partes normalizados (sin abreviaciones inconsistentes)
- [ ] Tipo de juicio mapeado a catalogo estandar (civil, familiar, mercantil, penal, laboral, administrativo)
- [ ] Test de normalizacion con datos reales de al menos 2 tribunales diferentes

**Tareas Tecnicas:**
- [ ] Crear catalogo de mapeo de tipos de movimiento por tribunal
- [ ] Crear catalogo de mapeo de tipos de juicio por tribunal
- [ ] Implementar normalizador de nombres (remover "LIC.", "C.", titulos)
- [ ] Tests: 5+ unit tests (normalizacion cross-tribunal, edge cases)

---

#### US-AT-037: Dashboard de cobertura de tribunales

**Como** Administrador AlertaTribunal
**Quiero** ver un dashboard con todos los tribunales soportados y el estado de cada driver
**Para** gestionar la expansion y detectar problemas de cobertura

**Criterios de Aceptacion:**
- [ ] Lista de tribunales con: nombre, estado (activo/inactivo/error), driver version, ultimo scrape exitoso
- [ ] Mapa de Mexico con tribunales cubiertos (marcados en verde)
- [ ] Metricas por tribunal: expedientes monitoreados, movimientos/dia, errores/dia
- [ ] Indicadores de salud: verde (<1h), amarillo (1-2h), rojo (>2h desde ultimo scrape)
- [ ] Boton para activar/desactivar un tribunal
- [ ] Log de errores recientes por tribunal

**Tareas Tecnicas:**
- [ ] Crear endpoint `GET /api/v1/admin/courts/coverage`
- [ ] Crear endpoint `PUT /api/v1/admin/courts/{court_id}/toggle`
- [ ] Almacenar metricas por tribunal en DynamoDB
- [ ] Tests: 4+ unit tests

**API:** `GET /api/v1/admin/courts/coverage`, `PUT /api/v1/admin/courts/{court_id}/toggle`

---

### EP-AT-007: Analisis IA de Documentos Judiciales

---

#### US-AT-038: Extraccion de entidades de textos judiciales

**Como** Abogado
**Quiero** que el sistema extraiga automaticamente fechas, montos, plazos y nombres de los textos de acuerdos
**Para** tener informacion estructurada sin leer todo el texto del movimiento

**Criterios de Aceptacion:**
- [ ] Extraccion de fechas (absolutas y relativas: "dentro de 10 dias")
- [ ] Extraccion de montos (pesos MXN, UDIs, salarios minimos)
- [ ] Extraccion de plazos (dias habiles/naturales, con fecha limite calculada)
- [ ] Extraccion de nombres de partes mencionadas
- [ ] Extraccion de articulos de ley citados
- [ ] Entidades presentadas como metadata estructurada en el movimiento
- [ ] Precision minima: 85% en datos de prueba

**Tareas Tecnicas:**
- [ ] Implementar pipeline NLP con spaCy o regex avanzado para entidades juridicas
- [ ] Crear modelo de entidades: `DateEntity`, `AmountEntity`, `DeadlineEntity`, `PersonEntity`
- [ ] Entrenar/configurar modelo con corpus de textos judiciales mexicanos
- [ ] Crear servicio `EntityExtractionService`
- [ ] Tests: 8+ unit tests (cada tipo de entidad, precision, edge cases)

---

#### US-AT-039: Clasificacion automatica de tipo de movimiento

**Como** Sistema
**Quiero** clasificar automaticamente cada movimiento en su tipo correcto (acuerdo, sentencia, auto, proveido)
**Para** que el usuario vea el tipo correcto aunque el scraper no lo detecte del HTML

**Criterios de Aceptacion:**
- [ ] Clasificador que analiza el texto del movimiento y asigna tipo
- [ ] Tipos: ACUERDO, SENTENCIA, AUTO, PROVEIDO, AUDIENCIA, EMPLAZAMIENTO, DESAHOGO, OTRO
- [ ] Precision minima: 90% en datos de prueba
- [ ] Confidence score por clasificacion (alta >0.9, media 0.7-0.9, baja <0.7)
- [ ] Si confidence es baja, se marca para revision manual
- [ ] El tipo clasificado por IA complementa (no reemplaza) el tipo del scraper

**Tareas Tecnicas:**
- [ ] Implementar clasificador basado en keywords + ML simple (o LLM via API)
- [ ] Crear dataset de entrenamiento con movimientos etiquetados manualmente
- [ ] Crear servicio `MovementClassifierService`
- [ ] Tests: 5+ unit tests (cada tipo, confidence levels, fallback)

---

#### US-AT-040: Resumen automatico de sentencias

**Como** Abogado
**Quiero** un resumen automatico de sentencias largas en maximo 200 palabras
**Para** entender rapidamente el fallo sin leer todo el documento

**Criterios de Aceptacion:**
- [ ] Genera resumen de 100-200 palabras para sentencias
- [ ] El resumen incluye: sentido del fallo (a favor/en contra), puntos resolutivos clave, condena (si aplica)
- [ ] Solo se aplica a movimientos tipo SENTENCIA
- [ ] El resumen se almacena junto al movimiento en DynamoDB
- [ ] Indicador visual "Resumen generado por IA" con opcion de ver texto completo
- [ ] El usuario puede reportar si el resumen es incorrecto (feedback)

**Tareas Tecnicas:**
- [ ] Integrar con LLM (OpenAI o Anthropic) para summarization
- [ ] Crear prompt especializado para resumenes de sentencias mexicanas
- [ ] Crear servicio `SummarizationService` con cache de resumenes
- [ ] Implementar endpoint de feedback: `POST /api/v1/cases/{id}/movements/{mov_id}/feedback`
- [ ] Tests: 4+ unit tests (resumen exitoso, movimiento no sentencia, feedback)

**API:** `POST /api/v1/cases/{id}/movements/{mov_id}/feedback`

---

#### US-AT-041: Deteccion de plazos criticos

**Como** Abogado
**Quiero** que el sistema detecte automaticamente plazos en los textos de acuerdos y calcule la fecha limite
**Para** no perder un plazo procesal por no leer el acuerdo a tiempo

**Criterios de Aceptacion:**
- [ ] Detecta frases de plazo: "se concede un termino de X dias", "dentro de los Y dias siguientes"
- [ ] Calcula fecha limite considerando dias habiles (excluyendo fines de semana y dias festivos oficiales)
- [ ] Calendario de dias festivos oficiales de Mexico actualizado
- [ ] Genera alerta especial de tipo PLAZO_CRITICO con fecha limite
- [ ] La alerta de plazo se envia como prioridad ALTA (siempre instantanea)
- [ ] Dashboard muestra plazos proximos a vencer (proximos 7 dias) con countdown

**Tareas Tecnicas:**
- [ ] Crear servicio `DeadlineDetectionService` con parser de plazos
- [ ] Implementar calculadora de dias habiles con calendario de festivos mexicanos
- [ ] Crear tipo de alerta especial PLAZO_CRITICO
- [ ] Crear endpoint `GET /api/v1/deadlines?days_ahead=7` para plazos proximos
- [ ] Tests: 6+ unit tests (dias habiles, festivos, plazos naturales vs habiles, edge cases)

**API:** `GET /api/v1/deadlines?days_ahead={days}`

---

#### US-AT-042: Alertas enriquecidas con analisis IA

**Como** Abogado
**Quiero** que las alertas que recibo incluyan un analisis breve de que significa el movimiento
**Para** tomar decisiones rapidas sin tener que abrir el portal y leer todo el texto

**Criterios de Aceptacion:**
- [ ] La alerta incluye un parrafo de analisis IA ademas de los datos del movimiento
- [ ] El analisis indica: que tipo de movimiento es, que implica para el caso, si hay plazo o accion requerida
- [ ] El analisis se adapta al tipo de movimiento (acuerdo vs sentencia vs audiencia)
- [ ] Template de email/WhatsApp incluye seccion "Analisis IA" diferenciada visualmente
- [ ] Disclaimer: "Este analisis es generado por IA y no constituye asesoria legal"
- [ ] El usuario puede deshabilitar analisis IA en sus preferencias

**Tareas Tecnicas:**
- [ ] Integrar EntityExtractionService + ClassifierService + SummarizationService en pipeline
- [ ] Crear servicio `AlertEnrichmentService` que enriquece alertas antes del despacho
- [ ] Modificar templates de notificacion para incluir seccion de analisis IA
- [ ] Agregar toggle `ia_analysis_enabled` en preferencias del usuario
- [ ] Tests: 5+ unit tests (enriquecimiento exitoso, IA deshabilitada, error de IA graceful)

---

### EP-AT-008: Monetizacion y Planes

---

#### US-AT-043: Definicion y gestion de planes

**Como** Administrador AlertaTribunal
**Quiero** definir los planes de suscripcion con sus limites y precios
**Para** monetizar el servicio de forma escalonada

**Criterios de Aceptacion:**
- [ ] Plan GRATIS: 3 expedientes, solo notificaciones in-app, sin analisis IA
- [ ] Plan PRO ($299 MXN/mes): 50 expedientes, todos los canales (email+WhatsApp+in-app), analisis IA basico, soporte por email
- [ ] Plan ENTERPRISE ($999 MXN/mes): expedientes ilimitados, todos los canales, analisis IA completo, API de acceso, soporte prioritario, multi-usuario (despacho)
- [ ] CRUD de planes: `GET/POST/PUT /api/v1/admin/plans`
- [ ] Cada plan tiene: id, nombre, precio, limites (JSON), features (lista), activo/inactivo
- [ ] Planes almacenados en DynamoDB con prefijo `PLAN#`

**Tareas Tecnicas:**
- [ ] Crear modelo `Plan` con limites y features
- [ ] Crear Blueprint `plans_bp` con CRUD de admin
- [ ] Seed inicial con los 3 planes definidos
- [ ] Tests: 5+ unit tests (CRUD, validaciones de limites)

**API:** `GET /api/v1/plans` (publico), `POST/PUT /api/v1/admin/plans` (admin)
**DynamoDB:** `PLAN#{plan_id} | META`

---

#### US-AT-044: Suscripcion a plan y trial period

**Como** Abogado
**Quiero** seleccionar un plan y comenzar a usarlo (con periodo de prueba para Pro)
**Para** acceder a las funcionalidades del plan elegido

**Criterios de Aceptacion:**
- [ ] Al registrarse, el usuario obtiene plan GRATIS automaticamente
- [ ] Boton "Upgrade a Pro" que activa trial de 14 dias sin pedir tarjeta
- [ ] Al finalizar trial: el usuario elige pagar o regresa a GRATIS
- [ ] Upgrade a ENTERPRISE requiere datos de pago desde el inicio
- [ ] Downgrade de ENTERPRISE a PRO o GRATIS con prorrateo del periodo pagado
- [ ] Si el usuario excede limites del plan, se le notifica y se le invita a upgrade
- [ ] Historial de cambios de plan por usuario

**Tareas Tecnicas:**
- [ ] Crear servicio `PlanSubscriptionService` con logica de upgrade/downgrade
- [ ] Crear endpoint `POST /api/v1/plan-subscription/upgrade`
- [ ] Crear endpoint `POST /api/v1/plan-subscription/downgrade`
- [ ] Implementar cron para vencimiento de trial (14 dias)
- [ ] Tests: 6+ unit tests (upgrade, downgrade, trial, vencimiento, prorrateo)

**API:** `POST /api/v1/plan-subscription/upgrade`, `POST /api/v1/plan-subscription/downgrade`, `GET /api/v1/plan-subscription`
**DynamoDB:** `USER#{user_id} | PLAN_SUB`

---

#### US-AT-045: Integracion con pasarela de pago

**Como** Abogado
**Quiero** pagar mi suscripcion Pro o Enterprise con tarjeta de credito/debito
**Para** mantener el servicio activo mes a mes de forma automatica

**Criterios de Aceptacion:**
- [ ] Integracion con Openpay (pasarela del ecosistema SuperPago) para cobro recurrente
- [ ] Formulario seguro de captura de tarjeta (tokenizacion, nunca datos en backend)
- [ ] Cobro automatico mensual en la fecha de registro
- [ ] Reintentos de cobro: dia 1, dia 3, dia 7 despues de fecha de cobro
- [ ] Si despues de 3 intentos no se cobra: downgrade automatico a plan GRATIS
- [ ] Email de confirmacion de pago y factura electronica
- [ ] Historial de pagos con montos, fechas y estatus

**Tareas Tecnicas:**
- [ ] Integrar con Openpay API para suscripciones recurrentes
- [ ] Crear servicio `PaymentService` con tokenizacion y cobro
- [ ] Crear webhook handler para eventos de Openpay (cobro exitoso, fallido)
- [ ] Crear cron de reintentos de cobro
- [ ] Nunca almacenar datos de tarjeta en nuestro backend (solo token de Openpay)
- [ ] Tests: 6+ unit tests (cobro exitoso, fallido, reintento, downgrade, idempotencia)

**API:** `POST /api/v1/payments/setup-card`, `GET /api/v1/payments/history`

---

#### US-AT-046: Metricas de conversion y revenue

**Como** Administrador AlertaTribunal
**Quiero** ver metricas de conversion (free -> pro -> enterprise), churn y revenue
**Para** tomar decisiones de negocio informadas sobre precios y marketing

**Criterios de Aceptacion:**
- [ ] Dashboard con KPIs: usuarios totales, usuarios por plan, MRR (Monthly Recurring Revenue)
- [ ] Funnel de conversion: registros -> free -> trial -> pro -> enterprise
- [ ] Churn rate mensual (usuarios que bajan de plan o cancelan)
- [ ] LTV estimado (Lifetime Value) por segmento
- [ ] Graficas de tendencia: usuarios, revenue, churn (ultimos 6 meses)
- [ ] Exportar metricas como CSV

**Tareas Tecnicas:**
- [ ] Crear endpoint `GET /api/v1/admin/metrics/revenue`
- [ ] Pre-computar metricas agregadas en cron diario (evitar scans pesados)
- [ ] Almacenar metricas en DynamoDB con PK `METRICS#revenue` y SK por fecha
- [ ] Tests: 4+ unit tests

**API:** `GET /api/v1/admin/metrics/revenue`

---

## Roadmap

### Fase 1 - Fundamentos (Sprint 1-3)

```
EP-AT-001: Motor de Scraping (US-AT-001 a US-AT-007)
  - Scheduling, parseo PJNL, deteccion de cambios, snapshots, anti-ban, retry
EP-AT-002: Gestion de Expedientes (US-AT-008 a US-AT-013)
  - CRUD, busqueda, timeline, metadatos, documentos, estado procesal
```

**Razon**: Sin scraper y expedientes no hay producto. Son los cimientos sobre los que todo lo demas se construye. El scraper PJNL ya tiene base en `mod_scrapper_mty`, lo que acelera el desarrollo.

**Entregable**: API funcional que scrapea PJNL, almacena expedientes y detecta cambios.

### Fase 2 - Core del Producto (Sprint 3-5)

```
EP-AT-003: Suscripciones y Alertas (US-AT-014 a US-AT-019)
  - Suscripcion a expedientes, configuracion de alertas, generacion de alertas
EP-AT-004: Notificaciones Multi-Canal (US-AT-020 a US-AT-025)
  - Dispatcher, templates, email, WhatsApp, in-app, retry/DLQ
```

**Razon**: Las suscripciones y notificaciones son la propuesta de valor diferenciadora. Un abogado se suscribe a expedientes y recibe alertas. Sin esto no hay razon para usar AlertaTribunal vs revisar el portal manualmente.

**Entregable**: Sistema completo de alertas end-to-end. Un abogado puede suscribirse y recibir emails/WhatsApp cuando hay movimientos.

### Fase 3 - Portal Web (Sprint 5-7)

```
EP-AT-005: Portal Web AlertaTribunal (US-AT-026 a US-AT-031)
  - Landing publica, dashboard, vista de expedientes, detalle, busqueda, configuracion
EP-AT-008: Monetizacion y Planes (US-AT-043 a US-AT-046)
  - Planes, trial, pasarela de pago, metricas
```

**Razon**: El portal web es la interfaz principal del usuario. La monetizacion se lanza junto con el portal para capturar revenue desde el primer dia con usuarios reales. El trial de 14 dias reduce friccion de adopcion.

**Entregable**: Producto completo lanzable al mercado con landing, dashboard, planes y cobro.

### Fase 4 - Expansion (Sprint 7-9)

```
EP-AT-006: Expansion a Otros Tribunales (US-AT-032 a US-AT-037)
  - Strategy Pattern, drivers CDMX y Jalisco, normalizacion, dashboard de cobertura
```

**Razon**: Expandir cobertura es critico para crecer mas alla de Nuevo Leon. CDMX y Jalisco representan ~40% del mercado de abogados en Mexico. La arquitectura de drivers permite agregar tribunales sin reescribir el core.

**Entregable**: Cobertura de 3 tribunales (NL, CDMX, Jalisco), ~60% del mercado objetivo.

### Fase 5 - Diferenciacion IA (Sprint 9-12)

```
EP-AT-007: Analisis IA de Documentos Judiciales (US-AT-038 a US-AT-042)
  - Extraccion de entidades, clasificacion, resumenes, plazos criticos, alertas enriquecidas
```

**Razon**: La IA es el diferenciador de largo plazo. Permite a AlertaTribunal ofrecer valor mas alla de las alertas basicas: deteccion de plazos criticos, resumenes de sentencias, y alertas que explican que significa cada movimiento. Es lo que justifica el plan Enterprise.

**Entregable**: Alertas inteligentes con analisis IA, deteccion de plazos, y resumenes automaticos.

---

## Grafo de Dependencias

```
EP-AT-001 (Motor de Scraping)
  └── No depende de otras epicas (puede empezar inmediatamente)
  └── Depende de: mod_scrapper_mty (codigo existente)
  └── Bloquea: EP-AT-002, EP-AT-003, EP-AT-006, EP-AT-007

EP-AT-002 (Gestion de Expedientes)
  └── Depende de: EP-AT-001 (scraper alimenta expedientes)
  └── Bloquea: EP-AT-003, EP-AT-005, EP-AT-007

EP-AT-003 (Suscripciones y Alertas)
  └── Depende de: EP-AT-001 (deteccion de cambios genera alertas)
  └── Depende de: EP-AT-002 (expedientes existen para suscribirse)
  └── Bloquea: EP-AT-004, EP-AT-005

EP-AT-004 (Notificaciones Multi-Canal)
  └── Depende de: EP-AT-003 (alertas que despachar)
  └── Depende de: covacha-botia (WhatsApp, existente)
  └── Depende de: covacha-notification (email, existente)
  └── Bloquea: ninguna (fin de cadena de notificaciones)

EP-AT-005 (Portal Web)
  └── Depende de: EP-AT-002 (API de expedientes)
  └── Depende de: EP-AT-003 (API de suscripciones)
  └── Se beneficia de: EP-AT-004 (notificaciones in-app)
  └── Bloquea: EP-AT-008 (el portal es donde se selecciona plan)

EP-AT-006 (Expansion Tribunales)
  └── Depende de: EP-AT-001 (motor de scraping base)
  └── Independiente de: EP-AT-003, EP-AT-004, EP-AT-005
  └── Se beneficia de: EP-AT-007 (IA normaliza datos entre tribunales)

EP-AT-007 (Analisis IA)
  └── Depende de: EP-AT-001 (textos del scraper)
  └── Depende de: EP-AT-002 (contexto del expediente)
  └── Se integra con: EP-AT-004 (alertas enriquecidas con IA)
  └── Independiente de: EP-AT-005, EP-AT-006, EP-AT-008

EP-AT-008 (Monetizacion)
  └── Depende de: EP-AT-005 (portal web para seleccion de plan)
  └── Se integra con: EP-AT-003 (limites de suscripciones segun plan)
  └── Independiente de: EP-AT-006, EP-AT-007
```

### Diagrama Visual de Dependencias

```
                    +-------------+
                    | EP-AT-001   |
                    | Scraping    |
                    +------+------+
                           |
              +------------+------------+
              |                         |
      +-------v-------+       +--------v-------+
      | EP-AT-002      |       | EP-AT-006      |
      | Expedientes    |       | Expansion      |
      +-------+--------+       | Tribunales     |
              |                 +----------------+
      +-------v--------+
      | EP-AT-003       |
      | Suscripciones   |
      +---+--------+----+
          |        |
  +-------v--+  +--v-----------+
  | EP-AT-004|  | EP-AT-005    |
  | Notific. |  | Portal Web   |
  +----------+  +------+-------+
                       |
                +------v-------+
                | EP-AT-008    |
                | Monetizacion |
                +--------------+

        +-------------+
        | EP-AT-007   |  (Independiente, conecta con 001, 002, 004)
        | Analisis IA |
        +-------------+
```

---

## Riesgos y Mitigaciones

| # | Riesgo | Impacto | Probabilidad | Mitigacion |
|---|--------|---------|--------------|------------|
| R1 | Portal del tribunal cambia estructura HTML sin aviso | Scraper deja de funcionar, alertas se detienen | **Alta** | Auto-deteccion de cambios de estructura (health check), snapshots para debugging, alertas al admin en <1h, driver refactorable rapidamente |
| R2 | Tribunal bloquea IP del scraper (ban) | Servicio no disponible para ese tribunal | **Alta** | Rotacion de IPs (proxy pool), delays aleatorios, rate limiting conservador, respeto a robots.txt, backup con scraping manual temporal |
| R3 | Volumen de expedientes crece y DynamoDB scan se vuelve lento | Dashboard y busquedas lentas | **Media** | GSIs optimizados desde el inicio, pre-computar metricas en cron, cache de resultados frecuentes (TTL 5min), paginacion cursor-based |
| R4 | Costos de IA (LLM) escalan con volumen de movimientos | Margen del plan Pro se erosiona | **Media** | Limitar analisis IA a planes Pro/Enterprise, cache de resultados, usar modelos mas baratos para clasificacion (no LLM), batch processing en horarios off-peak |
| R5 | Regulacion legal sobre scraping de portales publicos | Demanda o cease-and-desist del tribunal | **Baja** | Los portales de tribunales son informacion publica, respetar robots.txt y terms of service, rate limiting conservador, consulta legal preventiva |
| R6 | Baja adopcion: abogados no confian en sistema automatizado | Revenue insuficiente para sostener el producto | **Media** | Trial gratuito de 14 dias, testimoniales de abogados early adopters, demostraciones en colegios de abogados, contenido educativo sobre el producto |
| R7 | Precision de IA insuficiente genera alertas erroneas | Usuarios pierden confianza y cancelan | **Media** | Disclaimer visible, feedback loop del usuario, threshold de confidence (no enviar si <0.7), revision humana para sentencias, mejora continua con datos reales |
| R8 | Openpay rechaza integracion para AlertaTribunal (diferente merchant) | No se puede cobrar a usuarios | **Baja** | Tener Stripe como pasarela alternativa, AlertaTribunal puede operar como sub-merchant de SuperPago inicialmente |
| R9 | WhatsApp Business rechaza templates de AlertaTribunal | Canal WhatsApp no disponible | **Media** | Disenar templates que cumplan politicas de Meta desde el inicio, tener email como fallback, iterar con Meta hasta aprobacion |
| R10 | Expedientes con datos sensibles (menores, familia) | Violacion de privacidad | **Media** | No scrapear materias sensibles (familiar con menores), filtrar por materia, cumplir con Ley de Proteccion de Datos Personales |

---

## Definition of Done (Global)

Para considerar una user story como DONE:

- [ ] Codigo implementado en Python 3.9+ con Flask Blueprints
- [ ] Type hints en todas las funciones
- [ ] Docstrings en espanol para funciones publicas
- [ ] Unit tests con coverage >= 98% (pytest)
- [ ] Manejo de errores con try/except especificos (nunca bare except)
- [ ] Ningun archivo > 1000 lineas
- [ ] Ninguna funcion > 50 lineas
- [ ] DynamoDB: prefijos de keys correctos (CASE#, ALERT#, COURT#, SUB#, NOTIF#, PLAN#)
- [ ] API endpoints documentados con docstrings (OpenAPI compatible)
- [ ] Logs estructurados para debugging
- [ ] Code review aprobado
- [ ] PR creado automaticamente via GitHub Actions (coverage >= 98%)
- [ ] Variables de entorno para credenciales y configuracion sensible (nunca hardcoded)
