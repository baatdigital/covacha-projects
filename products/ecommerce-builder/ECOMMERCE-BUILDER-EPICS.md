# E-commerce Builder - Tienda Online con SPEI + WhatsApp (EP-EC-001 a EP-EC-008)

**Fecha**: 2026-03-14
**Product Owner**: SuperPago
**Estado**: Planificacion
**GitHub Issue**: baatdigital/covacha-projects#131
**Score**: 6.5/10 | **Time to Market**: 16 semanas | **Reuso**: 60%

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

Constructor de tiendas online para PyMEs mexicanas con pago SPEI integrado (sin comisiones de tarjeta), atencion al cliente via WhatsApp, y catalogo de productos sincronizado con el inventario existente. Similar a Shopify pero local, mas barato, y con WhatsApp nativo como canal de comunicacion y ventas.

**Propuesta de valor**: Tu propia tienda online en minutos, con SPEI sin comisiones y WhatsApp integrado para atender clientes.

---

## Analisis de Mercado

| Metrica | Valor |
|---------|-------|
| **TAM Mexico** | $4.8B MXN/ano (1M PyMEs online x $400/mes) |
| **SAM** | $960M MXN/ano (200K con capacidad digital) |
| **SOM Year 1** | $14.4M MXN/ano (3,000 tiendas x $399/mes) |

### Problema de Mercado

- Shopify: caro ($29 USD/mes + 2% comision) y no tiene SPEI nativo
- Mercado Libre: alta comision (16-20%) y no es tu tienda
- PyMEs quieren su tienda propia pero no tienen como construirla
- No hay builder de tiendas con SPEI + WhatsApp en Mexico

### Modelo de Revenue

| Plan | Precio MXN/mes | Productos | Comision |
|------|---------------|-----------|---------|
| Starter | $199 | 50 | 2% |
| Pro | $599 | 500 | 0.5% |
| Business | $999 | Ilimitados | 0% |

---

## Reutilizacion del Ecosistema

| Componente | Repo Existente | Reutilizacion | Descripcion |
|-----------|---------------|---------------|-------------|
| Landing editor/templates | mf-marketing | 70% | Builder visual, templates |
| Motor SPEI | covacha-payment | 100% | Checkout con SPEI QR |
| WhatsApp bot | covacha-botia | 80% | Atencion al cliente, pedidos |
| Inventario | covacha-inventory + mf-inventory | 75% | Catalogo, stock |
| Multi-tenant | covacha-core | 100% | Organizaciones, auth |
| Notificaciones | covacha-notification | 85% | Pedidos, tracking |
| Shell MF | mf-core | 100% | Module Federation |
| **Nuevo** | mf-ecommerce | 0% | Admin de tienda |
| **Nuevo** | storefront renderer | 0% | Frontend publico de tienda |

**Reutilizacion total estimada**: 60%

---

## Mapa de Epicas

| ID | Epica | Complejidad | Semana | Dependencias | Estado |
|----|-------|-------------|--------|--------------|--------|
| EP-EC-001 | Builder Visual de Tienda | XL | 1-4 | mf-marketing | Planificacion |
| EP-EC-002 | Catalogo de Productos y Stock | L | 2-4 | covacha-inventory | Planificacion |
| EP-EC-003 | Carrito de Compras y Checkout SPEI | L | 4-6 | EP-EC-002, covacha-payment | Planificacion |
| EP-EC-004 | Gestion de Pedidos y Envios | L | 5-8 | EP-EC-003 | Planificacion |
| EP-EC-005 | WhatsApp Commerce (Notificaciones + Bot) | M | 6-8 | EP-EC-004, covacha-botia | Planificacion |
| EP-EC-006 | Dominio Personalizado y SEO | M | 8-10 | EP-EC-001 | Planificacion |
| EP-EC-007 | Analytics y Dashboard del Vendedor | M | 10-12 | EP-EC-001 a EP-EC-005 | Planificacion |
| EP-EC-008 | Facturacion CFDI por Venta | M | 10-12 | EP-EC-003 | Planificacion |

**Totales:**
- 8 epicas
- 40 user stories (US-EC-001 a US-EC-040)
- Estimacion total: ~112 dev-days (16 semanas, 2-3 devs)

---

## Epicas Detalladas

---

### EP-EC-001: Builder Visual de Tienda

**Descripcion:**
Editor visual drag & drop para construir la tienda online. Basado en el landing editor de mf-marketing, extendido con componentes e-commerce (catalogo, carrito, checkout). Incluye templates por industria (ropa, comida, servicios, tecnologia) para que el comerciante lance su tienda en minutos.

**User Stories:**
- US-EC-001: Editor drag & drop con componentes e-commerce
- US-EC-002: Templates de tienda por industria (ropa, comida, servicios)
- US-EC-003: Personalizacion de colores, fuentes, logo, imagenes
- US-EC-004: Preview en mobile y desktop antes de publicar
- US-EC-005: Publicar tienda con un click

