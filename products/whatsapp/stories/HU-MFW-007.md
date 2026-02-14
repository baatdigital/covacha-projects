## 📖 Historia de Usuario

**Como** administrador de cliente  
**Quiero** ver las conversaciones de WhatsApp en tiempo real  
**Para** responder inmediatamente a los mensajes de mis contactos  

---

## 🎯 Criterios de Aceptación

- [ ] **C1.** La vista de chat muestra dos paneles: lista de conversaciones (izquierda) y mensajes de la conversación seleccionada (derecha); layout similar a WhatsApp Web (lista con preview de último mensaje, hora, indicador de no leídos).
- [ ] **C2.** Los mensajes se actualizan en tiempo real: al recibir un mensaje nuevo (vía WebSocket o polling), la lista de conversaciones se actualiza (último mensaje, hora) y el panel de mensajes activo muestra el mensaje nuevo sin recargar la página.
- [ ] **C3.** Indicadores de estado de mensaje: enviado (sent), entregado (delivered), leído (read), fallido (failed); se muestran iconos o texto según tipo de estado.
- [ ] **C4.** Soporte para tipos de mensaje: texto, imagen, audio, video, documento; cada tipo se muestra con preview o icono apropiado; descarga o apertura según tipo (enlaces a archivos si el backend los expone).
- [ ] **C5.** Los mensajes propios (outgoing) se alinean a la derecha; los entrantes (incoming) a la izquierda; diferenciación visual clara (burbujas, color).
- [ ] **C6.** Scroll en el panel de mensajes: al cargar conversación se posiciona al final (mensaje más reciente); opcional: “scroll to bottom” al recibir nuevo mensaje si el usuario ya estaba abajo.
- [ ] **C7.** Conexión en tiempo real: si se usa WebSocket, indicador de estado (conectado/desconectado/reconectando); si falla la conexión, fallback a polling con intervalo razonable (ej. 10–15 s) y reintentos.
- [ ] **C8.** Performance: lista de mensajes virtualizada o paginada si una conversación tiene muchos mensajes (ej. cargar últimos 50 y "cargar más" hacia arriba).

---

## ⚡ Requisitos No Funcionales

| Categoría | Requisito |
|-----------|-----------|
| **Performance** | Primer render de chat < 2s; mensajes nuevos aparecen en < 500ms vía WebSocket; lista virtualizada para > 100 mensajes |
| **Accesibilidad** | WCAG 2.1 AA; navegación por teclado; labels para screen readers |
| **Seguridad** | WebSocket autenticado con token; mensajes sanitizados contra XSS; media URLs validadas antes de renderizar |
| **Observabilidad** | Logs de error en consola con contexto; errores capturados por Sentry |
| **Compatibilidad** | Chrome 90+, Firefox 90+, Safari 15+, Edge 90+ |

---

## 📋 Tareas Técnicas

**Backend:**
- [ ] WebSocket o endpoint de polling para “mensajes nuevos” por conversación o por usuario; documentar contrato (eventos, payload).
- [ ] Endpoints de mensajes y conversaciones con campos status, type, media_url cuando aplique.

**Frontend (Hexagonal):**
- [ ] `domain/models/whatsapp.model.ts`: Message (id, conversationId, direction, type, content, status, timestamp, mediaUrl?, etc.); Conversation (id, contactName, contactPhone, lastMessage?, unreadCount?, etc.).
- [ ] `domain/ports/realtime.port.ts`: opcional `connect()`, `onNewMessage(callback)`, `disconnect()`; o extender whatsapp.port con `pollMessages(conversationId, since)`.
- [ ] `infrastructure/adapters/realtime.adapter.ts`: implementar WebSocket o polling; emitir eventos a use case (Subject/Observable).
- [ ] `application/use-cases/`: GetConversationsUseCase, GetMessagesUseCase; estado para conversaciones, mensajes activos, loading, error; método para suscribirse a nuevos mensajes y actualizar señales.
- [ ] `presentation/pages/chat/`: layout dos columnas; componente lista conversaciones; componente lista mensajes con burbujas por tipo; integración con use cases y realtime.
- [ ] Componentes presentacionales: MessageBubbleComponent (input: message; output: none o click para descargar); ConversationListItemComponent.
- [ ] Virtual scroll o paginación en lista de mensajes; scroll to bottom al cargar y opcionalmente al recibir nuevo mensaje.
- [ ] Indicador de conexión (conectado/desconectado) en UI.

