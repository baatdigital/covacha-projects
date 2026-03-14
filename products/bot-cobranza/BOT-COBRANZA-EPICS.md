# Bot de Cobranza Inteligente via WhatsApp (EP-BC-001 a EP-BC-008)

**Fecha**: 2026-03-14
**Product Owner**: SuperPago
**Estado**: Planificacion
**GitHub Issue**: baatdigital/covacha-projects#130
**Score**: 8.5/10 | **Time to Market**: 8 semanas | **Reuso**: 75%

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

Bot de cobranza automatizado via WhatsApp que usa IA para enviar recordatorios, negociar planes de pago, y facilitar el cobro de facturas vencidas. Tono amigable y respetuoso, cumpliendo con regulacion mexicana de cobranza. Reutiliza 75% de la infraestructura existente de covacha-botia (IA + WhatsApp) y covacha-payment (pagos SPEI).

**Propuesta de valor**: Cobranza con 95%+ tasa de apertura (WhatsApp), negociacion IA 24/7, y link de pago SPEI integrado en el mensaje.

---

## Analisis de Mercado

| Metrica | Valor |
|---------|-------|
| **TAM Mexico** | $50B MXN/ano (mercado cobranza total) |
| **SAM** | $8B MXN/ano (cobranza digital) |
| **SOM Year 1** | $6M MXN/ano (500 empresas x $999/mes) |

### Problema de Mercado

- Cobranza tradicional (call centers): cara y baja contactabilidad (< 20%)
- WhatsApp tiene 95%+ tasa de apertura en Mexico
- No hay solucion de cobranza IA asequible para PyMEs
- Regulacion exige horarios y tono respetuoso

### Modelo de Revenue

| Plan | Precio MXN/mes | Deudores | Mensajes/mes |
|------|---------------|----------|-------------|
| Starter | $499 | 200 | 2,000 |
| Pro | $999 | 2,000 | 20,000 |
| Enterprise | $2,499 | Ilimitados | Ilimitados |

---

## Reutilizacion del Ecosistema

| Componente | Repo Existente | Reutilizacion | Descripcion |
|-----------|---------------|---------------|-------------|
| Motor IA conversacional | covacha-botia | 90% | GPT/Claude para dialogo inteligente |
| WhatsApp Business API | covacha-botia | 100% | Envio/recepcion mensajes, templates |
| Motor SPEI | covacha-payment | 100% | Links de pago, confirmacion |
| Multi-tenant | covacha-core | 100% | Organizaciones, autenticacion |
| Notificaciones programadas | covacha-notification | 80% | Scheduling, colas SQS |
| Dashboard | mf-ia | 60% | Base para dashboard de cobranza |
| **Nuevo** | covacha-botia (flujos) | 30% | Flujos de cobranza especificos |
| **Nuevo** | mf-ia (pantallas) | 40% | Pantallas de gestion de cartera |

**Reutilizacion total estimada**: 75%

---

## Mapa de Epicas

| ID | Epica | Complejidad | Semana | Dependencias | Estado |
|----|-------|-------------|--------|--------------|--------|
| EP-BC-001 | Motor de Campanas de Cobranza | L | 1-2 | covacha-botia | Planificacion |
| EP-BC-002 | Flujos de Escalamiento Gradual | L | 2-3 | EP-BC-001 | Planificacion |
| EP-BC-003 | Negociacion IA de Planes de Pago | L | 3-4 | EP-BC-002 | Planificacion |
| EP-BC-004 | Links de Pago SPEI en Mensajes | M | 2-3 | EP-BC-001 | Planificacion |
| EP-BC-005 | Importacion y Gestion de Cartera | M | 1-2 | - | Planificacion |
| EP-BC-006 | Dashboard de Cobranza y Metricas | M | 4-5 | EP-BC-001 a EP-BC-004 | Planificacion |
| EP-BC-007 | Cumplimiento Legal y Opt-Out | M | 3-4 | EP-BC-001 | Planificacion |
| EP-BC-008 | A/B Testing y Optimizacion | S | 5-6 | EP-BC-001, EP-BC-006 | Planificacion |

**Totales:**
- 8 epicas
- 38 user stories (US-BC-001 a US-BC-038)
- Estimacion total: ~56 dev-days (8 semanas, 2 devs)

---

## Epicas Detalladas

---

### EP-BC-001: Motor de Campanas de Cobranza

**Descripcion:**
Motor que permite configurar y ejecutar campanas de cobranza via WhatsApp. Una campana define: audiencia (cartera vencida), mensaje template, horario de envio, y frecuencia. El motor programa los envios y gestiona el estado de cada contacto (no contactado, contactado, pagado, en negociacion, opt-out).

**User Stories:**
- US-BC-001: Crear campana de cobranza con audiencia y template
- US-BC-002: Programar envio de campana en horario configurable
- US-BC-003: Ejecutar envio masivo con rate limiting
- US-BC-004: Trackear estado de cada contacto en la campana
- US-BC-005: Pausar/reanudar campana en curso

