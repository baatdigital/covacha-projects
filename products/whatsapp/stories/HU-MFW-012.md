## 📖 Historia de Usuario

**Como** super administrador  
**Quiero** asignar agentes inteligentes específicos a números de WhatsApp  
**Para** automatizar flujos de conversación complejos  

---

## 🎯 Criterios de Aceptación

- [ ] **C1.** En la configuración de automatización (o en una sección “Agente IA”) el super administrador ve una lista de agentes disponibles provenientes de sp-agents/covacha-botIA (GET agentes por organización).
- [ ] **C2.** El usuario puede seleccionar un agente de la lista y asignarlo a un número de WhatsApp; la asignación se guarda en backend (relación phoneNumberId ↔ agentId); solo un agente por número (o política definida).
- [ ] **C3.** Cuando hay un agente asignado y la automatización está activa, los mensajes entrantes a ese número son procesados por el agente (backend); el MF no implementa la lógica del agente, solo la asignación.
- [ ] **C4.** La lista de agentes muestra nombre, descripción corta (si existe) y estado (activo/inactivo); se filtra por organización actual.
- [ ] **C5.** Al desasignar (seleccionar “Ninguno” o quitar asignación) el número deja de usar el agente; los mensajes pasan a manual o a respuesta simple si está configurada (HU-MFW-011).
- [ ] **C6.** Solo super_admin (o rol con permiso específico) puede asignar/cambiar agentes; administrador de cliente puede ver qué agente está asignado pero no cambiarlo (o según regla de negocio).
- [ ] **C7.** Documentación en CLAUDE.md: endpoints de covacha-botIA usados (list agents, assign agent to phone).

---

## ⚡ Requisitos No Funcionales

| Categoría | Requisito |
|-----------|-----------|
| **Performance** | Lista de agentes carga en < 1s; asignación guardada en < 500ms |
| **Accesibilidad** | WCAG 2.1 AA; navegación por teclado; labels para screen readers |
| **Seguridad** | Solo super_admin puede asignar agentes; agentId validado contra lista de agentes de la org; no permitir asignación cross-org |
| **Observabilidad** | Logs de error en consola con contexto; errores capturados por Sentry |
| **Compatibilidad** | Chrome 90+, Firefox 90+, Safari 15+, Edge 90+ |

---

## 📋 Tareas Técnicas

**Backend (covacha-botIA / mipay_core):**
- [ ] API para listar agentes de la organización (existente en covacha-botIA); endpoint para asignar agente a número (o guardar en tabla de configuración por phoneNumberId); documentar.

