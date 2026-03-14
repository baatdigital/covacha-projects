# Programa de Lealtad via WhatsApp (EP-LY-001 a EP-LY-007)

**Fecha**: 2026-03-14
**Product Owner**: SuperPago
**Estado**: Planificacion
**GitHub Issue**: baatdigital/covacha-projects#129
**Score**: 7.5/10 | **Time to Market**: 10 semanas | **Reuso**: 65%

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

Sistema de puntos y recompensas donde los clientes del comercio acumulan y canjean puntos directamente via WhatsApp, sin necesidad de descargar ninguna app. El comercio configura las reglas (1 punto por cada $X gastados) y los clientes interactuan con un bot de WhatsApp para consultar saldo, canjear, y recibir notificaciones proactivas.

**Propuesta de valor**: Programa de lealtad que vive donde el cliente ya esta (WhatsApp), sin fricciones de apps o tarjetas fisicas.

---

## Analisis de Mercado

| Metrica | Valor |
|---------|-------|
| **TAM Mexico** | $7.2B MXN/ano (2M comercios x $300/mes) |
| **SAM** | $1B MXN/ano (300K con WhatsApp Business) |
| **SOM Year 1** | $7.2M MXN/ano (2,000 comercios x $299/mes) |

### Problema de Mercado

- Programas de lealtad requieren apps dedicadas (baja adopcion < 20%)
- PyMEs no pueden costear desarrollo de app propia
- Tarjetas fisicas se pierden o se olvidan
- WhatsApp ya esta en 97% de smartphones en Mexico

### Modelo de Revenue

| Plan | Precio MXN/mes | Clientes activos | Puntos/mes |
|------|---------------|-----------------|-----------|
| Starter | $199 | 500 | 50,000 |
| Pro | $499 | 5,000 | 500,000 |
| Business | $999 | Ilimitados | Ilimitados |

---

## Reutilizacion del Ecosistema

| Componente | Repo Existente | Reutilizacion | Descripcion |
|-----------|---------------|---------------|-------------|
| WhatsApp Bot | covacha-botia | 90% | Dialogo, intenciones, sesiones |
| Motor SPEI/POS | covacha-payment | 80% | Vinculacion con pagos para acumulacion |
| Multi-tenant | covacha-core | 100% | Organizaciones, auth |
| Notificaciones | covacha-notification | 85% | Proactivas, campanas |
| Dashboard base | mf-marketing | 60% | Analytics, segmentacion |
| Shell MF | mf-core | 100% | Module Federation |
| **Nuevo** | covacha-core (loyalty engine) | 20% | Motor de puntos, reglas, niveles |

**Reutilizacion total estimada**: 65%

---

## Mapa de Epicas

| ID | Epica | Complejidad | Semana | Dependencias | Estado |
|----|-------|-------------|--------|--------------|--------|
| EP-LY-001 | Motor de Puntos y Reglas | L | 1-3 | covacha-core | Planificacion |
| EP-LY-002 | Bot WhatsApp de Lealtad | L | 2-4 | EP-LY-001, covacha-botia | Planificacion |
| EP-LY-003 | Acumulacion Automatica (Vinculacion con Pagos) | M | 3-5 | EP-LY-001, covacha-payment | Planificacion |
| EP-LY-004 | Catalogo de Recompensas y Canje | M | 4-6 | EP-LY-001, EP-LY-002 | Planificacion |
| EP-LY-005 | Niveles, Referidos y Gamificacion | M | 5-7 | EP-LY-001 | Planificacion |
| EP-LY-006 | Notificaciones Proactivas y Campanas | M | 6-8 | EP-LY-001, EP-LY-002 | Planificacion |
| EP-LY-007 | Dashboard del Comercio y Metricas | M | 7-10 | EP-LY-001 a EP-LY-006 | Planificacion |

**Totales:**
- 7 epicas
- 35 user stories (US-LY-001 a US-LY-035)
- Estimacion total: ~70 dev-days (10 semanas, 2 devs)

---

## Epicas Detalladas

---

### EP-LY-001: Motor de Puntos y Reglas

**Descripcion:**
Motor backend que gestiona el saldo de puntos de cada cliente, las reglas de acumulacion (cuantos puntos por peso gastado), y la expiracion de puntos. Es el corazon del programa de lealtad. Cada organizacion configura sus propias reglas.

**User Stories:**
- US-LY-001: Modelo de cuenta de puntos por cliente-comercio
- US-LY-002: Reglas de acumulacion configurables (1 punto por $X)
- US-LY-003: Acreditacion y debito de puntos con historial
- US-LY-004: Expiracion de puntos configurable (N dias/meses)
- US-LY-005: Saldo de puntos en tiempo real por cliente

