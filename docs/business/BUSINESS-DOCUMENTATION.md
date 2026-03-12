# Documentacion de Negocio - Ecosistema SuperPago/BaatDigital

**Fecha de generacion**: 2026-03-10
**Version**: 1.0
**Generado por**: Product Owner Validator
**Ultima actualizacion**: Automatica desde archivos de epicas en `covacha-projects/products/`

---

## Resumen Ejecutivo

El ecosistema SuperPago/BaatDigital es una plataforma multi-tenant que integra tres productos principales:

| Producto | Epicas | Completadas | En Progreso | Pendientes | User Stories |
|----------|--------|-------------|-------------|------------|--------------|
| **Marketing Digital** (mf-marketing) | 30 | 18 | 5 | 7 | ~140 |
| **SuperPago SPEI** (mf-sp) | 20 | 19 | 0 | 1 | ~84 |
| **Inventario** (mf-inventory) | 12 | 0 | 0 | 12 | 65 |
| **Total** | **62** | **37** | **5** | **20** | **~289** |

**Stack tecnologico compartido:**
- **Frontend**: Angular 21, Native Federation (micro-frontends), TypeScript strict, Signals + RxJS
- **Backend**: Python 3.9+, Flask, DynamoDB (single-table design), AWS (Lambda, SQS, SES, S3, CloudFront)
- **IA**: OpenAI, Anthropic/Claude, Google Gemini, Meta AI/LLama (multi-provider)
- **Integraciones**: Meta Graph API (FB/IG), WhatsApp Business API, Google Ads, Monato Fincore (SPEI)

**Arquitectura**: Micro-frontends con Shell (mf-core) + remotes independientes. Backend orientado a servicios con patron hexagonal. DynamoDB single-table con GSIs. Deploy via GitHub Actions a S3+CloudFront (frontend) y EC2 via CodeDeploy (backend).

---

## 1. Producto: Marketing Digital (mf-marketing)

### 1.1 Vision de Negocio

El modulo de Marketing Digital resuelve el problema de las agencias digitales que operan manualmente: crean calendarios editoriales en hojas de calculo, publican en redes sociales una por una, generan reportes mensuales en PowerPoint, y coordinan aprobaciones por email. **mf-marketing automatiza el ciclo completo de operaciones de agencia digital**, desde la planificacion de contenido hasta la entrega de reportes al cliente final.

**Propuesta de valor:**
- Reduccion de 4-8 horas a minutos en la planificacion de contenido mensual por cliente
- Publicacion automatizada y monitoreo 24/7 de redes sociales
- Reportes profesionales auto-generados con metricas reales
- Sistema de aprobaciones integrado que elimina el email como herramienta de coordinacion
- Generacion de contenido con IA multi-proveedor (OpenAI, Claude, Gemini, Meta AI/LLama)
- Landing pages y funnels de venta integrados con CRM

**Usuarios objetivo:**
- Account Managers de agencias digitales
- Community Managers
- Directores de marketing
- Clientes finales (reciben reportes y aprueban contenido)

### 1.2 Modulos Implementados

---

#### EP-MK-001: Gestion de Clientes de Agencia
**Estado**: COMPLETADO
**Complejidad**: L
**Valor de Negocio**: Permite a la agencia gestionar su cartera de clientes con datos de contacto, estados (ACTIVE, INACTIVE, ONBOARDING), y configuracion por cliente. Es la base sobre la que operan todas las demas funcionalidades.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: CRUD completo de clientes con wizard de 5 pasos (datos basicos, contactos, redes sociales, configuracion, confirmacion)
2. **UX/UI**: Listado con filtros por estado y busqueda, cards de resumen, navegacion fluida entre wizard steps
3. **Rendimiento**: Listado paginado server-side, lazy-loading del componente de detalle
4. **Seguridad**: Clientes filtrados por organization_id del token, validacion de permisos por rol
5. **Accesibilidad**: Formularios con labels ARIA, navegacion por teclado en wizard
6. **Integracion**: Conexion con SharedStateService para leer organizacion activa del Shell
7. **Error Handling**: Validaciones reactivas en formularios, mensajes de error descriptivos, retry en fallos de red
8. **Persistencia**: DynamoDB con PK `ORG#{orgId}` SK `CLIENT#{clientId}`, GSI por estado
9. **Multi-Tenant**: Datos aislados por organizacion, soporte multi-tenant via tenant_id en headers
10. **Observabilidad**: Logs de operaciones CRUD, metricas de clientes por organizacion

**E2E Test Coverage**: `clients.spec.ts`, `client-detail.spec.ts`, `client-workspace.spec.ts`

---

#### EP-MK-002: Social Media Management
**Estado**: COMPLETADO
**Complejidad**: XL
**Valor de Negocio**: Centraliza la gestion de redes sociales (Facebook e Instagram) en una sola plataforma: creacion de posts, programacion, publicacion automatica, y sincronizacion de cuentas via Meta Business OAuth.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: CRUD de posts con tipos IMAGE, VIDEO, CAROUSEL, REEL, STORY; workflow DRAFT->PENDING_REVIEW->APPROVED->SCHEDULED->PUBLISHED
2. **UX/UI**: Editor de posts con preview por plataforma, selector de fecha/hora, hashtag suggestions
3. **Rendimiento**: Carga optimista de posts, imagenes lazy-loaded, paginacion cursor-based
4. **Seguridad**: OAuth2 con Meta Business API, tokens almacenados encriptados, scopes minimos
5. **Accesibilidad**: Alt text obligatorio para imagenes, previews con contraste adecuado
6. **Integracion**: Conexion Meta Graph API v21.0, sincronizacion bidireccional de posts publicados
7. **Error Handling**: Reintentos automaticos para publicacion fallida, notificacion al usuario de errores de API
8. **Persistencia**: Posts en DynamoDB con GSI por estado y fecha de programacion
9. **Multi-Tenant**: Cuentas sociales aisladas por organizacion, posts por cliente
10. **Observabilidad**: Dashboard de actividad social, metricas de publicacion exitosa vs fallida

**E2E Test Coverage**: `calendar.spec.ts`, `analytics.spec.ts`

---

#### EP-MK-003: Estrategias de Marketing
**Estado**: COMPLETADO
**Complejidad**: L
**Valor de Negocio**: Permite definir estrategias de marketing por cliente con objetivos, KPIs, plan de contenido, y tracking de progreso. Es el marco estrategico que guia las operaciones diarias de la agencia.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Wizard de creacion de estrategia con pasos: briefing, objetivos, KPIs, canales, timeline
2. **UX/UI**: Vista de detalle con tabs (overview, objectives, KPIs, content plan, reports), dashboard de estrategia
3. **Rendimiento**: Dashboard con graficas ECharts lazy-loaded, datos en cache con TTL
4. **Seguridad**: Solo Account Managers y admins pueden crear/editar estrategias
5. **Accesibilidad**: Graficas con tooltips descriptivos, tablas con headers semanticos
6. **Integracion**: KPIs alimentados desde metricas reales de social media y ads
7. **Error Handling**: Guardado parcial de wizard, recuperacion de estado en navegacion accidental
8. **Persistencia**: Estrategia persiste en localStorage como `mf-marketing:active-strategy`
9. **Multi-Tenant**: Estrategias aisladas por organizacion y cliente
10. **Observabilidad**: Historial de cambios en estrategia, alertas cuando KPIs no alcanzan meta

**E2E Test Coverage**: `strategies.spec.ts`, `strategy-builder.spec.ts`, `strategy-detail.spec.ts`, `strategy-dashboard.spec.ts`

---

#### EP-MK-004: Landing Pages y Editor Visual
**Estado**: COMPLETADO
**Complejidad**: XL
**Valor de Negocio**: Editor visual drag-and-drop para crear landing pages de conversion sin necesidad de desarrolladores. Incluye preview responsivo, auto-guardado, historial undo/redo, SEO integrado y landing pages publicas accesibles por slug.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Editor DnD con secciones configurables (hero, beneficios, testimonios, CTA, formularios, footer)
2. **UX/UI**: Preview en tiempo real desktop/mobile, inline editing, toolbar de estilos
3. **Rendimiento**: Auto-guardado cada 30s con debounce, optimizacion de imagenes (WebP, srcset, blur placeholders)
4. **Seguridad**: Sanitizacion de HTML inyectado, CSP headers en landing publica
5. **Accesibilidad**: Estructura semantica generada (H1-H6), alt text en imagenes, contraste WCAG AA
6. **Integracion**: SEO dinamico (meta tags, Open Graph, Schema.org JSON-LD), WhatsApp boton flotante configurable
7. **Error Handling**: Historial undo/redo con keyboard shortcuts (Ctrl+Z/Y), recuperacion de sesion
8. **Persistencia**: Estado del editor en signals, secciones en DynamoDB, assets en S3
9. **Multi-Tenant**: Landing pages con slug unico por organizacion, temas heredados del brand kit
10. **Observabilidad**: Tracking de vistas y conversiones por landing page

**E2E Test Coverage**: `landing-editor.spec.ts`, `promotions-list.spec.ts`, `public-landing.spec.ts`

---

#### EP-MK-005: Brand Kit
**Estado**: COMPLETADO
**Complejidad**: M
**Valor de Negocio**: Centraliza la identidad visual de cada cliente (logos, colores, tipografias, imagenes) para garantizar consistencia de marca en todos los canales. Se integra con el editor de landing pages y la generacion de contenido IA.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: CRUD de logos (variantes), paleta de colores, tipografias, biblioteca de imagenes e iconos
2. **UX/UI**: Color picker, previews de tipografia, galeria de imagenes con zoom
3. **Rendimiento**: Imagenes comprimidas y cached en S3/CloudFront, thumbnails generados
4. **Seguridad**: Upload validado (solo formatos imagen, tamano maximo configurable)
5. **Accesibilidad**: Verificacion de contraste de colores del brand kit (WCAG AA)
6. **Integracion**: Brand kit inyectado en editor de landing, en generacion de contenido IA, y en reportes
7. **Error Handling**: Upload con retry, validacion de formato antes de subir
8. **Persistencia**: Brand kit en DynamoDB por cliente, assets en S3 con versionado
9. **Multi-Tenant**: Brand kit aislado por organizacion y cliente
10. **Observabilidad**: Historial de cambios en brand kit

**E2E Test Coverage**: `brand-kit.spec.ts`

---

#### EP-MK-006: Landing Editor Avanzado (Fases 1-5)
**Estado**: COMPLETADO
**Complejidad**: XL
**Valor de Negocio**: Extension del editor visual con secciones avanzadas, templates pre-diseñados, y optimizaciones de conversion. Incluye formularios de contacto conectados al CRM y boton de WhatsApp configurable.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Templates de landing pre-diseñados por industria, secciones avanzadas (pricing, FAQ, equipo)
2. **UX/UI**: Galeria de templates con preview, personalizacion por arrastrar secciones
3. **Rendimiento**: Templates cargados lazy, rendering optimizado con OnPush y signals
4. **Seguridad**: Formularios con captcha, sanitizacion de inputs del visitante
5. **Accesibilidad**: Templates cumplen WCAG AA por defecto, estructura semantica correcta
6. **Integracion**: Formulario de contacto envia lead a covacha-core CRM, WhatsApp pre-llenado
7. **Error Handling**: Fallback si formulario falla (mensaje de error amigable, retry)
8. **Persistencia**: Templates en DynamoDB, configuracion de secciones por landing
9. **Multi-Tenant**: Templates compartidos globales + templates custom por organizacion
10. **Observabilidad**: Metricas de conversion por landing (form submits, clicks WhatsApp)

**E2E Test Coverage**: `landing-editor.spec.ts`

---

#### EP-MK-007: Campaign Builder (Facebook Ads)
**Estado**: COMPLETADO
**Complejidad**: XL
**Valor de Negocio**: Wizard de 4 pasos para crear campanas de Facebook Ads directamente desde la plataforma: Campaign, AdSet, Ad, Review. Elimina la necesidad de usar Meta Ads Manager para campanas basicas.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Wizard de 4 pasos (Campaign→AdSet→Ad→Review), publicacion a Facebook Ads Manager
2. **UX/UI**: Formularios guiados con validacion en cada paso, preview del anuncio, resumen antes de publicar
3. **Rendimiento**: Carga de Ad Accounts asincrona, cache de audiencias y creativos
4. **Seguridad**: Tokens de Meta Ads con scopes minimos, no se almacenan datos de pago
5. **Accesibilidad**: Wizard navegable por teclado, labels descriptivos para cada campo
6. **Integracion**: Facebook Marketing API para CRUD de campanas, AdSets, Ads; insights de rendimiento
7. **Error Handling**: Validacion pre-publicacion, rollback si la publicacion falla parcialmente
8. **Persistencia**: Campanas en DynamoDB con referencia a IDs de Meta, historial de cambios
9. **Multi-Tenant**: Ad Accounts aisladas por organizacion y cliente
10. **Observabilidad**: Dashboard de metricas de campanas (ROAS, CPA, CTR, impressions)

