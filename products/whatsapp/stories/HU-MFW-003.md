## 📖 Historia de Usuario

**Como** desarrollador del sistema  
**Quiero** integrar mf-whatsapp con el pipeline de mensajes de sp-agents  
**Para** aprovechar la infraestructura existente de procesamiento  

---

## 🎯 Criterios de Aceptación

- [ ] **C1.** Los mensajes entrantes de WhatsApp son recibidos por sp_webhook (webhook.superpago.com.mx) y procesados según la configuración existente (identificación de cliente/número, almacenamiento).
- [ ] **C2.** mf-whatsapp consume APIs de listado de conversaciones y mensajes expuestas por mipay_core o sp_webhook (endpoints documentados en CLAUDE.md); no implementa su propio webhook.
- [ ] **C3.** El envío de mensajes desde el MF se realiza contra un endpoint REST definido (ej. POST a `/api/v1/webhook/organization/{id}/send` o equivalente); el adapter del MF llama a ese endpoint con body estándar (número destino, tipo, contenido).
- [ ] **C4.** Cuando exista integración con covacha-botIA (agentes), el flujo “mensaje entrante → agente → respuesta” queda del lado backend; el MF solo muestra mensajes y permite envío manual y configuración de agente (historias posteriores).
- [ ] **C5.** Contrato de API documentado: estructura de request/response para listar conversaciones, listar mensajes, enviar mensaje; tipos TypeScript en `domain/models` alineados con ese contrato.
- [ ] **C6.** Tests de integración (o E2E) opcionales: enviar mensaje desde el MF y verificar que aparece en la lista (o mock del backend).

---

## ⚡ Requisitos No Funcionales

| Categoría | Requisito |
|-----------|-----------|
| **Performance** | Listado de conversaciones < 500ms; envío de mensaje < 1s hasta confirmación optimista |
| **Accesibilidad** | WCAG 2.1 AA; navegación por teclado; labels para screen readers |
| **Seguridad** | Sanitizar contenido de mensajes para prevenir XSS; validar payload antes de POST; no exponer IDs internos de webhook |
| **Observabilidad** | Logs de error en consola con contexto; errores capturados por Sentry |
| **Compatibilidad** | Chrome 90+, Firefox 90+, Safari 15+, Edge 90+ |

---

## 📋 Tareas Técnicas

**Backend (sp_webhook / mipay_core):**
- [ ] Documentar endpoints usados por mf-whatsapp: list conversations, list messages, send message; método, path, headers, body, respuesta.
- [ ] Asegurar que las respuestas incluyan campos necesarios para el MF (id, timestamp, status, direction, type, etc.).

**Frontend (Hexagonal):**
- [ ] En `domain/models/whatsapp.model.ts`: interfaces Conversation, Message, SendMessageRequest, etc., alineadas con API.
- [ ] En `domain/ports/whatsapp.port.ts`: métodos `listConversations(orgId, phoneNumberId?)`, `listMessages(orgId, conversationId, page?)`, `sendMessage(orgId, payload)`.
- [ ] En `infrastructure/adapters/whatsapp.adapter.ts`: implementar port llamando HttpService a los endpoints documentados; mapear respuestas a modelos de dominio.
- [ ] En `application/use-cases/`: use cases que llamen al port (no HttpService directamente); exponer señales de estado (loading, error).
- [ ] Registrar adapter y use cases en entry/DI; usar en páginas de chat.
- [ ] Actualizar CLAUDE.md con URLs base (dev/prod) y resumen del contrato de API.