**Criterios de Aceptacion de la Epica:**
- [ ] CRUD de campanas con: nombre, audiencia, template, horario, frecuencia
- [ ] Programacion de envios con SQS delayed messages
- [ ] Rate limiting configurable (mensajes/minuto) para evitar bloqueo de WhatsApp
- [ ] Estado por contacto: NOT_CONTACTED, CONTACTED, REPLIED, PAYING, PAID, OPT_OUT
- [ ] Pausar/reanudar campana sin perder progreso
- [ ] Templates de WhatsApp aprobados por Meta (Business API requirement)
- [ ] Soporte para variables en templates: {nombre}, {monto}, {fecha_vencimiento}
- [ ] Retry automatico para mensajes fallidos (numero no valido, etc.)
- [ ] Logs detallados por cada envio
- [ ] Tests >= 98%

**Dependencias:** covacha-botia (WhatsApp), covacha-notification (scheduling)

**Complejidad:** L (5 user stories)

**Repositorios:** `covacha-botia`, `covacha-notification`

---

### EP-BC-002: Flujos de Escalamiento Gradual

**Descripcion:**
Sistema de escalamiento que incrementa gradualmente la urgencia de los mensajes de cobranza. Inicia con recordatorio amigable, escala a recordatorio urgente, luego a oferta de negociacion, y finalmente a aviso de acciones. Todo dentro de parametros legales y con tono respetuoso.

**User Stories:**
- US-BC-006: Definir flujo de escalamiento con N pasos configurables
- US-BC-007: Recordatorio amigable X dias antes de vencimiento
- US-BC-008: Recordatorio urgente el dia de vencimiento
- US-BC-009: Escalamiento post-vencimiento con oferta de negociacion
- US-BC-010: Pausa automatica al recibir respuesta del deudor

**Criterios de Aceptacion de la Epica:**
- [ ] Flujo configurable con N pasos (default: 5 pasos)
- [ ] Cada paso define: dias relativos al vencimiento, template, canal
- [ ] Paso 1: Recordatorio amigable (-3 dias)
- [ ] Paso 2: Recordatorio dia de vencimiento (dia 0)
- [ ] Paso 3: Seguimiento post-vencimiento (+3 dias)
- [ ] Paso 4: Oferta de negociacion (+7 dias)
- [ ] Paso 5: Aviso final (+15 dias)
- [ ] Pausa automatica del flujo cuando deudor responde
- [ ] Skip automatico cuando se detecta pago
- [ ] Tests >= 98%

**Dependencias:** EP-BC-001 (Motor de campanas)

**Complejidad:** L (5 user stories)

**Repositorios:** `covacha-botia`

---

### EP-BC-003: Negociacion IA de Planes de Pago

**Descripcion:**
Motor de IA que puede negociar planes de pago con deudores dentro de parametros configurados por la empresa. La IA entiende contexto, ofrece opciones, y cierra acuerdos de pago. Usa el modelo conversacional de covacha-botia con prompts especializados en cobranza.

**User Stories:**
- US-BC-011: Configurar parametros de negociacion (descuento max, plazos, montos min)
- US-BC-012: IA propone plan de pago basado en monto y parametros
- US-BC-013: IA negocia contra-ofertas del deudor dentro de limites
- US-BC-014: Generar acuerdo de pago formal con terminos
- US-BC-015: Seguimiento automatico de cumplimiento del plan

**Criterios de Aceptacion de la Epica:**
- [ ] Parametros configurables: descuento maximo (%), plazos (meses), monto minimo por pago
- [ ] IA ofrece hasta 3 opciones de plan de pago
- [ ] IA puede negociar contra-ofertas (dentro de limites configurados)
- [ ] Deteccion de intenciones: pagar, negociar, rechazar, consultar saldo
- [ ] Acuerdo formalizado con: montos, fechas, numero de pagos
- [ ] Link de pago SPEI generado para cada cuota
- [ ] Seguimiento automatico: recordatorio antes de cada cuota
- [ ] Escalamiento a agente humano cuando IA no puede resolver
- [ ] Historial completo de la negociacion almacenado
- [ ] Tests >= 98%

**Dependencias:** EP-BC-002 (escalamiento)

**Complejidad:** L (5 user stories)

**Repositorios:** `covacha-botia`

---

### EP-BC-004: Links de Pago SPEI en Mensajes

**Descripcion:**
Integracion que genera automaticamente links de pago SPEI personalizados dentro de cada mensaje de cobranza. El deudor recibe el link, lo abre, y paga via SPEI. El sistema confirma el pago y actualiza el estado del deudor automaticamente.

**User Stories:**
- US-BC-016: Generar link de pago SPEI personalizado por deudor
- US-BC-017: Incluir link de pago en template de WhatsApp
- US-BC-018: Confirmar pago y actualizar estado del deudor
- US-BC-019: Pago parcial: recalcular saldo pendiente
- US-BC-020: Recibo digital automatico post-pago