**Criterios de Aceptacion de la Epica:**
- [ ] Editor visual basado en mf-marketing landing editor
- [ ] Componentes e-commerce: header, catalogo grid, producto destacado, carrito, footer
- [ ] Minimo 6 templates por industria (ropa, comida, servicios, tech, belleza, general)
- [ ] Personalizacion: colores primario/secundario, fuente, logo, favicon
- [ ] Preview responsive: mobile, tablet, desktop
- [ ] Publicacion con un click (deploy a S3 + CloudFront)
- [ ] Undo/redo en el editor
- [ ] Auto-save cada 30 segundos
- [ ] Tiempo de publicacion < 60 segundos
- [ ] Tests >= 98%

**Dependencias:** mf-marketing (landing editor)

**Complejidad:** XL (5 user stories, editor visual complejo)

**Repositorios:** `mf-ecommerce`, `mf-marketing`

---

### EP-EC-002: Catalogo de Productos y Stock

**Descripcion:**
Catalogo de productos de la tienda sincronizado con el inventario existente (covacha-inventory). El comerciante puede gestionar productos desde el admin de la tienda o desde mf-inventory, y los cambios se reflejan en la tienda publica.

**User Stories:**
- US-EC-006: CRUD de productos con variantes (talla, color)
- US-EC-007: Galeria de imagenes por producto
- US-EC-008: Categorias y colecciones de productos
- US-EC-009: Control de stock con sincronizacion de inventario
- US-EC-010: Importacion masiva de productos desde CSV

**Criterios de Aceptacion de la Epica:**
- [ ] CRUD de productos: nombre, descripcion, precio, imagenes, variantes
- [ ] Variantes: combinaciones de atributos (talla S/M/L + color rojo/azul)
- [ ] Stock por variante, decrementado automaticamente al vender
- [ ] Galeria de imagenes con drag & drop para reordenar
- [ ] Categorias y colecciones (ej: "Ofertas de verano")
- [ ] Sincronizacion bidireccional con covacha-inventory
- [ ] Import CSV con productos y variantes
- [ ] Productos activos/inactivos (draft antes de publicar)
- [ ] Precio con descuento y precio original (tachado)
- [ ] Tests >= 98%

**Dependencias:** covacha-inventory

**Complejidad:** L (5 user stories)

**Repositorios:** `covacha-inventory`, `covacha-libs`

---

### EP-EC-003: Carrito de Compras y Checkout SPEI

**Descripcion:**
Experiencia de compra completa en la tienda publica: agregar productos al carrito, ingresar datos de envio, y pagar via SPEI QR. El checkout genera un QR de pago SPEI y confirma la compra automaticamente al detectar el pago. Sin necesidad de tarjeta de credito.

**User Stories:**
- US-EC-011: Carrito de compras persistente (localStorage + backend)
- US-EC-012: Formulario de datos de envio (nombre, direccion, telefono)
- US-EC-013: Checkout con QR de pago SPEI
- US-EC-014: Confirmacion automatica de pago y generacion de pedido
- US-EC-015: Email y WhatsApp de confirmacion al comprador

**Criterios de Aceptacion de la Epica:**
- [ ] Carrito: agregar, quitar, modificar cantidades, persistente entre sesiones
- [ ] Validacion de stock antes de checkout
- [ ] Datos de envio: nombre, direccion completa, CP, telefono, email
- [ ] Calculo de envio basado en CP destino (tabla configurable o integracion)
- [ ] QR de pago SPEI con monto total (reutiliza POS Virtual)
- [ ] Confirmacion automatica via webhook SPEI en < 30 segundos
- [ ] Pedido creado con estado PAID al confirmar
- [ ] Email de confirmacion con detalle del pedido
- [ ] WhatsApp de confirmacion al telefono del comprador
- [ ] Tests >= 98%

**Dependencias:** EP-EC-002 (productos), covacha-payment (SPEI)

**Complejidad:** L (5 user stories)

**Repositorios:** `covacha-payment`, `mf-ecommerce`

---

### EP-EC-004: Gestion de Pedidos y Envios

**Descripcion:**
Backend y admin para que el vendedor gestione los pedidos recibidos: ver nuevos pedidos, preparar envio, marcar como enviado con numero de guia, y dar seguimiento hasta la entrega. El comprador recibe actualizaciones por WhatsApp.

**User Stories:**
- US-EC-016: Vista de pedidos con estados (nuevo, preparando, enviado, entregado)
- US-EC-017: Detalle del pedido con productos, datos del comprador, pago
- US-EC-018: Marcar como enviado con numero de guia
- US-EC-019: Tracking de envio compartido por WhatsApp
- US-EC-020: Cancelacion y reembolso de pedidos

