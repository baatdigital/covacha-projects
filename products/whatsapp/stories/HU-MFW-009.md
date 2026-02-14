## 📖 Historia de Usuario

**Como** administrador de cliente  
**Quiero** enviar mensajes manuales desde la interface  
**Para** comunicarme directamente con contactos cuando sea necesario  

---

## 🎯 Criterios de Aceptación

- [ ] **C1.** En el panel de mensajes de una conversación hay un área de entrada (input + botón enviar) que permite escribir texto y enviar mensaje al contacto de esa conversación.
- [ ] **C2.** Al enviar: el mensaje aparece inmediatamente en la UI como “enviando” (estado optimista); al confirmar la respuesta del backend se actualiza a “enviado” o “fallido”; si falla, se muestra mensaje de error y opción de reintentar.
- [ ] **C3.** Soporte para envío de archivos (imagen, documento, audio): botón adjuntar abre selector de archivo; se sube el archivo (endpoint upload si aplica) y se envía el mensaje con referencia al media; límites de tamaño según política (ej. 16 MB para imágenes).
- [ ] **C4.** Validación: no enviar mensaje vacío (texto en blanco); para plantillas o mensajes con formato especial, seguir restricciones de WhatsApp Business API (ej. ventana 24 h para mensajes libres).
- [ ] **C5.** El mensaje enviado se añade al listado local y se sincroniza con tiempo real (WebSocket/polling) para que si otro dispositivo/envío lo refleja, no haya duplicados (por id de mensaje).
- [ ] **C6.** Accesibilidad: tecla Enter envía mensaje (opcional Shift+Enter para nueva línea); foco en input después de enviar; label para screen readers.
- [ ] **C7.** Rate limiting: si el backend devuelve 429 o error de límite, mostrar mensaje claro y deshabilitar envío temporalmente o con backoff.

---

## ⚡ Requisitos No Funcionales

| Categoría | Requisito |
|-----------|-----------|
| **Performance** | Envío de mensaje texto < 1s hasta status 'enviando'; upload de archivo < 5s para 5MB; optimistic update inmediato |
| **Accesibilidad** | WCAG 2.1 AA; navegación por teclado; labels para screen readers |
| **Seguridad** | Validar tipo y tamaño de archivo antes de upload; sanitizar contenido de texto contra XSS; rate limit en UI (disable botón 1s post-envío); no exponer URLs de media internas |
| **Observabilidad** | Logs de error en consola con contexto; errores capturados por Sentry |
| **Compatibilidad** | Chrome 90+, Firefox 90+, Safari 15+, Edge 90+ |

---

## 📋 Tareas Técnicas

**Backend:**
- [ ] Endpoint POST para envío de mensaje: body con conversationId o (phoneNumberId + destinationPhone), type (text, image, document, audio), content o mediaId; respuesta con mensaje creado (id, status: sending/sent/failed).
- [ ] Endpoint de upload de media (si aplica): multipart; devolver mediaId para usar en send message.
- [ ] Documentar límites de tamaño y ventana 24 h si aplica.