**Criterios de Aceptacion de la Epica:**
- [ ] Link de pago SPEI generado con monto exacto del adeudo
- [ ] Link embebido en mensaje de WhatsApp (URL corta)
- [ ] Pagina de pago con datos: acreedor, monto, concepto, QR
- [ ] Confirmacion automatica via webhook SPEI
- [ ] Estado del deudor cambia a PAID automaticamente
- [ ] Soporte pago parcial: recalcula saldo y genera nuevo link
- [ ] Recibo digital enviado por WhatsApp post-pago
- [ ] Notificacion al acreedor cuando se recibe pago
- [ ] Link expira despues de X dias (configurable)
- [ ] Tests >= 98%

**Dependencias:** EP-BC-001 (Motor de campanas)

**Complejidad:** M (5 user stories, reutiliza covacha-payment)

**Repositorios:** `covacha-payment`, `covacha-botia`

---

### EP-BC-005: Importacion y Gestion de Cartera

**Descripcion:**
Sistema para importar la cartera de deudores desde archivos CSV/Excel o via API. La empresa sube su lista de clientes con adeudo y el sistema los prepara para las campanas de cobranza. Incluye validacion de datos, deduplicacion, y enriquecimiento.

**User Stories:**
- US-BC-021: Importar cartera desde CSV/Excel
- US-BC-022: Validacion y limpieza de datos (telefono, monto, referencia)
- US-BC-023: API para integracion con sistema contable externo
- US-BC-024: Deduplicacion de deudores por telefono
- US-BC-025: Vista de cartera con filtros y busqueda

**Criterios de Aceptacion de la Epica:**
- [ ] Import CSV/Excel con columnas: nombre, telefono, monto, referencia, fecha_vencimiento
- [ ] Validacion: formato telefono (+52), monto > 0, fecha valida
- [ ] Reporte de errores por fila con motivo
- [ ] API REST para integracion programatica
- [ ] Deduplicacion por telefono: mergear o reportar duplicados
- [ ] Vista de cartera con filtros: estado, monto, fecha, antiguedad
- [ ] Busqueda por nombre o telefono
- [ ] Export de cartera actualizada
- [ ] Calculo de metricas: cartera total, vencida, promedio de antiguedad
- [ ] Tests >= 98%

**Dependencias:** Ninguna (independiente)

**Complejidad:** M (5 user stories)

**Repositorios:** `covacha-core`

---

### EP-BC-006: Dashboard de Cobranza y Metricas

**Descripcion:**
Dashboard para la empresa acreedora con visibilidad completa de la gestion de cobranza: cartera vencida, contactados, pagados, en negociacion. Incluye metricas de efectividad, reportes de recuperacion, y KPIs del bot.

**User Stories:**
- US-BC-026: Dashboard principal: cartera vencida, contactados, pagados
- US-BC-027: Metricas de efectividad: % recuperacion, tiempo promedio
- US-BC-028: Reporte de actividad del bot: mensajes enviados, respuestas, pagos
- US-BC-029: Pipeline visual: funnel de cobranza por etapa
- US-BC-030: Exportar reportes en PDF/Excel

**Criterios de Aceptacion de la Epica:**
- [ ] Dashboard con KPIs: cartera total, vencida, recuperada, en negociacion
- [ ] Porcentaje de recuperacion por campana
- [ ] Tiempo promedio de recuperacion
- [ ] Funnel visual: No contactado -> Contactado -> En negociacion -> Pagado
- [ ] Grafica de recuperacion por dia/semana/mes
- [ ] Metricas del bot: mensajes enviados, tasa de respuesta, tasa de pago
- [ ] Top deudores por monto
- [ ] Reporte exportable PDF/Excel
- [ ] Filtros por campana, fecha, estado, monto
- [ ] Tests >= 98%

**Dependencias:** EP-BC-001 a EP-BC-004

**Complejidad:** M (5 user stories)

**Repositorios:** `mf-ia`

---

### EP-BC-007: Cumplimiento Legal y Opt-Out

**Descripcion:**
Mecanismos para cumplir con la regulacion mexicana de cobranza (CONDUSEF, Ley de Proteccion de Datos). Incluye opt-out facil, horarios permitidos, registro de consentimiento, y limites de contacto.

**User Stories:**
- US-BC-031: Opt-out: deudor responde "No me contacten" y se detiene
- US-BC-032: Horarios de contacto configurables (L-V 7am-9pm, S 9am-3pm)
- US-BC-033: Limite de contactos por deudor por periodo
- US-BC-034: Registro de consentimiento y evidencia de opt-out

