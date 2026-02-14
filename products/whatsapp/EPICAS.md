# Epicas - MF-WhatsApp

## Resumen Ejecutivo

| Epica | Historias | Puntos | Duracion Est. | Prioridad |
|-------|-----------|--------|---------------|-----------|
| EP-MFW-001 | 3 (001-003) | 10 pts | 1-2 semanas | Alta |
| EP-MFW-002 | 3 (004-006) | 8 pts | 1-2 semanas | Alta |
| EP-MFW-003 | 4 (007-010) | 19 pts | 2-3 semanas | Alta |
| EP-MFW-004 | 4 (011-014) | 18 pts | 2-3 semanas | Alta |
| EP-MFW-005 | 3 (015-017) | 15 pts | 2-3 semanas | Media |
| EP-MFW-006 | 1 (018) | 13 pts | 2-3 semanas | Media |
| **Total** | **18** | **83 pts** | **10-16 semanas** | |

## Diagrama de Dependencias

```
EP-MFW-001 (Auth + Pipeline)
  HU-001 ──┬──> HU-002 ──┬──> HU-004 (EP-002)
            │             └──> HU-005 (EP-002)
            └──> HU-003 ──┬──> HU-007 (EP-003)
                           └──> HU-009 (EP-003)

EP-MFW-002 (Dashboard)
  HU-004 ──> HU-005 ──> HU-007 (EP-003)
  HU-006 (independiente de EP-003)

EP-MFW-003 (Chat)
  HU-007 ──┬──> HU-008
            ├──> HU-009
            └──> HU-010

EP-MFW-004 (Automatizacion)
  HU-011 ──┬──> HU-012 ──> HU-013
            └──> HU-014

EP-MFW-005 (Analytics)
  HU-015 ──> HU-016
  HU-017 (independiente)

EP-MFW-006 (Privacidad)
  HU-007 (Chat) ──> HU-018 (Conversaciones Privadas)
```

## Ruta Critica

```
HU-001 → HU-003 → HU-007 → HU-009 (path mas largo: 20 pts, 10-14 dias)
```

---

## EP-MFW-001: Integracion con SP-Agents y Autenticacion

**Descripcion:** Integrar mf-whatsapp con la infraestructura existente de sp-agents (Shell mipay_core_frontend), utilizando el sistema de autenticacion SuperPago/BAAT y la gestion multi-tenant.

**Historias:** HU-MFW-001 (2pts), HU-MFW-002 (3pts), HU-MFW-003 (5pts)
**Total:** 10 puntos | **Duracion estimada:** 1-2 semanas

**Entregables clave:**
- SSO con Shell (SharedStateService, covacha:auth, covacha:user)
- Roles y permisos para mf-whatsapp (super_admin vs admin cliente)
- Integracion con pipeline de mensajes (sp_webhook / covacha-botIA)
- Contrato API documentado para conversaciones y mensajes

**KPIs de exito:**
- Autenticacion transparente sin login propio (0 pantallas de login en MF)
- Headers HTTP correctos en 100% de requests
- Roles evaluados en < 10ms (computed signal)
- Cobertura de tests >= 98%

**Riesgos principales:**
- Endpoints de sp_webhook no estabilizados
- Modelo de permisos no alineado con backend

---

## EP-MFW-002: Dashboard Multi-Cliente (Super Admin)

**Descripcion:** Dashboard principal para super administradores: lista de clientes con WhatsApp, indicadores de actividad, navegacion a conversaciones y busqueda global.

**Historias:** HU-MFW-004 (3pts), HU-MFW-005 (2pts), HU-MFW-006 (3pts)
**Total:** 8 puntos | **Duracion estimada:** 1-2 semanas

**Entregables clave:**
- Pagina `presentation/pages/home/` o `clients-dashboard/` con lista de clientes
- Port/Adapter/UseCase para listar clientes con numeros WhatsApp (backend)
- Filtros, conteo de pendientes, estado de numeros
- Busqueda global con debounce y cancelacion de requests

**KPIs de exito:**
- Lista de clientes carga en < 1s para 100 clientes
- Busqueda con debounce 300ms, resultados en < 1s
- Navegacion lista → chat < 500ms
- Solo accesible para super_admin

**Riesgos principales:**
- Endpoint de clientes con WhatsApp no existe en backend
- Backend no soporta busqueda de contenido de mensajes

---

## EP-MFW-003: Interface de Conversaciones WhatsApp Web

**Descripcion:** Interface tipo WhatsApp Web: conversaciones en tiempo real, multiples numeros por cliente, envio manual, historial, soporte multimedia.

**Historias:** HU-MFW-007 (8pts), HU-MFW-008 (3pts), HU-MFW-009 (5pts), HU-MFW-010 (3pts)
**Total:** 19 puntos | **Duracion estimada:** 2-3 semanas

**Entregables clave:**
- Vista chat: lista de conversaciones + panel de mensajes (dos columnas)
- WebSocket o polling para tiempo real con fallback automatico
- Domain: Conversation, Message, Contact; ports para mensajes y conversaciones
- Cambio de numero (selector) y historial paginado con virtual scroll
- Envio de texto y multimedia con optimistic update

**KPIs de exito:**
- Primer render de chat < 2s
- Mensajes nuevos aparecen en < 500ms via WebSocket
- Envio de mensaje < 1s hasta confirmacion optimista
- Carga de historial 50 mensajes < 1s
- Sin memory leaks en real-time (verified con DevTools)

**Riesgos principales:**
- WebSocket no disponible en backend al inicio
- Memory leaks por subscripciones real-time
- Ventana 24h de WhatsApp Business API limita envios
- Scroll position inestable al cargar historial

---

## EP-MFW-004: Sistema de Automatizacion y Bots

