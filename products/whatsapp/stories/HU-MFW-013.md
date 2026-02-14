## 📖 Historia de Usuario

**Como** administrador de cliente  
**Quiero** tomar el control manual de una conversación automatizada  
**Para** manejar casos complejos que requieren intervención humana  

---

## 🎯 Criterios de Aceptación

- [ ] **C1.** En la vista de chat, cuando una conversación está siendo atendida por un bot/agente, se muestra un indicador visible (ej. “Bot activo” o “Respondiendo automáticamente”) y un botón o enlace “Tomar control” (escalamiento manual).
- [ ] **C2.** Al hacer clic en “Tomar control”, se envía una señal al backend (ej. POST conversation/{id}/take-over o PATCH conversation/{id} con mode: manual); el backend deja de enviar respuestas del agente para esa conversación y los siguientes mensajes se atienden manualmente (el usuario escribe desde el MF).
- [ ] **C3.** Después de tomar control, el indicador cambia a “Modo manual” o similar; el botón “Tomar control” se oculta o deshabilita; la conversación sigue mostrando el historial completo.
- [ ] **C4.** Opcional: botón “Devolver al bot” para volver a activar el agente en esa conversación; solo si el backend lo soporta.
- [ ] **C5.** Solo usuarios con permiso de atención al cliente (o administrador del cliente) pueden hacer “Tomar control”; si no tiene permiso, el botón no se muestra.
- [ ] **C6.** Si dos usuarios toman control al mismo tiempo, el backend debe definir política (ej. primero que llega gana, o bloqueo optimista); el MF muestra error claro si falla (“Alguien más tomó el control”).
- [ ] **C7.** La transición es inmediata: tras “Tomar control” el usuario puede enviar mensajes manuales de inmediato sin recargar.

---

## ⚡ Requisitos No Funcionales

| Categoría | Requisito |
|-----------|-----------|
| **Performance** | Acción 'Tomar control' ejecuta en < 1s; transición visual inmediata sin reload de página |
| **Accesibilidad** | WCAG 2.1 AA; navegación por teclado; labels para screen readers |
| **Seguridad** | Solo usuarios con permiso de atención pueden escalar; backend valida permisos; no permitir escalamiento de conversaciones de otra organización |
| **Observabilidad** | Logs de error en consola con contexto; errores capturados por Sentry |
| **Compatibilidad** | Chrome 90+, Firefox 90+, Safari 15+, Edge 90+ |

---

## 📋 Tareas Técnicas

**Backend:**
- [ ] Endpoint para tomar control: POST o PATCH conversation/{id} con body { mode: 'manual' } (o takeOver: true); endpoint opcional "devolver al bot" { mode: 'bot' }; persistir en estado de conversación; documentar.
- [ ] Incluir en respuesta de conversación/mensajes un campo `automationMode` o `handledBy` ('bot' | 'human') para que el MF muestre el indicador correcto.