**Criterios de Aceptacion de la Epica:**
- [ ] Estados: NEW, PREPARING, SHIPPED, DELIVERED, CANCELLED, REFUNDED
- [ ] Notificacion al vendedor (WhatsApp/email) cuando llega nuevo pedido
- [ ] Vista admin: lista de pedidos con filtros por estado, fecha
- [ ] Detalle: productos, cantidades, monto, datos de envio, pago
- [ ] Ingresar numero de guia y paqueteria al marcar como enviado
- [ ] Link de tracking generado automaticamente (Estafeta, DHL, etc.)
- [ ] Comprador recibe por WhatsApp: "Tu pedido ha sido enviado. Guia: {guia}"
- [ ] Cancelacion con motivo y reembolso (SPEI de vuelta)
- [ ] Metricas: pedidos por dia, tiempo promedio de preparacion
- [ ] Tests >= 98%

**Dependencias:** EP-EC-003

**Complejidad:** L (5 user stories)

**Repositorios:** `covacha-core`, `covacha-notification`

---

### EP-EC-005: WhatsApp Commerce (Notificaciones + Bot)

**Descripcion:**
Integracion profunda con WhatsApp para el e-commerce: notificaciones de pedido, atencion al cliente via bot, consulta de productos, y compra asistida por WhatsApp. El comprador puede preguntar "Tienen la camisa en talla M?" y el bot responde consultando el inventario.

**User Stories:**
- US-EC-021: Notificaciones de estado de pedido por WhatsApp
- US-EC-022: Bot de atencion: consulta de productos, stock, precios
- US-EC-023: Compra asistida: bot ayuda a elegir y envia link de checkout
- US-EC-024: Boton de WhatsApp en la tienda para soporte
- US-EC-025: Carrito abandonado: recordatorio por WhatsApp

**Criterios de Aceptacion de la Epica:**
- [ ] Notificaciones automaticas: pedido confirmado, enviado, entregado
- [ ] Bot responde consultas de productos: "Cuanto cuesta la camisa azul?"
- [ ] Bot consulta stock en tiempo real: "Hay talla M disponible?"
- [ ] Compra asistida: bot arma carrito y envia link de checkout
- [ ] Boton flotante de WhatsApp en la tienda con mensaje pre-llenado
- [ ] Carrito abandonado: detectar (> 30 min sin checkout) y enviar recordatorio
- [ ] Opt-out de notificaciones de marketing
- [ ] Escalamiento a vendedor humano si el bot no puede resolver
- [ ] Templates aprobados por Meta
- [ ] Tests >= 98%

**Dependencias:** EP-EC-004, covacha-botia

**Complejidad:** M (5 user stories)

**Repositorios:** `covacha-botia`, `covacha-notification`

---

### EP-EC-006: Dominio Personalizado y SEO

**Descripcion:**
Soporte para dominio personalizado (.com.mx) y optimizacion SEO para que la tienda aparezca en Google. Incluye meta tags, sitemap, Schema.org (Product), y certificado SSL automatico.

