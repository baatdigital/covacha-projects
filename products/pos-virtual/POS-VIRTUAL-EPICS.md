# POS Virtual - Cobro con QR + SPEI Instantaneo (EP-POS-001 a EP-POS-008)

**Fecha**: 2026-03-14
**Product Owner**: SuperPago
**Estado**: Planificacion
**GitHub Issue**: baatdigital/covacha-projects#128
**Score**: 9/10 | **Time to Market**: 8 semanas | **Reuso**: 80%

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

Terminal punto de venta virtual que genera codigos QR para cobro instantaneo via SPEI. Sin terminal fisica, sin comisiones de tarjeta de credito. Dirigido a comercios pequenos (fondas, tiendas, mercados) que necesitan cobrar de forma facil y economica.

**Propuesta de valor**: Cobro inmediato con SPEI a traves de un QR, confirmacion en menos de 5 segundos, y cero comisiones en plan Business.

---

## Analisis de Mercado

| Metrica | Valor |
|---------|-------|
| **TAM Mexico** | $14.4B MXN/ano (6M comercios x $200/mes) |
| **SAM** | $2.4B MXN/ano (1M comercios con smartphone) |
| **SOM Year 1** | $12M MXN/ano (5,000 comercios x $199/mes) |

### Problema de Mercado

- Comisiones de TPV tradicional: 2.5-3.5% en Mexico
- SPEI es gratis/bajo costo pero no tiene interfaz de punto de venta
- Comercios pequenos no pueden costear terminales fisicas

### Modelo de Revenue

| Plan | Precio MXN/mes | Transacciones | Comision |
|------|---------------|---------------|---------|
| Free | $0 | 50/mes | 1.5% |
| Pro | $199 | Ilimitadas | 0.5% |
| Business | $499 | Ilimitadas | 0% |

---

## Reutilizacion del Ecosistema

| Componente | Repo Existente | Reutilizacion | Descripcion |
|-----------|---------------|---------------|-------------|
| Motor SPEI completo | covacha-payment | 100% | Recepcion/envio SPEI, webhooks |
| Multi-tenant | covacha-core | 100% | Organizaciones, autenticacion |
| Ledger partida doble | covacha-payment | 100% | Registro contable de transacciones |
| Notificaciones | covacha-notification | 90% | Push, WhatsApp, email |
| Shell MF | mf-core | 100% | Module Federation, routing |
| Modelos Pydantic | covacha-libs | 80% | Modelos base, repositorios |
| **Nuevo** | mf-pos | 0% | Micro-frontend POS (crear) |
| **Nuevo** | covacha-payment (QR) | 30% | Generacion QR + link de pago |

**Reutilizacion total estimada**: 80%

---

## Mapa de Epicas

| ID | Epica | Complejidad | Semana | Dependencias | Estado |
|----|-------|-------------|--------|--------------|--------|
| EP-POS-001 | Motor de Cobro QR + SPEI | L | 1-2 | EP-SP-001, EP-SP-002 | Planificacion |
| EP-POS-002 | Confirmacion de Pago en Tiempo Real | M | 2-3 | EP-POS-001 | Planificacion |
| EP-POS-003 | Catalogo de Productos POS | M | 2-3 | EP-POS-001 | Planificacion |
| EP-POS-004 | Corte de Caja y Reportes | M | 3-4 | EP-POS-001, EP-POS-002 | Planificacion |
| EP-POS-005 | Links de Pago Compartibles | S | 3-4 | EP-POS-001 | Planificacion |
| EP-POS-006 | Multi-Empleado y Sucursales | M | 4-5 | EP-POS-001 | Planificacion |
| EP-POS-007 | mf-pos - Micro-Frontend POS | L | 3-6 | EP-POS-001 a EP-POS-006 | Planificacion |
| EP-POS-008 | Facturacion CFDI Automatica | M | 6-8 | EP-POS-002, EP-POS-004 | Planificacion |

**Totales:**
- 8 epicas
- 40 user stories (US-POS-001 a US-POS-040)
- Estimacion total: ~56 dev-days (8 semanas, 2 devs)

---

## Epicas Detalladas

---

### EP-POS-001: Motor de Cobro QR + SPEI

**Descripcion:**
Motor backend que genera codigos QR con monto especifico vinculados a una referencia SPEI unica. Cuando el cliente escanea el QR y realiza la transferencia SPEI, el sistema detecta el pago via webhook y lo asocia a la transaccion POS. Reutiliza el motor SPEI completo de covacha-payment.

**User Stories:**
- US-POS-001: Generar QR con monto y referencia SPEI unica
- US-POS-002: Detectar pago SPEI entrante y asociar a cobro POS
- US-POS-003: Generar URL corta embebida en QR para pago web
- US-POS-004: Expirar QR despues de tiempo configurable
- US-POS-005: Cobro con monto abierto (cliente ingresa cantidad)

