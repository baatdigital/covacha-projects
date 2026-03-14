# Nomina Digital - Dispersiones SPEI para PyMEs (EP-NM-001 a EP-NM-008)

**Fecha**: 2026-03-14
**Product Owner**: SuperPago
**Estado**: Planificacion
**GitHub Issue**: baatdigital/covacha-projects#132
**Score**: 7/10 | **Time to Market**: 12 semanas | **Reuso**: 70%

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

Sistema de nomina simplificado que permite a PyMEs con 5-50 empleados calcular y dispersar nomina via SPEI con un click. Sin la complejidad de un ERP, enfocado en simplicidad: registra empleados, configura sueldos, calcula nomina quincenal/semanal, y dispersa a todas las CLABEs en batch. Incluye recibos de nomina por WhatsApp y timbrado CFDI.

**Propuesta de valor**: Nomina simplificada para PyMEs que no necesitan un ERP completo, con dispersion SPEI instantanea y recibos por WhatsApp.

---

## Analisis de Mercado

| Metrica | Valor |
|---------|-------|
| **TAM Mexico** | $16.2B MXN/ano (4.5M PyMEs x $300/mes) |
| **SAM** | $3.6B MXN/ano (1M con nomina digital) |
| **SOM Year 1** | $7.2M MXN/ano (2,000 empresas x $299/mes) |

### Problema de Mercado

- PyMEs pequenas hacen nomina en Excel y transfieren manualmente
- ERPs (Aspel, CONTPAQi) son caros y complejos para 5-50 empleados
- Dispersion manual SPEI por empleado es lenta y propensa a errores
- No hay solucion integrada nomina + dispersion SPEI en Mexico para PyMEs

### Modelo de Revenue

| Plan | Precio MXN/mes | Empleados | Dispersiones/mes |
|------|---------------|-----------|-----------------|
| Starter | $199 | 10 | 2 |
| Pro | $499 | 50 | 4 |
| Business | $999 | Ilimitados | Ilimitadas |

---

## Reutilizacion del Ecosistema

| Componente | Repo Existente | Reutilizacion | Descripcion |
|-----------|---------------|---------------|-------------|
| Motor SPEI batch | covacha-payment | 90% | Dispersiones masivas existentes |
| Multi-tenant | covacha-core | 100% | Organizaciones, auth |
| Notificaciones WhatsApp | covacha-notification | 85% | Envio de recibos |
| Shell MF | mf-core | 100% | Module Federation |
| Modelos base | covacha-libs | 70% | Modelos, repos |
| **Nuevo** | covacha-payment (payroll) | 20% | Logica de calculo de nomina |
| **Nuevo** | mf-nomina | 0% | Micro-frontend nomina |

**Reutilizacion total estimada**: 70%

---

## Mapa de Epicas

| ID | Epica | Complejidad | Semana | Dependencias | Estado |
|----|-------|-------------|--------|--------------|--------|
| EP-NM-001 | Registro de Empleados y Datos Fiscales | M | 1-2 | covacha-core | Planificacion |
| EP-NM-002 | Calculo de Nomina (Sueldo + Deducciones) | L | 2-4 | EP-NM-001 | Planificacion |
| EP-NM-003 | Dispersion Masiva SPEI | L | 3-5 | EP-NM-002, covacha-payment | Planificacion |
| EP-NM-004 | Recibos de Nomina y Timbrado CFDI | L | 5-7 | EP-NM-003 | Planificacion |
| EP-NM-005 | Calendario de Pagos y Configuracion | M | 2-3 | EP-NM-001 | Planificacion |
| EP-NM-006 | Multi-Sucursal y Permisos | M | 5-7 | EP-NM-001 | Planificacion |
| EP-NM-007 | Dashboard y Reportes para Contador | M | 7-9 | EP-NM-001 a EP-NM-004 | Planificacion |
| EP-NM-008 | mf-nomina - Micro-Frontend | L | 4-12 | EP-NM-001 a EP-NM-007 | Planificacion |

**Totales:**
- 8 epicas
- 38 user stories (US-NM-001 a US-NM-038)
- Estimacion total: ~84 dev-days (12 semanas, 2 devs)

---

## Epicas Detalladas

---

### EP-NM-001: Registro de Empleados y Datos Fiscales

**Descripcion:**
CRUD de empleados con sus datos personales, fiscales (RFC, CURP, NSS), y bancarios (CLABE para dispersion SPEI). Cada empleado esta asociado a una organizacion y opcionalmente a una sucursal. Incluye validaciones de datos fiscales.

**User Stories:**
- US-NM-001: CRUD de empleados con datos personales y fiscales
- US-NM-002: Registro de datos bancarios (CLABE) por empleado
- US-NM-003: Importacion masiva de empleados desde CSV/Excel
- US-NM-004: Validacion de RFC y CURP contra formato SAT
- US-NM-005: Historial de cambios de datos del empleado

