## 📖 Historia de Usuario

**Como** administrador de cliente  
**Quiero** exportar conversaciones específicas  
**Para** cumplir con requisitos de auditoría o análisis externo  

---

## 🎯 Criterios de Aceptación

- [ ] **C1.** Desde la vista de una conversación (o desde una lista de conversaciones) el usuario tiene la opción “Exportar conversación” (o “Exportar” en el menú de la conversación); al seleccionarla se genera un archivo descargable con el historial de esa conversación.
- [ ] **C2.** Formato de exportación: al menos CSV (fecha, hora, dirección in/out, tipo, contenido o referencia a medio); opcional PDF legible (mensajes en orden cronológico con identificación de remitente).
- [ ] **C3.** El export incluye el rango de fechas de la conversación cargada, o el usuario puede elegir “últimos N días” / “todo el historial” antes de exportar; si “todo” es muy grande, el backend puede limitar (ej. último año) y documentar el límite.
- [ ] **C4.** Solo usuarios con permiso de exportar (o administradores del cliente) ven el botón de exportar; en caso contrario no se muestra.
- [ ] **C5.** La generación puede ser asíncrona si el historial es grande: mostrar “Preparando exportación…” y al final “Descargar” o descarga automática cuando el backend devuelva el archivo (o URL firmada); para conversaciones pequeñas puede ser síncrono.
- [ ] **C6.** No se exportan datos sensibles que no deban salir del sistema (ej. tokens); solo contenido de mensajes, fechas, tipos y direcciones permitidos por política.
- [ ] **C7.** Mensaje de error claro si falla la exportación (permisos, tamaño, error de servidor).

---

## ⚡ Requisitos No Funcionales

| Categoría | Requisito |
|-----------|-----------|
| **Performance** | Exportación CSV de conversación típica (500 msgs) < 5s; PDF < 10s; descarga inicia automáticamente |
| **Accesibilidad** | WCAG 2.1 AA; navegación por teclado; labels para screen readers |
| **Seguridad** | No incluir tokens, IDs internos ni metadata de sistema en exportación; respetar política de retención de datos; solo usuarios con permiso export; audit log de exportaciones |
| **Observabilidad** | Logs de error en consola con contexto; errores capturados por Sentry |
| **Compatibilidad** | Chrome 90+, Firefox 90+, Safari 15+, Edge 90+ |

---

## 📋 Tareas Técnicas

**Backend:**
- [ ] Endpoint de exportación: POST o GET con conversationId, format (csv | pdf), dateFrom?, dateTo? (opcional); respuesta: archivo (attachment) o URL temporal para descargar; si es pesado, job en background y webhook/email o polling con jobId; documentar.
- [ ] Generación CSV: columnas fecha, hora, dirección, tipo, contenido; escape correcto de comillas y saltos de línea.
- [ ] Opcional PDF: plantilla con mensajes ordenados; librería en backend (ej. ReportLab, WeasyPrint).