**Criterios de Aceptacion de la Epica:**
- [ ] Opt-out por keyword: "NO", "BAJA", "CANCELAR" detiene contacto inmediato
- [ ] Confirmacion de opt-out enviada al deudor
- [ ] Horarios configurables por empresa (default: regulacion CONDUSEF)
- [ ] No enviar fuera de horario (mensajes encolados para siguiente ventana)
- [ ] Limite de contactos: maximo N mensajes por semana por deudor
- [ ] Registro de consentimiento con timestamp
- [ ] Lista negra de numeros que hicieron opt-out (no reactivables sin consentimiento)
- [ ] Reporte de opt-outs para auditoria
- [ ] Cumplimiento LFPDPPP (aviso de privacidad en primer contacto)
- [ ] Tests >= 98%

**Dependencias:** EP-BC-001

**Complejidad:** M (4 user stories)

**Repositorios:** `covacha-botia`

---

### EP-BC-008: A/B Testing y Optimizacion

**Descripcion:**
Sistema de A/B testing para optimizar mensajes de cobranza. Permite probar diferentes templates, tonos, horarios, y ofertas para maximizar la tasa de recuperacion. Incluye significancia estadistica y recomendaciones automaticas.

**User Stories:**
- US-BC-035: Crear experimento A/B con 2+ variantes de mensaje
- US-BC-036: Distribucion aleatoria de deudores entre variantes
- US-BC-037: Metricas por variante: tasa de apertura, respuesta, pago
- US-BC-038: Recomendacion automatica del ganador con significancia estadistica

**Criterios de Aceptacion de la Epica:**
- [ ] Crear experimento con 2 o mas variantes de template
- [ ] Distribucion aleatoria (50/50 o configurable)
- [ ] Metricas por variante: mensajes enviados, leidos, respondidos, pagados
- [ ] Calculo de significancia estadistica (p-value < 0.05)
- [ ] Recomendacion automatica del ganador
- [ ] Opcion de promover ganador a template principal
- [ ] Historial de experimentos con resultados
- [ ] Filtros por campana y periodo
- [ ] Dashboard de optimizacion con tendencias
- [ ] Tests >= 98%

**Dependencias:** EP-BC-001, EP-BC-006

**Complejidad:** S (4 user stories)

**Repositorios:** `covacha-botia`

---

## User Stories Detalladas

### EP-BC-001: Motor de Campanas de Cobranza

#### US-BC-001: Crear campana de cobranza
**Como** empresa acreedora, **quiero** crear una campana de cobranza **para que** pueda contactar a mis deudores de forma organizada.

**Criterios de Aceptacion:**
- [ ] Endpoint `POST /collections/campaigns` con nombre, audiencia, template, horario
- [ ] Audiencia definida por filtros: monto minimo, dias de vencimiento, estado
- [ ] Template seleccionado de templates aprobados
- [ ] Horario de envio: hora inicio, hora fin, dias de la semana
- [ ] Estado de campana: DRAFT, ACTIVE, PAUSED, COMPLETED

#### US-BC-002: Programar envio de campana
**Como** sistema, **quiero** programar el envio de mensajes **para que** se envien en el horario configurado.

**Criterios de Aceptacion:**
- [ ] SQS delayed messages para programar envios
- [ ] Respetar horario configurado (no enviar fuera de ventana)
- [ ] Calcular hora de envio optima dentro de la ventana
- [ ] Manejar timezone Mexico (CDT/CST)
- [ ] Log de programacion con hora estimada de envio

#### US-BC-003: Ejecutar envio masivo con rate limiting
**Como** sistema, **quiero** enviar mensajes con rate limiting **para que** no se bloquee el numero de WhatsApp.

**Criterios de Aceptacion:**
- [ ] Rate limit configurable (default: 60 mensajes/minuto)
- [ ] Cola SQS con consumer que respeta el rate limit
- [ ] Retry automatico para mensajes fallidos (max 3 reintentos)
- [ ] Reporte de envio: enviados, fallidos, pendientes
- [ ] Pausa automatica si tasa de error > 10%

#### US-BC-004: Trackear estado de cada contacto
**Como** empresa, **quiero** ver el estado de cada deudor contactado **para que** sepa quien ya pago y quien no.

**Criterios de Aceptacion:**
- [ ] Estados: NOT_CONTACTED, CONTACTED, REPLIED, PAYING, PAID, OPT_OUT, FAILED
- [ ] Transiciones automaticas segun eventos (envio, respuesta, pago)
- [ ] Timestamp de ultimo contacto y ultimo cambio de estado
- [ ] Filtro de contactos por estado
- [ ] Historial de cambios de estado por contacto

#### US-BC-005: Pausar/reanudar campana
**Como** empresa, **quiero** pausar una campana **para que** pueda detener temporalmente los envios.

**Criterios de Aceptacion:**
- [ ] Endpoint `PATCH /collections/campaigns/{id}` con action: pause/resume
- [ ] Pausar: detiene envios pendientes, mantiene progreso
- [ ] Reanudar: continua desde donde quedo
- [ ] No re-enviar a contactos ya procesados
- [ ] Log de pausas/reanudaciones con motivo

### EP-BC-002: Flujos de Escalamiento Gradual