**Frontend (Hexagonal):**
- [ ] `domain/models/agent.model.ts`: Agent (id, name, description?, status); Assignment (phoneNumberId, agentId?).
- [ ] `domain/ports/agents.port.ts`: listAgents(orgId), getAssignment(orgId, phoneNumberId), setAssignment(orgId, phoneNumberId, agentId | null).
- [ ] `infrastructure/adapters/agents.adapter.ts`: GET agentes; GET/PUT asignación; base URL según env (covacha-botIA).
- [ ] `application/use-cases/agent-assignment.use-case.ts`: estado agents[], currentAssignment, loading, error; loadAgents(), loadAssignment(phoneNumberId), assign(phoneNumberId, agentId).
- [ ] UI: en página/section automatización: dropdown o lista de agentes; selector “Agente asignado” con opción “Ninguno”; guardar al cambiar; solo editable para super_admin (PermissionService).
- [ ] Mostrar en configuración “Agente actual: {nombre}” cuando hay asignación.
- [ ] **Tests:** Ver sección [Plan de Pruebas](#-plan-de-pruebas) para detalle completo.

---

## 🧪 Plan de Pruebas

### Tests Unitarios - Frontend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `should_list_available_agents` | `infrastructure/adapters/agents.adapter.spec.ts` | GET retorna Agent[] con id, name, description, status |
| `should_get_current_assignment` | `infrastructure/adapters/agents.adapter.spec.ts` | GET assignment retorna agentId o null por phoneNumberId |
| `should_set_agent_assignment` | `infrastructure/adapters/agents.adapter.spec.ts` | PUT assignment envía phoneNumberId + agentId |
| `should_clear_agent_assignment` | `infrastructure/adapters/agents.adapter.spec.ts` | PUT assignment con agentId null desasigna agente |
| `should_load_agents_and_assignment` | `application/use-cases/agent-assignment.use-case.spec.ts` | Use case carga lista de agentes y asignación actual |
| `should_assign_agent_and_update_state` | `application/use-cases/agent-assignment.use-case.spec.ts` | Asignar agente actualiza signal currentAssignment |
| `should_render_agent_dropdown` | `presentation/pages/automation/agent-selector.component.spec.ts` | Dropdown muestra agentes disponibles con nombre y status |
| `should_show_none_option` | `presentation/pages/automation/agent-selector.component.spec.ts` | Opción "Ninguno" disponible para desasignar |
| `should_disable_for_non_super_admin` | `presentation/pages/automation/agent-selector.component.spec.ts` | Selector deshabilitado si usuario no es super_admin |
| `should_show_current_agent_name` | `presentation/pages/automation/agent-selector.component.spec.ts` | Muestra "Agente actual: {name}" cuando asignado |

### Tests Unitarios - Backend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `test_list_agents_by_org` | `tests/unit/controllers/test_agents_controller.py` | GET retorna agentes activos de la organización |
| `test_assign_agent_to_phone_number` | `tests/unit/services/test_agent_assignment_service.py` | Asignación se persiste correctamente |
| `test_unassign_agent` | `tests/unit/services/test_agent_assignment_service.py` | Desasignación pone agentId null |
| `test_assign_validates_agent_belongs_to_org` | `tests/unit/services/test_agent_assignment_service.py` | No permite asignar agente de otra organización |
| `test_assign_requires_super_admin` | `tests/unit/controllers/test_agents_controller.py` | PUT assignment requiere super_admin, 403 si no |
| `test_agent_processes_message_when_assigned` | `tests/unit/services/test_agent_message_service.py` | Mensaje entrante a número con agente → agente procesa |

### Tests de Integración

| Test | Tipo | Descripción |
|------|------|-------------|
| `should_load_agents_select_and_save_assignment` | Frontend | Lista agentes → seleccionar → guardar → UI actualizada |
| `should_unassign_agent_and_update` | Frontend | Seleccionar "Ninguno" → guardar → asignación removida |
| `test_agent_assignment_flow` | Backend | Asignar agente → mensaje entrante → agente procesa → respuesta enviada |
| `test_unassign_stops_agent_processing` | Backend | Desasignar → mensaje entrante → no procesado por agente |

### Cobertura Esperada

| Componente | Cobertura mínima |
|-----------|-----------------|
| `AgentsAdapter` | ≥ 98% |
| `AgentAssignmentUseCase` | ≥ 98% |
| `AgentSelectorComponent` | ≥ 98% |
| `AgentAssignmentService` (backend) | ≥ 98% |
| `AgentsController` (backend) | ≥ 95% |

---

## 🔗 Dependencias

**Depende de:** HU-MFW-011 (configuración automatización), API covacha-botIA.  
**Bloquea a:** HU-MFW-013 (escalamiento manual puede depender de saber si hay agente activo).

---

## 📊 Estimación

**Complejidad:** Alta  
**Puntos de Historia:** 5  
**Tiempo estimado:** 3–4 días  

---

## 📝 Notas Técnicas

- Coordinar con equipo covacha-botIA para contrato de "assign agent to phone number".

---

## ⚠️ Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| API de covacha-botIA para listar/asignar agentes no estable | Alta | Alto | Definir contrato mínimo (GET /agents, PUT /assignment); desarrollar con mock adapter; coordinar con equipo botIA semanalmente |
| Asignación de agente no reflejada inmediatamente en procesamiento de mensajes | Media | Alto | Backend debe invalidar cache de asignación al cambiar; MF muestra warning 'Cambios pueden tardar hasta 1 minuto en aplicar' |
| Confusión entre 'sin agente' y 'auto-respuesta simple' (HU-MFW-011) | Media | Medio | UI clara: sección separada para auto-respuesta vs agente IA; tooltip explicando diferencia; no permitir ambos activos simultáneamente |

---

## ✅ Definición de Hecho (DoD)

- [ ] Código implementado según criterios de aceptación
- [ ] Tests unitarios (coverage >= 98% en código nuevo/modificado)
- [ ] Lint limpio (`ng lint` sin errores)
- [ ] Build exitoso (`yarn build:prod`)
- [ ] Sin errores en consola del navegador
- [ ] Documentación actualizada (CLAUDE.md si aplica)
- [ ] PR creado con descripción y linked issue
- [ ] Criterios de aceptación validados manualmente

---

## 🏷️ Labels

`user-story` `epic-4` `backend` `frontend` `priority:high` `size:L`
