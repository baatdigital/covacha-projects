# Propuesta de Nuevos Productos y Lineas de Negocio

**Fecha**: 2026-03-10
**Estratega**: Business Innovation Agent
**Version**: 1.0
**Ecosistema**: SuperPago / BaatDigital / AlertaTribunal

---

## Contexto del Ecosistema

### Capacidades Existentes

| Capacidad | Estado | Repo/MF |
|-----------|--------|---------|
| Multi-tenant SaaS platform (Angular 21 + Python/Flask + AWS) | Produccion | mf-core, covacha-core |
| Procesamiento de pagos SPEI (in/out, ledger partida doble) | Produccion | covacha-payment |
| Transferencias inter-organizacion (sin costo SPEI) | Backend completo | covacha-payment |
| Cash-In / Cash-Out (red de puntos fisicos) | Backend completo | covacha-payment |
| Subasta de efectivo (mercado de liquidez) | Backend completo | covacha-payment |
| Marketing automation + social media management | Produccion | mf-marketing, covacha-core |
| Generacion de contenido con IA (OpenAI, Anthropic, Google) | Produccion | mf-marketing |
| 10 agentes IA especializados para marketing | Planificacion | covacha-botia |
| WhatsApp Business API (chatbot + notificaciones) | Produccion | covacha-webhook, covacha-botia |
| Agente IA WhatsApp para operaciones financieras | Backend completo | covacha-botia |
| Landing pages + funnels de venta + SEO | Produccion | mf-marketing |
| Inventario y cotizaciones | Produccion | mf-inventory, covacha-inventory |
| CRM basico de clientes de agencia | Produccion | mf-marketing |
| Brand kit management | Produccion | mf-marketing |
| Facebook/Instagram Ads (campaign builder, insights, A/B test) | Produccion | mf-marketing |
| Module Federation micro-frontends | Produccion | Todos los mf-* |
| Notificaciones en tiempo real (BroadcastChannel) | Produccion | mf-core |
| Google Drive + S3 almacenamiento hibrido | Produccion | mf-marketing |

### Infraestructura Reutilizable

| Componente | Tecnologia | Reutilizacion |
|-----------|-----------|---------------|
| Base de datos | DynamoDB (single-table design, GSIs) | Cualquier producto nuevo |
| CDN | CloudFront (E3A0H41AD1MAWR) | Cualquier MF nuevo |
| Compute | Lambda + API Gateway + EC2 | Cualquier backend nuevo |
| Frontend | Native Federation, Angular 21 | Cualquier MF nuevo en <1 dia de scaffold |
| Auth | JWT + multi-tenant + roles + permisos | Cualquier producto nuevo |
| Comunicacion | WhatsApp Business API + BroadcastChannel | Cualquier canal conversacional |
| Pagos | Motor SPEI + ledger + cuentas | Cualquier producto con flujo de dinero |
| IA | Multi-provider (OpenAI, Bedrock, Anthropic) | Cualquier feature de IA |
| Estado compartido | SharedStateService + localStorage | Cualquier MF nuevo |
| CI/CD | GitHub Actions -> S3 -> CloudFront | Cualquier MF/backend nuevo |

### Datos de Mercado Clave (2025-2026)

| Metrica | Valor | Fuente |
|---------|-------|--------|
| Mercado SaaS Mexico | $2,000 MDD (17% de LATAM) | EBANX/EntreVeredas |
| SaaS Mexico proyeccion 2030 | $19,986 MDD | Grand View Research |
| PyMEs que usan IA en Mexico | 64% (73% planean aumentar inversion) | Aspel/Siigo |
| PyMEs no digitalizadas en Mexico | 76% | IFT Mexico |
| Penetracion WhatsApp en Mexico | 93% | YCloud/AuroraInbox |
| Mercado CRM Mexico 2024 | $843 MDD (-> $2,208 MDD en 2033) | IMARC Group |
| Mercado e-invoicing Mexico 2024 | $190 MDD (-> $778 MDD en 2033) | IMARC Group |
| E-commerce Mexico 2025 | $54,400 MDD | IMARC Group |
| Social commerce Mexico 2025 | $5,090 MDD (-> $10,520 MDD en 2030) | GlobeNewsWire |
| Startups IA en Mexico | 5x mas capital que no-IA en 2025 | Crunchbase |
| PyMEs = share de revenue SaaS | 70% del mercado SaaS LATAM | Antom/Knowledge |

---

## Productos Propuestos

---

### PRODUCTO 1: CobrarIA - CRM Conversacional para PyMEs

**Tagline**: "Tu equipo de ventas en WhatsApp, potenciado por IA"

#### Problema

Las PyMEs mexicanas (4.9 millones de empresas) gestionan sus ventas por WhatsApp de forma caotica: mensajes perdidos, sin seguimiento, sin CRM, sin metricas. El 80% de las interacciones comerciales iniciales en LATAM ocurren por mensajeria, pero el 76% de las PyMEs no tiene herramientas digitales integradas. Los CRMs existentes (HubSpot, Salesforce) son caros, en ingles, y no tienen WhatsApp como canal nativo sino como add-on.

#### Solucion

CRM conversacional donde WhatsApp es el canal primario (no un plugin). Incluye:
- Pipeline de ventas visual alimentado desde conversaciones de WhatsApp
- Bot IA que califica leads automaticamente (pregunta presupuesto, timeline, necesidad)
- Cotizaciones enviadas y firmadas desde WhatsApp (reutiliza mf-inventory/cotizaciones)
- Cobros via link de pago SPEI dentro de la conversacion
- Dashboard de metricas de ventas en tiempo real
- Catalogo de productos compartible via WhatsApp (reutiliza mf-inventory)

#### Mercado Objetivo

- **Primario**: PyMEs de servicios y comercio (1-50 empleados) que ya venden por WhatsApp
- **Secundario**: Freelancers y profesionistas independientes (contadores, abogados, dentistas)
- **TAM Mexico**: $1,200 MDD (segmento PyMEs del mercado CRM de $2,208 MDD)
- **TAM LATAM**: $4,800 MDD
- **SAM**: $360 MDD (PyMEs que ya usan WhatsApp Business y buscan CRM)
- **SOM (Year 1)**: $3.6 MDD (1,000 clientes pagando promedio $300 MXN/mes)

#### Modelo de Revenue

| Plan | Precio/mes (MXN) | Features | Target |
|------|-------------------|----------|--------|
| Starter | $299 | 1 usuario, 500 contactos, bot basico, pipeline | Freelancers |
| PyME | $799 | 5 usuarios, 5,000 contactos, bot IA, cotizaciones, cobros SPEI | PyMEs pequenas |
| Business | $1,999 | 15 usuarios, ilimitado, IA avanzada, multi-canal, API | PyMEs medianas |
| Enterprise | $4,999 | Custom, SLA, integraciones, white-label | Empresas |

#### Reutilizacion de Infra Existente

- **Backend (70%)**: covacha-core (organizaciones, usuarios, permisos), covacha-webhook (WhatsApp), covacha-botia (IA conversacional), covacha-payment (cobros SPEI), covacha-inventory (productos, cotizaciones)
- **Frontend (40%)**: mf-marketing (componentes de clientes, dashboard, analytics), shared-state, http-service
- **Nuevo desarrollo**: mf-crm (MF nuevo), adaptadores de pipeline CRM, modelos de lead scoring, UI de inbox unificado
- **Estimacion**: 60% reutilizado, 40% nuevo

#### Competencia

| Competidor | Precio/mes | Debilidad vs Nosotros |
|------------|-----------|----------------------|
| Leadsales | $499-$1,499 MXN | Sin pagos integrados, sin inventario, sin IA avanzada |
| Kommo (ex-amoCRM) | $249-$749 USD | Caro para PyMEs mexicanas, sin SPEI, UI en ingles |
| HubSpot Free | $0-$800 USD | WhatsApp es add-on, sin pagos, complejo para PyMEs |
| Respond.io | $99-$299 USD | Sin CRM real, sin pagos, enfoque enterprise |
| Aurora Inbox | $299-$999 MXN | Sin cobros, sin inventario, sin funnels |

**Ventaja competitiva**: Unico CRM que integra WhatsApp nativo + cobros SPEI + inventario + IA, todo en espanol y con precios en pesos.

#### Go-to-Market

1. **Fase 1 (0-3 meses)**: Beta con 50 clientes existentes de BaatDigital. Partnership con 3 camaras de comercio (CANACO). Contenido educativo en TikTok/Instagram ("Como vender mas por WhatsApp").
2. **Fase 2 (3-9 meses)**: Lanzamiento publico. Programa de referidos (1 mes gratis por referido). Integraciones con Shopify Mexico y Mercado Libre. Webinars semanales.
3. **Fase 3 (9-18 meses)**: Expansion a Colombia y Peru. API publica para integradores. Marketplace de templates de bots.

#### Metricas de Exito (12 meses)

- Users: 2,500 cuentas activas
- MRR: $1.5 MDP ($90K USD)
- Churn: <5% mensual
- NPS: >50

#### Esfuerzo de Desarrollo

- **Tiempo**: 14 semanas (MVP funcional en 8)
- **Equipo**: 2 backend, 2 frontend, 1 IA/ML, 1 diseno
- **Costo estimado**: $1.2 MDP (~$70K USD)

#### Score de Oportunidad: 9.5/10

> Maxima sinergia con infra existente. Mercado enorme y desatendido. Revenue recurrente desde dia 1.

---

### PRODUCTO 2: FacturaYA - Facturacion Electronica con IA