**Criterios de Aceptacion de la Epica:**
- [ ] Modelo Empleado: nombre, RFC, CURP, NSS, fecha_nacimiento, fecha_ingreso, CLABE, sueldo_base
- [ ] Validacion RFC formato (persona fisica, 13 caracteres)
- [ ] Validacion CURP formato (18 caracteres)
- [ ] CLABE validada (18 digitos, digito verificador)
- [ ] Import CSV con columnas estandar
- [ ] Reporte de errores de importacion
- [ ] Soft delete (baja de empleado con fecha y motivo)
- [ ] Historial de cambios (sueldo, CLABE, datos) con timestamp
- [ ] Busqueda por nombre, RFC, numero de empleado
- [ ] Tests >= 98%

**Dependencias:** covacha-core (multi-tenant)

**Complejidad:** M (5 user stories)

**Repositorios:** `covacha-core`, `covacha-libs`

---

### EP-NM-002: Calculo de Nomina (Sueldo + Deducciones)

**Descripcion:**
Motor de calculo de nomina que toma el sueldo base del empleado, aplica percepciones extras (horas extra, bonos, comisiones) y deducciones (ISR, IMSS, INFONAVIT, prestamos, faltas), y genera el neto a pagar. Soporta periodicidad quincenal y semanal.

**User Stories:**
- US-NM-006: Calculo de sueldo bruto con percepciones extras
- US-NM-007: Calculo de deducciones legales (ISR, IMSS, INFONAVIT)
- US-NM-008: Deducciones voluntarias (prestamos, anticipos, faltas)
- US-NM-009: Pre-nomina: preview del calculo antes de confirmar
- US-NM-010: Nomina extraordinaria (aguinaldo, PTU, finiquito)

**Criterios de Aceptacion de la Epica:**
- [ ] Percepciones: sueldo base, horas extra, bonos, comisiones, retroactivos
- [ ] Deducciones legales: ISR (tablas SAT vigentes), IMSS (cuotas obrero), INFONAVIT
- [ ] Deducciones voluntarias: prestamos empresa, anticipos, caja de ahorro, faltas
- [ ] Calculo de ISR con tablas mensuales/quincenales del SAT
- [ ] Pre-nomina: mostrar calculo por empleado antes de confirmar dispersion
- [ ] Ajustes manuales permitidos en pre-nomina
- [ ] Nomina extraordinaria: aguinaldo (15 dias min), PTU, finiquito/liquidacion
- [ ] Periodicidad: semanal, quincenal, mensual (configurable)
- [ ] Precision: calculos con Decimal (no float)
- [ ] Tests >= 98%

**Dependencias:** EP-NM-001 (empleados)

**Complejidad:** L (5 user stories, logica fiscal compleja)

**Repositorios:** `covacha-payment`

---

### EP-NM-003: Dispersion Masiva SPEI

**Descripcion:**
Orquestacion de la dispersion masiva de nomina via SPEI. Toma el resultado del calculo de nomina y genera transferencias SPEI individuales a la CLABE de cada empleado. Reutiliza el motor de SPEI batch de covacha-payment con un flujo de aprobacion y ejecucion.

**User Stories:**
- US-NM-011: Generar lote de dispersion desde nomina calculada
- US-NM-012: Aprobacion del lote antes de ejecutar (doble autorizacion)
- US-NM-013: Ejecutar dispersion masiva SPEI
- US-NM-014: Tracking de estado por empleado (enviado, confirmado, fallido)
- US-NM-015: Reintentar dispersiones fallidas individualmente

**Criterios de Aceptacion de la Epica:**
- [ ] Lote de dispersion generado desde pre-nomina aprobada
- [ ] Validacion de saldo suficiente antes de iniciar
- [ ] Aprobacion requerida: maker-checker (quien calcula != quien aprueba)
- [ ] Ejecucion batch via SPEI con el motor existente de covacha-payment
- [ ] Estado por dispersion: PENDING, SENT, CONFIRMED, FAILED
- [ ] Confirmacion via webhook SPEI por cada transferencia
- [ ] Retry individual para dispersiones fallidas
- [ ] Notificacion al admin: "Dispersion completada: X exitosos, Y fallidos"
- [ ] Log de dispersion: timestamp, montos, CLABEs, estados
- [ ] Tests >= 98%

**Dependencias:** EP-NM-002, covacha-payment (SPEI batch)

**Complejidad:** L (5 user stories)

**Repositorios:** `covacha-payment`

---

### EP-NM-004: Recibos de Nomina y Timbrado CFDI

**Descripcion:**
Generacion de recibos de nomina en PDF, timbrado CFDI ante el SAT, y envio automatico al empleado por WhatsApp y email. Los recibos cumplen con las especificaciones de la guia de llenado del SAT para nomina 1.2.