**Descripcion:** Integracion con agentes de sp-agents (covacha-botIA) para respuestas automaticas, asignacion de agente por numero, horarios de bot y escalamiento manual.

**Historias:** HU-MFW-011 (5pts), HU-MFW-012 (5pts), HU-MFW-013 (3pts), HU-MFW-014 (5pts)
**Total:** 18 puntos | **Duracion estimada:** 2-3 semanas

**Entregables clave:**
- Port/Adapter para agentes disponibles y asignacion (API covacha-botIA)
- UI de configuracion de respuestas automaticas y horarios con presets
- Toggle "tomar control manual" en conversacion (escalamiento) con optimistic locking
- Configuracion de horarios con timezone IANA y evaluacion en backend

**KPIs de exito:**
- Configuracion de auto-respuesta < 1s para guardar
- Asignacion de agente persiste inmediatamente
- Escalamiento manual < 1s
- Evaluacion de horario correcta al 100% con timezone

**Riesgos principales:**
- API de covacha-botIA no estable
- Conflictos de concurrencia en escalamiento manual
- Desfase de timezone entre servidor y cliente
- Confusion UX entre auto-respuesta y agente IA

---

## EP-MFW-005: Analisis y Reportes de Mensajeria

**Descripcion:** Metricas, dashboards y exportacion: mensajes por periodo, tiempo de respuesta, rendimiento de bots, exportacion para auditoria.

**Historias:** HU-MFW-015 (5pts), HU-MFW-016 (5pts), HU-MFW-017 (5pts)
**Total:** 15 puntos | **Duracion estimada:** 2-3 semanas

**Entregables clave:**
- Domain: Metric, Report; Port/Adapter para analytics (API backend)
- Pagina de metricas y graficos (por cliente/numero) con date range picker
- Reportes de rendimiento de bots (solo super_admin)
- Exportacion de conversaciones (CSV obligatorio, PDF opcional)

**KPIs de exito:**
- Dashboard carga en < 2s
- Endpoint de metricas responde < 500ms
- Exportacion CSV < 5s para 500 mensajes
- Audit log de cada exportacion

**Riesgos principales:**
- Backend sin agregacion de metricas implementada
- Eventos de bot no registrados en backend
- Exportacion de conversaciones largas causa timeout
- Datos sensibles exportados accidentalmente

---

## EP-MFW-006: Conversaciones Privadas y Proteccion de Privacidad

**Descripcion:** Permitir a los usuarios ocultar conversaciones sensibles detras de un codigo PIN privado. Al activar el modo privado, se muestra una conversacion de negocio simulada en lugar de la real. Solo ingresando el PIN correcto se puede ver el contenido real.

**Historias:** HU-MFW-018 (13pts)
**Total:** 13 puntos | **Duracion estimada:** 2-3 semanas

**Entregables clave:**
- Boton discreto para activar modo privado en cualquier conversacion
- Sistema de PIN con hash SHA-256 + salt (nunca texto plano)
- 3+ plantillas de conversaciones de negocio simuladas
- Auto-bloqueo al salir del chat o por inactividad
- Gesto discreto para desbloquear (long-press / triple-tap)
- Sin indicacion visual de que una conversacion esta protegida

**KPIs de exito:**
- Cambio entre modo real y simulado < 200ms
- PIN almacenado con hash, nunca en texto plano
- 0 indicadores visuales de conversacion protegida para observador casual
- Bloqueo automatico 100% confiable al salir o por timeout
- Cobertura de tests >= 98%

**Riesgos principales:**
- UX: que el modo privado sea detectado por un observador atento
- Seguridad: almacenamiento local del PIN podria ser accesible via DevTools
- Conversaciones simuladas poco convincentes
- Auto-bloqueo interfiere con flujo normal de uso

---

## Plan de Sprints Sugerido

### Sprint 1 (Semanas 1-2): Fundamentos
- **EP-MFW-001 completa** (10 pts): Auth + Roles + Pipeline
- HU-MFW-004 de EP-MFW-002 (3 pts): Vista de clientes
- **Total sprint:** 13 pts

### Sprint 2 (Semanas 3-4): Dashboard + Chat Base
- HU-MFW-005, HU-MFW-006 de EP-MFW-002 (5 pts): Navegacion + Busqueda
- HU-MFW-007 de EP-MFW-003 (8 pts): Chat tiempo real
- **Total sprint:** 13 pts

### Sprint 3 (Semanas 5-6): Chat Completo
- HU-MFW-008, HU-MFW-009, HU-MFW-010 de EP-MFW-003 (11 pts): Numeros + Envio + Historial
- **Total sprint:** 11 pts

### Sprint 4 (Semanas 7-9): Automatizacion
- **EP-MFW-004 completa** (18 pts): Auto-respuestas + Agentes + Escalamiento + Horarios
- **Total sprint:** 18 pts

### Sprint 5 (Semanas 10-12): Analytics
- **EP-MFW-005 completa** (15 pts): Metricas + Reportes + Exportacion
- **Total sprint:** 15 pts

### Sprint 6 (Semanas 13-15): Privacidad
- **EP-MFW-006 completa** (13 pts): Conversaciones privadas + PIN + Auto-bloqueo
- **Total sprint:** 13 pts

---

## Metricas de Tests Totales

| Epica | Tests Frontend | Tests Backend | Tests Integracion | Total |
|-------|---------------|---------------|-------------------|-------|
| EP-MFW-001 | 23 | 8 | 10 | 41 |
| EP-MFW-002 | 22 | 9 | 9 | 40 |
| EP-MFW-003 | 45 | 22 | 16 | 83 |
| EP-MFW-004 | 40 | 28 | 17 | 85 |
| EP-MFW-005 | 29 | 23 | 13 | 65 |
| **Total** | **159** | **90** | **65** | **314** |