**E2E Test Coverage**: `campaign-builder.spec.ts`

---

#### EP-MK-008: Brand Kit Completo
**Estado**: COMPLETADO
**Complejidad**: M
**Valor de Negocio**: Extension del brand kit con editor de templates de email, variaciones de logos para distintas plataformas, y paleta de colores avanzada con verificacion de contraste.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Editor de templates de email con brand kit integrado, variaciones de logo por plataforma
2. **UX/UI**: Preview de templates en multiples dispositivos, editor WYSIWYG para emails
3. **Rendimiento**: Templates renderizados server-side para preview, imagenes optimizadas
4. **Seguridad**: Templates sanitizados contra XSS, imagenes validadas
5. **Accesibilidad**: Templates de email accesibles (alt text, semantic HTML, contraste)
6. **Integracion**: Brand kit se consume en generacion de reportes PDF y campanas de email
7. **Error Handling**: Validacion de formato de imagenes, limites de tamano con mensaje claro
8. **Persistencia**: Templates de email en DynamoDB, assets en S3
9. **Multi-Tenant**: Templates aislados por organizacion y cliente
10. **Observabilidad**: Uso de brand kit en otros modulos (cuantos reportes/emails lo consumen)

**E2E Test Coverage**: `brand-kit.spec.ts`

---

#### EP-MK-009: Dashboards Ejecutivo y Comparativo
**Estado**: COMPLETADO
**Complejidad**: L
**Valor de Negocio**: Dashboards ejecutivos que consolidan metricas de todos los clientes de la agencia en una sola vista. Permite al director de marketing ver el estado de la agencia completa y comparar rendimiento entre estrategias y clientes.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Dashboard ejecutivo multi-cliente con KPIs globales, dashboard comparativo de estrategias
2. **UX/UI**: Graficas interactivas con ECharts, filtros por periodo/cliente/plataforma, responsive
3. **Rendimiento**: Datos agregados server-side, cache con TTL de 5 minutos, graficas lazy-loaded
4. **Seguridad**: Solo roles admin y Account Manager ven el dashboard ejecutivo
5. **Accesibilidad**: Graficas con tooltips descriptivos, tablas de datos alternativas
6. **Integracion**: Consolida datos de ClientManagementService, StrategyManagementService, SocialStatsService, ReportManagementService
7. **Error Handling**: Graceful degradation si un servicio falla (muestra datos parciales)
8. **Persistencia**: Datos agregados cacheados en DynamoDB con TTL
9. **Multi-Tenant**: Datos aislados por organizacion
10. **Observabilidad**: Tiempo de carga del dashboard, servicios lentos identificados

**E2E Test Coverage**: `executive-dashboard.spec.ts`

---

#### EP-MK-010: Calendario de Publicaciones
**Estado**: COMPLETADO
**Complejidad**: M
**Valor de Negocio**: Vista de calendario mensual/semanal de todas las publicaciones programadas, aprobadas y publicadas. Permite coordinar el contenido entre clientes y plataformas.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Vista mensual y semanal, arrastrar posts para reprogramar, filtros por cliente/plataforma/estado
2. **UX/UI**: Calendario con color-coding por estado, tooltips con preview del post, drag-and-drop
3. **Rendimiento**: Solo carga posts del mes visible, paginacion por rango de fechas
4. **Seguridad**: Solo usuarios con permiso pueden reprogramar posts
5. **Accesibilidad**: Calendario navegable por teclado, labels ARIA para cada dia
6. **Integracion**: Sincronizado con SocialMediaService, actualiza posts al arrastrar
7. **Error Handling**: Confirmacion antes de reprogramar, undo disponible
8. **Persistencia**: Posts con campo scheduled_at indexado en GSI
9. **Multi-Tenant**: Calendario filtrado por organizacion y opcionalmente por cliente
10. **Observabilidad**: Metricas de cumplimiento del calendario (posts programados vs publicados)

**E2E Test Coverage**: `calendar.spec.ts`

---

#### EP-MK-011: Templates WhatsApp y Email
**Estado**: COMPLETADO
**Complejidad**: M
**Valor de Negocio**: Gestion centralizada de templates de WhatsApp (catalogados por Meta) y templates de email para campanas y funnels.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: CRUD de templates WhatsApp con sincronizacion del catalogo Meta, templates de email con editor visual
2. **UX/UI**: Galeria de templates con preview, filtros por categoria y estado de aprobacion
3. **Rendimiento**: Templates cacheados localmente, sincronizacion bajo demanda con Meta
4. **Seguridad**: Templates WhatsApp solo los aprobados por Meta pueden enviarse
5. **Accesibilidad**: Previews con texto alternativo, formularios accesibles
6. **Integracion**: Templates consumidos por agentes IA de WhatsApp y Email Marketing
7. **Error Handling**: Notificacion cuando un template es rechazado por Meta, sugerencias de correccion
8. **Persistencia**: Templates en DynamoDB con sincronizacion periodica desde Meta catalog
9. **Multi-Tenant**: Templates aislados por organizacion y proyecto
10. **Observabilidad**: Tasa de aprobacion de templates, templates mas usados

**E2E Test Coverage**: `templates.spec.ts`, `subscriptions.spec.ts`

---

#### EP-MK-012: Analytics BI de Estrategias
**Estado**: COMPLETADO
**Complejidad**: L
**Valor de Negocio**: Business Intelligence aplicado a estrategias de marketing: metricas detalladas, tendencias, analisis de contenido, y ROI por canal.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Dashboard BI por estrategia con metricas de engagement, reach, conversiones por canal
2. **UX/UI**: Graficas interactivas con drill-down, tablas pivotables, exportacion
3. **Rendimiento**: Calculo de metricas en background (SQS), cache de resultados
4. **Seguridad**: Datos sensibles de metricas solo visibles para roles autorizados
5. **Accesibilidad**: Graficas con datos tabulares alternativos
6. **Integracion**: Datos de Facebook Insights, Instagram Insights, Google Analytics
7. **Error Handling**: Metricas parciales si una fuente falla, indicador de datos incompletos
8. **Persistencia**: Metricas historicas en DynamoDB para comparativas
9. **Multi-Tenant**: BI aislado por organizacion, estrategia y cliente
10. **Observabilidad**: Frecuencia de uso del BI, queries lentas identificadas

**E2E Test Coverage**: `analytics.spec.ts`

---

#### EP-MK-013: AI Config Multi-Provider
**Estado**: COMPLETADO
**Complejidad**: L
**Valor de Negocio**: Permite configurar multiples proveedores de IA por cliente (OpenAI, Claude, Gemini) con API keys, parametros de generacion, y quotas. Base para todos los agentes IA.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Wizard de configuracion con seleccion de provider, API key, parametros (temperatura, max_tokens)
2. **UX/UI**: Selector de provider con logos, formulario de API key con validacion, test de conexion inline
3. **Rendimiento**: Validacion de API key asincrona, cache de configuracion
4. **Seguridad**: API keys encriptadas en DynamoDB, nunca expuestas en frontend despues de guardar
5. **Accesibilidad**: Formularios con labels claros, feedback de validacion accesible
6. **Integracion**: Configuracion consumida por todos los agentes IA (EP-MK-014 a EP-MK-023)
7. **Error Handling**: Validacion de API key antes de guardar, fallback a provider por defecto
8. **Persistencia**: Config en DynamoDB con PK por organizacion y cliente
9. **Multi-Tenant**: Configuracion IA aislada por organizacion y cliente
10. **Observabilidad**: Uso de tokens por provider, alertas cuando quota se acerca al limite

**E2E Test Coverage**: `settings.spec.ts`

---

#### EP-MK-014: Agente de Content Planning y Generacion
**Estado**: PENDIENTE (Planificacion)
**Complejidad**: XL
**Valor de Negocio**: Automatiza la creacion de calendarios editoriales completos con IA. Reduce de 4-8 horas a minutos la planificacion mensual de contenido por cliente. Genera copywriting, hashtags y horarios optimos basados en datos reales.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Genera calendario editorial mensual con 20-30 posts distribuidos por plataforma (FB, IG, TikTok, LinkedIn)
2. **UX/UI**: Interfaz de solicitud simple, preview del calendario generado editable antes de confirmar
3. **Rendimiento**: Generacion asincrona via SQS (<60s), indicador de progreso
4. **Seguridad**: Respeta quotas de IA del cliente (EP-MK-013), no expone datos entre clientes
5. **Accesibilidad**: Calendario generado con estructura semantica, posts con alt text sugerido
6. **Integracion**: Consume estrategia activa del cliente, metricas historicas de posts, brand kit
7. **Error Handling**: Si el provider IA falla, intenta fallback provider; notifica si no puede generar
8. **Persistencia**: Calendarios generados en DynamoDB con PK `CONTENT#{clientId}` SK `PLAN#{yearMonth}`
9. **Multi-Tenant**: Generacion aislada por organizacion y cliente
10. **Observabilidad**: Metricas de generacion (tiempo, tokens usados, posts generados vs aprobados)

**E2E Test Coverage**: PENDIENTE

---

#### EP-MK-015: Agente de Social Media Management
**Estado**: PENDIENTE (Planificacion)
**Complejidad**: XL
**Valor de Negocio**: Community Manager virtual 24/7. Publica posts programados, monitorea comentarios y menciones, genera respuestas automaticas inteligentes, y detecta crisis de reputacion.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Publicacion automatica de posts programados, monitoreo de comentarios/menciones cada 5 min, respuestas automaticas
2. **UX/UI**: Dashboard de actividad del agente con timeline de acciones, alertas de crisis prominentes
3. **Rendimiento**: Monitoreo asincrono via SQS, procesamiento batch de comentarios
4. **Seguridad**: Respuestas automaticas solo en comentarios positivos/neutrales; escala a humano los negativos (sentimiento < 0.3)
5. **Accesibilidad**: Dashboard accesible, notificaciones con descripcion textual
6. **Integracion**: Facebook Graph API (comentarios, menciones, publicacion), Instagram API
7. **Error Handling**: Si publicacion falla, reintenta 3 veces con backoff; si monitoreo falla, alerta sin perder datos
8. **Persistencia**: Acciones del agente en DynamoDB con prefijo `AGENT#`, historial de respuestas
9. **Multi-Tenant**: Agente configurado por organizacion y cliente
10. **Observabilidad**: Metricas: tiempo de respuesta promedio, comentarios procesados, crisis detectadas

**E2E Test Coverage**: PENDIENTE

---

#### EP-MK-016: Agente de Campanas Publicitarias (FB/Google Ads)
**Estado**: PENDIENTE (Planificacion)
**Complejidad**: XL
**Valor de Negocio**: Automatiza la creacion y optimizacion de campanas publicitarias con IA: audiencias sugeridas, copys A/B, optimizacion de bids, y reportes de ROAS.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Genera audiencias sugeridas, crea copys A/B, optimiza bids cada 6h, pausa campanas de bajo rendimiento
2. **UX/UI**: Dashboard de ROAS por campana/canal/periodo, recomendaciones visuales
3. **Rendimiento**: Optimizacion de bids en background (SQS), metricas cacheadas
4. **Seguridad**: Tokens de Facebook Marketing API y Google Ads con scopes minimos
5. **Accesibilidad**: Reportes con tablas semanticas, graficas con datos alternativos
6. **Integracion**: Facebook Marketing API, Google Ads API, AdAccountManagementService
7. **Error Handling**: Notificacion antes de pausar campana, confirmacion para acciones destructivas
8. **Persistencia**: Historial de optimizaciones en DynamoDB, metricas historicas
9. **Multi-Tenant**: Cuentas publicitarias aisladas por organizacion y cliente
10. **Observabilidad**: ROAS global, CPA promedio, campanas pausadas automaticamente

