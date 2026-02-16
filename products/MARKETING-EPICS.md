# Marketing - Epicas Pendientes (EP-MK-006 a EP-MK-013)

**Fecha**: 2026-02-14
**Product Owner**: BaatDigital / Marketing
**Estado**: Planificacion
**Epicas completadas**: EP-MK-001 a EP-MK-005 (GitHub Issues #1-5, #8 en mf-marketing)
**User Stories**: US-MK-001 en adelante

---

## Tabla de Contenidos

1. [Contexto y Estado Actual](#contexto-y-estado-actual)
2. [Resumen de Epicas Completadas](#resumen-de-epicas-completadas)
3. [Mapa de Epicas Pendientes](#mapa-de-epicas-pendientes)
4. [Epicas Detalladas](#epicas-detalladas)
5. [User Stories Detalladas](#user-stories-detalladas)
6. [Roadmap](#roadmap)
7. [Grafo de Dependencias](#grafo-de-dependencias)
8. [Riesgos y Mitigaciones](#riesgos-y-mitigaciones)

---

## Contexto y Estado Actual

mf-marketing es el micro-frontend de agencia digital del ecosistema SuperPago/BaatDigital. Construido con Angular 21, Native Federation y arquitectura hexagonal.

### Repositorios Involucrados

| Repositorio | Funcion | Puerto Dev |
|-------------|---------|------------|
| `mf-marketing` | Micro-frontend Angular 21 | 4206 |
| `covacha-core` | Backend API (agencia, clientes, social) | 5001 |
| `mf-core` | Shell host | N/A |

### Estado del Codebase (Feb 2026)

| Metrica | Valor |
|---------|-------|
| Tests unitarios | 459+ passing |
| Framework test | Karma + Jasmine |
| E2E | Playwright configurado |
| Paginas | 22+ lazy-loaded |
| Componentes | 11+ reutilizables |
| Adapters | 24 archivos |
| Modelos dominio | 29 archivos, 429 exports |

### Features Produccion-Ready (~85%)

- Gestion de clientes completa (list, wizard 5 pasos, edit, dashboard, contactos, tareas, settings 7 tabs)
- Social media management (posts CRUD, calendario, cuentas FB/IG, analytics, workflow de aprobacion)
- Estrategias de marketing (builder wizard, detalle, dashboard KPIs, alertas, ciclos, timeline, radar chart)
- Landing pages publicas (renderizado por slug, SEO dinamico, formularios de contacto)
- Editor de promociones (wizard 5 pasos: identidad, diseno, landing, SEO, QR)
- Landing editor DnD FASE 1-2 (estructura + Angular CDK drag-and-drop)
- WhatsApp (templates, config form, floating button, demo landing)
- Media library hibrida (Google Drive OAuth + S3 + sync)
- Templates (WhatsApp, email, catalogo)

---

## Resumen de Epicas Completadas

| ID | Epica | GitHub Issue | Estado |
|----|-------|-------------|--------|
| EP-MK-001 | Refactor Client Cards - Info Enriquecida | #1 | Cerrado |
| EP-MK-002 | Edicion Inline de Clientes | #2 | Cerrado |
| EP-MK-003 | Paginacion Server-Side | #3 | Cerrado |
| EP-MK-004 | UX y Rendimiento Vista Clientes | #4 | Cerrado |
| EP-MK-005 | Landing Pages Publicas y Promociones | #8 | Cerrado |

---

## Mapa de Epicas Pendientes

| ID | Epica | Complejidad | Prioridad | Dependencias |
|----|-------|-------------|-----------|--------------|
| EP-MK-006 | Landing Editor Avanzado (FASE 3-5) | L | Alta | FASE 1-2 completadas |
| EP-MK-007 | Campaign Builder - Facebook Ads | XL | Alta | Social media adapters |
| EP-MK-008 | Brand Kit Completo | M | Media | Componentes parciales existen |
| EP-MK-009 | Dashboards Ejecutivo y Comparativo | M | Media | Datos de clientes/estrategias |
| EP-MK-010 | Team Visibility y Roles por Cliente | L | Alta | Modelo ClientTeamMember existe |
| EP-MK-011 | Task Manager Avanzado | L | Media | Tareas basicas implementadas |
| EP-MK-012 | Analytics BI de Estrategias | L | Baja | Estrategias implementadas |
| EP-MK-013 | AI Config Multi-Provider por Cliente | M | Baja | Settings AI parcialmente scaffolded |

**Totales pendientes:**
- 8 epicas
- 38 user stories (US-MK-001 a US-MK-038)
- Estimacion total: ~80-120 dev-days

---

## Epicas Detalladas

---

### EP-MK-006: Landing Editor Avanzado (FASE 3-5)

**Objetivo**: Completar el editor drag-and-drop de landing pages con edicion inline, previsualizacion, publicacion y persistencia backend.

**Estado actual**: FASE 1 (estructura base, servicios EditorState/History/AutoSave) y FASE 2 (DnD con Angular CDK) completadas. Faltan FASE 3, 4 y 5.

**Archivos clave existentes**:
- `src/app/domain/models/landing-editor.model.ts` (400+ lineas)
- `src/app/application/services/editor-state.service.ts` (400+ lineas)
- `src/app/application/services/history.service.ts` (100+ lineas)
- `src/app/application/services/auto-save.service.ts` (200+ lineas)
- `src/app/presentation/components/component-sidebar/` (DnD source)
- `src/app/presentation/components/editor-canvas/` (DnD target)

**User Stories**: US-MK-001 a US-MK-006

---

### EP-MK-007: Campaign Builder - Facebook Ads

**Objetivo**: Implementar un builder completo para campanas de Facebook/Instagram Ads con segmentacion de audiencia, presupuesto, creativos y tracking de rendimiento.

**Estado actual**: Scaffolding basico existe (componentes step: campaign, adset, ad, review) pero sin conexion a APIs de Meta ni logica funcional.

**Archivos clave existentes**:
- `src/app/presentation/pages/campaign-builder/` (componentes placeholder)
- `src/app/infrastructure/adapters/social-media.adapter.ts` (conexion FB/IG existente)

**User Stories**: US-MK-007 a US-MK-012

---

### EP-MK-008: Brand Kit Completo

**Objetivo**: Completar el sistema de brand kit que permite a cada cliente de la agencia tener su identidad visual centralizada (colores, logos, tipografias, iconos, imagenes).

**Estado actual**: Componentes UI existen (color-palette-editor, logo-manager, typography-manager, icon-library, image-library, email-template-editor). Adapter backend existe. Integracion parcial.

**Archivos clave existentes**:
- `src/app/presentation/pages/brand-kit/` (componentes parciales)
- `src/app/infrastructure/adapters/brand-kit.adapter.ts`

**User Stories**: US-MK-013 a US-MK-016

---

### EP-MK-009: Dashboards Ejecutivo y Comparativo

**Objetivo**: Crear dashboards de alto nivel que permitan a directores de agencia ver el rendimiento global de todos los clientes, comparar metricas entre clientes, y detectar tendencias.

**Estado actual**: Paginas placeholder con TODO comments. Sin logica funcional.

**User Stories**: US-MK-017 a US-MK-020

---

### EP-MK-010: Team Visibility y Roles por Cliente

**Objetivo**: Implementar reglas de visibilidad y acceso por equipo/usuario a nivel de cliente. Un miembro del equipo solo ve y actua sobre los clientes asignados, segun su rol (MANAGER, EDITOR, VIEWER).

**Estado actual**: Modelo `ClientTeamMember` definido con roles. Componentes `TeamAssignmentPanelComponent` y `TeamIndicatorComponent` referenciados en barrel export pero pendientes de integracion completa. Validaciones de transicion de estado definidas en `VALID_STATUS_TRANSITIONS`.

**Archivos clave existentes**:
- `src/app/domain/models/client.model.ts` (ClientTeamMember, TeamMemberRole)
- Barrel export en `src/app/presentation/components/index.ts`

**User Stories**: US-MK-021 a US-MK-024

---

### EP-MK-011: Task Manager Avanzado

**Objetivo**: Extender el gestor de tareas basico con dependencias entre tareas, vista Gantt, time tracking, y operaciones bulk. Convertirlo en una herramienta de project management ligera.

**Estado actual**: Tareas basicas implementadas (list, kanban, calendar, metrics views). Falta funcionalidad avanzada.

**Archivos clave existentes**:
- `src/app/presentation/pages/client-tasks/` (vistas basicas)

**User Stories**: US-MK-025 a US-MK-029

---

### EP-MK-012: Analytics BI de Estrategias

**Objetivo**: Dashboard de business intelligence para estrategias de marketing: comparativas cross-client, forecast de rendimiento, ROI por canal, y exportacion de reportes.

**Estado actual**: Estrategias implementadas con dashboard basico de KPIs. No hay BI avanzado ni cross-client.

**User Stories**: US-MK-030 a US-MK-033

---

### EP-MK-013: AI Config Multi-Provider por Cliente

**Objetivo**: Permitir configurar multiples proveedores de IA (OpenAI, Anthropic, Gemini) por cliente, con wizard de configuracion, quotas de uso, y facturacion por consumo.

**Estado actual**: Modelo `ClientAIConfig` definido. Tab "AI" en settings del cliente existe. Wizard de provider parcialmente scaffolded (`ai-provider-wizard.component.ts`).

**Archivos clave existentes**:
- `src/app/presentation/pages/client-settings/components/settings-ai.component.ts`
- `src/app/presentation/pages/client-settings/components/ai-provider-wizard.component.ts`

**User Stories**: US-MK-034 a US-MK-038

---

## User Stories Detalladas

---

### EP-MK-006: Landing Editor Avanzado

---

#### US-MK-001: Edicion de texto inline en secciones

**Como** creador de contenido
**Quiero** hacer clic en cualquier texto de una seccion del landing y editarlo directamente en el canvas
**Para** tener una experiencia WYSIWYG sin tener que usar el panel de propiedades

**Criterios de Aceptacion:**
- [ ] Click en texto activa edicion inline con cursor de escritura
- [ ] Soporte para texto plano y formateado (bold, italic, underline, links)
- [ ] Escape o click fuera cancela sin guardar
- [ ] Enter o blur guarda los cambios
- [ ] Undo/redo funciona con cambios de texto inline
- [ ] La edicion inline funciona en todos los viewports (mobile, tablet, desktop)

**Tareas Tecnicas:**
- [ ] Crear directiva `ContentEditableDirective` para textos editables
- [ ] Integrar con `EditorStateService.updateSection()`
- [ ] Agregar al historial de undo/redo
- [ ] Tests: 5+ unit tests

---

#### US-MK-002: Rich text toolbar contextual

**Como** creador de contenido
**Quiero** una toolbar flotante que aparezca al seleccionar texto con opciones de formato
**Para** aplicar estilos (bold, italic, color, tamano, alineacion) sin salir del canvas

**Criterios de Aceptacion:**
- [ ] Toolbar aparece al seleccionar texto (floating, posicion relativa a la seleccion)
- [ ] Opciones: Bold, Italic, Underline, Color de texto, Tamano, Alineacion, Link
- [ ] Toolbar desaparece al deseleccionar
- [ ] Formatos se aplican en tiempo real
- [ ] Toolbar no se sale de los limites del viewport

**Tareas Tecnicas:**
- [ ] Crear `RichTextToolbarComponent` standalone
- [ ] Usar `document.getSelection()` para detectar seleccion
- [ ] Aplicar formatos con `execCommand` o custom DOM manipulation
- [ ] Tests: 4+ unit tests

---

#### US-MK-003: Image uploader con crop integrado

**Como** creador de contenido
**Quiero** subir imagenes y recortarlas directamente en el editor
**Para** ajustar las imagenes al layout de la seccion sin herramientas externas

**Criterios de Aceptacion:**
- [ ] Boton de upload en cada seccion que acepta imagenes
- [ ] Preview del archivo antes de subir
- [ ] Crop tool con relaciones de aspecto predefinidas (16:9, 4:3, 1:1, libre)
- [ ] Compresion automatica para web (max 500KB)
- [ ] Upload a S3 via adapter existente
- [ ] Preview en canvas se actualiza inmediatamente

**Tareas Tecnicas:**
- [ ] Integrar libreria de crop (ej: `ngx-image-cropper` o similar)
- [ ] Conectar con `S3StorageAdapter` existente
- [ ] Optimizar imagenes antes de upload (resize + compress)
- [ ] Tests: 4+ unit tests

---

#### US-MK-004: Color picker para secciones

**Como** creador de contenido
**Quiero** un selector de color para fondos, textos y bordes de cada seccion
**Para** personalizar el aspecto visual de la landing sin escribir CSS

**Criterios de Aceptacion:**
- [ ] Color picker en panel de propiedades por seccion
- [ ] Soporte para colores hex, RGB y paleta predefinida del brand kit
- [ ] Preview en tiempo real del color seleccionado
- [ ] Colores recientes (ultimos 10 usados)
- [ ] Integracion con Brand Kit del cliente si existe

**Tareas Tecnicas:**
- [ ] Crear `ColorPickerComponent` standalone
- [ ] Integrar con panel de propiedades existente
- [ ] Persistir colores recientes en localStorage
- [ ] Tests: 3+ unit tests

---

#### US-MK-005: Preview modal responsive

**Como** creador de contenido
**Quiero** previsualizar la landing en un modal que simule diferentes dispositivos
**Para** verificar como se vera la landing en mobile, tablet y desktop antes de publicar

**Criterios de Aceptacion:**
- [ ] Boton "Preview" en toolbar del editor
- [ ] Modal fullscreen con iframe de preview
- [ ] Selector de dispositivo: Mobile (375px), Tablet (768px), Desktop (1200px)
- [ ] Transiciones suaves entre dispositivos
- [ ] Boton "Abrir en nueva pestana" para preview completo
- [ ] Preview refleja todos los cambios no guardados

**Tareas Tecnicas:**
- [ ] Crear `PreviewModalComponent` standalone
- [ ] Renderizar HTML de la landing en iframe seguro
- [ ] Sincronizar estado del editor con preview
- [ ] Tests: 3+ unit tests

---

#### US-MK-006: Publicacion y persistencia backend

**Como** creador de contenido
**Quiero** guardar y publicar la landing page al servidor
**Para** que los cambios se persistan y la landing sea accesible publicamente

**Criterios de Aceptacion:**
- [ ] Boton "Guardar borrador" persiste en backend sin publicar
- [ ] Boton "Publicar" guarda y hace la landing accesible via URL publica
- [ ] Validaciones previas a publicar (titulo requerido, al menos 1 seccion, SEO basico)
- [ ] Indicador de estado: Borrador / Publicado / Con cambios sin publicar
- [ ] AutoSave cada 30 segundos si hay cambios (ya scaffolded)
- [ ] Manejo de errores: retry automatico, notificacion al usuario

**Tareas Tecnicas:**
- [ ] Crear endpoint backend `PUT /api/v1/organization/{orgId}/landings/{id}` (o verificar existente)
- [ ] Crear endpoint `POST /api/v1/organization/{orgId}/landings/{id}/publish`
- [ ] Conectar `AutoSaveService` con adapter real (actualmente placeholder)
- [ ] Implementar validaciones de publicacion
- [ ] Tests: 5+ unit tests + 2 E2E tests

---

### EP-MK-007: Campaign Builder - Facebook Ads

---

#### US-MK-007: Wizard de creacion de campana

**Como** gestor de agencia
**Quiero** crear campanas de Facebook/Instagram Ads paso a paso
**Para** configurar objetivos, audiencia, presupuesto y creativos de forma guiada

**Criterios de Aceptacion:**
- [ ] Wizard de 4 pasos: Campana > Ad Set > Anuncios > Revision
- [ ] Paso 1 (Campana): nombre, objetivo (awareness, traffic, engagement, conversions, leads)
- [ ] Paso 2 (Ad Set): audiencia (edad, genero, ubicacion, intereses), presupuesto (diario/total), calendario
- [ ] Paso 3 (Anuncios): creativos (imagen/video/carousel), copy, CTA, URL destino
- [ ] Paso 4 (Revision): resumen completo con estimacion de alcance
- [ ] Validacion por paso antes de avanzar
- [ ] Guardar como borrador en cualquier paso

**Tareas Tecnicas:**
- [ ] Refactorizar componentes step existentes (campaign, adset, ad, review)
- [ ] Crear `CampaignBuilderService` para estado del wizard
- [ ] Crear `CampaignAdapter` para persistencia (crear/actualizar campana)
- [ ] Integrar con modelo de dominio (crear `campaign.model.ts`)
- [ ] Tests: 6+ unit tests por paso

---

#### US-MK-008: Conexion con Meta Marketing API

**Como** gestor de agencia
**Quiero** que las campanas creadas se publiquen directamente en Facebook Ads Manager
**Para** no tener que recrear la campana manualmente en la plataforma de Meta

**Criterios de Aceptacion:**
- [ ] Autenticacion OAuth con Facebook Marketing API (permisos: ads_management, ads_read)
- [ ] Mapeo de campana local a formato de Meta API (Campaign, Ad Set, Ad)
- [ ] Envio de campana a Meta con feedback de exito/error
- [ ] Sincronizacion de estado (campana activa, pausada, rechazada por Meta)
- [ ] Manejo de errores de validacion de Meta (policy violations, assets invalidos)

**Tareas Tecnicas:**
- [ ] Backend: Crear servicio Meta Marketing API en covacha-core
- [ ] Backend: Endpoint `POST /api/v1/organization/{orgId}/campaigns/{id}/publish-meta`
- [ ] Frontend: Integrar OAuth de Meta Ads (diferente al OAuth de paginas)
- [ ] Frontend: Mostrar errores de validacion de Meta en UI
- [ ] Tests: 4+ unit tests + mocks de Meta API

---

#### US-MK-009: Dashboard de rendimiento de campanas

**Como** gestor de agencia
**Quiero** ver metricas de rendimiento de mis campanas activas
**Para** tomar decisiones de optimizacion (aumentar presupuesto, pausar, ajustar audiencia)

**Criterios de Aceptacion:**
- [ ] Lista de campanas con status (activa, pausada, completada, borrador)
- [ ] Metricas por campana: impresiones, alcance, clicks, CTR, CPC, CPM, conversiones, gasto
- [ ] Graficas de tendencia (ultimos 7, 14, 30 dias)
- [ ] Comparativa entre campanas
- [ ] Filtros por cliente, periodo, objetivo
- [ ] Auto-refresh cada 5 minutos

**Tareas Tecnicas:**
- [ ] Backend: Endpoint `GET /api/v1/organization/{orgId}/campaigns/metrics`
- [ ] Backend: Sync periodico de metricas desde Meta Insights API
- [ ] Frontend: Crear `CampaignDashboardComponent` con graficas
- [ ] Tests: 4+ unit tests

---

#### US-MK-010: Gestion de audiencias guardadas

**Como** gestor de agencia
**Quiero** guardar configuraciones de audiencia para reutilizarlas en diferentes campanas
**Para** no tener que recrear la segmentacion cada vez

**Criterios de Aceptacion:**
- [ ] CRUD de audiencias: nombre, demografia, intereses, comportamientos, lookalikes
- [ ] Selector de audiencia guardada en paso 2 del wizard
- [ ] Estimacion de tamano de audiencia (via Meta API)
- [ ] Audiencias por cliente (cada cliente tiene sus propias audiencias)

**Tareas Tecnicas:**
- [ ] Backend: CRUD endpoints para audiencias
- [ ] Frontend: `AudienceManagerComponent`
- [ ] Integrar con Meta Audience API para estimacion de tamano
- [ ] Tests: 4+ unit tests

---

#### US-MK-011: Biblioteca de creativos publicitarios

**Como** gestor de agencia
**Quiero** tener una biblioteca de creativos (imagenes, videos, copies) organizados por cliente
**Para** reutilizar assets aprobados en diferentes campanas

**Criterios de Aceptacion:**
- [ ] Upload de imagenes y videos con preview
- [ ] Organizacion por carpetas/tags
- [ ] Validacion de specs de Meta (tamano, ratio, duracion de video)
- [ ] Reutilizar creativos de media library existente
- [ ] Preview de anuncio con creativo seleccionado (mockup de como se ve en feed)

**Tareas Tecnicas:**
- [ ] Integrar con `S3StorageAdapter` existente
- [ ] Crear `CreativeLibraryComponent`
- [ ] Validador de specs de Meta (image: 1080x1080, video: max 240min, carousel: 2-10 cards)
- [ ] Tests: 3+ unit tests

---

#### US-MK-012: A/B Testing de anuncios

**Como** gestor de agencia
**Quiero** crear variantes de un anuncio para probar cual funciona mejor
**Para** optimizar el rendimiento de las campanas con datos reales

**Criterios de Aceptacion:**
- [ ] Crear 2-5 variantes de un anuncio (diferente imagen, copy o CTA)
- [ ] Meta distribuye trafico automaticamente entre variantes
- [ ] Dashboard muestra metricas por variante
- [ ] Recomendacion automatica de "ganador" despues de N impresiones
- [ ] Opcion de pausar variantes perdedoras manualmente

**Tareas Tecnicas:**
- [ ] Backend: Modelo de variantes de anuncio
- [ ] Frontend: UI de creacion de variantes en paso 3 del wizard
- [ ] Frontend: Comparativa de metricas por variante
- [ ] Tests: 3+ unit tests

---

### EP-MK-008: Brand Kit Completo

---

#### US-MK-013: Paleta de colores del cliente

**Como** gestor de agencia
**Quiero** definir la paleta de colores oficial de cada cliente (primario, secundario, acento, neutros)
**Para** mantener consistencia visual en todo el contenido generado

**Criterios de Aceptacion:**
- [ ] Editor de paleta con color picker para cada slot (primario, secundario, acento, texto, fondo)
- [ ] Colores definidos en hex y RGB
- [ ] Preview de como se ven los colores aplicados (mini-preview de landing/post)
- [ ] Exportar paleta como CSS variables o JSON
- [ ] Historico de cambios de paleta

**Tareas Tecnicas:**
- [ ] Completar integracion de `ColorPaletteEditorComponent` con backend
- [ ] Backend: CRUD endpoint para brand kit del cliente
- [ ] Tests: 3+ unit tests

---

#### US-MK-014: Gestion de logos y assets visuales

**Como** gestor de agencia
**Quiero** subir y gestionar los logos del cliente (principal, horizontal, icono, monocromo)
**Para** tener los assets oficiales centralizados y accesibles para todo el equipo

**Criterios de Aceptacion:**
- [ ] Upload de logos en formatos PNG, SVG, JPG
- [ ] Variantes: logo principal, horizontal, solo icono, monocromo, sobre fondo oscuro
- [ ] Preview de cada logo sobre fondos claro y oscuro
- [ ] Download de assets en multiples formatos y tamanos
- [ ] Validacion de tamano minimo y calidad

**Tareas Tecnicas:**
- [ ] Completar integracion de `LogoManagerComponent` con S3
- [ ] Backend: Almacenamiento y versionado de logos
- [ ] Tests: 3+ unit tests

---

#### US-MK-015: Tipografia del cliente

**Como** gestor de agencia
**Quiero** definir las fuentes tipograficas oficiales del cliente (headings, body, accent)
**Para** aplicar la tipografia correcta en landings, posts y emails

**Criterios de Aceptacion:**
- [ ] Selector de fuentes con preview (Google Fonts + fonts custom uploaded)
- [ ] Slots: heading font, body font, accent font
- [ ] Preview de combinacion tipografica
- [ ] Upload de fuentes custom (woff2, ttf)
- [ ] Generacion de CSS `@font-face` para uso en landings

**Tareas Tecnicas:**
- [ ] Completar integracion de `TypographyManagerComponent`
- [ ] Integrar con Google Fonts API para busqueda
- [ ] Tests: 3+ unit tests

---

#### US-MK-016: Brand Kit aplicado automaticamente

**Como** gestor de agencia
**Quiero** que al crear una landing o post para un cliente se aplique automaticamente su brand kit
**Para** ahorrar tiempo y garantizar consistencia sin configuracion manual

**Criterios de Aceptacion:**
- [ ] Landing editor carga colores y tipografias del brand kit del cliente al abrir
- [ ] Templates de post pre-llenan colores del cliente
- [ ] Email templates usan paleta del cliente
- [ ] Override manual posible pero con advertencia "Fuera del brand kit"

**Tareas Tecnicas:**
- [ ] Crear `BrandKitService` que resuelve el brand kit activo por cliente
- [ ] Integrar con `EditorStateService` para landings
- [ ] Integrar con social media post creation
- [ ] Tests: 4+ unit tests

---

### EP-MK-009: Dashboards Ejecutivo y Comparativo

---

#### US-MK-017: Dashboard ejecutivo de la agencia

**Como** director de agencia
**Quiero** ver un resumen ejecutivo con KPIs globales de todos los clientes
**Para** tener visibilidad del estado general del negocio en un vistazo

**Criterios de Aceptacion:**
- [ ] KPIs globales: total clientes (por status), publicaciones del mes, estrategias activas, revenue total
- [ ] Graficas de tendencia mensual (ultimos 6 meses)
- [ ] Top 5 clientes por actividad/revenue
- [ ] Alertas: clientes inactivos, estrategias vencidas, tareas atrasadas
- [ ] Filtro por periodo (semana, mes, trimestre, ano)

**Tareas Tecnicas:**
- [ ] Backend: Endpoint de metricas agregadas `GET /api/v1/organization/{orgId}/agency/dashboard`
- [ ] Frontend: Reemplazar placeholder de `ExecutiveDashboardComponent`
- [ ] Graficas con ng2-charts o similar
- [ ] Tests: 4+ unit tests

---

#### US-MK-018: Dashboard comparativo entre clientes

**Como** director de agencia
**Quiero** comparar metricas de rendimiento entre 2-5 clientes seleccionados
**Para** identificar patrones de exito y clientes que necesitan atencion

**Criterios de Aceptacion:**
- [ ] Selector de clientes para comparar (2-5 max)
- [ ] Metricas comparables: publicaciones, engagement, alcance, tareas completadas, health score
- [ ] Grafica de radar/spider chart para comparativa visual
- [ ] Tabla comparativa con rankings
- [ ] Exportar comparativa como PDF o imagen

**Tareas Tecnicas:**
- [ ] Backend: Endpoint de metricas por grupo de clientes
- [ ] Frontend: Reemplazar placeholder de `ComparativeDashboardComponent`
- [ ] Integrar chart.js radar chart
- [ ] Tests: 3+ unit tests

---

#### US-MK-019: Reportes automaticos mensuales

**Como** director de agencia
**Quiero** generar reportes mensuales automaticos por cliente
**Para** enviar a los clientes un resumen de las actividades realizadas

**Criterios de Aceptacion:**
- [ ] Template de reporte con logo del cliente (brand kit)
- [ ] Secciones: resumen ejecutivo, publicaciones, engagement, estrategias, proximos pasos
- [ ] Generacion en PDF y HTML
- [ ] Envio automatico por email al contacto principal del cliente
- [ ] Historial de reportes generados

**Tareas Tecnicas:**
- [ ] Backend: Servicio de generacion de reportes (PDF via puppeteer o wkhtmltopdf)
- [ ] Backend: Cron job mensual para generacion automatica
- [ ] Frontend: Preview de reporte antes de enviar
- [ ] Tests: 3+ unit tests

---

#### US-MK-020: Widget de actividad reciente

**Como** gestor de agencia
**Quiero** ver un feed de actividad reciente de todos los clientes en tiempo real
**Para** estar al tanto de lo que esta pasando sin tener que entrar a cada cliente

**Criterios de Aceptacion:**
- [ ] Feed cronologico: publicaciones creadas, estrategias actualizadas, tareas completadas, clientes nuevos
- [ ] Filtro por tipo de actividad y por cliente
- [ ] Notificaciones de actividades importantes (aprobaciones pendientes, errores de publicacion)
- [ ] Auto-refresh cada 30 segundos
- [ ] Maximo 100 actividades visibles, paginacion scroll infinito

**Tareas Tecnicas:**
- [ ] Backend: Endpoint de actividad reciente con paginacion cursor-based
- [ ] Frontend: `ActivityFeedComponent` con virtual scroll
- [ ] Tests: 3+ unit tests

---

### EP-MK-010: Team Visibility y Roles por Cliente

---

#### US-MK-021: Asignacion de equipo a clientes

**Como** director de agencia
**Quiero** asignar miembros del equipo a clientes con roles especificos (Manager, Editor, Viewer)
**Para** controlar quien puede ver y modificar la informacion de cada cliente

**Criterios de Aceptacion:**
- [ ] Panel de asignacion de equipo en la pagina del cliente
- [ ] Roles: MANAGER (todo), EDITOR (crear/editar contenido), VIEWER (solo lectura)
- [ ] Buscar usuarios del equipo por nombre/email
- [ ] Un cliente puede tener multiples miembros con diferentes roles
- [ ] Indicador visual del equipo asignado en la tarjeta del cliente

**Tareas Tecnicas:**
- [ ] Completar `TeamAssignmentPanelComponent` (referenciado pero parcial)
- [ ] Completar `TeamIndicatorComponent` (referenciado pero parcial)
- [ ] Backend: CRUD de `client_team_members`
- [ ] Tests: 5+ unit tests

---

#### US-MK-022: Filtrado de clientes por visibilidad

**Como** miembro del equipo (no admin)
**Quiero** ver solo los clientes que me fueron asignados
**Para** enfocarme en mi trabajo sin distracciones

**Criterios de Aceptacion:**
- [ ] Lista de clientes filtrada automaticamente por asignacion del usuario logueado
- [ ] Admins ven todos los clientes
- [ ] Managers ven los clientes donde son manager + los que administran
- [ ] Editors y Viewers ven solo sus clientes asignados
- [ ] Indicador de "X de Y clientes visibles" en la UI

**Tareas Tecnicas:**
- [ ] Backend: Filtro `?team_member_id={userId}` en endpoint de clientes
- [ ] Frontend: Aplicar filtro automatico basado en permisos del usuario
- [ ] Tests: 4+ unit tests

---

#### US-MK-023: Permisos granulares por seccion del cliente

**Como** director de agencia
**Quiero** configurar que secciones del cliente puede ver/editar cada rol
**Para** tener control fino sobre acceso a informacion sensible (billing, settings, AI)

**Criterios de Aceptacion:**
- [ ] Matriz de permisos: seccion x rol (ej: EDITOR no ve billing, VIEWER no ve settings)
- [ ] Secciones controlables: dashboard, contactos, tareas, estrategias, posts, media, billing, settings, AI
- [ ] Permisos por defecto razonables (VIEWER = solo dashboard + posts, EDITOR = todo menos billing/settings)
- [ ] Override por cliente si es necesario
- [ ] Tabs/secciones no autorizadas se ocultan en la UI

**Tareas Tecnicas:**
- [ ] Crear `PermissionsService` con matriz de permisos
- [ ] Aplicar guards en rutas de cliente
- [ ] Ocultar tabs en settings basado en permisos
- [ ] Tests: 5+ unit tests

---

#### US-MK-024: Audit log de acciones por cliente

**Como** director de agencia
**Quiero** ver un historial de acciones realizadas en cada cliente (quien hizo que, cuando)
**Para** tener trazabilidad y accountability del equipo

**Criterios de Aceptacion:**
- [ ] Log de acciones: creacion, edicion, eliminacion, cambio de status, publicaciones, asignaciones
- [ ] Cada entrada: usuario, accion, timestamp, detalles del cambio
- [ ] Filtro por usuario, tipo de accion, rango de fechas
- [ ] Exportar log como CSV
- [ ] Retencion de 12 meses

**Tareas Tecnicas:**
- [ ] Backend: Tabla de audit log en DynamoDB
- [ ] Backend: Middleware que registra acciones automaticamente
- [ ] Frontend: `AuditLogComponent` con filtros y paginacion
- [ ] Tests: 3+ unit tests

---

### EP-MK-011: Task Manager Avanzado

---

#### US-MK-025: Dependencias entre tareas

**Como** gestor de agencia
**Quiero** definir dependencias entre tareas (tarea A bloquea a tarea B)
**Para** planificar el trabajo en secuencia correcta y detectar bloqueos

**Criterios de Aceptacion:**
- [ ] Al crear/editar tarea, selector de "Depende de" (busca otras tareas del cliente)
- [ ] Tarea bloqueada muestra indicador visual y no puede marcarse como completada
- [ ] Al completar tarea bloqueante, las dependientes se desbloquean automaticamente
- [ ] Deteccion de dependencias circulares (error al intentar crear)
- [ ] Vista de dependencias en grafo simple

**Tareas Tecnicas:**
- [ ] Backend: Campo `depends_on: string[]` en modelo de tarea
- [ ] Backend: Validacion de ciclos al crear dependencia
- [ ] Frontend: Selector de dependencias en form de tarea
- [ ] Frontend: Indicador visual de bloqueo en kanban/lista
- [ ] Tests: 5+ unit tests

---

#### US-MK-026: Vista Gantt de tareas

**Como** gestor de agencia
**Quiero** ver las tareas del cliente en un diagrama de Gantt
**Para** visualizar la planificacion temporal y dependencias de un vistazo

**Criterios de Aceptacion:**
- [ ] Diagrama Gantt con barras horizontales por tarea
- [ ] Eje X: tiempo (dias/semanas), Eje Y: tareas agrupadas por estado o asignado
- [ ] Flechas de dependencia entre tareas
- [ ] Drag para ajustar fechas de inicio/fin
- [ ] Zoom: dia, semana, mes
- [ ] Ruta critica resaltada (tareas que si se retrasan, retrasan el proyecto)

**Tareas Tecnicas:**
- [ ] Evaluar e integrar libreria Gantt (ej: `dhtmlx-gantt`, `frappe-gantt` o custom con Angular CDK)
- [ ] Mapear modelo de tareas a formato Gantt
- [ ] Implementar drag-to-resize para fechas
- [ ] Tests: 3+ unit tests

---

#### US-MK-027: Time tracking por tarea

**Como** miembro del equipo
**Quiero** registrar el tiempo dedicado a cada tarea
**Para** que la agencia pueda facturar por horas y medir eficiencia

**Criterios de Aceptacion:**
- [ ] Boton "Iniciar timer" en cada tarea
- [ ] Timer visible en la UI mientras corre
- [ ] Pausar y reanudar timer
- [ ] Agregar tiempo manual (para trabajo offline)
- [ ] Resumen de horas por tarea, por usuario, por cliente
- [ ] Solo un timer activo a la vez

**Tareas Tecnicas:**
- [ ] Backend: Modelo `TimeEntry` (task_id, user_id, start, end, duration, description)
- [ ] Backend: Endpoints CRUD de time entries
- [ ] Frontend: `TimeTrackerComponent` con timer en tiempo real
- [ ] Tests: 4+ unit tests

---

#### US-MK-028: Operaciones bulk de tareas

**Como** gestor de agencia
**Quiero** seleccionar multiples tareas y aplicar acciones en bulk
**Para** ahorrar tiempo en operaciones repetitivas

**Criterios de Aceptacion:**
- [ ] Checkbox de seleccion multiple en lista y kanban
- [ ] Acciones bulk: cambiar estado, asignar usuario, cambiar prioridad, eliminar
- [ ] Confirmacion antes de ejecutar (modal con resumen de acciones)
- [ ] Feedback de exito/error por tarea (si alguna falla, las demas continuan)
- [ ] Seleccionar todo / deseleccionar todo

**Tareas Tecnicas:**
- [ ] Backend: Endpoint bulk `PATCH /api/v1/organization/{orgId}/clients/{id}/tasks/bulk`
- [ ] Frontend: Modo de seleccion multiple con toolbar de acciones
- [ ] Tests: 4+ unit tests

---

#### US-MK-029: Notificaciones de tareas

**Como** miembro del equipo
**Quiero** recibir notificaciones cuando me asignan una tarea o cuando una tarea cambia de estado
**Para** estar al tanto de mi trabajo sin tener que revisar la plataforma constantemente

**Criterios de Aceptacion:**
- [ ] Notificacion in-app cuando me asignan una tarea
- [ ] Notificacion cuando una tarea que depende de mi se desbloquea
- [ ] Notificacion cuando un manager cambia prioridad de mi tarea
- [ ] Email digest diario con resumen de tareas pendientes
- [ ] Configuracion de preferencias de notificacion por usuario

**Tareas Tecnicas:**
- [ ] Integrar con sistema de notificaciones del Shell (BroadcastChannel)
- [ ] Backend: Eventos de tarea que disparan notificaciones
- [ ] Tests: 3+ unit tests

---

### EP-MK-012: Analytics BI de Estrategias

---

#### US-MK-030: Dashboard BI de estrategias

**Como** director de agencia
**Quiero** un dashboard de business intelligence con metricas avanzadas de todas las estrategias
**Para** entender el ROI global de los esfuerzos de marketing

**Criterios de Aceptacion:**
- [ ] KPIs globales: estrategias activas, completadas, ROI promedio, engagement rate promedio
- [ ] Graficas: rendimiento por canal (FB, IG, email, WA), tendencia mensual
- [ ] Desglose por cliente y por tipo de estrategia
- [ ] Filtros: periodo, cliente, canal, tipo de estrategia
- [ ] Top 5 estrategias por rendimiento

**Tareas Tecnicas:**
- [ ] Backend: Endpoint de metricas BI agregadas
- [ ] Frontend: `StrategyBIDashboardComponent` con graficas interactivas
- [ ] Tests: 4+ unit tests

---

#### US-MK-031: Comparativa cross-client de estrategias

**Como** director de agencia
**Quiero** comparar el rendimiento de estrategias similares entre diferentes clientes
**Para** identificar best practices y replicar exitos

**Criterios de Aceptacion:**
- [ ] Selector de estrategias para comparar (mismo tipo, diferentes clientes)
- [ ] Metricas comparativas: alcance, engagement, conversiones, ROI
- [ ] Grafica de radar para comparativa visual
- [ ] Insights automaticos (ej: "Cliente A tiene 3x mas engagement que Cliente B en la misma estrategia")
- [ ] Exportar como reporte

**Tareas Tecnicas:**
- [ ] Backend: Endpoint de comparativa con normalizacion de metricas
- [ ] Frontend: `StrategyComparisonComponent`
- [ ] Tests: 3+ unit tests

---

#### US-MK-032: Forecast de rendimiento

**Como** director de agencia
**Quiero** ver predicciones de rendimiento basadas en datos historicos
**Para** anticipar resultados y ajustar estrategias proactivamente

**Criterios de Aceptacion:**
- [ ] Proyeccion de metricas a 30, 60, 90 dias basada en tendencia actual
- [ ] Intervalo de confianza (optimista, esperado, pesimista)
- [ ] Alertas cuando la tendencia actual esta por debajo del target
- [ ] Visualizacion clara: datos reales vs proyeccion (linea solida vs punteada)

**Tareas Tecnicas:**
- [ ] Backend: Algoritmo de forecast (regresion lineal simple o media movil)
- [ ] Frontend: Grafica con linea de tendencia y area de confianza
- [ ] Tests: 3+ unit tests

---

#### US-MK-033: Exportacion de reportes BI

**Como** director de agencia
**Quiero** exportar los dashboards y comparativas como PDF, Excel o imagen
**Para** compartir con stakeholders que no tienen acceso a la plataforma

**Criterios de Aceptacion:**
- [ ] Exportar dashboard como PDF (con graficas renderizadas)
- [ ] Exportar datos tabulares como Excel/CSV
- [ ] Exportar graficas individuales como PNG
- [ ] Incluir logo de la agencia y fecha de generacion
- [ ] Programar envio automatico (semanal/mensual) por email

**Tareas Tecnicas:**
- [ ] Backend: Servicio de exportacion PDF (graficas server-side o screenshot)
- [ ] Frontend: Botones de exportacion en cada dashboard
- [ ] Integrar libreria de generacion Excel (ej: `xlsx`)
- [ ] Tests: 3+ unit tests

---

### EP-MK-013: AI Config Multi-Provider por Cliente

---

#### US-MK-034: Wizard de configuracion de proveedor AI

**Como** gestor de agencia
**Quiero** configurar un proveedor de IA (OpenAI, Anthropic, Gemini) para cada cliente
**Para** personalizar las respuestas del chatbot y generacion de contenido por cliente

**Criterios de Aceptacion:**
- [ ] Wizard de 3 pasos: Proveedor > API Key > Configuracion
- [ ] Proveedores soportados: OpenAI (GPT-4), Anthropic (Claude), Google (Gemini)
- [ ] Validacion de API key (test call) antes de guardar
- [ ] Configuracion por proveedor: modelo, temperatura, max tokens, system prompt
- [ ] Un cliente puede tener multiples proveedores (primario + fallback)

**Tareas Tecnicas:**
- [ ] Completar `AiProviderWizardComponent` (parcialmente scaffolded)
- [ ] Backend: CRUD de configuracion AI por cliente (cifrado de API keys)
- [ ] Backend: Endpoint de validacion de API key
- [ ] Tests: 4+ unit tests

---

#### US-MK-035: System prompt personalizado por cliente

**Como** gestor de agencia
**Quiero** definir el system prompt del AI para cada cliente
**Para** que el tono, estilo y conocimiento del AI sea especifico al negocio del cliente

**Criterios de Aceptacion:**
- [ ] Editor de system prompt con syntax highlighting
- [ ] Variables de contexto disponibles: `{client_name}`, `{industry}`, `{brand_voice}`, `{products}`
- [ ] Templates de system prompt por industria (restaurante, e-commerce, servicios, etc.)
- [ ] Preview de respuesta del AI con el prompt configurado
- [ ] Versionado de prompts (historial de cambios)

**Tareas Tecnicas:**
- [ ] Frontend: Editor de prompt con autocompletado de variables
- [ ] Backend: Almacenamiento de prompts con versionado
- [ ] Backend: Endpoint de test/preview que ejecuta el prompt
- [ ] Tests: 3+ unit tests

---

#### US-MK-036: Quotas de uso AI por cliente

**Como** director de agencia
**Quiero** configurar limites de uso de AI por cliente (tokens, requests, presupuesto)
**Para** controlar costos y evitar sorpresas en la facturacion

**Criterios de Aceptacion:**
- [ ] Configurar quota mensual por cliente: tokens o dolares
- [ ] Dashboard de consumo actual vs quota
- [ ] Alertas automaticas al 80% y 100% del limite
- [ ] Accion al llegar al limite: bloquear, reducir modelo, notificar admin
- [ ] Historial de consumo mensual

**Tareas Tecnicas:**
- [ ] Backend: Modelo `AIUsageQuota` y `AIUsageEntry`
- [ ] Backend: Middleware que valida quota antes de cada llamada AI
- [ ] Frontend: Widgets de consumo en settings del cliente
- [ ] Tests: 4+ unit tests

---

#### US-MK-037: Generacion de contenido asistida por AI

**Como** creador de contenido
**Quiero** generar borradores de posts y copies usando la IA configurada del cliente
**Para** acelerar la creacion de contenido manteniendo el tono del cliente

**Criterios de Aceptacion:**
- [ ] Boton "Generar con AI" en creacion de posts
- [ ] Inputs: tipo de post, tema/producto, tono deseado, longitud
- [ ] AI genera copy + sugerencias de hashtags
- [ ] El copy generado es editable antes de guardar
- [ ] Usa el system prompt y proveedor del cliente automaticamente

**Tareas Tecnicas:**
- [ ] Frontend: `AIContentGeneratorComponent` integrado en creacion de post
- [ ] Backend: Endpoint que orquesta la llamada al proveedor del cliente
- [ ] Streaming de respuesta para UX fluida
- [ ] Tests: 3+ unit tests

---

#### US-MK-038: Facturacion de consumo AI

**Como** director de agencia
**Quiero** ver el costo de AI por cliente para incluirlo en la facturacion
**Para** trasladar el costo de AI al cliente de forma transparente

**Criterios de Aceptacion:**
- [ ] Reporte de consumo AI por cliente por periodo
- [ ] Desglose por proveedor, modelo, tipo de uso (content generation, chatbot, etc.)
- [ ] Costo calculado basado en pricing del proveedor
- [ ] Exportar como CSV para sistemas de facturacion
- [ ] Markup configurable (ej: costo + 30% de margen)

**Tareas Tecnicas:**
- [ ] Backend: Calcular costos basado en tokens consumidos y pricing por modelo
- [ ] Frontend: `AIBillingReportComponent`
- [ ] Tests: 3+ unit tests

---

## Roadmap

### Fase 1 - Alta Prioridad (Sprint 1-3)

```
EP-MK-006: Landing Editor Avanzado (US-MK-001 a US-MK-006)
  - FASE 3: Inline editing, rich text, image crop, color picker
  - FASE 4: Preview modal, validaciones
  - FASE 5: Persistencia backend, publish flow
```
**Razon**: Feature mas avanzado con scaffolding ya hecho. Alto ROI por completar.

### Fase 2 - Alta Prioridad (Sprint 2-4)

```
EP-MK-010: Team Visibility y Roles (US-MK-021 a US-MK-024)
  - Modelo ya definido, componentes referenciados
  - Critico para agencias con equipos de 3+ personas
```
**Razon**: Seguridad y control de acceso. Bloqueante para escalar la agencia.

### Fase 3 - Media Prioridad (Sprint 3-5)

```
EP-MK-009: Dashboards Ejecutivo/Comparativo (US-MK-017 a US-MK-020)
EP-MK-008: Brand Kit Completo (US-MK-013 a US-MK-016)
```
**Razon**: Visibilidad operativa y consistencia visual. Valor inmediato para directores.

### Fase 4 - Media Prioridad (Sprint 5-8)

```
EP-MK-011: Task Manager Avanzado (US-MK-025 a US-MK-029)
EP-MK-007: Campaign Builder Facebook Ads (US-MK-007 a US-MK-012)
```
**Razon**: Features de productividad y automatizacion. Dependen de Meta Marketing API.

### Fase 5 - Baja Prioridad (Sprint 8-10)

```
EP-MK-012: Analytics BI (US-MK-030 a US-MK-033)
EP-MK-013: AI Config Multi-Provider (US-MK-034 a US-MK-038)
```
**Razon**: Features avanzados que requieren datos historicos y maduracion del producto.

---

## Grafo de Dependencias

```
EP-MK-006 (Landing Editor)
  └── Completado: FASE 1-2
  └── No depende de otras epicas pendientes

EP-MK-007 (Campaign Builder)
  └── Depende de: Social media adapters (completado)
  └── Depende de: Meta Marketing API (nuevo, backend)

EP-MK-008 (Brand Kit)
  └── Depende de: S3 adapter (completado)
  └── Se integra con: EP-MK-006 (landing editor usa brand kit)

EP-MK-009 (Dashboards)
  └── Depende de: Datos de clientes/estrategias (completado)
  └── Se beneficia de: EP-MK-012 (analytics BI)

EP-MK-010 (Team Visibility)
  └── Depende de: Modelo ClientTeamMember (completado)
  └── Bloquea: Escalamiento de agencia

EP-MK-011 (Task Manager Avanzado)
  └── Depende de: Tareas basicas (completado)
  └── Se beneficia de: EP-MK-010 (asignacion de equipo)

EP-MK-012 (Analytics BI)
  └── Depende de: Estrategias (completado)
  └── Se beneficia de: EP-MK-009 (dashboards base)

EP-MK-013 (AI Config)
  └── Depende de: Settings AI (parcialmente scaffolded)
  └── Se integra con: EP-MK-007 (campaign builder puede usar AI para copies)
```

---

## Riesgos y Mitigaciones

| Riesgo | Impacto | Probabilidad | Mitigacion |
|--------|---------|--------------|------------|
| Meta Marketing API tiene rate limits estrictos | Campaign builder lento | Alta | Cache de metricas, sync batch nocturno |
| API keys de AI expuestas en frontend | Seguridad critica | Media | Cifrado en backend, nunca enviar key al frontend |
| Landing editor se vuelve demasiado complejo | >1000 lineas, mantenibilidad | Alta | Mantener patron de componentes pequeños, split agresivo |
| Gantt chart library pesada (bundle size) | Performance de MF | Media | Lazy load solo en ruta de Gantt, tree shaking |
| Forecast con datos insuficientes da resultados erroneos | Usuarios confian en datos malos | Media | Minimo 3 meses de datos para habilitar forecast, disclaimer visible |
| DynamoDB scan para analytics BI es lento | Dashboard ejecutivo lento | Alta | Pre-computar metricas agregadas en cron, GSI optimizados |

---

## Definition of Done (Global)

Para considerar una user story como DONE:

- [ ] Codigo implementado siguiendo arquitectura hexagonal
- [ ] Unit tests con coverage >= 80% (Karma + Jasmine)
- [ ] E2E test para flujo principal (Playwright)
- [ ] Build de produccion exitoso (`yarn build:prod`)
- [ ] Ningun archivo > 1000 lineas
- [ ] Ninguna funcion > 50 lineas
- [ ] Code review aprobado
- [ ] Documentacion actualizada si aplica
- [ ] PR creado automaticamente via GitHub Actions (coverage >= 98%)