- [ ] **Tests:** Ver sección [Plan de Pruebas](#-plan-de-pruebas) para detalle completo.

---

## 🧪 Plan de Pruebas

### Tests Unitarios - Frontend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `should_connect_websocket_with_auth_token` | `infrastructure/adapters/realtime.adapter.spec.ts` | WebSocket se conecta con token en query/header |
| `should_emit_new_message_on_ws_event` | `infrastructure/adapters/realtime.adapter.spec.ts` | Evento WebSocket emite mensaje a través de Subject |
| `should_fallback_to_polling_on_ws_failure` | `infrastructure/adapters/realtime.adapter.spec.ts` | Si WS falla, inicia polling con intervalo de 10-15s |
| `should_reconnect_websocket_on_disconnect` | `infrastructure/adapters/realtime.adapter.spec.ts` | Desconexión inesperada intenta reconexión con backoff |
| `should_cleanup_subscriptions_on_destroy` | `infrastructure/adapters/realtime.adapter.spec.ts` | takeUntilDestroyed() limpia todas las subscripciones |
| `should_update_conversations_on_new_message` | `application/use-cases/get-conversations.use-case.spec.ts` | Mensaje nuevo actualiza lastMessage y unreadCount en lista |
| `should_add_message_to_active_conversation` | `application/use-cases/get-messages.use-case.spec.ts` | Mensaje entrante se agrega al final de mensajes activos |
| `should_not_duplicate_messages_by_id` | `application/use-cases/get-messages.use-case.spec.ts` | Si mensaje ya existe (mismo id), no se duplica |
| `should_render_incoming_messages_left` | `presentation/components/message-bubble/message-bubble.spec.ts` | Mensajes incoming se alinean a la izquierda |
| `should_render_outgoing_messages_right` | `presentation/components/message-bubble/message-bubble.spec.ts` | Mensajes outgoing se alinean a la derecha |
| `should_show_message_status_icons` | `presentation/components/message-bubble/message-bubble.spec.ts` | Iconos de sent/delivered/read/failed se muestran |
| `should_render_image_preview` | `presentation/components/message-bubble/message-bubble.spec.ts` | Tipo image muestra thumbnail con click para expandir |
| `should_render_document_with_download` | `presentation/components/message-bubble/message-bubble.spec.ts` | Tipo document muestra nombre y botón de descarga |
| `should_show_connection_status_indicator` | `presentation/pages/chat/chat.component.spec.ts` | Indicador conectado/desconectado/reconectando visible |
| `should_scroll_to_bottom_on_load` | `presentation/pages/chat/chat.component.spec.ts` | Al cargar conversación, scroll al final |
| `should_show_conversation_list_with_preview` | `presentation/components/conversation-list/conversation-list.spec.ts` | Lista muestra último mensaje, hora, badge no leídos |

### Tests Unitarios - Backend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `test_websocket_auth_validates_token` | `tests/unit/services/test_websocket_service.py` | Conexión WS rechazada sin token válido |
| `test_websocket_sends_new_message_event` | `tests/unit/services/test_websocket_service.py` | Nuevo mensaje genera evento WS al usuario conectado |
| `test_list_conversations_with_last_message` | `tests/unit/controllers/test_conversations_controller.py` | GET conversaciones incluye lastMessage y unreadCount |
| `test_list_messages_ordered_by_timestamp` | `tests/unit/controllers/test_conversations_controller.py` | Mensajes retornados en orden cronológico |
| `test_message_status_tracking` | `tests/unit/services/test_message_status_service.py` | Status se actualiza: sending → sent → delivered → read |
| `test_multimedia_message_includes_media_url` | `tests/unit/services/test_message_service.py` | Mensaje multimedia incluye media_url en respuesta |

### Tests de Integración

| Test | Tipo | Descripción |
|------|------|-------------|
| `should_receive_message_via_websocket_and_display` | Frontend | Mensaje WS mock → aparece en panel de mensajes sin reload |
| `should_update_conversation_list_on_new_message` | Frontend | Mensaje nuevo → conversación sube al top de lista con preview |
| `should_show_all_message_types_correctly` | Frontend | Renderizar texto, imagen, audio, video, documento correctamente |
| `test_incoming_webhook_to_websocket_flow` | Backend | Webhook recibe → almacena → emite WS → cliente recibe |
| `test_conversation_list_with_real_db` | Backend | Endpoint con DynamoDB local retorna conversaciones con metadata |

### Cobertura Esperada

| Componente | Cobertura mínima |
|-----------|-----------------|
| `RealtimeAdapter` | ≥ 98% |
| `GetConversationsUseCase` | ≥ 98% |
| `GetMessagesUseCase` | ≥ 98% |
| `MessageBubbleComponent` | ≥ 98% |
| `ConversationListComponent` | ≥ 98% |
| `ChatComponent` | ≥ 95% |
| `WebSocketService` (backend) | ≥ 98% |
| `ConversationsController` (backend) | ≥ 95% |

---

## 🔗 Dependencias

**Depende de:** HU-MFW-003 (API mensajes/conversaciones), HU-MFW-005 (navegación a chat por cliente).  
**Bloquea a:** HU-MFW-009 (envío manual), HU-MFW-010 (historial).

---

## 📊 Estimación

**Complejidad:** Alta  
**Puntos de Historia:** 8  
**Tiempo estimado:** 5–7 días  

---

## 📝 Notas Técnicas

- WebSocket requiere endpoint y posiblemente auth (token en query o header); coordinar con backend.
- Considerar límites de rate en polling; preferir WebSocket para producción.

---

## ⚠️ Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| WebSocket no disponible en backend al inicio del desarrollo | Alta | Alto | Implementar polling como fallback funcional; abstraer tras RealtimePort para swap transparente |
| Memory leaks por subscripciones no limpiadas en real-time | Media | Alto | Usar takeUntilDestroyed(); verificar en DevTools; test de ciclo de vida del componente |
| Rendimiento degradado con conversaciones de miles de mensajes | Media | Medio | Virtual scroll (CDK ScrollingModule); cargar máximo 50 mensajes iniciales; paginación hacia arriba |

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

`user-story` `epic-3` `backend` `frontend` `priority:high` `size:XL`