#### US-BC-006: Definir flujo de escalamiento
**Como** empresa, **quiero** definir los pasos de escalamiento **para que** la cobranza sea gradual y respetuosa.

**Criterios de Aceptacion:**
- [ ] Endpoint `POST /collections/escalation-flows` con N pasos
- [ ] Cada paso: dias_relativos, template_id, canal, urgencia
- [ ] Flujo default incluido al crear cuenta
- [ ] Validacion de secuencia logica (dias ascendentes)
- [ ] Preview del flujo completo antes de activar

#### US-BC-007: Recordatorio amigable pre-vencimiento
**Como** deudor, **quiero** recibir un recordatorio amigable antes del vencimiento **para que** pueda pagar a tiempo.

**Criterios de Aceptacion:**
- [ ] Mensaje enviado X dias antes del vencimiento (default: -3)
- [ ] Tono amigable: "Hola {nombre}, te recordamos que tu pago de ${monto} vence el {fecha}"
- [ ] Incluye link de pago SPEI
- [ ] No se envia si ya pago
- [ ] Template aprobado por Meta

#### US-BC-008: Recordatorio urgente dia de vencimiento
**Como** deudor, **quiero** recibir un recordatorio el dia de vencimiento **para que** no se me pase.

**Criterios de Aceptacion:**
- [ ] Mensaje el dia de vencimiento
- [ ] Tono mas directo: "Hoy vence tu pago de ${monto}. Paga aqui: {link}"
- [ ] Incluye link de pago SPEI
- [ ] No se envia si ya pago o si pago parcialmente
- [ ] Hora de envio configurable

#### US-BC-009: Escalamiento post-vencimiento
**Como** empresa, **quiero** que el bot escale los mensajes despues del vencimiento **para que** se recupere la cartera.

**Criterios de Aceptacion:**
- [ ] Paso +3 dias: "Tu pago esta vencido. Evita cargos adicionales: {link}"
- [ ] Paso +7 dias: "Podemos ayudarte con un plan de pago. Responde SI"
- [ ] Paso +15 dias: "Ultimo aviso antes de acciones adicionales"
- [ ] Cada paso mas urgente pero siempre respetuoso
- [ ] Respeta opt-out en cualquier momento

#### US-BC-010: Pausa automatica al recibir respuesta
**Como** sistema, **quiero** pausar el escalamiento cuando el deudor responde **para que** la IA pueda conversar.

**Criterios de Aceptacion:**
- [ ] Cualquier respuesta del deudor pausa el flujo automatico
- [ ] La IA toma la conversacion para entender intencion
- [ ] Si intencion es "pagar": enviar link de pago
- [ ] Si intencion es "negociar": iniciar flujo de negociacion (EP-BC-003)
- [ ] Si no hay respuesta en 48h: reanudar flujo automatico

### EP-BC-003: Negociacion IA de Planes de Pago

#### US-BC-011: Configurar parametros de negociacion
**Como** empresa, **quiero** definir hasta donde puede negociar el bot **para que** los acuerdos esten dentro de mis limites.

**Criterios de Aceptacion:**
- [ ] Endpoint `POST /collections/negotiation-params`
- [ ] Parametros: descuento_max (%), plazos_max (meses), monto_min_pago
- [ ] Reglas por antiguedad de deuda (mas vieja = mas flexible)
- [ ] Aprobacion manual requerida si excede limites
- [ ] Templates de planes predefinidos (3, 6, 12 meses)

#### US-BC-012: IA propone plan de pago
**Como** deudor, **quiero** que el bot me ofrezca un plan de pago **para que** pueda cubrir mi adeudo en parcialidades.

**Criterios de Aceptacion:**
- [ ] IA genera hasta 3 opciones de plan basadas en el monto
- [ ] Cada opcion: numero de pagos, monto por pago, descuento, fecha primer pago
- [ ] Formato claro en WhatsApp con numeracion
- [ ] Deudor responde con numero de opcion
- [ ] IA confirma seleccion y genera acuerdo

#### US-BC-013: IA negocia contra-ofertas
**Como** deudor, **quiero** poder negociar con el bot **para que** lleguemos a un acuerdo que pueda cumplir.

**Criterios de Aceptacion:**
- [ ] IA entiende contra-ofertas: "puedo pagar $500 al mes"
- [ ] Evalua si la contra-oferta esta dentro de parametros
- [ ] Si esta dentro: acepta y formaliza
- [ ] Si esta fuera: contra-propone alternativa mas cercana
- [ ] Maximo 3 rondas de negociacion antes de escalar a humano

#### US-BC-014: Generar acuerdo de pago formal
**Como** empresa, **quiero** un acuerdo de pago documentado **para que** tenga respaldo del compromiso.