**Criterios de Aceptacion de la Epica:**
- [ ] Modelo: PK=ORG#{org_id}, SK=LOYALTY#{phone} con balance, lifetime_points, tier
- [ ] Reglas configurables por organizacion: puntos_por_peso, minimo_compra, multiplicadores
- [ ] Transacciones de puntos: EARN, REDEEM, EXPIRE, ADJUST con historial
- [ ] Expiracion configurable: X meses desde emision (default: 12 meses)
- [ ] Job de expiracion diario que vence puntos antiguos
- [ ] Saldo consultable en tiempo real via API
- [ ] Limite de puntos por transaccion (anti-fraude)
- [ ] Auditoria completa de movimientos
- [ ] Concurrencia manejada con optimistic locking (version attribute)
- [ ] Tests >= 98%

**Dependencias:** covacha-core (multi-tenant)

**Complejidad:** L (5 user stories)

**Repositorios:** `covacha-core`, `covacha-libs`

---

### EP-LY-002: Bot WhatsApp de Lealtad

**Descripcion:**
Flujos conversacionales en WhatsApp para que el cliente interactue con su programa de lealtad: consultar saldo, ver historial, canjear puntos, referir amigos. Reutiliza el motor de covacha-botia con nuevos intents especificos de lealtad.

**User Stories:**
- US-LY-006: Intent "consultar puntos" ("Cuantos puntos tengo?")
- US-LY-007: Intent "historial" ("Mis ultimos movimientos")
- US-LY-008: Intent "canjear" ("Quiero canjear mis puntos")
- US-LY-009: Intent "referir" ("Quiero invitar a un amigo")
- US-LY-010: Registro de cliente en programa via WhatsApp

**Criterios de Aceptacion de la Epica:**
- [ ] Intent "saldo": responde con puntos disponibles, nivel, y puntos por vencer
- [ ] Intent "historial": ultimos 5-10 movimientos con fecha y concepto
- [ ] Intent "canjear": muestra catalogo de recompensas disponibles
- [ ] Intent "referir": genera link unico de referido
- [ ] Registro: cliente envia su nombre al bot y queda inscrito
- [ ] Onboarding: mensaje de bienvenida con explicacion del programa
- [ ] Fallback: "No entendi, escribe PUNTOS para ver tu saldo"
- [ ] Soporte multimedia: stickers de felicitacion al subir de nivel
- [ ] Sesion de conversacion para flujos multi-paso (canje)
- [ ] Tests >= 98%

**Dependencias:** EP-LY-001, covacha-botia

**Complejidad:** L (5 user stories)

**Repositorios:** `covacha-botia`

---

### EP-LY-003: Acumulacion Automatica (Vinculacion con Pagos)

**Descripcion:**
Integracion que acumula puntos automaticamente cuando un cliente realiza un pago (via POS Virtual, SPEI, o cualquier canal de covacha-payment). El cliente recibe notificacion WhatsApp: "Ganaste X puntos por tu compra de $Y".

**User Stories:**
- US-LY-011: Webhook de pago → acumular puntos automaticamente
- US-LY-012: Vinculacion cliente-telefono con transaccion de pago
- US-LY-013: Notificacion WhatsApp post-compra con puntos ganados
- US-LY-014: Multiplicadores por promocion (doble puntos en X fecha)
- US-LY-015: Puntos bonus por primera compra

**Criterios de Aceptacion de la Epica:**
- [ ] Webhook escucha evento PAYMENT_COMPLETED de covacha-payment
- [ ] Calcula puntos: monto × regla de acumulacion
- [ ] Acredita puntos automaticamente en cuenta del cliente
- [ ] Notificacion WhatsApp: "Ganaste {puntos} puntos por tu compra de ${monto}. Saldo: {total}"
- [ ] Vinculacion: telefono del pagador debe coincidir con programa
- [ ] Multiplicadores temporales: "Hoy doble puntos" configurable por fecha
- [ ] Bonus de primera compra configurable
- [ ] No acumular en compras < monto minimo configurable
- [ ] Idempotencia: misma transaccion no acumula dos veces
- [ ] Tests >= 98%

**Dependencias:** EP-LY-001, covacha-payment (POS Virtual, SPEI)

**Complejidad:** M (5 user stories)

**Repositorios:** `covacha-payment`, `covacha-core`

---

### EP-LY-004: Catalogo de Recompensas y Canje

**Descripcion:**
Catalogo de recompensas que el comercio configura (productos, descuentos, experiencias) y los clientes pueden canjear con sus puntos via WhatsApp. El flujo de canje es conversacional: el bot muestra opciones y el cliente selecciona.