**E2E Test Coverage**: PENDIENTE

---

#### EP-MK-017: Agente de Landing Page Generator
**Estado**: PENDIENTE (Planificacion)
**Complejidad**: L
**Valor de Negocio**: Genera landing pages completas con IA desde un briefing de texto. Reduce el tiempo de creacion de landing pages de 2-3 dias a minutos.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Genera landing completa desde briefing (<200 palabras), compatible con editor DnD existente
2. **UX/UI**: Formulario de briefing simple, preview de la landing generada, opcion de editar antes de publicar
3. **Rendimiento**: Generacion asincrona, estructura de landing pre-optimizada para carga rapida
4. **Seguridad**: Contenido generado sanitizado, no inyecta scripts maliciosos
5. **Accesibilidad**: Landing generada cumple WCAG AA por defecto (estructura semantica, contraste)
6. **Integracion**: Copywriting alineado al brand kit, meta tags SEO auto-generados, variantes A/B de CTAs
7. **Error Handling**: Si generacion falla, ofrece template por defecto como fallback
8. **Persistencia**: Landings generadas en DynamoDB, variantes A/B trackeadas
9. **Multi-Tenant**: Generacion aislada por organizacion y cliente
10. **Observabilidad**: Metricas de conversion de landings generadas por IA vs manuales

**E2E Test Coverage**: PENDIENTE

---

#### EP-MK-018: Agente de Email Marketing
**Estado**: PENDIENTE (Planificacion)
**Complejidad**: L
**Valor de Negocio**: Automatiza campanas de email completas: generacion de templates, personalizacion por segmento, programacion, A/B testing de subject lines, y monitoreo de metricas (open rate, click rate).

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Genera templates de email responsivos, personaliza por segmento, programa envios, A/B testing de subjects
2. **UX/UI**: Preview de email en multiples dispositivos, editor de segmentos, dashboard de metricas
3. **Rendimiento**: Envio masivo via AWS SES con rate limiting, tracking asincrono
4. **Seguridad**: CAN-SPAM compliance (unsubscribe link, direccion fisica), validacion de listas
5. **Accesibilidad**: Templates de email accesibles (semantic HTML, alt text, contraste)
6. **Integracion**: AWS SES para envio, brand kit para estilos, CRM para segmentacion
7. **Error Handling**: Bounces y complaints manejados automaticamente, listas limpias
8. **Persistencia**: Campanas y metricas en DynamoDB, tracking de aperturas/clicks
9. **Multi-Tenant**: Campanas aisladas por organizacion y cliente
10. **Observabilidad**: Open rate, click rate, bounce rate, unsubscribe rate por campana

**E2E Test Coverage**: PENDIENTE

---

#### EP-MK-019: Agente de WhatsApp Marketing (Secuencias)
**Estado**: PENDIENTE (Planificacion)
**Complejidad**: L
**Valor de Negocio**: Automatiza secuencias de WhatsApp Business para nurturing de leads: follow-up automatico, segmentacion de contactos, y tracking de conversiones por paso del funnel.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Crea secuencias con triggers (formulario, compra, inactividad), usa templates aprobados por Meta
2. **UX/UI**: Builder visual de secuencias con nodos arrastrables, metricas por paso
3. **Rendimiento**: Ejecucion de secuencias via SQS, respeta ventana de 24h de WhatsApp
4. **Seguridad**: Solo templates aprobados por Meta, opt-out respetado, datos GDPR-compliant
5. **Accesibilidad**: Builder accesible por teclado, descripciones de nodos
6. **Integracion**: WhatsApp Business API, templates existentes, covacha-webhook para respuestas
7. **Error Handling**: Retry si WhatsApp falla, pausa automatica si numero bloqueado
8. **Persistencia**: Secuencias y metricas en DynamoDB, estado de cada contacto en el funnel
9. **Multi-Tenant**: Secuencias aisladas por organizacion y cliente
10. **Observabilidad**: Conversion rate por paso, mensajes enviados/entregados/leidos

**E2E Test Coverage**: PENDIENTE

---

#### EP-MK-020: Agente de Analytics y Reportes
**Estado**: PENDIENTE (Planificacion)
**Complejidad**: L
**Valor de Negocio**: Genera reportes inteligentes bajo demanda o programados que consolidan metricas de todos los canales. Elimina la necesidad de crear reportes mensuales manualmente en PowerPoint.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Genera reportes bajo demanda via WhatsApp o Web chat, programables (semanal/mensual)
2. **UX/UI**: Reportes visuales con graficas, exportacion PDF/CSV, envio por email
3. **Rendimiento**: Consolidacion de datos asincrona, reportes pre-generados para acceso rapido
4. **Seguridad**: Reportes accesibles solo para usuarios autorizados
5. **Accesibilidad**: Reportes PDF con estructura semantica, tablas accesibles
6. **Integracion**: Consolida datos de social media, ads, email, WhatsApp, landing pages
7. **Error Handling**: Si una fuente falla, genera reporte parcial con indicador
8. **Persistencia**: Reportes generados en S3, historial en DynamoDB
9. **Multi-Tenant**: Reportes aislados por organizacion y cliente
10. **Observabilidad**: Reportes generados por mes, tiempo de generacion, fuentes consultadas

**E2E Test Coverage**: PENDIENTE

---

#### EP-MK-021: Agente de Lead Generation y Nurturing
**Estado**: PENDIENTE (Planificacion)
**Complejidad**: XL
**Valor de Negocio**: Automatiza el ciclo completo de leads: captura desde formularios/WhatsApp/ads, scoring por comportamiento, asignacion a vendedores, y nurturing personalizado. Identifica leads calientes en tiempo real.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Captura leads de landing pages/WhatsApp/FB Lead Ads, scoring automatico, asignacion a vendedores
2. **UX/UI**: Pipeline visual de leads, score badges, alertas de leads calientes
3. **Rendimiento**: Scoring en tiempo real, alertas push inmediatas para leads calientes
4. **Seguridad**: Datos de leads encriptados, acceso por rol (vendedor solo ve sus leads)
5. **Accesibilidad**: Pipeline navegable por teclado, scores con descripcion textual
6. **Integracion**: covacha-crm para pipeline, covacha-webhook para formularios, Facebook Lead Ads
7. **Error Handling**: Si scoring falla, marca lead como "pendiente de clasificacion"
8. **Persistencia**: Leads con historial de interacciones en DynamoDB, score historico
9. **Multi-Tenant**: Leads aislados por organizacion y cliente
10. **Observabilidad**: Leads por fuente, tasa de conversion, tiempo promedio de cierre

**E2E Test Coverage**: PENDIENTE

---

#### EP-MK-022: Agente de Brand Kit y Assets
**Estado**: PENDIENTE (Planificacion)
**Complejidad**: M
**Valor de Negocio**: Mantiene consistencia de marca automaticamente generando assets graficos respetando el brand kit, validando contenido contra guidelines, y generando variaciones de logos para distintas plataformas.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Genera assets graficos (banners, headers) respetando brand kit, valida contenido contra guidelines
2. **UX/UI**: Galeria de assets generados, indicadores de compliance, sugerencias visuales
3. **Rendimiento**: Generacion de assets en background, cache de assets generados
4. **Seguridad**: Assets generados con marca de agua si no estan aprobados
5. **Accesibilidad**: Verificacion automatica de contraste WCAG AA en colores del brand kit
6. **Integracion**: Consume brand kit existente (EP-MK-008), genera variaciones de logo por plataforma
7. **Error Handling**: Si generacion de asset falla, ofrece templates base como alternativa
8. **Persistencia**: Assets en S3, historial de generaciones en DynamoDB
9. **Multi-Tenant**: Assets aislados por organizacion y cliente
10. **Observabilidad**: Assets generados por mes, compliance rate, plataformas mas solicitadas

**E2E Test Coverage**: PENDIENTE

---

#### EP-MK-023: Agente de SEO/SEM
**Estado**: PENDIENTE (Planificacion)
**Complejidad**: L
**Valor de Negocio**: Optimiza la presencia en buscadores con analisis de keywords, auditorias tecnicas de landing pages, monitoreo de posiciones, y analisis de competencia.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Investigacion de keywords (volumen, dificultad, CPC), content briefs SEO, auditoria tecnica
2. **UX/UI**: Dashboard de posiciones, tabla de keywords con metricas, reporte de auditoria
3. **Rendimiento**: Monitoreo de posiciones en batch (semanal), resultados cacheados
4. **Seguridad**: Datos de Google Search Console con scopes minimos
5. **Accesibilidad**: Reportes de auditoria con estructura semantica
6. **Integracion**: Google Search Console API, Google Analytics Data API, landings existentes
7. **Error Handling**: Si API de Google falla, usa datos cacheados con indicador de "datos no actualizados"
8. **Persistencia**: Keywords y posiciones en DynamoDB con historial temporal
9. **Multi-Tenant**: SEO aislado por organizacion y cliente
10. **Observabilidad**: Posiciones ganadas/perdidas por semana, keywords trackeadas

**E2E Test Coverage**: PENDIENTE

---

#### EP-MK-024: Reportes de Resultados de Redes Sociales
**Estado**: PENDIENTE (Planificacion)
**Complejidad**: L
**Valor de Negocio**: Sistema completo de reportes formales de resultados de redes sociales: recopilacion automatica de metricas de FB/IG, ranking de posts, demografia de audiencia, comparativas periodo a periodo, templates PDF con branding, y envio automatico por email. Elimina los 1-2 dias manuales por reporte mensual por cliente.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: CRUD de reportes, recopilacion automatica de metricas FB/IG, ranking top/bottom posts, comparativas MoM/YoY
2. **UX/UI**: Cards de metricas por plataforma, graficas de tendencia, heatmap de mejores horarios, preview PDF
3. **Rendimiento**: Recopilacion de metricas asincrona (10-30s), graficas renderizadas con ECharts
4. **Seguridad**: Tokens de FB/IG validados antes de generar, datos de metricas aislados por cliente
5. **Accesibilidad**: Reportes PDF con estructura semantica, graficas con datos tabulares alternativos
6. **Integracion**: Facebook Graph API Insights, Instagram Graph API, Brand Kit para PDF branding, SES para envio
7. **Error Handling**: Si una plataforma falla, las demas continuan y se muestra error parcial; tokens expirados notificados
8. **Persistencia**: Reportes en DynamoDB (items separados por plataforma y posts), PDF en S3, reportes programados con cron SQS
9. **Multi-Tenant**: Reportes aislados por organizacion y cliente, templates de reportes personalizables
10. **Observabilidad**: Reportes generados/enviados por mes, tiempos de generacion, errores de API por plataforma

**E2E Test Coverage**: PENDIENTE (7 user stories: US-MK-094 a US-MK-100, 104+ tests planificados)

---

#### EP-MK-025: Integracion Meta AI / LLama
**Estado**: EN PROGRESO (backend COMPLETADO: 7 servicios + 2 controllers + 181 tests; frontend service COMPLETADO; pendiente: frontend components + E2E)
**Complejidad**: L
**Valor de Negocio**: Integracion dedicada de Meta AI/LLama como proveedor de IA. Ventajas: costo operativo minimo (modelos open-weight), optimizado para ecosistema Meta (FB/IG/WhatsApp/Ads), capacidad multimodal (analisis de imagenes de posts/ads), y opcion self-hosted para privacidad total.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Wizard de configuracion Meta AI, catalogo de modelos LLama (3.1/3.2/3.3), playground de pruebas, generacion de contenido
2. **UX/UI**: Catalogo visual de modelos con specs, playground interactivo, dashboard comparativo entre providers
3. **Rendimiento**: Routing inteligente entre providers (Meta AI API, Together AI, Fireworks AI, Groq, self-hosted)
4. **Seguridad**: API keys encriptadas, opcion self-hosted para datos que no salen del servidor
5. **Accesibilidad**: Formularios de configuracion accesibles, feedback de errores claro
6. **Integracion**: API OpenAI-compatible para todos los providers LLama, analisis multimodal de imagenes (LLama 3.2 Vision)
7. **Error Handling**: Fallback entre providers si uno falla, circuit breaker para providers inestables
8. **Persistencia**: Config de provider en DynamoDB, historial de generaciones con metricas
9. **Multi-Tenant**: Configuracion Meta AI aislada por organizacion y cliente
10. **Observabilidad**: Dashboard comparativo de rendimiento y costos entre todos los providers (calidad, velocidad, costo por token)