**Criterios de Aceptacion de la Epica:**
- [ ] QR generado con referencia SPEI unica por transaccion
- [ ] URL corta embebida en QR con instrucciones de pago
- [ ] Deteccion automatica de pago via webhook SPEI en < 5 segundos
- [ ] Asociacion pago-cobro por referencia unica
- [ ] Soporte monto fijo y monto abierto
- [ ] Expiracion configurable de QR (default 15 min)
- [ ] Idempotencia estricta con `idempotency_key`
- [ ] QR incluye datos del comercio (nombre, concepto)
- [ ] Soporte multi-tenant (cada comercio genera sus propios QR)
- [ ] Tests >= 98%

**Dependencias:** EP-SP-001 (Account Core Engine), EP-SP-002 (Monato SPEI Driver)

**Complejidad:** L (5 user stories, integracion SPEI + QR)

**Repositorios:** `covacha-payment`

---

### EP-POS-002: Confirmacion de Pago en Tiempo Real

**Descripcion:**
Sistema de notificacion en tiempo real que alerta al comerciante cuando un pago es recibido. Incluye sonido/vibracion en la app, notificacion push, y actualizacion instantanea de la UI via WebSocket o Server-Sent Events.

**User Stories:**
- US-POS-006: Notificacion sonora y vibracion al recibir pago
- US-POS-007: Actualizacion en tiempo real de estado del cobro (SSE/WebSocket)
- US-POS-008: Pantalla de confirmacion con detalle del pago
- US-POS-009: Notificacion push cuando la app esta en background
- US-POS-010: Recibo digital automatico para el pagador

**Criterios de Aceptacion de la Epica:**
- [ ] Confirmacion visual + sonora en < 5 segundos desde el pago SPEI
- [ ] WebSocket o SSE para actualizacion en tiempo real
- [ ] Sonido configurable por comercio
- [ ] Vibracion en dispositivos moviles
- [ ] Push notification cuando app en background
- [ ] Pantalla de confirmacion con: monto, hora, referencia, nombre pagador
- [ ] Recibo digital generado y disponible para compartir
- [ ] Funciona en mala conexion (retry automatico de conexion)
- [ ] Historico de notificaciones del dia
- [ ] Tests >= 98%

**Dependencias:** EP-POS-001 (Motor de cobro)

**Complejidad:** M (5 user stories)

**Repositorios:** `covacha-payment`, `covacha-notification`

---

### EP-POS-003: Catalogo de Productos POS

**Descripcion:**
Catalogo de productos/servicios del comercio integrado en el POS para cobro rapido. El vendedor selecciona productos del catalogo y el sistema genera el QR con el total. Similar a la funcionalidad de mf-inventory pero optimizada para flujo POS rapido.

**User Stories:**
- US-POS-011: CRUD de productos con nombre, precio, imagen, SKU
- US-POS-012: Busqueda rapida de productos por nombre o codigo
- US-POS-013: Carrito de cobro: agregar multiples productos
- US-POS-014: Calcular total con descuentos y generar QR del carrito
- US-POS-015: Categorias de productos para organizacion

**Criterios de Aceptacion de la Epica:**
- [ ] CRUD completo de productos (nombre, precio, imagen, SKU, categoria)
- [ ] Busqueda rapida por nombre o codigo de barras
- [ ] Carrito con multiples productos y cantidades
- [ ] Calculo de total con soporte para descuentos porcentuales y fijos
- [ ] QR generado con total del carrito y detalle de productos
- [ ] Importacion masiva de productos via CSV
- [ ] Categorias configurables
- [ ] Productos favoritos/frecuentes para acceso rapido
- [ ] Sincronizacion offline del catalogo
- [ ] Tests >= 98%

**Dependencias:** EP-POS-001 (Motor de cobro)

**Complejidad:** M (5 user stories)

**Repositorios:** `covacha-payment`, `covacha-inventory`

---

### EP-POS-004: Corte de Caja y Reportes

**Descripcion:**
Sistema de corte de caja diario con resumen de ventas, dashboard de metricas, y reportes exportables. Permite al comerciante cerrar el dia con un resumen claro de cobros recibidos, desglose por metodo, y tendencias.

**User Stories:**
- US-POS-016: Corte de caja diario con resumen de transacciones
- US-POS-017: Dashboard de ventas por hora, dia, semana, mes
- US-POS-018: Reporte exportable PDF/Excel de transacciones
- US-POS-019: Desglose por empleado/vendedor
- US-POS-020: Comparativo de ventas vs periodo anterior

**Criterios de Aceptacion de la Epica:**
- [ ] Corte de caja: total cobrado, numero de transacciones, ticket promedio
- [ ] Desglose por hora del dia
- [ ] Dashboard con graficas de ventas (linea, barras)
- [ ] Filtros por rango de fecha, empleado, sucursal
- [ ] Exportacion a PDF y Excel
- [ ] Comparativo vs dia/semana/mes anterior
- [ ] Top productos vendidos del periodo
- [ ] Indicadores: ticket promedio, transacciones/hora, conversion
- [ ] Acceso desde mobile y desktop
- [ ] Tests >= 98%