**User Stories:**
- US-LY-016: CRUD de recompensas (nombre, puntos_requeridos, stock, imagen)
- US-LY-017: Flujo de canje via WhatsApp (mostrar opciones → seleccionar → confirmar)
- US-LY-018: Codigo de canje generado para validar en tienda
- US-LY-019: Descuento automatico aplicable en siguiente compra
- US-LY-020: Historial de canjes por cliente

**Criterios de Aceptacion de la Epica:**
- [ ] CRUD de recompensas: nombre, descripcion, puntos_requeridos, stock, imagen, vigencia
- [ ] Tipos: producto fisico, descuento %, descuento fijo, experiencia, producto gratis
- [ ] Flujo WhatsApp: "Tienes {saldo} puntos. Puedes canjear: 1) Cafe gratis (100 pts) 2) 10% descuento (200 pts)"
- [ ] Cliente responde con numero de opcion
- [ ] Validacion de saldo suficiente antes de canjear
- [ ] Codigo de canje unico generado (6 caracteres alfanumerico)
- [ ] Descuento aplicable automaticamente en POS Virtual
- [ ] Control de stock de recompensas
- [ ] Historial de canjes con fecha, recompensa, codigo
- [ ] Tests >= 98%

**Dependencias:** EP-LY-001, EP-LY-002

**Complejidad:** M (5 user stories)

**Repositorios:** `covacha-core`, `covacha-botia`

---

### EP-LY-005: Niveles, Referidos y Gamificacion

**Descripcion:**
Sistema de niveles (Bronce, Plata, Oro) basado en puntos acumulados historicamente, con beneficios diferenciados por nivel. Incluye programa de referidos donde el cliente gana puntos por invitar amigos, y elementos de gamificacion.

**User Stories:**
- US-LY-021: Niveles configurables con umbrales y beneficios
- US-LY-022: Ascenso/descenso automatico de nivel
- US-LY-023: Programa de referidos con link unico
- US-LY-024: Puntos bonus por referido exitoso (ambos ganan)
- US-LY-025: Notificacion de cambio de nivel con felicitacion

**Criterios de Aceptacion de la Epica:**
- [ ] Niveles default: Bronce (0-499 pts), Plata (500-1999), Oro (2000+)
- [ ] Niveles y umbrales configurables por organizacion
- [ ] Beneficios por nivel: multiplicador de puntos, acceso a recompensas exclusivas, descuento base
- [ ] Ascenso automatico al alcanzar umbral de puntos lifetime
- [ ] Descenso por inactividad configurable (default: no descender)
- [ ] Link de referido unico por cliente: ref.superpago.com.mx/XXXXX
- [ ] Referido se registra via link → ambos ganan puntos bonus
- [ ] Mensaje de felicitacion por WhatsApp al subir de nivel
- [ ] Badge/sticker visual de nivel en respuestas del bot
- [ ] Tests >= 98%

**Dependencias:** EP-LY-001

**Complejidad:** M (5 user stories)

**Repositorios:** `covacha-core`, `covacha-botia`

---

### EP-LY-006: Notificaciones Proactivas y Campanas

**Descripcion:**
Sistema de notificaciones que envia mensajes proactivos a los clientes del programa: recordatorio de puntos por vencer, promociones de canje, y campanas de reengagement. Permite al comercio programar campanas segmentadas.

**User Stories:**
- US-LY-026: Notificacion de puntos por vencer ("Tienes 500 puntos que vencen en 7 dias")
- US-LY-027: Campana de promocion de canje ("Hoy doble valor en canjes!")
- US-LY-028: Reengagement de clientes inactivos
- US-LY-029: Notificacion de nueva recompensa disponible
- US-LY-030: Programacion de campanas con segmentacion por nivel/actividad

**Criterios de Aceptacion de la Epica:**
- [ ] Notificacion automatica X dias antes de expiracion de puntos
- [ ] Campanas programables con fecha/hora de envio
- [ ] Segmentacion por: nivel, puntos, ultima compra, inactivos X dias
- [ ] Template de WhatsApp aprobado por Meta
- [ ] Rate limiting para no exceder limites de WhatsApp Business
- [ ] Opt-out de notificaciones proactivas
- [ ] Metricas de campana: enviados, leidos, canjeados
- [ ] Campana de reengagement: clientes sin compra en X dias
- [ ] Preview de campana antes de enviar
- [ ] Tests >= 98%

**Dependencias:** EP-LY-001, EP-LY-002

**Complejidad:** M (5 user stories)

**Repositorios:** `covacha-botia`, `covacha-notification`

---

### EP-LY-007: Dashboard del Comercio y Metricas