**E2E Test Coverage**: PENDIENTE (7 user stories: US-MK-101 a US-MK-107)

---

#### EP-MK-026: Promociones Dinamicas desde Base de Datos
**Estado**: COMPLETADO
**Complejidad**: M
**Valor de Negocio**: Reemplaza el componente estatico de creacion de promociones por un listado dinamico que lee promociones activas y vigentes de la base de datos. Resuelve el problema critico de que la pagina publica mostraba un formulario de creacion en lugar de las promociones disponibles.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Endpoint publico de promociones activas con filtrado por vigencia, listado dinamico de cards
2. **UX/UI**: Cards responsivas con imagen/titulo/descripcion/badge vigencia/CTA, skeleton loading, mensaje "sin promociones"
3. **Rendimiento**: Cache de 5 minutos en endpoint publico, paginacion con limit/offset
4. **Seguridad**: Endpoint publico sin auth pero rate-limited, datos de promociones sanitizados
5. **Accesibilidad**: Cards con alt text en imagenes, estructura semantica, contraste de badges
6. **Integracion**: Routing dual en ingles (`/promotions/:slug`) y español (`/promociones/:slug`)
7. **Error Handling**: Promociones vencidas muestran "ya no disponible" con link al listado
8. **Persistencia**: Promociones en DynamoDB con GSI por status+fecha, cron/TTL para auto-expirar
9. **Multi-Tenant**: Promociones publicas filtradas por client_slug
10. **Observabilidad**: Visitas a listado de promociones, clicks por promocion, tasa de conversion a landing

**E2E Test Coverage**: `promotions-list.spec.ts`

---

#### EP-MK-027: Landing de Promociones Orientada a Ventas
**Estado**: COMPLETADO
**Complejidad**: L
**Valor de Negocio**: Landing pages de promociones con layout dedicado a conversion: sin navegacion principal, QR multidimensional, formulario de contacto que alimenta el CRM, boton flotante de WhatsApp, y estilo heredado del website del cliente.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Layout de conversion (header minimo + CTA), QR dinamico con logo del cliente, formulario→CRM leads
2. **UX/UI**: Boton flotante WhatsApp, QR prominente, formulario de contacto amigable, estilo heredado del website
3. **Rendimiento**: Landing optimizada para lighthouse (imagenes WebP, CSS inline critico)
4. **Seguridad**: Formulario con captcha, sanitizacion de inputs, CORS configurado
5. **Accesibilidad**: Formulario accesible, contraste WCAG AA, estructura semantica H1-H6
6. **Integracion**: Formulario crea lead en covacha-core CRM con source `promotion:{slug}`, WhatsApp pre-llenado
7. **Error Handling**: Si formulario falla, muestra error amigable con opcion de WhatsApp como alternativa
8. **Persistencia**: Leads en DynamoDB con referencia a promocion, tracking de conversiones por landing
9. **Multi-Tenant**: Landing pages con estilo del cliente, QR con logo del brand kit
10. **Observabilidad**: Conversiones (form submits), clicks WhatsApp, scans de QR, bounce rate

**E2E Test Coverage**: `public-landing.spec.ts`

---

#### EP-MK-028: Motor de Funnels de Venta Multi-Canal
**Estado**: COMPLETADO (backend)
**Complejidad**: XL
**Valor de Negocio**: Motor de funnels de venta configurable con canales email y WhatsApp. Incluye funnel por defecto (bienvenida al lead + notificacion al equipo + follow-up), configuracion de frecuencia/timezone/horarios, recurrencia mensual infinita, y funnel chaining.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Motor de funnels con steps secuenciales, triggers (lead created, compra, inactividad), canales email/WhatsApp
2. **UX/UI**: Builder visual de funnels con nodos, configuracion de delays y condiciones (pendiente frontend)
3. **Rendimiento**: Ejecucion via SQS, despacho respeta timezone y horarios configurados
4. **Seguridad**: Solo templates WhatsApp aprobados por Meta, emails via SES con validacion
5. **Accesibilidad**: Builder accesible por teclado (pendiente frontend)
6. **Integracion**: covacha-botia como motor de ejecucion, covacha-core para leads, SES para email, WhatsApp Business API
7. **Error Handling**: Retry automatico si envio falla, pausa de funnel si contacto bloquea, logs de cada step
8. **Persistencia**: Funnels y estado de ejecucion en DynamoDB, historial de envios
9. **Multi-Tenant**: Funnels aislados por organizacion y cliente
10. **Observabilidad**: Conversion rate por step, emails/WA enviados, funnels activos, leads en proceso

**E2E Test Coverage**: PENDIENTE (10 user stories: US-MK-123 a US-MK-132)

---

#### EP-MK-029: Integracion Chatbot + Promociones
**Estado**: COMPLETADO (backend)
**Complejidad**: M
**Valor de Negocio**: El chatbot del cliente (web y WhatsApp) entiende las promociones activas y puede responder preguntas sobre ellas. El chatbot esta visible en las landing pages de promociones, aumentando la tasa de conversion.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Knowledge base de promociones activas en chatbot, responde preguntas sobre ofertas/precios/vigencia
2. **UX/UI**: Widget de chatbot en landing pages de promociones (pendiente frontend)
3. **Rendimiento**: Cache de promociones activas (5 min), regex pattern matching para deteccion rapida
4. **Seguridad**: Chatbot no revela datos internos, solo informacion publica de promociones
5. **Accesibilidad**: Widget de chat accesible, respuestas con texto claro
6. **Integracion**: PromotionContextService en covacha-botia, inyeccion de contexto en WebChatController
7. **Error Handling**: Si no entiende la pregunta, ofrece opciones predefinidas o escala a humano
8. **Persistencia**: Conversaciones con referencia a promocion en DynamoDB
9. **Multi-Tenant**: Chatbot con knowledge base aislada por cliente
10. **Observabilidad**: Preguntas sobre promociones vs generales, tasa de resolucion, conversiones atribuidas al chat

**E2E Test Coverage**: PENDIENTE

---

#### EP-MK-030: Tests y Cobertura Completa Promociones
**Estado**: PENDIENTE
**Complejidad**: L
**Valor de Negocio**: Garantiza la calidad del sistema de promociones y funnels con cobertura >= 98% en backend y >= 90% en frontend. Reduce riesgo de regresiones en produccion.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Tests unitarios, de integracion y E2E para todo el sistema de promociones y funnels
2. **UX/UI**: Tests E2E verifican flujo completo de usuario (crear promocion → ver landing → submit form → funnel ejecuta)
3. **Rendimiento**: Tests de carga para endpoint publico de promociones (>100 req/s)
4. **Seguridad**: Tests de seguridad (SQL injection en formularios, XSS en contenido de promocion)
5. **Accesibilidad**: Tests de accesibilidad con axe-core en landing pages
6. **Integracion**: Tests de integracion con mocks de Facebook API, SES, WhatsApp API
7. **Error Handling**: Tests de edge cases (promocion sin imagen, vigencia nula, funnel sin steps)
8. **Persistencia**: Tests de repositorios DynamoDB con moto
9. **Multi-Tenant**: Tests de aislamiento (cliente A no ve promociones de cliente B)
10. **Observabilidad**: Reporte de cobertura publicado en CI, threshold de 98% backend / 90% frontend

**E2E Test Coverage**: US-MK-138 a US-MK-140 (test specs pendientes)

---

## 2. Producto: SuperPago SPEI

### 2.1 Vision de Negocio

SuperPago SPEI es una plataforma de pagos que revende servicios SPEI a traves de Monato Fincore, ofreciendo a clientes empresariales la capacidad de abrir cuentas CLABE, enviar y recibir dinero via SPEI, y gestionar una estructura jerarquica de cuentas financieras (concentradora, dispersion, CLABE, reservada). El sistema implementa contabilidad de partida doble (double-entry ledger) para cada movimiento y esta diseñado para escalar a multiples proveedores SPEI en el futuro.

**Propuesta de valor:**
- Cuentas CLABE propias para recibir y enviar SPEI
- Estructura de cuentas jerarquica (concentradora, dispersion, reservada)
- Contabilidad de partida doble con audit trail completo
- Transferencias internas entre organizaciones sin costo SPEI
- Red de puntos de Cash-In/Cash-Out (similar a OXXO Pay)
- Subasta de efectivo (mercado de liquidez interna)
- Agente IA WhatsApp para operar cuentas por chat
- Frontend multi-tier: Admin (Tier 1), Empresa B2B (Tier 2), Usuario B2C (Tier 3)

**Usuarios objetivo:**
- Administradores SuperPago (Tier 1) - gestion global del ecosistema
- Clientes empresariales B2B (Tier 2) - operan finanzas via SPEI
- Usuarios finales B2C (Tier 3) - persona natural con cuenta y CLABE
- Operadores de puntos de pago - procesan Cash-In/Cash-Out
- Agente IA (covacha-botia) - intermediario conversacional en WhatsApp

### 2.2 Modulos Implementados

---

#### EP-SP-001: Account Core Engine
**Estado**: COMPLETADO (backend)
**Complejidad**: XL
**Valor de Negocio**: Motor de cuentas financieras que modela la jerarquia CONCENTRADORA→CLABE→DISPERSION→RESERVADA como un grafo dirigido. Es el corazon del sistema SPEI: sin cuentas no hay transacciones.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: CRUD de 4 tipos de cuenta con validaciones de jerarquia, grafo padre-hijo, maquina de estados (PENDING→ACTIVE→FROZEN→CLOSED)
2. **UX/UI**: N/A (backend puro, consumido por mf-sp)
3. **Rendimiento**: Saldo calculado desde ledger en <200ms para cuentas con 10K+ entries
4. **Seguridad**: Validacion de organization_id en toda operacion, transiciones de estado controladas
5. **Accesibilidad**: N/A (backend)
6. **Integracion**: Monato Fincore para crear cuentas CLABE y obtener CLABEs, GSIs para consultas eficientes
7. **Error Handling**: Validacion de jerarquia (CLABE→hijo de CONCENTRADORA), no se permiten ciclos en el grafo, no se puede cerrar cuenta con hijas activas
8. **Persistencia**: DynamoDB con PK `ORG#{org_id}` SK `ACCOUNT#{id}`, GSIs para parent, CLABE y tipo
9. **Multi-Tenant**: Cuentas aisladas por organization_id
10. **Observabilidad**: Cobertura de tests >= 98%, logs estructurados para debugging

**E2E Test Coverage**: Consumido por EP-SP-007/EP-SP-008 (frontend)

---

#### EP-SP-002: Monato Driver (Strategy Pattern)
**Estado**: COMPLETADO (backend)
**Complejidad**: L
**Valor de Negocio**: Capa de abstraccion multi-proveedor para operaciones SPEI usando Strategy Pattern. Hoy implementa Monato Fincore; mañana puede agregar STP, Arcus, Mastercard sin cambiar logica de negocio.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Interface `SPEIProvider` implementada por `MonatoDriver`: crear cuenta, crear instrumento, money_out, webhook, catalogo participantes, penny validation
2. **UX/UI**: N/A (backend)
3. **Rendimiento**: Circuit breaker para API de Monato, retry con backoff exponencial
4. **Seguridad**: Idempotency key en todas las operaciones mutativas, credenciales en variables de entorno
5. **Accesibilidad**: N/A (backend)
6. **Integracion**: API REST de Monato Fincore para SPEI, catalogo de participantes SPEI
7. **Error Handling**: Retry con circuit breaker, logs estructurados para debugging de integracion, errores mapeados a codigos internos
8. **Persistencia**: Estado de operaciones en DynamoDB con idempotency key
9. **Multi-Tenant**: Driver configurado por organizacion (futuro: diferentes providers por org)
10. **Observabilidad**: Latencia de API Monato, tasa de exito/fallo, errores por tipo

**E2E Test Coverage**: Indirecto via EP-SP-004 (SPEI Out)

---