**User Stories:**
- US-NM-016: Generacion de recibo de nomina en PDF
- US-NM-017: Timbrado CFDI nomina 1.2 via PAC
- US-NM-018: Envio de recibo por WhatsApp al empleado
- US-NM-019: Portal de recibos para empleados (consulta historica)
- US-NM-020: Cancelacion de CFDI de nomina

**Criterios de Aceptacion de la Epica:**
- [ ] PDF de recibo con: datos empresa, datos empleado, percepciones, deducciones, neto
- [ ] Formato profesional con logo de la empresa
- [ ] Timbrado CFDI nomina complemento 1.2 via PAC (Finkok)
- [ ] XML + PDF almacenados en S3 por empleado y periodo
- [ ] Envio automatico por WhatsApp post-dispersion
- [ ] Envio por email como alternativa
- [ ] Portal web simple para que el empleado consulte sus recibos historicos
- [ ] Cancelacion de CFDI con motivos del SAT
- [ ] Acumulado anual por empleado para declaracion
- [ ] Tests >= 98%

**Dependencias:** EP-NM-003 (dispersion)

**Complejidad:** L (5 user stories, integracion SAT)

**Repositorios:** `covacha-payment`, `covacha-notification`

---

### EP-NM-005: Calendario de Pagos y Configuracion

**Descripcion:**
Configuracion del calendario de nomina: periodicidad (quincenal, semanal), dias de pago, y recordatorios automaticos. El sistema calcula las fechas de corte y pago, y avisa al admin cuando se acerca la fecha de dispersion.

**User Stories:**
- US-NM-021: Configurar periodicidad de nomina (semanal, quincenal, mensual)
- US-NM-022: Calendario visual de fechas de pago del ano
- US-NM-023: Recordatorio automatico X dias antes de la fecha de pago
- US-NM-024: Manejo de dias inhabiles (fines de semana, festivos)

**Criterios de Aceptacion de la Epica:**
- [ ] Periodicidad configurable: semanal (viernes), quincenal (1 y 15), mensual (ultimo dia)
- [ ] Calendario anual con todas las fechas de pago
- [ ] Ajuste automatico por dias inhabiles (pagar dia habil anterior)
- [ ] Dias festivos oficiales de Mexico precargados
- [ ] Recordatorio 3 dias antes de cada pago
- [ ] Recordatorio el dia anterior si no se ha calculado la nomina
- [ ] Vista de calendario visual en dashboard
- [ ] Notificacion por email y WhatsApp al admin
- [ ] Historial de nominas pagadas por periodo
- [ ] Tests >= 98%

**Dependencias:** EP-NM-001

**Complejidad:** M (4 user stories)

**Repositorios:** `covacha-core`

---

### EP-NM-006: Multi-Sucursal y Permisos

**Descripcion:**
Soporte para empresas con multiples sucursales, cada una con su propio grupo de empleados y potencialmente diferente periodicidad. Roles y permisos para separar quien captura nomina, quien aprueba, y quien dispersa.

**User Stories:**
- US-NM-025: CRUD de sucursales con empleados asignados
- US-NM-026: Nomina independiente por sucursal
- US-NM-027: Roles: capturista, aprobador, dispersor, visor
- US-NM-028: Permisos por sucursal (ver solo su sucursal)
- US-NM-029: Consolidado multi-sucursal para reportes

**Criterios de Aceptacion de la Epica:**
- [ ] CRUD de sucursales: nombre, direccion, registro patronal
- [ ] Empleados asignados a sucursal
- [ ] Calculo de nomina por sucursal o consolidado
- [ ] Roles: capturista (edita percepciones/deducciones), aprobador (autoriza), dispersor (ejecuta), visor (solo ve)
- [ ] Maker-checker: capturista != aprobador
- [ ] Permisos por sucursal: usuario solo ve empleados de su sucursal
- [ ] Admin ve todas las sucursales
- [ ] Reporte consolidado multi-sucursal
- [ ] Auditoria de acciones por rol y usuario
- [ ] Tests >= 98%

**Dependencias:** EP-NM-001

**Complejidad:** M (5 user stories)

**Repositorios:** `covacha-core`

---

### EP-NM-007: Dashboard y Reportes para Contador

**Descripcion:**
Dashboard de nomina con metricas de costo, historial de pagos, y reportes exportables para el contador. Incluye reportes especificos para IMSS, ISR, e INFONAVIT que el contador necesita para cumplimiento.

**User Stories:**
- US-NM-030: Dashboard: costo de nomina, historial, tendencia
- US-NM-031: Reporte para IMSS (SUA compatible)
- US-NM-032: Reporte de ISR retenido por empleado (acumulado anual)
- US-NM-033: Reporte de INFONAVIT (descuentos aplicados)
- US-NM-034: Export masivo de XMLs de CFDI por periodo