**Descripcion:**
Dashboard para que el comercio gestione su programa de lealtad: ver clientes inscritos, puntos emitidos, canjes, ROI del programa, y configurar reglas. Se integra como extension de mf-marketing o como seccion del dashboard existente.

**User Stories:**
- US-LY-031: Dashboard: clientes inscritos, puntos emitidos, canjes realizados
- US-LY-032: Top clientes por puntos y compras
- US-LY-033: ROI del programa: incremento en ventas atribuido a lealtad
- US-LY-034: Configuracion de reglas, niveles y recompensas desde UI
- US-LY-035: Reporte exportable PDF/Excel

**Criterios de Aceptacion de la Epica:**
- [ ] KPIs: clientes inscritos, activos (compra ultimo mes), puntos emitidos, canjeados
- [ ] Top 10 clientes por puntos acumulados y por numero de compras
- [ ] Tasa de canje: puntos canjeados / emitidos
- [ ] ROI: ventas de clientes del programa vs periodo anterior
- [ ] Distribucion de clientes por nivel (pie chart)
- [ ] Configuracion de reglas desde la UI (sin tocar backend)
- [ ] CRUD de recompensas visual
- [ ] Graficas de tendencia: inscripciones, puntos, canjes por semana
- [ ] Export PDF/Excel
- [ ] Tests >= 98%

**Dependencias:** EP-LY-001 a EP-LY-006

**Complejidad:** M (5 user stories)

**Repositorios:** `mf-marketing`

---

## User Stories Detalladas

### EP-LY-001: Motor de Puntos y Reglas

#### US-LY-001: Modelo de cuenta de puntos
**Como** desarrollador, **quiero** un modelo de cuenta de puntos por cliente-comercio **para que** cada cliente tenga su saldo independiente.

**Criterios de Aceptacion:**
- [ ] Modelo: PK=ORG#{org_id}, SK=LOYALTY#{phone}
- [ ] Campos: balance, lifetime_points, tier, last_earn_at, last_redeem_at
- [ ] GSI: busqueda por tier, por balance range
- [ ] Optimistic locking con version attribute
- [ ] Created_at, updated_at

#### US-LY-002: Reglas de acumulacion configurables
**Como** comerciante, **quiero** configurar cuantos puntos gana un cliente por peso gastado **para que** adapte el programa a mi negocio.

**Criterios de Aceptacion:**
- [ ] Regla base: X puntos por cada $Y gastados (ej: 1 punto por $10)
- [ ] Redondeo configurable (arriba, abajo, al mas cercano)
- [ ] Minimo de compra para acumular (ej: solo compras > $50)
- [ ] Maximo de puntos por transaccion
- [ ] Reglas almacenadas por organizacion

#### US-LY-003: Acreditacion y debito de puntos
**Como** sistema, **quiero** registrar cada movimiento de puntos **para que** el saldo sea preciso y auditable.

**Criterios de Aceptacion:**
- [ ] Transaccion: tipo (EARN/REDEEM/EXPIRE/ADJUST), puntos, concepto, timestamp
- [ ] Acreditacion: incrementa balance + lifetime_points
- [ ] Debito: decrementa balance (validar saldo suficiente)
- [ ] Historial completo consultable por API
- [ ] Paginacion para historial largo

#### US-LY-004: Expiracion de puntos
**Como** comerciante, **quiero** que los puntos expiren despues de un tiempo **para que** los clientes se motiven a usarlos.

**Criterios de Aceptacion:**
- [ ] Expiracion configurable: N meses desde emision (default: 12)
- [ ] Job diario que identifica puntos vencidos y los debita
- [ ] Notificacion al cliente X dias antes de expiracion
- [ ] Registro de transaccion tipo EXPIRE con detalle
- [ ] Opcion de "sin expiracion" por organizacion

#### US-LY-005: Consulta de saldo en tiempo real
**Como** cliente, **quiero** consultar mi saldo de puntos **para que** sepa cuantos tengo disponibles.

**Criterios de Aceptacion:**
- [ ] Endpoint `GET /loyalty/{org_id}/balance?phone=+52XXXXXXXXXX`
- [ ] Respuesta: balance, lifetime_points, tier, puntos_por_vencer
- [ ] Tiempo de respuesta < 200ms
- [ ] Cache de 30 segundos para consultas frecuentes
- [ ] Accesible via bot WhatsApp y via API

### EP-LY-002: Bot WhatsApp de Lealtad

#### US-LY-006: Intent "consultar puntos"
**Como** cliente, **quiero** escribir "Cuantos puntos tengo?" por WhatsApp **para que** vea mi saldo inmediatamente.