#### EP-SP-003: Double-Entry Ledger
**Estado**: COMPLETADO (backend)
**Complejidad**: L
**Valor de Negocio**: Sistema contable de partida doble. Cada movimiento genera exactamente 2 asientos (debito + credito), garantizando consistencia financiera y audit trail completo. El saldo se calcula sumando asientos, no se almacena directamente.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Modelo LedgerEntry con debito/credito, toda transaccion genera 2 entries, saldo = SUM(creditos) - SUM(debitos)
2. **UX/UI**: N/A (backend)
3. **Rendimiento**: Calculo de saldo en <200ms para cuentas con 10K+ entries (meta pendiente de optimizacion)
4. **Seguridad**: Entries append-only (no se pueden editar ni eliminar), reversos generan entries inversos
5. **Accesibilidad**: N/A (backend)
6. **Integracion**: Consumido por SPEI Out, SPEI In, movimientos internos, Cash-In/Cash-Out
7. **Error Handling**: Balance trial verification (SUM debitos = SUM creditos en todo el sistema)
8. **Persistencia**: DynamoDB con TransactWriteItems para atomicidad, GSIs por fecha y cuenta
9. **Multi-Tenant**: Entries aislados por organization_id
10. **Observabilidad**: Tests de concurrencia, cobertura >= 98%

**E2E Test Coverage**: Indirecto via EP-SP-004 y EP-SP-006

---

#### EP-SP-004: SPEI Out (Transferencias Salientes)
**Estado**: COMPLETADO (backend)
**Complejidad**: L
**Valor de Negocio**: Flujo completo de transferencias SPEI out. Desde cuentas CLABE o DISPERSION hacia cualquier banco de Mexico. Incluye validacion de saldo, asientos contables, envio via Monato, tracking de estado, y penny validation.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: SPEI out desde CLABE y DISPERSION, RESERVADA solo al destino fijo, CONCENTRADORA bloqueada, estados PENDING→PROCESSING→COMPLETED/FAILED/REVERSED
2. **UX/UI**: N/A (backend, UI en EP-SP-008)
3. **Rendimiento**: Transferencia iniciada en <2s, completada segun SLA de Monato
4. **Seguridad**: Idempotency key obligatoria, penny validation para primera transferencia a cuenta nueva, validacion de saldo pre-envio
5. **Accesibilidad**: N/A (backend)
6. **Integracion**: Monato Driver para ejecutar money_out, Ledger para asientos, beneficiarios frecuentes
7. **Error Handling**: Asientos hold al iniciar, confirmacion/reversa al completar, comision como asiento separado
8. **Persistencia**: Transferencias en DynamoDB con estados, asientos atomicos via TransactWriteItems
9. **Multi-Tenant**: Transferencias aisladas por organization_id
10. **Observabilidad**: Tasa de exito/fallo, tiempo promedio de completado, comisiones generadas

**E2E Test Coverage**: Consumido por EP-SP-008 (frontend)

---

#### EP-SP-005: Webhook Handler SPEI In
**Estado**: COMPLETADO (backend)
**Complejidad**: L
**Valor de Negocio**: Procesa depositos entrantes via webhooks de Monato. Cuando alguien envia SPEI a una CLABE de SuperPago, el handler identifica la cuenta, crea asientos contables, propaga saldo a concentradora padre, y notifica al usuario.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Endpoint POST para webhooks Monato, identifica CLABE destino, crea asientos de credito, propaga a concentradora
2. **UX/UI**: N/A (backend, notificacion al usuario via push/email)
3. **Rendimiento**: Response 200 en <500ms (meta pendiente), procesamiento async via SQS
4. **Seguridad**: Validacion de firma/token del webhook, procesamiento idempotente
5. **Accesibilidad**: N/A (backend)
6. **Integracion**: covacha-webhook para recepcion, covacha-payment para asientos, notificaciones
7. **Error Handling**: Eventos desconocidos se loggean sin fallar, retry queue con SQS dead letter
8. **Persistencia**: Eventos procesados en tabla de idempotencia con TTL
9. **Multi-Tenant**: Eventos ruteados a la organizacion correcta via CLABE
10. **Observabilidad**: Logs detallados para debugging, metricas de eventos procesados

**E2E Test Coverage**: Indirecto (backend testing)

---

#### EP-SP-006: Movimientos Internos (Grafo)
**Estado**: COMPLETADO (backend)
**Complejidad**: M
**Valor de Negocio**: Transferencias entre cuentas de la misma organizacion: instantaneas, sin costo, con reglas del grafo validadas. Ejemplos: CLABE→CONCENTRADORA, CONCENTRADORA→DISPERSION, CONCENTRADORA→RESERVADA.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Movimientos permitidos segun grafo (CLABE→CONCENTRADORA, CONCENTRADORA→DISPERSION/RESERVADA), dispersion masiva 1→N
2. **UX/UI**: N/A (backend, UI en EP-SP-008)
3. **Rendimiento**: Operacion instantanea (no pasa por SPEI), batch con rollback si falla
4. **Seguridad**: Validacion de reglas del grafo, movimientos no permitidos devuelven error descriptivo
5. **Accesibilidad**: N/A (backend)
6. **Integracion**: Ledger para asientos de partida doble, sin comision
7. **Error Handling**: Rollback atomico si alguna transferencia del batch falla
8. **Persistencia**: Asientos via TransactWriteItems para atomicidad
9. **Multi-Tenant**: Movimientos solo entre cuentas de la misma organizacion
10. **Observabilidad**: Volumen de movimientos internos, tipos mas frecuentes

**E2E Test Coverage**: Consumido por EP-SP-008 (frontend)

---

#### EP-SP-007: mf-sp Scaffold + Arquitectura Multi-Tier
**Estado**: COMPLETADO (frontend)
**Complejidad**: L
**Valor de Negocio**: Creacion del micro-frontend mf-sp con Angular 21, Native Federation, y arquitectura de 3 portales diferenciados por rol (Admin, Business, Personal). Base de toda la UI financiera.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Proyecto Angular 21 con estructura hexagonal, Native Federation (puerto 4212, remote mfSP), 3 layouts diferenciados
2. **UX/UI**: AdminLayout, BusinessLayout, PersonalLayout con navegacion adaptada por tier
3. **Rendimiento**: Lazy loading por tier, modelos y adapters base optimizados
4. **Seguridad**: TierDetectionService por permisos/rol, guards por tier, redirect inteligente
5. **Accesibilidad**: Layouts con estructura semantica, navegacion por teclado
6. **Integracion**: SharedStateService lee covacha:auth/user/tenant del Shell, HttpService con headers requeridos
7. **Error Handling**: Si tier no detectado, redirige a pagina de error con instrucciones
8. **Persistencia**: Path aliases configurados (@app, @core, @domain, etc.)
9. **Multi-Tenant**: Tier detection basada en permisos del usuario, datos scoped por organizacion
10. **Observabilidad**: Build de produccion exitoso, registrado en mf-core como remote

**E2E Test Coverage**: Indirecto via EP-SP-008, EP-SP-011, EP-SP-012

---

#### EP-SP-008: Portal Admin SuperPago (Tier 1)
**Estado**: COMPLETADO (frontend)
**Complejidad**: XL
**Valor de Negocio**: Centro de control financiero para el equipo interno de SuperPago. Vision global de todas las cuentas, monitoreo de proveedores SPEI, reconciliacion, configuracion de politicas, y audit trail.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Dashboard global, vista de todas las organizaciones con saldos, grafo visual del ecosistema, panel de monitoreo de Monato
2. **UX/UI**: Graficos de ecosistema (arbol SVG interactivo), panel de reconciliacion con calendario, alertas prominentes
3. **Rendimiento**: Datos agregados server-side, graficas lazy-loaded, paginacion server-side
4. **Seguridad**: Solo accesible con permiso `sp:admin`, datos de todas las organizaciones
5. **Accesibilidad**: Grafos con descripciones textuales alternativas, tablas semanticas
6. **Integracion**: API de cuentas, Ledger, reconciliacion, proveedores SPEI
7. **Error Handling**: DLQ management (ver, reintentar, resolver), alertas de anomalias
8. **Persistencia**: Reportes exportables (CSV, PDF)
9. **Multi-Tenant**: Vista cross-tenant para admin, datos de todas las organizaciones
10. **Observabilidad**: Panel de salud del sistema, latencia de Monato, errores por tipo

**E2E Test Coverage**: Cubierto por tests del scaffold

---

#### EP-SP-009: Reconciliacion y Auditoria
**Estado**: COMPLETADO (backend)
**Complejidad**: M
**Valor de Negocio**: Reconciliacion automatica diaria que compara ledger interno vs reportes de Monato. Detecta discrepancias, genera alertas, y provee audit trail completo.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Job de reconciliacion diaria, deteccion de discrepancias, audit trail, balance trial
2. **UX/UI**: Dashboard de reconciliacion en mf-sp (parcialmente pendiente frontend)
3. **Rendimiento**: Reconciliacion en batch nocturno, alertas en tiempo real para discrepancias criticas
4. **Seguridad**: Audit trail inmutable, acceso solo para admins
5. **Accesibilidad**: N/A (mayoria backend)
6. **Integracion**: Compara ledger (covacha-payment) vs reportes de Monato
7. **Error Handling**: Alerta automatica cuando discrepancia > umbral configurable
8. **Persistencia**: Resultados de reconciliacion en DynamoDB, export para contabilidad (pendiente)
9. **Multi-Tenant**: Reconciliacion por organizacion
10. **Observabilidad**: Tasa de discrepancias, tiempo de resolucion

**E2E Test Coverage**: Parcial (backend tests, frontend dashboard pendiente)

---

#### EP-SP-010: Limites, Politicas y Notificaciones
**Estado**: COMPLETADO (backend)
**Complejidad**: M
**Valor de Negocio**: Capa de politicas de negocio: limites de transaccion configurables, aprobaciones para montos altos, notificaciones en tiempo real, y rate limiting.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Limites por cuenta/organizacion (max por transaccion, diario, mensual, operaciones/dia), aprobaciones para montos altos
2. **UX/UI**: Configuracion de politicas via UI (parcialmente pendiente frontend)
3. **Rendimiento**: Validacion de limites en <50ms (in-memory cache)
4. **Seguridad**: Rate limiting en API de transferencias (pendiente), audit log de cambios a politicas (pendiente)
5. **Accesibilidad**: N/A (mayoria backend)
6. **Integracion**: Notificaciones via email+push para depositos, transferencias, limites alcanzados
7. **Error Handling**: Warning al 80% del limite, bloqueo al 100%, mensajes descriptivos
8. **Persistencia**: Politicas en DynamoDB, configurables por cuenta y organizacion
9. **Multi-Tenant**: Politicas aisladas por organizacion
10. **Observabilidad**: Transferencias bloqueadas por limites, alertas generadas

**E2E Test Coverage**: Backend tests completados

---

#### EP-SP-011: Portal Cliente Empresa B2B (Tier 2)
**Estado**: COMPLETADO (frontend)
**Complejidad**: XL
**Valor de Negocio**: Portal para clientes empresariales como "Boxito" que operan sus finanzas via SPEI. Dashboard de cuentas, transferencias SPEI out, movimientos internos, gestion de usuarios Tier 3, y aprobaciones.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Dashboard de cuentas con saldos, formulario SPEI out (wizard 3 pasos), movimiento interno, gestion de estructura
2. **UX/UI**: Wizard de transferencia con validaciones paso a paso, historial con filtros y paginacion
3. **Rendimiento**: Paginacion server-side en historial, polling de estado de transferencia
4. **Seguridad**: Solo accesible con permiso `sp:business`, scoped a la organizacion del usuario
5. **Accesibilidad**: Formularios accesibles, tablas con headers semanticos
6. **Integracion**: APIs de cuentas, SPEI out, movimientos internos, aprobaciones
7. **Error Handling**: Validacion de saldo pre-envio, confirmacion antes de transferir, undo disponible
8. **Persistencia**: Export a CSV/PDF disponible
9. **Multi-Tenant**: Datos scoped a la organizacion del usuario
10. **Observabilidad**: Transferencias por dia, saldo promedio, aprobaciones pendientes

**E2E Test Coverage**: Cubierto por tests del scaffold

---