**Criterios de Aceptacion de la Epica:**
- [ ] KPIs: costo total de nomina, promedio por empleado, tendencia mensual
- [ ] Comparativo: nomina actual vs anterior (diferencia)
- [ ] Reporte IMSS: movimientos de alta, baja, modificacion de salario
- [ ] Reporte ISR: retencion acumulada por empleado (tabla anual)
- [ ] Reporte INFONAVIT: descuentos aplicados por empleado
- [ ] Export CSV/Excel compatible con SUA (IMSS)
- [ ] Export masivo de XMLs de CFDI por mes/ano
- [ ] Filtros: periodo, sucursal, empleado
- [ ] PDF de resumen ejecutivo para gerencia
- [ ] Tests >= 98%

**Dependencias:** EP-NM-001 a EP-NM-004

**Complejidad:** M (5 user stories)

**Repositorios:** `mf-nomina`

---

### EP-NM-008: mf-nomina - Micro-Frontend

**Descripcion:**
Micro-frontend Angular para la administracion de nomina. Incluye todas las pantallas: empleados, calculo, dispersion, recibos, calendario, reportes. Se integra con mf-core via Module Federation.

**User Stories:**
- US-NM-035: Scaffold mf-nomina con Module Federation
- US-NM-036: Pantalla de gestion de empleados
- US-NM-037: Pantalla de calculo y dispersion de nomina
- US-NM-038: Pantalla de dashboard y reportes

**Criterios de Aceptacion de la Epica:**
- [ ] mf-nomina registrado en mf-core como micro-frontend
- [ ] Pantalla de empleados: CRUD, importacion, busqueda
- [ ] Pantalla de calculo: pre-nomina con edicion inline, aprobacion, dispersion
- [ ] Pantalla de calendario: visual con proximos pagos
- [ ] Pantalla de recibos: historial con descarga/reenvio
- [ ] Dashboard: costo, tendencia, comparativo
- [ ] Reportes: IMSS, ISR, INFONAVIT con export
- [ ] Responsive design
- [ ] Standalone components, OnPush, Signals
- [ ] Tests >= 98%

**Dependencias:** EP-NM-001 a EP-NM-007

**Complejidad:** L (4 user stories, frontend completo)

**Repositorios:** `mf-nomina`, `mf-core`

---

## User Stories Detalladas

### EP-NM-001: Registro de Empleados

#### US-NM-001: CRUD de empleados
**Como** admin, **quiero** registrar empleados con sus datos personales y fiscales **para que** pueda calcularles nomina.

**Criterios de Aceptacion:**
- [ ] Endpoint CRUD `/payroll/employees`
- [ ] Campos: nombre, RFC, CURP, NSS, fecha_nacimiento, fecha_ingreso, sueldo_base, puesto, departamento
- [ ] Validacion de campos obligatorios
- [ ] Numero de empleado auto-generado
- [ ] Baja de empleado con fecha y motivo

#### US-NM-002: Datos bancarios
**Como** admin, **quiero** registrar la CLABE bancaria de cada empleado **para que** se le deposite su sueldo.

**Criterios de Aceptacion:**
- [ ] CLABE: 18 digitos con validacion de digito verificador
- [ ] Nombre del banco inferido de los primeros 3 digitos
- [ ] Un empleado puede tener 1 CLABE activa
- [ ] Historial de CLABEs anteriores
- [ ] CLABE encriptada en base de datos

#### US-NM-003: Importacion masiva
**Como** admin, **quiero** importar empleados desde CSV **para que** no capture uno por uno.

**Criterios de Aceptacion:**
- [ ] CSV con columnas estandar
- [ ] Template descargable de ejemplo
- [ ] Validacion de cada fila antes de importar
- [ ] Reporte de errores por fila
- [ ] Maximo 500 empleados por import

#### US-NM-004: Validacion RFC y CURP
**Como** sistema, **quiero** validar formato de RFC y CURP **para que** los datos fiscales sean correctos.

**Criterios de Aceptacion:**
- [ ] RFC persona fisica: 4 letras + 6 digitos + 3 homoclave
- [ ] CURP: 18 caracteres alfanumericos con formato valido
- [ ] Validacion del digito verificador de CURP
- [ ] Warning (no bloqueo) si RFC no esta en lista LCO
- [ ] Regex configurable por tipo de validacion

#### US-NM-005: Historial de cambios
**Como** admin, **quiero** ver el historial de cambios de un empleado **para que** tenga auditoria.

**Criterios de Aceptacion:**
- [ ] Registro de cambios: campo, valor_anterior, valor_nuevo, usuario, fecha
- [ ] Cambios trackeados: sueldo, CLABE, puesto, departamento, sucursal
- [ ] Vista cronologica en el perfil del empleado
- [ ] Exportable para auditoria
- [ ] Inmutable: no se pueden editar cambios registrados