**Criterios de Aceptacion:**
- [ ] Acuerdo generado con: monto total, cuotas, fechas, descuento
- [ ] Enviado por WhatsApp como PDF
- [ ] Deudor confirma con respuesta "ACEPTO"
- [ ] Registro en base de datos con timestamp de aceptacion
- [ ] Notificacion a la empresa de nuevo acuerdo

#### US-BC-015: Seguimiento de cumplimiento del plan
**Como** empresa, **quiero** seguimiento automatico del plan de pago **para que** se cobre cada cuota a tiempo.

**Criterios de Aceptacion:**
- [ ] Recordatorio automatico 3 dias antes de cada cuota
- [ ] Link de pago SPEI generado para cada cuota
- [ ] Confirmacion automatica via webhook SPEI
- [ ] Si no paga la cuota: re-inicia escalamiento para esa cuota
- [ ] Dashboard con planes activos y cumplimiento

### EP-BC-004: Links de Pago SPEI en Mensajes

#### US-BC-016: Generar link de pago SPEI personalizado
**Como** sistema, **quiero** generar un link de pago SPEI por deudor **para que** pueda pagar con un click.

**Criterios de Aceptacion:**
- [ ] Link unico por deudor-deuda (cobranza.superpago.com.mx/p/XXXXX)
- [ ] Monto pre-cargado (total del adeudo o cuota)
- [ ] Referencia SPEI unica para identificar pago
- [ ] Link vigente hasta fecha configurable
- [ ] Reutiliza motor de links de covacha-payment

#### US-BC-017: Incluir link en template de WhatsApp
**Como** empresa, **quiero** que el link de pago este dentro del mensaje **para que** el deudor pague sin salir de WhatsApp.

**Criterios de Aceptacion:**
- [ ] Variable {link_pago} disponible en templates
- [ ] Link renderizado como URL clickeable
- [ ] Preview del link con Open Graph (monto, empresa)
- [ ] Link diferente por deudor (no compartir links)
- [ ] Template aprobado por Meta con URL variable

#### US-BC-018: Confirmar pago y actualizar estado
**Como** sistema, **quiero** detectar el pago SPEI y actualizar el estado **para que** el deudor no reciba mas mensajes.

**Criterios de Aceptacion:**
- [ ] Webhook SPEI detecta pago por referencia
- [ ] Estado del contacto cambia a PAID
- [ ] Flujo de escalamiento se detiene automaticamente
- [ ] Notificacion a la empresa: "Juan pago $5,000"
- [ ] Recibo enviado al deudor por WhatsApp

#### US-BC-019: Pago parcial
**Como** deudor, **quiero** poder pagar una parte de mi deuda **para que** reduzca mi saldo pendiente.

**Criterios de Aceptacion:**
- [ ] Detectar monto menor al adeudo como pago parcial
- [ ] Recalcular saldo pendiente
- [ ] Generar nuevo link con saldo restante
- [ ] Enviar confirmacion: "Recibimos $X. Tu saldo pendiente es $Y"
- [ ] No marcar como PAID, mantener en PAYING

#### US-BC-020: Recibo digital post-pago
**Como** deudor, **quiero** recibir un comprobante de mi pago **para que** tenga evidencia.

**Criterios de Aceptacion:**
- [ ] Recibo generado automaticamente al confirmar pago
- [ ] Incluye: acreedor, monto, fecha, referencia, saldo restante
- [ ] Enviado por WhatsApp como mensaje con datos
- [ ] PDF descargable desde link
- [ ] Almacenado en S3 por 5 anos (cumplimiento fiscal)

### EP-BC-005: Importacion y Gestion de Cartera

#### US-BC-021: Importar cartera desde CSV/Excel
**Como** empresa, **quiero** subir mi lista de deudores en CSV **para que** el bot comience a cobrar.

**Criterios de Aceptacion:**
- [ ] Endpoint `POST /collections/portfolio/import` con archivo
- [ ] Formatos soportados: CSV, XLSX
- [ ] Columnas: nombre, telefono, monto, referencia, fecha_vencimiento, concepto
- [ ] Template descargable de ejemplo
- [ ] Progreso de importacion visible (procesando X de Y)

#### US-BC-022: Validacion y limpieza de datos
**Como** sistema, **quiero** validar los datos importados **para que** no se envien mensajes a numeros invalidos.

**Criterios de Aceptacion:**
- [ ] Validar formato telefono (10 digitos, prefijo +52)
- [ ] Validar monto > 0 y formato numerico
- [ ] Validar fecha de vencimiento (formato valido, no futura excesiva)
- [ ] Reporte de errores: fila, campo, error
- [ ] Opcion de corregir y re-importar solo las filas con error

#### US-BC-023: API para integracion con sistema contable
**Como** empresa, **quiero** conectar mi sistema contable via API **para que** la cartera se actualice automaticamente.

**Criterios de Aceptacion:**
- [ ] API REST documentada con OpenAPI
- [ ] Endpoints: crear/actualizar/eliminar deudores, consultar estado
- [ ] Webhook para notificar pagos al sistema contable
- [ ] Autenticacion via API key por empresa
- [ ] Rate limiting por API key