#### EP-SP-012: Portal Usuario Final B2C (Tier 3)
**Estado**: COMPLETADO (frontend)
**Complejidad**: M
**Valor de Negocio**: Portal simplificado para personas naturales. Saldo de su cuenta, CLABE para recibir SPEI, historial de movimientos, y opcionalmente transferencias salientes.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Dashboard simple (saldo prominente, CLABE con boton copiar), historial, detalle de movimientos, SPEI out (si habilitado)
2. **UX/UI**: Interfaz optimizada para mobile, saldo grande y visible, CLABE con un tap para copiar
3. **Rendimiento**: Dashboard carga en <1s, historial paginado
4. **Seguridad**: Solo ve SU cuenta (datos scoped), permiso `sp:personal`
5. **Accesibilidad**: Interfaz mobile-first accesible, botones grandes, contraste alto
6. **Integracion**: API de cuentas, historial de movimientos
7. **Error Handling**: Si transferencia falla, mensaje claro con razon
8. **Persistencia**: N/A (solo lectura de datos existentes)
9. **Multi-Tenant**: Datos scoped al usuario individual
10. **Observabilidad**: Frecuencia de uso, transferencias por usuario

**E2E Test Coverage**: Cubierto por tests del scaffold

---

#### EP-SP-013: Componentes Compartidos entre Tiers
**Estado**: COMPLETADO (frontend)
**Complejidad**: L
**Valor de Negocio**: Biblioteca de componentes reutilizables compartidos entre los 3 portales, parametrizados por tier para mostrar mas o menos informacion segun nivel de acceso.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: MovementsTable, AccountTree, TransferForm, AccountDetailCard, TransferStatusTracker
2. **UX/UI**: Componentes parametrizados por tier (Admin ve mas columnas que Personal)
3. **Rendimiento**: OnPush + Signals en todos los componentes, lazy rendering
4. **Seguridad**: Columnas sensibles ocultas segun tier del usuario
5. **Accesibilidad**: Tablas con headers semanticos, arbol navegable por teclado
6. **Integracion**: Consumidos por EP-SP-008, EP-SP-011, EP-SP-012
7. **Error Handling**: Estados vacios con mensajes descriptivos, loading skeletons
8. **Persistencia**: N/A (componentes de presentacion)
9. **Multi-Tenant**: Comportamiento adaptado por tier via @Input
10. **Observabilidad**: Componentes documentados y exportados via barrel

**E2E Test Coverage**: Indirecto via portales que los consumen

---

#### EP-SP-014: Transferencias Internas Inter-Organizacion
**Estado**: COMPLETADO (backend)
**Complejidad**: M
**Valor de Negocio**: Mover dinero entre organizaciones dentro de SuperPago sin SPEI. Operacion instantanea, sin costo, con asientos que cruzan boundaries de organizacion. Solo Admin Tier 1 puede ejecutar.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Transferencia entre cuentas CONCENTRADORA/CLABE de diferentes orgs, politicas de pre-aprobacion, historial y reportes
2. **UX/UI**: N/A (backend, UI en EP-SP-020)
3. **Rendimiento**: Operacion instantanea, TransactWriteItems atomicos
4. **Seguridad**: Solo Admin Tier 1, idempotencia estricta, audit trail con tag `CROSS_ORG`
5. **Accesibilidad**: N/A (backend)
6. **Integracion**: Extiende EP-SP-006 con validaciones cross-org, ledger con asientos cross-boundary
7. **Error Handling**: Validacion de orgs activas, saldo suficiente, politicas de limites
8. **Persistencia**: InterOrgTransfer en DynamoDB con GSIs, InterOrgPolicy para pre-aprobacion
9. **Multi-Tenant**: Movimiento entre tenants controlado por Admin
10. **Observabilidad**: Saldo total del ecosistema no cambia (suma cero), metricas de transferencias cross-org

**E2E Test Coverage**: Backend tests (27 tests, 761 total)

---

#### EP-SP-015: Cash-In / Cash-Out (Red de Puntos)
**Estado**: COMPLETADO (backend)
**Complejidad**: XL
**Valor de Negocio**: Sistema de depositos y retiros de efectivo en red de puntos fisicos (similar a OXXO Pay). Cada punto de pago tiene cuenta de liquidacion propia. Incluye limites, comisiones configurables, y reconciliacion.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Modelo PaymentPoint con cuenta de liquidacion, Cash-In (deposito→credito), Cash-Out (retiro→debito), limites por operacion/dia/punto
2. **UX/UI**: N/A (backend, UI en EP-SP-020)
3. **Rendimiento**: Operaciones procesadas en <2s, referencias unicas generadas instantaneamente
4. **Seguridad**: Referencia unica por operacion (QR o codigo numerico), comprobante digital
5. **Accesibilidad**: N/A (backend)
6. **Integracion**: Asientos de partida doble nuevas categorias CASH_IN/CASH_OUT, reconciliacion de puntos
7. **Error Handling**: Validacion de limites pre-operacion, comision configurable por tipo
8. **Persistencia**: PaymentPoints y operaciones en DynamoDB
9. **Multi-Tenant**: Puntos de pago por organizacion
10. **Observabilidad**: Efectivo total en red, operaciones por punto, reconciliacion diaria

**E2E Test Coverage**: Backend tests (25 tests, 786 total)

---

#### EP-SP-016: Subasta de Efectivo (Mercado de Liquidez)
**Estado**: COMPLETADO (backend)
**Complejidad**: L
**Valor de Negocio**: Mercado interno de liquidez. Los puntos de pago con exceso de efectivo publican ofertas; las empresas compran el efectivo via transferencia interna. SuperPago cobra comision por intermediacion.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Modelo CashOffer, publicacion por puntos, marketplace visible para Tier 1/2, compra = transferencia inter-org automatica
2. **UX/UI**: N/A (backend, UI en EP-SP-020)
3. **Rendimiento**: Marketplace actualizado en tiempo real, ofertas expiradas automaticamente
4. **Seguridad**: Solo puntos autorizados publican, solo empresas verificadas compran
5. **Accesibilidad**: N/A (backend)
6. **Integracion**: Usa transferencias inter-org (EP-SP-014) para ejecutar compras
7. **Error Handling**: Expiracion de ofertas no compradas, validacion de fondos pre-compra
8. **Persistencia**: Ofertas y transacciones en DynamoDB
9. **Multi-Tenant**: Marketplace visible para todas las organizaciones del ecosistema
10. **Observabilidad**: Dashboard de liquidez (efectivo total, ofertas activas, tendencias)

**E2E Test Coverage**: Backend tests

---

#### EP-SP-017: Agente IA WhatsApp - Core
**Estado**: COMPLETADO (backend)
**Complejidad**: XL
**Valor de Negocio**: Agente conversacional en WhatsApp que permite operar cuentas SPEI por chat: vincular cuenta, consultar saldo, transferir con confirmacion 2FA. Lenguaje natural, no menus rigidos.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Vinculacion WhatsApp↔cuenta SPEI, consulta saldo, transferencia SPEI con flujo guiado y 2FA
2. **UX/UI**: Conversacion natural en español, confirmacion explicita antes de mover dinero
3. **Rendimiento**: Respuesta en <3s para consultas, <10s para transferencias
4. **Seguridad**: 2FA obligatorio para toda operacion que mueve dinero, rate limiting por usuario, hereda limites/politicas de la org
5. **Accesibilidad**: Lenguaje simple y claro, mensajes de error amigables
6. **Integracion**: covacha-botia (agente), covacha-payment (APIs), covacha-webhook (WhatsApp)
7. **Error Handling**: Mensajes amigables ("No tienes saldo suficiente. Tu saldo es $X"), contexto de sesion conversacional
8. **Persistencia**: Logs y audit trail de todas las operaciones via WhatsApp
9. **Multi-Tenant**: Agente hereda configuracion de la organizacion del usuario
10. **Observabilidad**: Operaciones por WhatsApp, tasa de exito, errores frecuentes

**E2E Test Coverage**: Backend tests con mocks de WhatsApp API y covacha-payment API

---

#### EP-SP-018: Agente IA WhatsApp - BillPay y Notificaciones
**Estado**: COMPLETADO (backend)
**Complejidad**: L
**Valor de Negocio**: Extension del agente para pago de servicios (CFE, Telmex, agua, gas, internet) y notificaciones proactivas de depositos/transferencias directamente en WhatsApp.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Catalogo de servicios pagables, flujo conversacional de pago con 2FA, consulta de adeudo, comprobante por WhatsApp
2. **UX/UI**: Conversacion guiada ("Paga mi recibo de luz"→pide referencia→confirma monto→2FA→paga), comprobante PDF
3. **Rendimiento**: Pago ejecutado en <15s incluyendo confirmacion
4. **Seguridad**: 2FA obligatorio para pagos, notificaciones configurables por usuario
5. **Accesibilidad**: Mensajes claros con montos formateados
6. **Integracion**: Agregador de BillPay (Openpay/Arcus), ledger nueva categoria BILL_PAY, SES para notificaciones
7. **Error Handling**: Si agregador falla, notifica al usuario con alternativa; si consulta adeudo no disponible, pide monto manual
8. **Persistencia**: Comprobantes en S3, transacciones en ledger
9. **Multi-Tenant**: Servicios disponibles configurados por organizacion
10. **Observabilidad**: Pagos por tipo de servicio, notificaciones enviadas, preferencias de usuario

**E2E Test Coverage**: Backend tests con mocks

---

#### EP-SP-019: Reglas de Integridad de Datos (Cross-cutting)
**Estado**: COMPLETADO (backend)
**Complejidad**: L
**Valor de Negocio**: Capa transversal de proteccion de integridad financiera. Previene race conditions, double-spending, y garantiza que toda operacion tenga sp_organization_id. Impacta a TODOS los servicios.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: sp_organization_id obligatorio en toda tabla/operacion, idempotencia con tabla dedicada, lock optimista para saldo
2. **UX/UI**: N/A (cross-cutting backend)
3. **Rendimiento**: Middleware de validacion en <5ms, idempotencia en <10ms
4. **Seguridad**: Middleware rechaza requests sin X-SP-Organization-Id, ConditionExpressions para saldo negativo
5. **Accesibilidad**: N/A (backend)
6. **Integracion**: TransactWriteItems para operaciones multi-entry, tabla de idempotencia con TTL
7. **Error Handling**: Double-spending prevenido con locks optimistas, mensajes de error especificos
8. **Persistencia**: Tabla de idempotencia dedicada con TTL configurable
9. **Multi-Tenant**: sp_organization_id validado en toda operacion
10. **Observabilidad**: Requests rechazados por falta de org_id, operaciones idempotentes detectadas, tests de concurrencia (pendiente)

**E2E Test Coverage**: Backend tests, cobertura >= 98%

---

#### EP-SP-020: mf-sp - Pantallas Cash, Subasta y Config IA
**Estado**: COMPLETADO (frontend stub)
**Complejidad**: L
**Valor de Negocio**: Extension del frontend con pantallas para Cash-In/Cash-Out, marketplace de subasta, y configuracion del agente IA WhatsApp. Completa la UI del ecosistema SPEI.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Gestion de puntos de pago (Admin), historial Cash-In/Cash-Out, marketplace subasta, config agente IA
2. **UX/UI**: Pantallas integradas en estructura multi-tier existente, patrones visuales consistentes con EP-SP-013
3. **Rendimiento**: Componentes lazy-loaded, paginacion server-side
4. **Seguridad**: Acceso por tier (Admin ve todo, Business ve su organizacion)
5. **Accesibilidad**: Componentes con estructura semantica, navegacion por teclado
6. **Integracion**: APIs de Cash (EP-SP-015), Subasta (EP-SP-016), Agente IA (EP-SP-017)
7. **Error Handling**: Estados vacios informativos, loading skeletons, error boundary
8. **Persistencia**: N/A (componentes de presentacion)
9. **Multi-Tenant**: Datos filtrados por tier del usuario
10. **Observabilidad**: Tests >= 98% (pendiente completar)

**E2E Test Coverage**: PENDIENTE (stubs implementados)

---

## 3. Producto: Inventario (mf-inventory)

### 3.1 Vision de Negocio

El modulo de Inventario es un sistema multi-cliente de gestion de productos, stock, venues (sucursales), proveedores, cotizaciones, ventas y reportes. Cada organizacion puede tener multiples clientes comerciales, cada uno con su propio inventario aislado. Se integra con mf-marketing para importar clientes existentes.

**Propuesta de valor:**
- Gestion de inventario multi-sucursal por cliente
- Catalogo de productos con codigos de barras, SKUs y QR
- Control de stock con alertas de minimos y maximos
- Cotizaciones inteligentes con precios por volumen
- Ventas y cierre diario por punto de venta
- Reportes de rotacion, valoracion y tendencias
- Auditorias fisicas y centros de costo