### EP-NM-002: Calculo de Nomina

#### US-NM-006: Calculo de sueldo bruto
**Como** admin, **quiero** calcular el sueldo bruto con percepciones extras **para que** refleje lo que gano el empleado.

**Criterios de Aceptacion:**
- [ ] Sueldo base por periodo (quincenal = base mensual / 2)
- [ ] Percepciones extras: horas_extra, bonos, comisiones, retroactivos
- [ ] Horas extra: dobles (primeras 9/semana) y triples (excedentes)
- [ ] Calculo con Decimal para precision
- [ ] Desglose visible en pre-nomina

#### US-NM-007: Deducciones legales
**Como** sistema, **quiero** calcular deducciones legales automaticamente **para que** la empresa cumpla con la ley.

**Criterios de Aceptacion:**
- [ ] ISR: segun tabla quincenal/mensual del SAT (2026)
- [ ] IMSS cuota obrero: enfermedad, invalidez, cesantia, retiro
- [ ] INFONAVIT: porcentaje o cuota fija segun CLABE
- [ ] Subsidio al empleo cuando aplique
- [ ] Tablas actualizables sin cambiar codigo

#### US-NM-008: Deducciones voluntarias
**Como** admin, **quiero** registrar deducciones como prestamos y faltas **para que** se descuenten de la nomina.

**Criterios de Aceptacion:**
- [ ] Tipos: prestamo_empresa, anticipo, caja_ahorro, falta, otro
- [ ] Prestamo: monto total, plazo, cuota por periodo (amortizacion)
- [ ] Falta: dias faltados × sueldo diario
- [ ] Aplicacion automatica cada periodo hasta liquidar prestamo
- [ ] Saldo pendiente de prestamo visible

#### US-NM-009: Pre-nomina
**Como** admin, **quiero** ver un preview del calculo antes de dispersar **para que** pueda verificar y ajustar.

**Criterios de Aceptacion:**
- [ ] Tabla: empleado, sueldo_bruto, percepciones, deducciones, neto
- [ ] Edicion inline de percepciones extras por empleado
- [ ] Totales: suma de sueldos brutos, deducciones, netos
- [ ] Boton "Aprobar" para pasar a dispersion
- [ ] Export de pre-nomina a Excel para revision

#### US-NM-010: Nomina extraordinaria
**Como** admin, **quiero** calcular nominas extraordinarias **para que** pague aguinaldos y finiquitos.

**Criterios de Aceptacion:**
- [ ] Aguinaldo: minimo 15 dias de salario (proporcional si < 1 ano)
- [ ] PTU: segun porcentaje configurado
- [ ] Finiquito: partes proporcionales + indemnizacion si aplica
- [ ] ISR calculado aparte de la nomina regular
- [ ] Tipo de nomina: ORDINARIA, EXTRAORDINARIA marcado en CFDI

### EP-NM-003: Dispersion Masiva SPEI

#### US-NM-011: Generar lote de dispersion
**Como** sistema, **quiero** generar un lote de transferencias desde la nomina aprobada **para que** se pueda ejecutar en batch.

**Criterios de Aceptacion:**
- [ ] Un registro por empleado: CLABE destino, monto neto, concepto, referencia
- [ ] Concepto: "Nomina {periodo} {empresa}"
- [ ] Referencia unica por dispersion
- [ ] Excluir empleados con CLABE invalida (reportar en warnings)
- [ ] Validacion de saldo suficiente para el total

#### US-NM-012: Aprobacion doble autorizacion
**Como** admin, **quiero** que otra persona apruebe la nomina antes de dispersar **para que** haya control.

**Criterios de Aceptacion:**
- [ ] Maker-checker: quien calcula no puede aprobar
- [ ] Flujo: CALCULATED → PENDING_APPROVAL → APPROVED → DISPERSING
- [ ] Aprobador ve resumen: total, #empleados, fecha
- [ ] Aprobacion con confirmacion explicita (ingresar clave)
- [ ] Rechazo con motivo (regresa a pre-nomina)

#### US-NM-013: Ejecutar dispersion masiva
**Como** admin aprobador, **quiero** ejecutar la dispersion con un click **para que** todos los empleados reciban su pago.

**Criterios de Aceptacion:**
- [ ] Dispersion batch via motor SPEI de covacha-payment
- [ ] Procesamiento paralelo con rate limiting
- [ ] Estado global: DISPERSING → COMPLETED → PARTIAL_FAILURE
- [ ] Tiempo estimado de completion mostrado al usuario
- [ ] No permitir doble ejecucion del mismo lote (idempotencia)

#### US-NM-014: Tracking por empleado
**Como** admin, **quiero** ver el estado de cada dispersion **para que** sepa quien ya recibio su pago.