**Tagline**: "Factura en 10 segundos desde WhatsApp"

#### Problema

En Mexico, TODA transaccion debe documentarse con CFDI 4.0 (mandato SAT). Las PyMEs gastan 2-4 horas diarias en facturacion. Los PAC (Proveedores Autorizados de Certificacion) existentes tienen interfaces anticuadas. El 68% de las PyMEs luchan con la digitalizacion. Con las nuevas reglas SAT 2026 (materialidad, validacion estricta, acceso en tiempo real a datos), la demanda de herramientas simples crecera exponencialmente.

#### Solucion

- Emision de CFDI 4.0 via WhatsApp ("Facturame $5,000 a nombre de Empresa X, RFC: ABC123")
- Bot IA que completa datos faltantes consultando directorio del SAT
- Portal web para facturas masivas y complementos de pago
- Integracion automatica con cobros SPEI (al recibir pago, se genera factura)
- Dashboard de obligaciones fiscales (IVA retenido, ISR, etc.)
- Cancelacion y sustitucion de CFDI desde WhatsApp
- Exportacion para contador (XML + PDF)

#### Mercado Objetivo

- **Primario**: PyMEs y micro-negocios (tienditas, profesionistas, freelancers)
- **Secundario**: Contadores que manejan 10-50 clientes
- **TAM Mexico**: $778 MDD (mercado e-invoicing proyectado a 2033)
- **TAM LATAM**: $2,500 MDD (facturacion electronica crece en toda la region)
- **SAM**: $234 MDD (PyMEs que necesitan solucion simple y asequible)
- **SOM (Year 1)**: $4.8 MDD (2,000 clientes, $200 MXN/mes promedio)

#### Modelo de Revenue

| Plan | Precio/mes (MXN) | Features | Target |
|------|-------------------|----------|--------|
| Micro | $149 | 50 facturas/mes, WhatsApp, 1 RFC | Freelancers |
| PyME | $399 | 300 facturas/mes, complementos, multi-RFC, reportes | PyMEs |
| Contador | $999 | 1,000 facturas, 20 RFCs, portal multi-cliente, exportacion masiva | Contadores |
| Enterprise | $2,499 | Ilimitado, API, integracion ERP, soporte prioritario | Empresas medianas |

#### Reutilizacion de Infra Existente

- **Backend (50%)**: covacha-core (orgs, auth), covacha-webhook (WhatsApp), covacha-botia (bot IA), covacha-payment (vinculacion pago-factura)
- **Frontend (30%)**: Shell multi-tenant, shared-state, http-service, componentes de dashboard
- **Nuevo desarrollo**: Modulo PAC (certificacion con SAT), modelos CFDI 4.0, motor de complementos, portal de contador, mf-facturacion
- **Estimacion**: 40% reutilizado, 60% nuevo (regulatorio es pesado)

#### Competencia

| Competidor | Precio/mes | Debilidad vs Nosotros |
|------------|-----------|----------------------|
| Facturama | $299-$999 MXN | Sin WhatsApp, sin cobros integrados, UI anticuada |
| Gigstack | $199-$599 MXN | Sin WhatsApp nativo, sin SPEI, enfoque API |
| Aspel (Siigo) | $499-$1,999 MXN | Software pesado, curva de aprendizaje alta |
| Bind ERP | $599-$2,999 MXN | Demasiado complejo para micro PyMEs |
| CONTPAQi | $500-$3,000 MXN | On-premise legacy, no conversacional |

**Ventaja competitiva**: Primera plataforma que permite facturar desde WhatsApp con IA, vinculada automaticamente a cobros SPEI.

#### Go-to-Market

1. **Fase 1 (0-3 meses)**: MVP con 100 beta testers de la red SuperPago. Partnership con 5 despachos contables. Certificacion como PAC ante el SAT.
2. **Fase 2 (3-9 meses)**: Lanzamiento publico. Campana "Factura en WhatsApp" en redes. Integracion con CobrarIA. Free tier de 10 facturas/mes como gancho.
3. **Fase 3 (9-18 meses)**: Modulo de nomina. Complemento carta porte. Expansion a regimenes fiscales especificos (RESICO, plataformas digitales).

#### Metricas de Exito (12 meses)

- Users: 3,000 cuentas activas
- MRR: $900K MXN ($54K USD)
- Facturas emitidas: 500,000/mes
- Churn: <4% mensual

#### Esfuerzo de Desarrollo

- **Tiempo**: 18 semanas (MVP en 10, certificacion PAC en paralelo)
- **Equipo**: 2 backend, 1 frontend, 1 fiscal/compliance, 1 QA
- **Costo estimado**: $1.8 MDP (~$105K USD)

#### Score de Oportunidad: 8.5/10

> Mercado regulado = barrera de entrada pero tambien foso competitivo. Sinergia con pagos SPEI es diferenciador unico.

---

### PRODUCTO 3: TiendaClick - Social Commerce Builder

**Tagline**: "Tu tienda online en Instagram y WhatsApp, lista en 5 minutos"

#### Problema

El social commerce en Mexico alcanza $5,090 MDD en 2025 y crecera a $10,520 MDD en 2030. Pero las PyMEs venden por Instagram/WhatsApp sin catalogo digital, sin carrito, sin cobros automaticos. Shopify es caro ($29+ USD/mes) y esta disenado para e-commerce tradicional, no para social sellers. El 40% del e-commerce en Mexico ya pasa por redes sociales, pero sin herramientas adecuadas.

#### Solucion

- Catalogo digital con link compartible en bio de Instagram/WhatsApp
- Carrito de compras dentro de WhatsApp (bot conversacional)
- Cobros SPEI instantaneos con confirmacion automatica
- Gestion de pedidos y envios desde dashboard
- Landing pages de producto (reutiliza landing editor de mf-marketing)
- Instagram Shopping sync automatico
- Notificaciones de pedido al comprador via WhatsApp
- Mini-POS para ventas presenciales con QR

#### Mercado Objetivo

- **Primario**: Social sellers (Instagram shops, revendedoras, emprendedoras)
- **Secundario**: Pequenos comercios que quieren venta online sin Shopify
- **TAM Mexico**: $5,090 MDD (social commerce 2025)
- **TAM LATAM**: $18,000 MDD
- **SAM**: $1,500 MDD (social sellers que necesitan herramientas)
- **SOM (Year 1)**: $6 MDD (5,000 tiendas, $100 MXN/mes promedio)

#### Modelo de Revenue

| Plan | Precio/mes (MXN) | Features | Target |
|------|-------------------|----------|--------|
| Free | $0 | 10 productos, link catalogo, cobros SPEI (comision 2.5%) | Emprendedores |
| Starter | $149 | 100 productos, bot WhatsApp, cobros (1.5% comision) | Social sellers |
| Pro | $499 | Ilimitado, Instagram sync, envios, 0.8% comision | Tiendas activas |
| Business | $1,299 | Multi-sucursal, API, analytics avanzado, 0.5% comision | Comercios |

**Revenue adicional**: Comision por transaccion (0.5%-2.5% segun plan).

#### Reutilizacion de Infra Existente

- **Backend (65%)**: covacha-core (orgs), covacha-payment (SPEI cobros), covacha-inventory (productos, catalogo), covacha-webhook (WhatsApp), covacha-botia (bot de compras)
- **Frontend (50%)**: mf-marketing (landing editor, media library), mf-inventory (productos), shared-state
- **Nuevo desarrollo**: Motor de carrito conversacional, checkout flow, gestion de envios, sync Instagram Shopping, mf-tienda
- **Estimacion**: 55% reutilizado, 45% nuevo

#### Competencia

| Competidor | Precio/mes | Debilidad vs Nosotros |
|------------|-----------|----------------------|
| Shopify | $29-$299 USD | Caro, no social-first, SPEI limitado, en ingles |
| Tiendanube | $449-$2,499 MXN | No WhatsApp nativo, no IA, enfoque web tradicional |
| Ecwid | $0-$89 USD | Sin WhatsApp commerce, sin SPEI |
| Kichink (cerrado) | - | Ya no opera, dejo hueco en mercado |
| WhatsApp Catalog | $0 | Limitado, sin cobros, sin analytics |

**Ventaja competitiva**: Social-first (WhatsApp + Instagram como canal primario), cobros SPEI nativos (sin intermediario), modelo freemium + comision.

#### Go-to-Market

1. **Fase 1 (0-3 meses)**: Beta con 200 social sellers de comunidades de Facebook ("Emprendedoras Mexico"). Partnership con influencers de emprendimiento. Free tier como gancho viral.
2. **Fase 2 (3-9 meses)**: Campana TikTok/Reels mostrando "Crea tu tienda en 5 min". Integraciones con paqueterias (Estafeta, Fedex, 99 Minutos). Programa de embajadores.
3. **Fase 3 (9-18 meses)**: Marketplace de vendedores. Creditos a social sellers basados en ventas (cross-sell con SuperPago). Expansion a Colombia.

#### Metricas de Exito (12 meses)

- Tiendas activas: 8,000
- GMV (Gross Merchandise Value): $50 MDP/mes
- MRR: $1.2 MDP ($72K USD) + comisiones
- Revenue total: $3 MDP/mes ($180K USD)
- Churn: <8% mensual

#### Esfuerzo de Desarrollo

- **Tiempo**: 12 semanas (MVP en 6)
- **Equipo**: 2 backend, 2 frontend, 1 UX/UI
- **Costo estimado**: $1 MDP (~$60K USD)

#### Score de Oportunidad: 9/10