**Usuarios objetivo:**
- Administradores de inventario
- Operadores de punto de venta
- Super admins (vision cross-organizacion)

**Estado actual del codebase:**
- Backend: 47 endpoints definidos, solo 3 conectados, 99 tests escritos pero 0 ejecutables (conftest vacio)
- Frontend: 12 adaptadores, 6 componentes funcionales, 9+ stubs, 0 unit tests, API key hardcoded
- **Nivel de madurez**: Pre-produccion, requiere activacion y estabilizacion significativa

### 3.2 Modulos Planificados

---

#### EP-INV-001: Infraestructura Backend - Activacion y Correccion de Base
**Estado**: PENDIENTE
**Complejidad**: M
**Valor de Negocio**: Activa funcionalidad backend existente pero no conectada. Sin esta epica, el modulo completo no funciona. Es la base obligatoria.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: 6 blueprints registrados en app.py, 47 endpoints respondiendo, conftest.py con fixtures funcionales
2. **UX/UI**: N/A (backend)
3. **Rendimiento**: Todos los endpoints responden en <500ms con datos de prueba
4. **Seguridad**: API key leida de variable de entorno (no hardcoded), auth validada en todos los endpoints
5. **Accesibilidad**: N/A (backend)
6. **Integracion**: Modelos alineados con covacha_libs, imports unificados
7. **Error Handling**: Bugs conocidos corregidos (CategoryRepo.index, BrandRepo.index, server.py import)
8. **Persistencia**: DynamoDB tables verificadas, conftest con moto mock
9. **Multi-Tenant**: Todos los endpoints filtran por organization_id
10. **Observabilidad**: 99 tests ejecutables, >=80% pasando en primera ejecucion

**E2E Test Coverage**: N/A (infraestructura)

---

#### EP-INV-002: Gestion de Clientes - Hub Central del Modulo
**Estado**: PENDIENTE
**Complejidad**: L
**Valor de Negocio**: Hub central del modulo. Cada operacion de inventario pertenece a un cliente. Sin seleccion de cliente, no se puede operar. Permite importar clientes desde marketing o crear nuevos.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: CRUD de clientes (SpClient), importacion desde mf-marketing, seleccion como primera pantalla
2. **UX/UI**: Lista de clientes como pantalla inicial, busqueda con debounce, formulario de registro, modal de importacion
3. **Rendimiento**: Lista paginada server-side, busqueda debounce 300ms, auto-seleccion si solo 1 cliente
4. **Seguridad**: Super admin ve todos los clientes de todas las orgs, usuarios normales solo los suyos
5. **Accesibilidad**: Tabla accesible, formularios con labels, modal con focus trap
6. **Integracion**: Importa desde API de marketing, current_sp_client_id en localStorage + BroadcastChannel, X-SP-Client-Id header
7. **Error Handling**: Duplicados en importacion se reportan sin error, validacion RFC mexicano
8. **Persistencia**: SpClient en DynamoDB nueva tabla `covacha_sp_clients`, GSI por status
9. **Multi-Tenant**: Clientes aislados por organization_id, client_id en toda operacion posterior
10. **Observabilidad**: Clientes por organizacion, importaciones exitosas/fallidas

**E2E Test Coverage**: PENDIENTE

---

#### EP-INV-003: Catalogo de Productos y Categorias
**Estado**: PENDIENTE
**Complejidad**: L
**Valor de Negocio**: CRUD completo de productos con categorias jerarquicas, codigos de barras/SKU/QR, busqueda y scan, e import/export masivo.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: CRUD productos (multi-seccion), categorias con arbol jerarquico, generacion de codigos, scan de barras
2. **UX/UI**: Formulario multi-seccion (basica, precios, stock, proveedor, media, codigos), arbol expandible de categorias
3. **Rendimiento**: Busqueda con debounce, scan auto-redirect a detalle si 1 resultado
4. **Seguridad**: Productos filtrados por sp_client_id, sin X-SP-Client-Id retorna 400
5. **Accesibilidad**: Formularios con labels, arbol navegable por teclado
6. **Integracion**: CodeGeneratorService para SKU/EAN13/QR, upload a S3 para imagenes
7. **Error Handling**: Import CSV con reporte de errores por fila, SKUs duplicados reportados sin fallo
8. **Persistencia**: Productos en DynamoDB con GSI por sp_client_id, export CSV
9. **Multi-Tenant**: Productos aislados por organizacion y cliente
10. **Observabilidad**: Productos por cliente, busquedas mas frecuentes

**E2E Test Coverage**: PENDIENTE

---

#### EP-INV-004: Venues y Sucursales por Cliente
**Estado**: PENDIENTE
**Complejidad**: M
**Valor de Negocio**: Gestion de venues (sucursales/ubicaciones) por cliente. Cada venue tiene su propio inventario, almacen y punto de venta.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: CRUD de venues con ubicacion, horarios, contacto, warehouse asociado
2. **UX/UI**: Lista de venues con mapa, formulario de registro, detalle con info y stock
3. **Rendimiento**: Mapa lazy-loaded, lista paginada
4. **Seguridad**: Venues filtradas por sp_client_id
5. **Accesibilidad**: Mapa con alternativa textual, formularios accesibles
6. **Integracion**: Venue asociada a warehouse para stock, consumida por ventas y reportes
7. **Error Handling**: Validacion de direccion, venue no eliminable si tiene stock activo
8. **Persistencia**: Venues en DynamoDB por cliente
9. **Multi-Tenant**: Venues aisladas por organizacion y cliente
10. **Observabilidad**: Venues activas por cliente, stock por venue

**E2E Test Coverage**: PENDIENTE

---

#### EP-INV-005: Proveedores por Cliente
**Estado**: PENDIENTE
**Complejidad**: M
**Valor de Negocio**: Gestion de proveedores por cliente con catalogo de productos que proveen, historial de compras, y condiciones comerciales.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: CRUD de proveedores, catalogo de productos por proveedor, condiciones comerciales
2. **UX/UI**: Lista de proveedores, detalle con productos y historial, formulario de registro
3. **Rendimiento**: Lista paginada, busqueda por nombre/RFC
4. **Seguridad**: Proveedores filtrados por sp_client_id
5. **Accesibilidad**: Tablas y formularios accesibles
6. **Integracion**: Productos vinculados a proveedores, consumido por cotizaciones
7. **Error Handling**: Proveedor no eliminable si tiene productos activos vinculados
8. **Persistencia**: Proveedores en DynamoDB por cliente
9. **Multi-Tenant**: Proveedores aislados por organizacion y cliente
10. **Observabilidad**: Proveedores activos, compras por proveedor

**E2E Test Coverage**: PENDIENTE

---

#### EP-INV-006: Stock e Inventario Operativo
**Estado**: PENDIENTE
**Complejidad**: L
**Valor de Negocio**: Control de stock en tiempo real: entradas, salidas, ajustes, transferencias entre venues, alertas de stock minimo/maximo. Nucleo operativo del modulo.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Movimientos de stock (entrada, salida, ajuste, transferencia), alertas de stock min/max, resumen por venue
2. **UX/UI**: Dashboard de stock con indicadores visuales (rojo/amarillo/verde), formulario de ajuste, historial de movimientos
3. **Rendimiento**: Resumen de stock calculado en <500ms, alertas evaluadas en batch
4. **Seguridad**: Movimientos de stock requieren autorizacion, audit trail de ajustes
5. **Accesibilidad**: Indicadores de color con texto alternativo, tablas semanticas
6. **Integracion**: Movimientos generan historial, consumido por reportes y auditorias
7. **Error Handling**: Stock negativo prevenido (segun configuracion), motivo obligatorio en ajustes
8. **Persistencia**: MovementType (IN, OUT, ADJUST, TRANSFER) en DynamoDB
9. **Multi-Tenant**: Stock aislado por organizacion, cliente y venue
10. **Observabilidad**: Alertas de stock bajo, movimientos por tipo por dia

**E2E Test Coverage**: PENDIENTE

---

#### EP-INV-007: Sistema de Cotizaciones Inteligente
**Estado**: PENDIENTE
**Complejidad**: L
**Valor de Negocio**: Generacion de cotizaciones formales con productos del catalogo, precios por volumen, multiples monedas, y conversion a orden de compra.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Wizard de cotizacion, precios por volumen, multiples monedas, conversion a orden, PDF exportable
2. **UX/UI**: Wizard multi-paso, tabla de productos con cantidades y precios, preview PDF
3. **Rendimiento**: Calculo de totales en tiempo real, PDF generado en <5s
4. **Seguridad**: Cotizaciones firmadas digitalmente (opcional), acceso por rol
5. **Accesibilidad**: Formularios y tablas accesibles, PDF con estructura semantica
6. **Integracion**: Productos del catalogo (EP-INV-003), proveedores (EP-INV-005)
7. **Error Handling**: Validacion de stock disponible al crear cotizacion, precios vigentes
8. **Persistencia**: Cotizaciones en DynamoDB con estados (draft, sent, accepted, rejected)
9. **Multi-Tenant**: Cotizaciones aisladas por organizacion y cliente
10. **Observabilidad**: Cotizaciones por estado, tasa de conversion, monto promedio

**E2E Test Coverage**: PENDIENTE

---

#### EP-INV-008: Ventas y Cierre Diario por Cliente
**Estado**: PENDIENTE
**Complejidad**: L
**Valor de Negocio**: Registro de ventas por punto de venta, cierre diario con cuadre de caja, y generacion de tickets/facturas. **Funcionalidad completamente nueva** (no existe en backend ni frontend).

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Registro de venta (productos, cantidades, precios, descuentos, metodo de pago), cierre diario por venue
2. **UX/UI**: POS simplificado, busqueda rapida de productos, resumen de venta, ticket imprimible
3. **Rendimiento**: Registro de venta en <2s, cierre diario procesado en background
4. **Seguridad**: Ventas firmadas por usuario, cierre requiere supervisor
5. **Accesibilidad**: POS optimizado para uso rapido con teclado
6. **Integracion**: Decrementa stock automaticamente (EP-INV-006), genera movimiento de salida
7. **Error Handling**: Validacion de stock pre-venta, precio <= 0 no permitido, cierre no reversible
8. **Persistencia**: Ventas en DynamoDB por venue y fecha, cierre diario como snapshot
9. **Multi-Tenant**: Ventas aisladas por organizacion, cliente y venue
10. **Observabilidad**: Ventas por dia/venue, monto total, productos mas vendidos

**E2E Test Coverage**: PENDIENTE

---

#### EP-INV-009: Reportes y Analitica de Inventario
**Estado**: PENDIENTE
**Complejidad**: M
**Valor de Negocio**: Reportes de rotacion de inventario, valoracion de stock, tendencias de ventas, y productos mas/menos vendidos. Dashboard analitico para toma de decisiones.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Reportes de rotacion, valoracion (FIFO/LIFO/promedio), tendencias, top/bottom productos
2. **UX/UI**: Dashboard con graficas ECharts, filtros por periodo/venue/categoria, export PDF/CSV
3. **Rendimiento**: Reportes pre-calculados en batch nocturno, cache de resultados
4. **Seguridad**: Reportes accesibles solo para administradores
5. **Accesibilidad**: Graficas con datos tabulares alternativos
6. **Integracion**: Datos de ventas (EP-INV-008), stock (EP-INV-006), productos (EP-INV-003)
7. **Error Handling**: Si datos insuficientes, muestra mensaje informativo
8. **Persistencia**: Reportes calculados en DynamoDB con fecha de generacion
9. **Multi-Tenant**: Reportes aislados por organizacion y cliente
10. **Observabilidad**: Reportes generados por mes, queries lentas

**E2E Test Coverage**: PENDIENTE

---

#### EP-INV-010: Auditorias, Centros de Costo y Tareas
**Estado**: PENDIENTE
**Complejidad**: M
**Valor de Negocio**: Auditorias fisicas de inventario (conteo real vs sistema), centros de costo para control presupuestario, y sistema de tareas para coordinacion del equipo.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Auditorias fisicas (crear, ejecutar, reconciliar), centros de costo CRUD, tareas asignables
2. **UX/UI**: Wizard de auditoria, dashboard de centros de costo, tablero de tareas (kanban-like)
3. **Rendimiento**: Auditoria de 1000+ productos procesable en <30s
4. **Seguridad**: Auditorias firmadas por auditor, centros de costo con permisos por rol
5. **Accesibilidad**: Formularios accesibles, tablero navegable por teclado
6. **Integracion**: Auditoria compara stock sistema (EP-INV-006) vs conteo fisico
7. **Error Handling**: Diferencias detectadas generan alerta, ajustes requieren aprobacion
8. **Persistencia**: Auditorias con historial en DynamoDB, centros de costo por organizacion
9. **Multi-Tenant**: Auditorias y centros de costo aislados por organizacion y cliente
10. **Observabilidad**: Diferencias encontradas en auditorias, tareas completadas vs pendientes