**Dependencias:** EP-POS-001, EP-POS-002

**Complejidad:** M (5 user stories)

**Repositorios:** `covacha-payment`

---

### EP-POS-005: Links de Pago Compartibles

**Descripcion:**
Generacion de links de pago compartibles por WhatsApp, SMS, email, o cualquier medio. El link abre una pagina web con los datos del cobro y QR para pagar. Ideal para cobro a distancia sin necesidad de que el cliente este fisicamente en el comercio.

**User Stories:**
- US-POS-021: Generar link de pago con monto y concepto
- US-POS-022: Pagina web de pago con QR y datos del comercio
- US-POS-023: Compartir link por WhatsApp con un click
- US-POS-024: Historial de links generados con estado de pago
- US-POS-025: Link con monto abierto (cliente decide cuanto pagar)

**Criterios de Aceptacion de la Epica:**
- [ ] Link corto generado (pos.superpago.com.mx/p/XXXXX)
- [ ] Pagina web responsive con datos del cobro y QR
- [ ] Boton de compartir por WhatsApp nativo
- [ ] Compartir por SMS y email
- [ ] Expiracion configurable del link
- [ ] Soporte monto fijo y monto abierto
- [ ] Historial de links con estado: pendiente, pagado, expirado
- [ ] Personalizacion con logo del comercio
- [ ] Sin necesidad de app instalada para el pagador
- [ ] Tests >= 98%

**Dependencias:** EP-POS-001

**Complejidad:** S (5 user stories, reutiliza EP-POS-001)

**Repositorios:** `covacha-payment`

---

### EP-POS-006: Multi-Empleado y Sucursales

**Descripcion:**
Sistema de permisos que permite al comercio tener multiples empleados usando el POS, cada uno con su perfil, y organizar cobros por sucursal. Incluye roles (admin, cajero), permisos granulares, y reportes por empleado/sucursal.

**User Stories:**
- US-POS-026: CRUD de empleados con roles (admin, cajero, visor)
- US-POS-027: Permisos granulares por rol (cobrar, cancelar, reportes)
- US-POS-028: CRUD de sucursales con datos de ubicacion
- US-POS-029: Asignacion de empleados a sucursales
- US-POS-030: Filtros de reporte por empleado y sucursal

**Criterios de Aceptacion de la Epica:**
- [ ] Roles: admin (todo), cajero (cobrar + ver), visor (solo ver)
- [ ] Permisos granulares configurables por rol
- [ ] CRUD de empleados con email y telefono
- [ ] CRUD de sucursales con nombre, direccion, horario
- [ ] Asignacion empleado-sucursal
- [ ] Cada cobro registra empleado y sucursal
- [ ] Reportes filtrados por empleado y/o sucursal
- [ ] Invitacion de empleado por email o WhatsApp
- [ ] Limite de empleados segun plan (Free: 1, Pro: 5, Business: ilimitados)
- [ ] Tests >= 98%

**Dependencias:** EP-POS-001

**Complejidad:** M (5 user stories)

**Repositorios:** `covacha-core`, `covacha-payment`

---

### EP-POS-007: mf-pos - Micro-Frontend POS

**Descripcion:**
Nuevo micro-frontend Angular para la interfaz del punto de venta virtual. Diseno mobile-first optimizado para uso en mostrador con pantalla tactil. Incluye todas las pantallas: cobro, catalogo, corte de caja, reportes, configuracion. Se integra con mf-core via Module Federation.

**User Stories:**
- US-POS-031: Scaffold mf-pos con Module Federation
- US-POS-032: Pantalla principal de cobro (monto + generar QR)
- US-POS-033: Pantalla de catalogo y carrito
- US-POS-034: Pantalla de corte de caja y reportes
- US-POS-035: Pantalla de configuracion (sucursales, empleados, planes)

**Criterios de Aceptacion de la Epica:**
- [ ] mf-pos registrado en mf-core como micro-frontend
- [ ] Diseno mobile-first con soporte desktop
- [ ] Pantalla de cobro: input monto + boton generar QR + vista QR
- [ ] Pantalla de catalogo con busqueda y carrito
- [ ] Pantalla de corte de caja con resumen diario
- [ ] Dashboard de reportes con graficas
- [ ] Configuracion de perfil de comercio
- [ ] PWA: funciona offline para catalogo
- [ ] Standalone components, OnPush, Signals
- [ ] Tests >= 98%

**Dependencias:** EP-POS-001 a EP-POS-006 (APIs), EP-SP-007 (patron mf-sp)

**Complejidad:** L (5 user stories, frontend completo)