**Frontend (Hexagonal):**
- [ ] `domain/ports/export.port.ts`: exportConversation(conversationId, options: { format, dateFrom?, dateTo? }) → Observable<Blob | { downloadUrl }>.
- [ ] `infrastructure/adapters/export.adapter.ts`: llamar endpoint; si es blob, crear link de descarga; si es URL, abrir en nueva pestaña o descargar con fetch.
- [ ] `application/use-cases/export-conversation.use-case.ts`: export(conversationId, options); estado loading, error; al recibir blob/URL disparar descarga y mostrar toast “Exportación lista”.
- [ ] En componente de chat (menú o botón): “Exportar conversación”; opcional modal con formato (CSV/PDF) y rango; al confirmar llamar use case; mostrar “Preparando…” y luego “Descargar” o descarga automática.
- [ ] Ocultar opción si el usuario no tiene permiso de exportación.
- [ ] **Tests:** Ver sección [Plan de Pruebas](#-plan-de-pruebas) para detalle completo.

---

## 🧪 Plan de Pruebas

### Tests Unitarios - Frontend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `should_request_csv_export` | `infrastructure/adapters/export.adapter.spec.ts` | POST/GET export con format=csv retorna Blob |
| `should_request_pdf_export` | `infrastructure/adapters/export.adapter.spec.ts` | POST/GET export con format=pdf retorna Blob o downloadUrl |
| `should_trigger_file_download` | `application/use-cases/export-conversation.use-case.spec.ts` | Blob recibido → download link creado y clickeado |
| `should_show_loading_during_export` | `application/use-cases/export-conversation.use-case.spec.ts` | Estado loading true durante generación |
| `should_handle_export_error` | `application/use-cases/export-conversation.use-case.spec.ts` | Error → loading false, error signal con mensaje |
| `should_show_export_button_in_chat` | `presentation/pages/chat/chat.component.spec.ts` | Botón "Exportar conversación" visible en menú |
| `should_hide_export_without_permission` | `presentation/pages/chat/chat.component.spec.ts` | Sin permiso export, botón no renderizado |
| `should_show_export_modal_with_options` | `presentation/components/export-modal/export-modal.spec.ts` | Modal con formato (CSV/PDF), rango de fechas, confirmar |
| `should_show_preparing_state` | `presentation/components/export-modal/export-modal.spec.ts` | "Preparando exportación..." durante generación |
| `should_show_download_ready_state` | `presentation/components/export-modal/export-modal.spec.ts` | "Descargar" cuando archivo listo |

### Tests Unitarios - Backend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `test_export_csv_format` | `tests/unit/services/test_export_service.py` | CSV generado con columnas: fecha, hora, dirección, tipo, contenido |
| `test_export_csv_escapes_special_chars` | `tests/unit/services/test_export_service.py` | Comillas, saltos de línea y comas escapados correctamente |
| `test_export_filters_by_date_range` | `tests/unit/services/test_export_service.py` | Solo mensajes dentro del rango incluidos |
| `test_export_excludes_sensitive_data` | `tests/unit/services/test_export_service.py` | No incluye tokens, IDs internos ni metadata de sistema |
| `test_export_requires_permission` | `tests/unit/controllers/test_export_controller.py` | Sin permiso retorna 403 |
| `test_export_validates_conversation_access` | `tests/unit/controllers/test_export_controller.py` | Conversación de otra org retorna 403 |
| `test_export_large_conversation_async` | `tests/unit/services/test_export_service.py` | > 1000 mensajes → generación async → retorna jobId |
| `test_export_pdf_format` | `tests/unit/services/test_export_service.py` | PDF generado con mensajes cronológicos y formato legible |
| `test_export_audit_log` | `tests/unit/services/test_export_service.py` | Cada exportación registra audit log (userId, conversationId, timestamp) |

### Tests de Integración

| Test | Tipo | Descripción |
|------|------|-------------|
| `should_export_csv_and_download` | Frontend | Click exportar → CSV → modal muestra progreso → descarga automática |
| `should_show_error_on_export_failure` | Frontend | Error en backend → modal muestra error → retry disponible |
| `test_csv_export_end_to_end` | Backend | Conversación con mensajes → POST export → CSV válido con todos los mensajes |
| `test_async_export_large_conversation` | Backend | Conversación 5000 msgs → POST → jobId → polling → S3 URL → descarga |
| `test_audit_log_on_export` | Backend | Exportar → audit log registrado con detalles correctos |

### Cobertura Esperada

| Componente | Cobertura mínima |
|-----------|-----------------|
| `ExportAdapter` | ≥ 98% |
| `ExportConversationUseCase` | ≥ 98% |
| `ExportModalComponent` | ≥ 98% |
| `ExportService` (backend) | ≥ 98% |
| `ExportController` (backend) | ≥ 95% |

---

## 🔗 Dependencias

**Depende de:** HU-MFW-007 (vista conversación), HU-MFW-010 (historial disponible en backend).  
**Bloquea a:** Ninguna.

---

## 📊 Estimación

**Complejidad:** Media  
**Puntos de Historia:** 5  
**Tiempo estimado:** 3–4 días  

---

## 📝 Notas Técnicas

- Considerar límites de tamaño (ej. 10 MB) y timeout; para conversaciones muy largas, export asíncrono con notificación.

---

## ⚠️ Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Exportación de conversación muy larga (10,000+ mensajes) causa timeout | Media | Alto | Backend genera export asíncronamente (job + S3 + URL temporal); MF muestra 'Preparando exportación...' con polling de estado; límite de 1 año de historial |
| Formato PDF costoso de generar en backend | Media | Medio | Para MVP, solo CSV; PDF como mejora futura (o generación frontend con jsPDF para conversaciones cortas) |
| Datos sensibles exportados accidentalmente | Baja | Alto | Backend filtra campos sensibles; no incluir IDs de sistema, tokens, ni metadata interna; solo: fecha, hora, dirección, tipo, contenido |

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

`user-story` `epic-5` `backend` `frontend` `priority:medium` `size:L`