**User Stories:**
- US-EC-026: Conectar dominio personalizado (.com.mx)
- US-EC-027: SSL automatico (Let's Encrypt)
- US-EC-028: Meta tags y Open Graph configurables por pagina
- US-EC-029: Sitemap XML generado automaticamente
- US-EC-030: Schema.org Product para rich snippets en Google

**Criterios de Aceptacion de la Epica:**
- [ ] Configurar dominio personalizado con CNAME a CloudFront
- [ ] SSL gratuito via AWS Certificate Manager
- [ ] Instrucciones paso a paso para configurar DNS
- [ ] Meta tags: title, description, og:image por pagina y producto
- [ ] Sitemap.xml generado automaticamente con productos y categorias
- [ ] Schema.org Product: nombre, precio, disponibilidad, imagen, resenas
- [ ] Robots.txt configurable
- [ ] URLs amigables: /producto/nombre-del-producto
- [ ] Canonical URLs para evitar contenido duplicado
- [ ] Tests >= 98%

**Dependencias:** EP-EC-001

**Complejidad:** M (5 user stories)

**Repositorios:** `mf-ecommerce`

---

### EP-EC-007: Analytics y Dashboard del Vendedor

**Descripcion:**
Dashboard para que el vendedor monitoree su tienda: visitas, ventas, conversion rate, productos top, y ticket promedio. Incluye fuentes de trafico y comportamiento del comprador.

**User Stories:**
- US-EC-031: Dashboard: visitas, ventas, conversion, ticket promedio
- US-EC-032: Productos top por ventas y por visitas
- US-EC-033: Fuentes de trafico (directo, Google, WhatsApp, redes)
- US-EC-034: Embudo de conversion: visita → carrito → checkout → pago
- US-EC-035: Reporte exportable PDF/Excel

**Criterios de Aceptacion de la Epica:**
- [ ] KPIs: visitas unicas, pedidos, conversion rate (%), ticket promedio, revenue
- [ ] Graficas de ventas por dia/semana/mes
- [ ] Top 10 productos por ventas ($) y por visitas
- [ ] Fuentes de trafico con porcentaje
- [ ] Embudo: visita → pagina producto → agregar carrito → checkout → pago
- [ ] Porcentaje de abandono en cada paso
- [ ] Filtro por periodo
- [ ] Comparativo vs periodo anterior
- [ ] Export PDF/Excel
- [ ] Tests >= 98%

**Dependencias:** EP-EC-001 a EP-EC-005

**Complejidad:** M (5 user stories)

**Repositorios:** `mf-ecommerce`

---

### EP-EC-008: Facturacion CFDI por Venta

**Descripcion:**
Facturacion automatica CFDI para cada venta realizada en la tienda. El comprador puede solicitar factura desde la pagina de confirmacion de pedido proporcionando su RFC y datos fiscales.

**User Stories:**
- US-EC-036: Solicitud de factura en pagina de confirmacion
- US-EC-037: Generacion y timbrado CFDI por venta
- US-EC-038: Envio de factura por email y WhatsApp
- US-EC-039: Portal de facturacion para compradores
- US-EC-040: Reporte de facturacion mensual para el vendedor

**Criterios de Aceptacion de la Epica:**
- [ ] Formulario de facturacion: RFC, razon social, regimen fiscal, CP, uso CFDI
- [ ] Opcion de solicitar factura hasta 30 dias despues de la compra
- [ ] CFDI 4.0 timbrado via PAC
- [ ] PDF + XML generados y almacenados
- [ ] Envio automatico por email con PDF + XML
- [ ] Envio por WhatsApp si se proporcionó telefono
- [ ] Portal publico: factura.tienda.com/solicitar
- [ ] Reporte mensual: facturas emitidas, monto facturado, IVA
- [ ] Cancelacion de factura con motivos del SAT
- [ ] Tests >= 98%

**Dependencias:** EP-EC-003

**Complejidad:** M (5 user stories)

**Repositorios:** `covacha-payment`

---

## User Stories Detalladas

### EP-EC-001: Builder Visual

#### US-EC-001: Editor drag & drop
**Como** comerciante, **quiero** construir mi tienda arrastrando componentes **para que** no necesite saber programar.

**Criterios de Aceptacion:**
- [ ] Drag & drop de componentes desde sidebar al canvas
- [ ] Componentes: hero, catalogo grid, producto destacado, banner, texto, imagen, video
- [ ] Edicion inline de texto
- [ ] Propiedades configurables por componente (margenes, colores, alineacion)
- [ ] Canvas refleja cambios en tiempo real

#### US-EC-002: Templates por industria
**Como** comerciante, **quiero** elegir un template para mi tipo de negocio **para que** mi tienda se vea profesional desde el inicio.

**Criterios de Aceptacion:**
- [ ] Minimo 6 templates: ropa, comida, servicios, tech, belleza, general
- [ ] Cada template con componentes pre-configurados y paleta de colores
- [ ] Preview del template antes de seleccionar
- [ ] Template editable despues de seleccionar
- [ ] Opcion de empezar desde cero

#### US-EC-003: Personalizacion visual
**Como** comerciante, **quiero** personalizar colores y logo **para que** mi tienda refleje mi marca.

**Criterios de Aceptacion:**
- [ ] Color picker para colores primario y secundario
- [ ] Upload de logo con crop y resize
- [ ] Seleccion de fuentes (Google Fonts)
- [ ] Favicon personalizado
- [ ] Preview en tiempo real de cambios

#### US-EC-004: Preview responsive
**Como** comerciante, **quiero** ver como se ve mi tienda en celular **para que** sepa que mis clientes tendran buena experiencia.

**Criterios de Aceptacion:**
- [ ] Preview en 3 tamaños: mobile (375px), tablet (768px), desktop (1440px)
- [ ] Toggle entre vistas desde el editor
- [ ] Componentes se adaptan responsivamente
- [ ] Preview en nueva pestaña con URL temporal
- [ ] Warning si algun componente no se ve bien en mobile

#### US-EC-005: Publicar tienda
**Como** comerciante, **quiero** publicar mi tienda con un click **para que** mis clientes puedan comprar.

**Criterios de Aceptacion:**
- [ ] Boton "Publicar" despliega la tienda
- [ ] Deploy a S3 + CloudFront en < 60 segundos
- [ ] URL publica: {slug}.mitienda.mx
- [ ] Validacion antes de publicar (minimo 1 producto activo)
- [ ] Historial de publicaciones con opcion de rollback

### EP-EC-002: Catalogo de Productos

#### US-EC-006: CRUD de productos con variantes
**Como** comerciante, **quiero** registrar productos con tallas y colores **para que** mis clientes elijan la variante que quieren.

**Criterios de Aceptacion:**
- [ ] Campos: nombre, descripcion (rich text), precio, precio_descuento, SKU
- [ ] Variantes: atributos configurables (talla, color, material)
- [ ] Combinaciones de variantes con precio y stock independiente
- [ ] Producto con o sin variantes soportado
- [ ] Estado: activo, draft, agotado

#### US-EC-007: Galeria de imagenes
**Como** comerciante, **quiero** subir varias fotos de cada producto **para que** el cliente lo vea desde diferentes angulos.

**Criterios de Aceptacion:**
- [ ] Upload multiple (hasta 10 imagenes por producto)
- [ ] Drag & drop para reordenar (primera = principal)
- [ ] Resize automatico para thumbnails y full-size
- [ ] Almacenamiento en S3 + CDN
- [ ] Formatos: JPG, PNG, WebP

#### US-EC-008: Categorias y colecciones
**Como** comerciante, **quiero** organizar mis productos en categorias **para que** los clientes encuentren lo que buscan.

**Criterios de Aceptacion:**
- [ ] CRUD de categorias con nombre, descripcion, imagen
- [ ] Subcategorias (1 nivel)
- [ ] Colecciones manuales (seleccion de productos especificos)
- [ ] Colecciones automaticas (regla: precio < $500, tag = "oferta")
- [ ] Navegacion por categoria en la tienda publica

#### US-EC-009: Control de stock
**Como** comerciante, **quiero** que el stock se actualice automaticamente **para que** no venda productos que no tengo.

**Criterios de Aceptacion:**
- [ ] Stock por producto o por variante
- [ ] Decremento automatico al confirmar pedido
- [ ] Alerta de stock bajo (configurable: < N unidades)
- [ ] "Agotado" visible automaticamente cuando stock = 0
- [ ] Sincronizacion bidireccional con covacha-inventory

#### US-EC-010: Importacion masiva
**Como** comerciante, **quiero** importar productos desde CSV **para que** no capture uno por uno.

**Criterios de Aceptacion:**
- [ ] CSV con columnas: nombre, descripcion, precio, stock, categoria, imagenes_url
- [ ] Template descargable
- [ ] Validacion y reporte de errores
- [ ] Soporte para variantes en el CSV
- [ ] Maximo 1,000 productos por import

### EP-EC-003: Carrito y Checkout SPEI

#### US-EC-011: Carrito de compras
**Como** comprador, **quiero** agregar productos al carrito **para que** compre todo en una sola transaccion.

**Criterios de Aceptacion:**
- [ ] Agregar producto/variante al carrito
- [ ] Modificar cantidad y eliminar items
- [ ] Subtotal actualizado en tiempo real
- [ ] Persistencia: localStorage + backend (si esta logueado)
- [ ] Indicador de items en carrito visible en header

#### US-EC-012: Datos de envio
**Como** comprador, **quiero** ingresar mi direccion de envio **para que** me llegue el pedido.

**Criterios de Aceptacion:**
- [ ] Formulario: nombre, calle, numero, colonia, CP, ciudad, estado, telefono, email
- [ ] Validacion de CP (catalogo SEPOMEX)
- [ ] Calculo de costo de envio basado en CP destino
- [ ] Opcion "Recoger en tienda" si aplica
- [ ] Guardar direccion para futuras compras (opcional)

#### US-EC-013: Checkout con QR SPEI
**Como** comprador, **quiero** pagar con SPEI escaneando un QR **para que** no necesite tarjeta de credito.

**Criterios de Aceptacion:**
- [ ] Resumen del pedido: productos, envio, total
- [ ] QR de pago SPEI con monto total
- [ ] CLABE y referencia visibles (para pago manual)
- [ ] Timer de expiracion del QR (15 minutos)
- [ ] Instrucciones claras para el comprador

#### US-EC-014: Confirmacion de pago
**Como** sistema, **quiero** confirmar el pago y crear el pedido **para que** el vendedor lo prepare.

**Criterios de Aceptacion:**
- [ ] Deteccion de pago via webhook SPEI
- [ ] Pedido creado con estado NEW
- [ ] Stock decrementado
- [ ] Pantalla de "Gracias por tu compra" con numero de pedido
- [ ] Numero de pedido: {slug}-{secuencia} (ej: ROPA-001)

#### US-EC-015: Confirmacion al comprador
**Como** comprador, **quiero** recibir confirmacion de mi compra **para que** tenga la certeza de que todo salio bien.

**Criterios de Aceptacion:**
- [ ] Email con detalle del pedido: productos, monto, direccion, numero de pedido
- [ ] WhatsApp: "Gracias {nombre}! Tu pedido #{numero} ha sido confirmado"
- [ ] Link para consultar estado del pedido
- [ ] Datos de contacto del vendedor
- [ ] Enviado en < 1 minuto post-pago

### EP-EC-004: Pedidos y Envios

#### US-EC-016: Vista de pedidos
**Como** vendedor, **quiero** ver todos mis pedidos **para que** los prepare y envie.

**Criterios de Aceptacion:**
- [ ] Lista de pedidos con: numero, cliente, monto, estado, fecha
- [ ] Filtros por estado, fecha, monto
- [ ] Conteo por estado en tabs o sidebar
- [ ] Ordenar por fecha (mas recientes primero)
- [ ] Badge de pedidos nuevos sin atender

#### US-EC-017: Detalle del pedido
**Como** vendedor, **quiero** ver todo el detalle de un pedido **para que** sepa que preparar.

**Criterios de Aceptacion:**
- [ ] Productos: nombre, variante, cantidad, precio
- [ ] Datos del comprador: nombre, telefono, email
- [ ] Direccion de envio completa
- [ ] Detalle del pago: monto, referencia SPEI, hora
- [ ] Timeline del pedido: estados con timestamps

#### US-EC-018: Marcar como enviado
**Como** vendedor, **quiero** registrar la guia de envio **para que** el comprador pueda rastrear su paquete.

**Criterios de Aceptacion:**
- [ ] Ingresar: paqueteria (Estafeta, DHL, FedEx, etc.) + numero de guia
- [ ] Estado cambia a SHIPPED
- [ ] Notificacion automatica al comprador
- [ ] Link de tracking generado segun paqueteria
- [ ] Opcion de pegar URL de tracking directamente

#### US-EC-019: Tracking por WhatsApp
**Como** comprador, **quiero** recibir mi tracking por WhatsApp **para que** sepa cuando llega mi pedido.

**Criterios de Aceptacion:**
- [ ] Mensaje: "Tu pedido #{numero} ha sido enviado con {paqueteria}. Rastrear: {link}"
- [ ] Actualizacion al cambiar a DELIVERED (si se integra tracking API)
- [ ] Consulta de estado via bot: "Estado de mi pedido #{numero}"
- [ ] Boton de contactar vendedor si hay problema
- [ ] Template aprobado por Meta

#### US-EC-020: Cancelacion y reembolso
**Como** vendedor, **quiero** cancelar un pedido y reembolsar **para que** gestione devoluciones.

**Criterios de Aceptacion:**
- [ ] Cancelar pedido con motivo (antes o despues de envio)
- [ ] Reembolso via SPEI a la cuenta de origen
- [ ] Stock restaurado al cancelar
- [ ] Notificacion al comprador de cancelacion
- [ ] Estado: CANCELLED o REFUNDED con motivo

### EP-EC-005: WhatsApp Commerce

#### US-EC-021: Notificaciones de pedido
**Como** comprador, **quiero** recibir actualizaciones por WhatsApp **para que** este informado en todo momento.

**Criterios de Aceptacion:**
- [ ] Confirmacion de pedido
- [ ] Pedido enviado con guia
- [ ] Pedido entregado
- [ ] Cancelacion/reembolso
- [ ] Opt-out disponible

#### US-EC-022: Bot de consulta de productos
**Como** comprador, **quiero** preguntar por WhatsApp sobre productos **para que** tome mi decision de compra.

**Criterios de Aceptacion:**
- [ ] "Cuanto cuesta la camisa azul?" → responde con precio y link
- [ ] "Hay talla M disponible?" → consulta stock en tiempo real
- [ ] "Que colores tienen del vestido X?" → lista variantes disponibles
- [ ] Imagen del producto en la respuesta cuando sea posible
- [ ] Fallback a vendedor humano si el bot no entiende

#### US-EC-023: Compra asistida
**Como** comprador, **quiero** que el bot me ayude a comprar **para que** no tenga que navegar la tienda.

**Criterios de Aceptacion:**
- [ ] "Quiero comprar la camisa azul talla M" → agrega al carrito
- [ ] Bot confirma: "Camisa Azul Talla M - $299. Confirmar?"
- [ ] Genera link de checkout con carrito pre-armado
- [ ] Enviar link por WhatsApp
- [ ] Datos de envio capturados via conversacion

#### US-EC-024: Boton de WhatsApp en tienda
**Como** comprador, **quiero** un boton de WhatsApp en la tienda **para que** pueda preguntar dudas.

**Criterios de Aceptacion:**
- [ ] Boton flotante en esquina inferior derecha
- [ ] Click abre WhatsApp con mensaje pre-llenado: "Hola! Tengo una pregunta sobre..."
- [ ] Configurable: mostrar/ocultar, mensaje predefinido
- [ ] Funciona en mobile (abre app) y desktop (abre web.whatsapp.com)
- [ ] Analytics: clicks en boton de WhatsApp

#### US-EC-025: Carrito abandonado
**Como** vendedor, **quiero** recuperar carritos abandonados **para que** no pierda ventas.

**Criterios de Aceptacion:**
- [ ] Detectar carrito abandonado: > 30 min sin checkout + telefono capturado
- [ ] Enviar recordatorio por WhatsApp: "Olvidaste algo! Tu carrito te espera: {link}"
- [ ] Incluir productos del carrito en el mensaje
- [ ] Maximo 1 recordatorio por carrito
- [ ] Configurable: activar/desactivar, tiempo de espera

### EP-EC-006: Dominio y SEO

#### US-EC-026: Dominio personalizado
**Como** comerciante, **quiero** usar mi propio dominio **para que** mi tienda se vea profesional.

**Criterios de Aceptacion:**
- [ ] Configurar dominio: mitienda.com.mx
- [ ] Instrucciones para agregar CNAME en registrar de dominio
- [ ] Validacion de configuracion DNS
- [ ] SSL automatico via ACM
- [ ] Subdominio default: {slug}.mitienda.mx

#### US-EC-027: SSL automatico
**Como** sistema, **quiero** generar certificado SSL **para que** la tienda sea segura.

**Criterios de Aceptacion:**
- [ ] Certificado Let's Encrypt o ACM generado automaticamente
- [ ] Renovacion automatica
- [ ] Redirect HTTP → HTTPS
- [ ] Badge de "Sitio seguro" visible
- [ ] Sin intervencion manual del comerciante

#### US-EC-028: Meta tags configurables
**Como** comerciante, **quiero** configurar meta tags **para que** mi tienda aparezca bien en Google y redes sociales.

**Criterios de Aceptacion:**
- [ ] Title y description por pagina (home, categorias, productos)
- [ ] Open Graph: og:title, og:description, og:image por producto
- [ ] Twitter Card meta tags
- [ ] Default generado automaticamente de datos del producto
- [ ] Editable desde el admin

#### US-EC-029: Sitemap XML
**Como** sistema, **quiero** generar un sitemap **para que** Google indexe todos los productos.

**Criterios de Aceptacion:**
- [ ] Sitemap.xml generado automaticamente
- [ ] Incluye: home, categorias, productos activos
- [ ] Actualizado al publicar cambios
- [ ] Registrado en robots.txt
- [ ] Formato valido (validable con Google Search Console)

#### US-EC-030: Schema.org Product
**Como** sistema, **quiero** agregar Schema.org a los productos **para que** aparezcan como rich snippets en Google.

**Criterios de Aceptacion:**
- [ ] JSON-LD con: name, description, price, availability, image
- [ ] Disponibilidad: InStock, OutOfStock, PreOrder
- [ ] Precio con moneda MXN
- [ ] Brand y category cuando disponible
- [ ] Validable con Google Rich Results Test

### EP-EC-007: Analytics y Dashboard

#### US-EC-031: Dashboard del vendedor
**Como** vendedor, **quiero** ver las metricas de mi tienda **para que** sepa como van las ventas.

**Criterios de Aceptacion:**
- [ ] KPIs: visitas, pedidos, conversion rate, ticket promedio, revenue
- [ ] Grafica de ventas por dia (ultimos 30 dias)
- [ ] Comparativo vs periodo anterior
- [ ] Top 5 productos por ventas
- [ ] Revenue total del mes

#### US-EC-032: Productos top
**Como** vendedor, **quiero** saber cuales productos venden mas **para que** promueva los mejores.

**Criterios de Aceptacion:**
- [ ] Top 10 por revenue ($)
- [ ] Top 10 por unidades vendidas
- [ ] Top 10 por visitas a pagina de producto
- [ ] Filtro por periodo
- [ ] Productos con cero ventas destacados

#### US-EC-033: Fuentes de trafico
**Como** vendedor, **quiero** saber de donde vienen mis compradores **para que** invierta en los canales correctos.

**Criterios de Aceptacion:**
- [ ] Fuentes: directo, Google, WhatsApp, redes sociales, referido
- [ ] Porcentaje de cada fuente
- [ ] Conversion rate por fuente
- [ ] UTM parameters para tracking de campanas
- [ ] Grafica de tendencia por fuente

#### US-EC-034: Embudo de conversion
**Como** vendedor, **quiero** ver donde se pierden los compradores **para que** mejore mi tienda.

**Criterios de Aceptacion:**
- [ ] Etapas: visita → pagina producto → agregar carrito → checkout → pago
- [ ] Porcentaje de conversion entre etapas
- [ ] Drop-off rate por etapa
- [ ] Comparativo por periodo
- [ ] Recomendaciones basicas si conversion < benchmark

#### US-EC-035: Export de reportes
**Como** vendedor, **quiero** exportar reportes **para que** los comparta con mi equipo.

**Criterios de Aceptacion:**
- [ ] Export PDF con graficas y KPIs
- [ ] Export Excel con datos crudos
- [ ] Filtros aplicados reflejados
- [ ] Logo de la tienda en el reporte
- [ ] Envio programado mensual por email

### EP-EC-008: Facturacion CFDI

#### US-EC-036: Solicitud de factura
**Como** comprador, **quiero** solicitar factura de mi compra **para que** pueda deducirla.

**Criterios de Aceptacion:**
- [ ] Formulario en pagina de confirmacion: RFC, razon social, regimen, CP, uso CFDI
- [ ] Validacion de RFC formato
- [ ] Plazo de 30 dias para solicitar
- [ ] Link en email de confirmacion: "Solicita tu factura aqui"
- [ ] Guardar datos fiscales para futuras compras (opcional)

#### US-EC-037: Generacion CFDI
**Como** sistema, **quiero** generar y timbrar CFDI **para que** la factura sea valida ante el SAT.

**Criterios de Aceptacion:**
- [ ] CFDI 4.0 con datos del receptor proporcionados
- [ ] Timbrado via PAC (Finkok)
- [ ] Conceptos: productos del pedido con clave SAT
- [ ] IVA desglosado
- [ ] PDF + XML almacenados en S3

#### US-EC-038: Envio de factura
**Como** comprador, **quiero** recibir mi factura por email **para que** la tenga disponible.

**Criterios de Aceptacion:**
- [ ] Email con PDF + XML adjuntos
- [ ] WhatsApp con PDF si se proporciono telefono
- [ ] Enviado en < 5 minutos post-solicitud
- [ ] Reenvio disponible desde portal
- [ ] Notificacion al vendedor de factura generada

#### US-EC-039: Portal de facturacion
**Como** comprador, **quiero** un portal para solicitar y descargar facturas **para que** lo haga cuando quiera.

**Criterios de Aceptacion:**
- [ ] URL: factura.{dominio-tienda}/solicitar
- [ ] Buscar por numero de pedido + email
- [ ] Formulario de datos fiscales
- [ ] Descarga de PDF y XML
- [ ] Historial de facturas por email

#### US-EC-040: Reporte de facturacion
**Como** vendedor, **quiero** un reporte de facturas emitidas **para que** mi contador lo tenga.

**Criterios de Aceptacion:**
- [ ] Lista de facturas por periodo: numero, cliente, monto, fecha
- [ ] Total facturado e IVA cobrado
- [ ] Export Excel y PDF
- [ ] Descarga masiva de XMLs (ZIP)
- [ ] Filtros por mes, estado (vigente, cancelada)

---

## Timeline

```
Semana 1-4:   EP-EC-001 (Builder visual) - Critico, mas esfuerzo
Semana 2-4:   EP-EC-002 (Catalogo) - En paralelo
Semana 4-6:   EP-EC-003 (Carrito + Checkout)
Semana 5-8:   EP-EC-004 (Pedidos + Envios)
Semana 6-8:   EP-EC-005 (WhatsApp Commerce)
Semana 8-10:  EP-EC-006 (Dominio + SEO)
Semana 10-12: EP-EC-007 (Analytics) + EP-EC-008 (CFDI)
Semana 12-16: QA + optimizacion + templates adicionales
```

**Equipo**: 3 devs (1 backend, 1 frontend/builder, 1 integraciones)
**Costo estimado**: ~$500K MXN

---

## Dependencias entre Epicas

```
EP-EC-001 (Builder) ← Base visual
    |
    ├── EP-EC-006 (Dominio/SEO) → depende de EP-EC-001
    |
EP-EC-002 (Catalogo) ← Base de datos
    |
    └── EP-EC-003 (Carrito/Checkout) → depende de EP-EC-002
            |
            ├── EP-EC-004 (Pedidos) → depende de EP-EC-003
            │       |
            │       └── EP-EC-005 (WhatsApp) → depende de EP-EC-004
            |
            └── EP-EC-008 (CFDI) → depende de EP-EC-003

EP-EC-007 (Analytics) → depende de EP-EC-001 a EP-EC-005
```

**Dependencias externas:**
- mf-marketing: Landing editor para builder
- covacha-payment: Motor SPEI para checkout
- covacha-botia: WhatsApp Business API
- covacha-inventory: Sincronizacion de productos
- POS Virtual (EP-POS): Reutiliza motor QR de pago

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|------------|
| Builder visual complejo de desarrollar | Alta | Alto | Reutilizar 70% de mf-marketing, limitar features V1 |
| Competencia fuerte (Shopify, Tiendanube) | Alta | Alto | Diferenciar con SPEI + WhatsApp + precio MXN |
| Performance de tiendas generadas | Media | Alto | SSG (Static Site Generation), CDN agresivo |
| Integracion de envios (tracking API) | Media | Medio | V1: tracking manual, V2: integracion con APIs |
| SEO de tiendas nuevas (baja autoridad) | Alta | Medio | Schema.org, contenido unico, blog integrado V2 |