**Repositorios:** `mf-pos`, `mf-core`

---

### EP-POS-008: Facturacion CFDI Automatica

**Descripcion:**
Integracion con servicio de timbrado CFDI para generar facturas automaticamente despues de cada venta. El comercio configura sus datos fiscales y el sistema genera CFDIs validos ante el SAT. Incluye portal de descarga para el cliente.

**User Stories:**
- US-POS-036: Configuracion de datos fiscales del comercio (RFC, regimen, CSDs)
- US-POS-037: Generacion automatica de CFDI post-pago
- US-POS-038: Portal publico para descarga de factura por referencia
- US-POS-039: Envio de factura por WhatsApp y email
- US-POS-040: Cancelacion de CFDI con motivo

**Criterios de Aceptacion de la Epica:**
- [ ] Configuracion de datos fiscales: RFC, regimen fiscal, CSDs
- [ ] Generacion de CFDI 4.0 valido post-pago
- [ ] Timbrado via PAC integrado (Finkok o similar)
- [ ] PDF + XML generados y almacenados en S3
- [ ] Portal publico de descarga por referencia de pago
- [ ] Envio automatico por WhatsApp y email
- [ ] Cancelacion con motivos del SAT
- [ ] Complemento de pago para pagos parciales
- [ ] Reporte mensual de facturas emitidas
- [ ] Tests >= 98%

**Dependencias:** EP-POS-002, EP-POS-004

**Complejidad:** M (5 user stories, integracion SAT)

**Repositorios:** `covacha-payment`

---

## User Stories Detalladas

### EP-POS-001: Motor de Cobro QR + SPEI

#### US-POS-001: Generar QR con monto y referencia SPEI unica
**Como** comerciante, **quiero** generar un codigo QR con un monto especifico **para que** mi cliente pueda pagar escaneando el QR.

**Criterios de Aceptacion:**
- [ ] Endpoint `POST /pos/charges` con monto, concepto, moneda
- [ ] Genera referencia SPEI unica (formato: POS-{org_id}-{timestamp}-{random})
- [ ] QR contiene URL corta con referencia de pago
- [ ] Respuesta incluye: QR base64, URL, referencia, monto, expiracion
- [ ] Validacion de monto minimo ($1 MXN) y maximo (configurable por plan)

#### US-POS-002: Detectar pago SPEI entrante y asociar a cobro POS
**Como** sistema, **quiero** detectar automaticamente un pago SPEI **para que** el cobro POS se marque como pagado instantaneamente.

**Criterios de Aceptacion:**
- [ ] Webhook de SPEI entrante busca referencia POS activa
- [ ] Asocia pago SPEI con cobro POS por referencia
- [ ] Actualiza estado del cobro: PENDING -> PAID
- [ ] Registra: monto pagado, hora, banco origen, nombre pagador
- [ ] Maneja pagos parciales (monto menor al esperado)

#### US-POS-003: Generar URL corta embebida en QR para pago web
**Como** cliente, **quiero** escanear un QR y ver una pagina con los datos del pago **para que** pueda transferir facilmente.

**Criterios de Aceptacion:**
- [ ] URL corta tipo pos.superpago.com.mx/p/XXXXX
- [ ] Pagina muestra: nombre comercio, monto, concepto, CLABE destino
- [ ] Boton de copiar CLABE + referencia
- [ ] Compatible con todas las apps bancarias
- [ ] Pagina responsive (mobile-first)

#### US-POS-004: Expirar QR despues de tiempo configurable
**Como** comerciante, **quiero** que los QR expiren automaticamente **para que** no se acumulen cobros pendientes.

**Criterios de Aceptacion:**
- [ ] Tiempo de expiracion configurable (default: 15 minutos)
- [ ] QR expirado muestra mensaje de "cobro expirado"
- [ ] Cobros expirados se marcan como EXPIRED en la base de datos
- [ ] Job de limpieza que expira cobros pendientes
- [ ] Notificacion al comerciante si un cobro expira sin pago

#### US-POS-005: Cobro con monto abierto
**Como** comerciante, **quiero** generar un QR sin monto fijo **para que** el cliente decida cuanto pagar (propinas, donativos).

**Criterios de Aceptacion:**
- [ ] Endpoint soporta campo `amount: null` para monto abierto
- [ ] Pagina de pago muestra input para que el cliente ingrese monto
- [ ] Monto minimo y maximo configurables
- [ ] QR indica visualmente que es monto abierto
- [ ] El pago se registra con el monto que el cliente envio

### EP-POS-002: Confirmacion de Pago en Tiempo Real

#### US-POS-006: Notificacion sonora y vibracion al recibir pago
**Como** comerciante, **quiero** escuchar un sonido y sentir vibracion cuando recibo un pago **para que** sepa inmediatamente que el cobro fue exitoso.