**Tests:** Ver sección [Plan de Pruebas](#-plan-de-pruebas) para detalle completo.

---

## 🧪 Plan de Pruebas

### Tests Unitarios - Frontend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `should_list_conversations_with_correct_params` | `infrastructure/adapters/whatsapp.adapter.spec.ts` | Adapter llama endpoint con orgId y headers correctos |
| `should_map_api_response_to_domain_model` | `infrastructure/adapters/whatsapp.adapter.spec.ts` | Respuesta API se mapea correctamente a `Conversation[]` |
| `should_send_message_with_correct_payload` | `infrastructure/adapters/whatsapp.adapter.spec.ts` | POST envío incluye conversationId, type, content |
| `should_handle_api_error_gracefully` | `infrastructure/adapters/whatsapp.adapter.spec.ts` | Error 500 se captura y propaga como error de dominio |
| `should_list_messages_with_pagination` | `infrastructure/adapters/whatsapp.adapter.spec.ts` | Paginación envía before/limit correctamente |
| `should_load_conversations_on_init` | `application/use-cases/get-conversations.use-case.spec.ts` | Use case carga conversaciones al inicializar |
| `should_update_state_signals_on_success` | `application/use-cases/get-conversations.use-case.spec.ts` | Señales conversations, loading, error se actualizan |
| `should_set_error_state_on_failure` | `application/use-cases/get-conversations.use-case.spec.ts` | Error en adapter pone error signal y loading false |

### Tests Unitarios - Backend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `test_list_conversations_returns_200` | `tests/unit/controllers/test_whatsapp_controller.py` | GET /conversations retorna lista con formato correcto |
| `test_list_conversations_filters_by_org` | `tests/unit/controllers/test_whatsapp_controller.py` | Conversaciones filtradas por X-SP-Organization-Id |
| `test_send_message_creates_record` | `tests/unit/services/test_whatsapp_message_service.py` | Servicio crea mensaje en DynamoDB y encola en SQS |
| `test_send_message_validates_payload` | `tests/unit/services/test_whatsapp_message_service.py` | Payload inválido retorna 400 con mensaje descriptivo |
| `test_list_messages_with_pagination` | `tests/unit/controllers/test_whatsapp_controller.py` | Paginación con before/limit funciona correctamente |
| `test_send_message_returns_optimistic_response` | `tests/unit/services/test_whatsapp_message_service.py` | Respuesta incluye id y status 'sending' inmediatamente |

### Tests de Integración

| Test | Tipo | Descripción |
|------|------|-------------|
| `should_display_conversations_from_api` | Frontend | Componente chat muestra conversaciones obtenidas del adapter (mock HTTP) |
| `should_send_message_and_show_in_list` | Frontend | Enviar mensaje aparece en lista con status 'enviando' |
| `test_full_message_flow_api_to_db` | Backend | POST /send -> SQS -> procesamiento -> GET /messages incluye mensaje |
| `test_webhook_incoming_message_stored` | Backend | Webhook recibe mensaje -> almacenado en DynamoDB -> listable via API |

### Cobertura Esperada

| Componente | Cobertura mínima |
|-----------|-----------------|
| `WhatsAppAdapter` | ≥ 98% |
| `GetConversationsUseCase` | ≥ 98% |
| `SendMessageUseCase` | ≥ 98% |
| `WhatsAppMessageService` (backend) | ≥ 98% |
| `WhatsAppController` (backend) | ≥ 95% |

---

## 🔗 Dependencias

**Depende de:** HU-MFW-001 (auth/headers).  
**Bloquea a:** HU-MFW-007, HU-MFW-009 (conversaciones y envío en UI).

---

## 📊 Estimación

**Complejidad:** Alta  
**Puntos de Historia:** 5  
**Tiempo estimado:** 3–5 días  

---

## 📝 Notas Técnicas

- Coordinar con equipo de sp_webhook para definir/estabilizar endpoints si aún no existen.
- Considerar versionado de API (`/api/v1/...`) para futuros cambios.

---

## ⚠️ Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Endpoints de sp_webhook no estabilizados o con contrato diferente al esperado | Alta | Alto | Definir contrato API en documento compartido ANTES de implementar adapter; mock responses para desarrollo paralelo |
| Latencia alta en APIs de mensajes por webhook chain | Media | Medio | Implementar loading states claros; timeout configurable; retry con backoff para envío |
| Formato de respuesta diferente entre dev y prod | Baja | Alto | Crear interceptor de validación que alerte discrepancias en desarrollo |

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

`user-story` `epic-1` `backend` `frontend` `priority:high` `size:L`