**Criterios de Aceptacion:**
- [ ] Estado por empleado: PENDING, SENT, CONFIRMED, FAILED
- [ ] Confirmacion via webhook SPEI
- [ ] Hora de confirmacion registrada
- [ ] Vista de tabla con filtro por estado
- [ ] Alerta si > 10% de dispersiones fallan

#### US-NM-015: Reintentar dispersiones fallidas
**Como** admin, **quiero** reintentar dispersiones que fallaron **para que** todos los empleados reciban su pago.

**Criterios de Aceptacion:**
- [ ] Boton "Reintentar" por dispersion fallida individual
- [ ] Boton "Reintentar todos los fallidos"
- [ ] Motivo de fallo visible (CLABE invalida, saldo insuficiente, etc.)
- [ ] Opcion de corregir CLABE y reintentar
- [ ] Maximo 3 reintentos por dispersion

### EP-NM-004: Recibos de Nomina y Timbrado CFDI

#### US-NM-016: Recibo de nomina PDF
**Como** empleado, **quiero** recibir mi recibo de nomina en PDF **para que** tenga comprobante de mi pago.

**Criterios de Aceptacion:**
- [ ] PDF con: datos empresa, datos empleado, percepciones, deducciones, neto
- [ ] Desglose detallado de cada concepto
- [ ] Logo de la empresa configurable
- [ ] Periodo de pago y fecha de deposito
- [ ] Almacenado en S3 por empleado y periodo

#### US-NM-017: Timbrado CFDI nomina
**Como** empresa, **quiero** timbrar los recibos de nomina ante el SAT **para que** sean deducibles fiscalmente.

**Criterios de Aceptacion:**
- [ ] CFDI nomina complemento 1.2 (SAT)
- [ ] Timbrado via PAC (Finkok)
- [ ] XML generado con todos los campos requeridos
- [ ] UUID del timbre almacenado
- [ ] Validacion contra esquema XSD antes de timbrar

#### US-NM-018: Envio por WhatsApp
**Como** empleado, **quiero** recibir mi recibo por WhatsApp **para que** lo tenga en mi celular inmediatamente.

**Criterios de Aceptacion:**
- [ ] Envio automatico post-dispersion
- [ ] Mensaje: "Hola {nombre}, tu nomina de {periodo} ha sido depositada. Neto: ${monto}"
- [ ] PDF adjunto como documento
- [ ] Solo enviar si empleado tiene WhatsApp registrado
- [ ] Fallback a email si no hay WhatsApp

#### US-NM-019: Portal de recibos para empleados
**Como** empleado, **quiero** consultar mis recibos anteriores **para que** pueda descargarlos cuando los necesite.

**Criterios de Aceptacion:**
- [ ] URL: nomina.superpago.com.mx/recibos
- [ ] Login con RFC + telefono o email
- [ ] Lista de recibos por periodo
- [ ] Descarga individual de PDF y XML
- [ ] Descarga masiva de todos los recibos del ano

#### US-NM-020: Cancelacion de CFDI
**Como** admin, **quiero** cancelar un CFDI de nomina **para que** pueda corregir errores.

**Criterios de Aceptacion:**
- [ ] Cancelacion ante SAT via PAC
- [ ] Motivos del SAT (01, 02, 03, 04)
- [ ] Sustitucion de CFDI (generar nuevo con correccion)
- [ ] Estado del recibo actualizado a "Cancelado"
- [ ] Notificacion al empleado de cancelacion

### EP-NM-005: Calendario de Pagos

#### US-NM-021: Configurar periodicidad
**Como** admin, **quiero** configurar si pago semanal, quincenal o mensual **para que** la nomina se ajuste a mi empresa.

**Criterios de Aceptacion:**
- [ ] Opciones: semanal (viernes), quincenal (1 y 15), mensual (ultimo dia)
- [ ] Configurable por organizacion
- [ ] Recalculo de fechas al cambiar periodicidad
- [ ] Historial de cambios de configuracion
- [ ] No afectar nominas ya dispersadas

#### US-NM-022: Calendario visual
**Como** admin, **quiero** ver un calendario con todas las fechas de pago **para que** pueda planificar.

**Criterios de Aceptacion:**
- [ ] Vista mensual y anual
- [ ] Fechas de pago marcadas
- [ ] Fechas de corte marcadas (diferente color)
- [ ] Dias inhabiles marcados
- [ ] Indicador de nominas pagadas vs pendientes

#### US-NM-023: Recordatorio automatico
**Como** admin, **quiero** recibir recordatorio antes de la fecha de pago **para que** no se me olvide procesar la nomina.

**Criterios de Aceptacion:**
- [ ] Recordatorio 3 dias antes: "La nomina del {periodo} debe procesarse. Fecha limite: {fecha}"
- [ ] Recordatorio 1 dia antes si no se ha calculado: "URGENTE: La nomina de manana no ha sido calculada"
- [ ] Envio por email y/o WhatsApp
- [ ] Configurable: activar/desactivar, cambiar dias de anticipacion
- [ ] Solo a usuarios con rol de capturista o admin