**Criterios de Aceptacion:**
- [ ] Sonido de confirmacion reproducido automaticamente
- [ ] Vibracion en dispositivos moviles (Vibration API)
- [ ] Sonido configurable (varios opciones)
- [ ] Volumen independiente del sistema
- [ ] Funciona con la app en primer plano

#### US-POS-007: Actualizacion en tiempo real de estado del cobro
**Como** comerciante, **quiero** ver el estado del cobro actualizarse en tiempo real **para que** no tenga que refrescar la pagina.

**Criterios de Aceptacion:**
- [ ] Conexion SSE o WebSocket para actualizaciones en tiempo real
- [ ] Estado cambia visualmente: Esperando -> Procesando -> Pagado
- [ ] Animacion visual al confirmar pago
- [ ] Reconexion automatica si se pierde conexion
- [ ] Indicador de conexion activa visible

#### US-POS-008: Pantalla de confirmacion con detalle del pago
**Como** comerciante, **quiero** ver los detalles del pago recibido **para que** pueda confirmar que el monto es correcto.

**Criterios de Aceptacion:**
- [ ] Pantalla muestra: monto, hora, referencia, nombre del pagador
- [ ] Indicador visual grande de "PAGADO" en verde
- [ ] Opcion de imprimir recibo (si hay impresora conectada)
- [ ] Boton para nuevo cobro rapido
- [ ] Detalle del banco de origen

#### US-POS-009: Notificacion push cuando app en background
**Como** comerciante, **quiero** recibir notificacion push cuando recibo un pago y la app esta cerrada **para que** no pierda ninguna confirmacion.

**Criterios de Aceptacion:**
- [ ] Push notification via Service Worker (PWA)
- [ ] Notificacion incluye: monto y nombre del pagador
- [ ] Click en notificacion abre la app en el detalle del pago
- [ ] Funciona con app cerrada/background
- [ ] Configurable: activar/desactivar push

#### US-POS-010: Recibo digital automatico para el pagador
**Como** pagador, **quiero** recibir un recibo digital de mi pago **para que** tenga comprobante de la transaccion.

**Criterios de Aceptacion:**
- [ ] Recibo generado automaticamente al confirmar pago
- [ ] Recibo incluye: comercio, monto, fecha, referencia, concepto
- [ ] Disponible en la URL de pago (pagina actualiza a "Pagado")
- [ ] Opcion de enviar recibo por WhatsApp al pagador
- [ ] Formato PDF descargable

### EP-POS-003: Catalogo de Productos POS

#### US-POS-011: CRUD de productos
**Como** comerciante, **quiero** registrar mis productos con nombre, precio e imagen **para que** pueda cobrar rapidamente seleccionandolos.

**Criterios de Aceptacion:**
- [ ] Endpoint CRUD `POST/GET/PUT/DELETE /pos/products`
- [ ] Campos: nombre, precio, descripcion, imagen, SKU, categoria_id
- [ ] Validacion de campos obligatorios (nombre, precio)
- [ ] Imagen almacenada en S3 con CDN
- [ ] Paginacion y filtros por categoria

#### US-POS-012: Busqueda rapida de productos
**Como** vendedor, **quiero** buscar productos por nombre o codigo **para que** pueda encontrarlos rapido durante el cobro.

**Criterios de Aceptacion:**
- [ ] Busqueda por nombre con autocompletado (debounce 300ms)
- [ ] Busqueda por SKU/codigo exacto
- [ ] Resultados en < 200ms
- [ ] Ordenamiento por frecuencia de uso
- [ ] Busqueda funciona offline (catalogo cacheado)

#### US-POS-013: Carrito de cobro
**Como** vendedor, **quiero** agregar multiples productos a un cobro **para que** pueda cobrar todo en una sola transaccion.

**Criterios de Aceptacion:**
- [ ] Agregar/quitar productos al carrito
- [ ] Modificar cantidades
- [ ] Subtotal actualizado en tiempo real
- [ ] Limpiar carrito con confirmacion
- [ ] Persistencia del carrito entre sesiones

#### US-POS-014: Calcular total con descuentos y generar QR
**Como** vendedor, **quiero** aplicar descuentos y generar el QR del total **para que** el cliente pague el monto correcto.

**Criterios de Aceptacion:**
- [ ] Descuento porcentual (ej: 10% off)
- [ ] Descuento fijo (ej: -$50 MXN)
- [ ] Calculo de IVA configurable (incluido/excluido)
- [ ] Boton "Cobrar" genera QR con total final
- [ ] Detalle del cobro incluye lista de productos

#### US-POS-015: Categorias de productos
**Como** comerciante, **quiero** organizar mis productos en categorias **para que** sea mas facil encontrarlos.