**Frontend (Hexagonal):**
- [ ] `domain/models/whatsapp.model.ts`: SendMessageRequest (conversationId o to + phoneNumberId, type, content?, mediaId?).
- [ ] `domain/ports/whatsapp.port.ts`: ya debe tener `sendMessage(...)`; extender si hace falta para media.
- [ ] Adapter: POST send message; POST upload si existe; mapear respuesta a Message.
- [ ] `application/use-cases/send-message.use-case.ts`: método sendMessage(payload); actualización optimista en señal de mensajes; en error, revertir o marcar fallido; exponer error para mostrar en UI.
- [ ] Componente de entrada: textarea + botón enviar + botón adjuntar; al enviar llamar use case; deshabilitar si mensaje vacío; manejar Enter/Shift+Enter.
- [ ] Componente o servicio de selección de archivo y upload (si hay endpoint); progreso opcional.
- [ ] Mostrar mensaje “enviando” y luego “enviado”/“fallido”; botón reintentar en fallido.
- [ ] **Tests:** Ver sección [Plan de Pruebas](#-plan-de-pruebas) para detalle completo.

---

## 🧪 Plan de Pruebas

### Tests Unitarios - Frontend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `should_send_text_message` | `application/use-cases/send-message.use-case.spec.ts` | Envío de texto llama adapter con payload correcto |
| `should_add_optimistic_message_on_send` | `application/use-cases/send-message.use-case.spec.ts` | Mensaje aparece inmediatamente con status 'enviando' |
| `should_update_status_on_server_response` | `application/use-cases/send-message.use-case.spec.ts` | Status cambia de 'enviando' a 'enviado' con respuesta del server |
| `should_mark_as_failed_on_error` | `application/use-cases/send-message.use-case.spec.ts` | Error del server marca mensaje como 'fallido' |
| `should_not_send_empty_message` | `application/use-cases/send-message.use-case.spec.ts` | Mensaje vacío/solo espacios no dispara envío |
| `should_prevent_double_send` | `application/use-cases/send-message.use-case.spec.ts` | Botón deshabilitado durante envío activo |
| `should_upload_file_before_sending` | `application/use-cases/send-message.use-case.spec.ts` | Archivo se sube primero, luego se envía mensaje con mediaId |
| `should_validate_file_size_limit` | `application/use-cases/send-message.use-case.spec.ts` | Archivo > 16MB muestra error sin intentar upload |
| `should_render_input_area` | `presentation/components/message-input/message-input.spec.ts` | Textarea + botón enviar + botón adjuntar visibles |
| `should_send_on_enter_key` | `presentation/components/message-input/message-input.spec.ts` | Enter envía; Shift+Enter inserta nueva línea |
| `should_show_retry_on_failed_message` | `presentation/components/message-bubble/message-bubble.spec.ts` | Mensaje fallido muestra botón "Reintentar" |
| `should_show_file_upload_progress` | `presentation/components/message-input/message-input.spec.ts` | Progress bar visible durante upload de archivo |

### Tests Unitarios - Backend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `test_send_text_message_success` | `tests/unit/services/test_send_message_service.py` | POST envía texto, retorna message con id y status sending |
| `test_send_message_validates_empty_content` | `tests/unit/services/test_send_message_service.py` | Contenido vacío retorna 400 |
| `test_send_message_with_media` | `tests/unit/services/test_send_message_service.py` | Envío con mediaId incluye referencia a archivo |
| `test_upload_file_validates_size` | `tests/unit/services/test_file_upload_service.py` | Archivo > 16MB rechazado con error descriptivo |
| `test_upload_file_validates_type` | `tests/unit/services/test_file_upload_service.py` | Solo tipos permitidos (image, document, audio, video) |
| `test_send_message_rate_limit` | `tests/unit/controllers/test_message_controller.py` | Rate limit retorna 429 con retry-after header |
| `test_send_message_idempotency` | `tests/unit/services/test_send_message_service.py` | Mismo idempotency key no crea duplicado |

### Tests de Integración

| Test | Tipo | Descripción |
|------|------|-------------|
| `should_type_and_send_message_optimistically` | Frontend | Escribir → Enter → mensaje aparece como 'enviando' → 'enviado' |
| `should_attach_and_send_file` | Frontend | Seleccionar archivo → upload → envío → preview en chat |
| `should_show_error_and_retry_on_failure` | Frontend | Error de red → mensaje 'fallido' → click retry → reenvío |
| `test_send_message_full_flow` | Backend | POST send → SQS → WhatsApp API mock → status update callback |
| `test_file_upload_to_s3_and_send` | Backend | Upload multipart → S3 → send con mediaId → mensaje con media_url |

### Cobertura Esperada

| Componente | Cobertura mínima |
|-----------|-----------------|
| `SendMessageUseCase` | ≥ 98% |
| `MessageInputComponent` | ≥ 98% |
| `WhatsAppAdapter` (envío) | ≥ 98% |
| `SendMessageService` (backend) | ≥ 98% |
| `FileUploadService` (backend) | ≥ 98% |

---

## 🔗 Dependencias

**Depende de:** HU-MFW-003 (contrato envío), HU-MFW-007 (vista mensajes).  
**Bloquea a:** Ninguna crítica.

---

## 📊 Estimación

**Complejidad:** Media  
**Puntos de Historia:** 5  
**Tiempo estimado:** 3 días  

---

## 📝 Notas Técnicas

- Evitar doble envío (debounce o deshabilitar botón hasta respuesta).
- WhatsApp Cloud API: mensajes fuera de ventana 24 h requieren plantilla aprobada; documentar en UI si aplica.

---

## ⚠️ Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Mensajes duplicados por doble-click o retry automático | Media | Alto | Disable botón durante envío; idempotency key en cada request; deduplicar en lista por messageId |
| Upload de archivos grandes falla por timeout | Media | Medio | Límite de 16MB en UI; progress bar; retry automático una vez; mensaje claro de error con tamaño máximo |
| Ventana de 24h de WhatsApp Business API limita envíos | Alta | Alto | Documentar restricción en UI; backend retorna error específico; mostrar mensaje explicativo y sugerir template |

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

`user-story` `epic-3` `backend` `frontend` `priority:high` `size:L`