#### US-NM-024: Manejo de dias inhabiles
**Como** sistema, **quiero** ajustar la fecha de pago cuando cae en dia inhabil **para que** el deposito llegue a tiempo.

**Criterios de Aceptacion:**
- [ ] Dias festivos oficiales de Mexico precargados (2026)
- [ ] Si fecha de pago cae en sabado/domingo: pagar viernes anterior
- [ ] Si cae en festivo: pagar dia habil anterior
- [ ] Dias inhabiles editables por organizacion
- [ ] Calendario muestra la fecha ajustada

### EP-NM-006: Multi-Sucursal y Permisos

#### US-NM-025: CRUD de sucursales
**Como** admin, **quiero** registrar mis sucursales **para que** cada una tenga su nomina independiente.

**Criterios de Aceptacion:**
- [ ] Campos: nombre, direccion, registro patronal IMSS, telefono
- [ ] Empleados asignados a sucursal
- [ ] Un empleado solo puede estar en 1 sucursal
- [ ] Cambio de sucursal registrado en historial
- [ ] Sucursal default para empresas de 1 ubicacion

#### US-NM-026: Nomina por sucursal
**Como** admin, **quiero** procesar nomina por sucursal **para que** cada ubicacion tenga su control.

**Criterios de Aceptacion:**
- [ ] Calculo de nomina filtrable por sucursal
- [ ] Dispersion por sucursal o todas juntas
- [ ] Totales por sucursal en pre-nomina
- [ ] Calendario puede ser diferente por sucursal
- [ ] Aprobador puede ser distinto por sucursal

#### US-NM-027: Roles de nomina
**Como** admin, **quiero** asignar roles especificos de nomina **para que** haya control en el proceso.

**Criterios de Aceptacion:**
- [ ] Capturista: edita percepciones, deducciones, incidencias
- [ ] Aprobador: revisa y autoriza pre-nomina
- [ ] Dispersor: ejecuta la dispersion SPEI
- [ ] Visor: solo puede ver reportes y dashboard
- [ ] Maker-checker obligatorio: capturista != aprobador

#### US-NM-028: Permisos por sucursal
**Como** admin, **quiero** limitar el acceso por sucursal **para que** cada responsable vea solo su equipo.

**Criterios de Aceptacion:**
- [ ] Usuario asociado a 1 o mas sucursales
- [ ] Ve solo empleados de sus sucursales
- [ ] Admin global ve todas las sucursales
- [ ] Permisos evaluados en backend (no solo frontend)
- [ ] Log de accesos por usuario y sucursal

#### US-NM-029: Consolidado multi-sucursal
**Como** admin global, **quiero** ver un reporte consolidado de todas las sucursales **para que** tenga vision general.

**Criterios de Aceptacion:**
- [ ] Reporte con totales por sucursal y total global
- [ ] Comparativo entre sucursales: costo promedio, #empleados
- [ ] Filtro por periodo
- [ ] Export a Excel con tab por sucursal
- [ ] Dashboard consolidado

### EP-NM-007: Dashboard y Reportes para Contador

#### US-NM-030: Dashboard de nomina
**Como** admin, **quiero** un dashboard de costo de nomina **para que** monitoree el gasto.

**Criterios de Aceptacion:**
- [ ] KPIs: costo total, promedio por empleado, diferencia vs periodo anterior
- [ ] Grafica de tendencia mensual
- [ ] Desglose: percepciones vs deducciones
- [ ] Top empleados por costo
- [ ] Filtro por sucursal y periodo

#### US-NM-031: Reporte IMSS
**Como** contador, **quiero** un reporte compatible con SUA **para que** pueda presentar al IMSS.

**Criterios de Aceptacion:**
- [ ] Movimientos afiliatorios: altas, bajas, modificaciones de salario
- [ ] Formato compatible con importacion SUA
- [ ] Datos: NSS, nombre, tipo_movimiento, SBC, fecha
- [ ] Generado por periodo quincenal/mensual
- [ ] Export CSV con formato SUA

#### US-NM-032: Reporte ISR
**Como** contador, **quiero** ver el ISR retenido acumulado **para que** prepare la declaracion anual.

**Criterios de Aceptacion:**
- [ ] ISR retenido por empleado por periodo
- [ ] Acumulado anual por empleado
- [ ] Base gravable, ISR tarifa, subsidio, ISR retenido
- [ ] Formato compatible con declaracion anual
- [ ] Export Excel y PDF

#### US-NM-033: Reporte INFONAVIT
**Como** contador, **quiero** ver los descuentos de INFONAVIT **para que** los concilie.