> Mercado en explosion. Alto reuso de infra. Modelo freemium + comision = revenue compuesto. Potencial viral.

---

### PRODUCTO 4: CobraBot - Bot de Cobranza Inteligente por WhatsApp

**Tagline**: "Recupera cartera vencida mientras duermes"

#### Problema

En Mexico, las PyMEs pierden entre 5-15% de sus ingresos por cuentas incobrables. La cobranza manual es costosa, incomoda y poco efectiva. Los call centers de cobranza son agresivos y regulados. No existe una solucion conversacional, empatitica y automatizada que cobre por WhatsApp respetando la NOM-179 y la Ley de Proteccion al Consumidor.

#### Solucion

- Bot IA que contacta deudores por WhatsApp con mensajes empatiticos y personalizados
- Secuencias de cobranza configurables (recordatorio suave -> urgente -> ultimatum)
- Link de pago SPEI directo en la conversacion
- Planes de pago (parcialidades) negociados por el bot
- Horarios de contacto configurables (respeta regulacion)
- Dashboard de recuperacion con metricas por campana
- Escalacion automatica a agente humano cuando el bot no resuelve
- Integracion con facturacion (emite complemento de pago al cobrar)

#### Mercado Objetivo

- **Primario**: PyMEs con cartera de credito (ferreterias, distribuidoras, profesionistas)
- **Secundario**: Despachos de cobranza, instituciones de microfinanzas, cooperativas
- **TAM Mexico**: $800 MDD (servicios de cobranza)
- **TAM LATAM**: $3,200 MDD
- **SAM**: $240 MDD (PyMEs con cartera vencida que no usan call center)
- **SOM (Year 1)**: $3.6 MDD (300 clientes, $1,000 MXN/mes promedio)

#### Modelo de Revenue

| Plan | Precio/mes (MXN) | Features | Target |
|------|-------------------|----------|--------|
| Starter | $499 | 200 contactos, 1 secuencia, bot basico | PyMEs pequenas |
| Professional | $1,499 | 1,000 contactos, secuencias ilimitadas, IA negociadora, planes de pago | PyMEs medianas |
| Agency | $3,999 | 5,000 contactos, multi-empresa, reportes avanzados, API | Despachos |
| Enterprise | $9,999 | Ilimitado, compliance avanzado, SLA, integracion ERP | Financieras |

**Revenue adicional**: Comision por exito (1-3% del monto recuperado, configurable).

#### Reutilizacion de Infra Existente

- **Backend (70%)**: covacha-webhook (WhatsApp), covacha-botia (bot IA con secuencias), covacha-payment (cobros SPEI, links de pago), covacha-core (orgs, permisos)
- **Frontend (35%)**: mf-marketing (dashboards, analytics), shared-state
- **Nuevo desarrollo**: Motor de secuencias de cobranza, modelos de negociacion IA, compliance engine (NOM-179), reportes de recuperacion
- **Estimacion**: 55% reutilizado, 45% nuevo

#### Competencia

| Competidor | Precio/mes | Debilidad vs Nosotros |
|------------|-----------|----------------------|
| Truora | $500-$2,000 USD | Enfoque verificacion, no cobranza pura |
| Auronix | Custom | Enterprise-only, caro para PyMEs |
| YaloChat | Custom | Enfoque retail, no cobranza especializada |
| Despachos de cobranza | 15-30% de lo cobrado | Agresivos, danan reputacion, caros |
| Llamadas manuales | Tiempo empleados | Ineficiente, costoso, sin metricas |

**Ventaja competitiva**: Cobranza empatica con IA + cobro SPEI en la misma conversacion + compliance built-in.

#### Go-to-Market

1. **Fase 1 (0-3 meses)**: Piloto con 30 distribuidoras de la red SuperPago. Caso de estudio: "Recuperamos X% de cartera vencida en 30 dias".
2. **Fase 2 (3-9 meses)**: Campana dirigida a despachos contables (canal de distribucion). Partnership con AMFE (Asoc. Mexicana de Finanzas Empresariales).
3. **Fase 3 (9-18 meses)**: Modelo de "Cobranza como servicio" (CaaS) para fintechs. Expansion a microfinancieras.

#### Metricas de Exito (12 meses)

- Clientes activos: 500
- MRR: $750K MXN ($45K USD)
- Monto recuperado para clientes: $50 MDP
- Tasa de recuperacion promedio: 35%
- Churn: <3% mensual

#### Esfuerzo de Desarrollo

- **Tiempo**: 10 semanas (MVP en 6)
- **Equipo**: 2 backend, 1 frontend, 1 IA/NLP
- **Costo estimado**: $900K MXN (~$53K USD)

#### Score de Oportunidad: 8.5/10

> Alto valor percibido (recupera dinero perdido). Revenue recurrente + comision por exito. Bajo churn (si funciona, no se van).

---

### PRODUCTO 5: ReservaFacil - Sistema de Reservaciones con Pagos

**Tagline**: "Reservas, pagos y recordatorios, todo en WhatsApp"

#### Problema

Restaurantes, salones de belleza, consultorios medicos, dentistas, y estudios de fitness en Mexico (600,000+ negocios) manejan reservaciones por telefono, WhatsApp manual o libretas fisicas. Las no-shows cuestan entre 15-30% del ingreso potencial. Calendly y similares no tienen pagos en pesos ni WhatsApp nativo.

#### Solucion

- Link de reservacion compartible (landing page con horarios disponibles)
- Bot WhatsApp para agendar citas ("Quiero una cita el martes a las 3")
- Anticipo/pago completo via SPEI al reservar (reduce no-shows de 30% a <5%)
- Recordatorios automaticos por WhatsApp (24h, 2h, "estas en camino?")
- Calendario visual para el negocio con vista por sucursal/profesional
- Lista de espera automatica
- Resenas post-servicio via WhatsApp
- Facturacion automatica del servicio (cross-sell con FacturaYA)

#### Mercado Objetivo

- **Primario**: Salones de belleza, barber shops, spas (150,000+ en Mexico)
- **Secundario**: Consultorios medicos/dentales, restaurantes, estudios fitness
- **TAM Mexico**: $600 MDD (scheduling + pagos para servicios)
- **TAM LATAM**: $2,400 MDD
- **SAM**: $180 MDD (negocios de servicios que cobran cita)
- **SOM (Year 1)**: $2.4 MDD (2,000 negocios, $100 MXN/mes promedio + comision)

#### Modelo de Revenue

| Plan | Precio/mes (MXN) | Features | Target |
|------|-------------------|----------|--------|
| Free | $0 | 1 profesional, 30 citas/mes, recordatorios WhatsApp | Independientes |
| Pro | $199 | 3 profesionales, ilimitado, pagos SPEI (1.5% comision) | Salones pequenos |
| Business | $599 | 10 profesionales, multi-sucursal, analytics, 0.8% comision | Salones medianos |
| Enterprise | $1,499 | Ilimitado, API, white-label, 0.5% comision | Cadenas |

#### Reutilizacion de Infra Existente

- **Backend (55%)**: covacha-core (orgs, multi-tenant), covacha-webhook (WhatsApp), covacha-botia (bot), covacha-payment (SPEI)
- **Frontend (40%)**: mf-marketing (landing pages, calendario), shared-state
- **Nuevo desarrollo**: Motor de disponibilidad/scheduling, checkout de reserva, gestion de no-shows, motor de resenas, mf-reservas
- **Estimacion**: 48% reutilizado, 52% nuevo

#### Competencia

| Competidor | Precio/mes | Debilidad vs Nosotros |
|------------|-----------|----------------------|
| Calendly | $8-$16 USD | Sin pagos SPEI, sin WhatsApp, en ingles |
| Treatwell/Vagaro | $25-$85 USD | Enfoque primer mundo, sin SPEI, sin WhatsApp |
| SimplyBook.me | $8-$50 USD | Sin WhatsApp nativo, sin pagos locales |
| WhatsApp manual | $0 | Caotico, sin pagos, sin recordatorios automaticos |
| Libreta fisica | $0 | Sin digitalizacion |

**Ventaja competitiva**: WhatsApp nativo + pagos SPEI + modelo freemium asequible para Mexico.

#### Go-to-Market

1. **Fase 1 (0-3 meses)**: Beta con 100 salones de belleza en CDMX. Partnership con distribuidoras de productos de belleza (canal de distribucion natural).
2. **Fase 2 (3-9 meses)**: Expansion a consultorios y restaurantes. Campana Instagram Reels "Deja de perder clientes por no-shows".
3. **Fase 3 (9-18 meses)**: Marketplace de servicios (como "busca tu salon cerca"). Programa de lealtad cross-negocios.

#### Metricas de Exito (12 meses)

- Negocios activos: 3,000
- Citas agendadas: 200,000/mes
- MRR: $500K MXN ($30K USD) + comisiones
- No-show reduction: de 30% a <5% para clientes
- Churn: <6% mensual

#### Esfuerzo de Desarrollo

- **Tiempo**: 10 semanas (MVP en 6)
- **Equipo**: 1 backend, 1 frontend, 1 UX
- **Costo estimado**: $700K MXN (~$42K USD)

#### Score de Oportunidad: 8/10

> Mercado grande y fragmentado. Modelo freemium + comision. Efecto red (mas negocios = mas valor para consumidores).

---

### PRODUCTO 6: NominaExpress - Dispersion de Nomina via SPEI

**Tagline**: "Paga tu nomina en 3 clicks, sin banco empresarial"

#### Problema