**Criterios de Aceptacion:**
- [ ] CRUD de categorias con nombre, icono, color
- [ ] Filtro por categoria en la pantalla de cobro
- [ ] Drag & drop para reordenar categorias
- [ ] Subcategorias opcionales (1 nivel)
- [ ] Categoria "Favoritos" con productos frecuentes

### EP-POS-004: Corte de Caja y Reportes

#### US-POS-016: Corte de caja diario
**Como** comerciante, **quiero** hacer corte de caja al final del dia **para que** sepa cuanto vendimos.

**Criterios de Aceptacion:**
- [ ] Endpoint `POST /pos/cash-register/close` cierra el dia
- [ ] Resumen: total cobrado, numero de transacciones, ticket promedio
- [ ] Desglose por hora
- [ ] Listado de todas las transacciones del dia
- [ ] Corte almacenado con fecha/hora de cierre

#### US-POS-017: Dashboard de ventas
**Como** comerciante, **quiero** ver graficas de mis ventas **para que** pueda entender tendencias.

**Criterios de Aceptacion:**
- [ ] Grafica de ventas por hora del dia actual
- [ ] Grafica de ventas por dia (ultimos 30 dias)
- [ ] Grafica de ventas por semana y mes
- [ ] Selector de rango de fechas
- [ ] KPIs: total, transacciones, ticket promedio, producto top

#### US-POS-018: Reporte exportable PDF/Excel
**Como** comerciante, **quiero** exportar mis reportes **para que** pueda entregarselos a mi contador.

**Criterios de Aceptacion:**
- [ ] Exportar a PDF con formato profesional
- [ ] Exportar a Excel con datos crudos
- [ ] Filtros aplicados se reflejan en el reporte
- [ ] Logo del comercio en el reporte
- [ ] Envio por email del reporte

#### US-POS-019: Desglose por empleado
**Como** administrador, **quiero** ver las ventas de cada empleado **para que** pueda evaluar su desempeno.

**Criterios de Aceptacion:**
- [ ] Ranking de empleados por monto cobrado
- [ ] Filtro por empleado en todos los reportes
- [ ] Numero de transacciones por empleado
- [ ] Ticket promedio por empleado
- [ ] Comparativo entre empleados

#### US-POS-020: Comparativo de ventas
**Como** comerciante, **quiero** comparar mis ventas con periodos anteriores **para que** sepa si estoy creciendo.

**Criterios de Aceptacion:**
- [ ] Comparativo dia vs dia anterior
- [ ] Comparativo semana vs semana anterior
- [ ] Comparativo mes vs mes anterior
- [ ] Indicador visual: verde (crecimiento), rojo (decrecimiento)
- [ ] Porcentaje de cambio

### EP-POS-005: Links de Pago Compartibles

#### US-POS-021: Generar link de pago
**Como** comerciante, **quiero** generar un link de pago **para que** pueda cobrar a distancia.

**Criterios de Aceptacion:**
- [ ] Endpoint `POST /pos/payment-links` genera link
- [ ] URL corta: pos.superpago.com.mx/p/XXXXX
- [ ] Campos: monto, concepto, expiracion
- [ ] Link unico por cobro
- [ ] Metadata del comercio incluida

#### US-POS-022: Pagina web de pago
**Como** cliente, **quiero** abrir un link y ver los datos para pagar **para que** pueda hacer la transferencia facilmente.

**Criterios de Aceptacion:**
- [ ] Pagina responsive con datos del cobro
- [ ] QR visible para escanear desde app bancaria
- [ ] CLABE y referencia con boton de copiar
- [ ] Logo y nombre del comercio
- [ ] Sin necesidad de registro/login

#### US-POS-023: Compartir link por WhatsApp
**Como** comerciante, **quiero** compartir el link por WhatsApp **para que** el cliente lo reciba instantaneamente.

**Criterios de Aceptacion:**
- [ ] Boton "Compartir por WhatsApp" con API de WhatsApp
- [ ] Mensaje predefinido con: "Hola, aqui esta tu link de pago: [link]"
- [ ] Preview del link con Open Graph tags
- [ ] Funciona en mobile y desktop (web.whatsapp.com)
- [ ] Registro de envio en historial

#### US-POS-024: Historial de links generados
**Como** comerciante, **quiero** ver todos los links que he generado **para que** pueda dar seguimiento a cobros pendientes.

**Criterios de Aceptacion:**
- [ ] Lista de links con estado: pendiente, pagado, expirado
- [ ] Filtros por estado y fecha
- [ ] Opcion de reenviar link pendiente
- [ ] Opcion de cancelar link pendiente
- [ ] Detalle del pago cuando fue pagado

#### US-POS-025: Link con monto abierto
**Como** comerciante, **quiero** crear un link sin monto fijo **para que** el cliente decida cuanto pagar.

**Criterios de Aceptacion:**
- [ ] Link con monto abierto soportado
- [ ] Pagina de pago muestra input de monto
- [ ] Monto minimo y maximo configurables
- [ ] Ideal para propinas, donativos, pagos parciales
- [ ] Mismo flujo de confirmacion que monto fijo

