# Website - Epicas de Landing Pages y Portales Publicos (EP-WB-001 a EP-WB-006)

**Fecha**: 2026-02-16
**Product Owner**: SuperPago / BaatDigital / AlertaTribunal
**Estado**: Planificacion
**Prefijo Epicas**: EP-WB
**Prefijo User Stories**: US-WB
**Prioridad del Producto**: P3

---

## Tabla de Contenidos

1. [Contexto y Motivacion](#contexto-y-motivacion)
2. [Roles Involucrados](#roles-involucrados)
3. [Arquitectura de Websites](#arquitectura-de-websites)
4. [Mapa de Epicas](#mapa-de-epicas)
5. [Epicas Detalladas](#epicas-detalladas)
6. [User Stories Detalladas](#user-stories-detalladas)
7. [Roadmap](#roadmap)
8. [Grafo de Dependencias](#grafo-de-dependencias)
9. [Riesgos y Mitigaciones](#riesgos-y-mitigaciones)
10. [Definition of Done Global](#definition-of-done-global)

---

## Contexto y Motivacion

El ecosistema BAAT Digital / SuperPago opera multiples marcas bajo un modelo multi-tenant. Cada marca necesita una presencia web publica profesional que comunique su propuesta de valor, capture leads, posicione en buscadores y genere confianza. Actualmente existe una landing page basica de BaatDigital parcialmente implementada, routing por dominio (tenant detection) y un layout publico separado del admin. Falta completar las landing pages de SuperPago y AlertaTribunal, optimizar SEO, implementar un sistema de blog, captura de leads, documentacion publica de APIs y tracking de conversion.

### Repositorios Involucrados

| Repositorio | Funcion | Puerto Dev |
|-------------|---------|------------|
| `mf-core` | Shell principal Angular 21 - rutas publicas en `src/app/portals/website/` | N/A |
| `covacha-core` | Backend API (paginas, blog, leads, contacto) | 5001 |
| `covacha-libs` | Modelos compartidos, utilidades | N/A |
| `covacha-crm` | Integracion CRM para leads | 5008 |

### Dominios del Ecosistema

| Dominio | Tenant | Enfoque de Landing |
|---------|--------|--------------------|
| `superpago.com.mx` | SuperPago | Pagos empresariales, SPEI, BillPay, cobros |
| `baatdigital.com.mx` | BaatDigital | Agencia digital, marketing, social media |
| `alertatribunal.com` | AlertaTribunal | Alertas judiciales, monitoreo de expedientes |

### Estado Actual (Feb 2026)

| Metrica | Valor |
|---------|-------|
| Landing BaatDigital | Parcialmente implementada |
| Landing SuperPago | No implementada |
| Landing AlertaTribunal | No implementada |
| Tenant detection | Funcional (routing por dominio) |
| Layout publico | Separado del admin |
| SEO | Basico / sin optimizar |
| Blog | No existe |
| Lead capture | No existe |
| Documentacion publica | No existe |

---

## Roles Involucrados

### R1: Visitante

Persona anonima que llega al sitio web a traves de busqueda, redes sociales, link directo o publicidad.

**Necesidades:**
- Entender la propuesta de valor del producto rapidamente
- Encontrar informacion de precios y funcionalidades
- Contactar al equipo de ventas
- Leer contenido relevante (blog, guias)
- Registrarse o solicitar demo

### R2: Content Manager

Persona interna del equipo que gestiona el contenido publico de los sitios web.

**Responsabilidades:**
- Crear y editar articulos del blog
- Actualizar contenido de landing pages
- Gestionar formularios de contacto
- Publicar y despublicar contenido
- Revisar metricas de engagement

### R3: Administrador Web

Persona con acceso tecnico que configura la infraestructura web, SEO, analytics y portales de documentacion.

**Responsabilidades:**
- Configurar meta tags y SEO por pagina
- Gestionar sitemap y robots.txt
- Configurar analytics y tracking de conversion
- Administrar portal de documentacion
- Configurar A/B tests

### R4: Sistema

Procesos automatizados que operan sin intervencion humana.

**Responsabilidades:**
- Pre-renderizar paginas para SEO
- Generar sitemap.xml automaticamente
- Enviar auto-respuestas a formularios de contacto
- Sincronizar leads con CRM
- Invalidar cache de CDN al publicar cambios
- Registrar eventos de analytics

---

## Arquitectura de Websites

```
                    VISITANTES
                        |
                        v
              +-------------------+
              |   CloudFront CDN  |
              | (S3 static + SSR) |
              +-------------------+
                        |
           +------------+------------+
           |            |            |
           v            v            v
  superpago.com.mx  baatdigital.com.mx  alertatribunal.com
           |            |            |
           +------------+------------+
                        |
                        v
              +-------------------+
              | mf-core (Angular) |
              |  Tenant Detector  |
              +-------------------+
                        |
           +------------+------------+
           |                         |
           v                         v
  +------------------+     +------------------+
  | Portal Publico   |     | Portal Admin     |
  | (layout website) |     | (layout admin)   |
  +------------------+     +------------------+
           |
           +------+------+------+------+
           |      |      |      |      |
           v      v      v      v      v
        Landing  Blog  Docs  Contact  Pricing
        Pages          Portal  Forms
           |      |      |      |
           +------+------+------+
                        |
                        v
              +-------------------+
              | API Gateway + WAF |
              +-------------------+
                        |
           +------------+------------+
           |            |            |
           v            v            v
  +-------------+  +-----------+  +-----------+
  | covacha-core|  |covacha-crm|  |covacha-   |
  | /website/   |  | /leads/   |  |libs       |
  | /blog/      |  |           |  |(modelos)  |
  +-------------+  +-----------+  +-----------+
           |            |
           v            v
  +-------------------+
  |    DynamoDB       |
  | PAGE# BLOG# LEAD#|
  | FORM# DOC# ANLY# |
  +-------------------+
```

### Flujo de Rendering Multi-Tenant

```
1. Visitante accede a superpago.com.mx
2. CloudFront sirve index.html (cache no-cache)
3. Angular carga → TenantDetectorService lee hostname
4. Resuelve tenant: "superpago"
5. Router carga rutas publicas: /portals/website/superpago/
6. Componentes cargan contenido via API: GET /api/v1/website/pages?tenant=superpago
7. Meta tags dinamicos se inyectan (SSR/prerender)
8. Visitante ve landing de SuperPago con branding correcto
```

### Modelo de Datos DynamoDB

```
Tabla: covacha-main (single-table)

# Paginas estaticas
PK: PAGE#{tenant}#{slug}        SK: METADATA
PK: PAGE#{tenant}#{slug}        SK: CONTENT#{version}
PK: PAGE#{tenant}#{slug}        SK: SEO

# Blog
PK: BLOG#{tenant}               SK: POST#{post_id}
PK: BLOG#{tenant}               SK: CATEGORY#{category_id}
PK: BLOG#{tenant}               SK: TAG#{tag_name}

# Leads
PK: LEAD#{tenant}               SK: ENTRY#{timestamp}#{lead_id}
PK: LEAD#{tenant}               SK: FORM#{form_id}

# Documentacion
PK: DOC#{tenant}                 SK: PAGE#{slug}#{version}
PK: DOC#{tenant}                 SK: SEARCH#{term}

# Analytics eventos
PK: ANLY#{tenant}#{date}         SK: EVENT#{timestamp}#{event_id}

# GSIs
GSI1: GSI1PK=BLOG#{tenant}#STATUS#{status}  GSI1SK=PUBLISHED_AT
GSI2: GSI2PK=LEAD#{tenant}#SOURCE#{source}  GSI2SK=CREATED_AT
GSI3: GSI3PK=PAGE#{tenant}#TYPE#{type}      GSI3SK=UPDATED_AT
```

---

## Mapa de Epicas

| ID | Epica | Complejidad | Prioridad | Dependencias |
|----|-------|-------------|-----------|--------------|
| EP-WB-001 | Landing Pages Multi-Tenant | XL | Alta | Tenant detection existente |
| EP-WB-002 | SEO y Performance | L | Alta | EP-WB-001 |
| EP-WB-003 | Sistema de Blog / Contenido | L | Media | EP-WB-001, EP-WB-002 |
| EP-WB-004 | Formularios de Contacto y Lead Capture | M | Alta | EP-WB-001 |
| EP-WB-005 | Portal de Documentacion (mf-docs) | L | Media | EP-WB-001, EP-WB-002 |
| EP-WB-006 | Analytics y Conversion Tracking | M | Media | EP-WB-001 |

**Totales:**
- 6 epicas
- 36 user stories (US-WB-001 a US-WB-036)
- Estimacion total: ~60-90 dev-days

---

## Epicas Detalladas

---

### EP-WB-001: Landing Pages Multi-Tenant

**Descripcion:**
Landing page diferenciada por dominio/tenant. SuperPago enfocada en pagos empresariales, SPEI, BillPay. BaatDigital enfocada en agencia digital, marketing, social media. AlertaTribunal enfocada en alertas judiciales, monitoreo de expedientes. Cada una con branding propio, hero section, features, pricing, testimonios, CTA y footer. El sistema detecta el tenant por hostname y carga el contenido y branding correspondiente desde backend.

**User Stories:** US-WB-001 a US-WB-008

**Criterios de Aceptacion de la Epica:**
- [ ] Cada dominio muestra su landing page con branding correcto
- [ ] Secciones estandar: hero, features, pricing, testimonios, CTA, footer
- [ ] Contenido configurable por tenant desde backend (no hardcodeado)
- [ ] Responsive design: mobile (375px), tablet (768px), desktop (1200px+)
- [ ] Navegacion publica (sin autenticacion)
- [ ] CTA de registro/login redirige al flujo de autenticacion (mf-auth)
- [ ] Carga inicial < 2 segundos (LCP)
- [ ] Cobertura de tests >= 80%

**Dependencias:** Tenant detection existente en mf-core

**Complejidad:** XL (3 tenants, multiples secciones, backend API)

**Repositorios:** `mf-core` (src/app/portals/website/), `covacha-core`

---

### EP-WB-002: SEO y Performance

**Descripcion:**
Optimizacion completa de SEO y performance para posicionamiento en buscadores. Incluye pre-rendering o SSR para que los crawlers indexen correctamente, meta tags dinamicos por pagina y tenant, Open Graph y Twitter Cards para compartir en redes, Schema.org structured data para rich snippets, sitemap.xml automatico, robots.txt por tenant, y optimizacion de Core Web Vitals (LCP, FID, CLS).

**User Stories:** US-WB-009 a US-WB-014

**Criterios de Aceptacion de la Epica:**
- [ ] Paginas pre-renderizadas accesibles para Google, Bing, Facebook, Twitter
- [ ] Meta tags (title, description, canonical) configurables por pagina
- [ ] Open Graph y Twitter Cards funcionales (preview al compartir URL)
- [ ] Schema.org structured data para Organization, Product, FAQ, Article
- [ ] sitemap.xml generado automaticamente y actualizado al publicar contenido
- [ ] robots.txt configurado por tenant
- [ ] Core Web Vitals en verde (LCP < 2.5s, FID < 100ms, CLS < 0.1)
- [ ] Lazy loading de imagenes y assets pesados
- [ ] CDN cache configurado correctamente (assets hasheados: 1 ano, HTML: no-cache)

**Dependencias:** EP-WB-001 (necesita las landing pages base)

**Complejidad:** L (SSR/pre-rendering, configuracion de CDN, structured data)

**Repositorios:** `mf-core`, `covacha-core`

---

### EP-WB-003: Sistema de Blog / Contenido

**Descripcion:**
Blog multi-tenant con CMS basico para publicar articulos. Cada tenant tiene su propio blog con categorias y tags. Los articulos soportan Markdown, tienen SEO optimizado individualmente, muestran autor y fecha, se pueden compartir en redes, y generan RSS feed. El Content Manager puede crear, editar, previsualizar y publicar articulos desde el panel de administracion.

**User Stories:** US-WB-015 a US-WB-020

**Criterios de Aceptacion de la Epica:**
- [ ] CRUD completo de articulos de blog por tenant
- [ ] Editor Markdown con preview en tiempo real
- [ ] Categorias y tags por tenant
- [ ] SEO individual por articulo (title, description, canonical, OG tags)
- [ ] Autor, fecha de publicacion, tiempo estimado de lectura
- [ ] Compartir en redes sociales (FB, Twitter, LinkedIn, WhatsApp)
- [ ] RSS feed por tenant (XML valido)
- [ ] Listado publico con paginacion y filtro por categoria/tag
- [ ] Busqueda full-text de articulos
- [ ] Estados: borrador, en revision, publicado, archivado

**Dependencias:** EP-WB-001 (layout publico), EP-WB-002 (SEO por articulo)

**Complejidad:** L (CMS backend, editor Markdown, RSS, busqueda)

**Repositorios:** `mf-core` (portals/website/blog/), `covacha-core`

---

### EP-WB-004: Formularios de Contacto y Lead Capture

**Descripcion:**
Sistema de formularios de contacto y captura de leads por tenant. Cada tenant tiene formularios configurables (contacto, solicitar demo, cotizacion). Los leads se sincronizan automaticamente con el CRM (covacha-crm). Se envian auto-respuestas por email al visitante y notificaciones al equipo de ventas. Incluye CAPTCHA para evitar spam y lead scoring basico.

**User Stories:** US-WB-021 a US-WB-026

**Criterios de Aceptacion de la Epica:**
- [ ] Formulario de contacto funcional por tenant (nombre, email, telefono, mensaje)
- [ ] Formulario de solicitud de demo (datos adicionales: empresa, tamano, industria)
- [ ] CAPTCHA (reCAPTCHA v3 o hCaptcha) en todos los formularios
- [ ] Auto-respuesta por email al visitante (template por tenant)
- [ ] Notificacion al equipo de ventas (email + notificacion in-app)
- [ ] Sincronizacion automatica de leads con covacha-crm
- [ ] Lead scoring basico (por fuente, tamano de empresa, urgencia)
- [ ] Dashboard de leads en panel admin con filtros
- [ ] Rate limiting para prevenir abuso (max 5 envios por IP por hora)

**Dependencias:** EP-WB-001 (formularios embebidos en landing), covacha-crm (integracion CRM)

**Complejidad:** M (formularios, email, integracion CRM, anti-spam)

**Repositorios:** `mf-core`, `covacha-core`, `covacha-crm`

---

### EP-WB-005: Portal de Documentacion (mf-docs)

**Descripcion:**
Portal de documentacion publica para APIs, guias de integracion, tutoriales y changelog. Orientado a desarrolladores que integran con SuperPago (SPEI, pagos, webhooks). Incluye busqueda full-text, versionado de documentacion, status page del sistema, y ejemplos de codigo en multiples lenguajes. El portal vive como seccion publica dentro de mf-core o como MF independiente (mf-docs).

**User Stories:** US-WB-027 a US-WB-032

**Criterios de Aceptacion de la Epica:**
- [ ] Portal accesible en docs.superpago.com.mx o superpago.com.mx/docs
- [ ] Documentacion de APIs REST con endpoints, parametros, respuestas y ejemplos
- [ ] Guias de integracion paso a paso (SPEI, BillPay, webhooks)
- [ ] Tutoriales con ejemplos de codigo (Python, Node.js, PHP, cURL)
- [ ] Changelog publico con historial de versiones
- [ ] Status page con estado de cada servicio (API, SPEI, webhooks)
- [ ] Busqueda full-text en toda la documentacion
- [ ] Versionado de docs (v1, v2) con selector de version
- [ ] Navegacion lateral con tabla de contenidos
- [ ] Feedback por pagina ("Fue util esta pagina? Si/No")

**Dependencias:** EP-WB-001 (layout publico), EP-WB-002 (SEO para indexacion de docs)

**Complejidad:** L (renderizado Markdown, busqueda full-text, versionado, status page)

**Repositorios:** `mf-core` (portals/website/docs/) o `mf-docs`, `covacha-core`

---

### EP-WB-006: Analytics y Conversion Tracking

**Descripcion:**
Implementacion de analytics y tracking de conversion para medir el rendimiento de los sitios web. Incluye integracion con Google Analytics 4, eventos personalizados, funnel de conversion (visit > signup > activate), integracion con heatmaps (Hotjar o similar), A/B testing de landing pages, y UTM tracking para campanas de marketing.

**User Stories:** US-WB-033 a US-WB-036

**Criterios de Aceptacion de la Epica:**
- [ ] Google Analytics 4 configurado por tenant
- [ ] Eventos personalizados: page_view, cta_click, form_submit, signup_start, signup_complete
- [ ] Funnel de conversion visible en GA4 y en dashboard interno
- [ ] Integracion con Hotjar o similar para heatmaps y session recordings
- [ ] A/B testing de variantes de landing page (hero, CTA, pricing)
- [ ] UTM tracking completo (source, medium, campaign, term, content)
- [ ] Dashboard interno basico con metricas clave (visitas, conversiones, tasa de rebote)
- [ ] Cumplimiento con regulaciones de privacidad (banner de cookies, consentimiento)

**Dependencias:** EP-WB-001 (landing pages como base de tracking)

**Complejidad:** M (integraciones terceros, A/B testing, compliance de privacidad)

**Repositorios:** `mf-core`, `covacha-core`

---

## User Stories Detalladas

---

### EP-WB-001: Landing Pages Multi-Tenant

---

#### US-WB-001: Tenant detection y routing por dominio

**Como** visitante
**Quiero** que al acceder a superpago.com.mx vea la landing de SuperPago y al acceder a baatdigital.com.mx vea la de BaatDigital
**Para** obtener informacion relevante del producto que me interesa sin confusion entre marcas

**Criterios de Aceptacion:**
- [ ] `TenantDetectorService` resuelve tenant por `window.location.hostname`
- [ ] Mapeo de dominios: superpago.com.mx → `superpago`, baatdigital.com.mx → `baatdigital`, alertatribunal.com → `alertatribunal`, localhost → configurable
- [ ] Si el dominio no se reconoce, redirige a superpago.com.mx (tenant por defecto)
- [ ] El tenant se almacena en `covacha:tenant` en localStorage
- [ ] Las rutas publicas se cargan bajo `/portals/website/{tenant}/`
- [ ] El titulo del documento (`<title>`) refleja el tenant activo

**Tareas Tecnicas:**
- [ ] Refactorizar `TenantDetectorService` si es necesario para soportar 3 tenants
- [ ] Crear guard `PublicRouteGuard` que permite acceso sin autenticacion
- [ ] Configurar lazy loading de rutas por tenant
- [ ] Tests: 5+ unit tests (1 por dominio + fallback + localhost)

---

#### US-WB-002: Landing page SuperPago (hero, features, CTA)

**Como** visitante de superpago.com.mx
**Quiero** ver una landing page profesional que explique los servicios de pagos empresariales, SPEI y BillPay
**Para** evaluar si SuperPago es la solucion que mi empresa necesita

**Criterios de Aceptacion:**
- [ ] Hero section: titulo impactante, subtitulo, CTA "Comenzar ahora", imagen/ilustracion
- [ ] Seccion de features: SPEI (transferencias), BillPay (cobros), Dashboard (metricas), Multi-tenant
- [ ] Seccion de como funciona: 3-4 pasos ilustrados
- [ ] Seccion de pricing: planes con comparativa (basico, profesional, empresarial)
- [ ] Seccion de testimonios: al menos 3 testimonios con foto y empresa
- [ ] CTA final: formulario de registro o "Solicitar demo"
- [ ] Footer: links, redes sociales, datos de contacto, legal
- [ ] Responsive en mobile, tablet y desktop

**Tareas Tecnicas:**
- [ ] Crear `SuperpagoLandingComponent` standalone en `portals/website/superpago/`
- [ ] Crear componentes reutilizables: `HeroSectionComponent`, `FeatureGridComponent`, `PricingTableComponent`, `TestimonialCarouselComponent`, `FooterComponent`
- [ ] Obtener contenido desde API: `GET /api/v1/website/pages?tenant=superpago&slug=home`
- [ ] Implementar design system con variables CSS del tenant
- [ ] Tests: 4+ unit tests

---

#### US-WB-003: Landing page BaatDigital (agencia digital)

**Como** visitante de baatdigital.com.mx
**Quiero** ver una landing page que muestre los servicios de agencia digital y marketing
**Para** conocer las capacidades de BaatDigital y decidir si contratar sus servicios

**Criterios de Aceptacion:**
- [ ] Hero section: propuesta de valor de agencia digital, CTA "Ver portafolio"
- [ ] Seccion de servicios: social media, marketing digital, branding, landing pages, WhatsApp marketing
- [ ] Seccion de portafolio: 4-6 casos de exito con imagen y metricas
- [ ] Seccion de equipo: fotos y roles del equipo principal
- [ ] Seccion de clientes: logos de clientes actuales
- [ ] CTA final: formulario de contacto o "Agendar llamada"
- [ ] Footer con datos de contacto, redes y legal
- [ ] Responsive

**Tareas Tecnicas:**
- [ ] Crear `BaatdigitalLandingComponent` standalone en `portals/website/baatdigital/`
- [ ] Reutilizar componentes compartidos (HeroSection, Footer, etc.) con variantes por tenant
- [ ] API: `GET /api/v1/website/pages?tenant=baatdigital&slug=home`
- [ ] Tests: 4+ unit tests

---

#### US-WB-004: Landing page AlertaTribunal (alertas judiciales)

**Como** visitante de alertatribunal.com
**Quiero** ver una landing page que explique el servicio de alertas judiciales y monitoreo de expedientes
**Para** entender como AlertaTribunal puede ayudarme a no perder notificaciones legales

**Criterios de Aceptacion:**
- [ ] Hero section: propuesta de valor de alertas legales, CTA "Registrar mi expediente"
- [ ] Seccion de funcionalidades: monitoreo de expedientes, alertas por email/WhatsApp, historial de movimientos, reportes
- [ ] Seccion de como funciona: 3 pasos (registrar expediente, configurar alertas, recibir notificaciones)
- [ ] Seccion de pricing: plan gratuito vs premium
- [ ] Seccion de FAQ: preguntas frecuentes sobre el servicio
- [ ] CTA final: registro con numero de expediente
- [ ] Footer con legal (aviso de privacidad obligatorio para servicios legales)
- [ ] Responsive

**Tareas Tecnicas:**
- [ ] Crear `AlertatribunalLandingComponent` standalone en `portals/website/alertatribunal/`
- [ ] Crear `FaqSectionComponent` reutilizable con expand/collapse
- [ ] API: `GET /api/v1/website/pages?tenant=alertatribunal&slug=home`
- [ ] Tests: 4+ unit tests

---

#### US-WB-005: Backend API de paginas estaticas

**Como** sistema
**Quiero** un API REST para gestionar el contenido de las paginas del sitio web por tenant
**Para** que el contenido sea editable sin re-deploy y centralizado en DynamoDB

**Criterios de Aceptacion:**
- [ ] `GET /api/v1/website/pages?tenant={tenant}` - listar paginas del tenant
- [ ] `GET /api/v1/website/pages/{slug}?tenant={tenant}` - obtener pagina por slug
- [ ] `POST /api/v1/website/pages` - crear pagina (requiere autenticacion admin)
- [ ] `PUT /api/v1/website/pages/{slug}` - actualizar pagina
- [ ] `DELETE /api/v1/website/pages/{slug}` - eliminar pagina (soft delete)
- [ ] Cada pagina tiene: slug, tenant, title, sections (JSON), seo_meta, status (draft/published), created_at, updated_at
- [ ] Versionado de contenido (cada update crea nueva version, rollback posible)
- [ ] Cache de respuestas publicas (TTL 5 minutos)
- [ ] Paginacion y filtros (por status, por tipo)

**Tareas Tecnicas:**
- [ ] Crear Blueprint `website_bp` en covacha-core con rutas `/api/v1/website/`
- [ ] Crear modelo `WebsitePage` con DynamoDB keys: PK=`PAGE#{tenant}#{slug}`, SK=`METADATA`
- [ ] Crear `WebsitePageService` con logica de negocio
- [ ] Crear `WebsitePageRepository` con operaciones DynamoDB
- [ ] Implementar versionado: PK=`PAGE#{tenant}#{slug}`, SK=`CONTENT#{version}`
- [ ] Tests: 8+ unit tests (CRUD + versionado + cache)

---

#### US-WB-006: Sistema de branding por tenant

**Como** administrador web
**Quiero** configurar el branding visual (colores, logo, tipografia) de cada tenant desde el backend
**Para** que cada landing refleje la identidad de marca correcta sin hardcodear estilos

**Criterios de Aceptacion:**
- [ ] `GET /api/v1/website/branding/{tenant}` - obtener branding del tenant
- [ ] `PUT /api/v1/website/branding/{tenant}` - actualizar branding (admin)
- [ ] Branding incluye: primary_color, secondary_color, accent_color, logo_url, logo_dark_url, favicon_url, font_heading, font_body, brand_name, tagline
- [ ] CSS custom properties se inyectan dinamicamente segun el tenant activo
- [ ] Fallback a branding por defecto si el tenant no tiene configuracion
- [ ] Preview de branding antes de publicar cambios

**Tareas Tecnicas:**
- [ ] Crear `BrandingService` en frontend que carga y aplica CSS custom properties
- [ ] Backend: almacenar branding en DynamoDB PK=`TENANT#{tenant}`, SK=`BRANDING`
- [ ] Crear `TenantBrandingComponent` que inyecta estilos en `:root`
- [ ] Tests: 4+ unit tests (1 por tenant + fallback)

---

#### US-WB-007: Navegacion publica multi-tenant

**Como** visitante
**Quiero** una barra de navegacion con links relevantes al tenant que estoy visitando
**Para** navegar facilmente entre las secciones del sitio (inicio, features, precios, blog, contacto, login)

**Criterios de Aceptacion:**
- [ ] Navbar fija en top con logo del tenant y links de navegacion
- [ ] Links configurables por tenant (no todas las secciones aplican a todos)
- [ ] SuperPago: Inicio, Servicios, Precios, Blog, Documentacion, Contacto, Login
- [ ] BaatDigital: Inicio, Servicios, Portafolio, Blog, Contacto, Login
- [ ] AlertaTribunal: Inicio, Como funciona, Precios, FAQ, Contacto, Login
- [ ] Scroll suave a secciones dentro de la landing (anchor links)
- [ ] Hamburger menu en mobile
- [ ] Boton "Login" redirige a mf-auth

**Tareas Tecnicas:**
- [ ] Crear `PublicNavbarComponent` standalone con inputs de tenant y links
- [ ] Obtener configuracion de navegacion desde branding API o hardcoded por tenant
- [ ] Implementar scroll suave con `scrollIntoView({ behavior: 'smooth' })`
- [ ] Tests: 3+ unit tests

---

#### US-WB-008: Paginas legales (privacidad, terminos, cookies)

**Como** visitante
**Quiero** acceder a las paginas de aviso de privacidad, terminos de servicio y politica de cookies
**Para** conocer las condiciones legales antes de registrarme

**Criterios de Aceptacion:**
- [ ] Pagina de aviso de privacidad por tenant
- [ ] Pagina de terminos y condiciones por tenant
- [ ] Pagina de politica de cookies por tenant
- [ ] Links accesibles desde el footer de todas las paginas
- [ ] Contenido editable desde backend (Markdown renderizado a HTML)
- [ ] Fecha de ultima actualizacion visible
- [ ] URL amigable: `/privacidad`, `/terminos`, `/cookies`

**Tareas Tecnicas:**
- [ ] Crear `LegalPageComponent` generico que renderiza Markdown a HTML
- [ ] Usar la API de paginas existente (US-WB-005) con slugs: `privacy`, `terms`, `cookies`
- [ ] Integrar libreria Markdown (ej: `ngx-markdown` o `marked`)
- [ ] Tests: 3+ unit tests

---

### EP-WB-002: SEO y Performance

---

#### US-WB-009: Pre-rendering para SEO (Angular Universal / Prerender)

**Como** administrador web
**Quiero** que las paginas publicas se pre-rendericen para que los buscadores las indexen correctamente
**Para** aparecer en los primeros resultados de Google cuando busquen nuestros servicios

**Criterios de Aceptacion:**
- [ ] Paginas publicas generan HTML completo al primer request (no SPA vacio)
- [ ] Google Search Console muestra paginas indexadas correctamente
- [ ] El crawler de Google ve el contenido completo (verificar con Google Rich Results Test)
- [ ] Pre-rendering se ejecuta en build time o via servicio SSR
- [ ] Paginas pre-renderizadas se suben a S3 y se sirven desde CloudFront
- [ ] Actualizacion automatica al publicar nuevo contenido (invalidacion de cache + re-prerender)

**Tareas Tecnicas:**
- [ ] Evaluar e implementar: Angular SSR (Universal) o prerendering estatico (Scully / `@angular/ssr`)
- [ ] Configurar build pipeline para generar HTML pre-renderizado
- [ ] Script de invalidacion de CloudFront post-deploy
- [ ] Tests: 3+ unit tests + verificacion manual con Google Bot simulator

---

#### US-WB-010: Meta tags dinamicos por pagina y tenant

**Como** administrador web
**Quiero** configurar title, description y canonical URL por cada pagina y tenant
**Para** optimizar el SEO de cada pagina individualmente y evitar contenido duplicado

**Criterios de Aceptacion:**
- [ ] `<title>` dinamico por pagina (ej: "SuperPago - Pagos Empresariales SPEI" para home)
- [ ] `<meta name="description">` configurado por pagina
- [ ] `<link rel="canonical">` apuntando a la URL canonica
- [ ] Meta tags se actualizan en navegacion SPA (sin reload)
- [ ] Fallback a meta tags del tenant si la pagina no tiene configurados
- [ ] `<html lang="es-MX">` para geotargeting

**Tareas Tecnicas:**
- [ ] Crear `SeoService` que actualiza meta tags via `Meta` y `Title` de Angular
- [ ] Integrar con router events para actualizar en cada navegacion
- [ ] Leer configuracion SEO desde la API de paginas (campo `seo_meta`)
- [ ] Tests: 4+ unit tests

---

#### US-WB-011: Open Graph y Twitter Cards

**Como** visitante
**Quiero** que al compartir una URL del sitio en Facebook, Twitter o WhatsApp se muestre un preview con imagen, titulo y descripcion
**Para** que el link compartido se vea profesional y genere mas clicks

**Criterios de Aceptacion:**
- [ ] `og:title`, `og:description`, `og:image`, `og:url`, `og:type` en todas las paginas
- [ ] `twitter:card`, `twitter:title`, `twitter:description`, `twitter:image` en todas las paginas
- [ ] Imagen OG predeterminada por tenant (1200x630px)
- [ ] Imagen OG personalizable por pagina/articulo
- [ ] Preview correcto en Facebook Debugger, Twitter Card Validator, WhatsApp
- [ ] `og:locale` = `es_MX`

**Tareas Tecnicas:**
- [ ] Extender `SeoService` con metodos para Open Graph y Twitter Cards
- [ ] Generar imagenes OG automaticas para articulos de blog (texto sobre imagen base del tenant)
- [ ] Crear endpoint `GET /api/v1/website/og-image/{tenant}/{slug}` para imagenes OG dinamicas
- [ ] Tests: 3+ unit tests

---

#### US-WB-012: Schema.org structured data

**Como** administrador web
**Quiero** agregar Schema.org structured data (JSON-LD) en las paginas
**Para** obtener rich snippets en Google (estrellas, FAQ, precios, breadcrumbs)

**Criterios de Aceptacion:**
- [ ] Schema `Organization` en la pagina principal de cada tenant
- [ ] Schema `Product` en paginas de pricing/servicios
- [ ] Schema `FAQPage` en paginas con preguntas frecuentes
- [ ] Schema `Article` en articulos del blog
- [ ] Schema `BreadcrumbList` en todas las paginas internas
- [ ] JSON-LD validado con Google Structured Data Testing Tool
- [ ] Los schemas se generan dinamicamente desde los datos del backend

**Tareas Tecnicas:**
- [ ] Crear `StructuredDataService` que inyecta JSON-LD en `<head>`
- [ ] Crear generadores por tipo: `generateOrganizationSchema()`, `generateProductSchema()`, etc.
- [ ] Integrar con router para inyectar schema correcto por ruta
- [ ] Tests: 4+ unit tests

---

#### US-WB-013: Sitemap.xml y robots.txt automaticos

**Como** administrador web
**Quiero** que el sitemap.xml y robots.txt se generen y actualicen automaticamente
**Para** que los buscadores descubran e indexen todas las paginas relevantes

**Criterios de Aceptacion:**
- [ ] `GET /sitemap.xml` genera sitemap XML valido con todas las paginas publicas
- [ ] Sitemap incluye: landing pages, articulos de blog, paginas de docs, paginas legales
- [ ] Cada entrada tiene: loc, lastmod, changefreq, priority
- [ ] `GET /robots.txt` configurado por tenant (permite crawling de paginas publicas, bloquea admin)
- [ ] Sitemap se regenera automaticamente al publicar/despublicar contenido
- [ ] Sitemap registrado en Google Search Console

**Tareas Tecnicas:**
- [ ] Backend: Endpoint `GET /api/v1/website/sitemap/{tenant}` que genera XML
- [ ] Backend: Endpoint `GET /api/v1/website/robots/{tenant}` que genera robots.txt
- [ ] Configurar CloudFront para servir sitemap.xml y robots.txt desde el backend
- [ ] Cron job o trigger al publicar contenido para regenerar sitemap
- [ ] Tests: 3+ unit tests

---

#### US-WB-014: Optimizacion de Core Web Vitals y carga

**Como** visitante
**Quiero** que el sitio cargue rapido y sea fluido al navegar
**Para** tener una buena experiencia sin esperas ni saltos visuales

**Criterios de Aceptacion:**
- [ ] LCP (Largest Contentful Paint) < 2.5 segundos
- [ ] FID (First Input Delay) < 100 milisegundos
- [ ] CLS (Cumulative Layout Shift) < 0.1
- [ ] Lazy loading de imagenes con `loading="lazy"` y placeholder
- [ ] Font display swap para evitar FOIT (Flash of Invisible Text)
- [ ] Compresion gzip/brotli en CloudFront
- [ ] Critical CSS inline para above-the-fold content
- [ ] Preconnect a dominios externos (fonts, analytics, CDN de imagenes)
- [ ] Bundle size de rutas publicas < 200KB (gzipped)

**Tareas Tecnicas:**
- [ ] Auditar con Lighthouse y PageSpeed Insights
- [ ] Implementar `NgOptimizedImage` para imagenes
- [ ] Configurar font-display: swap en Google Fonts
- [ ] Optimizar bundle con tree shaking y code splitting por ruta
- [ ] Configurar CloudFront con compresion brotli
- [ ] Tests: verificacion con Lighthouse CI (score > 90)

---

### EP-WB-003: Sistema de Blog / Contenido

---

#### US-WB-015: Backend API de blog multi-tenant

**Como** sistema
**Quiero** un API REST para gestionar articulos de blog por tenant con categorias y tags
**Para** centralizar el contenido del blog en DynamoDB con operaciones estandar

**Criterios de Aceptacion:**
- [ ] `GET /api/v1/blog/posts?tenant={tenant}` - listar articulos publicados (paginacion cursor-based)
- [ ] `GET /api/v1/blog/posts/{post_id}?tenant={tenant}` - obtener articulo por ID
- [ ] `GET /api/v1/blog/posts/slug/{slug}?tenant={tenant}` - obtener articulo por slug
- [ ] `POST /api/v1/blog/posts` - crear articulo (autenticacion requerida)
- [ ] `PUT /api/v1/blog/posts/{post_id}` - actualizar articulo
- [ ] `DELETE /api/v1/blog/posts/{post_id}` - archivar articulo (soft delete)
- [ ] `GET /api/v1/blog/categories?tenant={tenant}` - listar categorias
- [ ] `GET /api/v1/blog/tags?tenant={tenant}` - listar tags
- [ ] Filtros: por categoria, por tag, por autor, por estado
- [ ] Cada articulo: title, slug, content (Markdown), excerpt, category, tags[], author, cover_image, status (draft/review/published/archived), published_at, reading_time_minutes

**Tareas Tecnicas:**
- [ ] Crear Blueprint `blog_bp` en covacha-core con rutas `/api/v1/blog/`
- [ ] Modelo DynamoDB: PK=`BLOG#{tenant}`, SK=`POST#{post_id}`
- [ ] GSI para listar por status+fecha: GSI1PK=`BLOG#{tenant}#STATUS#{status}`, GSI1SK=`PUBLISHED_AT`
- [ ] Crear `BlogService` y `BlogRepository`
- [ ] Calcular `reading_time_minutes` automaticamente (palabras / 200)
- [ ] Tests: 8+ unit tests

---

#### US-WB-016: Editor Markdown para articulos

**Como** content manager
**Quiero** un editor Markdown con preview en tiempo real para escribir articulos del blog
**Para** crear contenido con formato sin necesidad de conocer HTML

**Criterios de Aceptacion:**
- [ ] Editor split-view: Markdown a la izquierda, preview HTML a la derecha
- [ ] Toolbar con botones: heading, bold, italic, link, image, code block, quote, list
- [ ] Drag and drop de imagenes que se suben automaticamente a S3
- [ ] Syntax highlighting en bloques de codigo
- [ ] Autoguardado cada 30 segundos
- [ ] Contador de palabras y tiempo estimado de lectura
- [ ] Modo fullscreen para escritura sin distracciones

**Tareas Tecnicas:**
- [ ] Crear `MarkdownEditorComponent` standalone
- [ ] Integrar libreria Markdown (ej: `marked` + `highlight.js` para syntax highlighting)
- [ ] Conectar upload de imagenes con S3 adapter existente
- [ ] Auto-save via `BlogService`
- [ ] Tests: 4+ unit tests

---

#### US-WB-017: Listado publico de articulos con filtros

**Como** visitante
**Quiero** ver una lista de articulos del blog con la opcion de filtrar por categoria o tag
**Para** encontrar contenido relevante a mis intereses

**Criterios de Aceptacion:**
- [ ] Pagina `/blog` que lista articulos publicados en orden cronologico inverso
- [ ] Card por articulo: cover image, titulo, excerpt, autor, fecha, categoria, tags, tiempo de lectura
- [ ] Filtro por categoria (sidebar o dropdown)
- [ ] Filtro por tag (clickeable desde cada articulo)
- [ ] Paginacion (10 articulos por pagina)
- [ ] Vista de articulo individual en `/blog/{slug}`
- [ ] Responsive: 1 columna en mobile, 2 en tablet, 3 en desktop

**Tareas Tecnicas:**
- [ ] Crear `BlogListComponent` y `BlogPostCardComponent` standalone
- [ ] Crear `BlogDetailComponent` para vista individual
- [ ] Integrar con API de blog (US-WB-015)
- [ ] Routing: `/blog`, `/blog/:slug`, `/blog/category/:category`, `/blog/tag/:tag`
- [ ] Tests: 4+ unit tests

---

#### US-WB-018: Compartir articulos en redes sociales

**Como** visitante
**Quiero** compartir un articulo del blog en Facebook, Twitter, LinkedIn o WhatsApp con un click
**Para** recomendar contenido interesante a mis contactos

**Criterios de Aceptacion:**
- [ ] Botones de compartir: Facebook, Twitter/X, LinkedIn, WhatsApp, copiar link
- [ ] Cada boton genera la URL de share correcta con titulo y URL del articulo
- [ ] Los botones aparecen en la vista de detalle del articulo (lateral sticky y al final)
- [ ] Contador de shares por red social (si la API del proveedor lo permite)
- [ ] Los botones funcionan en mobile (native share si disponible)

**Tareas Tecnicas:**
- [ ] Crear `ShareButtonsComponent` standalone
- [ ] Usar Web Share API en mobile como fallback
- [ ] URLs de share: `https://www.facebook.com/sharer/sharer.php?u=`, `https://twitter.com/intent/tweet?url=`, etc.
- [ ] Tests: 3+ unit tests

---

#### US-WB-019: RSS feed por tenant

**Como** visitante
**Quiero** suscribirme al RSS feed del blog
**Para** recibir actualizaciones de nuevos articulos en mi lector de feeds

**Criterios de Aceptacion:**
- [ ] `GET /api/v1/blog/rss/{tenant}` genera XML RSS 2.0 valido
- [ ] Feed incluye: title, link, description, language, pubDate, generator
- [ ] Cada item: title, link, description (excerpt), author, category, pubDate, guid
- [ ] Maximo 50 articulos en el feed (los mas recientes)
- [ ] Link al feed en el `<head>` de la pagina: `<link rel="alternate" type="application/rss+xml">`
- [ ] Icono de RSS visible en el header o sidebar del blog

**Tareas Tecnicas:**
- [ ] Backend: Endpoint que genera XML RSS desde articulos publicados
- [ ] Frontend: `<link>` en head y boton/icono RSS en blog
- [ ] Validar con W3C Feed Validation Service
- [ ] Tests: 3+ unit tests

---

#### US-WB-020: Busqueda full-text de articulos

**Como** visitante
**Quiero** buscar articulos por palabras clave
**Para** encontrar rapidamente contenido sobre un tema especifico

**Criterios de Aceptacion:**
- [ ] Campo de busqueda en la pagina del blog
- [ ] Busqueda por titulo, contenido y tags
- [ ] Resultados ordenados por relevancia
- [ ] Highlighting de terminos buscados en los resultados
- [ ] Debounce de 300ms para evitar busquedas por cada tecla
- [ ] Mensaje "Sin resultados" con sugerencia de ampliar la busqueda
- [ ] Busqueda accesible con teclado (Enter para buscar)

**Tareas Tecnicas:**
- [ ] Backend: `GET /api/v1/blog/search?tenant={tenant}&q={query}` con busqueda en DynamoDB (contains en titulo + tags) o solucion externa (Algolia, ElasticSearch lite)
- [ ] Frontend: `BlogSearchComponent` con debounce y highlighting
- [ ] Evaluar si DynamoDB scan es suficiente para el volumen esperado o si se necesita indice de busqueda externo
- [ ] Tests: 3+ unit tests

---

### EP-WB-004: Formularios de Contacto y Lead Capture

---

#### US-WB-021: Formulario de contacto por tenant

**Como** visitante
**Quiero** enviar un mensaje de contacto desde la landing page
**Para** comunicarme con el equipo de ventas sin necesidad de buscar un email

**Criterios de Aceptacion:**
- [ ] Formulario con campos: nombre, email, telefono (opcional), empresa (opcional), mensaje
- [ ] Validacion frontend: email valido, nombre requerido, mensaje min 10 caracteres
- [ ] Validacion backend: sanitizacion de inputs, rate limiting
- [ ] Confirmacion visual al enviar (snackbar "Mensaje enviado correctamente")
- [ ] El formulario se resetea despues de envio exitoso
- [ ] Formulario embebido en la seccion de contacto de cada landing
- [ ] `POST /api/v1/leads/contact` con tenant automatico

**Tareas Tecnicas:**
- [ ] Crear `ContactFormComponent` standalone con reactive forms
- [ ] Backend: Blueprint `leads_bp` con ruta `/api/v1/leads/contact`
- [ ] Modelo DynamoDB: PK=`LEAD#{tenant}`, SK=`ENTRY#{timestamp}#{lead_id}`
- [ ] Rate limiting: max 5 envios por IP por hora (middleware)
- [ ] Tests: 5+ unit tests (validaciones + envio + rate limit)

---

#### US-WB-022: CAPTCHA anti-spam

**Como** administrador web
**Quiero** que los formularios de contacto tengan CAPTCHA
**Para** evitar envios automaticos de spam que llenen la base de leads con basura

**Criterios de Aceptacion:**
- [ ] reCAPTCHA v3 (invisible) integrado en todos los formularios publicos
- [ ] Score minimo de 0.5 para aceptar el envio
- [ ] Si el score es bajo, mostrar reCAPTCHA v2 (checkbox) como fallback
- [ ] Backend valida el token de reCAPTCHA antes de procesar el lead
- [ ] Clave de reCAPTCHA configurable por tenant (cada tenant puede tener su propia)
- [ ] Logs de intentos rechazados para analisis de patrones de spam

**Tareas Tecnicas:**
- [ ] Integrar `ng-recaptcha` o implementacion custom de reCAPTCHA v3
- [ ] Backend: middleware de validacion de token reCAPTCHA con Google API
- [ ] Configurar site keys por tenant en variables de entorno
- [ ] Tests: 3+ unit tests (token valido, invalido, score bajo)

---

#### US-WB-023: Auto-respuesta por email al visitante

**Como** visitante
**Quiero** recibir un email de confirmacion cuando envio un formulario de contacto
**Para** saber que mi mensaje fue recibido y tener expectativa de cuando me responderan

**Criterios de Aceptacion:**
- [ ] Email enviado automaticamente al email del visitante despues de enviar formulario
- [ ] Template de email personalizado por tenant (logo, colores, nombre de marca)
- [ ] Contenido: agradecimiento, resumen del mensaje enviado, tiempo estimado de respuesta, datos de contacto directo
- [ ] Email enviado via SQS (async, no bloquea el response del formulario)
- [ ] Email con formato HTML responsive
- [ ] Remitente configurable por tenant (ej: contacto@superpago.com.mx)

**Tareas Tecnicas:**
- [ ] Backend: Servicio de envio de email (SES o SMTP existente)
- [ ] Templates de email en HTML por tenant (Jinja2 o similar)
- [ ] Encolar envio en SQS para procesamiento async
- [ ] Tests: 3+ unit tests (template rendering, enqueue, envio)

---

#### US-WB-024: Notificacion al equipo de ventas

**Como** equipo de ventas
**Quiero** recibir una notificacion inmediata cuando un visitante envia un formulario de contacto
**Para** responder rapidamente y no perder oportunidades de venta

**Criterios de Aceptacion:**
- [ ] Email al equipo de ventas con datos del lead (nombre, email, telefono, empresa, mensaje)
- [ ] Notificacion in-app en el dashboard admin (badge en bell icon)
- [ ] Notificacion por WhatsApp al numero del vendedor asignado (si esta configurado)
- [ ] Configuracion de destinatarios por tenant (puede ser 1 o multiples emails)
- [ ] Prioridad visual: leads con empresa grande o urgente resaltados

**Tareas Tecnicas:**
- [ ] Backend: Dispatch de notificaciones multi-canal (email + in-app + WhatsApp)
- [ ] Integrar con covacha-notification para notificaciones in-app
- [ ] Integrar con WhatsApp Business API existente para notificaciones
- [ ] Tests: 4+ unit tests

---

#### US-WB-025: Sincronizacion de leads con CRM

**Como** equipo de ventas
**Quiero** que los leads capturados desde el sitio web se sincronicen automaticamente con el CRM
**Para** gestionar el seguimiento desde una sola herramienta sin duplicar datos

**Criterios de Aceptacion:**
- [ ] Cada lead nuevo se crea automaticamente como contacto/lead en covacha-crm
- [ ] Mapeo de campos: nombre → name, email → email, empresa → company, mensaje → notes
- [ ] Fuente del lead marcada como "website" con el tenant y la pagina de origen
- [ ] Si el email ya existe en CRM, se actualiza el registro existente (no duplicar)
- [ ] Lead scoring basico: +10 si tiene empresa, +5 si tiene telefono, +20 si solicita demo
- [ ] Log de sincronizacion para debugging (exito/error por lead)

**Tareas Tecnicas:**
- [ ] Backend: Servicio de sincronizacion lead → CRM via API interna a covacha-crm
- [ ] `POST /api/v1/crm/leads` en covacha-crm (verificar si existe o crear)
- [ ] Cola SQS para sincronizacion async (no bloquear response del formulario)
- [ ] Tests: 4+ unit tests (crear nuevo, actualizar existente, scoring, error handling)

---

#### US-WB-026: Dashboard de leads en admin

**Como** administrador web
**Quiero** ver un dashboard con todos los leads capturados desde el sitio web
**Para** monitorear el volumen y calidad de leads y medir la efectividad de las landing pages

**Criterios de Aceptacion:**
- [ ] Lista de leads con: nombre, email, empresa, fuente (pagina), fecha, score, estado (nuevo/contactado/calificado/descartado)
- [ ] Filtros: por tenant, por fuente, por estado, por rango de fechas
- [ ] KPIs: total leads del periodo, leads por dia (grafica), conversion rate, top fuentes
- [ ] Cambiar estado del lead manualmente (nuevo → contactado → calificado/descartado)
- [ ] Exportar leads como CSV
- [ ] Paginacion y busqueda por nombre/email

**Tareas Tecnicas:**
- [ ] Backend: `GET /api/v1/leads?tenant={tenant}` con filtros y paginacion
- [ ] Backend: `PATCH /api/v1/leads/{lead_id}` para cambiar estado
- [ ] Backend: `GET /api/v1/leads/export?tenant={tenant}&format=csv`
- [ ] Frontend: `LeadDashboardComponent` en area admin de mf-core
- [ ] GSI para filtrar por fuente: GSI2PK=`LEAD#{tenant}#SOURCE#{source}`, GSI2SK=`CREATED_AT`
- [ ] Tests: 5+ unit tests

---

### EP-WB-005: Portal de Documentacion (mf-docs)

---

#### US-WB-027: Estructura de navegacion del portal de docs

**Como** desarrollador
**Quiero** un portal de documentacion con navegacion lateral organizada por secciones
**Para** encontrar facilmente la informacion que necesito para integrar con SuperPago

**Criterios de Aceptacion:**
- [ ] Sidebar de navegacion con estructura de arbol: Inicio, Guia de Inicio, API Reference, Tutoriales, Changelog, Status
- [ ] Cada seccion expandible/colapsable con subsecciones
- [ ] Breadcrumbs para saber donde estoy dentro de la estructura
- [ ] Navegacion con teclado (flechas arriba/abajo, Enter para expandir)
- [ ] Estado de la navegacion se persiste en URL (deep linking)
- [ ] Responsive: sidebar colapsable en mobile (hamburger)
- [ ] URL: superpago.com.mx/docs/{seccion}/{pagina}

**Tareas Tecnicas:**
- [ ] Crear `DocsLayoutComponent` con sidebar + content area
- [ ] Crear `DocsSidebarComponent` con arbol de navegacion recursivo
- [ ] Definir estructura de navegacion en JSON/YAML (configurable)
- [ ] Routing: `/docs/:section/:page`
- [ ] Tests: 4+ unit tests

---

#### US-WB-028: Documentacion de APIs REST

**Como** desarrollador
**Quiero** ver la documentacion completa de cada endpoint de la API con parametros, headers, body y respuestas de ejemplo
**Para** integrar mi sistema con SuperPago sin necesidad de soporte humano

**Criterios de Aceptacion:**
- [ ] Listado de endpoints agrupados por recurso (Accounts, Transfers, Webhooks, etc.)
- [ ] Por endpoint: metodo HTTP, URL, descripcion, parametros de path/query, headers requeridos, body de request (con schema), responses (200, 400, 401, 404, 500) con ejemplos JSON
- [ ] Ejemplos de codigo: cURL, Python, Node.js, PHP
- [ ] Boton "Try it" (opcional futuro) para probar el endpoint con API key de sandbox
- [ ] Autenticacion documentada: como obtener y usar el API key
- [ ] Rate limits documentados por endpoint
- [ ] Contenido renderizado desde Markdown con code blocks

**Tareas Tecnicas:**
- [ ] Crear `ApiDocComponent` que renderiza documentacion de endpoint
- [ ] Backend: `GET /api/v1/docs/pages/{slug}` que sirve contenido Markdown
- [ ] Modelo DynamoDB: PK=`DOC#{tenant}`, SK=`PAGE#{slug}#{version}`
- [ ] Implementar code tabs (cURL / Python / Node.js / PHP) con syntax highlighting
- [ ] Tests: 4+ unit tests

---

#### US-WB-029: Guias de integracion paso a paso

**Como** desarrollador
**Quiero** guias de integracion con instrucciones paso a paso para los casos de uso mas comunes
**Para** implementar la integracion con SuperPago de forma rapida y sin errores

**Criterios de Aceptacion:**
- [ ] Guia "Primeros Pasos": crear cuenta, obtener API key, primer request
- [ ] Guia "Integracion SPEI Out": enviar transferencia SPEI paso a paso
- [ ] Guia "Recibir SPEI In": configurar webhook, procesar deposito entrante
- [ ] Guia "BillPay": crear enlace de pago, procesar pago, manejar webhook
- [ ] Cada guia con: prerrequisitos, pasos numerados, ejemplos de codigo, troubleshooting
- [ ] Indicador de progreso (paso 1 de 5) visible al seguir la guia
- [ ] Tiempo estimado de implementacion por guia

**Tareas Tecnicas:**
- [ ] Crear `GuideComponent` con stepper visual y bloques de codigo
- [ ] Contenido de guias almacenado en DynamoDB como Markdown
- [ ] Crear `CodeBlockComponent` con copy-to-clipboard
- [ ] Tests: 3+ unit tests

---

#### US-WB-030: Changelog publico

**Como** desarrollador
**Quiero** ver un historial de cambios de la API con nuevas funcionalidades, deprecations y bug fixes
**Para** mantener mi integracion actualizada y anticipar cambios que me afecten

**Criterios de Aceptacion:**
- [ ] Lista cronologica de releases con fecha y version
- [ ] Cada release: titulo, descripcion, lista de cambios agrupados por tipo (Added, Changed, Deprecated, Removed, Fixed, Security)
- [ ] Badges de tipo de cambio (verde para Added, amarillo para Changed, rojo para Breaking)
- [ ] Filtro por tipo de cambio y por servicio (SPEI, BillPay, Webhooks)
- [ ] RSS feed del changelog para suscripcion
- [ ] Alertas prominentes para breaking changes

**Tareas Tecnicas:**
- [ ] Crear `ChangelogComponent` con lista de releases
- [ ] Backend: `GET /api/v1/docs/changelog` con paginacion
- [ ] Modelo DynamoDB: PK=`DOC#changelog`, SK=`RELEASE#{date}#{version}`
- [ ] Tests: 3+ unit tests

---

#### US-WB-031: Status page del sistema

**Como** desarrollador
**Quiero** ver el estado actual de cada servicio de SuperPago (API, SPEI, webhooks)
**Para** saber si un problema es de mi lado o del servicio y cuando se resolvera

**Criterios de Aceptacion:**
- [ ] Lista de servicios: API Principal, SPEI Out, SPEI In (webhooks), BillPay, Dashboard, CDN
- [ ] Estado por servicio: Operacional (verde), Degradado (amarillo), Caido (rojo), Mantenimiento (azul)
- [ ] Historial de incidentes de los ultimos 90 dias
- [ ] Uptime percentage por servicio (99.9%, etc.)
- [ ] Suscripcion a actualizaciones por email
- [ ] Actualizacion automatica cada 60 segundos
- [ ] Pagina accesible en status.superpago.com.mx o superpago.com.mx/docs/status

**Tareas Tecnicas:**
- [ ] Crear `StatusPageComponent` con indicadores por servicio
- [ ] Backend: `GET /api/v1/docs/status` que verifica health de cada servicio
- [ ] Backend: health checks a endpoints internos (covacha-payment, covacha-webhook, etc.)
- [ ] Almacenar historial de incidentes en DynamoDB
- [ ] Tests: 4+ unit tests

---

#### US-WB-032: Busqueda full-text en documentacion

**Como** desarrollador
**Quiero** buscar en toda la documentacion por palabras clave
**Para** encontrar rapidamente la seccion que necesito sin navegar por todo el arbol

**Criterios de Aceptacion:**
- [ ] Campo de busqueda en el header del portal de docs
- [ ] Busqueda en titulos, contenido y snippets de codigo
- [ ] Resultados agrupados por seccion (API, Guias, Changelog)
- [ ] Highlighting de terminos buscados en los resultados
- [ ] Shortcut de teclado para abrir busqueda (Ctrl+K o Cmd+K)
- [ ] Resultados en tiempo real mientras se escribe (debounce 200ms)
- [ ] Maximo 20 resultados por busqueda con "Ver mas"

**Tareas Tecnicas:**
- [ ] Crear `DocsSearchComponent` con dialog modal (estilo Algolia DocSearch)
- [ ] Backend: `GET /api/v1/docs/search?q={query}` con busqueda en contenido
- [ ] Evaluar indexacion: DynamoDB scan vs indice de busqueda (Algolia free tier o MiniSearch client-side)
- [ ] Pre-indexar contenido en build time para busqueda client-side (alternativa ligera)
- [ ] Tests: 3+ unit tests

---

### EP-WB-006: Analytics y Conversion Tracking

---

#### US-WB-033: Integracion Google Analytics 4

**Como** administrador web
**Quiero** que todas las paginas publicas reporten eventos a Google Analytics 4
**Para** medir trafico, comportamiento de usuarios y rendimiento de las landing pages

**Criterios de Aceptacion:**
- [ ] GA4 Measurement ID configurable por tenant (variable de entorno)
- [ ] Tracking automatico de page_view en cada navegacion SPA
- [ ] Eventos personalizados: `cta_click` (cual CTA, en que seccion), `form_submit` (cual formulario), `scroll_depth` (25%, 50%, 75%, 100%), `outbound_link_click`
- [ ] User properties: tenant, device_type, referrer
- [ ] Consent mode: GA4 carga solo si el usuario acepta cookies de analytics
- [ ] Datos visibles en GA4 dashboard en menos de 24 horas

**Tareas Tecnicas:**
- [ ] Crear `AnalyticsService` que encapsula gtag.js con metodos tipados
- [ ] Lazy load del script de GA4 (no bloquear rendering)
- [ ] Integrar con router events para page_view automatico
- [ ] Integrar con CookieConsentService para respetar consent
- [ ] Tests: 4+ unit tests (eventos enviados, consent respetado, tenant correcto)

---

#### US-WB-034: UTM tracking y atribucion de fuente

**Como** administrador web
**Quiero** capturar y persistir parametros UTM de las campanas de marketing
**Para** saber de donde vienen los visitantes y cuales campanas generan mas conversiones

**Criterios de Aceptacion:**
- [ ] Captura automatica de utm_source, utm_medium, utm_campaign, utm_term, utm_content de la URL
- [ ] UTM parameters se almacenan en sessionStorage al primer acceso
- [ ] Los UTM se adjuntan a cualquier formulario enviado (lead capture, registro)
- [ ] Si el visitante llega sin UTM, se registra la fuente como: direct, organic, referral (basado en `document.referrer`)
- [ ] Dashboard de leads muestra la fuente/campaña de cada lead
- [ ] Los UTM se envian como parametros a GA4 automaticamente

**Tareas Tecnicas:**
- [ ] Crear `UtmTrackingService` que captura y persiste UTMs
- [ ] Integrar con `ContactFormComponent` y flujo de registro
- [ ] Almacenar fuente del lead en DynamoDB junto con los datos del lead
- [ ] Tests: 4+ unit tests (captura UTM, fallback a referrer, persistencia, adjuntar a lead)

---

#### US-WB-035: A/B testing de landing pages

**Como** administrador web
**Quiero** crear variantes de una landing page y medir cual convierte mejor
**Para** optimizar la tasa de conversion con datos reales en lugar de suposiciones

**Criterios de Aceptacion:**
- [ ] Crear experimento: seleccionar pagina base, definir variantes (A, B, opcionalmente C)
- [ ] Variantes pueden cambiar: hero text, CTA text, CTA color, orden de secciones, imagen hero
- [ ] Distribucion de trafico configurable (50/50, 70/30, etc.)
- [ ] Asignacion de variante persistente por visitante (cookie o fingerprint)
- [ ] Dashboard de experimento: visitas, conversiones, tasa de conversion por variante
- [ ] Significancia estadistica calculada (chi-squared o similar)
- [ ] Accion de "declarar ganador" que aplica la variante ganadora al 100%
- [ ] Maximo 3 experimentos activos por tenant

**Tareas Tecnicas:**
- [ ] Backend: Modelo de experimento en DynamoDB PK=`ABTEST#{tenant}`, SK=`EXP#{exp_id}`
- [ ] Backend: Endpoints CRUD de experimentos + asignacion de variante
- [ ] Frontend: `AbTestService` que asigna variante y renderiza contenido correspondiente
- [ ] Frontend: `AbTestDashboardComponent` en admin con metricas y graficas
- [ ] Calcular significancia estadistica en backend
- [ ] Tests: 5+ unit tests (asignacion, persistencia, metricas, significancia)

---

#### US-WB-036: Banner de cookies y consent management

**Como** visitante
**Quiero** ver un banner de cookies que me permita aceptar o rechazar el uso de cookies de analytics
**Para** tener control sobre mi privacidad y que el sitio cumpla con regulaciones

**Criterios de Aceptacion:**
- [ ] Banner de cookies aparece en la primera visita (bottom bar o modal)
- [ ] Opciones: "Aceptar todas", "Solo necesarias", "Configurar"
- [ ] Configuracion granular: cookies esenciales (siempre activas), analytics, marketing, funcionales
- [ ] Preferencia se guarda en cookie/localStorage y no vuelve a preguntar
- [ ] Si rechaza analytics: GA4, Hotjar y UTM tracking no se cargan
- [ ] Link a politica de cookies desde el banner
- [ ] Opcion de cambiar preferencias desde footer ("Configurar cookies")
- [ ] Compatible con LFPDPPP (Ley Federal de Proteccion de Datos Personales Mexico)

**Tareas Tecnicas:**
- [ ] Crear `CookieConsentBannerComponent` standalone
- [ ] Crear `CookieConsentService` que gestiona preferencias y expone estado reactivo
- [ ] Integrar con `AnalyticsService` para condicionar carga de scripts
- [ ] Almacenar consent en localStorage con key `covacha:cookie_consent`
- [ ] Tests: 4+ unit tests (banner aparece, guardar preferencia, condicionar scripts, cambiar preferencia)

---

## Roadmap

### Fase 1 - Fundacion (Sprint 1-3)

```
EP-WB-001: Landing Pages Multi-Tenant (US-WB-001 a US-WB-008)
  - Sprint 1: Tenant detection, componentes base, API de paginas
  - Sprint 2: Landing SuperPago completa, branding por tenant
  - Sprint 3: Landing BaatDigital, AlertaTribunal, paginas legales, navegacion
```
**Razon**: Sin landing pages no hay producto web publico. Es la base para todo lo demas. Alta prioridad.

### Fase 2 - SEO y Leads (Sprint 3-5)

```
EP-WB-002: SEO y Performance (US-WB-009 a US-WB-014)
  - Sprint 3: Pre-rendering, meta tags, Open Graph
  - Sprint 4: Schema.org, sitemap, robots.txt
  - Sprint 5: Core Web Vitals optimization

EP-WB-004: Formularios de Contacto y Lead Capture (US-WB-021 a US-WB-026)
  - Sprint 3: Formulario de contacto, CAPTCHA
  - Sprint 4: Auto-respuesta, notificacion a ventas, sync CRM
  - Sprint 5: Dashboard de leads
```
**Razon**: SEO es critico para adquisicion organica. Lead capture monetiza el trafico. Ambos deben ir juntos.

### Fase 3 - Contenido (Sprint 5-7)

```
EP-WB-003: Sistema de Blog / Contenido (US-WB-015 a US-WB-020)
  - Sprint 5: Backend API de blog, editor Markdown
  - Sprint 6: Listado publico, compartir, RSS
  - Sprint 7: Busqueda full-text
```
**Razon**: El blog alimenta el SEO con contenido fresco y posiciona la marca como autoridad. Depende de que el SEO base ya este funcionando.

### Fase 4 - Documentacion (Sprint 7-9)

```
EP-WB-005: Portal de Documentacion (US-WB-027 a US-WB-032)
  - Sprint 7: Estructura de navegacion, API docs
  - Sprint 8: Guias de integracion, changelog
  - Sprint 9: Status page, busqueda full-text
```
**Razon**: La documentacion habilita integraciones de terceros y reduce carga de soporte. Se puede construir incrementalmente.

### Fase 5 - Optimizacion (Sprint 9-11)

```
EP-WB-006: Analytics y Conversion Tracking (US-WB-033 a US-WB-036)
  - Sprint 9: GA4, UTM tracking
  - Sprint 10: A/B testing
  - Sprint 11: Cookie consent, refinamiento
```
**Razon**: Analytics y A/B testing requieren trafico existente para ser utiles. Se implementan despues de que las landing pages esten en produccion y recibiendo visitantes.

---

## Grafo de Dependencias

```
EP-WB-001 (Landing Pages Multi-Tenant)
  ├── Depende de: Tenant detection existente en mf-core (completado)
  ├── Depende de: Layout publico separado del admin (completado)
  └── Bloquea: TODAS las demas epicas

EP-WB-002 (SEO y Performance)
  ├── Depende de: EP-WB-001 (necesita paginas para optimizar)
  ├── Se integra con: EP-WB-003 (SEO por articulo de blog)
  └── Se integra con: EP-WB-005 (SEO para indexacion de docs)

EP-WB-003 (Blog / Contenido)
  ├── Depende de: EP-WB-001 (layout publico)
  ├── Depende de: EP-WB-002 (meta tags y structured data por articulo)
  └── Se beneficia de: EP-WB-006 (analytics de engagement en blog)

EP-WB-004 (Formularios y Lead Capture)
  ├── Depende de: EP-WB-001 (formularios embebidos en landing)
  ├── Depende de: covacha-crm (sincronizacion de leads)
  ├── Depende de: covacha-notification (notificaciones a ventas)
  └── Se beneficia de: EP-WB-006 (UTM tracking en leads)

EP-WB-005 (Portal de Documentacion)
  ├── Depende de: EP-WB-001 (layout publico)
  ├── Depende de: EP-WB-002 (SEO para indexacion)
  └── Independiente de: EP-WB-003, EP-WB-004 (puede desarrollarse en paralelo)

EP-WB-006 (Analytics y Conversion Tracking)
  ├── Depende de: EP-WB-001 (paginas como base de tracking)
  ├── Se integra con: EP-WB-004 (UTM en leads, conversion tracking en formularios)
  └── Se beneficia de: EP-WB-003 (tracking de engagement en blog)
```

### Diagrama de Dependencias

```
                 +---------------------------+
                 | Tenant Detection (Existe) |
                 +---------------------------+
                              |
                              v
                 +---------------------------+
                 | EP-WB-001                 |
                 | Landing Pages Multi-Tenant|
                 +---------------------------+
                   |       |       |       |
          +--------+   +---+   +---+   +---+--------+
          |            |       |       |             |
          v            v       v       v             v
  +-----------+  +---------+  +----------+  +-----------+  +-----------+
  | EP-WB-002 |  |EP-WB-004|  | EP-WB-005|  | EP-WB-006 |  |           |
  | SEO &     |  |Lead     |  | Docs     |  | Analytics |  | covacha-  |
  | Performa. |  |Capture  |  | Portal   |  | & A/B     |  | crm       |
  +-----------+  +---------+  +----------+  +-----------+  +-----------+
       |              |                           |
       v              v                           v
  +-----------+  +---------+               +-----------+
  | EP-WB-003 |  |covacha- |               | EP-WB-004 |
  | Blog /    |  |notific. |               | (UTM en   |
  | Contenido |  +---------+               |  leads)   |
  +-----------+                            +-----------+
```

---

## Riesgos y Mitigaciones

| # | Riesgo | Impacto | Probabilidad | Mitigacion |
|---|--------|---------|--------------|------------|
| 1 | Angular SSR/pre-rendering agrega complejidad al build y deploy | Build time largo, errores de hydration | Alta | Evaluar prerendering estatico (mas simple que SSR completo). Implementar incrementalmente: primero landing home, luego blog, luego docs |
| 2 | Contenido hardcodeado vs dinamico: si se abusa del CMS, el rendimiento baja | Latencia alta, cache invalidation compleja | Media | Definir que es estatico (layout, componentes) vs dinamico (textos, imagenes). Contenido "semi-estatico" con cache de 5 min en CloudFront |
| 3 | SEO para SPA es dificil sin SSR: Google puede no indexar correctamente | Paginas no aparecen en Google | Alta | Pre-rendering es obligatorio para paginas publicas. Verificar indexacion con Google Search Console semanalmente despues del deploy |
| 4 | Spam en formularios de contacto satura la base de leads | Leads basura, equipo de ventas pierde confianza | Alta | reCAPTCHA v3 + rate limiting + blacklist de IPs. Monitoreo semanal de volumen de spam |
| 5 | 3 tenants con branding diferente multiplica esfuerzo de QA | Bugs visuales en un tenant que no se detectan | Media | Tests E2E por tenant (Playwright parametrizado por dominio). Design system con CSS custom properties que garantiza consistencia |
| 6 | Portal de documentacion desactualizado vs API real | Desarrolladores se frustran con docs incorrectos | Alta | Generar docs parcialmente desde OpenAPI specs. Changelog obligatorio en cada deploy. PR review incluye verificar docs |
| 7 | A/B testing puede degradar la experiencia si no se maneja bien | Visitantes ven contenido inconsistente entre visitas | Media | Asignacion persistente por cookie (misma variante siempre). Limitar a 3 experimentos activos. Rollback rapido si metricas caen |
| 8 | LFPDPPP compliance: regulaciones mexicanas de privacidad de datos | Multas, problemas legales | Media | Cookie consent banner desde dia 1. Aviso de privacidad por tenant. No capturar datos sensibles sin consentimiento explicito |
| 9 | DynamoDB scan para busqueda full-text no escala | Busqueda lenta con muchos articulos | Baja (inicio) | Comenzar con DynamoDB contains. Si el volumen supera 500 articulos, migrar a Algolia o busqueda client-side pre-indexada |
| 10 | Bundle size de rutas publicas crece al agregar blog, docs, analytics | LCP se degrada, UX pobre | Media | Code splitting agresivo: cada seccion es un lazy-loaded module. Monitorear bundle size en CI (alerta si > 200KB gzipped) |

---

## Definition of Done (Global)

Para considerar una user story como DONE:

- [ ] Codigo implementado en `mf-core` (src/app/portals/website/) o `covacha-core` segun corresponda
- [ ] Componentes Angular: standalone, OnPush change detection, Signals donde aplique
- [ ] Unit tests con coverage >= 80% (Karma + Jasmine)
- [ ] E2E test para flujo principal (Playwright, parametrizado por tenant)
- [ ] Build de produccion exitoso
- [ ] Responsive verificado en 3 breakpoints: mobile (375px), tablet (768px), desktop (1200px)
- [ ] Branding correcto para los 3 tenants verificado visualmente
- [ ] Ningun archivo > 1000 lineas
- [ ] Ninguna funcion > 50 lineas
- [ ] Lighthouse score > 90 en paginas publicas
- [ ] Code review aprobado
- [ ] Documentacion actualizada si aplica (especialmente para EP-WB-005)
- [ ] PR creado automaticamente via GitHub Actions (coverage >= 98%)