Las PyMEs con 5-100 empleados pagan nomina manualmente: generan archivos TXT, suben a portal bancario, esperan autorizacion. Los ERPs de nomina (NOI, ContPAQ, Aspel NOI) calculan pero no dispersan. Las fintechs de nomina (Runa, Worky) estan enfocadas en HR, no en dispersion eficiente. SuperPago ya tiene motor SPEI - solo falta el modulo de nomina.

#### Solucion

- Alta de empleados con CLABE + RFC
- Calculo basico de nomina (salario base, ISR, IMSS, extras)
- Dispersion masiva via SPEI con un click
- Timbrado de recibos de nomina (CFDI 4.0 tipo nomina)
- Calendario de pagos quincenal/semanal/mensual
- Notificacion de deposito al empleado via WhatsApp
- Portal de empleado: recibos, constancias, historial
- Integracion con FacturaYA para timbrado

#### Mercado Objetivo

- **Primario**: PyMEs con 5-100 empleados que no tienen ERP de nomina
- **Secundario**: Despachos contables que procesan nominas de multiples empresas
- **TAM Mexico**: $1,500 MDD (servicios de nomina para PyMEs)
- **TAM LATAM**: $6,000 MDD
- **SAM**: $450 MDD (PyMEs que dispersan manualmente)
- **SOM (Year 1)**: $4.2 MDD (350 empresas, $1,000 MXN/mes promedio)

#### Modelo de Revenue

| Plan | Precio/mes (MXN) | Features | Target |
|------|-------------------|----------|--------|
| Micro | $499 | Hasta 10 empleados, dispersion SPEI, recibos basicos | Micro empresas |
| PyME | $1,299 | Hasta 50 empleados, calculo ISR/IMSS, timbrado CFDI, WhatsApp | PyMEs |
| Despacho | $2,999 | Multi-empresa (10), 200 empleados total, portal empleado | Contadores |
| Enterprise | $5,999 | Ilimitado, API, integraciones, SLA | Empresas medianas |

**Revenue adicional**: $5 MXN por timbrado de recibo + $3 MXN por dispersion SPEI.

#### Reutilizacion de Infra Existente

- **Backend (60%)**: covacha-payment (motor SPEI, dispersion masiva, ledger), covacha-core (orgs, usuarios), covacha-webhook (WhatsApp notificaciones)
- **Frontend (30%)**: Shell multi-tenant, shared-state, componentes de dashboard
- **Nuevo desarrollo**: Motor de calculo de nomina (ISR, IMSS, tablas SAT), timbrado de recibos CFDI tipo nomina, portal de empleado, mf-nomina
- **Estimacion**: 45% reutilizado, 55% nuevo (cumplimiento fiscal es complejo)

#### Competencia

| Competidor | Precio/mes | Debilidad vs Nosotros |
|------------|-----------|----------------------|
| Runa | $999-$4,999 MXN | No dispersa SPEI nativo, enfoque HR |
| Worky | $49-$149 MXN/empleado | Caro para PyMEs grandes, sin SPEI propio |
| Aspel NOI | $5,000+ MXN (licencia) | On-premise, no dispersa, setup costoso |
| ContPAQi Nominas | $8,000+ MXN | Legacy, requiere capacitacion, no dispersa |
| Manualmente (banco) | Tiempo | 2-4 horas por quincena, errores frecuentes |

**Ventaja competitiva**: Unico que calcula, timbra, dispersa por SPEI y notifica por WhatsApp en un solo flujo.

#### Go-to-Market

1. **Fase 1 (0-3 meses)**: Beta con 30 empresas de la red SuperPago. Partnership con despachos contables (canal de distribucion).
2. **Fase 2 (3-9 meses)**: Integracion con FacturaYA (timbrado). Campana "Adios al portal bancario". Webinars con Colegio de Contadores.
3. **Fase 3 (9-18 meses)**: Modulo de prestaciones (aguinaldo, prima vacacional, PTU). Portal de autoservicio empleado. API para ERPs.

#### Metricas de Exito (12 meses)

- Empresas activas: 500
- Empleados dispersados: 15,000/quincena
- MRR: $700K MXN ($42K USD) + fees por transaccion
- Churn: <3% mensual (nomina es sticky)
- Revenue por transaccion: $250K MXN/mes

#### Esfuerzo de Desarrollo

- **Tiempo**: 16 semanas (MVP en 10)
- **Equipo**: 2 backend, 1 frontend, 1 fiscal/compliance
- **Costo estimado**: $1.5 MDP (~$88K USD)

#### Score de Oportunidad: 8/10

> Producto extremadamente sticky (nadie cambia de proveedor de nomina facilmente). Revenue recurrente + transaccional. Alta sinergia con SPEI existente.

---

### PRODUCTO 7: AgenciaHub - Plataforma White-Label para Agencias Digitales

**Tagline**: "Tu agencia digital, con tu marca, en 24 horas"

#### Problema

Mexico tiene 15,000+ agencias de marketing digital (la mayoria de 2-15 personas). Operan con 8-12 herramientas desconectadas (Hootsuite, Canva, Google Sheets, WhatsApp). No pueden ofrecer un "portal de cliente" profesional. BaatDigital ya construyo toda la infra de agencia en mf-marketing - solo falta empaquetarlo como producto white-label.

#### Solucion

- Plataforma completa de agencia digital con la marca de la agencia
- Gestion de clientes, estrategias, aprobaciones, calendario editorial
- Social media management multi-canal
- Landing pages y funnels para clientes
- Campaign builder (Facebook/Instagram Ads)
- Brand kit management por cliente
- Dashboard ejecutivo para el dueno de la agencia
- Portal de cliente donde ven avances y aprueban contenido
- Reportes automaticos mensuales con IA

#### Mercado Objetivo

- **Primario**: Agencias digitales pequenas/medianas (2-15 personas)
- **Secundario**: Freelancers de marketing que quieren parecer agencia
- **TAM Mexico**: $500 MDD (herramientas para agencias)
- **TAM LATAM**: $2,000 MDD
- **SAM**: $150 MDD (agencias que buscan plataforma unificada)
- **SOM (Year 1)**: $5.4 MDD (300 agencias, $1,500 MXN/mes promedio)

#### Modelo de Revenue

| Plan | Precio/mes (MXN) | Features | Target |
|------|-------------------|----------|--------|
| Freelancer | $799 | 5 clientes, social media, landing pages, 1 usuario | Freelancers |
| Agencia | $2,499 | 20 clientes, 5 usuarios, dashboard, aprobaciones, reportes IA | Agencias pequenas |
| Pro | $4,999 | 50 clientes, 15 usuarios, white-label, campaign builder, API | Agencias medianas |
| Enterprise | $9,999 | Ilimitado, custom domain, SLA, integraciones custom | Agencias grandes |

#### Reutilizacion de Infra Existente

- **Backend (90%)**: TODO covacha-core (marketing APIs: clientes, estrategias, posts, aprobaciones, reportes), covacha-botia (agentes IA)
- **Frontend (85%)**: TODO mf-marketing (30 paginas, 113 componentes, dashboards, calendar, campaign builder, landing editor)
- **Nuevo desarrollo**: Sistema de white-labeling (custom domains, logos, colores), portal de cliente simplificado, billing por agencia, onboarding wizard
- **Estimacion**: 85% reutilizado, 15% nuevo

#### Competencia

| Competidor | Precio/mes | Debilidad vs Nosotros |
|------------|-----------|----------------------|
| Hootsuite | $99-$739 USD | Solo social media, sin landing, sin estrategias, en ingles |
| Metricool | $18-$199 USD | Solo analytics/social, sin agencia features |
| Vendasta | $79-$599 USD | En ingles, enfoque norteamericano, complejo |
| SocialBee | $29-$99 USD | Solo scheduling, sin CRM de clientes |
| Herramientas separadas | $200-$500 USD total | 8-12 tools, sin integracion, costoso en total |

**Ventaja competitiva**: Plataforma completa de agencia (no solo social media) en espanol, con IA integrada, a fraccion del costo de herramientas separadas.

#### Go-to-Market

1. **Fase 1 (0-3 meses)**: Beta con 20 agencias de la red BaatDigital. Programa "Agencia Partner" con descuento del 50% por 6 meses + co-marketing.
2. **Fase 2 (3-9 meses)**: Lanzamiento publico. Contenido educativo ("Como escalar tu agencia con IA"). Webinars mensuales. Directorio de agencias partners.
3. **Fase 3 (9-18 meses)**: Marketplace de servicios entre agencias. Certificacion "Agencia Powered by BaatDigital". Revenue share por upsells de agencias a sus clientes.

#### Metricas de Exito (12 meses)

- Agencias activas: 400
- Clientes gestionados (indirectos): 4,000
- MRR: $1 MDP ($60K USD)
- Churn: <4% mensual
- NPS: >55

#### Esfuerzo de Desarrollo

- **Tiempo**: 8 semanas (MVP en 4 - ya casi existe!)
- **Equipo**: 1 backend, 1 frontend, 1 DevOps (multi-tenancy)
- **Costo estimado**: $500K MXN (~$30K USD)

#### Score de Oportunidad: 9.5/10

> MAYOR RATIO REVENUE/ESFUERZO de todos los productos. 85% ya esta construido. Solo falta empaquetar y monetizar.

---

### PRODUCTO 8: LealtadPay - Programa de Lealtad con Monedero Digital

**Tagline**: "Tus clientes regresan porque los premias, no porque los persigues"

#### Problema