### EP-POS-006: Multi-Empleado y Sucursales

#### US-POS-026: CRUD de empleados con roles
**Como** administrador, **quiero** registrar empleados con diferentes roles **para que** cada uno tenga acceso apropiado.

**Criterios de Aceptacion:**
- [ ] Endpoint CRUD `/pos/employees`
- [ ] Roles: admin, cajero, visor
- [ ] Campos: nombre, email, telefono, rol, sucursal
- [ ] Invitacion por email con link de activacion
- [ ] Desactivar empleado sin eliminar historial

#### US-POS-027: Permisos granulares por rol
**Como** administrador, **quiero** definir que puede hacer cada rol **para que** los empleados solo accedan a lo necesario.

**Criterios de Aceptacion:**
- [ ] Admin: cobrar, cancelar, reportes, configuracion, empleados
- [ ] Cajero: cobrar, ver historial del dia
- [ ] Visor: solo ver reportes y dashboard
- [ ] Permisos evaluados en backend y frontend
- [ ] Roles personalizables en plan Business

#### US-POS-028: CRUD de sucursales
**Como** administrador, **quiero** registrar mis sucursales **para que** pueda organizar los cobros por ubicacion.

**Criterios de Aceptacion:**
- [ ] Endpoint CRUD `/pos/branches`
- [ ] Campos: nombre, direccion, telefono, horario
- [ ] Geolocalizacion opcional
- [ ] Cada cobro asociado a una sucursal
- [ ] Sucursal default para comercios con una sola ubicacion

#### US-POS-029: Asignacion de empleados a sucursales
**Como** administrador, **quiero** asignar empleados a sucursales **para que** los reportes reflejen donde se cobro.

**Criterios de Aceptacion:**
- [ ] Un empleado puede estar asignado a 1+ sucursales
- [ ] Sucursal activa seleccionable al iniciar sesion
- [ ] Cobros se registran con sucursal del empleado
- [ ] Historial de cambios de sucursal
- [ ] Admin ve todas las sucursales sin restriccion

#### US-POS-030: Filtros de reporte por empleado y sucursal
**Como** administrador, **quiero** filtrar reportes por empleado y sucursal **para que** pueda analizar ventas por ubicacion.

**Criterios de Aceptacion:**
- [ ] Filtro por sucursal en todos los reportes
- [ ] Filtro por empleado en todos los reportes
- [ ] Combinacion de filtros (sucursal + empleado + fecha)
- [ ] Corte de caja por sucursal
- [ ] Comparativo entre sucursales

### EP-POS-007: mf-pos - Micro-Frontend POS

#### US-POS-031: Scaffold mf-pos con Module Federation
**Como** desarrollador, **quiero** crear el micro-frontend mf-pos **para que** se integre con mf-core via Module Federation.