#### US-BC-024: Deduplicacion de deudores
**Como** sistema, **quiero** detectar deudores duplicados **para que** no se contacte a la misma persona dos veces.

**Criterios de Aceptacion:**
- [ ] Deteccion por telefono (match exacto)
- [ ] Opcion: mergear (sumar montos) o reportar para decision manual
- [ ] Vista de duplicados detectados con opcion de accion
- [ ] Deduplicacion automatica en importaciones masivas
- [ ] Log de merges realizados

#### US-BC-025: Vista de cartera con filtros
**Como** empresa, **quiero** ver mi cartera completa con filtros **para que** pueda gestionar mis deudores.

**Criterios de Aceptacion:**
- [ ] Tabla paginada con: nombre, telefono, monto, estado, fecha_vencimiento
- [ ] Filtros: estado (todos, pendientes, pagados, opt-out), monto min/max
- [ ] Busqueda por nombre o telefono
- [ ] Ordenar por monto, fecha, estado
- [ ] Export filtrado a CSV

### EP-BC-006: Dashboard de Cobranza y Metricas

#### US-BC-026: Dashboard principal
**Como** empresa, **quiero** un dashboard de cobranza **para que** tenga visibilidad de la gestion.

**Criterios de Aceptacion:**
- [ ] KPIs: cartera total ($), cartera vencida ($), recuperada ($), en negociacion ($)
- [ ] Tasa de recuperacion (%) general y por campana
- [ ] Grafica de recuperacion acumulada por dia
- [ ] Numero de contactos por estado (pie chart)
- [ ] Actualizado en tiempo real

#### US-BC-027: Metricas de efectividad
**Como** empresa, **quiero** ver la efectividad del bot **para que** sepa si esta funcionando.

**Criterios de Aceptacion:**
- [ ] Tasa de contactabilidad (mensajes entregados / enviados)
- [ ] Tasa de respuesta (deudores que respondieron / contactados)
- [ ] Tasa de pago (pagados / contactados)
- [ ] Tiempo promedio de recuperacion (dias desde primer contacto hasta pago)
- [ ] Monto promedio recuperado por deudor

#### US-BC-028: Reporte de actividad del bot
**Como** empresa, **quiero** un reporte detallado de actividad **para que** pueda auditar la gestion.

**Criterios de Aceptacion:**
- [ ] Mensajes enviados por dia/semana/mes
- [ ] Respuestas recibidas con clasificacion (pago, negociacion, queja, opt-out)
- [ ] Planes de pago creados y cumplidos
- [ ] Escalamientos a agente humano
- [ ] Historial exportable

#### US-BC-029: Pipeline visual de cobranza
**Como** empresa, **quiero** ver un funnel de cobranza **para que** entienda donde se pierden los pagos.

**Criterios de Aceptacion:**
- [ ] Funnel: No contactado → Contactado → Respondio → En negociacion → Pagado
- [ ] Porcentaje de conversion entre cada etapa
- [ ] Click en etapa muestra los contactos en esa etapa
- [ ] Comparativo entre campanas
- [ ] Filtros por periodo

#### US-BC-030: Exportar reportes
**Como** empresa, **quiero** exportar los reportes **para que** pueda compartirlos con mi equipo.

**Criterios de Aceptacion:**
- [ ] Exportar dashboard a PDF
- [ ] Exportar datos a Excel
- [ ] Programar envio automatico semanal/mensual por email
- [ ] Incluir graficas en el PDF
- [ ] Filtros aplicados reflejados en el reporte

### EP-BC-007: Cumplimiento Legal y Opt-Out

#### US-BC-031: Opt-out para deudores
**Como** deudor, **quiero** poder detener los mensajes de cobranza **para que** no me contacten mas.

**Criterios de Aceptacion:**
- [ ] Keywords reconocidas: "NO", "BAJA", "CANCELAR", "NO ME CONTACTEN"
- [ ] Deteccion automatica por IA (variantes: "dejen de escribirme", etc.)
- [ ] Respuesta inmediata: "Hemos detenido los mensajes. No te contactaremos mas."
- [ ] Estado cambia a OPT_OUT
- [ ] No se puede reactivar sin consentimiento explicito

#### US-BC-032: Horarios de contacto legales
**Como** sistema, **quiero** respetar horarios legales **para que** la empresa cumpla con la regulacion.

**Criterios de Aceptacion:**
- [ ] Default CONDUSEF: L-V 7am-9pm, S 9am-3pm, D no contacto
- [ ] Configurable por empresa (dentro de limites legales)
- [ ] Mensajes fuera de horario encolados para siguiente ventana
- [ ] Timezone Mexico manejado correctamente
- [ ] Log de intentos fuera de horario (para auditoria)

#### US-BC-033: Limite de contactos por periodo
**Como** empresa, **quiero** limitar cuantas veces contactamos a un deudor **para que** no sea acoso.