Los programas de lealtad en Mexico estan dominados por grandes cadenas (Puntos BBVA, Monedero del Ahorro). Las PyMEs no pueden ofrecer programas de lealtad porque los sistemas existentes son caros y complejos. Tarjetas de sellos de carton son la unica opcion. Con la infra de pagos SPEI + WhatsApp, se puede crear un sistema de puntos/cashback accesible.

#### Solucion

- Monedero digital para clientes del negocio (saldo en pesos, no puntos ficticios)
- Cashback configurable por compra (ej: 3% de cada compra regresa al monedero)
- Canje del monedero en la siguiente compra (descuento automatico)
- Tarjeta de cliente digital en WhatsApp (envia "Mi tarjeta" y ve su saldo)
- Promociones por segmento ("Clientes VIP: 5% extra este fin de semana")
- Notificaciones de saldo y promociones via WhatsApp
- QR de identificacion en punto de venta
- Dashboard para el negocio: retencion, frecuencia, ticket promedio

#### Mercado Objetivo

- **Primario**: Cafeterias, restaurantes, tiendas de conveniencia, farmacias independientes
- **Secundario**: Cadenas pequenas (5-20 sucursales)
- **TAM Mexico**: $400 MDD (loyalty programs para PyMEs)
- **TAM LATAM**: $1,600 MDD
- **SAM**: $120 MDD (PyMEs retail que quieren retener clientes)
- **SOM (Year 1)**: $1.8 MDD (1,500 negocios, $100 MXN/mes promedio)

#### Modelo de Revenue

| Plan | Precio/mes (MXN) | Features | Target |
|------|-------------------|----------|--------|
| Starter | $99 | 200 clientes, cashback fijo, WhatsApp basico | Micro negocios |
| Growth | $399 | 2,000 clientes, segmentacion, promociones, analytics | PyMEs |
| Chain | $999 | 10,000 clientes, multi-sucursal, API, QR POS | Cadenas pequenas |
| Enterprise | $2,499 | Ilimitado, white-label, integraciones custom | Cadenas medianas |

#### Reutilizacion de Infra Existente

- **Backend (65%)**: covacha-payment (monedero digital = cuenta SPEI simplificada, ledger), covacha-core (orgs, multi-tenant), covacha-webhook (WhatsApp)
- **Frontend (30%)**: shared-state, componentes de dashboard
- **Nuevo desarrollo**: Motor de reglas de cashback, segmentacion de clientes, generador de QR, app/web de consulta para cliente final, mf-lealtad
- **Estimacion**: 48% reutilizado, 52% nuevo

#### Competencia

| Competidor | Precio/mes | Debilidad vs Nosotros |
|------------|-----------|----------------------|
| Stamp | $500-$2,000 MXN | Sin WhatsApp nativo, UI anticuada |
| Belly (cerrado) | - | Ya no opera |
| FiveStars | $200+ USD | Enfoque US, sin SPEI, en ingles |
| Tarjetas de sellos | $0 | Sin datos, sin digital, perdible |
| Monederos de cadena | Custom | Solo para cadenas grandes, inalcanzable para PyMEs |

**Ventaja competitiva**: Monedero en pesos reales (no puntos), WhatsApp como canal, precio accesible.

#### Go-to-Market

1. **Fase 1 (0-3 meses)**: Piloto con 50 cafeterias y restaurantes en CDMX/GDL/MTY.
2. **Fase 2 (3-9 meses)**: Partnership con distribuidoras de alimentos (canal natural). Campana "Dale razones a tus clientes para regresar".
3. **Fase 3 (9-18 meses)**: Red de lealtad cross-negocios (puntos canjeables en multiples negocios). Datos agregados para insights de consumo.

#### Metricas de Exito (12 meses)

- Negocios activos: 2,000
- Consumidores registrados: 100,000
- MRR: $400K MXN ($24K USD)
- Churn: <5% mensual
- Aumento en frecuencia de visita de clientes: +25%

#### Esfuerzo de Desarrollo

- **Tiempo**: 12 semanas (MVP en 8)
- **Equipo**: 2 backend, 1 frontend, 1 UX
- **Costo estimado**: $800K MXN (~$47K USD)

#### Score de Oportunidad: 7.5/10

> Buen producto pero requiere masa critica. Sinergia media con infra existente. Potencial de red a largo plazo.

---

### PRODUCTO 9: CreditoFlash - Creditos PyME basados en Datos Transaccionales

**Tagline**: "Tu historial de ventas es tu mejor garantia"

#### Problema

El 67% de las PyMEs en Mexico no acceden a credito formal (CNBV). Los bancos piden garantias, avales y buro de credito limpio. Las fintechs de credito (Konfio, Credijusto) cobran tasas altas (25-50% anual). SuperPago tiene data transaccional unica: volumen de pagos SPEI, frecuencia, estacionalidad, diversificacion de clientes. Esta data es mejor predictor de repago que el Buro de Credito.

#### Solucion

- Scoring crediticio basado en transacciones SPEI del negocio (no Buro)
- Pre-aprobacion automatica basada en historial de pagos recibidos
- Linea de credito revolvente (desembolso SPEI instantaneo)
- Cobro automatico via retencion de flujo entrante (como merchant cash advance)
- Solicitud via WhatsApp ("Necesito $50,000 para inventario")
- Sin papeles, sin sucursal, sin garantias fisicas
- Dashboard de credito: disponible, utilizado, pagos, tasa

#### Mercado Objetivo

- **Primario**: PyMEs que ya usan SuperPago para cobros SPEI
- **Secundario**: Comercios de la red de puntos Cash-In/Cash-Out
- **TAM Mexico**: $12,000 MDD (credito PyME desatendido)
- **TAM LATAM**: $48,000 MDD
- **SAM**: $3,600 MDD (PyMEs con historial transaccional digital)
- **SOM (Year 1)**: $12 MDD (200 creditos activos, $50K MXN promedio, NIM 15%)

#### Modelo de Revenue

| Producto | Tasa anual | Monto | Plazo | Target |
|----------|-----------|-------|-------|--------|
| Micro Flash | 24% | $10K-$50K MXN | 3-6 meses | Micro negocios |
| PyME Credito | 18% | $50K-$500K MXN | 6-12 meses | PyMEs |
| Growth Line | 15% | $500K-$2M MXN | 12-24 meses | PyMEs en crecimiento |

**Revenue**: Net Interest Margin (NIM) del 12-18% + origination fee del 2%.

#### Reutilizacion de Infra Existente

- **Backend (55%)**: covacha-payment (SPEI dispersion, ledger, data transaccional), covacha-core (orgs, KYC basico)
- **Frontend (25%)**: Dashboards, shared-state
- **Nuevo desarrollo**: Motor de scoring crediticio (ML), modulo de originacion, cobro automatico (retencion de flujo), reportes regulatorios (CNBV/CONDUSEF), mf-credito
- **Estimacion**: 40% reutilizado, 60% nuevo (regulatorio y riesgo es complejo)

#### Competencia

| Competidor | Tasa anual | Debilidad vs Nosotros |
|------------|-----------|----------------------|
| Konfio | 25-50% | Tasas altas, proceso largo, requiere buro |
| Credijusto | 20-40% | Enterprise-focused, montos altos |
| Bancos | 15-30% | Proceso 2-4 semanas, garantias, papeleria |
| Prestamistas informales | 60-120% | Usureros, sin proteccion legal |

**Ventaja competitiva**: Data transaccional propia = mejor scoring + cobro automatico via flujo = menor riesgo = menores tasas.

#### Go-to-Market

1. **Fase 1 (0-6 meses)**: Regulacion (registro ante CNBV como SOFOM o partnership con regulado). Piloto con 50 comercios de alta transaccionalidad.
2. **Fase 2 (6-12 meses)**: Expansion a toda la base de SuperPago. Modelo "gana acceso a credito usando SuperPago" como incentivo de adopcion.
3. **Fase 3 (12-24 meses)**: Securitizacion de cartera. Partnership con fondos de inversion. Expansion de montos.

#### Metricas de Exito (12 meses)

- Creditos activos: 300
- Cartera total: $30 MDP
- NIM: 15%
- Mora >30 dias: <5%
- Revenue anual: $4.5 MDP

#### Esfuerzo de Desarrollo

- **Tiempo**: 24 semanas (MVP en 14, regulacion en paralelo)
- **Equipo**: 2 backend, 1 frontend, 1 data scientist, 1 compliance/legal
- **Costo estimado**: $3 MDP (~$176K USD)

#### Score de Oportunidad: 8/10

> Mercado gigantesco. Revenue exponencial. Pero regulacion y riesgo crediticio son complejos. Necesita capital de fondeo.

---

### PRODUCTO 10: PagaQR - POS Virtual con QR + SPEI Instantaneo

**Tagline**: "Cobra con tu celular, sin terminal, sin comisiones bancarias"

#### Problema

Las terminales punto de venta (TPV) cobran 2.5-3.5% de comision + renta mensual ($200-$500 MXN). Para negocios con ticket bajo (tacos, tianguis, mercados, ambulantes), la comision se come el margen. CoDi (cobro digital de Banxico) fracaso por mala UX. Hay una oportunidad de crear un QR+SPEI simple que funcione.

#### Solucion

- Genera QR unico por negocio (estatico) o por transaccion (dinamico)
- Cliente escanea y paga via SPEI desde su app bancaria
- Confirmacion instantanea al comercio via notificacion push + sonido
- WhatsApp como "terminal": "Cobra $150 al cliente" -> genera QR
- Sin terminal fisica, sin comision bancaria (solo fee fijo de $1-3 MXN)
- Dashboard de ventas diarias, corte de caja
- Facturas automaticas por venta (cross-sell FacturaYA)
- Integracion con LealtadPay (cashback al pagar)