**Criterios de Aceptacion:**
- [ ] Reconoce variantes: "puntos", "saldo", "cuantos puntos", "mis puntos"
- [ ] Respuesta: "Tienes {balance} puntos (nivel {tier}). {X} puntos vencen el {fecha}."
- [ ] Si no esta registrado: invitar a registrarse
- [ ] Tiempo de respuesta < 3 segundos
- [ ] Funciona en horario 24/7

#### US-LY-007: Intent "historial"
**Como** cliente, **quiero** ver mis ultimos movimientos de puntos **para que** entienda como los gane y gaste.

**Criterios de Aceptacion:**
- [ ] Reconoce: "historial", "movimientos", "ultimas compras"
- [ ] Muestra ultimos 5 movimientos: fecha, tipo, puntos, concepto
- [ ] Formato legible: "+100 pts - Compra en Tienda X (15/Mar)"
- [ ] Opcion de ver mas: "Escribe MAS para ver mas movimientos"
- [ ] Sin movimientos: "Aun no tienes movimientos. Haz tu primera compra!"

#### US-LY-008: Intent "canjear"
**Como** cliente, **quiero** canjear mis puntos por WhatsApp **para que** obtenga mi recompensa sin ir a una app.

**Criterios de Aceptacion:**
- [ ] Reconoce: "canjear", "quiero canjear", "usar puntos", "recompensas"
- [ ] Muestra recompensas disponibles con puntos requeridos
- [ ] Cliente responde con numero de opcion
- [ ] Confirma: "Vas a canjear {recompensa} por {puntos} puntos. Confirma con SI"
- [ ] Genera codigo de canje y lo envia

#### US-LY-009: Intent "referir"
**Como** cliente, **quiero** invitar a un amigo al programa **para que** ambos ganemos puntos.

**Criterios de Aceptacion:**
- [ ] Reconoce: "referir", "invitar", "recomendar"
- [ ] Genera link unico: ref.superpago.com.mx/{codigo}
- [ ] Mensaje: "Comparte este link con tus amigos. Ambos ganan {X} puntos!"
- [ ] Link se puede compartir directamente por WhatsApp
- [ ] Tracking de referidos por cliente

#### US-LY-010: Registro en programa via WhatsApp
**Como** cliente, **quiero** registrarme en el programa de puntos por WhatsApp **para que** comience a acumular.

**Criterios de Aceptacion:**
- [ ] Flujo: cliente envia "PUNTOS" o escanea QR del comercio
- [ ] Bot pide nombre completo
- [ ] Crea cuenta de lealtad con telefono + nombre
- [ ] Mensaje de bienvenida: "Bienvenido {nombre} al programa de {comercio}. Empiezas con {X} puntos!"
- [ ] Puntos de bienvenida configurables por organizacion

### EP-LY-003: Acumulacion Automatica

#### US-LY-011: Webhook de pago acumula puntos
**Como** sistema, **quiero** acumular puntos automaticamente al detectar un pago **para que** el cliente no tenga que hacer nada.

**Criterios de Aceptacion:**
- [ ] Escucha evento PAYMENT_COMPLETED de covacha-payment
- [ ] Calcula puntos segun regla de la organizacion
- [ ] Acredita puntos en cuenta del cliente
- [ ] Idempotencia: misma transaccion no genera puntos dos veces
- [ ] Log de acumulacion con referencia al pago

#### US-LY-012: Vinculacion cliente con pago
**Como** sistema, **quiero** vincular el telefono del pagador con su cuenta de lealtad **para que** se acrediten los puntos correctamente.

**Criterios de Aceptacion:**
- [ ] Match por numero de telefono del pagador
- [ ] Si no esta registrado: invitar a registrarse post-compra
- [ ] Si esta registrado: acumular automaticamente
- [ ] Soporte para pagos POS Virtual y SPEI
- [ ] Fallback: acumulacion manual por el vendedor

#### US-LY-013: Notificacion post-compra
**Como** cliente, **quiero** recibir notificacion de puntos ganados despues de mi compra **para que** sepa que mi programa esta activo.

**Criterios de Aceptacion:**
- [ ] WhatsApp: "Ganaste {puntos} puntos por tu compra de ${monto} en {comercio}. Saldo: {total} puntos."
- [ ] Enviado dentro de 30 segundos post-pago
- [ ] Incluir nivel actual si aplica
- [ ] Solo si cliente esta registrado en programa
- [ ] Configurable: activar/desactivar por organizacion

#### US-LY-014: Multiplicadores por promocion
**Como** comerciante, **quiero** ofrecer doble puntos en fechas especiales **para que** incentive mas compras.

