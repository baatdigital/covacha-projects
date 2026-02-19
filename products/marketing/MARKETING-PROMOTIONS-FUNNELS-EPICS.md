# Marketing - Promociones Dinamicas y Funnels de Venta (EP-MK-026 a EP-MK-030)

**Fecha**: 2026-02-19
**Product Owner**: BaatDigital / Marketing
**Estado**: EN PROGRESO (EP-MK-026 a 029 completados, EP-MK-030 pendiente)
**Continua desde**: MARKETING-META-AI-EPICS.md (EP-MK-025, US-MK-101 a US-MK-107)
**User Stories**: US-MK-108 a US-MK-140
**Referencia**: baatdigital.com.mx como cliente ejemplo ya sincronizado

---

## Tabla de Contenidos

1. [Contexto y Motivacion](#contexto-y-motivacion)
2. [Problemas Actuales a Resolver](#problemas-actuales-a-resolver)
3. [Arquitectura de Promociones y Funnels](#arquitectura-de-promociones-y-funnels)
4. [Mapa de Epicas](#mapa-de-epicas)
5. [Epicas Detalladas](#epicas-detalladas)
6. [User Stories Detalladas](#user-stories-detalladas)
7. [Estrategia de Testing](#estrategia-de-testing)
8. [Roadmap](#roadmap)
9. [Grafo de Dependencias](#grafo-de-dependencias)
10. [Riesgos y Mitigaciones](#riesgos-y-mitigaciones)

---

## Contexto y Motivacion

El sistema de promociones de mf-marketing/covacha-core ya tiene funcionalidad basica: creacion de promociones con wizard de 5 pasos (identidad, diseno, landing, SEO, QR) y landing pages publicas renderizadas por slug. Sin embargo, hay problemas criticos que impiden la adopcion en produccion:

### Cliente de Referencia: BaatDigital

| URL | Estado Actual | Problema |
|-----|---------------|----------|
| `baatdigital.com.mx/baatdigital/promociones` | Muestra formulario de creacion en lugar de listado | Debe leer promociones de la base de datos |
| `baatdigital.com.mx/promotions/bot-whatsapp-ia` | Redirige a pagina normal (404/home) | La ruta en ingles no funciona, solo `/promociones/slug` |
| Landing pages de promociones | Mezcla layouts del sitio web con landing | Debe ser layout independiente enfocado a ventas |

### Capacidades Faltantes

| Capacidad | Estado | Prioridad |
|-----------|--------|-----------|
| Lectura de promociones desde BD | No implementado (usa form component) | P1 Critica |
| Routing en ingles `/promotions/:slug` | Roto (redirige a home) | P1 Critica |
| QR multidimensional en landing | No implementado | P1 Alta |
| Formulario contacto → CRM leads | No conectado al CRM | P1 Alta |
| Vigencia de promociones (auto-hide) | No implementado | P1 Alta |
| Estilo del website heredado | Parcial, mezcla layouts | P2 Media |
| Chatbot entiende promociones | No implementado | P2 Media |
| Chatbot visible en landing | No implementado | P2 Media |
| Funnels de venta por canal | No existe | P1 Alta |
| Funnel por defecto (email bienvenida) | No existe | P1 Alta |
| Funnel chaining | No existe | P2 Media |
| Presencia mensual ante cliente | No automatizado | P2 Media |

### Repositorios Involucrados

| Repositorio | Funcion | Cambios |
|-------------|---------|---------|
| `mf-marketing` | Frontend Angular 21 | Paginas de promociones, landing, funnels, formularios |
| `covacha-core` | Backend API Flask | Endpoints promociones, funnels, leads, vigencia |
| `covacha-botia` | Motor de bots/IA | Chatbot entiende promociones, funnels WhatsApp |
| `mf-ia` | Frontend IA | Configuracion de funnels, clientes |
| `covacha-libs` | Modelos compartidos | Modelos Pydantic de funnels y promociones |

---

## Problemas Actuales a Resolver

### 1. Promociones NO leen de base de datos

**Problema**: La pagina `/baatdigital/promociones` renderiza el componente de formulario de creacion en lugar de un listado de promociones activas.

**Solucion**: Crear componente `PromotionListPublicComponent` que consuma el endpoint `GET /api/v1/clients/{client_id}/promotions?status=active&valid=true` y renderice cards de promociones.

### 2. Routing en ingles roto

**Problema**: `/promotions/bot-whatsapp-ia` redirige a home. Solo funciona `/promociones/bot-whatsapp-ia`.

**Solucion**: Configurar rutas duplicadas en el router de la pagina web publica: tanto `/promotions/:slug` como `/promociones/:slug` deben funcionar. La URL canonica debe ser en ingles `/promotions/:slug`.

### 3. Layouts mezclados

**Problema**: Las landing pages de promociones heredan el layout general del sitio web (header, footer, nav), lo cual distrae del objetivo de conversion.

**Solucion**: Crear `PromotionLandingLayout` dedicado: sin navegacion principal, con header minimo (logo + CTA), footer legal, formulario de contacto prominente, y QR code.

### 4. Sin QR multidimensional

**Problema**: Las landing de promociones no muestran QR code para compartir.

**Solucion**: Integrar generacion de QR dinaminco (con logo del cliente en el centro) que apunte a la URL de la landing. QR visible en todas las landing de promociones.

### 5. Formulario de contacto desconectado del CRM

**Problema**: Los formularios de contacto en landing pages no se guardan como leads en el CRM de mf-marketing.

**Solucion**: Cada submit del formulario crea un lead en `covacha-core` endpoint `POST /api/v1/clients/{client_id}/leads` con source=`promotion:{slug}`, que se visualiza en mf-marketing.

### 6. Sin sistema de funnels de venta

**Problema**: No existe un motor de funnels que automatice la comunicacion post-lead (email bienvenida, seguimiento, reactivacion).

**Solucion**: Crear motor de funnels en covacha-botia con canales email y WhatsApp, configurable por frecuencia, timezone, y con funnel chaining.

---

## Arquitectura de Promociones y Funnels

```
                    ┌────────────────────────────────────────┐
                    │         PAGINA WEB DEL CLIENTE          │
                    │         (baatdigital.com.mx)             │
                    │                                          │
                    │  /promotions  ──► Lista de promociones   │
                    │                    activas (desde BD)     │
                    │                                          │
                    │  /promotions/:slug ──► Landing de venta  │
                    │     - QR multidimensional                │
                    │     - Formulario contacto → CRM Lead     │
                    │     - Chatbot del cliente visible         │
                    │     - Estilo heredado del website         │
                    │     - Vigencia auto-check                │
                    └──────────────────┬───────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                        covacha-core (Backend)                         │
│                                                                       │
│  GET /promotions?status=active&valid=true  ──► Lista filtrada        │
│  GET /promotions/:slug                     ──► Detalle + vigencia    │
│  POST /leads                               ──► Crear lead en CRM    │
│  GET /funnels                              ──► Funnels del cliente   │
│  POST /funnels/:id/trigger                 ──► Disparar funnel      │
└───────────────────────┬──────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     covacha-botia (Motor de Funnels)                   │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                   MOTOR DE FUNNELS DE VENTA                     │ │
│  │                                                                  │ │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │ │
│  │  │ Trigger  │───►│  Step 1  │───►│  Step 2  │───►│  Step N  │  │ │
│  │  │ (Lead    │    │ (Email   │    │ (Wait    │    │ (Email   │  │ │
│  │  │  created)│    │  welcome)│    │  3 days) │    │  follow) │  │ │
│  │  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │ │
│  │                                                                  │ │
│  │  Canales:                                                        │ │
│  │  - EMAIL: SES/SMTP, templates, personalización                  │ │
│  │  - WHATSAPP: Templates aprobados, bot atiende respuestas        │ │
│  │                                                                  │ │
│  │  Configuracion por step:                                         │ │
│  │  - Delay: minutos/horas/dias                                     │ │
│  │  - Horario de envio: 9am-6pm (timezone configurable)            │ │
│  │  - Recurrencia: una vez / semanal / mensual / infinito           │ │
│  │  - Condicion: abrio email? respondio? compro?                   │ │
│  │  - Funnel chain: si condicion → enviar a otro funnel            │ │
│  │                                                                  │ │
│  │  Funnel por defecto (auto-creado):                               │ │
│  │  1. Email bienvenida al lead (inmediato)                         │ │
│  │  2. Email notificacion al equipo (inmediato)                     │ │
│  │  3. Email follow-up (3 dias)                                     │ │
│  │  4. Email info de valor (7 dias)                                 │ │
│  │  5. Loop mensual: nuevas promos / info / lanzamientos           │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │              CHATBOT + PROMOCIONES                               │ │
│  │                                                                  │ │
│  │  - Knowledge base incluye promociones activas del cliente       │ │
│  │  - Bot puede responder preguntas sobre promociones              │ │
│  │  - Bot visible en landing pages de promociones                   │ │
│  │  - Si cliente tiene WhatsApp bot → funnel WhatsApp disponible   │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Mapa de Epicas

| ID | Epica | User Stories | Complejidad | Prioridad | Dependencias |
|----|-------|-------------|-------------|-----------|--------------|
| EP-MK-026 | Promociones Dinamicas desde BD | US-MK-108 a US-MK-114 | M | P1 Critica | COMPLETADO |
| EP-MK-027 | Landing de Promociones Orientada a Ventas | US-MK-115 a US-MK-122 | L | P1 Alta | COMPLETADO |
| EP-MK-028 | Motor de Funnels de Venta Multi-Canal | US-MK-123 a US-MK-132 | XL | P1 Alta | COMPLETADO (backend) |
| EP-MK-029 | Integracion Chatbot + Promociones | US-MK-133 a US-MK-137 | M | P2 Media | COMPLETADO (backend) |
| EP-MK-030 | Tests y Cobertura Completa Promociones | US-MK-138 a US-MK-140 | L | P1 Alta | EP-MK-026 a EP-MK-029 |

**Totales**:
- 5 epicas
- 33 user stories (US-MK-108 a US-MK-140)
- Estimacion: ~40-60 dev-days

---

## Epicas Detalladas

---

### EP-MK-026: Promociones Dinamicas desde Base de Datos

> **Estado: COMPLETADO** — PromocionesComponent refactorizado de JSON estatico a DynamicPromotionsService. Routing reestructurado para slug dinamico. Filtrado por expiracion implementado.

**Objetivo**: Reemplazar el componente de formulario de creacion en la pagina publica de promociones por un listado dinamico que lee promociones activas y vigentes de la base de datos.

**Estado actual**: La pagina `/baatdigital/promociones` renderiza el wizard de creacion de promociones en lugar de un listado. No hay endpoint publico que filtre por vigencia.

**Archivos clave**:
- `mf-marketing/src/app/presentation/pages/` (paginas de promociones)
- `mf-marketing/src/app/infrastructure/adapters/` (adapters HTTP)
- `covacha-core/src/` (endpoints de promociones)

**User Stories**: US-MK-108 a US-MK-114

---

### EP-MK-027: Landing de Promociones Orientada a Ventas

> **Estado: COMPLETADO** — DynamicLandingComponent integrado con SendContactUseCase para CRM, boton flotante WhatsApp, boton flotante QR, tracking de conversiones.

**Objetivo**: Crear landing pages de promociones con layout dedicado a conversion, QR multidimensional, formulario de contacto amigable que alimenta el CRM, y chatbot integrado. Las URLs deben funcionar en ingles `/promotions/:slug`.

**Estado actual**: Landing existe pero mezcla layouts, no tiene QR, el formulario no conecta al CRM, y la ruta en ingles redirige a home.

**Archivos clave**:
- Router principal de pagina web publica
- Componentes de landing existentes
- Formularios de contacto existentes

**User Stories**: US-MK-115 a US-MK-122

---

### EP-MK-028: Motor de Funnels de Venta Multi-Canal

> **Estado: COMPLETADO (backend)** — FunnelExecutorService en covacha-botia: auto-enroll, funnel por defecto 4 pasos, despacho SQS email/WhatsApp, FunnelController + routes. 33 tests.

**Objetivo**: Crear sistema de funnels de venta configurable con canales email y WhatsApp. Incluye funnel por defecto (bienvenida + notificacion equipo), configuracion de frecuencia/timezone/horarios, recurrencia mensual infinita, y funnel chaining.

**Estado actual**: No existe ningun sistema de funnels. Las promociones no tienen seguimiento automatizado post-lead.

**Backend**: covacha-botia (motor de funnels)
**Frontend**: mf-marketing (selector de funnels en editor de landing) + mf-ia (configuracion de funnels)

**User Stories**: US-MK-123 a US-MK-132

---

### EP-MK-029: Integracion Chatbot + Promociones

> **Estado: COMPLETADO (backend)** — PromotionContextService en covacha-botia: regex pattern matching + cache 5min + inyeccion de contexto de promociones en WebChatController. 16 tests.

**Objetivo**: El chatbot del cliente (web y WhatsApp) debe entender las promociones activas, poder responder preguntas sobre ellas, y estar visible en las landing pages de promociones.

**Estado actual**: El chatbot no tiene knowledge base de promociones ni esta integrado en las landing pages.

**User Stories**: US-MK-133 a US-MK-137

---

### EP-MK-030: Tests y Cobertura Completa Promociones

**Objetivo**: Tests unitarios, de integracion y E2E para todo el sistema de promociones y funnels. Coverage >= 98% en backend, >= 90% en frontend.

**User Stories**: US-MK-138 a US-MK-140

---

## User Stories Detalladas

---

### EP-MK-026: Promociones Dinamicas desde BD

---

#### US-MK-108: Endpoint publico de promociones activas y vigentes

**Como** sistema de pagina web publica
**Quiero** un endpoint que devuelva solo promociones activas cuya fecha de vigencia no haya expirado
**Para** mostrar unicamente promociones disponibles al visitante

**Criterios de Aceptacion:**
- [ ] `GET /api/v1/public/clients/{client_slug}/promotions` devuelve solo promociones con `status=active`
- [ ] Filtra por vigencia: `start_date <= now <= end_date`
- [ ] Incluye campos: titulo, descripcion corta, imagen, slug, fecha vigencia, precio/descuento
- [ ] Ordenado por fecha de creacion descendente
- [ ] Paginacion con `limit` y `offset`
- [ ] Cache de 5 minutos para reducir carga
- [ ] Response incluye `total_count` para paginacion

**Tareas Tecnicas:**
- [ ] Crear endpoint publico en covacha-core (sin auth requerida)
- [ ] Filtro de vigencia en query DynamoDB (GSI por status + fecha)
- [ ] Tests: 8+ unit tests (happy path, sin promociones, expiradas, paginacion, cache)

---

#### US-MK-109: Componente listado publico de promociones

**Como** visitante de la pagina web del cliente
**Quiero** ver un listado de promociones disponibles con cards atractivas
**Para** descubrir ofertas y acceder a sus landing pages

**Criterios de Aceptacion:**
- [ ] Componente `PromotionListPublicComponent` reemplaza el formulario actual
- [ ] Muestra cards con: imagen, titulo, descripcion corta, badge de vigencia, CTA
- [ ] Click en card navega a `/promotions/:slug`
- [ ] Responsive: 3 columnas desktop, 2 tablet, 1 mobile
- [ ] Loading skeleton mientras carga datos
- [ ] Mensaje "No hay promociones disponibles" si lista vacia
- [ ] Hereda el estilo CSS del website del cliente (colores primarios, tipografia)

**Tareas Tecnicas:**
- [ ] Crear componente standalone en mf-marketing
- [ ] Consumir adapter `PromotionPublicAdapter` → endpoint publico
- [ ] CSS variables para heredar estilo del website
- [ ] Tests: 6+ unit tests

---

#### US-MK-110: Filtrado por vigencia automatico

**Como** administrador de promociones
**Quiero** que las promociones vencidas desaparezcan automaticamente de la lista publica y landing
**Para** no mostrar ofertas que ya no estan disponibles

**Criterios de Aceptacion:**
- [ ] Promociones con `end_date < now` no aparecen en listado publico
- [ ] Landing de promocion vencida muestra mensaje "Esta promocion ya no esta disponible" con link a lista
- [ ] El endpoint de detalle devuelve `is_expired: true` para promociones vencidas
- [ ] Cron job o TTL que marca promociones como `expired` automaticamente
- [ ] En el admin, las promociones vencidas se muestran con badge "Expirada" pero siguen visibles

**Tareas Tecnicas:**
- [ ] Agregar campo `end_date` y `start_date` al modelo de promocion si no existe
- [ ] Logica de vigencia en endpoint publico (server-side, no client-side)
- [ ] Scheduler o DynamoDB TTL para auto-expirar
- [ ] Tests: 6+ unit tests (vigencia activa, expirada, sin fecha, futura)

---

#### US-MK-111: Herencia de estilo del website del cliente

**Como** administrador de la pagina web
**Quiero** que las promociones y landing pages hereden automaticamente el estilo visual de mi website
**Para** mantener consistencia de marca sin configuracion manual

**Criterios de Aceptacion:**
- [ ] Colores primarios, secundarios y de acento del website se aplican a cards y landing
- [ ] Tipografia del website se hereda
- [ ] Logo del cliente aparece en header de landing
- [ ] Botones CTA usan el color primario del cliente
- [ ] Si no hay estilo configurado, usar estilo por defecto del sistema

**Tareas Tecnicas:**
- [ ] Leer configuracion de estilo desde `client.brand_kit` o `client.website_config`
- [ ] Inyectar CSS variables dinamicas en runtime
- [ ] Fallback a tema por defecto si no hay config
- [ ] Tests: 4+ unit tests

---

#### US-MK-112: Routing en ingles /promotions/:slug funcional

**Como** visitante internacional de la pagina web
**Quiero** acceder a promociones via URL en ingles `/promotions/:slug`
**Para** tener URLs profesionales y SEO-friendly en ingles

**Criterios de Aceptacion:**
- [ ] `/promotions/:slug` carga la landing de la promocion correctamente
- [ ] `/promotions` carga el listado de promociones
- [ ] `/promociones/:slug` redirige con 301 a `/promotions/:slug` (backward compatible)
- [ ] `/promociones` redirige con 301 a `/promotions`
- [ ] No hay redirect loop ni 404
- [ ] URL canonica en `<link rel="canonical">` apunta a version en ingles

**Tareas Tecnicas:**
- [ ] Corregir configuracion de rutas en el router del website publico
- [ ] Agregar redirect 301 de `/promociones/` a `/promotions/`
- [ ] Verificar que el middleware de routing no intercepte la ruta en ingles
- [ ] Tests: 6+ unit tests (routing, redirects, 404, canonical)

---

#### US-MK-113: Pagina de promocion no disponible

**Como** visitante que accede a una promocion vencida o inexistente
**Quiero** ver un mensaje claro indicando que la promocion no esta disponible
**Para** no quedarme en una pagina rota y poder explorar otras ofertas

**Criterios de Aceptacion:**
- [ ] Promocion vencida muestra: "Esta promocion finalizo el {fecha}. Descubre nuestras ofertas actuales."
- [ ] Promocion inexistente muestra: "Promocion no encontrada. Conoce nuestras ofertas."
- [ ] Boton CTA hacia `/promotions` (listado de promociones activas)
- [ ] Diseño coherente con el estilo del website
- [ ] Meta tag `noindex` para evitar indexacion de paginas vencidas

**Tareas Tecnicas:**
- [ ] Crear componente `PromotionNotAvailableComponent`
- [ ] Logica de redirect condicional en resolver o guard
- [ ] Tests: 4+ unit tests

---

#### US-MK-114: SEO dinamico para listado de promociones

**Como** motor de busqueda (Google, Bing)
**Quiero** que la pagina de listado de promociones tenga meta tags dinamicos
**Para** indexar correctamente las promociones del cliente

**Criterios de Aceptacion:**
- [ ] `<title>` incluye nombre del cliente + "Promociones"
- [ ] `<meta description>` incluye resumen de promociones activas
- [ ] `<meta og:image>` usa imagen de la primera promocion o logo del cliente
- [ ] Schema.org `OfferCatalog` markup para rich snippets
- [ ] Sitemap XML incluye URLs de promociones activas

**Tareas Tecnicas:**
- [ ] Actualizar servicio de SEO dinamico existente
- [ ] Agregar structured data Schema.org
- [ ] Tests: 4+ unit tests

---

### EP-MK-027: Landing de Promociones Orientada a Ventas

---

#### US-MK-115: Layout dedicado para landing de promociones

**Como** visitante de una landing de promocion
**Quiero** ver una pagina enfocada exclusivamente en la oferta sin distracciones
**Para** tomar una decision de compra/contacto sin navegacion que me saque de la pagina

**Criterios de Aceptacion:**
- [ ] Layout sin menu de navegacion principal del website
- [ ] Header minimo: logo del cliente (pequeno) + boton CTA sticky
- [ ] Hero section con imagen/video principal de la promocion
- [ ] Seccion de beneficios (3-6 bullet points)
- [ ] Seccion de precio/descuento con urgencia visual (countdown si hay fecha fin)
- [ ] Formulario de contacto prominente (above the fold en mobile)
- [ ] Testimonios/social proof si disponibles
- [ ] Footer legal minimo (privacidad, terminos)
- [ ] Boton floating de CTA en mobile

**Tareas Tecnicas:**
- [ ] Crear `PromotionLandingLayoutComponent` standalone
- [ ] Separar del `WebsiteLayoutComponent` existente
- [ ] Responsive first: mobile → tablet → desktop
- [ ] Tests: 6+ unit tests

---

#### US-MK-116: QR multidimensional integrado en landing

**Como** administrador de promociones
**Quiero** que cada landing de promocion muestre un QR code personalizado con el logo del cliente
**Para** que los visitantes puedan compartir la promocion facilmente (impresos, redes, email)

**Criterios de Aceptacion:**
- [ ] QR code generado dinamicamente con URL de la landing
- [ ] Logo del cliente en el centro del QR (formato multidimensional)
- [ ] Colores del QR heredan del brand kit del cliente
- [ ] Boton "Descargar QR" en formato PNG (300dpi) y SVG
- [ ] QR visible en seccion dedicada de la landing (no oculto)
- [ ] QR tambien disponible en el admin de la promocion para impresion
- [ ] QR incluye UTM parameters para tracking: `?utm_source=qr&utm_medium=offline&utm_campaign={slug}`

**Tareas Tecnicas:**
- [ ] Integrar libreria de QR con logo overlay (ej: `qrcode` + canvas manipulation)
- [ ] Servicio `QRGeneratorService` que acepta URL + logo + colores
- [ ] Endpoint backend para generar QR server-side (para impresion alta calidad)
- [ ] Tests: 5+ unit tests

---

#### US-MK-117: Formulario de contacto super amigable

**Como** visitante interesado en una promocion
**Quiero** un formulario de contacto simple, rapido y sin friccion
**Para** solicitar informacion sin sentir que es un proceso tedioso

**Criterios de Aceptacion:**
- [ ] Campos minimos: nombre, email, telefono (opcional), mensaje (opcional)
- [ ] Autocompletado del navegador activado
- [ ] Validacion en tiempo real (no al submit) con mensajes amigables
- [ ] Boton de envio con micro-animacion de carga
- [ ] Mensaje de exito con personalidad: "Genial, {nombre}! Te contactaremos pronto."
- [ ] Opcion de contacto rapido via WhatsApp (si el cliente tiene bot)
- [ ] Responsive y accesible (WCAG 2.1 AA)
- [ ] Pre-fill de utm_source, utm_medium, utm_campaign desde URL
- [ ] Campo oculto con slug de la promocion para tracking

**Tareas Tecnicas:**
- [ ] Crear `PromotionContactFormComponent` standalone
- [ ] Reactive forms con validacion asincrona
- [ ] Conectar con endpoint de leads del CRM
- [ ] Tests: 8+ unit tests (validacion, submit, errores, prefill)

---

#### US-MK-118: Formulario de contacto carga como lead en CRM

**Como** equipo de ventas del cliente
**Quiero** que cada formulario enviado desde una landing de promocion se registre como lead en el CRM de mf-marketing
**Para** hacer seguimiento y conversion de prospectos

**Criterios de Aceptacion:**
- [ ] Submit del formulario crea lead via `POST /api/v1/clients/{client_id}/leads`
- [ ] Lead incluye: nombre, email, telefono, mensaje, source=`promotion:{slug}`, utm_params
- [ ] Lead aparece en mf-marketing en la seccion de leads del cliente
- [ ] Lead tiene status inicial `new`
- [ ] Notificacion al equipo del cliente (email + in-app) cuando llega nuevo lead
- [ ] Deduplicacion: si el email ya existe como lead, actualizar en lugar de duplicar
- [ ] Dispara funnel de venta asociado a la promocion (si existe)

**Tareas Tecnicas:**
- [ ] Crear/actualizar endpoint de leads en covacha-core
- [ ] Integracion con motor de funnels en covacha-botia
- [ ] Notificacion via SQS/webhook al equipo
- [ ] Tests: 8+ unit tests (crear, deduplicar, notificar, funnel trigger)

---

#### US-MK-119: Countdown de vigencia en landing

**Como** visitante de una landing de promocion
**Quiero** ver un countdown visual con el tiempo restante de la oferta
**Para** sentir urgencia y tomar accion antes de que expire

**Criterios de Aceptacion:**
- [ ] Countdown muestra dias, horas, minutos, segundos restantes
- [ ] Se actualiza en tiempo real (cada segundo)
- [ ] Diseño integrado en el hero de la landing
- [ ] Cuando expira: oculta countdown y muestra "Oferta finalizada"
- [ ] Si la promocion no tiene fecha fin, no muestra countdown
- [ ] Timezone del countdown es la del visitante (client-side)

**Tareas Tecnicas:**
- [ ] Crear `CountdownTimerComponent` standalone
- [ ] Usar `setInterval` con cleanup en `ngOnDestroy`
- [ ] Tests: 4+ unit tests

---

#### US-MK-120: Template de landing enfocado a ventas

**Como** administrador de promociones
**Quiero** que el template por defecto de landing de promociones este disenado para maximizar conversiones
**Para** obtener mas leads y ventas de cada promocion

**Criterios de Aceptacion:**
- [ ] Estructura de landing tipo sales page:
  1. Hero: titulo impactante + imagen + CTA principal + countdown
  2. Problema: que problema resuelve la oferta
  3. Solucion: como la promocion resuelve el problema
  4. Beneficios: 3-6 beneficios con iconos
  5. Social proof: testimonios o logos de clientes
  6. Precio/oferta: precio original vs precio promocional
  7. QR code: compartir la promocion
  8. FAQ: preguntas frecuentes
  9. CTA final: formulario de contacto + WhatsApp
  10. Footer legal
- [ ] Cada seccion es un componente standalone reutilizable
- [ ] Se puede seleccionar como template al crear una promocion

**Tareas Tecnicas:**
- [ ] Crear 10 componentes de seccion standalone
- [ ] Registrar como template en el sistema de landing editor
- [ ] Tests: 6+ unit tests

---

#### US-MK-121: Chatbot visible en landing de promociones

**Como** visitante de una landing de promocion
**Quiero** poder chatear con el bot del cliente directamente en la landing
**Para** resolver dudas sobre la promocion sin salir de la pagina

**Criterios de Aceptacion:**
- [ ] Widget de chat flotante (esquina inferior derecha) visible en landing
- [ ] Se carga solo si el cliente tiene chatbot configurado en covacha-botia
- [ ] Chat se abre con mensaje de bienvenida contextual: "Hola! Tienes preguntas sobre {nombre_promocion}?"
- [ ] Chat puede responder preguntas sobre la promocion especifica
- [ ] Chat puede capturar datos de contacto (como alternativa al formulario)
- [ ] Responsive y no bloquea el contenido en mobile

**Tareas Tecnicas:**
- [ ] Integrar widget de chat de covacha-botia/mf-ia en landing
- [ ] Pasar contexto de la promocion al bot via parametros
- [ ] Tests: 5+ unit tests

---

#### US-MK-122: Chatbot entiende promociones activas

**Como** usuario del chatbot del cliente (web o WhatsApp)
**Quiero** que el bot conozca las promociones vigentes y pueda responder preguntas sobre ellas
**Para** obtener informacion de ofertas conversando con el bot

**Criterios de Aceptacion:**
- [ ] Knowledge base del bot se actualiza automaticamente con promociones activas
- [ ] Bot puede listar promociones vigentes cuando se le pregunta
- [ ] Bot puede dar detalles de una promocion especifica (precio, vigencia, beneficios)
- [ ] Bot puede enviar link a la landing de una promocion
- [ ] Cuando una promocion expira, se elimina de la knowledge base automaticamente
- [ ] Funciona tanto en web chat como en WhatsApp

**Tareas Tecnicas:**
- [ ] Crear sync de promociones → knowledge base en covacha-botia
- [ ] Endpoint de sincronizacion: `POST /api/v1/bots/{bot_id}/knowledge/sync-promotions`
- [ ] Webhook/cron que dispara sync cuando se crea/edita/expira una promocion
- [ ] Tests: 6+ unit tests

---

### EP-MK-028: Motor de Funnels de Venta Multi-Canal

---

#### US-MK-123: Modelo de datos de funnel de venta

**Como** arquitecto del sistema
**Quiero** un modelo de datos robusto para funnels de venta multi-canal
**Para** soportar configuraciones complejas de comunicacion automatizada

**Criterios de Aceptacion:**
- [ ] Modelo `SalesFunnel` con: id, client_id, name, description, channel (email/whatsapp), status, steps[], created_at, updated_at
- [ ] Modelo `FunnelStep` con: id, funnel_id, order, type (email/whatsapp/wait/condition), config{}, delay_minutes, schedule{timezone, hours_start, hours_end, days_of_week}, recurrence (once/daily/weekly/monthly/infinite)
- [ ] Modelo `FunnelExecution` con: id, funnel_id, lead_id, current_step, status, started_at, next_execution_at
- [ ] Modelo `FunnelChain` con: source_funnel_id, target_funnel_id, condition{}
- [ ] Persistencia en DynamoDB con PK=`CLIENT#{client_id}`, SK=`FUNNEL#{funnel_id}`
- [ ] GSI por status para queries eficientes

**Tareas Tecnicas:**
- [ ] Crear modelos en covacha-libs (Pydantic)
- [ ] Crear tabla/indices en DynamoDB
- [ ] Tests: 8+ unit tests

---

#### US-MK-124: Funnel por defecto de notificaciones

**Como** administrador de promociones
**Quiero** que cuando un cliente no tenga funnel personalizado, se use un funnel por defecto
**Para** garantizar que cada lead reciba al menos comunicacion basica

**Criterios de Aceptacion:**
- [ ] Al crear una promocion sin funnel asociado, se asigna funnel por defecto
- [ ] Funnel por defecto tiene 5 pasos:
  1. Email de bienvenida al lead (inmediato)
  2. Email de notificacion al equipo de ventas (inmediato)
  3. Email de follow-up al lead (3 dias despues)
  4. Email de informacion de valor (7 dias despues)
  5. Loop mensual: alternando entre nuevas promos, info de valor, lanzamientos
- [ ] Funnel por defecto se crea automaticamente al dar de alta un cliente
- [ ] Los templates de email del funnel por defecto son editables

**Tareas Tecnicas:**
- [ ] Crear servicio `DefaultFunnelService` en covacha-botia
- [ ] Templates de email por defecto en covacha-core
- [ ] Logica de auto-asignacion en endpoint de promociones
- [ ] Tests: 6+ unit tests

---

#### US-MK-125: Configuracion de funnel de email

**Como** administrador del cliente
**Quiero** configurar funnels de email con correo de salida, frecuencia, timezone y horarios
**Para** personalizar la comunicacion automatizada con mis leads

**Criterios de Aceptacion:**
- [ ] Seleccionar correo de salida (from address) configurado por el cliente
- [ ] Configurar frecuencia por step: minutos, horas, dias entre cada paso
- [ ] Seleccionar timezone del destinatario (dropdown con todas las zonas)
- [ ] Configurar ventana de horario de envio (ej: 9am-6pm)
- [ ] Configurar dias de la semana para envio (ej: L-V)
- [ ] Si el horario de envio cae fuera de ventana, postergar al proximo slot valido
- [ ] Preview del calendario de envio antes de activar

**Tareas Tecnicas:**
- [ ] Crear UI de configuracion en mf-marketing/mf-ia
- [ ] Logica de scheduling en covacha-botia
- [ ] Integracion con SES/SMTP para envio
- [ ] Tests: 8+ unit tests (timezone, horarios, dias, postergacion)

---

#### US-MK-126: Configuracion de funnel de WhatsApp

**Como** administrador del cliente con WhatsApp Business configurado
**Quiero** crear funnels de venta por WhatsApp usando templates aprobados
**Para** automatizar seguimiento de leads por el canal mas efectivo

**Criterios de Aceptacion:**
- [ ] Solo disponible si el cliente tiene WhatsApp Business configurado en covacha-botia
- [ ] Seleccionar templates de WhatsApp aprobados por Meta para cada step
- [ ] Variables de template se llenan automaticamente con datos del lead
- [ ] Configurar frecuencia, timezone y horarios (igual que email)
- [ ] Si el lead responde, el bot de WhatsApp lo atiende
- [ ] Si no hay templates aprobados, mostrar instruccion para aprobar en Meta
- [ ] Preview del mensaje antes de activar

**Tareas Tecnicas:**
- [ ] Reutilizar servicio de templates de WhatsApp existente
- [ ] Conectar con motor de funnels
- [ ] Handler de respuestas del lead en covacha-botia
- [ ] Tests: 8+ unit tests

---

#### US-MK-127: Recurrencia y bucle infinito de notificaciones

**Como** administrador del cliente
**Quiero** configurar pasos del funnel con recurrencia mensual infinita
**Para** mantener presencia continua ante el lead con contenido de valor

**Criterios de Aceptacion:**
- [ ] Opciones de recurrencia por step: una vez, semanal, mensual, infinito
- [ ] "Infinito" repite el step cada N dias/semanas/meses hasta que el lead se convierta o se desuscriba
- [ ] Contenido del loop puede ser: plantilla fija, rotacion de templates, contenido dinamico (nuevas promos)
- [ ] El lead puede desuscribirse con link en email o escribiendo "STOP" en WhatsApp
- [ ] Dashboard de leads en loop con metricas (aperturas, clicks, respuestas)
- [ ] Limite configurable de intentos maximos (ej: 12 meses)

**Tareas Tecnicas:**
- [ ] Logica de recurrencia en scheduler de covacha-botia
- [ ] Mecanismo de desuscripcion por canal
- [ ] Content rotation service
- [ ] Tests: 8+ unit tests (recurrencia, desuscripcion, limites, rotacion)

---

#### US-MK-128: Funnel chaining (conexion entre funnels)

**Como** administrador del cliente
**Quiero** que un funnel pueda enviar leads a otro funnel cuando se cumplan condiciones
**Para** crear flujos de conversion complejos (ej: funnel de pagina → funnel de promociones)

**Criterios de Aceptacion:**
- [ ] Configurar condicion de salida por step: abrio email, hizo click, respondio, compro, tiempo transcurrido
- [ ] Si condicion se cumple, el lead se mueve al funnel destino
- [ ] Solo se puede chain entre funnels del mismo canal (email→email, whatsapp→whatsapp)
- [ ] El lead mantiene su historial de funnels anteriores
- [ ] Vista visual de conexiones entre funnels (grafo simple)
- [ ] Proteccion contra loops infinitos (max 5 chains)

**Tareas Tecnicas:**
- [ ] Modelo `FunnelChain` en covacha-libs
- [ ] Logica de evaluacion de condiciones en covacha-botia
- [ ] UI de conexion de funnels en mf-ia
- [ ] Tests: 8+ unit tests (condiciones, chain, loops, historial)

---

#### US-MK-129: Selector de funnels en editor de landing

**Como** administrador de promociones
**Quiero** seleccionar el funnel de venta que se activa cuando un lead llena el formulario de la landing
**Para** asociar cada promocion con su flujo de conversion correspondiente

**Criterios de Aceptacion:**
- [ ] Dropdown en el editor de landing (paso "Landing" del wizard) con funnels disponibles del cliente
- [ ] Opcion "Funnel por defecto" siempre disponible
- [ ] Preview del funnel seleccionado (pasos, canal, frecuencia)
- [ ] Si no hay funnels personalizados, se usa el funnel por defecto automaticamente
- [ ] Al guardar la promocion, se asocia el funnel_id

**Tareas Tecnicas:**
- [ ] Agregar campo `funnel_id` al modelo de promocion
- [ ] Componente selector de funnel con preview
- [ ] Tests: 5+ unit tests

---

#### US-MK-130: Alta automatica en covacha-botia si no existe

**Como** administrador que quiere usar funnels de WhatsApp
**Quiero** que al activar funnels de WhatsApp, si el cliente no esta dado de alta en covacha-botia, se de de alta automaticamente
**Para** no tener que configurar manualmente el bot antes de usar funnels

**Criterios de Aceptacion:**
- [ ] Al seleccionar canal WhatsApp para funnel, verificar si el cliente existe en covacha-botia
- [ ] Si no existe, mostrar wizard simplificado de alta: numero WhatsApp + nombre del bot + idioma
- [ ] Crear cliente en covacha-botia via API
- [ ] Configurar bot basico con knowledge base de la promocion
- [ ] Mostrar instrucciones para verificar el numero con Meta (si aplica)

**Tareas Tecnicas:**
- [ ] Endpoint de verificacion y alta en covacha-botia
- [ ] Wizard simplificado en mf-marketing
- [ ] Tests: 6+ unit tests

---

#### US-MK-131: Presencia mensual automatizada ante el cliente

**Como** equipo de marketing del cliente
**Quiero** que el sistema envie automaticamente comunicaciones mensuales a los leads
**Para** mantener presencia de marca sin esfuerzo manual

**Criterios de Aceptacion:**
- [ ] Sistema genera contenido mensual automaticamente: nuevas promociones, info de valor, lanzamientos
- [ ] Calendario mensual editable con slots de contenido
- [ ] Templates predefinidos: "Nuevas ofertas del mes", "Tips de {industria}", "Lanzamiento: {producto}"
- [ ] Metricas de engagement por envio mensual
- [ ] El equipo puede aprobar/editar el contenido antes del envio

**Tareas Tecnicas:**
- [ ] Cron mensual en covacha-botia
- [ ] Generacion de contenido con LLM (usando configuracion IA del cliente)
- [ ] Workflow de aprobacion
- [ ] Tests: 6+ unit tests

---

#### US-MK-132: Dashboard de funnels y metricas de conversion

**Como** administrador del cliente
**Quiero** ver un dashboard con el rendimiento de todos los funnels activos
**Para** optimizar la estrategia de conversion y saber que funciona

**Criterios de Aceptacion:**
- [ ] Vista de todos los funnels del cliente con status y metricas
- [ ] Por funnel: leads entrantes, leads convertidos, tasa de conversion, tiempo promedio
- [ ] Por step: tasa de apertura (email), tasa de click, tasa de respuesta
- [ ] Grafico de embudo visual (funnel chart)
- [ ] Filtros por fecha, canal, promocion
- [ ] Export a CSV

**Tareas Tecnicas:**
- [ ] Componente dashboard en mf-marketing
- [ ] Endpoints de metricas en covacha-botia
- [ ] Tests: 6+ unit tests

---

### EP-MK-029: Integracion Chatbot + Promociones

---

#### US-MK-133: Sync automatico de promociones a knowledge base del bot

**Como** sistema
**Quiero** que las promociones activas se sincronicen automaticamente con la knowledge base del chatbot
**Para** que el bot siempre tenga informacion actualizada de ofertas

**Criterios de Aceptacion:**
- [ ] Al crear/editar/activar una promocion, se dispara sync a covacha-botia
- [ ] Al vencer una promocion, se elimina de la knowledge base
- [ ] Sync incluye: titulo, descripcion, precio, vigencia, link a landing, beneficios
- [ ] El sync es por cliente (cada bot tiene su propia knowledge base)
- [ ] Log de sincronizaciones exitosas/fallidas

**Tareas Tecnicas:**
- [ ] Webhook de covacha-core a covacha-botia en eventos de promocion
- [ ] Servicio de ingestion en knowledge base
- [ ] Tests: 6+ unit tests

---

#### US-MK-134: Widget de chat embebible en landing pages

**Como** desarrollador de landing pages
**Quiero** un widget de chat que se pueda integrar en cualquier landing page
**Para** ofrecer soporte conversacional contextual al visitante

**Criterios de Aceptacion:**
- [ ] Widget JavaScript embebible con `<script>` tag unico
- [ ] Configurable via atributos: `data-client-id`, `data-bot-id`, `data-context`
- [ ] Se carga lazy (no afecta performance de la landing)
- [ ] Aspecto visual configurable (colores, posicion, mensaje inicial)
- [ ] Funciona en mobile y desktop
- [ ] No requiere autenticacion del visitante

**Tareas Tecnicas:**
- [ ] Crear bundle standalone del widget de chat
- [ ] Endpoint de configuracion publica del widget
- [ ] Tests: 5+ unit tests

---

#### US-MK-135: Bot responde preguntas sobre promociones especificas

**Como** visitante en una landing de promocion
**Quiero** preguntarle al bot detalles sobre la promocion que estoy viendo
**Para** resolver dudas sin tener que leer toda la pagina o llenar el formulario

**Criterios de Aceptacion:**
- [ ] Bot recibe contexto de la promocion actual (slug, titulo) al abrir chat en landing
- [ ] Bot responde preguntas sobre: precio, vigencia, beneficios, condiciones
- [ ] Bot puede capturar datos de contacto y crear lead (alternativa al formulario)
- [ ] Bot sugiere CTA: "Quieres que te contactemos? Dame tu nombre y email."
- [ ] Si el bot no puede responder, escala a humano o muestra formulario

**Tareas Tecnicas:**
- [ ] Context injection en sesion de chat
- [ ] Prompts especializados para promociones
- [ ] Integracion con endpoint de leads
- [ ] Tests: 6+ unit tests

---

#### US-MK-136: Bot lista promociones vigentes por chat

**Como** usuario del chatbot (web o WhatsApp)
**Quiero** preguntar "Que promociones tienen?" y recibir la lista de ofertas vigentes
**Para** descubrir ofertas conversando naturalmente

**Criterios de Aceptacion:**
- [ ] Bot reconoce intenciones: "promociones", "ofertas", "descuentos", "que hay nuevo"
- [ ] Responde con lista formateada: nombre + precio + vigencia + link
- [ ] En WhatsApp: usa formato de lista interactiva si disponible
- [ ] En web chat: muestra cards clickeables
- [ ] Solo muestra promociones vigentes (misma logica que endpoint publico)

**Tareas Tecnicas:**
- [ ] Intent handler para promociones en covacha-botia
- [ ] Formatters por canal (WhatsApp vs web)
- [ ] Tests: 5+ unit tests

---

#### US-MK-137: Metricas de interaccion chatbot + promociones

**Como** administrador del cliente
**Quiero** ver metricas de como los visitantes interactuan con el bot respecto a promociones
**Para** entender si el bot ayuda a convertir leads

**Criterios de Aceptacion:**
- [ ] Metricas: preguntas sobre promociones, leads capturados via bot, tasa de conversion bot vs formulario
- [ ] Vista en dashboard de promociones
- [ ] Filtro por promocion especifica
- [ ] Comparativa: leads de formulario vs leads de bot

**Tareas Tecnicas:**
- [ ] Tracking de eventos en covacha-botia
- [ ] Endpoints de metricas
- [ ] Componente de metricas en mf-marketing
- [ ] Tests: 4+ unit tests

---

### EP-MK-030: Tests y Cobertura Completa Promociones

---

#### US-MK-138: Tests unitarios completos de backend (covacha-core)

**Como** equipo de desarrollo
**Quiero** cobertura >= 98% en todos los endpoints y servicios de promociones y funnels
**Para** garantizar calidad y detectar regresiones

**Criterios de Aceptacion:**
- [ ] Tests unitarios para todos los endpoints nuevos (promociones publicas, leads, funnels)
- [ ] Tests para servicios de vigencia, QR generation, SEO dinamico
- [ ] Tests para integracion con covacha-botia (mocks)
- [ ] Coverage >= 98% en modulos de promociones
- [ ] CI/CD verde antes de merge

**Tareas Tecnicas:**
- [ ] pytest con fixtures y mocks
- [ ] coverage report integrado en CI
- [ ] Tests: 50+ unit tests

---

#### US-MK-139: Tests unitarios completos de frontend (mf-marketing)

**Como** equipo de desarrollo
**Quiero** cobertura >= 90% en todos los componentes de promociones, landing y funnels
**Para** garantizar que la UI funcione correctamente

**Criterios de Aceptacion:**
- [ ] Tests para todos los componentes nuevos (listado, landing, formulario, QR, countdown, funnels)
- [ ] Tests para servicios y adapters nuevos
- [ ] Tests para routing y guards
- [ ] Coverage >= 90% en modulos de promociones
- [ ] Karma + Jasmine

**Tareas Tecnicas:**
- [ ] Test suites por componente
- [ ] Mocks de servicios HTTP
- [ ] Tests: 80+ unit tests

---

#### US-MK-140: Tests E2E de flujo completo de promociones

**Como** QA
**Quiero** tests end-to-end que validen el flujo completo: crear promocion → publicar → visitar landing → enviar formulario → lead en CRM → funnel activado
**Para** garantizar que todo el flujo funciona de punta a punta

**Criterios de Aceptacion:**
- [ ] E2E: Crear promocion con wizard → verificar en listado publico
- [ ] E2E: Visitar landing → formulario → lead creado en CRM
- [ ] E2E: Promocion vencida → mensaje de no disponible
- [ ] E2E: QR code → scan → landing carga correctamente
- [ ] E2E: Chat en landing → bot responde sobre promocion
- [ ] E2E: Funnel se activa → emails programados
- [ ] Playwright con CI integration

**Tareas Tecnicas:**
- [ ] Configurar Playwright para flujo de promociones
- [ ] Fixtures de datos de prueba
- [ ] Tests: 10+ E2E scenarios

---

## Estrategia de Testing

### Backend (covacha-core + covacha-botia)

| Tipo | Framework | Coverage Min | Enfoque |
|------|-----------|-------------|---------|
| Unitarios | pytest | 98% | Servicios, endpoints, modelos |
| Integracion | pytest + mocks | 95% | API calls entre servicios |
| E2E | pytest + requests | N/A | Flujos completos |

### Frontend (mf-marketing + mf-ia)

| Tipo | Framework | Coverage Min | Enfoque |
|------|-----------|-------------|---------|
| Unitarios | Karma + Jasmine | 90% | Componentes, servicios, pipes |
| E2E | Playwright | N/A | Flujos de usuario completos |

---

## Roadmap

### Sprint 1 (6 dias): EP-MK-026 - Promociones desde BD
- Dia 1-2: Endpoint publico + filtrado vigencia
- Dia 3-4: Componente listado + herencia estilo
- Dia 5: Routing ingles + pagina no disponible
- Dia 6: SEO + tests

### Sprint 2 (6 dias): EP-MK-027 - Landing de Ventas
- Dia 1-2: Layout dedicado + template sales page
- Dia 3: QR multidimensional
- Dia 4: Formulario contacto + CRM
- Dia 5: Countdown + chatbot en landing
- Dia 6: Tests

### Sprint 3 (6 dias): EP-MK-028 - Funnels (parte 1)
- Dia 1-2: Modelo de datos + funnel por defecto
- Dia 3-4: Configuracion email + WhatsApp
- Dia 5: Recurrencia + bucle infinito
- Dia 6: Tests

### Sprint 4 (6 dias): EP-MK-028 - Funnels (parte 2) + EP-MK-029 Chatbot
- Dia 1-2: Funnel chaining + selector en landing
- Dia 3: Alta auto covacha-botia + presencia mensual
- Dia 4: Dashboard metricas
- Dia 5: Chatbot + promociones
- Dia 6: Tests E2E

---

## Grafo de Dependencias

```
EP-MK-005 (Landing Pages - COMPLETADA)
    │
    ▼
EP-MK-026 (Promociones desde BD)
    │
    ├──► EP-MK-027 (Landing de Ventas)
    │       │
    │       ├──► EP-MK-029 (Chatbot + Promociones)
    │       │       │
    │       │       └──► EP-IA-001 (Orquestador Agentes)
    │       │
    │       └──► EP-MK-028 (Funnels de Venta)
    │               │
    │               ├──► EP-IA-012 (Motor Funnels en covacha-botia)
    │               ├──► EP-IA-013 (Canal Email)
    │               └──► EP-IA-014 (Canal WhatsApp)
    │
    └──► EP-MK-030 (Tests Completos)
```

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|------------|
| Templates WhatsApp no aprobados por Meta | Alta | Bloquea funnels WhatsApp | Proveer templates pre-aprobados genéricos |
| Performance con muchas promociones activas | Baja | Lentitud en listado | Cache de 5min + paginacion |
| SPAM en funnels de email (recurrencia infinita) | Media | Deliverability afectada | Rate limiting + opt-out obligatorio |
| Chatbot no entiende contexto de promocion | Media | UX pobre | Fallback a formulario + escalacion humana |
| Complejidad de funnel chaining | Media | Bugs dificiles | Limite de 5 chains + tests exhaustivos |
| Timezone incorrecta en envios | Baja | Emails a horas inadecuadas | Validacion de timezone + preview de calendario |