#### Mercado Objetivo

- **Primario**: Comercio informal y semi-formal (tianguis, mercados, food trucks, ambulantes)
- **Secundario**: Profesionistas independientes, PyMEs que quieren alternativa a TPV
- **TAM Mexico**: $2,000 MDD (pagos digitales en comercio informal/PyME)
- **TAM LATAM**: $8,000 MDD
- **SAM**: $600 MDD (comercios que aceptarian QR+SPEI)
- **SOM (Year 1)**: $3.6 MDD (10,000 comercios, $30 MXN/mes promedio + fee por tx)

#### Modelo de Revenue

| Plan | Precio/mes (MXN) | Fee por tx | Features | Target |
|------|-------------------|-----------|----------|--------|
| Free | $0 | $3 MXN | QR estatico, 30 txs/mes, notificaciones | Ambulantes |
| Basico | $49 | $1.5 MXN | QR dinamico, ilimitado, corte de caja | Tianguis |
| Pro | $149 | $1 MXN | Dashboard, facturas, multi-empleado | Comercios |
| Business | $399 | $0.50 MXN | Analytics, API, integraciones, multi-sucursal | Cadenas |

#### Reutilizacion de Infra Existente

- **Backend (75%)**: covacha-payment (SPEI completo, cuentas, ledger, notificaciones), covacha-core (orgs), covacha-webhook (WhatsApp)
- **Frontend (35%)**: shared-state, componentes de dashboard
- **Nuevo desarrollo**: Generador de QR SPEI, pagina de pago (landing ligera), notificaciones instantaneas al comercio, app web progresiva (PWA) para comerciante, corte de caja
- **Estimacion**: 55% reutilizado, 45% nuevo

#### Competencia

| Competidor | Fee | Debilidad vs Nosotros |
|------------|-----|----------------------|
| Clip | 2.6-3.6% + renta | Requiere terminal fisica, comision alta |
| Mercado Pago QR | 0.99-3.49% | Comision porcentual (duele en ticket alto) |
| CoDi | $0 | Fracaso de adopcion, mala UX |
| STP directo | $3-5 MXN | Requiere integracion tecnica |
| Efectivo | $0 | Sin trazabilidad, riesgo, sin digital |

**Ventaja competitiva**: Fee fijo (no porcentual) + confirmacion instantanea + WhatsApp como terminal + sin hardware.

#### Go-to-Market

1. **Fase 1 (0-3 meses)**: Piloto en 3 mercados/tianguis de CDMX (500 comerciantes). Partnership con administraciones de mercados.
2. **Fase 2 (3-9 meses)**: Expansion a food trucks, ferias, tianguis nacionales. Campana "Cobra sin terminal, sin comision". Kits de stickers QR gratuitos.
3. **Fase 3 (9-18 meses)**: Red de aceptacion PagaQR (consumer brand). App para consumidores con directorio de comercios. Cross-sell con LealtadPay + CreditoFlash.

#### Metricas de Exito (12 meses)

- Comercios activos: 15,000
- Transacciones/mes: 500,000
- GMV mensual: $75 MDP
- MRR: $750K MXN ($45K USD) + fees: $750K MXN
- Revenue total: $1.5 MDP/mes ($90K USD)
- Churn: <10% mensual (mercado informal es volatil)

#### Esfuerzo de Desarrollo

- **Tiempo**: 8 semanas (MVP en 4)
- **Equipo**: 1 backend, 1 frontend (PWA), 1 UX
- **Costo estimado**: $500K MXN (~$30K USD)

#### Score de Oportunidad: 8.5/10

> Altisima sinergia con SPEI existente. Bajo costo de desarrollo. Mercado masivo. Crecimiento viral (boca a boca en mercados).

---

### PRODUCTO 11: CursoVende - Plataforma de Cursos con Pagos Integrados

**Tagline**: "Vende tu conocimiento. Cobra al instante."

#### Problema

Mexico tiene 1.5 millones de creadores de contenido educativo (coaches, consultores, instructores). Plataformas como Hotmart cobran 10-20% de comision. Teachable y Thinkific estan en ingles y cobran en USD. No hay una plataforma en espanol, con pagos SPEI nativos y comisiones bajas, para el mercado mexicano.

#### Solucion

- Creacion de cursos con editor drag & drop (reutiliza landing editor)
- Pagos unicos y suscripciones via SPEI
- Certificados digitales automaticos
- Comunidad de alumnos via WhatsApp Groups o canal
- Drip content (libera modulos por fecha o progreso)
- Landing de venta del curso con checkout integrado
- Webinars en vivo integrados
- Afiliados: otros pueden vender tu curso por comision

#### Mercado Objetivo

- **Primario**: Coaches, consultores, instructores independientes
- **Secundario**: Empresas que venden capacitacion (compliance, seguridad, ventas)
- **TAM Mexico**: $800 MDD (e-learning)
- **TAM LATAM**: $3,200 MDD
- **SAM**: $240 MDD (creadores que monetizan conocimiento)
- **SOM (Year 1)**: $2.4 MDD (500 creadores, $400 MXN/mes promedio + comision 3%)

#### Modelo de Revenue

| Plan | Precio/mes (MXN) | Comision | Features | Target |
|------|-------------------|---------|----------|--------|
| Free | $0 | 8% | 1 curso, pagos SPEI, landing basica | Nuevos creadores |
| Creator | $299 | 3% | 5 cursos, drip content, certificados | Creadores activos |
| Pro | $799 | 1% | Ilimitado, afiliados, analytics, white-label | Creadores serios |
| Academy | $1,999 | 0% | Multi-instructor, LMS completo, API | Empresas |

#### Reutilizacion de Infra Existente

- **Backend (45%)**: covacha-core (orgs, auth), covacha-payment (SPEI, suscripciones), covacha-webhook (WhatsApp notificaciones)
- **Frontend (40%)**: mf-marketing (landing editor, media library), shared-state
- **Nuevo desarrollo**: LMS engine, video hosting/streaming, sistema de certificados, motor de afiliados, mf-cursos
- **Estimacion**: 42% reutilizado, 58% nuevo

#### Competencia

| Competidor | Comision/Precio | Debilidad vs Nosotros |
|------------|----------------|----------------------|
| Hotmart | 10-20% comision | Comision altisima, enfoque Brasil |
| Teachable | $39-$119 USD/mes | En ingles, sin SPEI, caro en MXN |
| Thinkific | $49-$99 USD/mes | En ingles, sin pagos locales |
| Domestika | Revenue share | Solo cierto tipo de cursos, editorial control |
| WhatsApp + transferencia | $0 | Sin plataforma, sin seguimiento, caotico |

**Ventaja competitiva**: Espanol nativo + pagos SPEI + comisiones bajas + WhatsApp para comunidad.

#### Go-to-Market

1. **Fase 1 (0-3 meses)**: Beta con 30 creadores de contenido mexicanos. Partnership con 5 influencers educativos.
2. **Fase 2 (3-9 meses)**: Lanzamiento publico. Campana "Tu curso listo en 1 hora". Programa de afiliados para primeros 100 creadores.
3. **Fase 3 (9-18 meses)**: Marketplace de cursos. Certificaciones con valor curricular (alianzas con universidades). Expansion LATAM.

#### Metricas de Exito (12 meses)

- Creadores activos: 800
- Alumnos registrados: 25,000
- GMV (ventas de cursos): $15 MDP
- MRR: $400K MXN ($24K USD) + comisiones
- Revenue total: $600K MXN/mes ($36K USD)

#### Esfuerzo de Desarrollo

- **Tiempo**: 14 semanas (MVP en 8)
- **Equipo**: 2 backend, 2 frontend, 1 UX
- **Costo estimado**: $1.2 MDP (~$70K USD)

#### Score de Oportunidad: 7/10

> Buen mercado pero competitivo. Diferenciacion por pagos locales y espanol. Video hosting es costoso en infra.

---

### PRODUCTO 12: MiSuscripcion - Plataforma de Suscripciones B2C

**Tagline**: "Tus fans te pagan mes a mes. Tu solo crea."

#### Problema

Patreon domina globalmente pero no acepta SPEI, cobra en USD, y las comisiones + conversion cambiaria comen 10-15% del ingreso del creador mexicano. No existe un "Patreon mexicano" con pagos locales. El mercado de creator economy en LATAM esta creciendo 40% anual.

#### Solucion

- Pagina de creador con planes de suscripcion (contenido exclusivo por nivel)
- Cobro automatico mensual via SPEI domiciliado o tarjeta
- Contenido exclusivo: posts, videos, archivos, comunidad
- Comunicacion con suscriptores via WhatsApp (canal o grupo exclusivo)
- Tips/donaciones unicas via SPEI
- Dashboard de revenue, suscriptores, engagement
- Herramientas de growth: landing page, referidos, promos

#### Mercado Objetivo

- **Primario**: Creadores de contenido mexicanos (YouTubers, podcasters, escritores, artistas)
- **Secundario**: Periodistas independientes, organizaciones sin fines de lucro
- **TAM Mexico**: $200 MDD (creator economy monetizable)
- **TAM LATAM**: $800 MDD
- **SAM**: $60 MDD (creadores que ya monetizan o quieren monetizar)
- **SOM (Year 1)**: $1.2 MDD (400 creadores, promedio $250 MXN/mes de revenue)

#### Modelo de Revenue