**Criterios de Aceptacion:**
- [ ] Maximo configurable: N mensajes por semana (default: 3)
- [ ] Contador por deudor reiniciado semanalmente
- [ ] Mensajes excedentes encolados para siguiente semana
- [ ] Excepcion: respuestas del deudor no cuentan como contacto
- [ ] Reporte de contactos por deudor

#### US-BC-034: Registro de consentimiento
**Como** empresa, **quiero** un registro de consentimiento y opt-out **para que** tenga evidencia legal.

**Criterios de Aceptacion:**
- [ ] Primer mensaje incluye aviso de privacidad resumido + link completo
- [ ] Registro de aceptacion implicita al no hacer opt-out
- [ ] Registro de opt-out con: fecha, hora, keyword, mensaje original
- [ ] Exportable para auditoria CONDUSEF
- [ ] Retencion de registros por 5 anos

### EP-BC-008: A/B Testing y Optimizacion

#### US-BC-035: Crear experimento A/B
**Como** empresa, **quiero** probar diferentes mensajes **para que** use el mas efectivo.

**Criterios de Aceptacion:**
- [ ] Endpoint `POST /collections/experiments`
- [ ] Minimo 2 variantes, maximo 4
- [ ] Cada variante es un template diferente
- [ ] Nombre y descripcion del experimento
- [ ] Duracion configurable

#### US-BC-036: Distribucion aleatoria
**Como** sistema, **quiero** distribuir deudores aleatoriamente **para que** el test sea estadisticamente valido.

**Criterios de Aceptacion:**
- [ ] Distribucion aleatoria uniforme entre variantes
- [ ] Peso configurable por variante (ej: 60/40)
- [ ] Un deudor solo recibe una variante durante el experimento
- [ ] Tamano minimo de muestra sugerido
- [ ] Seed para reproducibilidad

#### US-BC-037: Metricas por variante
**Como** empresa, **quiero** ver como rinde cada variante **para que** elija la mejor.

**Criterios de Aceptacion:**
- [ ] Metricas por variante: enviados, leidos, respondidos, pagados
- [ ] Tasa de conversion por variante
- [ ] Monto recuperado por variante
- [ ] Grafica comparativa
- [ ] Actualizacion en tiempo real

#### US-BC-038: Recomendacion del ganador
**Como** sistema, **quiero** recomendar la variante ganadora **para que** la empresa optimice su cobranza.

**Criterios de Aceptacion:**
- [ ] Calculo de significancia estadistica (chi-squared test)
- [ ] Recomendacion solo si p-value < 0.05
- [ ] Indicador: "Variante A es X% mejor que B (95% confianza)"
- [ ] Opcion de promover ganador como template principal
- [ ] Historial de experimentos completados

---

## Timeline

```
Semana 1-2: EP-BC-005 (Cartera) + EP-BC-001 (Motor campanas) - en paralelo
Semana 2-3: EP-BC-002 (Escalamiento) + EP-BC-004 (Links de pago)
Semana 3-4: EP-BC-003 (Negociacion IA) + EP-BC-007 (Cumplimiento legal)
Semana 4-5: EP-BC-006 (Dashboard)
Semana 5-6: EP-BC-008 (A/B Testing) + QA + ajustes
```

**Equipo**: 2 devs (1 backend/IA, 1 frontend/integraciones)
**Costo estimado**: ~$250K MXN

---

## Dependencias entre Epicas

```
EP-BC-005 (Cartera) ← Independiente, puede iniciar primero
    |
EP-BC-001 (Motor campanas) ← Base del sistema
    |
    ├── EP-BC-002 (Escalamiento) → depende de EP-BC-001
    │       |
    │       └── EP-BC-003 (Negociacion IA) → depende de EP-BC-002
    |
    ├── EP-BC-004 (Links pago) → depende de EP-BC-001
    |
    ├── EP-BC-007 (Legal) → depende de EP-BC-001
    |
    └── EP-BC-006 (Dashboard) → depende de EP-BC-001 a EP-BC-004
            |
            └── EP-BC-008 (A/B Testing) → depende de EP-BC-001, EP-BC-006
```

**Dependencias externas:**
- covacha-botia: Motor IA y WhatsApp Business API
- covacha-payment: Motor SPEI para links de pago
- EP-SP-001: Account Core Engine (multi-tenant)

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|------------|
| Bloqueo de numero WhatsApp por spam | Alta | Critico | Rate limiting estricto, templates aprobados, opt-out facil |
| Regulacion CONDUSEF mas restrictiva | Media | Alto | Disenar con cumplimiento desde el inicio, parametros configurables |
| Baja tasa de recuperacion | Media | Alto | A/B testing, optimizacion continua, escalamiento a humano |
| IA negocia fuera de parametros | Baja | Alto | Limites estrictos en backend, nunca solo en prompt |
| Quejas de deudores | Media | Medio | Tono siempre respetuoso, opt-out facil, horarios legales |