**Criterios de Aceptacion:**
- [ ] Angular standalone app con Native Federation
- [ ] Registrado como remoteEntry en mf-core
- [ ] Routing: /pos/* con lazy loading
- [ ] Shared dependencies: @angular/core, rxjs
- [ ] Build de produccion funcional

#### US-POS-032: Pantalla principal de cobro
**Como** vendedor, **quiero** una pantalla simple para cobrar **para que** pueda generar un QR rapidamente.

**Criterios de Aceptacion:**
- [ ] Input grande de monto (numpad touch-friendly)
- [ ] Campo de concepto opcional
- [ ] Boton "Cobrar" prominente
- [ ] Vista de QR generado con animacion
- [ ] Estado del cobro en tiempo real

#### US-POS-033: Pantalla de catalogo y carrito
**Como** vendedor, **quiero** ver mi catalogo y armar un carrito **para que** pueda cobrar multiples productos.

**Criterios de Aceptacion:**
- [ ] Grid de productos con imagen y precio
- [ ] Filtro por categoria
- [ ] Barra de busqueda
- [ ] Carrito lateral/inferior con resumen
- [ ] Boton "Cobrar carrito" genera QR del total

#### US-POS-034: Pantalla de corte de caja y reportes
**Como** comerciante, **quiero** ver mi corte de caja y reportes **para que** pueda monitorear mis ventas.

**Criterios de Aceptacion:**
- [ ] Vista de corte de caja actual (dia en curso)
- [ ] Boton de cerrar caja
- [ ] Graficas de ventas con ng2-charts o ngx-echarts
- [ ] Tabla de transacciones con paginacion
- [ ] Filtros de fecha y exportacion

#### US-POS-035: Pantalla de configuracion
**Como** administrador, **quiero** configurar mi POS **para que** se adapte a mi negocio.

**Criterios de Aceptacion:**
- [ ] Seccion: datos del comercio (nombre, logo, RFC)
- [ ] Seccion: empleados y sucursales
- [ ] Seccion: plan y facturacion
- [ ] Seccion: personalizacion (sonido, QR, recibos)
- [ ] Seccion: integraciones (facturacion CFDI)

### EP-POS-008: Facturacion CFDI Automatica

#### US-POS-036: Configuracion de datos fiscales
**Como** comerciante, **quiero** configurar mis datos fiscales **para que** el sistema pueda emitir facturas validas.

**Criterios de Aceptacion:**
- [ ] Formulario: RFC, razon social, regimen fiscal, CP fiscal
- [ ] Upload de CSD (certificado .cer y llave .key)
- [ ] Validacion de CSD contra SAT
- [ ] Almacenamiento seguro de CSDs (encriptado en S3)
- [ ] Verificacion de datos en lista LCO del SAT

#### US-POS-037: Generacion automatica de CFDI post-pago
**Como** comerciante, **quiero** que se genere factura automaticamente al recibir un pago **para que** mi cliente tenga su comprobante fiscal.

**Criterios de Aceptacion:**
- [ ] CFDI 4.0 generado al confirmar pago
- [ ] Timbrado via PAC integrado
- [ ] PDF + XML almacenados en S3
- [ ] Datos del receptor obtenidos de la referencia de pago
- [ ] Factura disponible inmediatamente post-pago

#### US-POS-038: Portal publico para descarga de factura
**Como** cliente, **quiero** descargar mi factura desde un portal web **para que** no dependa del comercio para obtenerla.

**Criterios de Aceptacion:**
- [ ] URL publica: factura.superpago.com.mx
- [ ] Busqueda por referencia de pago + RFC receptor
- [ ] Descarga de PDF y XML
- [ ] Vista previa de la factura en el navegador
- [ ] Sin necesidad de login

#### US-POS-039: Envio de factura por WhatsApp y email
**Como** comerciante, **quiero** enviar la factura al cliente por WhatsApp **para que** la reciba inmediatamente.

**Criterios de Aceptacion:**
- [ ] Envio automatico por WhatsApp (PDF adjunto)
- [ ] Envio por email con PDF + XML adjuntos
- [ ] Configurable: envio automatico o manual
- [ ] Registro de envios realizados
- [ ] Reenvio disponible desde historial

#### US-POS-040: Cancelacion de CFDI
**Como** comerciante, **quiero** cancelar una factura emitida **para que** pueda corregir errores.

**Criterios de Aceptacion:**
- [ ] Cancelacion con motivos del SAT (01, 02, 03, 04)
- [ ] Sustitucion de CFDI (motivo 01)
- [ ] Confirmacion de cancelacion ante SAT
- [ ] Estado de factura actualizado: cancelada
- [ ] Nota de credito cuando aplique

---

## Timeline

```
Semana 1-2: EP-POS-001 (Motor QR + SPEI) - CRITICO
Semana 2-3: EP-POS-002 (Confirmacion tiempo real) + EP-POS-003 (Catalogo)
Semana 3-4: EP-POS-004 (Corte de caja) + EP-POS-005 (Links de pago)
Semana 3-6: EP-POS-007 (mf-pos frontend) - en paralelo con backend
Semana 4-5: EP-POS-006 (Multi-empleado)
Semana 6-8: EP-POS-008 (Facturacion CFDI)
```

**Equipo**: 2 devs full-stack (1 backend, 1 frontend)
**Costo estimado**: ~$250K MXN

---

## Dependencias entre Epicas

```
EP-POS-001 (Motor QR + SPEI) ← Base de todo
    |
    ├── EP-POS-002 (Confirmacion) → depende de EP-POS-001
    ├── EP-POS-003 (Catalogo) → depende de EP-POS-001
    ├── EP-POS-005 (Links) → depende de EP-POS-001
    ├── EP-POS-006 (Multi-empleado) → depende de EP-POS-001
    |
    ├── EP-POS-004 (Corte de caja) → depende de EP-POS-001, EP-POS-002
    |
    ├── EP-POS-007 (Frontend) → depende de EP-POS-001 a EP-POS-006
    |
    └── EP-POS-008 (CFDI) → depende de EP-POS-002, EP-POS-004
```

**Dependencias externas:**
- EP-SP-001 (Account Core Engine) - motor de cuentas
- EP-SP-002 (Monato SPEI Driver) - recepcion SPEI

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|------------|
| Latencia SPEI > 5 seg | Media | Alto | SSE con retry, notificacion cuando llegue |
| Adopcion lenta en comercios | Media | Alto | Plan Free sin costo, onboarding guiado |
| Competencia con CoDi/DiMo | Baja | Medio | Diferenciar con catalogo + reportes + facturacion |
| Integracion PAC para CFDI | Baja | Medio | Usar Finkok (probado), mockear en tests |
| Fraude con QR clonados | Baja | Alto | QR con expiracion corta + referencia unica |