| Plan | Precio/mes (MXN) | Comision | Features |
|------|-------------------|---------|----------|
| Free | $0 | 10% | Pagina basica, 1 plan, SPEI |
| Creator | $149 | 5% | 5 planes, WhatsApp, analytics |
| Pro | $399 | 2.5% | Ilimitado, custom domain, referidos |
| Business | $999 | 1% | Multi-creador, API, white-label |

#### Reutilizacion de Infra Existente

- **Backend (55%)**: covacha-payment (SPEI, suscripciones recurrentes, ledger), covacha-core (orgs, auth), covacha-webhook (WhatsApp)
- **Frontend (40%)**: mf-marketing (landing pages, media), shared-state
- **Nuevo desarrollo**: Motor de suscripciones recurrentes, paywall de contenido, pagina de creador, motor de tips, mf-suscripciones
- **Estimacion**: 48% reutilizado, 52% nuevo

#### Competencia

| Competidor | Comision | Debilidad vs Nosotros |
|------------|---------|----------------------|
| Patreon | 5-12% + FX + fees | Sin SPEI, USD, conversion cambiaria = 15% real |
| Ko-fi | 0-5% | Sin pagos locales, limitado |
| Buy Me a Coffee | 5% | Sin SPEI, sin WhatsApp |
| YouTube Memberships | 30% | Comision absurda, solo YouTube |

**Ventaja competitiva**: SPEI nativo = sin conversion cambiaria. Comision real mas baja. WhatsApp como canal de comunidad (donde ya estan los fans mexicanos).

#### Go-to-Market

1. **Fase 1 (0-3 meses)**: Onboarding de 30 creadores mexicanos con >10K seguidores. "Migra de Patreon y ahorra 10%".
2. **Fase 2 (3-9 meses)**: Partnership con podcasts y YouTubers mexicanos. Campana "Apoya creadores mexicanos".
3. **Fase 3 (9-18 meses)**: Discovery/marketplace de creadores. Revenue share con eventos presenciales. Expansion LATAM.

#### Metricas de Exito (12 meses)

- Creadores activos: 600
- Suscriptores pagando: 15,000
- GMV mensual: $3 MDP
- MRR: $200K MXN ($12K USD) + comisiones: $150K MXN
- Churn de creadores: <5%

#### Esfuerzo de Desarrollo

- **Tiempo**: 12 semanas (MVP en 6)
- **Equipo**: 1 backend, 1 frontend, 1 UX
- **Costo estimado**: $700K MXN (~$42K USD)

#### Score de Oportunidad: 6.5/10

> Nicho interesante pero mercado mas pequeno. Requiere masa critica de creadores. Sinergia media.

---

### PRODUCTO 13: FlotaTrack - Gestion de Delivery con Rastreo y Pagos

**Tagline**: "Controla tus entregas, cobra al entregar"

#### Problema

PyMEs de distribucion (purificadoras, tortillerias, ferreterias con delivery) gestionan rutas con WhatsApp y papel. No saben donde estan sus repartidores, los cobros se pierden, no hay prueba de entrega. Rappi y Uber Eats resuelven para restaurantes, pero no para B2B delivery ni entrega propia.

#### Solucion

- Asignacion de rutas y pedidos a repartidores
- Rastreo GPS en tiempo real (PWA para repartidor)
- Prueba de entrega con foto y firma digital
- Cobro en punto de entrega via QR + SPEI (reutiliza PagaQR)
- Notificacion al cliente: "Tu pedido va en camino" via WhatsApp
- Optimizacion de rutas con IA
- Dashboard: entregas completadas, cobros, tiempos, eficiencia
- Facturacion automatica al entregar (cross-sell FacturaYA)

#### Mercado Objetivo

- **Primario**: Distribuidoras, purificadoras, panaderias con reparto, ferreterias
- **Secundario**: E-commerces con delivery propio, dark kitchens
- **TAM Mexico**: $500 MDD (last-mile logistics para PyMEs)
- **TAM LATAM**: $2,000 MDD
- **SAM**: $150 MDD (PyMEs con flota propia 2-20 vehiculos)
- **SOM (Year 1)**: $1.8 MDD (300 empresas, $500 MXN/mes promedio)

#### Modelo de Revenue

| Plan | Precio/mes (MXN) | Features | Target |
|------|-------------------|----------|--------|
| Starter | $299 | 3 repartidores, rastreo, 100 entregas/mes | Micro distribuidoras |
| Business | $799 | 10 repartidores, cobros QR, WhatsApp, 500 entregas | PyMEs |
| Fleet | $1,999 | 30 repartidores, optimizacion rutas, API, ilimitado | Distribuidoras |
| Enterprise | $4,999 | Custom, integraciones, SLA | Cadenas de distribucion |

#### Reutilizacion de Infra Existente

- **Backend (45%)**: covacha-payment (SPEI cobros, QR), covacha-core (orgs), covacha-webhook (WhatsApp notificaciones)
- **Frontend (25%)**: shared-state, componentes de mapa/dashboard
- **Nuevo desarrollo**: Motor de rutas, rastreo GPS, PWA para repartidores, prueba de entrega, optimizacion con IA, mf-flota
- **Estimacion**: 35% reutilizado, 65% nuevo

#### Competencia

| Competidor | Precio/mes | Debilidad vs Nosotros |
|------------|-----------|----------------------|
| Beetrack | $500+ USD | Enterprise-only, caro, sin pagos |
| OnFleet | $500-$1,150 USD | En ingles, sin SPEI, sin WhatsApp |
| Google Maps manual | $0 | Sin rastreo, sin cobros, sin prueba de entrega |
| WhatsApp + GPS share | $0 | Caotico, sin automatizacion |

**Ventaja competitiva**: Cobro al entregar via SPEI + WhatsApp notificaciones + precio accesible para PyMEs mexicanas.

#### Go-to-Market

1. **Fase 1 (0-3 meses)**: Piloto con 20 purificadoras/distribuidoras. Case study de ahorro en tiempo y cobros.
2. **Fase 2 (3-9 meses)**: Campana en asociaciones de distribuidores. Integracion con CobrarIA (pedido -> ruta -> entrega -> cobro -> factura).
3. **Fase 3 (9-18 meses)**: Marketplace de repartidores (crowd-sourced delivery). API para e-commerces.

#### Metricas de Exito (12 meses)

- Empresas activas: 400
- Entregas rastreadas: 200,000/mes
- MRR: $400K MXN ($24K USD)
- Cobros procesados: $30 MDP/mes
- Churn: <4% mensual

#### Esfuerzo de Desarrollo

- **Tiempo**: 14 semanas (MVP en 8)
- **Equipo**: 2 backend, 1 frontend (PWA), 1 mobile
- **Costo estimado**: $1.2 MDP (~$70K USD)

#### Score de Oportunidad: 7/10

> Mercado vertical solido pero menor sinergia con infra existente. Requiere GPS/mobile que es nuevo.

---

## Matriz de Priorizacion

| # | Producto | Revenue Potencial | Esfuerzo Dev | Sinergia Ecosistema | Time to Market | Score Final |
|---|---------|-------------------|-------------|---------------------|---------------|-------------|
| 7 | AgenciaHub (White-Label) | Alta | S (8 sem) | **Maxima (85%)** | 4 semanas | **9.5/10** |
| 1 | CobrarIA (CRM WhatsApp) | **Muy Alta** | M (14 sem) | Alta (60%) | 8 semanas | **9.5/10** |
| 3 | TiendaClick (Social Commerce) | **Muy Alta** | M (12 sem) | Alta (55%) | 6 semanas | **9/10** |
| 10 | PagaQR (POS Virtual) | Alta | S (8 sem) | Alta (55%) | 4 semanas | **8.5/10** |
| 4 | CobraBot (Cobranza IA) | Alta | S (10 sem) | Alta (55%) | 6 semanas | **8.5/10** |
| 2 | FacturaYA (CFDI + IA) | Alta | L (18 sem) | Media (40%) | 10 semanas | **8.5/10** |
| 9 | CreditoFlash (Creditos PyME) | **Muy Alta** | XL (24 sem) | Media (40%) | 14 semanas | **8/10** |
| 6 | NominaExpress (Nomina SPEI) | Alta | L (16 sem) | Media (45%) | 10 semanas | **8/10** |
| 5 | ReservaFacil (Reservaciones) | Media | M (10 sem) | Media (48%) | 6 semanas | **8/10** |
| 8 | LealtadPay (Lealtad/Monedero) | Media | M (12 sem) | Media (48%) | 8 semanas | **7.5/10** |
| 11 | CursoVende (Cursos Online) | Media | M (14 sem) | Media (42%) | 8 semanas | **7/10** |
| 13 | FlotaTrack (Delivery) | Media | L (14 sem) | Baja (35%) | 8 semanas | **7/10** |
| 12 | MiSuscripcion (Creator Economy) | Baja | M (12 sem) | Media (48%) | 6 semanas | **6.5/10** |

---

## Recomendacion Final: Top 3 Productos a Construir

### 1. AgenciaHub - White-Label para Agencias (Score: 9.5/10)

**Por que primero:**
- **85% ya esta construido**. mf-marketing tiene 30 paginas, 113 componentes, dashboards, campaign builder, landing editor, brand kit, aprobaciones - TODO lo que una agencia necesita.
- Solo requiere: white-labeling (custom domains/logos), portal simplificado de cliente, billing, y onboarding wizard.
- **4-8 semanas a MVP**. Revenue inmediato.
- **Efecto multiplicador**: cada agencia trae 10-20 clientes indirectos al ecosistema.
- **Costo minimo**: $500K MXN (~$30K USD).
- **MRR estimado en 12 meses**: $1 MDP ($60K USD).