**Criterios de Aceptacion:**
- [ ] Multiplicador configurable: 2x, 3x, 5x puntos
- [ ] Fecha inicio y fin de la promocion
- [ ] Aplicado automaticamente durante el periodo
- [ ] Notificacion a clientes: "Hoy doble puntos en {comercio}!"
- [ ] Visible en respuesta del bot: "Ganaste {puntos} puntos (DOBLE PUNTOS!)"

#### US-LY-015: Puntos bonus por primera compra
**Como** comerciante, **quiero** dar puntos extra en la primera compra **para que** incentive el registro.

**Criterios de Aceptacion:**
- [ ] Bonus configurable (default: 50 puntos)
- [ ] Solo aplica en primera transaccion del cliente
- [ ] Acreditado junto con puntos regulares de la compra
- [ ] Mensaje: "Ganaste {puntos} + {bonus} puntos de BIENVENIDA!"
- [ ] Flag en cuenta: first_purchase_bonus_claimed

### EP-LY-004: Catalogo de Recompensas y Canje

#### US-LY-016: CRUD de recompensas
**Como** comerciante, **quiero** crear recompensas canjeables **para que** mis clientes tengan motivacion para acumular.

**Criterios de Aceptacion:**
- [ ] Endpoint CRUD `/loyalty/{org_id}/rewards`
- [ ] Campos: nombre, descripcion, puntos_requeridos, stock, imagen, tipo, vigencia
- [ ] Tipos: PRODUCT, DISCOUNT_PCT, DISCOUNT_FIXED, FREE_ITEM, EXPERIENCE
- [ ] Stock decrementado automaticamente al canjear
- [ ] Vigencia opcional: fecha inicio y fin

#### US-LY-017: Flujo de canje via WhatsApp
**Como** cliente, **quiero** canjear puntos desde WhatsApp **para que** obtenga mi recompensa facilmente.

**Criterios de Aceptacion:**
- [ ] Bot muestra opciones numeradas con puntos requeridos
- [ ] Cliente responde con numero
- [ ] Validacion: saldo suficiente + stock disponible + vigente
- [ ] Confirmacion: "Confirma con SI para canjear {recompensa}"
- [ ] Post-canje: muestra codigo + nuevo saldo

#### US-LY-018: Codigo de canje
**Como** cliente, **quiero** recibir un codigo de canje **para que** pueda validarlo en la tienda.

**Criterios de Aceptacion:**
- [ ] Codigo alfanumerico de 6 caracteres (ej: AB12CD)
- [ ] Vigencia de 24 horas (configurable)
- [ ] Validacion por el vendedor: endpoint `POST /loyalty/redeem/{code}`
- [ ] Una sola validacion por codigo
- [ ] Estado: GENERATED, VALIDATED, EXPIRED

#### US-LY-019: Descuento automatico en siguiente compra
**Como** cliente, **quiero** que mi descuento canjeado se aplique automaticamente **para que** no necesite recordar un codigo.

**Criterios de Aceptacion:**
- [ ] Descuento vinculado al telefono del cliente
- [ ] Aplicado automaticamente en POS Virtual al detectar pago del mismo telefono
- [ ] Solo aplicable una vez
- [ ] Monto del descuento restado del total de la compra
- [ ] Notificacion: "Se aplico tu descuento de -${monto}. Pagaste ${total}"

#### US-LY-020: Historial de canjes
**Como** cliente, **quiero** ver mis canjes anteriores **para que** tenga registro de mis recompensas.

**Criterios de Aceptacion:**
- [ ] Endpoint `GET /loyalty/{org_id}/redemptions?phone=XXX`
- [ ] Campos: fecha, recompensa, puntos usados, codigo, estado
- [ ] Consultable via bot WhatsApp (intent "mis canjes")
- [ ] Paginacion para historial largo
- [ ] Filtro por fecha y tipo de recompensa

### EP-LY-005: Niveles, Referidos y Gamificacion

#### US-LY-021: Niveles configurables
**Como** comerciante, **quiero** configurar niveles con beneficios **para que** mis mejores clientes se sientan especiales.

**Criterios de Aceptacion:**
- [ ] CRUD de niveles: nombre, umbral_puntos, color, icono, beneficios
- [ ] Beneficios por nivel: multiplicador de puntos, recompensas exclusivas, descuento base
- [ ] Default: Bronce (0), Plata (500), Oro (2000)
- [ ] Maximo 5 niveles por organizacion
- [ ] Descripcion de beneficios visible para el cliente

#### US-LY-022: Ascenso/descenso de nivel
**Como** sistema, **quiero** actualizar el nivel del cliente automaticamente **para que** refleje su actividad.