**Criterios de Aceptacion:**
- [ ] Descuentos por empleado y periodo
- [ ] Tipo: porcentaje, cuota fija, veces salario minimo
- [ ] Acumulado bimestral
- [ ] Export compatible con portal INFONAVIT
- [ ] Alerta si hay empleados con credito no registrado

#### US-NM-034: Export masivo de XMLs
**Como** contador, **quiero** descargar todos los XMLs de un periodo **para que** los suba a mi sistema contable.

**Criterios de Aceptacion:**
- [ ] Descarga en ZIP de todos los XMLs de un mes
- [ ] Organizados por empleado o por fecha
- [ ] Incluir PDFs opcionalmente
- [ ] Filtro por periodo, sucursal
- [ ] Generacion asincrona con notificacion al completar

### EP-NM-008: mf-nomina - Micro-Frontend

#### US-NM-035: Scaffold mf-nomina
**Como** desarrollador, **quiero** crear mf-nomina con Module Federation **para que** se integre con mf-core.

**Criterios de Aceptacion:**
- [ ] Angular standalone con Native Federation
- [ ] Registrado en mf-core
- [ ] Routing: /nomina/* con lazy loading
- [ ] Shared dependencies configuradas
- [ ] Build de produccion funcional

#### US-NM-036: Pantalla de empleados
**Como** admin, **quiero** gestionar empleados desde la interfaz **para que** tenga todo centralizado.

**Criterios de Aceptacion:**
- [ ] Tabla con busqueda, filtros, paginacion
- [ ] Formulario de alta/edicion con validaciones
- [ ] Importacion CSV con drag & drop
- [ ] Detalle de empleado con historial
- [ ] Responsive design

#### US-NM-037: Pantalla de calculo y dispersion
**Como** admin, **quiero** calcular y dispersar nomina desde una pantalla **para que** el proceso sea sencillo.

**Criterios de Aceptacion:**
- [ ] Selector de periodo y tipo de nomina
- [ ] Tabla de pre-nomina con edicion inline
- [ ] Botones de flujo: Calcular → Aprobar → Dispersar
- [ ] Estado de dispersion en tiempo real por empleado
- [ ] Indicador de progreso global

#### US-NM-038: Pantalla de dashboard y reportes
**Como** admin, **quiero** ver metricas y generar reportes **para que** gestione la nomina efectivamente.

**Criterios de Aceptacion:**
- [ ] Dashboard con graficas (costo, tendencia, desglose)
- [ ] Seccion de reportes: IMSS, ISR, INFONAVIT, XMLs
- [ ] Filtros por periodo y sucursal
- [ ] Botones de export PDF/Excel/ZIP
- [ ] Calendario de pagos integrado

---

## Timeline

```
Semana 1-2:   EP-NM-001 (Empleados) + EP-NM-005 (Calendario)
Semana 2-4:   EP-NM-002 (Calculo de nomina)
Semana 3-5:   EP-NM-003 (Dispersion SPEI)
Semana 4-12:  EP-NM-008 (Frontend) - En paralelo con backend
Semana 5-7:   EP-NM-004 (Recibos/CFDI) + EP-NM-006 (Multi-sucursal)
Semana 7-9:   EP-NM-007 (Dashboard/Reportes)
Semana 9-12:  QA + ajustes + tablas fiscales
```

**Equipo**: 2 devs (1 backend/fiscal, 1 frontend)
**Costo estimado**: ~$350K MXN

---

## Dependencias entre Epicas

```
EP-NM-001 (Empleados) ← Base
    |
    ├── EP-NM-002 (Calculo) → depende de EP-NM-001
    │       |
    │       └── EP-NM-003 (Dispersion) → depende de EP-NM-002
    │               |
    │               └── EP-NM-004 (Recibos/CFDI) → depende de EP-NM-003
    |
    ├── EP-NM-005 (Calendario) → depende de EP-NM-001
    ├── EP-NM-006 (Multi-sucursal) → depende de EP-NM-001
    |
    └── EP-NM-007 (Dashboard) → depende de EP-NM-001 a EP-NM-004
            |
            └── EP-NM-008 (Frontend) → depende de todas las APIs
```

**Dependencias externas:**
- covacha-payment: Motor SPEI para dispersiones batch
- PAC (Finkok): Timbrado CFDI nomina
- SAT: Tablas de ISR, reglas de calculo

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|------------|
| Tablas de ISR cambian anualmente | Alta | Alto | Tablas parametrizables, actualizar sin deploy |
| Error en calculo de ISR/IMSS | Media | Critico | Tests extensivos, validacion contra calculadoras del SAT |
| Timbrado CFDI rechazado | Media | Alto | Validar contra XSD antes de timbrar, tests con PAC sandbox |
| Dispersion SPEI fallida masivamente | Baja | Critico | Rate limiting, retry automatico, notificacion inmediata |
| Regulacion laboral cambia (2026) | Media | Medio | Parametros configurables, alertas de actualizacion |