### 2. CobrarIA - CRM Conversacional WhatsApp (Score: 9.5/10)

**Por que segundo:**
- **Mercado masivo**: 4.9M PyMEs en Mexico, 80% venden por WhatsApp.
- **Sinergia unica**: combina WhatsApp (covacha-webhook), IA (covacha-botia), pagos (covacha-payment), e inventario (covacha-inventory).
- **Diferenciador imbatible**: unico CRM que va de la conversacion al cobro SPEI en un flujo.
- **Network effects**: mas comercios cobrando = mas consumidores pagando = mas datos transaccionales.
- **MRR estimado en 12 meses**: $1.5 MDP ($90K USD).
- **Base para CreditoFlash**: los datos transaccionales de CobrarIA alimentan el scoring crediticio del Producto 9.

### 3. PagaQR - POS Virtual con SPEI (Score: 8.5/10)

**Por que tercero:**
- **75% de backend ya existe** (motor SPEI completo).
- **4 semanas a MVP**. Es el producto mas rapido de lanzar.
- **Mercado masivo y desatendido**: millones de comercios informales sin terminal.
- **Fee fijo vs % = value prop clara**: "$1 peso por cobro vs 3% del banco".
- **Efecto red**: cada comercio que adopta QR+SPEI trae consumidores al ecosistema.
- **Complemento perfecto** para CobrarIA (CRM online) + PagaQR (cobros presenciales).
- **Gateway drug**: comercios entran por PagaQR y luego usan CobrarIA, FacturaYA, CreditoFlash.

### Secuencia Recomendada

```
Mes 1-2:   AgenciaHub MVP (revenue inmediato, valida modelo)
Mes 2-4:   PagaQR MVP (captura base de comercios)
Mes 3-6:   CobrarIA MVP (producto flagship)
Mes 6-9:   FacturaYA + CobraBot (cross-sell a base existente)
Mes 9-12:  CreditoFlash piloto (monetiza datos transaccionales)
Mes 12-18: TiendaClick + NominaExpress (expansion de ecosistema)
```

### Revenue Proyectado Combinado (12 meses)

| Producto | MRR Mes 12 (MXN) | MRR Mes 12 (USD) |
|----------|-------------------|-------------------|
| AgenciaHub | $1,000,000 | $60,000 |
| CobrarIA | $1,500,000 | $90,000 |
| PagaQR | $1,500,000 | $90,000 |
| **Total Top 3** | **$4,000,000** | **$240,000** |

**Inversion total Top 3**: $2.2 MDP (~$130K USD)
**Payback period**: ~7 meses
**ARR proyectado Year 2**: $96 MDP (~$5.7M USD) con crecimiento agresivo

---

## Epicas Iniciales (Draft)

### AgenciaHub

| ID | Epica | Complejidad | Descripcion |
|----|-------|-------------|-------------|
| EP-AH-001 | White-Label Engine | M | Custom domains, logos, colores, favicon por agencia |
| EP-AH-002 | Portal de Cliente Simplificado | M | Vista read-only + aprobaciones para clientes de la agencia |
| EP-AH-003 | Billing y Suscripciones | M | Planes, facturacion, medicion de uso por agencia |
| EP-AH-004 | Onboarding Wizard para Agencias | S | Setup guiado: datos, branding, primer cliente, primer post |
| EP-AH-005 | Marketplace y Directorio de Agencias | L | Directorio publico, programa partner, certificaciones |

### CobrarIA

| ID | Epica | Complejidad | Descripcion |
|----|-------|-------------|-------------|
| EP-CR-001 | Inbox Unificado WhatsApp | XL | Bandeja de conversaciones con pipeline visual integrado |
| EP-CR-002 | Pipeline de Ventas CRM | L | Kanban de oportunidades, arrastrar entre etapas |
| EP-CR-003 | Bot de Calificacion de Leads | L | Bot IA que califica leads automaticamente por conversacion |
| EP-CR-004 | Cotizaciones y Cobros en Chat | M | Generar cotizacion, enviar link de pago SPEI desde conversacion |
| EP-CR-005 | Catalogo Compartible | M | Link de catalogo de productos para WhatsApp/redes |
| EP-CR-006 | Dashboard de Metricas de Ventas | M | Conversion, ticket promedio, tiempo de cierre, embudo |
| EP-CR-007 | Automatizaciones y Secuencias | L | Follow-up automatico, recordatorios, nurturing |

### PagaQR

| ID | Epica | Complejidad | Descripcion |
|----|-------|-------------|-------------|
| EP-QR-001 | Generador de QR SPEI | M | QR estatico (negocio) y dinamico (por transaccion) con monto |
| EP-QR-002 | Pagina de Pago (Landing) | S | Pagina ligera donde el cliente confirma y paga via SPEI |
| EP-QR-003 | Notificacion Instantanea al Comercio | M | Push notification + sonido + WhatsApp al recibir pago |
| EP-QR-004 | PWA del Comerciante | L | Dashboard movil: ventas del dia, cobrar, corte de caja |
| EP-QR-005 | WhatsApp como Terminal | M | "Cobra $150" -> genera QR -> comparte en chat -> confirma pago |

---

## Notas Regulatorias Importantes

| Producto | Regulacion | Entidad | Accion Requerida |
|----------|-----------|---------|-----------------|
| CreditoFlash | Ley Fintech, CNBV | CNBV | Registro como SOFOM o partnership con regulado |
| FacturaYA | Reglas SAT, CFDI 4.0 | SAT | Certificacion como PAC (6-12 meses) |
| NominaExpress | LFT, IMSS, SAT | SAT/IMSS | Cumplimiento tablas ISR, SUA, timbrado nomina |
| CobraBot | NOM-179, Ley Proteccion Consumidor | PROFECO/CONDUSEF | Horarios de contacto, mensajes no amenazantes |
| PagaQR | Disposiciones SPEI, Banxico | Banxico | Cumplimiento con reglas de SPEI para cobros |
| LealtadPay | Ley Fintech (monedero) | CNBV | Evaluar si califica como "fondo de pago electronico" |

---

## Fuentes de Investigacion de Mercado

- [Mexico SaaS Market 2026-2034 - Grand View Research](https://www.grandviewresearch.com/horizon/outlook/software-as-a-service-saas-market/mexico)
- [Mexico concentra 17% del mercado SaaS en LATAM - EntreVeredas](https://www.entreveredas.com.mx/2026/02/mexico-concentra-17-del-mercado-saas-en.html)
- [LATAM SaaS Growth - EBANX](https://www.fintechweekly.com/magazine/articles/latin-america-saas-growth-ebanx-2027)
- [SME Demand Powers SaaS Growth in LATAM - Antom](https://knowledge.antom.com/latin-america-on-the-rise-sme-demand-powers-saas-growth)
- [Top 10 Trends LatAm Fintech 2025 - QED Investors](https://www.qedinvestors.com/blog/top-10-trends-for-latam-fintech-in-2025)
- [LatAm Fintech Investment Revival 2026 - CrowdfundInsider](https://www.crowdfundinsider.com/2026/01/257085-latam-startups-gear-up-for-a-2026-investment-revival-with-fintech-being-key-focus-area-analysis/)
- [Fintech Trends LATAM 2026 - FacePhi](https://facephi.com/en/fintech-trends-in-latam/)
- [Transformacion Digital PyMEs Mexico - Aspel/Siigo](https://www.siigo.com/mx/blog/tecnologia-e-innovacion/transformacion-digital-para-pymes-y-mipymes-mexicanas/)
- [PyMEs y Digitalizacion - IFT Mexico](https://www.ift.org.mx/transformacion-digital/blog/la-transformacion-digital-de-la-pymes-y-su-impacto-en-el-desarrollo-economico-de-mexico)
- [Mexico CRM Market 2033 - IMARC Group](https://www.imarcgroup.com/mexico-customer-relationship-management-market)
- [Mexico E-Invoicing Market 2033 - IMARC Group](https://www.imarcgroup.com/mexico-e-invoicing-market)
- [Mexico E-Commerce Market 2034 - IMARC Group](https://www.imarcgroup.com/mexico-e-commerce-market)
- [Mexico Social Commerce $10.5B by 2030 - GlobeNewsWire](https://www.globenewswire.com/news-release/2025/05/15/3082054/28124/en/Mexico-Social-Commerce-Market-Intelligence-Report-2025-Market-to-Surpass-10-5-Billion-by-2030-Facebook-Remains-the-Dominant-Player-with-Over-90-of-Social-Commerce-Consumers.html)
- [WhatsApp Business Statistics 2025 - AuroraInbox](https://www.aurorainbox.com/en/2026/03/01/whatsapp-business-2025-statistics/)
- [CRM WhatsApp Mexico 2025 - AuroraInbox](https://www.aurorainbox.com/en/2026/01/31/mejores-crm-whatsapp-mexico/)
- [MarTech Guia LATAM 2026 - MaretechLatam](https://www.marketechlatam.com/que-es-martech-guia-completa-latam-2026)
- [MarTech Market $702B by 2030 - Fortune Business Insights](https://www.fortunebusinessinsights.com/martech-market-111523)
- [CFDI 4.0 Facturacion 2026 - Gigstack](https://blog.gigstack.pro/post/cfdi-4-0-facturacion-electronica-automatizacion-mexico-2026)
- [Reforma Fiscal 2026 CFDI - Gigstack](https://blog.gigstack.pro/post/reforma-fiscal-2026-nuevas-reglas-cfdi-sat)
