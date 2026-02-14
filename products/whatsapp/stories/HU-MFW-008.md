## 📖 Historia de Usuario

**Como** administrador de cliente  
**Quiero** cambiar entre diferentes números de WhatsApp de mi cliente  
**Para** gestionar conversaciones desde múltiples líneas de negocio  

---

## 🎯 Criterios de Aceptación

- [ ] **C1.** En la vista de chat (o en el encabezado del cliente) hay un selector desplegable o pestañas que lista todos los números de WhatsApp activos del cliente actual.
- [ ] **C2.** Al cambiar de número seleccionado, la lista de conversaciones y el panel de mensajes se actualizan para mostrar solo las conversaciones de ese número; no se mezclan conversaciones de distintos números.
- [ ] **C3.** El número seleccionado se persiste en la sesión (sessionStorage o query param) para que al recargar o volver a la vista se mantenga la misma selección.
- [ ] **C4.** Cada ítem del selector muestra identificador del número (ej. número enmascarado + nombre si existe, ej. “Ventas +52 55…”) para que el usuario distinga líneas.
- [ ] **C5.** Si el cliente tiene un solo número, el selector puede ocultarse o mostrarse deshabilitado con ese único valor.
- [ ] **C6.** La API de conversaciones acepta un parámetro "phoneNumberId" o "waPhoneId" (o equivalente) para filtrar por número; el adapter y use case lo envían según la selección del usuario.

---

## ⚡ Requisitos No Funcionales

| Categoría | Requisito |
|-----------|-----------|
| **Performance** | Cambio de número recarga conversaciones en < 1s; selector renderiza instantáneamente |
| **Accesibilidad** | WCAG 2.1 AA; navegación por teclado; labels para screen readers |
| **Seguridad** | phoneNumberId validado en backend; usuario solo ve números asignados a su organización |
| **Observabilidad** | Logs de error en consola con contexto; errores capturados por Sentry |
| **Compatibilidad** | Chrome 90+, Firefox 90+, Safari 15+, Edge 90+ |

---

## 📋 Tareas Técnicas

**Backend:**
- [ ] Endpoint para listar números de WhatsApp del cliente (o de la org): id, número enmascarado, nombre/alias, estado; documentar.
- [ ] Endpoints de conversaciones/mensajes que acepten filtro por número (phoneNumberId/waPhoneId).

**Frontend (Hexagonal):**
- [ ] `domain/models/whatsapp.model.ts`: WhatsAppNumber (id, displayName?, maskedPhone, status).
- [ ] `domain/ports/whatsapp.port.ts`: método `listPhoneNumbers(orgId, clientId?)` si no está ya.
- [ ] Adapter: implementar listado de números; conversaciones con query param del número seleccionado.
- [ ] `application/use-cases/`: estado `selectedPhoneNumberId` (signal); método `setSelectedPhoneNumberId(id)`; al cambiar, recargar conversaciones con ese filtro.
- [ ] Componente selector: dropdown o tabs con lista de números; emite (phoneNumberId) al cambiar; se ubica en layout del chat o en header del cliente.
- [ ] Persistencia: al cambiar número guardar en sessionStorage (key por clientId); al iniciar vista leer y aplicar; opcional query param `?phone=id`.
- [ ] **Tests:** Ver sección [Plan de Pruebas](#-plan-de-pruebas) para detalle completo.

---

## 🧪 Plan de Pruebas

### Tests Unitarios - Frontend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `should_list_phone_numbers_for_client` | `infrastructure/adapters/whatsapp.adapter.spec.ts` | Adapter retorna WhatsAppNumber[] para orgId/clientId |
| `should_map_number_with_display_name` | `infrastructure/adapters/whatsapp.adapter.spec.ts` | Número mapeado con displayName y maskedPhone |
| `should_update_selected_number_signal` | `application/use-cases/phone-selector.use-case.spec.ts` | Signal selectedPhoneNumberId se actualiza al cambiar |
| `should_reload_conversations_on_number_change` | `application/use-cases/phone-selector.use-case.spec.ts` | Cambio de número recarga conversaciones con filtro |
| `should_persist_selection_in_session_storage` | `application/use-cases/phone-selector.use-case.spec.ts` | phoneNumberId guardado en sessionStorage por clientId |
| `should_restore_selection_from_session_storage` | `application/use-cases/phone-selector.use-case.spec.ts` | Al iniciar, lee selección previa de sessionStorage |
| `should_render_number_selector_dropdown` | `presentation/components/phone-selector/phone-selector.spec.ts` | Dropdown muestra números con nombre y teléfono masked |
| `should_hide_selector_with_single_number` | `presentation/components/phone-selector/phone-selector.spec.ts` | Con un solo número, selector oculto o deshabilitado |
| `should_emit_selection_change_event` | `presentation/components/phone-selector/phone-selector.spec.ts` | Cambio emite (phoneNumberChanged) con ID correcto |

### Tests Unitarios - Backend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `test_list_phone_numbers_by_org` | `tests/unit/controllers/test_phone_numbers_controller.py` | GET retorna números activos de la organización |
| `test_list_phone_numbers_with_status` | `tests/unit/controllers/test_phone_numbers_controller.py` | Cada número incluye status (active/disconnected) |
| `test_conversations_filtered_by_phone_number` | `tests/unit/controllers/test_conversations_controller.py` | Query param phoneNumberId filtra conversaciones |
| `test_phone_number_belongs_to_org` | `tests/unit/services/test_phone_number_service.py` | Validación: número pertenece a org del usuario |

### Tests de Integración

| Test | Tipo | Descripción |
|------|------|-------------|
| `should_change_number_and_reload_conversations` | Frontend | Seleccionar número → lista de conversaciones se actualiza |
| `should_persist_number_across_navigation` | Frontend | Navegar y volver mantiene número seleccionado |
| `test_conversations_filter_with_db` | Backend | Endpoint con phoneNumberId filtra correctamente en DynamoDB |

### Cobertura Esperada

| Componente | Cobertura mínima |
|-----------|-----------------|
| `PhoneSelectorUseCase` | ≥ 98% |
| `PhoneSelectorComponent` | ≥ 98% |
| `WhatsAppAdapter` (números) | ≥ 98% |
| `PhoneNumberService` (backend) | ≥ 98% |

---

## 🔗 Dependencias

**Depende de:** HU-MFW-007 (vista de conversaciones), backend que exponga números por cliente.  
**Bloquea a:** Ninguna crítica.

---

## 📊 Estimación

**Complejidad:** Media  
**Puntos de Historia:** 3  
**Tiempo estimado:** 2 días  

---

## 📝 Notas Técnicas

- Alinear nombre del parámetro (phoneNumberId, wa_phone_id, etc.) con sp_webhook/mipay_core.

---

## ⚠️ Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Parámetro de filtro por número no consistente entre endpoints | Media | Medio | Estandarizar nombre (phoneNumberId) en contrato API; adapter normaliza si backend usa otro nombre |
| sessionStorage lleno en navegadores con límite bajo | Baja | Bajo | Guardar solo phoneNumberId (string corto); limpiar al cambiar de cliente |

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

`user-story` `epic-3` `frontend` `priority:high` `size:M`