**Criterios de Aceptacion:**
- [ ] Ascenso: cuando lifetime_points >= umbral del siguiente nivel
- [ ] Evaluacion despues de cada acreditacion de puntos
- [ ] Descenso: configurable (por inactividad X meses, o nunca)
- [ ] Gracia: no descender inmediatamente, dar X dias
- [ ] Historial de cambios de nivel

#### US-LY-023: Programa de referidos
**Como** cliente, **quiero** un link para invitar amigos **para que** ambos ganemos puntos.

**Criterios de Aceptacion:**
- [ ] Link unico por cliente: ref.superpago.com.mx/{org}/{codigo}
- [ ] Link lleva a pagina de registro WhatsApp del programa
- [ ] Tracking: quien refirio a quien
- [ ] Maximo de referidos configurables por organizacion
- [ ] Estadisticas: referidos exitosos por cliente

#### US-LY-024: Puntos bonus por referido
**Como** cliente, **quiero** ganar puntos cuando mi referido hace su primera compra **para que** valga la pena invitar.

**Criterios de Aceptacion:**
- [ ] Puntos para el referidor: configurables (default: 100)
- [ ] Puntos para el referido: configurables (default: 50)
- [ ] Solo al primera compra del referido (no solo registro)
- [ ] Notificacion: "Tu amigo {nombre} hizo su primera compra. Ganaste {puntos} puntos!"
- [ ] Anti-fraude: maximo N referidos por mes

#### US-LY-025: Notificacion de cambio de nivel
**Como** cliente, **quiero** recibir felicitacion al subir de nivel **para que** me sienta valorado.

**Criterios de Aceptacion:**
- [ ] WhatsApp: "Felicidades {nombre}! Subiste a nivel {nivel}! Ahora ganas {multiplicador}x puntos."
- [ ] Detalle de nuevos beneficios desbloqueados
- [ ] Sticker o imagen personalizada por nivel
- [ ] Solo al ascender (no al descender)
- [ ] Descenso comunicado con tacto: "Tu nivel cambio a {nivel}. Compra para recuperar {nivel_anterior}!"

### EP-LY-006: Notificaciones Proactivas y Campanas

#### US-LY-026: Notificacion de puntos por vencer
**Como** cliente, **quiero** que me avisen cuando mis puntos estan por vencer **para que** los use antes.

**Criterios de Aceptacion:**
- [ ] Mensaje X dias antes de vencimiento (default: 7)
- [ ] "Tienes {puntos} puntos que vencen el {fecha}. Canjealos: {recompensas_sugeridas}"
- [ ] Solo enviar si hay puntos por vencer
- [ ] Maximo 1 notificacion por lote de puntos
- [ ] Template aprobado por Meta

#### US-LY-027: Campana de promocion de canje
**Como** comerciante, **quiero** enviar promociones de canje **para que** los clientes usen sus puntos y vuelvan.

**Criterios de Aceptacion:**
- [ ] Crear campana con: audiencia, template, fecha envio
- [ ] Audiencia: clientes con > X puntos, nivel Y, inactivos Z dias
- [ ] Template: "Hoy tus puntos valen doble para canjear!"
- [ ] Programacion de envio
- [ ] Metricas: enviados, canjes realizados post-campana

#### US-LY-028: Reengagement de inactivos
**Como** comerciante, **quiero** reactivar clientes inactivos **para que** vuelvan a comprar.

**Criterios de Aceptacion:**
- [ ] Detectar clientes sin compra en X dias (configurable)
- [ ] Mensaje: "Te extranamos! Tienes {puntos} puntos esperandote en {comercio}"
- [ ] Incluir oferta especial de reengagement
- [ ] Solo 1 mensaje de reengagement por periodo
- [ ] Metricas: reactivados vs total inactivos

#### US-LY-029: Notificacion de nueva recompensa
**Como** cliente, **quiero** saber cuando hay nuevas recompensas **para que** me motive a acumular.

**Criterios de Aceptacion:**
- [ ] Envio automatico al publicar nueva recompensa
- [ ] Solo a clientes activos del programa
- [ ] "Nueva recompensa! {nombre} por solo {puntos} puntos. Canjea escribiendo CANJEAR"
- [ ] Configurable: activar/desactivar por recompensa
- [ ] Imagen de la recompensa incluida si disponible

#### US-LY-030: Programacion de campanas con segmentacion
**Como** comerciante, **quiero** programar campanas segmentadas **para que** cada cliente reciba mensajes relevantes.

**Criterios de Aceptacion:**
- [ ] Builder de campana: nombre, audiencia, template, fecha/hora
- [ ] Segmentos: nivel, rango de puntos, ultima compra, tags
- [ ] Preview de audiencia (cuantos clientes)
- [ ] Envio programado o inmediato
- [ ] Reporte post-campana