**Frontend (Hexagonal):**
- [ ] `domain/models/conversation.model.ts`: agregar campo automationMode o handledBy a Conversation si no existe.
- [ ] `domain/ports/whatsapp.port.ts` o conversations: takeOver(conversationId), releaseToBot(conversationId)?.
- [ ] Adapter: POST/PATCH a endpoints documentados.
- [ ] `application/use-cases/conversation-control.use-case.ts`: takeOver(conversationId); actualizar estado local de la conversación a manual; manejar error (mensaje para usuario).
- [ ] En componente de chat (header de conversación o barra de herramientas): mostrar badge “Bot activo” cuando handledBy === 'bot'; botón “Tomar control” que llame use case; tras éxito actualizar vista a “Modo manual”.
- [ ] Ocultar “Tomar control” si el usuario no tiene permiso (PermissionService).
- [ ] **Tests:** Ver sección [Plan de Pruebas](#-plan-de-pruebas) para detalle completo.

---

## 🧪 Plan de Pruebas

### Tests Unitarios - Frontend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `should_show_take_control_button_when_bot_active` | `presentation/pages/chat/chat-header.component.spec.ts` | Botón "Tomar control" visible cuando handledBy === 'bot' |
| `should_hide_take_control_when_manual_mode` | `presentation/pages/chat/chat-header.component.spec.ts` | Botón oculto cuando ya en modo manual |
| `should_hide_take_control_without_permission` | `presentation/pages/chat/chat-header.component.spec.ts` | Sin permiso de atención, botón no renderizado |
| `should_call_take_over_on_click` | `application/use-cases/conversation-control.use-case.spec.ts` | takeOver() llama adapter con conversationId |
| `should_update_mode_to_manual_on_success` | `application/use-cases/conversation-control.use-case.spec.ts` | Éxito cambia handledBy a 'human' en signal local |
| `should_show_error_on_concurrent_takeover` | `application/use-cases/conversation-control.use-case.spec.ts` | Error 409 muestra "Otro usuario ya tomó control" |
| `should_send_take_over_request` | `infrastructure/adapters/whatsapp.adapter.spec.ts` | POST/PATCH conversation/{id} con { mode: 'manual' } |
| `should_show_bot_active_badge` | `presentation/pages/chat/chat-header.component.spec.ts` | Badge "Bot activo" visible cuando handledBy === 'bot' |
| `should_show_manual_mode_badge` | `presentation/pages/chat/chat-header.component.spec.ts` | Badge "Modo manual" visible después de tomar control |
| `should_show_return_to_bot_button` | `presentation/pages/chat/chat-header.component.spec.ts` | Botón "Devolver a bot" visible en modo manual (si backend soporta) |

### Tests Unitarios - Backend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `test_take_over_conversation` | `tests/unit/controllers/test_conversation_control_controller.py` | POST takeover cambia modo a 'manual' |
| `test_take_over_requires_permission` | `tests/unit/controllers/test_conversation_control_controller.py` | Sin permiso retorna 403 |
| `test_take_over_concurrent_lock` | `tests/unit/services/test_conversation_control_service.py` | Segundo takeover retorna 409 Conflict |
| `test_release_to_bot` | `tests/unit/services/test_conversation_control_service.py` | Release cambia modo de vuelta a 'bot' |
| `test_take_over_stops_agent_responses` | `tests/unit/services/test_conversation_control_service.py` | Tras takeover, mensajes entrantes no procesados por agente |
| `test_mode_included_in_conversation_response` | `tests/unit/controllers/test_conversation_control_controller.py` | GET conversation incluye campo handledBy |

### Tests de Integración

| Test | Tipo | Descripción |
|------|------|-------------|
| `should_take_control_and_send_manual_message` | Frontend | Click "Tomar control" → badge cambia → enviar mensaje manual funciona |
| `should_return_to_bot_and_verify` | Frontend | Click "Devolver a bot" → badge cambia → indicador actualizado |
| `test_takeover_stops_bot_processing` | Backend | Takeover → mensaje entrante → no procesado por bot → aparece en inbox |
| `test_release_resumes_bot_processing` | Backend | Release → mensaje entrante → bot procesa → respuesta automática |
| `test_concurrent_takeover_handling` | Backend | Dos usuarios simultáneos → primero éxito → segundo 409 |

### Cobertura Esperada

| Componente | Cobertura mínima |
|-----------|-----------------|
| `ConversationControlUseCase` | ≥ 98% |
| `ChatHeaderComponent` (control) | ≥ 98% |
| `WhatsAppAdapter` (takeover) | ≥ 98% |
| `ConversationControlService` (backend) | ≥ 98% |
| `ConversationControlController` (backend) | ≥ 95% |

---

## 🔗 Dependencias

**Depende de:** HU-MFW-007 (vista chat), HU-MFW-012 (agente asignado).  
**Bloquea a:** Ninguna crítica.

---

## 📊 Estimación

**Complejidad:** Media  
**Puntos de Historia:** 3  
**Tiempo estimado:** 2 días  

---

## 📝 Notas Técnicas

- Estado "manual" puede tener timeout (ej. después de 24 h sin respuesta volver a bot); definir en backend.

---

## ⚠️ Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Dos usuarios intentan tomar control simultáneamente | Media | Alto | Backend implementa optimistic locking; MF muestra error claro 'Otro usuario ya tomó control'; retry no automático |
| Estado de conversación (bot/manual) desincronizado entre UI y backend | Media | Medio | Polling ligero cada 30s del estado de conversación; o escuchar evento WebSocket de cambio de modo |
| Usuario toma control y no responde, dejando conversación sin atención | Alta | Alto | Backend implementa timeout configurable (ej. 30min sin respuesta → vuelve a bot); notificación push al usuario si aplica |

---

## ✅ Definición de Hecho (DoD)

- [ ] Código implementado según criterios de aceptación
- [ ] Tests unitarios (coverage ≥ 98% en código nuevo/modificado)
- [ ] Lint limpio (`ng lint` sin errores)
- [ ] Build exitoso (`yarn build:prod`)
- [ ] Sin errores en consola del navegador
- [ ] Documentación actualizada (CLAUDE.md si aplica)
- [ ] PR creado con descripción y linked issue
- [ ] Criterios de aceptación validados manualmente

---

## 🏷️ Labels

`user-story` `epic-4` `backend` `frontend` `priority:high` `size:M`
