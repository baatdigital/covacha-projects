# CRM WhatsApp-First para PyMEs Mexicanas (EP-CW-001 a EP-CW-008)

**Fecha**: 2026-03-14
**Product Owner**: SuperPago
**Estado**: Planificacion
**GitHub Issue**: baatdigital/covacha-projects#127
**Score**: 8/10 | **Time to Market**: 14 semanas | **Reuso**: 65%

---

## Tabla de Contenidos

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Analisis de Mercado](#analisis-de-mercado)
3. [Reutilizacion del Ecosistema](#reutilizacion-del-ecosistema)
4. [Mapa de Epicas](#mapa-de-epicas)
5. [Epicas Detalladas](#epicas-detalladas)
6. [User Stories Detalladas](#user-stories-detalladas)
7. [Timeline](#timeline)
8. [Dependencias entre Epicas](#dependencias-entre-epicas)
9. [Riesgos y Mitigaciones](#riesgos-y-mitigaciones)

---

## Resumen Ejecutivo

CRM disenado desde cero para PyMEs mexicanas donde WhatsApp es el canal principal de comunicacion con clientes. No es un CRM tradicional con WhatsApp como add-on: es una experiencia WhatsApp-first con funcionalidad CRM integrada. Incluye inbox unificado, pipeline de ventas Kanban, automatizaciones con IA, y cierre de venta con pago SPEI.

**Propuesta de valor**: El 90% de las PyMEs mexicanas usan WhatsApp como canal principal. Este CRM pone WhatsApp al centro, no como un canal mas.

---

## Analisis de Mercado

| Metrica | Valor |
|---------|-------|
| **TAM Mexico** | $27B MXN/ano (4.5M PyMEs x $500/mes) |
| **SAM** | $3B MXN/ano (500K PyMEs digitalizadas) |
| **SOM Year 1** | $6M MXN/ano (1,000 clientes x $499/mes) |

### Problema de Mercado

- 90% de PyMEs mexicanas usan WhatsApp como canal principal
- CRMs existentes (HubSpot, Salesforce) tratan WhatsApp como canal secundario
- No hay CRM nativo WhatsApp-first en Mexico a precio accesible
- PyMEs pierden ventas por falta de seguimiento en WhatsApp

### Modelo de Revenue

| Plan | Precio MXN/mes | Contactos | Conversaciones/mes |
|------|---------------|-----------|-------------------|
| Starter | $299 | 500 | 1,000 |
| Pro | $699 | 5,000 | 10,000 |
| Business | $1,499 | Ilimitados | 50,000 |

---

## Reutilizacion del Ecosistema

| Componente | Repo Existente | Reutilizacion | Descripcion |
|-----------|---------------|---------------|-------------|
| WhatsApp Business API | covacha-botia | 90% | Envio/recepcion, webhooks |
| IA conversacional | covacha-botia | 80% | Clasificacion de intenciones |
| Multi-tenant | covacha-core | 100% | Organizaciones, auth |
| Pagos SPEI | covacha-payment | 100% | Cierre de venta con pago |
| Client management | mf-marketing | 60% | Gestion de contactos base |
| Shell MF | mf-core | 100% | Module Federation |
| Modelos base | covacha-libs | 70% | Modelos, repositorios |
| **Nuevo** | covacha-crm (extiende) | 30% | Pipeline, deals, actividades |
| **Nuevo** | mf-crm | 0% | Micro-frontend completo |

**Reutilizacion total estimada**: 65%

---

## Mapa de Epicas

| ID | Epica | Complejidad | Semana | Dependencias | Estado |
|----|-------|-------------|--------|--------------|--------|
| EP-CW-001 | Core CRM Data Model y Contactos | L | 1-3 | covacha-core | Planificacion |
| EP-CW-002 | Inbox Unificado WhatsApp | XL | 2-5 | EP-CW-001, covacha-botia | Planificacion |
| EP-CW-003 | Pipeline de Ventas Kanban | L | 3-5 | EP-CW-001 | Planificacion |
| EP-CW-004 | Automatizaciones y Clasificacion IA | L | 5-7 | EP-CW-002, EP-CW-003 | Planificacion |
| EP-CW-005 | Cotizaciones y Cierre de Venta | M | 6-8 | EP-CW-003, covacha-payment | Planificacion |
| EP-CW-006 | Multi-Agente y Asignacion | M | 5-7 | EP-CW-002 | Planificacion |
| EP-CW-007 | Dashboard CRM y Analytics | M | 8-10 | EP-CW-001 a EP-CW-006 | Planificacion |
| EP-CW-008 | mf-crm - Micro-Frontend PWA | XL | 4-14 | EP-CW-001 a EP-CW-007 | Planificacion |

**Totales:**
- 8 epicas
- 42 user stories (US-CW-001 a US-CW-042)
- Estimacion total: ~98 dev-days (14 semanas, 2 devs)

---

## Epicas Detalladas

---

### EP-CW-001: Core CRM Data Model y Contactos

**Descripcion:**
Modelo de datos central del CRM: contactos, empresas, actividades, notas, tags. Cada contacto esta vinculado a su numero de WhatsApp como identificador primario. Incluye CRUD completo, busqueda, filtros, y enriquecimiento basico de perfil.

**User Stories:**
- US-CW-001: Modelo de contacto con WhatsApp como ID primario
- US-CW-002: CRUD de contactos con validacion
- US-CW-003: Tags y segmentacion de contactos
- US-CW-004: Notas y actividades por contacto
- US-CW-005: Importacion masiva de contactos desde CSV/WhatsApp

**Criterios de Aceptacion de la Epica:**
- [ ] Modelo Contacto: nombre, telefono (PK), email, empresa, tags, notas, custom_fields
- [ ] Telefono WhatsApp como identificador unico (formato +52XXXXXXXXXX)
- [ ] CRUD completo con validacion de campos
- [ ] Tags personalizables para segmentacion
- [ ] Actividades: llamada, mensaje, reunion, nota, tarea
- [ ] Timeline de actividades por contacto
- [ ] Importacion desde CSV con deduplicacion
- [ ] Busqueda full-text por nombre, telefono, empresa, tags
- [ ] Campos personalizados (custom fields) por organizacion
- [ ] Tests >= 98%

**Dependencias:** covacha-core (multi-tenant)

**Complejidad:** L (5 user stories)

**Repositorios:** `covacha-crm`, `covacha-libs`

---

### EP-CW-002: Inbox Unificado WhatsApp

**Descripcion:**
Bandeja de entrada unificada que muestra todas las conversaciones de WhatsApp de la empresa. Similar a un cliente de email pero para WhatsApp. Soporta multiples numeros, asignacion de conversaciones a agentes, y estados (nueva, en curso, resuelta).

**User Stories:**
- US-CW-006: Vista de inbox con todas las conversaciones activas
- US-CW-007: Detalle de conversacion con historial completo
- US-CW-008: Enviar y recibir mensajes desde el inbox (texto, imagen, audio, documento)
- US-CW-009: Estados de conversacion: nueva, en curso, esperando, resuelta
- US-CW-010: Respuestas rapidas y templates predefinidos
- US-CW-011: Vinculacion automatica conversacion-contacto CRM

**Criterios de Aceptacion de la Epica:**
- [ ] Vista lista de conversaciones ordenada por ultimo mensaje
- [ ] Indicador de mensajes no leidos
- [ ] Detalle con historial completo de mensajes (texto, media, documentos)
- [ ] Enviar mensajes de texto, imagenes, documentos, audio desde la UI
- [ ] Estados: NEW, IN_PROGRESS, WAITING, RESOLVED con transiciones
- [ ] Respuestas rapidas: shortcuts con /comando
- [ ] Templates de WhatsApp Business aprobados por Meta
- [ ] Vinculacion automatica: numero -> contacto CRM existente
- [ ] Creacion automatica de contacto si no existe
- [ ] Tests >= 98%

**Dependencias:** EP-CW-001, covacha-botia (WhatsApp API)

**Complejidad:** XL (6 user stories, integracion profunda con WhatsApp)

**Repositorios:** `covacha-botia`, `covacha-crm`

---

### EP-CW-003: Pipeline de Ventas Kanban

**Descripcion:**
Pipeline de ventas visual estilo Kanban donde cada tarjeta es un "deal" vinculado a un contacto de WhatsApp. Las columnas representan etapas del proceso de venta (Nuevo lead, Cotizacion, Negociacion, Cierre). Drag & drop para mover deals entre etapas.

**User Stories:**
- US-CW-012: Modelo de Deal con etapas configurables
- US-CW-013: Vista Kanban con drag & drop
- US-CW-014: Detalle del deal con actividades y conversacion WhatsApp
- US-CW-015: Pipelines multiples configurables por equipo
- US-CW-016: Automatizacion basica: mover deal al recibir mensaje

**Criterios de Aceptacion de la Epica:**
- [ ] Modelo Deal: nombre, monto, contacto, etapa, probabilidad, fecha_cierre
- [ ] Etapas configurables (default: Lead, Cotizacion, Negociacion, Propuesta, Ganado, Perdido)
- [ ] Vista Kanban con tarjetas drag & drop
- [ ] Tarjeta muestra: nombre, monto, contacto, ultimo mensaje WhatsApp
- [ ] Detalle del deal incluye conversacion WhatsApp del contacto
- [ ] Pipeline multiples: ventas, soporte, proyectos
- [ ] Filtros: por agente, monto, fecha, probabilidad
- [ ] Valor total del pipeline por etapa
- [ ] Automatizacion: nuevo mensaje WhatsApp de contacto sin deal → crear deal
- [ ] Tests >= 98%

**Dependencias:** EP-CW-001 (contactos)

**Complejidad:** L (5 user stories)

**Repositorios:** `covacha-crm`

---

### EP-CW-004: Automatizaciones y Clasificacion IA

**Descripcion:**
Motor de automatizaciones que usa IA para clasificar mensajes entrantes, asignar tags automaticamente, mover deals en el pipeline, y enviar respuestas automaticas. Incluye reglas configurables (if-then) y clasificacion inteligente de intenciones.

**User Stories:**
- US-CW-017: Clasificacion IA de intenciones de mensajes entrantes
- US-CW-018: Auto-tag de contactos basado en conversacion
- US-CW-019: Auto-respuestas configurables por intencion
- US-CW-020: Reglas de automatizacion if-then personalizables
- US-CW-021: Asignacion automatica de conversaciones por reglas

**Criterios de Aceptacion de la Epica:**
- [ ] IA clasifica intenciones: comprar, cotizar, soporte, queja, informacion
- [ ] Auto-tag basado en productos mencionados, intenciones, sentimiento
- [ ] Auto-respuesta configurable por intencion (ej: "cotizar" → enviar catalogo)
- [ ] Motor de reglas: IF [condicion] THEN [accion]
- [ ] Condiciones: intencion, tag, etapa, horario, agente disponible
- [ ] Acciones: responder, asignar, mover deal, crear tarea, notificar
- [ ] Reglas evaluadas en orden de prioridad
- [ ] Log de automatizaciones ejecutadas
- [ ] Toggle on/off por regla
- [ ] Tests >= 98%

**Dependencias:** EP-CW-002 (inbox), EP-CW-003 (pipeline)

**Complejidad:** L (5 user stories)

**Repositorios:** `covacha-botia`, `covacha-crm`

---

### EP-CW-005: Cotizaciones y Cierre de Venta

**Descripcion:**
Sistema de cotizaciones que se generan y envian directamente por WhatsApp. El vendedor arma la cotizacion con productos/servicios, la envia al contacto por WhatsApp, y puede cerrar la venta con un link de pago SPEI integrado. Todo sin salir del CRM.

**User Stories:**
- US-CW-022: Crear cotizacion con productos/servicios y precios
- US-CW-023: Enviar cotizacion por WhatsApp (PDF + link de pago)
- US-CW-024: Tracking de cotizacion: enviada, vista, aceptada, rechazada
- US-CW-025: Cierre de venta con link de pago SPEI
- US-CW-026: Integracion con catalogo de productos (mf-inventory)

**Criterios de Aceptacion de la Epica:**
- [ ] Cotizacion: items (nombre, cantidad, precio), subtotal, IVA, total
- [ ] Templates de cotizacion personalizables con logo de la empresa
- [ ] PDF generado y enviado por WhatsApp
- [ ] Link de pago SPEI embebido en la cotizacion
- [ ] Estado: DRAFT, SENT, VIEWED, ACCEPTED, REJECTED, PAID
- [ ] Notificacion cuando el cliente abre la cotizacion
- [ ] Aceptacion: cliente responde "ACEPTO" o paga via link
- [ ] Integracion con catalogo de productos existente
- [ ] Conversion automatica cotizacion → venta al recibir pago
- [ ] Tests >= 98%

**Dependencias:** EP-CW-003 (pipeline), covacha-payment (SPEI)

**Complejidad:** M (5 user stories)

**Repositorios:** `covacha-crm`, `covacha-payment`

---

### EP-CW-006: Multi-Agente y Asignacion

**Descripcion:**
Sistema que permite multiples vendedores/agentes compartir los numeros de WhatsApp de la empresa. Cada agente tiene su bandeja de conversaciones asignadas. Incluye asignacion automatica (round-robin, por carga, por skill) y transferencia entre agentes.

**User Stories:**
- US-CW-027: Registro de agentes con perfil y habilidades
- US-CW-028: Asignacion automatica de conversaciones (round-robin, carga, skill)
- US-CW-029: Transferencia de conversacion entre agentes
- US-CW-030: Vista por agente: "Mis conversaciones"
- US-CW-031: Indicadores de carga por agente y disponibilidad

**Criterios de Aceptacion de la Epica:**
- [ ] CRUD de agentes con: nombre, email, habilidades, horario, max_conversaciones
- [ ] Asignacion automatica: round-robin, por carga, por skill match
- [ ] Transferencia con nota interna ("Te paso este cliente porque...")
- [ ] Vista filtrada: solo mis conversaciones vs todas
- [ ] Estado de agente: disponible, ocupado, ausente
- [ ] Indicador de carga: conversaciones activas vs maximo
- [ ] Reasignacion automatica cuando agente se ausenta
- [ ] Historial de asignaciones por conversacion
- [ ] Metricas: tiempo de respuesta por agente, conversaciones resueltas
- [ ] Tests >= 98%

**Dependencias:** EP-CW-002 (inbox)

**Complejidad:** M (5 user stories)

**Repositorios:** `covacha-crm`

---

### EP-CW-007: Dashboard CRM y Analytics

**Descripcion:**
Dashboard con metricas de ventas, actividad de WhatsApp, rendimiento de agentes, y conversion del pipeline. Incluye reportes configurables, KPIs en tiempo real, y proyeccion de ventas.

**User Stories:**
- US-CW-032: Dashboard principal: ventas, pipeline, actividad WhatsApp
- US-CW-033: Metricas de WhatsApp: response time, mensajes, conversaciones
- US-CW-034: Rendimiento por agente: ventas, deals, tiempo de respuesta
- US-CW-035: Reporte de conversion del pipeline
- US-CW-036: Proyeccion de ventas basada en pipeline actual

**Criterios de Aceptacion de la Epica:**
- [ ] KPIs principales: ventas cerradas, deals activos, conversion rate
- [ ] Metricas WhatsApp: tiempo de primera respuesta, mensajes/dia, tasa de resolucion
- [ ] Ranking de agentes por: ventas, deals cerrados, response time
- [ ] Conversion rate por etapa del pipeline (funnel)
- [ ] Proyeccion de ventas: pipeline value x probabilidad por etapa
- [ ] Filtros: periodo, agente, pipeline, tag
- [ ] Graficas interactivas (linea, barras, pie, funnel)
- [ ] Export PDF/Excel
- [ ] Datos en tiempo real (refresh cada 30s)
- [ ] Tests >= 98%

**Dependencias:** EP-CW-001 a EP-CW-006

**Complejidad:** M (5 user stories)

**Repositorios:** `mf-crm`

---

### EP-CW-008: mf-crm - Micro-Frontend PWA

**Descripcion:**
Micro-frontend Angular completo para el CRM con soporte PWA (Progressive Web App). Mobile-first para que los vendedores puedan gestionar conversaciones desde el celular. Incluye inbox, pipeline, contactos, cotizaciones, y dashboard. Se integra con mf-core via Module Federation.

**User Stories:**
- US-CW-037: Scaffold mf-crm con Module Federation + PWA
- US-CW-038: Pantalla de inbox WhatsApp (mobile-first)
- US-CW-039: Pantalla de pipeline Kanban (responsive)
- US-CW-040: Pantalla de contactos con detalle y timeline
- US-CW-041: Pantalla de cotizaciones
- US-CW-042: Pantalla de dashboard con graficas

**Criterios de Aceptacion de la Epica:**
- [ ] mf-crm registrado en mf-core como micro-frontend
- [ ] PWA: instalable, funciona offline (lectura), push notifications
- [ ] Inbox: lista de conversaciones + detalle con chat (mobile-first)
- [ ] Pipeline: Kanban con drag & drop (responsive, tactil)
- [ ] Contactos: lista + detalle con timeline de actividades
- [ ] Cotizaciones: crear, editar, enviar, tracking
- [ ] Dashboard: graficas con ngx-echarts
- [ ] Standalone components, OnPush, Signals
- [ ] Routing con lazy loading por seccion
- [ ] Tests >= 98%

**Dependencias:** EP-CW-001 a EP-CW-007

**Complejidad:** XL (6 user stories, frontend completo PWA)

**Repositorios:** `mf-crm`, `mf-core`

---

## User Stories Detalladas

### EP-CW-001: Core CRM Data Model y Contactos

#### US-CW-001: Modelo de contacto con WhatsApp como ID primario
**Como** desarrollador, **quiero** un modelo de contacto con telefono WhatsApp como clave **para que** cada contacto sea unico por numero.

**Criterios de Aceptacion:**
- [ ] Modelo en covacha-libs: PK=ORG#{org_id}, SK=CONTACT#{phone}
- [ ] Campos: nombre, telefono, email, empresa, cargo, tags[], notas, custom_fields{}
- [ ] Telefono validado formato +52XXXXXXXXXX
- [ ] created_at, updated_at, last_contact_at
- [ ] GSI por email para busqueda alternativa

#### US-CW-002: CRUD de contactos
**Como** vendedor, **quiero** crear y gestionar contactos **para que** tenga mi base de clientes organizada.

**Criterios de Aceptacion:**
- [ ] Endpoints: POST/GET/PUT/DELETE /crm/contacts
- [ ] Validacion de campos obligatorios (nombre, telefono)
- [ ] Paginacion con cursor para listas grandes
- [ ] Soft delete (no eliminar datos, solo marcar)
- [ ] Busqueda full-text por nombre, telefono, empresa

#### US-CW-003: Tags y segmentacion
**Como** vendedor, **quiero** etiquetar contactos **para que** pueda segmentarlos por interes o tipo.

**Criterios de Aceptacion:**
- [ ] Tags libres (texto) asociados al contacto
- [ ] Tags predefinidos por organizacion
- [ ] Filtro de contactos por 1 o mas tags (AND/OR)
- [ ] Conteo de contactos por tag
- [ ] Bulk tagging (aplicar tag a multiples contactos)

#### US-CW-004: Notas y actividades
**Como** vendedor, **quiero** registrar notas y actividades de cada contacto **para que** todo el equipo tenga contexto.

**Criterios de Aceptacion:**
- [ ] Tipos de actividad: nota, llamada, reunion, tarea, whatsapp
- [ ] Cada actividad con: tipo, descripcion, fecha, agente
- [ ] Timeline cronologico en el detalle del contacto
- [ ] Tareas con fecha de vencimiento y estado (pendiente, completada)
- [ ] Notificacion de tarea proxima a vencer

#### US-CW-005: Importacion masiva de contactos
**Como** empresa, **quiero** importar mi base de clientes existente **para que** no tenga que capturar uno por uno.

**Criterios de Aceptacion:**
- [ ] Import CSV con columnas: nombre, telefono, email, empresa, tags
- [ ] Deduplicacion por telefono
- [ ] Reporte de errores y duplicados
- [ ] Maximo 10,000 contactos por import
- [ ] Progreso visible durante importacion

### EP-CW-002: Inbox Unificado WhatsApp

#### US-CW-006: Vista de inbox con conversaciones activas
**Como** vendedor, **quiero** ver todas mis conversaciones de WhatsApp en un solo lugar **para que** no pierda ningun mensaje.

**Criterios de Aceptacion:**
- [ ] Lista de conversaciones ordenada por ultimo mensaje
- [ ] Preview del ultimo mensaje en la lista
- [ ] Badge de mensajes no leidos
- [ ] Filtro por estado: todas, nuevas, en curso, mias
- [ ] Indicador de quien esta atendiendo cada conversacion

#### US-CW-007: Detalle de conversacion con historial
**Como** vendedor, **quiero** ver el historial completo de una conversacion **para que** tenga contexto antes de responder.

**Criterios de Aceptacion:**
- [ ] Chat estilo WhatsApp con burbujas de mensaje
- [ ] Soporte de texto, imagenes, audio, video, documentos
- [ ] Scroll infinito hacia arriba para historial
- [ ] Info del contacto CRM visible en sidebar
- [ ] Notas internas entre agentes (no visibles para el cliente)

#### US-CW-008: Enviar y recibir mensajes
**Como** vendedor, **quiero** enviar mensajes desde el CRM **para que** pueda responder sin cambiar de app.

**Criterios de Aceptacion:**
- [ ] Enviar texto con formato (bold, italic, link)
- [ ] Adjuntar imagen, documento, audio
- [ ] Templates de WhatsApp Business para iniciar conversacion
- [ ] Indicador de enviado/entregado/leido
- [ ] Recepcion en tiempo real via webhook

#### US-CW-009: Estados de conversacion
**Como** vendedor, **quiero** marcar el estado de una conversacion **para que** sepa cuales requieren atencion.

**Criterios de Aceptacion:**
- [ ] Estados: NEW (automatico), IN_PROGRESS, WAITING (respuesta del cliente), RESOLVED
- [ ] Transicion manual por el agente
- [ ] Reapertura automatica si cliente envia nuevo mensaje post-RESOLVED
- [ ] SLA configurable: alerta si conversacion NEW > X minutos
- [ ] Conteo de conversaciones por estado en sidebar

#### US-CW-010: Respuestas rapidas y templates
**Como** vendedor, **quiero** usar respuestas rapidas **para que** pueda responder mas eficientemente.

**Criterios de Aceptacion:**
- [ ] Shortcuts con /comando (ej: /precio → "Nuestros precios son...")
- [ ] CRUD de respuestas rapidas por organizacion
- [ ] Templates con variables: {nombre}, {producto}, {precio}
- [ ] Busqueda de shortcuts por keyword
- [ ] Favoritos de respuestas mas usadas

#### US-CW-011: Vinculacion conversacion-contacto
**Como** sistema, **quiero** vincular automaticamente conversaciones con contactos CRM **para que** el agente tenga contexto.

**Criterios de Aceptacion:**
- [ ] Match automatico por numero de telefono
- [ ] Si no existe contacto: crear automaticamente con datos del perfil WhatsApp
- [ ] Sidebar muestra: info del contacto, deals activos, ultimo contacto
- [ ] Opcion de vincular manualmente si match automatico falla
- [ ] Historial de todas las conversaciones del contacto

### EP-CW-003: Pipeline de Ventas Kanban

#### US-CW-012: Modelo de Deal
**Como** desarrollador, **quiero** un modelo de Deal configurable **para que** represente cada oportunidad de venta.

**Criterios de Aceptacion:**
- [ ] Modelo: nombre, monto, contacto_id, pipeline_id, etapa, probabilidad, fecha_cierre
- [ ] Estados: OPEN, WON, LOST
- [ ] Etapas configurables por pipeline
- [ ] Historial de cambios de etapa con timestamp
- [ ] Campos personalizados por pipeline

#### US-CW-013: Vista Kanban con drag & drop
**Como** vendedor, **quiero** ver mis oportunidades en un tablero Kanban **para que** tenga visibilidad de mi pipeline.

**Criterios de Aceptacion:**
- [ ] Columnas = etapas del pipeline
- [ ] Tarjetas = deals con nombre, monto, contacto
- [ ] Drag & drop para mover entre etapas
- [ ] Valor total por columna
- [ ] Responsive: scroll horizontal en mobile

#### US-CW-014: Detalle del deal
**Como** vendedor, **quiero** ver todos los detalles de un deal **para que** pueda gestionarlo efectivamente.

**Criterios de Aceptacion:**
- [ ] Info del deal: monto, etapa, probabilidad, fecha cierre
- [ ] Contacto vinculado con link a perfil
- [ ] Conversacion WhatsApp del contacto integrada
- [ ] Timeline de actividades del deal
- [ ] Cotizaciones vinculadas al deal

#### US-CW-015: Pipelines multiples
**Como** admin, **quiero** crear diferentes pipelines **para que** cada equipo tenga su proceso de venta.

**Criterios de Aceptacion:**
- [ ] CRUD de pipelines con nombre y etapas
- [ ] Default pipeline creado con etapas estandar
- [ ] Cada pipeline con sus propias etapas
- [ ] Mover deal entre pipelines
- [ ] Metricas independientes por pipeline

#### US-CW-016: Automatizacion de pipeline por mensaje
**Como** sistema, **quiero** crear deals automaticamente cuando llega un mensaje **para que** no se pierda ninguna oportunidad.

**Criterios de Aceptacion:**
- [ ] Regla: nuevo mensaje de numero desconocido → crear contacto + deal
- [ ] Regla: IA detecta intencion "comprar" → mover deal a etapa X
- [ ] Regla configurable: si keyword en mensaje → accion
- [ ] Toggle on/off por regla
- [ ] Log de automatizaciones ejecutadas

### EP-CW-004: Automatizaciones y Clasificacion IA

#### US-CW-017: Clasificacion IA de intenciones
**Como** sistema, **quiero** clasificar automaticamente los mensajes entrantes **para que** se prioricen y enruten correctamente.

**Criterios de Aceptacion:**
- [ ] Intenciones: comprar, cotizar, soporte, queja, informacion, saludo, spam
- [ ] Confianza: high, medium, low
- [ ] Clasificacion en < 2 segundos
- [ ] Precision > 85% en intenciones principales
- [ ] Entrenamiento con datos de la organizacion

#### US-CW-018: Auto-tag de contactos
**Como** sistema, **quiero** etiquetar contactos automaticamente **para que** la segmentacion sea mas precisa sin esfuerzo manual.

**Criterios de Aceptacion:**
- [ ] Tag por producto mencionado en conversacion
- [ ] Tag por sentimiento (positivo, neutro, negativo)
- [ ] Tag por interes detectado por IA
- [ ] Tags automaticos diferenciados de manuales
- [ ] Configurable: activar/desactivar por tipo de auto-tag

#### US-CW-019: Auto-respuestas configurables
**Como** admin, **quiero** configurar respuestas automaticas **para que** los clientes reciban atencion inmediata.

**Criterios de Aceptacion:**
- [ ] Respuesta por intencion: cotizar → enviar catalogo
- [ ] Respuesta fuera de horario: "Te contactamos manana"
- [ ] Respuesta de bienvenida: primer mensaje de numero nuevo
- [ ] Delay configurable antes de auto-respuesta (parecer humano)
- [ ] No auto-responder si agente ya esta respondiendo

#### US-CW-020: Motor de reglas if-then
**Como** admin, **quiero** crear reglas de automatizacion **para que** el CRM trabaje por mi.

**Criterios de Aceptacion:**
- [ ] Builder visual de reglas: IF [condicion] THEN [accion]
- [ ] Condiciones: intencion, tag, etapa_deal, horario, agente_disponible, keyword
- [ ] Acciones: responder, asignar, mover_deal, crear_tarea, notificar, tag
- [ ] Prioridad de reglas (primera que match se ejecuta)
- [ ] Maximo 50 reglas por organizacion

#### US-CW-021: Asignacion automatica de conversaciones
**Como** sistema, **quiero** asignar conversaciones automaticamente **para que** los clientes sean atendidos rapido.

**Criterios de Aceptacion:**
- [ ] Regla: round-robin entre agentes disponibles
- [ ] Regla: por carga (menor numero de conversaciones activas)
- [ ] Regla: por skill (tag del contacto match con habilidad del agente)
- [ ] Regla: por horario (agente en turno)
- [ ] Fallback: si no hay agente disponible, asignar a cola general

### EP-CW-005: Cotizaciones y Cierre de Venta

#### US-CW-022: Crear cotizacion
**Como** vendedor, **quiero** crear una cotizacion desde el CRM **para que** pueda enviarla rapidamente por WhatsApp.

**Criterios de Aceptacion:**
- [ ] Items: nombre, descripcion, cantidad, precio unitario
- [ ] Calculo automatico: subtotal, IVA, total
- [ ] Descuentos por item o global
- [ ] Vigencia de la cotizacion (dias)
- [ ] Template personalizable con logo y datos de la empresa

#### US-CW-023: Enviar cotizacion por WhatsApp
**Como** vendedor, **quiero** enviar la cotizacion por WhatsApp **para que** el cliente la reciba inmediatamente.

**Criterios de Aceptacion:**
- [ ] Generar PDF de la cotizacion
- [ ] Enviar PDF como adjunto por WhatsApp
- [ ] Incluir link de pago SPEI en el mensaje
- [ ] Mensaje personalizable: "Hola {nombre}, te envio la cotizacion..."
- [ ] Registro en timeline del contacto

#### US-CW-024: Tracking de cotizacion
**Como** vendedor, **quiero** saber el estado de mis cotizaciones **para que** pueda dar seguimiento.

**Criterios de Aceptacion:**
- [ ] Estados: DRAFT, SENT, VIEWED, ACCEPTED, REJECTED, EXPIRED
- [ ] VIEWED: detectar cuando el cliente abre el PDF (tracking pixel)
- [ ] Notificacion al vendedor cuando cambia estado
- [ ] Lista de cotizaciones con filtros por estado
- [ ] Vencimiento automatico al pasar la fecha de vigencia

#### US-CW-025: Cierre de venta con pago SPEI
**Como** vendedor, **quiero** que el cliente pueda pagar la cotizacion via SPEI **para que** cierre la venta sin friccion.

**Criterios de Aceptacion:**
- [ ] Link de pago SPEI generado con monto de la cotizacion
- [ ] Deteccion automatica del pago via webhook SPEI
- [ ] Cotizacion cambia a ACCEPTED/PAID automaticamente
- [ ] Deal en pipeline se mueve a "Ganado" automaticamente
- [ ] Recibo enviado al cliente por WhatsApp

#### US-CW-026: Integracion con catalogo de productos
**Como** vendedor, **quiero** seleccionar productos del catalogo al cotizar **para que** no tenga que capturar precios manualmente.

**Criterios de Aceptacion:**
- [ ] Busqueda de productos desde el formulario de cotizacion
- [ ] Autocompletar precio, descripcion, SKU
- [ ] Productos de mf-inventory disponibles via API
- [ ] Productos custom (no del catalogo) tambien soportados
- [ ] Actualizacion de precios en tiempo real

### EP-CW-006: Multi-Agente y Asignacion

#### US-CW-027: Registro de agentes
**Como** admin, **quiero** registrar a mi equipo de ventas **para que** cada uno tenga su cuenta.

**Criterios de Aceptacion:**
- [ ] CRUD de agentes: nombre, email, rol, habilidades[], max_conversaciones
- [ ] Roles: admin, vendedor, soporte
- [ ] Invitacion por email
- [ ] Perfil de agente con foto y bio
- [ ] Horario de trabajo configurable

#### US-CW-028: Asignacion automatica
**Como** sistema, **quiero** asignar conversaciones nuevas automaticamente **para que** se atiendan rapido.

**Criterios de Aceptacion:**
- [ ] Algoritmos: round-robin, least-loaded, skill-based
- [ ] Configurable por organizacion
- [ ] Solo asignar a agentes con estado "disponible"
- [ ] Respetar max_conversaciones del agente
- [ ] Log de asignaciones con razon

#### US-CW-029: Transferencia entre agentes
**Como** vendedor, **quiero** transferir una conversacion a otro agente **para que** el mejor perfil atienda al cliente.

**Criterios de Aceptacion:**
- [ ] Boton "Transferir" con selector de agente destino
- [ ] Nota interna obligatoria al transferir
- [ ] Notificacion al agente destino
- [ ] Historial de transferencias en la conversacion
- [ ] Cliente no ve las notas internas

#### US-CW-030: Vista "Mis conversaciones"
**Como** vendedor, **quiero** ver solo mis conversaciones asignadas **para que** me enfoque en mis clientes.

**Criterios de Aceptacion:**
- [ ] Filtro default: solo mis conversaciones
- [ ] Toggle: ver todas vs solo mias
- [ ] Badge de "Mis pendientes" en sidebar
- [ ] Ordenar por prioridad (nuevas primero)
- [ ] Indicador de SLA (tiempo sin respuesta)

#### US-CW-031: Indicadores de carga por agente
**Como** admin, **quiero** ver la carga de trabajo de cada agente **para que** pueda balancear el equipo.

**Criterios de Aceptacion:**
- [ ] Conversaciones activas por agente
- [ ] Tiempo promedio de respuesta por agente
- [ ] Estado actual de cada agente (disponible, ocupado, ausente)
- [ ] Alerta si agente supera max_conversaciones
- [ ] Grafica de distribucion de carga

### EP-CW-007: Dashboard CRM y Analytics

#### US-CW-032: Dashboard principal
**Como** admin, **quiero** un dashboard con KPIs de ventas y WhatsApp **para que** tenga visibilidad del negocio.

**Criterios de Aceptacion:**
- [ ] KPIs: ventas cerradas ($), deals activos (#), conversion (%), response time
- [ ] Grafica de ventas por dia/semana/mes
- [ ] Pipeline value total y por etapa
- [ ] Top 5 deals por monto
- [ ] Actividad reciente (ultimas conversaciones, deals movidos)

#### US-CW-033: Metricas de WhatsApp
**Como** admin, **quiero** metricas de WhatsApp **para que** sepa como estamos atendiendo.

**Criterios de Aceptacion:**
- [ ] Tiempo promedio de primera respuesta
- [ ] Mensajes enviados/recibidos por dia
- [ ] Conversaciones nuevas vs resueltas
- [ ] Tasa de resolucion por agente
- [ ] Horario pico de mensajes

#### US-CW-034: Rendimiento por agente
**Como** admin, **quiero** metricas por agente **para que** pueda evaluar al equipo.

**Criterios de Aceptacion:**
- [ ] Ventas cerradas por agente ($)
- [ ] Deals ganados vs perdidos
- [ ] Tiempo promedio de respuesta
- [ ] Satisfaccion del cliente (si hay encuesta)
- [ ] Ranking de agentes

#### US-CW-035: Reporte de conversion del pipeline
**Como** admin, **quiero** ver tasas de conversion por etapa **para que** identifique donde se pierden las ventas.

**Criterios de Aceptacion:**
- [ ] Funnel: leads → cotizacion → negociacion → cierre
- [ ] Porcentaje de conversion entre cada etapa
- [ ] Tiempo promedio por etapa
- [ ] Deals perdidos por etapa con motivo
- [ ] Comparativo mensual

#### US-CW-036: Proyeccion de ventas
**Como** admin, **quiero** una proyeccion de ventas **para que** pueda planificar.

**Criterios de Aceptacion:**
- [ ] Proyeccion = sum(monto_deal × probabilidad_etapa) para deals activos
- [ ] Proyeccion por mes (proximo trimestre)
- [ ] Grafica de proyeccion vs real
- [ ] Desglose por agente
- [ ] Ajuste manual de probabilidad por deal

### EP-CW-008: mf-crm - Micro-Frontend PWA

#### US-CW-037: Scaffold mf-crm
**Como** desarrollador, **quiero** crear el micro-frontend mf-crm con PWA **para que** funcione como app instalable.

**Criterios de Aceptacion:**
- [ ] Angular standalone app con Native Federation
- [ ] Service Worker para PWA (caching, offline)
- [ ] Manifest.json con iconos y colores
- [ ] Registrado en mf-core como remote
- [ ] Build de produccion funcional

#### US-CW-038: Pantalla de inbox WhatsApp
**Como** vendedor, **quiero** un inbox mobile-first **para que** pueda responder desde el celular.

**Criterios de Aceptacion:**
- [ ] Lista de conversaciones con swipe actions
- [ ] Chat view con input de mensaje y adjuntos
- [ ] Push notification al recibir mensaje
- [ ] Funcionamiento fluido en 3G/4G
- [ ] Offline: ver conversaciones cacheadas

#### US-CW-039: Pantalla de pipeline Kanban
**Como** vendedor, **quiero** ver mi pipeline desde el celular **para que** revise mis oportunidades en cualquier momento.

**Criterios de Aceptacion:**
- [ ] Kanban con scroll horizontal (touch-friendly)
- [ ] Drag & drop funcional en tactil
- [ ] Detalle de deal con bottom sheet
- [ ] Crear deal rapido desde mobile
- [ ] Filtros por agente y etapa

#### US-CW-040: Pantalla de contactos
**Como** vendedor, **quiero** buscar y ver contactos desde mobile **para que** acceda a la info antes de una reunion.

**Criterios de Aceptacion:**
- [ ] Lista de contactos con busqueda
- [ ] Detalle con timeline de actividades
- [ ] Boton rapido: llamar, WhatsApp, email
- [ ] Tags visibles en tarjeta de contacto
- [ ] Crear contacto desde mobile

#### US-CW-041: Pantalla de cotizaciones
**Como** vendedor, **quiero** crear y enviar cotizaciones desde mobile **para que** pueda cerrar ventas en campo.

**Criterios de Aceptacion:**
- [ ] Lista de cotizaciones con estado
- [ ] Crear cotizacion rapida (seleccionar productos + enviar)
- [ ] Enviar por WhatsApp desde la app
- [ ] Preview de PDF antes de enviar
- [ ] Estado actualizado en tiempo real

#### US-CW-042: Pantalla de dashboard
**Como** admin, **quiero** ver el dashboard desde mobile **para que** monitoree las ventas.

**Criterios de Aceptacion:**
- [ ] KPIs principales visibles sin scroll
- [ ] Graficas adaptadas a mobile (vertical)
- [ ] Filtro por periodo rapido (hoy, semana, mes)
- [ ] Pull-to-refresh para actualizar
- [ ] Performance: carga < 3 segundos

---

## Timeline

```
Semana 1-3:   EP-CW-001 (Core data model) - Base
Semana 2-5:   EP-CW-002 (Inbox WhatsApp) - Critico
Semana 3-5:   EP-CW-003 (Pipeline Kanban)
Semana 4-14:  EP-CW-008 (Frontend) - En paralelo con backend
Semana 5-7:   EP-CW-004 (Automatizaciones IA) + EP-CW-006 (Multi-agente)
Semana 6-8:   EP-CW-005 (Cotizaciones)
Semana 8-10:  EP-CW-007 (Dashboard)
Semana 10-14: QA + ajustes + optimizacion PWA
```

**Equipo**: 2 devs full-stack (1 backend, 1 frontend)
**Costo estimado**: ~$400K MXN

---

## Dependencias entre Epicas

```
EP-CW-001 (Core Data Model) ← Base de todo
    |
    ├── EP-CW-002 (Inbox WhatsApp) → depende de EP-CW-001
    │       |
    │       ├── EP-CW-006 (Multi-agente) → depende de EP-CW-002
    │       |
    │       └── EP-CW-004 (Automatizaciones) → depende de EP-CW-002, EP-CW-003
    |
    ├── EP-CW-003 (Pipeline Kanban) → depende de EP-CW-001
    │       |
    │       └── EP-CW-005 (Cotizaciones) → depende de EP-CW-003
    |
    └── EP-CW-007 (Dashboard) → depende de EP-CW-001 a EP-CW-006
            |
            └── EP-CW-008 (Frontend PWA) → depende de todas las APIs
```

**Dependencias externas:**
- covacha-botia: WhatsApp Business API, motor IA
- covacha-payment: Motor SPEI para links de pago
- covacha-core: Multi-tenant, autenticacion
- mf-inventory: Catalogo de productos (opcional)

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|------------|
| WhatsApp Business API costosa | Media | Alto | Pricing incluye costo de WhatsApp, negociar con Meta |
| Competencia con CRMs establecidos | Alta | Medio | Diferenciarse con WhatsApp-first + precio accesible |
| Complejidad del inbox en tiempo real | Media | Alto | Usar SSE probado en covacha-botia, no WebSocket |
| Adopcion de PWA vs app nativa | Media | Medio | PWA funcional, evaluar app nativa si demanda lo justifica |
| Limites de WhatsApp Business API (24h window) | Alta | Alto | Disenar UX alrededor de templates aprobados para re-engagement |
