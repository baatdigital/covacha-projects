# SuperPago - Agentes IA Especializados (EP-SP-031 a EP-SP-040)

**Fecha**: 2026-02-16
**Product Owner**: SuperPago
**Estado**: Planificacion
**Continua desde**: NOTIFICATIONS-EPICS.md (EP-SP-029 a EP-SP-030, US-SP-117 a US-SP-130)
**User Stories**: US-SP-131 en adelante

---

## Tabla de Contenidos

1. [Contexto y Motivacion](#contexto-y-motivacion)
2. [Relacion con Epicas Existentes](#relacion-con-epicas-existentes)
3. [Arquitectura de Agentes IA](#arquitectura-de-agentes-ia)
4. [Mapa de Epicas](#mapa-de-epicas)
5. [Epicas Detalladas](#epicas-detalladas)
6. [User Stories Detalladas](#user-stories-detalladas)
7. [Roadmap](#roadmap)
8. [Grafo de Dependencias](#grafo-de-dependencias)
9. [Riesgos y Mitigaciones](#riesgos-y-mitigaciones)

---

## Contexto y Motivacion

EP-SP-017 (Agente IA WhatsApp Core) y EP-SP-018 (BillPay y Notificaciones) establecen la base conversacional: vinculacion de cuenta, consulta de saldo, transferencias SPEI, pago de servicios basico y notificaciones proactivas. Sin embargo, la plataforma SuperPago tiene **10 dominios funcionales** que requieren agentes especializados con conocimiento profundo de cada vertical. Este documento define esos 10 agentes como extensiones del framework conversacional existente.

| Capacidad | Problema que Resuelve |
|-----------|----------------------|
| **Onboarding Empresarial** | El registro de clientes empresa es manual, lento (dias) y propenso a errores. Un agente guia el proceso paso a paso via WhatsApp |
| **Soporte Financiero** | El 70% de tickets de soporte son preguntas repetitivas sobre saldos, comisiones y estados de transaccion que un agente puede resolver en segundos |
| **Transferencias SPEI Avanzadas** | Usuarios avanzados necesitan programar, recurrir y hacer batch de transferencias sin entrar al portal web |
| **Conciliacion Inteligente** | Discrepancias financieras se detectan tarde y se resuelven manualmente. Un agente proactivo detecta y alerta en tiempo real |
| **Pago de Servicios BillPay** | Pagar 15+ tipos de servicios requiere navegacion compleja. Un agente conversacional simplifica a "Paga mi recibo de luz" |
| **Cash-In/Cash-Out** | Operadores de puntos de pago necesitan asistencia rapida para procesar depositos y retiros sin errores |
| **Prevencion de Fraude** | La deteccion manual de fraude es reactiva. Un agente monitorea en tiempo real y actua preventivamente |
| **Reportes Financieros** | Generar reportes requiere acceso al portal. Un agente los envia bajo demanda por WhatsApp |
| **Subasta de Efectivo** | El marketplace de liquidez necesita notificacion inmediata de matches y ejecucion conversacional |
| **Compliance Regulatorio** | Cumplimiento CNBV/Banxico es manual y riesgoso. Un agente automatiza verificaciones y reportes |

### Relacion con EP-SP-017 y EP-SP-018

Todos los agentes nuevos **heredan** del framework definido en EP-SP-017:

- Sesion conversacional con persistencia de estado (`CONV#`, `SESSION#`)
- Autenticacion via vinculacion WhatsApp-cuenta (US-SP-066)
- Confirmacion 2FA para operaciones sensibles (US-SP-069)
- Rate limiting por usuario (US-SP-070)
- Audit trail completo (US-SP-070)
- NLU con OpenAI GPT-4 + Bedrock fallback

EP-SP-018 aporta la base de BillPay y notificaciones proactivas que EP-SP-035 extiende con cobertura completa de servicios.

---

## Relacion con Epicas Existentes

| Epica Existente | Relacion con Agentes IA |
|-----------------|------------------------|
| EP-SP-001 (Account Core Engine) | EP-SP-031 crea cuentas automaticamente durante onboarding |
| EP-SP-003 (Double-Entry Ledger) | EP-SP-034 consulta el ledger para conciliacion |
| EP-SP-004 (SPEI Out) | EP-SP-033 ejecuta transferencias SPEI avanzadas |
| EP-SP-005 (SPEI In / Webhook) | EP-SP-033 detecta SPEI entrantes para alertas |
| EP-SP-009 (Reconciliacion) | EP-SP-034 extiende la reconciliacion con IA conversacional |
| EP-SP-010 (Limites y Politicas) | EP-SP-037 usa limites como baseline para deteccion de fraude |
| EP-SP-015 (Cash-In/Cash-Out) | EP-SP-036 opera como interfaz conversacional de Cash |
| EP-SP-016 (Subasta de Efectivo) | EP-SP-039 facilita operaciones de subasta via chat |
| EP-SP-017 (Agente IA Core) | Base de todos los agentes: sesion, NLU, 2FA, vinculacion |
| EP-SP-018 (BillPay + Notif) | EP-SP-035 extiende BillPay con cobertura completa |
| EP-SP-021 (Monato BillPay Driver) | EP-SP-035 consume el driver Monato para pagos |
| EP-SP-024 (Onboarding Empresa) | EP-SP-031 automatiza el onboarding via conversacion |
| EP-SP-029 (Notificaciones Backend) | Todos los agentes publican eventos al dispatcher de notificaciones |

---

## Arquitectura de Agentes IA

### Sistema Multi-Agente

```
                         WhatsApp Business API (Meta)
                                    |
                                    v
                          covacha-webhook (receptor)
                                    |
                                    v
                    SQS: sp-whatsapp-inbound (cola de mensajes)
                                    |
                                    v
                    +=======================================+
                    |        covacha-botia (Flask)          |
                    |                                       |
                    |   +-------------------------------+   |
                    |   |      Agent Router / NLU       |   |
                    |   |   (intent classification)     |   |
                    |   +-------------------------------+   |
                    |         |    |    |    |    |         |
                    |         v    v    v    v    v         |
                    |   +----+ +----+ +----+ +----+ +----+ |
                    |   |031 | |032 | |033 | |034 | |035 | |
                    |   +----+ +----+ +----+ +----+ +----+ |
                    |   +----+ +----+ +----+ +----+ +----+ |
                    |   |036 | |037 | |038 | |039 | |040 | |
                    |   +----+ +----+ +----+ +----+ +----+ |
                    |                                       |
                    |   +-------------------------------+   |
                    |   |     Shared Context Manager     |  |
                    |   |  (sesion, estado, preferencias) | |
                    |   +-------------------------------+   |
                    +=======================================+
                         |         |         |         |
                         v         v         v         v
                  covacha-    covacha-   covacha-   covacha-
                  payment    transaction  core     notification
```

### Orquestacion de Agentes

```
Usuario envia mensaje WhatsApp
    |
    v
Agent Router recibe mensaje + contexto de sesion
    |
    +-- 1. Verifica vinculacion WhatsApp-cuenta (SESSION#)
    +-- 2. Clasifica intent con GPT-4 (INTENT#)
    +-- 3. Determina agente especializado
    +-- 4. Verifica permisos del usuario para ese agente
    |
    v
Agente Especializado
    |
    +-- Lee estado de conversacion (CONV#{agent_type}#{conv_id})
    +-- Ejecuta logica de dominio (consulta APIs internas)
    +-- Solicita 2FA si la operacion lo requiere
    +-- Persiste nuevo estado de conversacion
    +-- Genera respuesta en lenguaje natural
    |
    v
Respuesta via WhatsApp Business API
    |
    v
Evento publicado a SQS: sp-notification-events (para audit trail)
```

### Modelo de Datos DynamoDB

```
# Registro de agentes disponibles por organizacion
PK: ORG#{org_id}#AGENTS
SK: AGENT#{agent_type}                 # Ej: AGENT#onboarding, AGENT#fraud
Attrs: enabled, config, limits, created_at

# Conversaciones por agente
PK: CONV#{conversation_id}
SK: MSG#{timestamp}#{msg_id}
Attrs: agent_type, user_id, direction (IN/OUT), content, intent, metadata

# Estado de sesion por agente
PK: SESSION#{user_phone}
SK: AGENT#{agent_type}
Attrs: state_machine_step, context_data, last_activity, ttl

# Intents clasificados (analytics)
PK: INTENT#{date}
SK: #{timestamp}#{intent_id}
Attrs: agent_type, intent_name, confidence, user_id, resolved
GSI-1: PK=INTENT#AGENT#{agent_type}, SK=#{date}#{timestamp}

# Configuracion de agente por organizacion
PK: ORG#{org_id}#AGENT_CONFIG
SK: AGENT#{agent_type}
Attrs: welcome_message, fallback_message, max_retries, escalation_rules, active_hours

# Metricas de agente
PK: AGENT_METRICS#{agent_type}
SK: #{date}
Attrs: total_conversations, resolved, escalated, avg_response_time, satisfaction_score
```

### Canales de Comunicacion

| Canal | Agentes que lo usan | Protocolo |
|-------|--------------------|-----------|
| WhatsApp Business API | Todos (031-040) | Meta Cloud API via covacha-webhook |
| Web Chat (mf-ia) | 031, 032, 033, 035, 038 | WebSocket via covacha-botia |
| API Directa | 034, 037, 040 (sistema) | REST via covacha-botia |
| SQS (eventos async) | 034, 037, 039 (triggers) | SQS consumer en covacha-botia |

---

## Mapa de Epicas

| ID | Epica | Complejidad | Sprint Sugerido | Dependencias |
|----|-------|-------------|-----------------|--------------|
| EP-SP-031 | Agente de Onboarding Empresarial | XL | 17-19 | EP-SP-017, EP-SP-024 |
| EP-SP-032 | Agente de Soporte Financiero (Help Desk IA) | L | 17-18 | EP-SP-017 |
| EP-SP-033 | Agente de Transferencias SPEI Avanzado | XL | 18-20 | EP-SP-017, EP-SP-004 |
| EP-SP-034 | Agente de Conciliacion Inteligente | L | 19-20 | EP-SP-017, EP-SP-009, EP-SP-023 |
| EP-SP-035 | Agente de Pago de Servicios BillPay | XL | 18-20 | EP-SP-018, EP-SP-021 |
| EP-SP-036 | Agente de Cash-In/Cash-Out (Puntos de Pago) | L | 19-20 | EP-SP-017, EP-SP-015 |
| EP-SP-037 | Agente de Alertas y Prevencion de Fraude | XL | 20-22 | EP-SP-017, EP-SP-010, EP-SP-029 |
| EP-SP-038 | Agente de Reportes y Analytics Financieros | L | 20-21 | EP-SP-017, EP-SP-029 |
| EP-SP-039 | Agente de Subasta de Efectivo (Marketplace) | M | 21-22 | EP-SP-017, EP-SP-016 |
| EP-SP-040 | Agente de Compliance y Regulatorio | XL | 21-23 | EP-SP-017, EP-SP-037 |

**Totales:**
- 10 epicas nuevas (EP-SP-031 a EP-SP-040)
- 55 user stories nuevas (US-SP-131 a US-SP-185)
- Estimacion total: ~200 dev-days

---

## Epicas Detalladas

---

### EP-SP-031: Agente de Onboarding Empresarial

**Objetivo:** Automatizar el registro de nuevos clientes empresa via conversacion guiada en WhatsApp, reduciendo el tiempo de onboarding de dias a minutos.

**Descripcion:**
Agente conversacional que guia a nuevos clientes empresa a traves de todo el proceso de registro: recoleccion de datos de la empresa (razon social, RFC, direccion fiscal), documentos KYC/KYB (constancia fiscal, acta constitutiva, INE del representante legal), seleccion de productos a contratar (SPEI, BillPay, Openpay), verificacion automatica de documentos con OCR/IA, y creacion automatica de cuentas una vez aprobado. El flujo es multi-paso con persistencia de estado: el cliente puede abandonar la conversacion y retomar donde se quedo dias despues.

**Criterios de Aceptacion:**
- [ ] Flujo conversacional multi-paso con estado persistente en DynamoDB
- [ ] Recoleccion de datos empresa: razon social, RFC, direccion fiscal, giro comercial
- [ ] Recepcion de documentos via WhatsApp: imagenes/PDF de constancia fiscal, acta constitutiva, INE
- [ ] Verificacion automatica de RFC contra SAT (via API)
- [ ] OCR de documentos con validacion basica (nombre coincide, RFC coincide)
- [ ] Seleccion de productos: SPEI, BillPay, Openpay (o combinacion)
- [ ] Creacion automatica de cuentas al aprobar (consume EP-SP-024)
- [ ] Notificacion al Admin SuperPago para revision final
- [ ] El cliente puede retomar el onboarding dias despues sin perder progreso
- [ ] Seguimiento automatico: si no completa en 48h, envia recordatorio
- [ ] Tests >= 98% con mocks de WhatsApp API y APIs externas (SAT, OCR)

**APIs:**
- `POST /api/v1/agents/onboarding/start` - Inicia flujo de onboarding
- `POST /api/v1/agents/onboarding/document` - Recibe documento para verificacion
- `GET /api/v1/agents/onboarding/status/{session_id}` - Estado del onboarding
- `POST /api/v1/agents/onboarding/approve/{session_id}` - Aprobacion manual por admin
- Consume: `POST /api/v1/onboarding/organization` (EP-SP-024)
- Consume: `POST /api/v1/accounts/batch-create` (EP-SP-001)

**Dependencias:** EP-SP-017 (framework agente), EP-SP-024 (onboarding backend), EP-SP-001 (cuentas)

**Repositorios:** `covacha-botia`, `covacha-core`, `covacha-payment`

**Complejidad:** XL (6 user stories, integracion con SAT, OCR, multi-paso con persistencia)

**Sprint sugerido:** 17-19

---

### EP-SP-032: Agente de Soporte Financiero (Help Desk IA)

**Objetivo:** Resolver el 70% de consultas de soporte de primer nivel automaticamente, reduciendo la carga del equipo de soporte humano.

**Descripcion:**
Agente que responde preguntas frecuentes sobre la plataforma, consulta el historial de transacciones del usuario para dar respuestas contextuales, explica comisiones y limites aplicables a la organizacion del usuario, y escala inteligentemente a soporte humano cuando detecta que no puede resolver. Usa una base de conocimiento (FAQ) administrable por el equipo SuperPago y aprende de las escalaciones para mejorar sus respuestas.

**Criterios de Aceptacion:**
- [ ] Base de conocimiento FAQ administrable (CRUD) almacenada en DynamoDB
- [ ] Busqueda semantica en FAQ usando embeddings (OpenAI)
- [ ] Consulta contextual del historial de transacciones del usuario
- [ ] Explicacion de comisiones: "Cuanto me cobran por SPEI?" responde con la comision de SU organizacion
- [ ] Explicacion de limites: "Cuanto puedo transferir?" responde con sus limites reales
- [ ] Consulta de estado de transaccion: "Que paso con mi transferencia de ayer?" busca y responde
- [ ] Escalacion inteligente a soporte humano con contexto de la conversacion
- [ ] Clasificacion de satisfaccion post-resolucion (emoji rating)
- [ ] Dashboard de metricas: tasa de resolucion, tiempo promedio, temas frecuentes
- [ ] Tests >= 98%

**APIs:**
- `GET /api/v1/agents/support/faq` - Lista FAQ
- `POST /api/v1/agents/support/faq` - Crea entrada FAQ
- `PUT /api/v1/agents/support/faq/{faq_id}` - Actualiza FAQ
- `POST /api/v1/agents/support/escalate` - Escala a humano
- `GET /api/v1/agents/support/metrics` - Metricas de soporte
- Consume: `GET /api/v1/transactions/{user_id}` (covacha-transaction)
- Consume: `GET /api/v1/organizations/{org_id}/policies` (EP-SP-010)

**Dependencias:** EP-SP-017 (framework agente)

**Repositorios:** `covacha-botia`, `covacha-transaction`, `covacha-core`

**Complejidad:** L (5 user stories, busqueda semantica, escalacion)

**Sprint sugerido:** 17-18

---

### EP-SP-033: Agente de Transferencias SPEI Avanzado

**Objetivo:** Permitir operaciones SPEI complejas via conversacion: programadas, recurrentes, masivas y con gestion de beneficiarios.

**Descripcion:**
Extiende la capacidad basica de transferencia SPEI de EP-SP-017 con funcionalidades avanzadas. El usuario puede programar transferencias para una fecha futura, configurar transferencias recurrentes (nomina semanal, renta mensual), enviar transferencias masivas a multiples beneficiarios, gestionar una lista de beneficiarios frecuentes, y recibir validacion inteligente de CLABEs (banco correcto, digito verificador). Todas las operaciones requieren 2FA.

**Criterios de Aceptacion:**
- [ ] Transferencias programadas: "Envia $5,000 a Juan el viernes" -> agenda y ejecuta en fecha
- [ ] Transferencias recurrentes: "Paga la renta cada dia 1 del mes" -> configura recurrencia
- [ ] Transferencias masivas: "Paga nomina" -> lee lista de beneficiarios y montos -> confirma -> ejecuta batch
- [ ] Gestion de beneficiarios: agregar, editar, eliminar favoritos via conversacion
- [ ] Validacion inteligente de CLABE: identifica banco, valida digito verificador, alerta si es sospechosa
- [ ] Confirmacion detallada antes de ejecutar: muestra resumen con banco destino, nombre del beneficiario
- [ ] Cancelacion de transferencias programadas/recurrentes via conversacion
- [ ] Notificacion de transferencia ejecutada (programada/recurrente) cuando se completa
- [ ] Tests >= 98%

**APIs:**
- `POST /api/v1/agents/transfer/schedule` - Programa transferencia futura
- `POST /api/v1/agents/transfer/recurring` - Configura transferencia recurrente
- `POST /api/v1/agents/transfer/batch` - Ejecuta transferencia masiva
- `GET /api/v1/agents/transfer/beneficiaries` - Lista beneficiarios
- `POST /api/v1/agents/transfer/beneficiaries` - Agrega beneficiario
- `DELETE /api/v1/agents/transfer/beneficiaries/{id}` - Elimina beneficiario
- `POST /api/v1/agents/transfer/validate-clabe` - Valida CLABE
- Consume: `POST /api/v1/spei/transfer` (EP-SP-004)

**Dependencias:** EP-SP-017 (framework agente), EP-SP-004 (SPEI Out), EP-SP-005 (SPEI In)

**Repositorios:** `covacha-botia`, `covacha-payment`

**Complejidad:** XL (6 user stories, scheduler, batch processing, beneficiarios)

**Sprint sugerido:** 18-20

---

### EP-SP-034: Agente de Conciliacion Inteligente

**Objetivo:** Detectar discrepancias financieras automaticamente y permitir su resolucion via conversacion con el administrador.

**Descripcion:**
Agente que monitorea la conciliacion diaria del ledger de partida doble, detecta discrepancias entre el saldo contable y el saldo real (Monato, BillPay, Cash), y notifica proactivamente al administrador con el detalle de la discrepancia. El admin puede investigar y resolver la discrepancia directamente via conversacion: "Muestra los movimientos del dia para Boxito" -> "Aplica ajuste de $150 por comision no registrada" -> confirma y ejecuta.

**Criterios de Aceptacion:**
- [ ] Monitoreo automatico de resultados de conciliacion diaria (consume EP-SP-009 y EP-SP-023)
- [ ] Deteccion de discrepancias con clasificacion: monto, fecha, estado, duplicado
- [ ] Notificacion proactiva al admin via WhatsApp cuando hay discrepancia
- [ ] Consulta conversacional de movimientos: por organizacion, por fecha, por tipo
- [ ] Resolucion via conversacion: ajuste manual, reversa, reclasificacion
- [ ] Generacion de reporte de conciliacion en PDF bajo demanda
- [ ] Historial de resoluciones con audit trail
- [ ] Tests >= 98%

**APIs:**
- `GET /api/v1/agents/reconciliation/discrepancies` - Lista discrepancias abiertas
- `GET /api/v1/agents/reconciliation/report/{date}` - Reporte de conciliacion
- `POST /api/v1/agents/reconciliation/resolve/{discrepancy_id}` - Resuelve discrepancia
- `GET /api/v1/agents/reconciliation/history` - Historial de resoluciones
- Consume: `GET /api/v1/reconciliation/results` (EP-SP-009)
- Consume: `GET /api/v1/ledger/entries` (EP-SP-003)

**Dependencias:** EP-SP-017 (framework agente), EP-SP-009 (reconciliacion SPEI), EP-SP-023 (reconciliacion BillPay), EP-SP-003 (ledger)

**Repositorios:** `covacha-botia`, `covacha-payment`, `covacha-transaction`

**Complejidad:** L (5 user stories, integracion con reconciliacion existente)

**Sprint sugerido:** 19-20

---

### EP-SP-035: Agente de Pago de Servicios BillPay

**Objetivo:** Simplificar el pago de 15+ tipos de servicios a una conversacion natural: "Paga mi recibo de luz".

**Descripcion:**
Agente especializado en el pago de servicios domesticos e institucionales. Cubre: CFE (luz), agua (por estado), telefonia fija (Telmex), telefonia movil (Telcel, AT&T, Movistar), gas natural, internet, TV por cable (Izzi, Totalplay, SKY), recargas telefonicas, SAT (impuestos), IMSS (cuotas). Permite consultar adeudos antes de pagar, realizar pagos parciales cuando el proveedor lo permite, generar comprobantes, mantener un historial por servicio, y configurar recordatorios de vencimiento.

**Criterios de Aceptacion:**
- [ ] Catalogo completo de servicios: CFE, agua, Telmex, Telcel, AT&T, gas, internet, TV cable, SAT, IMSS, recargas
- [ ] Consulta de adeudo: "Cuanto debo de luz?" -> consulta via Monato y responde monto
- [ ] Pago completo: "Paga mi recibo de luz" -> confirma referencia -> muestra monto -> 2FA -> paga
- [ ] Pago parcial: "Paga $500 de mi recibo de luz" (si el proveedor lo permite)
- [ ] Recargas telefonicas: "Recarga $200 a mi Telcel" -> confirma numero -> 2FA -> recarga
- [ ] Comprobante digital enviado por WhatsApp (imagen o PDF)
- [ ] Historial de pagos por servicio: "Muestrame mis pagos de luz del ultimo ano"
- [ ] Recordatorios de vencimiento configurables: "Avisame 3 dias antes de que venza mi luz"
- [ ] Servicios favoritos: recuerda referencias y montos frecuentes del usuario
- [ ] Tests >= 98%

**APIs:**
- `GET /api/v1/agents/billpay/services` - Catalogo de servicios
- `POST /api/v1/agents/billpay/query` - Consulta adeudo de un servicio
- `POST /api/v1/agents/billpay/pay` - Ejecuta pago de servicio
- `POST /api/v1/agents/billpay/recharge` - Ejecuta recarga telefonica
- `GET /api/v1/agents/billpay/history/{user_id}` - Historial de pagos
- `POST /api/v1/agents/billpay/reminder` - Configura recordatorio
- `GET /api/v1/agents/billpay/favorites/{user_id}` - Servicios favoritos
- Consume: `POST /api/v1/billpay/query` (EP-SP-021, Monato driver)
- Consume: `POST /api/v1/billpay/pay` (EP-SP-022)

**Dependencias:** EP-SP-018 (interface BillPayProvider), EP-SP-021 (Monato driver), EP-SP-022 (operacion transaccional)

**Repositorios:** `covacha-botia`, `covacha-payment`, `covacha-transaction`

**Complejidad:** XL (6 user stories, 15+ proveedores, recordatorios, favoritos)

**Sprint sugerido:** 18-20

---

### EP-SP-036: Agente de Cash-In/Cash-Out (Puntos de Pago)

**Objetivo:** Asistir a operadores de puntos de pago para procesar depositos y retiros de efectivo de forma rapida y sin errores.

**Descripcion:**
Agente orientado a operadores de puntos de pago (R6). Permite generar codigos QR para depositos, verificar la identidad del cliente antes de un retiro, procesar Cash-In y Cash-Out con confirmacion, realizar cuadre de caja automatico al final del turno, recibir alertas de limites operativos, y generar reportes de turno. El agente entiende el contexto del punto de pago (saldo disponible, limites, horario).

**Criterios de Aceptacion:**
- [ ] Generacion de codigo QR para deposito Cash-In via WhatsApp
- [ ] Verificacion de identidad del cliente: nombre, monto, referencia
- [ ] Procesamiento de Cash-In con confirmacion del operador
- [ ] Procesamiento de Cash-Out con PIN dinamico del cliente
- [ ] Cuadre de caja: "Cuadrar caja" -> calcula diferencia entre efectivo fisico y digital
- [ ] Alertas de limites: notifica cuando el punto se acerca al limite diario
- [ ] Reporte de turno: resumen de operaciones al cierre
- [ ] Tests >= 98%

**APIs:**
- `POST /api/v1/agents/cash/qr-generate` - Genera QR para deposito
- `POST /api/v1/agents/cash/verify-identity` - Verifica identidad para retiro
- `POST /api/v1/agents/cash/cash-in` - Procesa deposito
- `POST /api/v1/agents/cash/cash-out` - Procesa retiro
- `POST /api/v1/agents/cash/reconcile-shift` - Cuadre de caja
- `GET /api/v1/agents/cash/shift-report/{point_id}` - Reporte de turno
- Consume: `POST /api/v1/cash/deposit` (EP-SP-015)
- Consume: `POST /api/v1/cash/withdraw` (EP-SP-015)

**Dependencias:** EP-SP-017 (framework agente), EP-SP-015 (Cash-In/Cash-Out backend)

**Repositorios:** `covacha-botia`, `covacha-payment`

**Complejidad:** L (5 user stories, integracion con Cash existente)

**Sprint sugerido:** 19-20

---

### EP-SP-037: Agente de Alertas y Prevencion de Fraude

**Objetivo:** Monitorear transacciones en tiempo real, detectar patrones sospechosos y actuar preventivamente para proteger las cuentas de los usuarios.

**Descripcion:**
Agente que opera tanto de forma proactiva (monitoreo continuo) como reactiva (verificacion post-alerta). Analiza cada transaccion contra reglas de velocidad (N transacciones en M minutos), montos atipicos (desviacion vs promedio historico), horarios inusuales, geolocalizacion inconsistente, y listas negras de CLABEs/cuentas. Cuando detecta una anomalia puede: notificar al usuario, bloquear preventivamente la operacion, solicitar verificacion adicional al usuario via cuestionario conversacional, o escalar al equipo antifraude.

**Criterios de Aceptacion:**
- [ ] Motor de reglas de fraude configurable por organizacion en DynamoDB
- [ ] Regla de velocidad: N transacciones en M minutos -> alerta
- [ ] Regla de monto atipico: transaccion > X desviaciones del promedio -> alerta
- [ ] Regla de horario: operacion fuera de horario habitual del usuario -> alerta
- [ ] Integracion con listas negras de CLABEs (CNBV, internas)
- [ ] Bloqueo preventivo de operacion con notificacion al usuario
- [ ] Cuestionario de verificacion: "Realizaste una transferencia de $X a CLABE Y?" -> Si/No
- [ ] Desbloqueo automatico si el usuario confirma legitimidad
- [ ] Reporte de intentos de fraude para el Admin SuperPago
- [ ] Dashboard de alertas con metricas: falsos positivos, fraudes evitados, monto protegido
- [ ] Tests >= 98%

**APIs:**
- `POST /api/v1/agents/fraud/evaluate` - Evalua transaccion contra reglas
- `GET /api/v1/agents/fraud/rules/{org_id}` - Reglas de fraude de la org
- `PUT /api/v1/agents/fraud/rules/{org_id}` - Actualiza reglas
- `POST /api/v1/agents/fraud/block/{transaction_id}` - Bloquea transaccion
- `POST /api/v1/agents/fraud/verify/{alert_id}` - Envia verificacion al usuario
- `POST /api/v1/agents/fraud/unblock/{transaction_id}` - Desbloquea tras verificacion
- `GET /api/v1/agents/fraud/alerts` - Lista alertas activas
- `GET /api/v1/agents/fraud/report` - Reporte de fraude
- Consume: `GET /api/v1/organizations/{org_id}/policies` (EP-SP-010)
- Consume: SQS events de covacha-payment (cada transaccion)

**Dependencias:** EP-SP-017 (framework agente), EP-SP-010 (limites y politicas), EP-SP-029 (notificaciones)

**Repositorios:** `covacha-botia`, `covacha-payment`, `covacha-notification`

**Complejidad:** XL (6 user stories, motor de reglas, monitoreo en tiempo real, bloqueo)

**Sprint sugerido:** 20-22

---

### EP-SP-038: Agente de Reportes y Analytics Financieros

**Objetivo:** Generar y enviar reportes financieros bajo demanda o programados directamente por WhatsApp, eliminando la necesidad de acceder al portal web.

**Descripcion:**
Agente que genera reportes financieros en multiples formatos (PDF, CSV, Excel) y los envia por WhatsApp o email. Soporta reportes bajo demanda ("Enviam el estado de cuenta de enero") y programados ("Envia mi resumen de comisiones cada lunes"). Los reportes cubren: estados de cuenta, flujo de caja, comisiones generadas, resumen de transacciones por periodo, y KPIs del negocio. Para WhatsApp, genera versiones simplificadas con datos clave y graficas basicas.

**Criterios de Aceptacion:**
- [ ] Estado de cuenta por periodo: "Estado de cuenta de enero" -> genera PDF y envia
- [ ] Resumen de transacciones: "Cuantas transferencias hice este mes?" -> responde con resumen
- [ ] Reporte de comisiones: "Cuanto he pagado de comisiones?" -> detalle por tipo
- [ ] Flujo de caja: "Como va mi flujo de caja?" -> entradas vs salidas del periodo
- [ ] Exportacion en PDF, CSV y Excel
- [ ] Reportes programados: configurar envio automatico semanal/mensual
- [ ] KPIs via WhatsApp: resumen rapido con numeros clave (texto formateado)
- [ ] Tests >= 98%

**APIs:**
- `POST /api/v1/agents/reports/generate` - Genera reporte bajo demanda
- `GET /api/v1/agents/reports/templates` - Tipos de reporte disponibles
- `POST /api/v1/agents/reports/schedule` - Programa reporte recurrente
- `GET /api/v1/agents/reports/scheduled/{user_id}` - Reportes programados
- `DELETE /api/v1/agents/reports/scheduled/{schedule_id}` - Cancela programacion
- `GET /api/v1/agents/reports/kpis/{org_id}` - KPIs del negocio
- Consume: `GET /api/v1/transactions/summary` (covacha-transaction)
- Consume: `GET /api/v1/ledger/balance` (EP-SP-003)

**Dependencias:** EP-SP-017 (framework agente), EP-SP-029 (notificaciones para envio)

**Repositorios:** `covacha-botia`, `covacha-transaction`, `covacha-payment`

**Complejidad:** L (5 user stories, generacion de reportes, scheduling)

**Sprint sugerido:** 20-21

---

### EP-SP-039: Agente de Subasta de Efectivo (Marketplace)

**Objetivo:** Facilitar las operaciones del mercado de liquidez via conversacion, notificando matches y ejecutando transacciones bilaterales.

**Descripcion:**
Agente que integra el marketplace de subasta de efectivo (EP-SP-016) con WhatsApp. Permite a operadores de puntos publicar ofertas de efectivo, notifica a empresas cuando hay ofertas que coinciden con sus necesidades, facilita la negociacion y confirmacion bilateral via conversacion, ejecuta la transaccion de subasta con confirmacion de ambas partes, y hace seguimiento de la entrega fisica del efectivo. Incluye rating de participantes.

**Criterios de Aceptacion:**
- [ ] Publicar oferta de efectivo via conversacion: "Tengo $50,000 disponibles en sucursal Centro"
- [ ] Notificacion automatica a compradores potenciales cuando hay match
- [ ] Confirmacion bilateral: vendedor y comprador confirman via WhatsApp
- [ ] Ejecucion de transferencia interna al confirmar ambas partes
- [ ] Seguimiento de entrega: "Ya entregue el efectivo" -> confirma y cierra operacion
- [ ] Rating de participantes post-operacion
- [ ] Tests >= 98%

**APIs:**
- `POST /api/v1/agents/auction/offer` - Publica oferta de efectivo
- `GET /api/v1/agents/auction/matches/{offer_id}` - Compradores potenciales
- `POST /api/v1/agents/auction/accept/{offer_id}` - Acepta oferta
- `POST /api/v1/agents/auction/confirm-delivery/{auction_id}` - Confirma entrega
- `POST /api/v1/agents/auction/rate/{auction_id}` - Califica participante
- Consume: `POST /api/v1/auction/offers` (EP-SP-016)
- Consume: `POST /api/v1/transfers/inter-org` (EP-SP-014)

**Dependencias:** EP-SP-017 (framework agente), EP-SP-016 (subasta backend), EP-SP-014 (transferencias inter-org)

**Repositorios:** `covacha-botia`, `covacha-payment`

**Complejidad:** M (5 user stories, integracion con marketplace existente)

**Sprint sugerido:** 21-22

---

### EP-SP-040: Agente de Compliance y Regulatorio

**Objetivo:** Automatizar la verificacion de cumplimiento normativo CNBV/Banxico y la generacion de reportes regulatorios obligatorios.

**Descripcion:**
Agente que monitorea el cumplimiento normativo de la plataforma. Genera automaticamente los reportes regulatorios requeridos por CNBV y Banxico: operaciones relevantes (>$50,000 MXN), operaciones inusuales, operaciones preocupantes. Monitorea umbrales de reporte, alerta sobre vencimiento de documentos KYC de clientes, mantiene un audit trail completo de todas las verificaciones PLD/FT (Prevencion de Lavado de Dinero / Financiamiento al Terrorismo), y permite al Oficial de Compliance consultar y gestionar todo via conversacion.

**Criterios de Aceptacion:**
- [ ] Deteccion automatica de operaciones relevantes (umbral CNBV: >$50,000 MXN o equivalente USD)
- [ ] Clasificacion de operaciones: relevante, inusual, preocupante (segun criterios CNBV)
- [ ] Generacion de reportes regulatorios en formato CNBV/Banxico
- [ ] Monitoreo de umbrales: alerta cuando una cuenta acumula >$200,000 MXN mensual
- [ ] Alertas de vencimiento KYC: "El INE de Empresa X vence en 30 dias"
- [ ] Consulta conversacional: "Cuantas operaciones relevantes hubo este mes?"
- [ ] Audit trail completo de verificaciones PLD/FT
- [ ] Reporte mensual automatico de PLD para el Oficial de Compliance
- [ ] Tests >= 98%

**APIs:**
- `GET /api/v1/agents/compliance/relevant-ops` - Operaciones relevantes del periodo
- `GET /api/v1/agents/compliance/unusual-ops` - Operaciones inusuales
- `POST /api/v1/agents/compliance/generate-report` - Genera reporte regulatorio
- `GET /api/v1/agents/compliance/kyc-expiring` - Documentos KYC por vencer
- `GET /api/v1/agents/compliance/pld-audit` - Audit trail PLD/FT
- `POST /api/v1/agents/compliance/flag-operation/{txn_id}` - Marca operacion como preocupante
- Consume: `GET /api/v1/transactions/by-threshold` (covacha-transaction)
- Consume: `GET /api/v1/organizations/{org_id}/kyc` (covacha-core)

**Dependencias:** EP-SP-017 (framework agente), EP-SP-037 (fraude como input), EP-SP-029 (notificaciones)

**Repositorios:** `covacha-botia`, `covacha-transaction`, `covacha-core`

**Complejidad:** XL (6 user stories, normativa CNBV/Banxico, reportes regulatorios, PLD/FT)

**Sprint sugerido:** 21-23

---

## User Stories Detalladas

---

### EP-SP-031: Agente de Onboarding Empresarial

---

#### US-SP-131: Framework Multi-Agente y Agent Router

**ID:** US-SP-131
**Epica:** EP-SP-031
**Prioridad:** P0
**Story Points:** 13

Como **Sistema** quiero un framework multi-agente con router de intents para clasificar mensajes entrantes y dirigirlos al agente especializado correcto, de modo que cada dominio funcional tenga su propio agente independiente.

**Criterios de Aceptacion:**
- [ ] Clase base `BaseAgent` con interface comun: `handle_message(session, message) -> AgentResponse`
- [ ] `AgentRouter` que clasifica intent del mensaje usando GPT-4 y selecciona agente
- [ ] Registro dinamico de agentes: cada agente se registra con sus intents soportados
- [ ] Modelo DynamoDB `AGENT#` con configuracion por organizacion
- [ ] Fallback a GPT-4 generico si ningun agente tiene confianza > 0.7
- [ ] Contexto compartido entre agentes via `SESSION#{user_phone}`
- [ ] Logging de clasificacion: intent detectado, confianza, agente seleccionado
- [ ] Endpoint `GET /api/v1/agents/registry` lista agentes activos por organizacion

**Notas Tecnicas:**
- Implementar Strategy Pattern: cada agente es una estrategia
- Agent Router usa `INTENT#` para analytics de clasificacion
- GPT-4 como clasificador principal, Bedrock como fallback
- DynamoDB key: `PK: ORG#{org_id}#AGENTS, SK: AGENT#{agent_type}`

**Dependencias:** EP-SP-017 (framework base WhatsApp)

---

#### US-SP-132: Flujo Conversacional Multi-Paso de Onboarding

**ID:** US-SP-132
**Epica:** EP-SP-031
**Prioridad:** P0
**Story Points:** 8

Como **Cliente Empresa** quiero iniciar mi registro via WhatsApp y que el agente me guie paso a paso para que pueda completar el onboarding sin necesidad de llenar formularios web.

**Criterios de Aceptacion:**
- [ ] Flujo de estado: INICIO -> DATOS_EMPRESA -> DOCUMENTOS -> PRODUCTOS -> REVISION -> APROBACION
- [ ] Persistencia de estado en DynamoDB: `PK: SESSION#{phone}, SK: AGENT#onboarding`
- [ ] Paso DATOS_EMPRESA: solicita razon social, RFC, direccion fiscal, giro comercial
- [ ] Validacion en cada paso antes de avanzar (RFC formato valido, campos no vacios)
- [ ] El usuario puede escribir "atras" para regresar al paso anterior
- [ ] El usuario puede abandonar y retomar dias despues sin perder progreso (TTL 30 dias)
- [ ] Timeout de inactividad: si no responde en 24h, envia recordatorio

**Notas Tecnicas:**
- State machine implementada con patron de estados en DynamoDB
- `context_data` almacena datos recolectados hasta el momento
- TTL de 30 dias en el registro de sesion para limpieza automatica

**Dependencias:** US-SP-131 (framework multi-agente)

---

#### US-SP-133: Recepcion y Verificacion de Documentos KYB

**ID:** US-SP-133
**Epica:** EP-SP-031
**Prioridad:** P0
**Story Points:** 8

Como **Cliente Empresa** quiero enviar mis documentos (constancia fiscal, acta constitutiva, INE) via WhatsApp para que sean verificados automaticamente sin tener que ir a una sucursal.

**Criterios de Aceptacion:**
- [ ] Recepcion de imagenes y PDFs via WhatsApp Media API
- [ ] Almacenamiento seguro en S3 con encriptacion: `s3://sp-kyb-docs/{org_id}/{doc_type}_{timestamp}`
- [ ] OCR con AWS Textract para extraer datos clave (RFC, nombre, direccion)
- [ ] Validacion cruzada: RFC extraido por OCR == RFC proporcionado por el usuario
- [ ] Verificacion de RFC contra API del SAT (servicio externo)
- [ ] Si la verificacion falla, solicita reenvio del documento con indicacion del error
- [ ] Registro de documentos verificados en DynamoDB: `PK: ORG#{org_id}#KYB, SK: DOC#{doc_type}`

**Notas Tecnicas:**
- AWS Textract para OCR (no GPT-4 Vision por costos)
- API SAT: verificar RFC activo y datos fiscales
- Documentos requeridos: CSF (Constancia de Situacion Fiscal), Acta Constitutiva, INE del representante

**Dependencias:** US-SP-132 (flujo multi-paso, paso DOCUMENTOS)

---

#### US-SP-134: Seleccion de Productos y Creacion Automatica de Cuentas

**ID:** US-SP-134
**Epica:** EP-SP-031
**Prioridad:** P0
**Story Points:** 8

Como **Cliente Empresa** quiero seleccionar los productos que deseo contratar (SPEI, BillPay, Openpay) para que mis cuentas se creen automaticamente al aprobar mi registro.

**Criterios de Aceptacion:**
- [ ] Menu conversacional de productos disponibles con descripcion breve de cada uno
- [ ] El usuario selecciona 1 o mas productos: "Quiero SPEI y BillPay"
- [ ] Al completar el flujo, envia solicitud a `POST /api/v1/onboarding/organization` (EP-SP-024)
- [ ] Si es aprobacion automatica (criterios basicos cumplidos), crea cuentas inmediatamente
- [ ] Si requiere revision manual, notifica al Admin SuperPago y al cliente "Tu solicitud esta en revision"
- [ ] Al aprobar, se crean cuentas segun el modelo de EP-SP-024 (CONCENTRADORA, COMISIONES, etc.)
- [ ] Confirmacion final al cliente: "Tu cuenta esta activa. Ya puedes usar [productos seleccionados]"

**Notas Tecnicas:**
- Consume API de EP-SP-024 para creacion de organizacion
- Consume API de EP-SP-001 para creacion batch de cuentas
- Productos disponibles configurables por `ORG#{superpago_id}#PRODUCTS_CATALOG`

**Dependencias:** US-SP-133 (documentos verificados), EP-SP-024 (onboarding backend), EP-SP-001 (cuentas)

---

#### US-SP-135: Seguimiento Automatico y Recordatorios de Onboarding

**ID:** US-SP-135
**Epica:** EP-SP-031
**Prioridad:** P1
**Story Points:** 5

Como **Administrador SuperPago** quiero que el agente envie recordatorios automaticos a clientes que no completan su onboarding para maximizar la tasa de conversion.

**Criterios de Aceptacion:**
- [ ] Recordatorio a las 24h si el cliente no avanza al siguiente paso
- [ ] Segundo recordatorio a las 48h con mensaje diferente
- [ ] Tercer y ultimo recordatorio a las 72h indicando que la solicitud expirara
- [ ] Expiracion a los 30 dias si no se completa (limpieza automatica)
- [ ] Dashboard para Admin: solicitudes en curso, abandonadas, completadas, tasa de conversion
- [ ] Endpoint `GET /api/v1/agents/onboarding/pipeline` con metricas del embudo

**Notas Tecnicas:**
- Scheduler via SQS con delay: publica mensaje con delay de 24h/48h/72h
- Metricas almacenadas en `AGENT_METRICS#onboarding` por dia
- Cron Lambda para limpieza de onboardings expirados (TTL DynamoDB)

**Dependencias:** US-SP-132 (flujo multi-paso)

---

#### US-SP-136: Panel de Administracion de Onboarding IA

**ID:** US-SP-136
**Epica:** EP-SP-031
**Prioridad:** P1
**Story Points:** 5

Como **Administrador SuperPago** quiero un panel para revisar y aprobar solicitudes de onboarding pendientes para mantener el control sobre los nuevos clientes que ingresan a la plataforma.

**Criterios de Aceptacion:**
- [ ] Lista de solicitudes pendientes de revision con datos de la empresa y documentos
- [ ] Vista de detalle con documentos subidos (enlaces a S3 presigned URLs)
- [ ] Acciones: Aprobar, Rechazar (con motivo), Solicitar mas informacion
- [ ] Al aprobar desde el panel, se ejecuta la creacion automatica de cuentas
- [ ] Al rechazar, el agente notifica al cliente via WhatsApp con el motivo
- [ ] Filtros: por estado, por fecha, por producto solicitado
- [ ] Endpoint `POST /api/v1/agents/onboarding/approve/{session_id}` para aprobacion

**Notas Tecnicas:**
- Frontend en mf-ia (micro-frontend de IA)
- Presigned URLs de S3 con expiracion de 1h para seguridad
- Webhook a covacha-botia para notificar al cliente automaticamente

**Dependencias:** US-SP-134 (flujo completo de onboarding)

---

### EP-SP-032: Agente de Soporte Financiero (Help Desk IA)

---

#### US-SP-137: Base de Conocimiento FAQ con Busqueda Semantica

**ID:** US-SP-137
**Epica:** EP-SP-032
**Prioridad:** P0
**Story Points:** 8

Como **Administrador SuperPago** quiero administrar una base de conocimiento de preguntas frecuentes para que el agente de soporte pueda resolver consultas automaticamente.

**Criterios de Aceptacion:**
- [ ] CRUD de entradas FAQ en DynamoDB: `PK: FAQ#CATALOG, SK: FAQ#{faq_id}`
- [ ] Cada entrada: pregunta, respuesta, categoria, tags, embedding vector
- [ ] Generacion de embeddings con OpenAI text-embedding-ada-002 al crear/actualizar
- [ ] Busqueda semantica: dado un mensaje del usuario, busca las 3 FAQ mas similares
- [ ] Threshold de similitud: si la mejor FAQ tiene score < 0.75, responde con GPT-4 contextual
- [ ] Categorias predefinidas: Transacciones, Comisiones, Limites, Productos, Seguridad, General
- [ ] Importacion masiva de FAQ desde CSV
- [ ] Endpoint `POST /api/v1/agents/support/faq/search` para busqueda semantica

**Notas Tecnicas:**
- Embeddings almacenados como lista de floats en DynamoDB (max 1536 dims)
- Busqueda por similitud coseno en memoria (FAQ < 1000 entradas, cabe en cache)
- Si FAQ crece > 1000, migrar a OpenSearch o Pinecone

**Dependencias:** EP-SP-017 (framework agente)

---

#### US-SP-138: Consultas Contextuales de Transacciones

**ID:** US-SP-138
**Epica:** EP-SP-032
**Prioridad:** P0
**Story Points:** 8

Como **Usuario Final B2C** quiero preguntar "Que paso con mi transferencia de ayer?" y recibir informacion especifica de MIS transacciones para no tener que buscar en el portal.

**Criterios de Aceptacion:**
- [ ] Consulta de transacciones del usuario por rango de fecha, monto, tipo, estado
- [ ] Lenguaje natural: "mi transferencia de ayer", "el pago de $500", "mis movimientos de la semana"
- [ ] GPT-4 extrae parametros de busqueda del mensaje (fecha, monto, tipo)
- [ ] Consulta `GET /api/v1/transactions/{user_id}` con filtros extraidos
- [ ] Respuesta formateada: fecha, monto, destino, estado, referencia
- [ ] Si hay multiples resultados, muestra lista resumida y permite elegir
- [ ] Si no encuentra resultados, lo indica claramente

**Notas Tecnicas:**
- GPT-4 con function calling para extraer parametros de busqueda
- API de covacha-transaction para consulta de historial
- Limitar resultados a ultimos 30 dias por defecto, ampliable por solicitud

**Dependencias:** US-SP-131 (framework multi-agente)

---

#### US-SP-139: Explicacion de Comisiones y Limites por Organizacion

**ID:** US-SP-139
**Epica:** EP-SP-032
**Prioridad:** P1
**Story Points:** 5

Como **Cliente Empresa** quiero preguntar "Cuanto me cobran por SPEI?" y recibir la comision REAL de mi organizacion para tomar decisiones informadas.

**Criterios de Aceptacion:**
- [ ] Consulta de comisiones de la organizacion del usuario: SPEI, BillPay, Cash, Openpay
- [ ] Consulta de limites: diario, por transaccion, mensual, por producto
- [ ] Respuesta personalizada: "Tu organizacion (Boxito) paga $5.00 + IVA por SPEI Out"
- [ ] Si el usuario pregunta por un producto que no tiene contratado, lo indica
- [ ] Consume `GET /api/v1/organizations/{org_id}/policies` (EP-SP-010)
- [ ] Consume `GET /api/v1/organizations/{org_id}/fees` (covacha-core)

**Notas Tecnicas:**
- Las politicas y comisiones vienen de EP-SP-010
- Cache en sesion por 5 minutos para evitar queries repetidas
- Formateo de montos en formato mexicano: $1,234.56

**Dependencias:** US-SP-131 (framework multi-agente), EP-SP-010 (limites y politicas)

---

#### US-SP-140: Escalacion Inteligente a Soporte Humano

**ID:** US-SP-140
**Epica:** EP-SP-032
**Prioridad:** P0
**Story Points:** 8

Como **Usuario Final B2C** quiero que el agente me conecte con un humano cuando no pueda resolver mi problema para no quedarme sin ayuda.

**Criterios de Aceptacion:**
- [ ] Deteccion automatica de necesidad de escalacion: 3 intentos fallidos, sentimiento negativo, solicitud explicita
- [ ] El usuario puede escribir "hablar con un humano" en cualquier momento
- [ ] Al escalar, se genera ticket con contexto completo: conversacion, datos del usuario, intent original
- [ ] Ticket almacenado en DynamoDB: `PK: SUPPORT_TICKET#{ticket_id}, SK: DETAIL`
- [ ] Notificacion al equipo de soporte via Slack (o canal configurado)
- [ ] El usuario recibe confirmacion: "Te conecto con un agente humano. Ticket #XXX"
- [ ] Endpoint `POST /api/v1/agents/support/escalate` con contexto de la conversacion
- [ ] Metricas de escalacion: tasa, motivos, tiempo de resolucion

**Notas Tecnicas:**
- Analisis de sentimiento con GPT-4 (simple prompt, no modelo separado)
- Ticket incluye transcript completo de la sesion con el agente IA
- Slack webhook para notificacion inmediata al canal #soporte

**Dependencias:** US-SP-137 (FAQ como primer recurso antes de escalar)

---

#### US-SP-141: Dashboard de Metricas de Soporte IA

**ID:** US-SP-141
**Epica:** EP-SP-032
**Prioridad:** P2
**Story Points:** 5

Como **Administrador SuperPago** quiero ver metricas del agente de soporte (tasa de resolucion, temas frecuentes, escalaciones) para optimizar la base de conocimiento y reducir escalaciones.

**Criterios de Aceptacion:**
- [ ] Metricas principales: total consultas, resueltas por IA, escaladas, tasa de resolucion
- [ ] Top 10 preguntas mas frecuentes con intent y frecuencia
- [ ] Top 5 motivos de escalacion
- [ ] Tiempo promedio de resolucion por tipo de consulta
- [ ] Satisfaccion promedio (emoji rating post-resolucion)
- [ ] Filtro por periodo: hoy, semana, mes, personalizado
- [ ] Endpoint `GET /api/v1/agents/support/metrics?from={date}&to={date}`

**Notas Tecnicas:**
- Metricas agregadas en `AGENT_METRICS#support` por dia
- Calculo de metricas via Lambda scheduled (cron diario)
- Frontend en mf-ia

**Dependencias:** US-SP-140 (escalaciones como dato), US-SP-137 (FAQ como dato)

---

### EP-SP-033: Agente de Transferencias SPEI Avanzado

---

#### US-SP-142: Gestion de Beneficiarios Frecuentes

**ID:** US-SP-142
**Epica:** EP-SP-033
**Prioridad:** P0
**Story Points:** 5

Como **Usuario Final B2C** quiero guardar mis beneficiarios frecuentes para no tener que dictar la CLABE completa cada vez que transfiero.

**Criterios de Aceptacion:**
- [ ] Agregar beneficiario via conversacion: "Guarda a Juan, CLABE 072180..." -> confirma -> guarda
- [ ] Listar beneficiarios: "Mis contactos" -> lista con nombre y banco
- [ ] Eliminar beneficiario: "Elimina a Juan de mis contactos" -> confirma -> elimina
- [ ] Modelo DynamoDB: `PK: USER#{user_id}#BENEFICIARIES, SK: BEN#{beneficiary_id}`
- [ ] Attrs: alias, full_name, clabe, bank_name, last_used, transfer_count
- [ ] Maximo 50 beneficiarios por usuario
- [ ] Validacion de CLABE al agregar (digito verificador + banco)

**Notas Tecnicas:**
- Tabla de codigos bancarios para resolver nombre del banco desde CLABE (primeros 3 digitos)
- Ordenar por last_used para mostrar los mas recientes primero

**Dependencias:** US-SP-131 (framework multi-agente)

---

#### US-SP-143: Transferencias Programadas

**ID:** US-SP-143
**Epica:** EP-SP-033
**Prioridad:** P0
**Story Points:** 8

Como **Usuario Final B2C** quiero programar una transferencia para una fecha futura para no tener que recordar hacerla manualmente.

**Criterios de Aceptacion:**
- [ ] Programar via conversacion: "Envia $5,000 a Juan el viernes" -> confirma datos y fecha -> 2FA -> programa
- [ ] Modelo DynamoDB: `PK: USER#{user_id}#SCHEDULED, SK: SCHED#{schedule_id}`
- [ ] Attrs: beneficiary_id, amount, scheduled_date, status (PENDING/EXECUTED/FAILED/CANCELLED), created_at
- [ ] Validacion de saldo al momento de ejecutar (no al programar)
- [ ] Ejecutor Lambda con EventBridge Scheduler: evalua cada minuto transferencias pendientes
- [ ] Notificacion al usuario cuando se ejecuta: "Tu transferencia de $5,000 a Juan fue enviada"
- [ ] Notificacion si falla (saldo insuficiente): "No se pudo enviar. Saldo insuficiente"
- [ ] Cancelar: "Cancela mi transferencia programada para el viernes" -> confirma -> cancela

**Notas Tecnicas:**
- EventBridge Scheduler para ejecucion en fecha exacta
- Validacion de saldo al momento de ejecucion, no al programar
- 2FA obligatoria al programar

**Dependencias:** US-SP-142 (beneficiarios), EP-SP-004 (SPEI Out)

---

#### US-SP-144: Transferencias Recurrentes

**ID:** US-SP-144
**Epica:** EP-SP-033
**Prioridad:** P1
**Story Points:** 8

Como **Cliente Empresa** quiero configurar transferencias recurrentes (nomina semanal, renta mensual) para automatizar pagos repetitivos.

**Criterios de Aceptacion:**
- [ ] Configurar recurrencia: "Paga la renta cada dia 1 del mes" -> confirma datos -> 2FA -> configura
- [ ] Frecuencias: diaria, semanal (dia de la semana), quincenal, mensual (dia del mes)
- [ ] Modelo DynamoDB: `PK: USER#{user_id}#RECURRING, SK: REC#{recurring_id}`
- [ ] Attrs: beneficiary_id, amount, frequency, next_execution, end_date (opcional), status
- [ ] Ejecutor Lambda con cron: evalua recurrencias pendientes cada hora
- [ ] Notificacion al ejecutar cada recurrencia
- [ ] Pausar/reanudar: "Pausa la renta" / "Reanuda la renta"
- [ ] Cancelar: "Cancela el pago recurrente de la renta"
- [ ] Listar activas: "Mis pagos recurrentes" -> lista con proximo pago

**Notas Tecnicas:**
- Cron Lambda cada hora para evaluar recurrencias cuyo next_execution <= ahora
- Al ejecutar, calcular proximo next_execution segun frecuencia
- end_date opcional: si se define, la recurrencia se cancela automaticamente

**Dependencias:** US-SP-143 (programadas como base), US-SP-142 (beneficiarios)

---

#### US-SP-145: Transferencias Masivas (Batch)

**ID:** US-SP-145
**Epica:** EP-SP-033
**Prioridad:** P1
**Story Points:** 13

Como **Cliente Empresa** quiero enviar transferencias masivas a multiples beneficiarios para procesar la nomina o pagos a proveedores en una sola operacion.

**Criterios de Aceptacion:**
- [ ] Iniciar batch via conversacion: "Pagar nomina" -> lista beneficiarios con montos -> confirma -> 2FA -> ejecuta
- [ ] Opcion de subir archivo CSV via WhatsApp: nombre, CLABE, monto, concepto
- [ ] Opcion de usar beneficiarios guardados con montos predefinidos
- [ ] Modelo DynamoDB: `PK: BATCH#{batch_id}, SK: ITEM#{item_id}`
- [ ] Attrs por item: beneficiary_clabe, amount, concept, status (PENDING/SUCCESS/FAILED)
- [ ] Ejecucion asincrona via SQS: cada transferencia individual se encola
- [ ] Resumen post-ejecucion: "Batch completado: 45/50 exitosos, 5 fallidos"
- [ ] Detalle de fallidos con motivo
- [ ] Maximo 100 transferencias por batch
- [ ] Validacion de saldo total antes de iniciar (suma de todos los montos)

**Notas Tecnicas:**
- CSV parsing en covacha-botia, archivo recibido via WhatsApp Media
- SQS para procesamiento asincrono de cada transferencia individual
- DynamoDB TransactWriteItems para validar saldo total atomicamente
- Notificacion parcial cada 10 transferencias ejecutadas

**Dependencias:** US-SP-142 (beneficiarios), EP-SP-004 (SPEI Out), EP-SP-019 (integridad)

---

#### US-SP-146: Validacion Inteligente de CLABEs

**ID:** US-SP-146
**Epica:** EP-SP-033
**Prioridad:** P1
**Story Points:** 5

Como **Usuario Final B2C** quiero que el agente valide automaticamente la CLABE que proporciono y me diga el banco destino para asegurarme de que estoy enviando al lugar correcto.

**Criterios de Aceptacion:**
- [ ] Validacion de digito verificador de CLABE (algoritmo estandar Banxico)
- [ ] Identificacion de banco destino por primeros 3 digitos
- [ ] Respuesta: "CLABE verificada: Banco BBVA, sucursal 1234"
- [ ] Alerta si la CLABE aparece en lista negra interna
- [ ] Sugerencia de correccion si la CLABE tiene 1 digito incorrecto (distancia de Hamming)
- [ ] Historial de CLABEs usadas recientemente para autocompletar
- [ ] Endpoint `POST /api/v1/agents/transfer/validate-clabe`

**Notas Tecnicas:**
- Algoritmo de validacion CLABE: pesos [3,7,1] ciclicos, modulo 10
- Catalogo de bancos: 3 primeros digitos -> nombre del banco (JSON estatico)
- Lista negra: `PK: BLACKLIST#CLABE, SK: #{clabe}` en DynamoDB

**Dependencias:** US-SP-131 (framework multi-agente)

---

#### US-SP-147: Alertas de Transferencias Completadas

**ID:** US-SP-147
**Epica:** EP-SP-033
**Prioridad:** P1
**Story Points:** 5

Como **Usuario Final B2C** quiero recibir una notificacion por WhatsApp cuando mi transferencia programada o recurrente se ejecute para estar tranquilo de que se proceso correctamente.

**Criterios de Aceptacion:**
- [ ] Notificacion de transferencia programada ejecutada: monto, beneficiario, hora, referencia SPEI
- [ ] Notificacion de transferencia recurrente ejecutada: misma info + proxima ejecucion
- [ ] Notificacion de fallo: monto, beneficiario, motivo del fallo, accion sugerida
- [ ] Notificacion de batch completado: resumen (exitosos/fallidos) + detalle de fallidos
- [ ] Publicar evento a SQS: sp-notification-events (EP-SP-029) para audit trail
- [ ] El usuario puede responder "Detalles" para ver mas informacion

**Notas Tecnicas:**
- Eventos publicados al dispatcher de notificaciones (EP-SP-029)
- Template de notificacion especifico por tipo: SCHEDULED_EXECUTED, RECURRING_EXECUTED, BATCH_COMPLETED
- Integrar con `NOTIF_TEMPLATE` de EP-SP-029

**Dependencias:** US-SP-143 (programadas), US-SP-144 (recurrentes), US-SP-145 (batch), EP-SP-029 (notificaciones)

---

### EP-SP-034: Agente de Conciliacion Inteligente

---

#### US-SP-148: Monitor de Resultados de Conciliacion

**ID:** US-SP-148
**Epica:** EP-SP-034
**Prioridad:** P0
**Story Points:** 8

Como **Sistema** quiero monitorear automaticamente los resultados de la conciliacion diaria para detectar discrepancias y notificar al administrador en tiempo real.

**Criterios de Aceptacion:**
- [ ] Consumer de SQS que escucha eventos RECONCILIATION_OK y DISCREPANCY_DETECTED (EP-SP-009)
- [ ] Consumer para eventos de conciliacion BillPay (EP-SP-023)
- [ ] Clasificacion de discrepancia: MONTO_DIFERENTE, TRANSACCION_FALTANTE, DUPLICADA, ESTADO_INCORRECTO
- [ ] Almacenamiento: `PK: DISC#{discrepancy_id}, SK: DETAIL`
- [ ] Attrs: type, org_id, original_txn_id, expected_amount, actual_amount, detected_at, status (OPEN/INVESTIGATING/RESOLVED)
- [ ] Notificacion inmediata al Admin SuperPago via WhatsApp cuando hay discrepancia
- [ ] Formato de notificacion: tipo, org afectada, monto de la discrepancia, transaccion involucrada

**Notas Tecnicas:**
- SQS consumer en covacha-botia que escucha la cola de eventos de reconciliacion
- Threshold configurable: solo alertar si discrepancia > $100 MXN (evitar ruido)
- Agregar GSI: `PK: DISC#ORG#{org_id}, SK: #{detected_at}` para consulta por org

**Dependencias:** EP-SP-009 (reconciliacion SPEI), EP-SP-023 (reconciliacion BillPay)

---

#### US-SP-149: Consulta Conversacional de Movimientos para Conciliacion

**ID:** US-SP-149
**Epica:** EP-SP-034
**Prioridad:** P0
**Story Points:** 8

Como **Administrador SuperPago** quiero consultar movimientos via WhatsApp para investigar discrepancias sin tener que abrir el portal web.

**Criterios de Aceptacion:**
- [ ] "Muestra movimientos de Boxito del 15 de febrero" -> lista movimientos filtrados
- [ ] "Detalle de transaccion TXN#abc123" -> muestra asientos de partida doble completos
- [ ] "Compara saldo contable vs saldo Monato de Boxito" -> muestra ambos y la diferencia
- [ ] Filtros: por organizacion, por fecha, por tipo (SPEI, BillPay, Cash), por estado
- [ ] Paginacion: "Siguiente pagina" para ver mas resultados
- [ ] Consume `GET /api/v1/ledger/entries` (EP-SP-003) y `GET /api/v1/transactions` (covacha-transaction)

**Notas Tecnicas:**
- GPT-4 con function calling para parsear parametros de consulta del lenguaje natural
- Paginacion con cursor-based: devolver max 10 movimientos por pagina
- Cache de resultados en sesion para paginacion fluida

**Dependencias:** US-SP-148 (deteccion de discrepancias), EP-SP-003 (ledger)

---

#### US-SP-150: Resolucion de Discrepancias via Conversacion

**ID:** US-SP-150
**Epica:** EP-SP-034
**Prioridad:** P0
**Story Points:** 8

Como **Administrador SuperPago** quiero resolver discrepancias via conversacion con el agente para agilizar el proceso de conciliacion.

**Criterios de Aceptacion:**
- [ ] "Aplica ajuste de $150 en cuenta de Boxito por comision no registrada" -> confirma -> 2FA -> ejecuta
- [ ] Tipos de resolucion: AJUSTE_MANUAL, REVERSA, RECLASIFICACION, MARCAR_CORRECTO
- [ ] Cada resolucion genera asiento de partida doble correspondiente (EP-SP-003)
- [ ] 2FA obligatoria para toda resolucion que afecte saldos
- [ ] Registro de resolucion: quien resolvio, tipo, monto de ajuste, justificacion
- [ ] Actualiza status de discrepancia a RESOLVED con referencia a la resolucion
- [ ] Endpoint `POST /api/v1/agents/reconciliation/resolve/{discrepancy_id}`

**Notas Tecnicas:**
- Asientos de ajuste con categoria CONCILIATION_ADJUSTMENT en el ledger
- Idempotency key obligatoria para evitar doble resolucion
- Solo Admin SuperPago (Tier 1) puede resolver discrepancias

**Dependencias:** US-SP-149 (consulta de movimientos), EP-SP-003 (ledger)

---

#### US-SP-151: Reporte de Conciliacion en PDF

**ID:** US-SP-151
**Epica:** EP-SP-034
**Prioridad:** P1
**Story Points:** 5

Como **Administrador SuperPago** quiero generar un reporte de conciliacion en PDF y recibirlo por WhatsApp para tener un registro formal de la conciliacion diaria.

**Criterios de Aceptacion:**
- [ ] "Genera reporte de conciliacion de ayer" -> genera PDF -> envia por WhatsApp
- [ ] Contenido del PDF: fecha, organizaciones conciliadas, totales, discrepancias encontradas, resoluciones aplicadas
- [ ] Formato profesional con logo SuperPago y firma digital
- [ ] Almacenamiento del PDF en S3: `s3://sp-reports/reconciliation/{date}_{org_id}.pdf`
- [ ] Historial de reportes generados consultable via conversacion
- [ ] Endpoint `POST /api/v1/agents/reconciliation/report/{date}`

**Notas Tecnicas:**
- Generacion PDF con ReportLab o WeasyPrint (Python)
- Envio via WhatsApp Media API (documento PDF)
- Tamano maximo del PDF: 16MB (limite WhatsApp)

**Dependencias:** US-SP-148 (datos de conciliacion), US-SP-150 (resoluciones)

---

#### US-SP-152: Historial de Resoluciones y Audit Trail

**ID:** US-SP-152
**Epica:** EP-SP-034
**Prioridad:** P1
**Story Points:** 5

Como **Administrador SuperPago** quiero consultar el historial de resoluciones de discrepancias para auditoria y trazabilidad.

**Criterios de Aceptacion:**
- [ ] "Muestrame las resoluciones del ultimo mes" -> lista con fecha, tipo, monto, quien resolvio
- [ ] Filtros: por organizacion, por tipo de resolucion, por fecha
- [ ] Detalle de cada resolucion: discrepancia original, asiento de ajuste, justificacion
- [ ] Modelo DynamoDB: `PK: RESOLUTION#{resolution_id}, SK: DETAIL`
- [ ] GSI: `PK: RESOLUTION#ORG#{org_id}, SK: #{resolved_at}`
- [ ] Exportar historial en CSV: "Exporta resoluciones de enero"

**Notas Tecnicas:**
- GSI para consulta eficiente por organizacion y fecha
- CSV generado en memoria y enviado como documento via WhatsApp
- Maximo 500 registros por exportacion

**Dependencias:** US-SP-150 (resoluciones registradas)

---

### EP-SP-035: Agente de Pago de Servicios BillPay

---

#### US-SP-153: Catalogo de Servicios y Consulta de Adeudos

**ID:** US-SP-153
**Epica:** EP-SP-035
**Prioridad:** P0
**Story Points:** 8

Como **Usuario Final B2C** quiero consultar cuanto debo de luz, agua u otro servicio via WhatsApp para saber el monto exacto antes de pagar.

**Criterios de Aceptacion:**

- [ ] Catalogo de servicios en DynamoDB: `PK: BILLPAY_CATALOG, SK: SVC#{service_id}`
- [ ] Servicios soportados: CFE, agua (por estado), Telmex, Telcel, AT&T, Movistar, gas natural, Izzi, Totalplay, SKY, SAT, IMSS
- [ ] Consulta de adeudo: "Cuanto debo de luz?" -> pide numero de servicio -> consulta via Monato -> responde monto
- [ ] Respuesta con desglose: monto total, fecha limite, periodo facturado
- [ ] Si el servicio no tiene adeudo, lo indica: "Tu recibo de luz esta al corriente"
- [ ] Si el numero de servicio es invalido, solicita reingreso
- [ ] Consume `POST /api/v1/billpay/query` (EP-SP-021, Monato driver)

**Notas Tecnicas:**

- Catalogo actualizado manualmente por Admin, no dinamico
- Monato como unico provider inicial; Strategy Pattern para futuros providers
- Cache de consulta de adeudo: 30 minutos (evitar queries repetidas al provider)

**Dependencias:** US-SP-131 (framework multi-agente), EP-SP-021 (Monato driver)

---

#### US-SP-154: Pago Completo y Parcial de Servicios

**ID:** US-SP-154
**Epica:** EP-SP-035
**Prioridad:** P0
**Story Points:** 8

Como **Usuario Final B2C** quiero pagar mi recibo de luz completo o un monto parcial via WhatsApp para cumplir con mis obligaciones sin ir a una tienda.

**Criterios de Aceptacion:**

- [ ] Pago completo: "Paga mi recibo de luz" -> confirma referencia y monto -> 2FA -> ejecuta pago
- [ ] Pago parcial: "Paga $500 de mi recibo de luz" -> confirma monto parcial -> 2FA -> ejecuta
- [ ] Validacion de saldo suficiente antes de ejecutar
- [ ] Si el proveedor no acepta pago parcial, lo indica y ofrece pago completo
- [ ] Comprobante digital generado y enviado por WhatsApp (imagen con datos del pago)
- [ ] Asiento contable BILL_PAY generado en ledger (EP-SP-022)
- [ ] Consume `POST /api/v1/billpay/pay` (EP-SP-022)

**Notas Tecnicas:**

- Flujo: query adeudo -> confirma monto -> 2FA -> pay -> receipt
- Idempotency key obligatoria para evitar doble pago
- Comprobante generado como imagen PNG con datos clave (mas facil de ver en WhatsApp que PDF)

**Dependencias:** US-SP-153 (consulta de adeudo), EP-SP-022 (operacion transaccional BillPay)

---

#### US-SP-155: Recargas Telefonicas

**ID:** US-SP-155
**Epica:** EP-SP-035
**Prioridad:** P1
**Story Points:** 5

Como **Usuario Final B2C** quiero recargar tiempo aire a mi celular o al de alguien mas via WhatsApp para tener saldo telefonico sin salir de casa.

**Criterios de Aceptacion:**

- [ ] "Recarga $200 a mi Telcel" -> confirma numero telefonico -> 2FA -> ejecuta recarga
- [ ] "Recarga $100 al 5512345678" -> confirma operador y numero -> 2FA -> ejecuta
- [ ] Deteccion automatica de operador por prefijo telefonico (Telcel, AT&T, Movistar)
- [ ] Montos predefinidos por operador: $20, $50, $100, $200, $300, $500
- [ ] Comprobante de recarga enviado por WhatsApp
- [ ] Consume API de recargas del provider Monato

**Notas Tecnicas:**

- Prefijos de operador: Telcel (33, 55, 81...), AT&T (Unefon/Iusacell), Movistar
- Montos fijos definidos por el provider, no customizables
- Recarga se trata como pago BillPay con service_type=RECHARGE

**Dependencias:** US-SP-153 (catalogo de servicios), EP-SP-021 (Monato driver)

---

#### US-SP-156: Historial de Pagos por Servicio

**ID:** US-SP-156
**Epica:** EP-SP-035
**Prioridad:** P1
**Story Points:** 5

Como **Usuario Final B2C** quiero consultar mi historial de pagos de un servicio especifico para verificar que he pagado correctamente.

**Criterios de Aceptacion:**

- [ ] "Mis pagos de luz" -> lista ultimos 12 pagos de CFE con fecha, monto, referencia
- [ ] "Mis pagos de este mes" -> todos los pagos de servicios del mes actual
- [ ] Filtros: por servicio, por periodo, por monto
- [ ] Paginacion: "Mas pagos" para ver pagos anteriores
- [ ] Modelo DynamoDB: consulta via GSI en covacha-transaction con filtro service_type
- [ ] Exportar historial: "Exporta mis pagos de luz del 2025" -> genera CSV

**Notas Tecnicas:**

- Consulta al historial de transacciones de covacha-transaction con filtro tipo BILL_PAY
- GSI por usuario + service_type + fecha para consultas eficientes
- CSV enviado como documento via WhatsApp Media API

**Dependencias:** US-SP-154 (pagos registrados en historial)

---

#### US-SP-157: Recordatorios de Vencimiento

**ID:** US-SP-157
**Epica:** EP-SP-035
**Prioridad:** P1
**Story Points:** 8

Como **Usuario Final B2C** quiero recibir recordatorios antes de que venzan mis recibos para no pagar recargos por pago tardio.

**Criterios de Aceptacion:**

- [ ] "Avisame 3 dias antes de que venza mi luz" -> configura recordatorio
- [ ] Modelo DynamoDB: `PK: USER#{user_id}#REMINDERS, SK: REM#{reminder_id}`
- [ ] Attrs: service_type, service_reference, days_before, next_check_date, enabled
- [ ] Scheduler Lambda que verifica vencimientos diariamente
- [ ] El scheduler consulta adeudo via Monato y compara con fecha limite
- [ ] Notificacion: "Tu recibo de luz vence en 3 dias. Adeudo: $1,234. Quieres pagar ahora?"
- [ ] Si el usuario responde "Si", inicia flujo de pago directamente
- [ ] Gestionar recordatorios: "Mis recordatorios", "Cancela recordatorio de luz"

**Notas Tecnicas:**

- Lambda con cron diario a las 8am hora Mexico (UTC-6)
- Consulta de adeudo al provider para obtener fecha de vencimiento actualizada
- Si el servicio ya fue pagado, no envia recordatorio

**Dependencias:** US-SP-153 (consulta de adeudo), EP-SP-029 (notificaciones)

---

#### US-SP-158: Servicios Favoritos y Referencias Guardadas

**ID:** US-SP-158
**Epica:** EP-SP-035
**Prioridad:** P2
**Story Points:** 5

Como **Usuario Final B2C** quiero que el agente recuerde mis numeros de servicio y servicios frecuentes para pagar mas rapido sin repetir datos.

**Criterios de Aceptacion:**

- [ ] Al pagar un servicio por primera vez, preguntar "Quieres guardar este servicio como favorito?"
- [ ] Modelo DynamoDB: `PK: USER#{user_id}#FAVORITES, SK: FAV#{favorite_id}`
- [ ] Attrs: service_type, service_reference, alias (ej: "Mi luz"), last_paid, times_paid
- [ ] "Paga mi luz" -> si tiene favorito de CFE, usa la referencia guardada automaticamente
- [ ] Listar favoritos: "Mis servicios" -> lista con alias, tipo y ultima fecha de pago
- [ ] Eliminar favorito: "Elimina mi servicio de agua"
- [ ] Maximo 20 servicios favoritos por usuario

**Notas Tecnicas:**

- Alias opcional; si no se proporciona, se usa el nombre del servicio + ultimos 4 digitos referencia
- Ordenar por times_paid descendente para mostrar los mas usados primero

**Dependencias:** US-SP-154 (pago de servicios como trigger para guardar)

---

### EP-SP-036: Agente de Cash-In/Cash-Out (Puntos de Pago)

---

#### US-SP-159: Generacion de QR para Deposito Cash-In

**ID:** US-SP-159
**Epica:** EP-SP-036
**Prioridad:** P0
**Story Points:** 5

Como **Operador Punto de Pago** quiero generar un codigo QR de deposito para que el cliente lo escanee y se acredite su deposito automaticamente.

**Criterios de Aceptacion:**

- [ ] "Generar QR deposito $5,000" -> genera QR con monto y referencia unica
- [ ] QR contiene: point_id, amount, reference, expiration (15 min)
- [ ] QR enviado como imagen via WhatsApp al operador
- [ ] El operador muestra el QR al cliente para que lo escanee con la app
- [ ] Al escanear, se inicia el flujo Cash-In (EP-SP-015)
- [ ] QR expira en 15 minutos por seguridad
- [ ] Endpoint `POST /api/v1/agents/cash/qr-generate`

**Notas Tecnicas:**

- Generacion QR con libreria qrcode (Python)
- Referencia unica: UUID + timestamp truncado
- QR almacenado temporalmente en S3 con TTL de 15 min
- El contenido del QR es una URL: `https://app.superpago.com.mx/cash-in/{reference}`

**Dependencias:** US-SP-131 (framework multi-agente), EP-SP-015 (Cash-In backend)

---

#### US-SP-160: Procesamiento de Cash-In y Cash-Out via Conversacion

**ID:** US-SP-160
**Epica:** EP-SP-036
**Prioridad:** P0
**Story Points:** 8

Como **Operador Punto de Pago** quiero procesar depositos y retiros via WhatsApp para atender clientes de forma rapida sin usar un portal web.

**Criterios de Aceptacion:**

- [ ] Cash-In: "Deposito $3,000 para cliente 5512345678" -> verifica cliente -> confirma -> procesa
- [ ] Cash-Out: "Retiro $2,000 para cliente 5512345678" -> verifica PIN del cliente -> confirma -> procesa
- [ ] Verificacion de identidad del cliente: nombre completo y ultimos 4 digitos de telefono
- [ ] PIN dinamico para Cash-Out: el cliente recibe PIN por WhatsApp, el operador lo solicita
- [ ] Comprobante de operacion enviado al operador y al cliente
- [ ] Consume `POST /api/v1/cash/deposit` y `POST /api/v1/cash/withdraw` (EP-SP-015)
- [ ] Validacion de limites por operacion y por dia del punto de pago

**Notas Tecnicas:**

- PIN dinamico: 6 digitos, valido por 10 minutos, generado via SQS event
- El operador esta vinculado a un punto de pago especifico (`POINT#{point_id}`)
- Validar que el operador tiene sesion activa en su turno

**Dependencias:** US-SP-159 (QR como flujo alternativo), EP-SP-015 (Cash-In/Cash-Out backend)

---

#### US-SP-161: Cuadre de Caja Automatico

**ID:** US-SP-161
**Epica:** EP-SP-036
**Prioridad:** P0
**Story Points:** 8

Como **Operador Punto de Pago** quiero realizar el cuadre de caja al final de mi turno via WhatsApp para verificar que mi efectivo fisico cuadra con las operaciones registradas.

**Criterios de Aceptacion:**

- [ ] "Cuadrar caja" -> solicita monto de efectivo fisico en caja -> calcula diferencia con saldo digital
- [ ] Muestra resumen: depositos del turno, retiros del turno, saldo digital esperado, diferencia
- [ ] Si cuadra (diferencia = $0): "Caja cuadrada. Turno cerrado correctamente"
- [ ] Si no cuadra: "Diferencia de $X. Deseas registrar la diferencia?" -> registra con justificacion
- [ ] Cierre de turno: marca turno como cerrado en DynamoDB
- [ ] Modelo: `PK: POINT#{point_id}#SHIFT, SK: SHIFT#{shift_id}`
- [ ] Endpoint `POST /api/v1/agents/cash/reconcile-shift`

**Notas Tecnicas:**

- Saldo digital esperado = saldo inicial del turno + cash-ins - cash-outs
- Diferencias se registran con categoria SHIFT_VARIANCE en el ledger
- Alerta al admin si la diferencia supera umbral configurable ($500 por defecto)

**Dependencias:** US-SP-160 (operaciones Cash registradas), EP-SP-015 (Cash backend)

---

#### US-SP-162: Alertas de Limites Operativos del Punto

**ID:** US-SP-162
**Epica:** EP-SP-036
**Prioridad:** P1
**Story Points:** 5

Como **Operador Punto de Pago** quiero recibir alertas cuando me acerco a los limites operativos de mi punto para evitar rechazos de operaciones.

**Criterios de Aceptacion:**

- [ ] Alerta al 80% del limite diario de Cash-In: "Has procesado $80,000 de $100,000 limite diario"
- [ ] Alerta al 80% del limite diario de Cash-Out
- [ ] Alerta al alcanzar el 100%: "Limite diario alcanzado. No puedes procesar mas depositos hoy"
- [ ] Alerta de efectivo bajo: si el saldo digital del punto baja de umbral minimo
- [ ] Limites configurables por punto en `ORG#{org_id}#POINT#{point_id}#LIMITS`
- [ ] Consume EP-SP-010 (limites y politicas) para obtener limites del punto

**Notas Tecnicas:**

- Verificacion de limites en cada operacion Cash-In/Cash-Out
- Alertas via WhatsApp al operador del punto activo
- Los limites vienen de EP-SP-010 con override por punto de pago

**Dependencias:** US-SP-160 (operaciones que acumulan contra limites), EP-SP-010 (limites)

---

#### US-SP-163: Reporte de Turno

**ID:** US-SP-163
**Epica:** EP-SP-036
**Prioridad:** P1
**Story Points:** 5

Como **Operador Punto de Pago** quiero recibir un resumen de mi turno al cerrarlo para tener un registro de todas las operaciones realizadas.

**Criterios de Aceptacion:**

- [ ] Al cerrar turno (cuadre de caja), generar reporte automatico
- [ ] Contenido: hora inicio, hora cierre, total Cash-In (cantidad y monto), total Cash-Out (cantidad y monto), comisiones generadas, diferencia de caja
- [ ] Envio por WhatsApp como mensaje formateado (texto)
- [ ] Opcion de PDF: "Quiero el reporte en PDF" -> genera y envia
- [ ] Historial de turnos: "Mis turnos de esta semana" -> lista resumida
- [ ] Endpoint `GET /api/v1/agents/cash/shift-report/{point_id}`

**Notas Tecnicas:**

- Reporte generado al momento del cuadre de caja (US-SP-161)
- PDF con ReportLab si se solicita
- Historial consultable por operador y por punto de pago

**Dependencias:** US-SP-161 (cuadre de caja como trigger)

---

### EP-SP-037: Agente de Alertas y Prevencion de Fraude

---

#### US-SP-164: Motor de Reglas de Fraude Configurable

**ID:** US-SP-164
**Epica:** EP-SP-037
**Prioridad:** P0
**Story Points:** 13

Como **Administrador SuperPago** quiero configurar reglas de deteccion de fraude por organizacion para adaptar la sensibilidad a cada tipo de negocio.

**Criterios de Aceptacion:**

- [ ] Modelo de reglas en DynamoDB: `PK: ORG#{org_id}#FRAUD_RULES, SK: RULE#{rule_id}`
- [ ] Tipos de regla: VELOCITY (N ops en M minutos), AMOUNT_THRESHOLD (monto > X), TIME_WINDOW (fuera de horario), BLACKLIST (CLABE en lista negra)
- [ ] Cada regla tiene: nombre, tipo, parametros, severidad (LOW/MEDIUM/HIGH/CRITICAL), accion (ALERT/BLOCK/VERIFY)
- [ ] CRUD de reglas via API y via conversacion con Admin
- [ ] Reglas por defecto al crear organizacion (plantilla estandar)
- [ ] Evaluacion de reglas en cascada: una transaccion pasa por TODAS las reglas activas
- [ ] Endpoint `GET /PUT /api/v1/agents/fraud/rules/{org_id}`
- [ ] Tests con escenarios: transaccion normal (pasa), transaccion sospechosa (alerta), transaccion bloqueada

**Notas Tecnicas:**

- Evaluacion sincrona en el flujo de transaccion (< 200ms)
- Cache de reglas en memoria por organizacion (TTL 5 min)
- Reglas default: velocity > 10 ops/5min, amount > $50,000, horario fuera 6am-11pm

**Dependencias:** US-SP-131 (framework multi-agente), EP-SP-010 (limites como baseline)

---

#### US-SP-165: Evaluacion en Tiempo Real de Transacciones

**ID:** US-SP-165
**Epica:** EP-SP-037
**Prioridad:** P0
**Story Points:** 13

Como **Sistema** quiero evaluar cada transaccion contra las reglas de fraude en tiempo real para detectar operaciones sospechosas antes de que se ejecuten.

**Criterios de Aceptacion:**

- [ ] Consumer de SQS que recibe evento pre-transaccion de covacha-payment
- [ ] Evaluacion contra todas las reglas activas de la organizacion
- [ ] Calculo de risk score (0-100) basado en reglas activadas y sus severidades
- [ ] Si risk_score > 80: BLOQUEAR transaccion y notificar
- [ ] Si risk_score 50-80: VERIFICAR con el usuario antes de ejecutar
- [ ] Si risk_score < 50: PERMITIR y registrar score
- [ ] Registro de evaluacion: `PK: FRAUD_EVAL#{eval_id}, SK: DETAIL`
- [ ] Latencia maxima de evaluacion: 200ms (para no afectar experiencia del usuario)
- [ ] Metricas: evaluaciones/minuto, bloqueos, verificaciones, falsos positivos

**Notas Tecnicas:**

- Patron pre-hook: covacha-payment publica evento PRE_TRANSACTION a SQS antes de ejecutar
- covacha-botia evalua y responde con ALLOW/BLOCK/VERIFY via SQS de respuesta
- Si no responde en 500ms, covacha-payment procede (fail-open para no degradar servicio)

**Dependencias:** US-SP-164 (reglas configuradas)

---

#### US-SP-166: Bloqueo Preventivo y Notificacion

**ID:** US-SP-166
**Epica:** EP-SP-037
**Prioridad:** P0
**Story Points:** 8

Como **Usuario Final B2C** quiero ser notificado inmediatamente si una transaccion sospechosa se bloquea en mi cuenta para saber que mi dinero esta protegido.

**Criterios de Aceptacion:**

- [ ] Al bloquear, notificar al usuario via WhatsApp: "Bloqueamos una transaccion sospechosa de $X a CLABE Y. No fuiste tu? Responde NO"
- [ ] Si el usuario responde "NO" (no fue el): escalar a equipo antifraude + bloquear cuenta temporalmente
- [ ] Si el usuario responde "SI" (si fue el): iniciar flujo de verificacion (US-SP-167)
- [ ] Notificacion simultanea al Admin SuperPago via Slack
- [ ] Transaccion queda en estado BLOCKED hasta resolucion
- [ ] Timeout de respuesta: si no responde en 30 minutos, mantener bloqueo y escalar

**Notas Tecnicas:**

- Doble notificacion: WhatsApp al usuario + Slack al equipo antifraude
- Estado BLOCKED en la transaccion con TTL de 24h para auto-resolucion
- Evento publicado a EP-SP-029 (notificaciones) para audit trail

**Dependencias:** US-SP-165 (evaluacion que genera bloqueo), EP-SP-029 (notificaciones)

---

#### US-SP-167: Cuestionario de Verificacion al Usuario

**ID:** US-SP-167
**Epica:** EP-SP-037
**Prioridad:** P0
**Story Points:** 8

Como **Sistema** quiero verificar la identidad del usuario cuando una transaccion es sospechosa pero no lo suficiente para bloquear, para reducir falsos positivos sin comprometer la seguridad.

**Criterios de Aceptacion:**

- [ ] Cuestionario via WhatsApp: 2-3 preguntas de verificacion
- [ ] Preguntas posibles: ultimo monto transferido, nombre del ultimo beneficiario, saldo aproximado
- [ ] Si responde correctamente (2/3): desbloquear y ejecutar transaccion
- [ ] Si responde incorrectamente: bloquear transaccion y escalar
- [ ] 2FA adicional obligatoria despues de verificacion exitosa
- [ ] Maximo 1 intento de verificacion por transaccion
- [ ] Timeout: 5 minutos para responder el cuestionario

**Notas Tecnicas:**

- Preguntas generadas dinamicamente basadas en historial real del usuario
- No usar datos sensibles como preguntas (no preguntar CLABE completa)
- Registro en audit trail: preguntas realizadas, respuestas, resultado

**Dependencias:** US-SP-166 (flujo de verificacion post-bloqueo)

---

#### US-SP-168: Reportes de Fraude y Dashboard de Alertas

**ID:** US-SP-168
**Epica:** EP-SP-037
**Prioridad:** P1
**Story Points:** 8

Como **Administrador SuperPago** quiero ver un dashboard de alertas de fraude con metricas para evaluar la efectividad del sistema y ajustar reglas.

**Criterios de Aceptacion:**

- [ ] "Reporte de fraude de esta semana" -> resumen: alertas generadas, bloqueados, verificados, falsos positivos
- [ ] Metricas clave: tasa de deteccion, tasa de falsos positivos, monto protegido, tiempo promedio de resolucion
- [ ] Top 5 reglas mas activadas
- [ ] Top 5 organizaciones con mas alertas
- [ ] Historial de alertas filtrable: por severidad, por tipo, por organizacion, por fecha
- [ ] Endpoint `GET /api/v1/agents/fraud/report?from={date}&to={date}`
- [ ] Endpoint `GET /api/v1/agents/fraud/alerts?status={status}&severity={severity}`

**Notas Tecnicas:**

- Metricas pre-calculadas via Lambda cron diario, almacenadas en `AGENT_METRICS#fraud`
- Dashboard en mf-ia para vista grafica
- Reporte enviable por WhatsApp como texto formateado o PDF

**Dependencias:** US-SP-165 (evaluaciones registradas), US-SP-166 (bloqueos registrados)

---

#### US-SP-169: Integracion con Listas Negras

**ID:** US-SP-169
**Epica:** EP-SP-037
**Prioridad:** P1
**Story Points:** 5

Como **Administrador SuperPago** quiero mantener listas negras de CLABEs y cuentas sospechosas para bloquear automaticamente transacciones a destinos conocidos como fraudulentos.

**Criterios de Aceptacion:**

- [ ] CRUD de listas negras: `PK: BLACKLIST#CLABE, SK: #{clabe}` y `PK: BLACKLIST#PHONE, SK: #{phone}`
- [ ] Agregar via conversacion: "Agrega CLABE 072180... a lista negra" -> confirma -> agrega
- [ ] Importar via CSV: subir archivo con CLABEs a bloquear
- [ ] Fuente de lista: manual (admin), automatica (fraude confirmado), externa (CNBV)
- [ ] Al evaluar transaccion, verificar destino contra lista negra
- [ ] Alerta si el destino esta en lista negra: severidad CRITICAL, accion BLOCK
- [ ] Endpoint `POST /api/v1/agents/fraud/blacklist` para agregar entrada

**Notas Tecnicas:**

- Listas negras cacheadas en memoria (< 10K entradas, lookup O(1) con set)
- Refresh de cache cada 5 minutos
- Fuente CNBV: importacion manual periodica (no hay API publica)

**Dependencias:** US-SP-164 (reglas de fraude, BLACKLIST como tipo de regla)

---

### EP-SP-038: Agente de Reportes y Analytics Financieros

---

#### US-SP-170: Estado de Cuenta por Periodo

**ID:** US-SP-170
**Epica:** EP-SP-038
**Prioridad:** P0
**Story Points:** 8

Como **Cliente Empresa** quiero solicitar mi estado de cuenta de un periodo especifico via WhatsApp para tener visibilidad de mis movimientos sin entrar al portal.

**Criterios de Aceptacion:**

- [ ] "Estado de cuenta de enero" -> genera PDF con todos los movimientos del periodo
- [ ] "Estado de cuenta del 1 al 15 de febrero" -> periodo personalizado
- [ ] Contenido: saldo inicial, movimientos (fecha, tipo, monto, concepto, saldo parcial), saldo final
- [ ] Agrupacion por tipo: SPEI In, SPEI Out, BillPay, Cash-In, Cash-Out, Comisiones
- [ ] PDF con formato profesional: logo, datos de la organizacion, periodo, totales
- [ ] Envio por WhatsApp como documento PDF
- [ ] Tambien disponible en CSV y Excel si se solicita

**Notas Tecnicas:**

- PDF generado con ReportLab (Python)
- Datos de covacha-transaction + covacha-payment (ledger entries)
- Maximo 3 meses por reporte para limitar tamano
- PDF almacenado en S3 con presigned URL (expira en 24h)

**Dependencias:** US-SP-131 (framework multi-agente)

---

#### US-SP-171: Resumen de Transacciones y KPIs

**ID:** US-SP-171
**Epica:** EP-SP-038
**Prioridad:** P0
**Story Points:** 5

Como **Cliente Empresa** quiero preguntar "Como van mis numeros este mes?" y recibir un resumen rapido con metricas clave para tomar decisiones informadas.

**Criterios de Aceptacion:**

- [ ] Resumen rapido via texto formateado (no PDF, para lectura inmediata en WhatsApp)
- [ ] KPIs incluidos: total ingresos, total egresos, balance neto, numero de transacciones, comisiones pagadas
- [ ] Comparacion vs mes anterior: "Tus ingresos subieron 15% vs enero"
- [ ] Desglose por producto: SPEI, BillPay, Cash
- [ ] "Mis KPIs" -> resumen del mes actual
- [ ] "Mis KPIs de enero" -> resumen del mes especificado

**Notas Tecnicas:**

- Metricas calculadas en tiempo real consultando covacha-transaction
- Formato WhatsApp: usar negritas (*texto*) y saltos de linea para legibilidad
- Cache de KPIs por 1 hora (evitar recalcular en cada consulta)

**Dependencias:** US-SP-131 (framework multi-agente)

---

#### US-SP-172: Reporte de Comisiones Detallado

**ID:** US-SP-172
**Epica:** EP-SP-038
**Prioridad:** P1
**Story Points:** 5

Como **Cliente Empresa** quiero ver cuanto he pagado de comisiones desglosado por tipo de servicio para controlar mis costos operativos.

**Criterios de Aceptacion:**

- [ ] "Cuanto he pagado de comisiones?" -> desglose por producto (SPEI, BillPay, Cash, Openpay)
- [ ] Detalle por producto: numero de operaciones, comision unitaria, total comisiones, IVA
- [ ] Periodo: mes actual por defecto, personalizable
- [ ] Comparacion: "Mis comisiones de enero vs febrero" -> tabla comparativa
- [ ] Exportable en CSV para integracion con sistemas contables del cliente

**Notas Tecnicas:**

- Comisiones almacenadas en cuentas RESERVADA_COMISIONES_* (EP-SP-024)
- Consulta directa al ledger agrupando por categoria
- CSV generado en memoria y enviado via WhatsApp Media

**Dependencias:** US-SP-170 (estado de cuenta como contexto)

---

#### US-SP-173: Reportes Programados

**ID:** US-SP-173
**Epica:** EP-SP-038
**Prioridad:** P1
**Story Points:** 8

Como **Cliente Empresa** quiero programar reportes automaticos semanales o mensuales para recibirlos sin tener que solicitarlos cada vez.

**Criterios de Aceptacion:**

- [ ] "Envia mi estado de cuenta cada lunes" -> configura reporte semanal
- [ ] "Envia resumen de comisiones el 1 de cada mes" -> configura reporte mensual
- [ ] Modelo DynamoDB: `PK: USER#{user_id}#REPORT_SCHEDULES, SK: RSCHED#{schedule_id}`
- [ ] Attrs: report_type, frequency (weekly/monthly), day_of_week/day_of_month, format (pdf/csv), enabled
- [ ] Lambda scheduler que ejecuta reportes programados
- [ ] Listar programados: "Mis reportes automaticos" -> lista activos
- [ ] Cancelar: "Cancela el reporte semanal" -> desactiva
- [ ] Maximo 5 reportes programados por usuario

**Notas Tecnicas:**

- EventBridge Scheduler para ejecutar en fecha/hora configurada
- Generacion del reporte y envio via SQS a covacha-botia para delivery por WhatsApp
- Hora de envio: 8am hora Mexico por defecto, configurable

**Dependencias:** US-SP-170 (generacion de reportes), EP-SP-029 (notificaciones para envio)

---

#### US-SP-174: Exportacion Multi-Formato

**ID:** US-SP-174
**Epica:** EP-SP-038
**Prioridad:** P2
**Story Points:** 5

Como **Cliente Empresa** quiero recibir mis reportes en PDF, CSV o Excel para integrarlos con mis sistemas contables segun el formato que necesite.

**Criterios de Aceptacion:**

- [ ] Al solicitar cualquier reporte, preguntar formato: "En que formato lo quieres? PDF, CSV o Excel"
- [ ] PDF: formato visual con graficas y totales
- [ ] CSV: datos tabulares planos para importacion a sistemas
- [ ] Excel: datos tabulares con formato, totales y graficas basicas
- [ ] Envio por WhatsApp como documento adjunto
- [ ] Si el archivo > 16MB (limite WhatsApp), enviar enlace de descarga (presigned URL S3)

**Notas Tecnicas:**

- PDF: ReportLab, CSV: modulo csv de Python, Excel: openpyxl
- Archivos almacenados en S3 con TTL de 7 dias
- Presigned URL como fallback para archivos grandes

**Dependencias:** US-SP-170 (generacion base de reportes)

---

### EP-SP-039: Agente de Subasta de Efectivo (Marketplace)

---

#### US-SP-175: Publicacion de Ofertas de Efectivo via Conversacion

**ID:** US-SP-175
**Epica:** EP-SP-039
**Prioridad:** P0
**Story Points:** 5

Como **Operador Punto de Pago** quiero publicar mi efectivo disponible en el marketplace via WhatsApp para que empresas interesadas puedan comprarlo.

**Criterios de Aceptacion:**

- [ ] "Tengo $50,000 disponibles en sucursal Centro" -> crea oferta en marketplace
- [ ] Validacion: monto disponible <= saldo fisico del punto (segun ultimo cuadre)
- [ ] Oferta incluye: monto, ubicacion del punto, vigencia (24h por defecto)
- [ ] Confirmacion: "Oferta publicada: $50,000 en Punto Centro. Vigencia: 24h"
- [ ] Consume `POST /api/v1/auction/offers` (EP-SP-016)
- [ ] Listado de ofertas activas: "Mis ofertas" -> lista con estado

**Notas Tecnicas:**

- Validacion de saldo contra ultimo cuadre de caja (US-SP-161)
- Oferta expira automaticamente si no se compra (EP-SP-016 maneja expiracion)

**Dependencias:** US-SP-131 (framework multi-agente), EP-SP-016 (subasta backend)

---

#### US-SP-176: Notificacion de Matches y Aceptacion

**ID:** US-SP-176
**Epica:** EP-SP-039
**Prioridad:** P0
**Story Points:** 8

Como **Cliente Empresa** quiero ser notificado cuando haya efectivo disponible en puntos cercanos y poder aceptar la oferta via WhatsApp para obtener liquidez fisica rapidamente.

**Criterios de Aceptacion:**

- [ ] Notificacion al comprador potencial: "Hay $50,000 disponibles en Punto Centro. Quieres comprar?"
- [ ] Match basado en: monto solicitado, ubicacion preferida, historial de compras
- [ ] Aceptar oferta: "Si, compro" -> confirma -> 2FA -> ejecuta transferencia inter-org
- [ ] Rechazar: "No, gracias" -> busca siguiente match
- [ ] Contraoferta: "Solo necesito $30,000" -> si el vendedor acepta, ejecuta parcial
- [ ] Consume `POST /api/v1/auction/accept/{offer_id}` (EP-SP-016)
- [ ] Consume `POST /api/v1/transfers/inter-org` (EP-SP-014) para la transferencia

**Notas Tecnicas:**

- Matching algorithm en covacha-payment (EP-SP-016); el agente solo notifica y facilita
- Notificacion via SQS event AUCTION_MATCH_FOUND
- 2FA obligatoria para la transferencia (mueve dinero real)

**Dependencias:** US-SP-175 (ofertas publicadas), EP-SP-016 (matching), EP-SP-014 (transferencia inter-org)

---

#### US-SP-177: Confirmacion Bilateral y Ejecucion

**ID:** US-SP-177
**Epica:** EP-SP-039
**Prioridad:** P0
**Story Points:** 8

Como **Sistema** quiero que tanto vendedor como comprador confirmen la transaccion de subasta para garantizar que ambas partes estan de acuerdo antes de mover dinero.

**Criterios de Aceptacion:**

- [ ] Al aceptar comprador, notificar al vendedor: "Empresa X quiere comprar tu oferta de $50,000. Confirmas?"
- [ ] Vendedor confirma: "Si" -> ejecuta transferencia inter-org
- [ ] Vendedor rechaza: "No" -> notifica al comprador y cancela match
- [ ] Timeout de confirmacion: 30 minutos; si no confirma, cancela y busca otro match
- [ ] Al ejecutar: dinero digital se transfiere, efectivo queda asignado para retiro
- [ ] Ambas partes reciben confirmacion: "Transaccion completada. Referencia: SUB-XXXX"

**Notas Tecnicas:**

- Estado de subasta: PUBLISHED -> MATCHED -> PENDING_SELLER -> CONFIRMED -> EXECUTED -> DELIVERED
- Cada cambio de estado persiste en DynamoDB con timestamp
- Transaccion inter-org usa idempotency key basada en auction_id

**Dependencias:** US-SP-176 (match aceptado por comprador)

---

#### US-SP-178: Seguimiento de Entrega y Rating

**ID:** US-SP-178
**Epica:** EP-SP-039
**Prioridad:** P1
**Story Points:** 5

Como **Cliente Empresa** quiero confirmar que recibi el efectivo fisico y calificar al vendedor para mantener la confianza en el marketplace.

**Criterios de Aceptacion:**

- [ ] Despues de ejecutar, el agente pregunta al comprador (24h despues): "Ya recibiste el efectivo?"
- [ ] "Si, ya lo recibi" -> marca como DELIVERED y solicita rating
- [ ] "No, aun no" -> programa seguimiento a las 48h; si pasan 72h, escalar al Admin
- [ ] Rating: 1-5 estrellas via WhatsApp: "Califica al vendedor: 1-5"
- [ ] Rating almacenado en: `PK: RATING#USER#{seller_id}, SK: #{timestamp}`
- [ ] Rating promedio visible al publicar ofertas futuras

**Notas Tecnicas:**

- Seguimiento via SQS con delay de 24h/48h
- Rating promedio calculado y cacheado en perfil del punto de pago
- Escalacion al Admin si no se confirma entrega en 72h

**Dependencias:** US-SP-177 (transaccion ejecutada)

---

#### US-SP-179: Historial de Subastas y Metricas

**ID:** US-SP-179
**Epica:** EP-SP-039
**Prioridad:** P2
**Story Points:** 5

Como **Administrador SuperPago** quiero ver metricas del marketplace de efectivo para entender la liquidez de la red y optimizar el sistema.

**Criterios de Aceptacion:**

- [ ] "Metricas de subasta de esta semana" -> resumen: ofertas publicadas, ejecutadas, monto total, tiempo promedio de match
- [ ] Historial filtrable: por punto de pago, por empresa compradora, por fecha, por monto
- [ ] Metricas de liquidez: efectivo disponible en red, demanda no satisfecha
- [ ] Top 5 puntos con mas ofertas, top 5 empresas compradoras
- [ ] Endpoint `GET /api/v1/agents/auction/metrics?from={date}&to={date}`

**Notas Tecnicas:**

- Metricas pre-calculadas via Lambda cron diario
- Almacenadas en `AGENT_METRICS#auction` por dia
- Dashboard en mf-ia

**Dependencias:** US-SP-177 (transacciones ejecutadas como dato)

---

### EP-SP-040: Agente de Compliance y Regulatorio

---

#### US-SP-180: Deteccion de Operaciones Relevantes e Inusuales

**ID:** US-SP-180
**Epica:** EP-SP-040
**Prioridad:** P0
**Story Points:** 13

Como **Sistema** quiero clasificar automaticamente cada transaccion como relevante, inusual o preocupante segun criterios CNBV para cumplir con la regulacion de PLD/FT.

**Criterios de Aceptacion:**

- [ ] Clasificacion automatica al ejecutar transaccion (post-hook via SQS)
- [ ] Operacion RELEVANTE: monto > $50,000 MXN (o equivalente USD) en una sola operacion
- [ ] Operacion RELEVANTE: acumulado > $200,000 MXN mensual por cuenta
- [ ] Operacion INUSUAL: patron que no coincide con perfil historico del cliente
- [ ] Operacion PREOCUPANTE: multiples indicadores simultaneos (monto + velocidad + horario)
- [ ] Registro en DynamoDB: `PK: COMPLIANCE#{org_id}, SK: OP#{timestamp}#{txn_id}`
- [ ] Attrs: classification, amount, account_id, trigger_rules, reviewer_id, status (PENDING_REVIEW/REVIEWED/REPORTED)
- [ ] Notificacion al Oficial de Compliance via WhatsApp cuando hay operacion PREOCUPANTE

**Notas Tecnicas:**

- Consumer de SQS post-transaccion (diferente al de fraude: fraude es pre, compliance es post)
- Umbrales configurables por organizacion en `ORG#{org_id}#COMPLIANCE_THRESHOLDS`
- Acumulado mensual calculado con query al ledger agrupando por cuenta y mes

**Dependencias:** US-SP-131 (framework multi-agente), EP-SP-037 (fraude como input complementario)

---

#### US-SP-181: Generacion de Reportes Regulatorios CNBV/Banxico

**ID:** US-SP-181
**Epica:** EP-SP-040
**Prioridad:** P0
**Story Points:** 13

Como **Oficial de Compliance** quiero generar los reportes regulatorios requeridos por CNBV y Banxico para cumplir con las obligaciones legales de la plataforma.

**Criterios de Aceptacion:**

- [ ] "Genera reporte CNBV de enero" -> genera reporte de operaciones relevantes del periodo
- [ ] Formato de reporte segun especificacion CNBV (XML o formato requerido)
- [ ] Incluye: operaciones relevantes, inusuales, preocupantes con todos los datos requeridos
- [ ] Datos por operacion: fecha, monto, origen, destino, tipo, justificacion si fue revisada
- [ ] Reporte mensual automatico generado el dia 5 de cada mes
- [ ] Almacenamiento de reportes en S3: `s3://sp-compliance-reports/{year}/{month}/cnbv_{date}.xml`
- [ ] Historial de reportes generados consultable via conversacion

**Notas Tecnicas:**

- Formato CNBV: XML con schema definido por la regulacion (investigar schema actual)
- Generacion con lxml (Python) para XML
- Reportes firmados digitalmente con certificado de la empresa
- Retencion minima: 10 anos (regulacion CNBV)

**Dependencias:** US-SP-180 (operaciones clasificadas)

---

#### US-SP-182: Monitoreo de Umbrales y Alertas KYC

**ID:** US-SP-182
**Epica:** EP-SP-040
**Prioridad:** P0
**Story Points:** 8

Como **Oficial de Compliance** quiero recibir alertas cuando una cuenta se acerca a umbrales regulatorios o cuando documentos KYC estan por vencer para actuar preventivamente.

**Criterios de Aceptacion:**

- [ ] Alerta al 80% del umbral mensual ($160,000 de $200,000): "Cuenta X de Org Y lleva $160,000 acumulados este mes"
- [ ] Alerta al alcanzar umbral: "Cuenta X supero $200,000. Operacion clasificada como RELEVANTE"
- [ ] Alerta de KYC por vencer: 90, 60, 30 dias antes de vencimiento de documentos
- [ ] "El INE de representante legal de Boxito vence el 15 de marzo (en 27 dias)"
- [ ] Modelo DynamoDB para KYC: `PK: ORG#{org_id}#KYC, SK: DOC#{doc_type}`
- [ ] Attrs: doc_type, expiry_date, status (VALID/EXPIRING/EXPIRED), last_verified
- [ ] Lambda cron diario para verificar vencimientos y umbrales

**Notas Tecnicas:**

- Umbrales consultados del ledger (acumulado mensual por cuenta)
- KYC expiry verificada diariamente a las 7am
- Notificaciones via EP-SP-029 al canal WhatsApp del Oficial de Compliance

**Dependencias:** US-SP-180 (umbrales), EP-SP-029 (notificaciones)

---

#### US-SP-183: Consulta Conversacional de Compliance

**ID:** US-SP-183
**Epica:** EP-SP-040
**Prioridad:** P1
**Story Points:** 5

Como **Oficial de Compliance** quiero consultar el estado de compliance via WhatsApp para tener visibilidad sin abrir el portal.

**Criterios de Aceptacion:**

- [ ] "Operaciones relevantes de hoy" -> lista con monto, cuenta, organizacion
- [ ] "Cuantas operaciones inusuales hay pendientes?" -> conteo por estado
- [ ] "Status de KYC de Boxito" -> lista documentos con fecha de vencimiento y estado
- [ ] "Resumen de compliance de enero" -> metricas: relevantes, inusuales, preocupantes, reportadas
- [ ] Filtros: por organizacion, por clasificacion, por estado de revision

**Notas Tecnicas:**

- Consultas directas a DynamoDB con los GSIs de compliance
- Respuestas formateadas con negritas y listas para legibilidad en WhatsApp
- Cache de 5 minutos para consultas frecuentes

**Dependencias:** US-SP-180 (datos de compliance)

---

#### US-SP-184: Audit Trail Completo PLD/FT

**ID:** US-SP-184
**Epica:** EP-SP-040
**Prioridad:** P0
**Story Points:** 8

Como **Sistema** quiero mantener un audit trail inmutable de todas las verificaciones y acciones de compliance para cumplir con los requisitos de trazabilidad de la CNBV.

**Criterios de Aceptacion:**

- [ ] Registro de cada accion de compliance: `PK: AUDIT_PLD#{org_id}, SK: #{timestamp}#{action_id}`
- [ ] Acciones registradas: clasificacion de operacion, revision manual, cambio de status, generacion de reporte, alerta enviada
- [ ] Attrs: action_type, actor (user_id o SYSTEM), target_entity, details, timestamp
- [ ] Inmutabilidad: solo INSERT, nunca UPDATE ni DELETE (append-only)
- [ ] Retencion minima: 10 anos (configurar TTL = null, sin expiracion)
- [ ] Exportacion del audit trail: "Exporta audit PLD de Boxito 2025" -> CSV con todos los registros
- [ ] GSI: `PK: AUDIT_PLD#ACTOR#{user_id}, SK: #{timestamp}` para consultar por responsable

**Notas Tecnicas:**

- Append-only: DynamoDB ConditionExpression que prohibe overwrite de registros existentes
- Backup diario a S3 Glacier para retencion de largo plazo
- Formato compatible con requerimientos de auditoria CNBV

**Dependencias:** US-SP-180 (clasificaciones), US-SP-181 (reportes)

---

#### US-SP-185: Marcado Manual de Operaciones y Revision

**ID:** US-SP-185
**Epica:** EP-SP-040
**Prioridad:** P1
**Story Points:** 5

Como **Oficial de Compliance** quiero marcar manualmente una operacion como preocupante y registrar mi revision para documentar hallazgos que el sistema automatico no detecto.

**Criterios de Aceptacion:**

- [ ] "Marcar operacion TXN#abc123 como preocupante" -> confirma -> registra con justificacion
- [ ] Solicita justificacion: "Cual es el motivo?" -> registra texto libre
- [ ] Cambiar clasificacion: "Reclasifica TXN#abc123 de inusual a preocupante"
- [ ] Revisar pendientes: "Operaciones pendientes de revision" -> lista PENDING_REVIEW
- [ ] Marcar como revisada: "Revisar operacion TXN#abc123: sin hallazgos" -> status = REVIEWED
- [ ] Cada accion registrada en audit trail (US-SP-184)
- [ ] Endpoint `POST /api/v1/agents/compliance/flag-operation/{txn_id}`

**Notas Tecnicas:**

- Solo Oficial de Compliance puede marcar/reclasificar (validacion de rol en sesion)
- Justificacion obligatoria para operaciones PREOCUPANTES
- Registro en audit trail con actor = user_id del Oficial

**Dependencias:** US-SP-180 (operaciones clasificadas), US-SP-184 (audit trail)

---

## Roadmap

### Vista por Sprint

| Sprint | Epica(s) | User Stories | Story Points |
|--------|----------|-------------|--------------|
| 17 | EP-SP-031, EP-SP-032 | US-SP-131 (Framework), US-SP-132, US-SP-137, US-SP-138 | 37 |
| 18 | EP-SP-031, EP-SP-032, EP-SP-033, EP-SP-035 | US-SP-133, US-SP-134, US-SP-139, US-SP-140, US-SP-142, US-SP-153 | 42 |
| 19 | EP-SP-031, EP-SP-033, EP-SP-034, EP-SP-035, EP-SP-036 | US-SP-135, US-SP-136, US-SP-143, US-SP-148, US-SP-154, US-SP-159 | 39 |
| 20 | EP-SP-033, EP-SP-034, EP-SP-035, EP-SP-036, EP-SP-037, EP-SP-038 | US-SP-144, US-SP-145, US-SP-149, US-SP-150, US-SP-155, US-SP-156, US-SP-160, US-SP-161, US-SP-164, US-SP-170, US-SP-171 | 87 |
| 21 | EP-SP-033, EP-SP-034, EP-SP-035, EP-SP-036, EP-SP-037, EP-SP-038, EP-SP-039 | US-SP-141, US-SP-146, US-SP-147, US-SP-151, US-SP-152, US-SP-157, US-SP-158, US-SP-162, US-SP-163, US-SP-165, US-SP-166, US-SP-172, US-SP-173, US-SP-175, US-SP-176, US-SP-180 | 118 |
| 22 | EP-SP-037, EP-SP-038, EP-SP-039, EP-SP-040 | US-SP-167, US-SP-168, US-SP-169, US-SP-174, US-SP-177, US-SP-178, US-SP-179, US-SP-181, US-SP-182 | 70 |
| 23 | EP-SP-040 | US-SP-183, US-SP-184, US-SP-185 | 18 |

### Linea de Tiempo

```
Sprint 17: [Equipo A: US-SP-131 Framework + US-SP-132 Onboarding]  [Equipo B: US-SP-137 FAQ + US-SP-138 Consultas]
Sprint 18: [Equipo A: US-SP-133 KYB + US-SP-134 Cuentas]          [Equipo B: US-SP-139 Comisiones + US-SP-140 Escalacion + US-SP-142 Beneficiarios + US-SP-153 Catalogo]
Sprint 19: [Equipo A: US-SP-135/136 Onboarding + US-SP-143 Programadas]  [Equipo B: US-SP-148 Monitor Conc. + US-SP-154 Pagos + US-SP-159 QR]
Sprint 20: [Equipo A: US-SP-144/145 Recurrentes+Batch + US-SP-149/150 Conciliacion]  [Equipo B: US-SP-155/156 Recargas+Historial + US-SP-160/161 Cash + US-SP-164 Fraude + US-SP-170/171 Reportes]
Sprint 21: [Equipo A: US-SP-141/146/147 Metricas+CLABE+Alertas + US-SP-151/152 PDF+Audit + US-SP-165/166 Fraude RT]  [Equipo B: US-SP-157/158 Recordatorios+Favs + US-SP-162/163 Limites+Turno + US-SP-172/173 Comisiones+Programados + US-SP-175/176 Subasta + US-SP-180 Compliance]
Sprint 22: [Equipo A: US-SP-167/168/169 Verificacion+Reportes+Blacklist + US-SP-177/178/179 Subasta]  [Equipo B: US-SP-174 Export + US-SP-181/182 CNBV+KYC]
Sprint 23: [Equipo A: US-SP-183/184/185 Compliance conversacional + audit + revision]  [Buffer + QA + Integration testing]
```

### Resumen por Epica

| Epica | User Stories | Story Points | Sprints |
|-------|-------------|--------------|---------|
| EP-SP-031 (Onboarding) | 6 (US-SP-131 a 136) | 47 | 17-19 |
| EP-SP-032 (Soporte) | 5 (US-SP-137 a 141) | 34 | 17-18 |
| EP-SP-033 (SPEI Avanzado) | 6 (US-SP-142 a 147) | 44 | 18-21 |
| EP-SP-034 (Conciliacion) | 5 (US-SP-148 a 152) | 34 | 19-21 |
| EP-SP-035 (BillPay) | 6 (US-SP-153 a 158) | 39 | 18-21 |
| EP-SP-036 (Cash) | 5 (US-SP-159 a 163) | 31 | 19-21 |
| EP-SP-037 (Fraude) | 6 (US-SP-164 a 169) | 55 | 20-22 |
| EP-SP-038 (Reportes) | 5 (US-SP-170 a 174) | 31 | 20-22 |
| EP-SP-039 (Subasta) | 5 (US-SP-175 a 179) | 31 | 21-22 |
| EP-SP-040 (Compliance) | 6 (US-SP-180 a 185) | 52 | 21-23 |
| **TOTAL** | **55** | **398** | **17-23** |

---

## Grafo de Dependencias

### Dependencias entre Epicas

```
EP-SP-017 (Agente IA Core - existente)
    |
    +---> EP-SP-031 (Onboarding) ---> EP-SP-024 (Onboarding Backend)
    |                              +-> EP-SP-001 (Cuentas)
    |
    +---> EP-SP-032 (Soporte)
    |
    +---> EP-SP-033 (SPEI Avanzado) ---> EP-SP-004 (SPEI Out)
    |
    +---> EP-SP-034 (Conciliacion) ---> EP-SP-009 (Reconciliacion SPEI)
    |                               +-> EP-SP-023 (Reconciliacion BillPay)
    |
    +---> EP-SP-036 (Cash) ---> EP-SP-015 (Cash-In/Cash-Out)
    |
    +---> EP-SP-038 (Reportes) ---> EP-SP-029 (Notificaciones)
    |
    +---> EP-SP-039 (Subasta) ---> EP-SP-016 (Subasta Backend)
    |                           +-> EP-SP-014 (Transferencias Inter-Org)

EP-SP-018 (BillPay WhatsApp - existente)
    |
    +---> EP-SP-035 (BillPay Completo) ---> EP-SP-021 (Monato Driver)
                                         +-> EP-SP-022 (Operacion BILLPAY)

EP-SP-037 (Fraude)
    |
    +---> EP-SP-010 (Limites y Politicas)
    +---> EP-SP-029 (Notificaciones)
    |
    +---> EP-SP-040 (Compliance) ---> EP-SP-037 (input de fraude)
                                  +-> EP-SP-029 (Notificaciones)
```

### Dependencias entre User Stories (criticas)

```
US-SP-131 (Framework Multi-Agente)
    |
    +---> US-SP-132 (Onboarding Flujo)
    |         +---> US-SP-133 (Documentos KYB)
    |                   +---> US-SP-134 (Productos + Cuentas)
    |                             +---> US-SP-135 (Seguimiento)
    |                             +---> US-SP-136 (Panel Admin)
    |
    +---> US-SP-137 (FAQ Semantica)
    |         +---> US-SP-140 (Escalacion)
    |                   +---> US-SP-141 (Metricas Soporte)
    |
    +---> US-SP-138 (Consultas Transacciones)
    +---> US-SP-139 (Comisiones/Limites)
    |
    +---> US-SP-142 (Beneficiarios)
    |         +---> US-SP-143 (Programadas)
    |                   +---> US-SP-144 (Recurrentes)
    |         +---> US-SP-145 (Batch)
    |         +---> US-SP-146 (Validacion CLABE)
    |
    +---> US-SP-148 (Monitor Conciliacion)
    |         +---> US-SP-149 (Consulta Movimientos)
    |                   +---> US-SP-150 (Resolucion)
    |                             +---> US-SP-151 (Reporte PDF)
    |                             +---> US-SP-152 (Historial)
    |
    +---> US-SP-153 (Catalogo BillPay)
    |         +---> US-SP-154 (Pago Completo/Parcial)
    |                   +---> US-SP-155 (Recargas)
    |                   +---> US-SP-156 (Historial Pagos)
    |                   +---> US-SP-158 (Favoritos)
    |         +---> US-SP-157 (Recordatorios)
    |
    +---> US-SP-159 (QR Cash-In)
    |         +---> US-SP-160 (Cash-In/Out Conversacion)
    |                   +---> US-SP-161 (Cuadre Caja)
    |                             +---> US-SP-163 (Reporte Turno)
    |                   +---> US-SP-162 (Alertas Limites)
    |
    +---> US-SP-164 (Reglas Fraude)
    |         +---> US-SP-165 (Evaluacion RT)
    |                   +---> US-SP-166 (Bloqueo)
    |                             +---> US-SP-167 (Verificacion)
    |         +---> US-SP-169 (Listas Negras)
    |         +---> US-SP-168 (Dashboard Fraude)
    |
    +---> US-SP-170 (Estado Cuenta)
    |         +---> US-SP-172 (Comisiones)
    |         +---> US-SP-173 (Programados)
    |         +---> US-SP-174 (Multi-Formato)
    +---> US-SP-171 (KPIs)
    |
    +---> US-SP-175 (Publicar Oferta)
    |         +---> US-SP-176 (Match + Aceptacion)
    |                   +---> US-SP-177 (Confirmacion Bilateral)
    |                             +---> US-SP-178 (Entrega + Rating)
    |         +---> US-SP-179 (Metricas Subasta)
    |
    +---> US-SP-180 (Deteccion Compliance)
              +---> US-SP-181 (Reportes CNBV)
              +---> US-SP-182 (Umbrales + KYC)
              +---> US-SP-183 (Consulta Conversacional)
              +---> US-SP-184 (Audit Trail PLD)
                        +---> US-SP-185 (Marcado Manual)
```

---

## Riesgos y Mitigaciones

| # | Riesgo | Probabilidad | Impacto | Mitigacion |
|---|--------|-------------|---------|------------|
| R1 | Latencia de GPT-4 degrada experiencia conversacional (> 5s de respuesta) | Alta | Alto | Implementar cache de respuestas frecuentes, usar GPT-3.5-turbo para clasificacion de intents (rapido), GPT-4 solo para generacion de respuestas complejas. Bedrock como fallback |
| R2 | Costos de OpenAI escalan con volumen de usuarios | Alta | Medio | Monitorear costo por conversacion. Migrar clasificacion de intents a modelo local (Bedrock/Mistral) cuando el volumen justifique. Cache agresivo de FAQ |
| R3 | WhatsApp Business API tiene limites de rate (80 msg/s por numero) | Media | Alto | Implementar cola de mensajes salientes con rate limiter. Solicitar aumento de limites a Meta. Distribuir trafico entre multiples numeros si es necesario |
| R4 | Falsos positivos del motor de fraude bloquean transacciones legitimas | Alta | Alto | Comenzar con reglas conservadoras (umbral alto). Monitorear tasa de falsos positivos semanalmente. Ajustar reglas basado en datos reales. Verificacion antes de bloqueo para score 50-80 |
| R5 | OCR de documentos KYB falla con fotos de baja calidad | Media | Medio | Indicar al usuario requisitos de foto (buena iluminacion, sin reflejos). Permitir reintento. Fallback a revision manual si OCR falla 2 veces |
| R6 | Regulacion CNBV cambia formatos o umbrales de reporte | Media | Alto | Diseno modular de reportes (templates configurables). Umbrales como parametros en DynamoDB, no hardcodeados. Monitorear cambios regulatorios trimestralmente |
| R7 | Agente de conciliacion detecta discrepancia falsa por timing (transaccion en transito) | Media | Medio | Ventana de tolerancia de 24h antes de clasificar como discrepancia. Re-verificacion automatica antes de alertar. Estado IN_TRANSIT como filtro |
| R8 | Multiples agentes compiten por atender el mismo mensaje (race condition) | Baja | Alto | Agent Router como single point of entry. Mutex via DynamoDB ConditionExpression en sesion activa. Solo 1 agente activo por sesion |
| R9 | Datos sensibles (CLABEs, montos, RFC) expuestos en logs de conversacion | Media | Critico | Enmascarar datos sensibles en logs: CLABE -> 072***5678, RFC -> ABC***123. Encriptacion at-rest en DynamoDB. No loggear contenido completo de mensajes |
| R10 | Usuario malicioso manipula agente de compliance para ocultar operaciones | Baja | Critico | Audit trail inmutable (append-only). Segregacion de roles: solo Oficial de Compliance puede marcar/reclasificar. Doble verificacion para reclasificar de PREOCUPANTE a NORMAL |