**E2E Test Coverage**: PENDIENTE

---

#### EP-INV-011: Testing Backend - Cobertura Completa
**Estado**: PENDIENTE
**Complejidad**: L
**Valor de Negocio**: Suite de tests completa para el backend de inventario. Garantiza estabilidad y previene regresiones. Prerequisito para deploy en produccion.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Tests unitarios para todos los servicios, tests de integracion para endpoints
2. **UX/UI**: N/A (backend)
3. **Rendimiento**: Suite completa ejecuta en <5 minutos
4. **Seguridad**: Tests de autenticacion y autorizacion, tests de filtrado por organization_id
5. **Accesibilidad**: N/A (backend)
6. **Integracion**: Mocks con moto para DynamoDB, fixtures para todos los modelos
7. **Error Handling**: Tests de edge cases (datos vacios, nulos, limites, duplicados)
8. **Persistencia**: Tests de repositorios con DynamoDB mock
9. **Multi-Tenant**: Tests de aislamiento (org A no ve datos de org B)
10. **Observabilidad**: Cobertura >= 98%, reporte publicado en CI

**E2E Test Coverage**: N/A (es el testing mismo)

---

#### EP-INV-012: Testing Frontend - Cobertura Completa
**Estado**: PENDIENTE
**Complejidad**: L
**Valor de Negocio**: Suite de tests completa para el frontend de inventario. Garantiza calidad de UI y previene regresiones visuales.

**Criterios de Aceptacion (10):**
1. **Funcional Core**: Tests unitarios Karma+Jasmine para componentes, tests Jest para servicios, E2E Playwright
2. **UX/UI**: Tests de rendering con OnPush, tests de interaccion de usuario
3. **Rendimiento**: Suite unitaria ejecuta en <3 minutos
4. **Seguridad**: Tests de guards y permisos
5. **Accesibilidad**: Tests de accesibilidad con axe-core
6. **Integracion**: Tests de adaptadores con mocks HTTP
7. **Error Handling**: Tests de estados de error en componentes
8. **Persistencia**: Tests de use cases con mocks de ports
9. **Multi-Tenant**: Tests de filtrado por client_id y organization_id
10. **Observabilidad**: Cobertura >= 90%, reporte publicado en CI

**E2E Test Coverage**: Epica de testing cubre E2E

---

## 4. Matriz de Calidad Global

| Producto | Epicas Totales | Completadas | En Progreso | Pendientes | Coverage E2E | Score |
|----------|---------------|-------------|-------------|------------|--------------|-------|
| Marketing Digital | 30 | 18 (60%) | 5 (17%) | 7 (23%) | 30 spec files | 77% |
| SuperPago SPEI | 20 | 19 (95%) | 0 (0%) | 1 (5%) | Indirecto (backend + scaffold) | 95% |
| Inventario | 12 | 0 (0%) | 0 (0%) | 12 (100%) | 3 smoke tests | 0% |
| **Total** | **62** | **37 (60%)** | **5 (8%)** | **20 (32%)** | | **57%** |

### Cobertura de Testing por Producto

| Producto | Unit Tests | E2E Specs | Framework | Estado |
|----------|-----------|-----------|-----------|--------|
| Marketing (mf-marketing) | 459+ passing | 30 spec files | Karma+Jasmine, Jest, Playwright | Activo |
| SuperPago (covacha-payment) | 786+ passing | Via frontend scaffold | pytest | Activo |
| SuperPago (mf-sp) | Scaffold tests | Via estructura multi-tier | Karma+Jasmine | Activo |
| Inventario (covacha-inventory) | 99 escritos, 0 ejecutables | 3 smoke tests | pytest (broken) | Critico |
| Inventario (mf-inventory) | 0 | 3 basics | N/A | Critico |

---

## 5. Mapa de Dependencias entre Productos

```
┌───────────────────────────────────────────────────────────────────────┐
│                           mf-core (Shell)                              │
│                     Host de todos los micro-frontends                   │
│                                                                        │
│  Provee: SharedStateService (auth, user, tenant, organization)         │
│  Registra remotes: mfMarketing, mfSP, mfInventory, mfDashboard, etc. │
└─────┬──────────────────────┬───────────────────────┬──────────────────┘
      │                      │                       │
      ▼                      ▼                       ▼
┌───────────┐      ┌────────────────┐      ┌──────────────────┐
│mf-marketing│     │     mf-sp      │     │  mf-inventory    │
│  :4206    │      │     :4212     │      │     :4211        │
│           │      │               │      │                  │
│ 30 epicas │      │  20 epicas    │      │  12 epicas       │
│ Agencia   │      │  Pagos SPEI   │      │  Inventario      │
│ digital   │      │  Multi-tier   │      │  Multi-cliente   │
└─────┬─────┘      └───────┬───────┘      └────────┬─────────┘
      │                     │                       │
      │ Importa             │                       │
      │ clientes ──────────►│                       │
      │                     │                       │
      │ Importa clientes ──────────────────────────►│
      │ marketing                                   │
      │                     │                       │
      │ Carga componentes ──────────────────────────►│
      │ de mf-inventory     │                       │
      │ via Federation      │                       │
      │                     │                       │
      ▼                     ▼                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                        Backend APIs                                │
│                                                                    │
│  covacha-core (:5001)     - Organizaciones, clientes, social,     │
│                             estrategias, promociones, brand kit   │
│                                                                    │
│  covacha-botia (:5002)    - Agentes IA, funnels, chatbot,        │
│                             WhatsApp marketing                    │
│                                                                    │
│  covacha-inventory (:5003) - Productos, stock, venues,            │
│                              cotizaciones, ventas                  │
│                                                                    │
│  covacha-payment (:5004)  - Cuentas SPEI, ledger, transferencias,│
│                             Cash-In/Out, subastas                 │
│                                                                    │
│  covacha-webhook (:5006)  - Webhooks SPEI, WhatsApp, Facebook    │
│                                                                    │
│  covacha-libs             - Modelos compartidos (Pydantic)        │
└──────────────────────────────────────────────────────────────────┘

Dependencias Cross-Producto:
━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. mf-marketing → mf-inventory: Carga componentes de productos y
   cotizaciones via Native Federation (loadInventoryModule)

2. mf-inventory → mf-marketing: Importa catalogo de clientes de
   marketing para no duplicar registros

3. mf-marketing → covacha-botia: Los 10 agentes IA (EP-MK-014 a
   EP-MK-023) viven en covacha-botia y consumen APIs de covacha-core

4. mf-sp → covacha-botia: El agente IA WhatsApp (EP-SP-017/018) vive
   en covacha-botia y consume APIs de covacha-payment

5. Todos los MFs → mf-core: SharedStateService para auth, tenant,
   organizacion activa. BroadcastChannel para sincronizacion.
```

---

## 6. Riesgos y Recomendaciones

### Riesgos Criticos

| # | Riesgo | Producto | Impacto | Probabilidad | Mitigacion Propuesta |
|---|--------|----------|---------|--------------|---------------------|
| 1 | **Inventario sin tests ejecutables** | Inventario | Alto - no se puede deployar con confianza | Confirmado | EP-INV-001 es prerequisito absoluto: activar conftest.py y ejecutar los 99 tests existentes |
| 2 | **API key hardcoded en mf-inventory** | Inventario | Alto - vulnerabilidad de seguridad | Confirmado | US-INV-005 debe priorizarse: mover a environment.ts |
| 3 | **Rate limits de Facebook/IG Graph API** | Marketing | Medio - recopilacion de metricas incompleta | Alta | Batch requests, cache de metricas, retry con backoff. Critico para EP-MK-024 (reportes) y EP-MK-015 (monitoring) |
| 4 | **Tokens de Meta expirados** | Marketing | Medio - funcionalidades sociales dejan de operar | Alta | Validacion proactiva de tokens, notificacion al usuario, redirect a reconexion |
| 5 | **DynamoDB items > 400KB** | SPEI, Marketing | Medio - operaciones fallan | Media | Diseño single-table con items separados (REPORT#/PLATFORM#, REPORT#/POST#) |
| 6 | **Componentes > 1000 lineas en mf-inventory** | Inventario | Bajo - violacion de convenciones | Confirmado | QuotationForm (~1845 lineas) y QuotationDetail (~1934 lineas) deben dividirse |

### Deuda Tecnica Identificada

| # | Deuda | Producto | Prioridad | Estimacion |
|---|-------|----------|-----------|------------|
| 1 | conftest.py vacio en covacha-inventory | Inventario | P0 | 2 dev-days |
| 2 | 2 de 7 blueprints registrados en covacha-inventory | Inventario | P0 | 1 dev-day |
| 3 | Modelos desalineados (locales vs covacha-libs) | Inventario | P0 | 2 dev-days |
| 4 | 0 unit tests en mf-inventory frontend | Inventario | P1 | 5 dev-days |
| 5 | Frontend stubs pendientes para EP-SP-020 (Cash/Subasta/IA) | SPEI | P2 | 10 dev-days |
| 6 | Frontend pendiente para EP-MK-025 (Meta AI components) | Marketing | P1 | 8 dev-days |
| 7 | Frontend pendiente para EP-MK-028 (Funnels builder UI) | Marketing | P1 | 10 dev-days |
| 8 | Documentacion OpenAPI no generada para varios endpoints | Cross | P2 | Continuo |

### Recomendaciones Estrategicas

1. **Priorizar Inventario EP-INV-001**: El producto de inventario esta en estado critico. Los 99 tests escritos no ejecutan, hay API keys hardcoded, y la mayoria de endpoints no responde. EP-INV-001 debe ser la primera prioridad para estabilizar el producto.

2. **Completar frontends pendientes de Marketing**: EP-MK-025 (Meta AI), EP-MK-028 (Funnels), y EP-MK-029 (Chatbot en landing) tienen backend completado pero componentes frontend pendientes. Completar estos cierra funcionalidad ya desarrollada.

3. **Iniciar EP-MK-024 (Reportes Sociales)**: Es una funcionalidad de alto valor con modelos de dominio ya definidos y 7 user stories detalladas. Diferencia competitiva significativa al eliminar la creacion manual de reportes.

4. **Mantener cobertura de testing >= 98%**: El pipeline de CI ya valida coverage. No relajar este umbral. Para inventario, establecer el mismo estandar desde EP-INV-001.

5. **Considerar Agent Teams para trabajo paralelo**: Con 3 productos independientes, usar Agent Teams de Claude Code para avanzar en paralelo: un teammate en inventario (EP-INV-001), otro en frontend marketing (EP-MK-025 components), otro en reportes sociales (EP-MK-024).

---

## Apendice: Indice de Archivos Fuente

| Archivo | Ubicacion | Contenido |
|---------|-----------|-----------|
| MARKETING-EPICS.md | `products/marketing/` | EP-MK-001 a EP-MK-013 (38 US) |
| MARKETING-AI-AGENTS-EPICS.md | `products/marketing/` | EP-MK-014 a EP-MK-023 (55 US) |
| MARKETING-SOCIAL-REPORTS-EPICS.md | `products/marketing/` | EP-MK-024 (7 US) |
| MARKETING-META-AI-EPICS.md | `products/marketing/` | EP-MK-025 (7 US) |
| MARKETING-PROMOTIONS-FUNNELS-EPICS.md | `products/marketing/` | EP-MK-026 a EP-MK-030 (33 US) |
| SPEI-PRODUCT-PLAN.md | `products/superpago/` | EP-SP-001 a EP-SP-010 (39 US) |
| SPEI-FRONTEND-EPICS-MULTI-TIER.md | `products/superpago/` | EP-SP-007/008/011/012/013 (27 US) |
| SPEI-EXPANSION-EPICS.md | `products/superpago/` | EP-SP-014 a EP-SP-020 (33 US) |
| INVENTORY-EPICS.md | `products/inventory/` | EP-INV-001 a EP-INV-012 (65 US) |