### EP-LY-007: Dashboard del Comercio y Metricas

#### US-LY-031: Dashboard principal
**Como** comerciante, **quiero** un dashboard de mi programa de lealtad **para que** sepa como esta funcionando.

**Criterios de Aceptacion:**
- [ ] KPIs: clientes inscritos, activos (ultimo mes), puntos emitidos, canjeados
- [ ] Tasa de canje: puntos canjeados / emitidos (%)
- [ ] Grafica de inscripciones por semana
- [ ] Grafica de puntos emitidos vs canjeados
- [ ] Distribucion por nivel (pie chart)

#### US-LY-032: Top clientes
**Como** comerciante, **quiero** ver mis mejores clientes **para que** pueda darles atencion especial.

**Criterios de Aceptacion:**
- [ ] Top 10 por puntos acumulados (lifetime)
- [ ] Top 10 por numero de compras
- [ ] Top 10 por monto gastado
- [ ] Filtro por periodo (mes, trimestre, ano)
- [ ] Detalle del cliente al hacer click

#### US-LY-033: ROI del programa
**Como** comerciante, **quiero** ver el retorno de inversion del programa **para que** sepa si vale la pena.

**Criterios de Aceptacion:**
- [ ] Comparativo: ventas de miembros vs no miembros
- [ ] Frecuencia de compra: miembros vs no miembros
- [ ] Ticket promedio: miembros vs no miembros
- [ ] Costo del programa (puntos emitidos valorados)
- [ ] ROI: incremento en ventas / costo del programa

#### US-LY-034: Configuracion desde UI
**Como** comerciante, **quiero** configurar mi programa desde el dashboard **para que** no dependa de soporte tecnico.

**Criterios de Aceptacion:**
- [ ] Editar regla de acumulacion (puntos por peso)
- [ ] Editar niveles y umbrales
- [ ] CRUD de recompensas visual
- [ ] Configurar expiracion de puntos
- [ ] Preview de como se ve el bot con la configuracion

#### US-LY-035: Reporte exportable
**Como** comerciante, **quiero** exportar reportes de mi programa **para que** pueda analizarlos offline.

**Criterios de Aceptacion:**
- [ ] Export PDF con graficas y KPIs
- [ ] Export Excel con datos crudos: clientes, puntos, canjes
- [ ] Filtros aplicados reflejados en export
- [ ] Envio automatico mensual por email (opcional)
- [ ] Datos anonimizados para compartir con terceros

---

## Timeline

```
Semana 1-3:  EP-LY-001 (Motor de puntos) - Base
Semana 2-4:  EP-LY-002 (Bot WhatsApp) - En paralelo
Semana 3-5:  EP-LY-003 (Acumulacion automatica)
Semana 4-6:  EP-LY-004 (Catalogo y canje)
Semana 5-7:  EP-LY-005 (Niveles y referidos)
Semana 6-8:  EP-LY-006 (Notificaciones)
Semana 7-10: EP-LY-007 (Dashboard) + QA
```

**Equipo**: 2 devs (1 backend, 1 frontend/bot)
**Costo estimado**: ~$300K MXN

---

## Dependencias entre Epicas

```
EP-LY-001 (Motor de puntos) ← Base de todo
    |
    ├── EP-LY-002 (Bot WhatsApp) → depende de EP-LY-001
    │       |
    │       └── EP-LY-004 (Catalogo/Canje) → depende de EP-LY-001, EP-LY-002
    |
    ├── EP-LY-003 (Acumulacion) → depende de EP-LY-001, covacha-payment
    |
    ├── EP-LY-005 (Niveles/Referidos) → depende de EP-LY-001
    |
    ├── EP-LY-006 (Notificaciones) → depende de EP-LY-001, EP-LY-002
    |
    └── EP-LY-007 (Dashboard) → depende de EP-LY-001 a EP-LY-006
```

**Dependencias externas:**
- covacha-botia: WhatsApp Business API, motor conversacional
- covacha-payment: Eventos de pago para acumulacion automatica
- POS Virtual (EP-POS): Vinculacion de pagos POS con puntos

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|------------|
| Baja inscripcion de clientes | Media | Alto | QR en punto de venta + incentivo de bienvenida |
| Abuso de puntos/referidos | Media | Alto | Limites anti-fraude, validacion de telefono unico |
| Costo de WhatsApp Business por mensaje | Media | Medio | Limitar notificaciones proactivas, incluir en pricing |
| Complejidad de vincular pago con lealtad | Baja | Medio | Usar telefono como ID comun, fallback manual |
| Clientes no entienden el bot | Media | Medio | Flujos guiados, menu de opciones, fallback a humano |
