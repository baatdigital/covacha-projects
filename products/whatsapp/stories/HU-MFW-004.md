## 📖 Historia de Usuario

**Como** super administrador  
**Quiero** ver una lista consolidada de todos mis clientes con WhatsApp  
**Para** tener una visión general del estado de las conversaciones  

---

## 🎯 Criterios de Aceptación

- [ ] **C1.** Se muestra una lista de clientes que tienen al menos un número de WhatsApp configurado y activo; los datos provienen del backend (mipay_core/sp_webhook) filtrados por organización actual.
- [ ] **C2.** Cada ítem de la lista muestra: nombre del cliente, cantidad de números de WhatsApp activos, indicador de actividad reciente (ej. última interacción en últimas 24 h), conteo de mensajes pendientes (sin leer) si el backend lo expone.
- [ ] **C3.** La lista es filtrable por nombre de cliente (búsqueda en frontend o vía parámetro de API); se mantiene filtro en estado (signal o query params) para no perderlo al recargar.
- [ ] **C4.** Indicadores de estado de números: activo/desconectado/error si el backend los provee; en caso contrario mostrar solo “activo” cuando hay al menos un número.
- [ ] **C5.** La vista está disponible solo para usuarios con rol super_admin o permiso equivalente (usar PermissionService de HU-MFW-002).
- [ ] **C6.** Diseño responsive; lista usable en tablet y desktop; carga con skeleton o spinner mientras se obtienen datos.
- [ ] **C7.** Si no hay clientes con WhatsApp, se muestra mensaje claro y CTA para configurar (enlace a configuración o mensaje informativo).

---

## ⚡ Requisitos No Funcionales

| Categoría | Requisito |
|-----------|-----------|
| **Performance** | Lista de clientes carga en < 1s para hasta 100 clientes; paginación si > 100 |
| **Accesibilidad** | WCAG 2.1 AA; navegación por teclado; labels para screen readers |
| **Seguridad** | Solo super_admin puede listar todos los clientes; backend valida rol en endpoint |
| **Observabilidad** | Logs de error en consola con contexto; errores capturados por Sentry |
| **Compatibilidad** | Chrome 90+, Firefox 90+, Safari 15+, Edge 90+ |

---

## 📋 Tareas Técnicas

**Backend:**
- [ ] Endpoint (o uso de existente) para listar “clientes con WhatsApp” de la organización: id, nombre, lista de números (o resumen), último mensaje/actividad, pendientes; documentar en CLAUDE.md.

**Frontend (Hexagonal):**
- [ ] `domain/models/client-summary.model.ts`: interfaz ClientSummary (id, name, phoneNumbers[], lastActivityAt?, pendingCount?, status?).
- [ ] `domain/ports/clients.port.ts`: método `listClientsWithWhatsApp(orgId, filters?)` retornando Observable/List.
- [ ] `infrastructure/adapters/clients.adapter.ts`: implementar port; llamar HttpService al endpoint documentado.
- [ ] `application/use-cases/list-clients.use-case.ts`: estado (señales) clients, loading, error; método loadClients() que use adapter y SharedState para orgId.
- [ ] `presentation/pages/clients-dashboard/` (o home con modo super_admin): página que use ListClientsUseCase; tabla o cards con filtro por nombre; indicadores según criterios.
- [ ] Ruta en `remote-entry/entry.routes.ts` (ej. `clients` o ``); guard o condicional para super_admin.
- [ ] Registrar port/adapter/use case en entry; path aliases en imports.

**Tests:** Ver sección [Plan de Pruebas](#-plan-de-pruebas) para detalle completo.

---

## 🧪 Plan de Pruebas

### Tests Unitarios - Frontend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `should_list_clients_with_whatsapp_numbers` | `infrastructure/adapters/clients.adapter.spec.ts` | Adapter llama endpoint correcto y mapea ClientSummary[] |
| `should_handle_empty_client_list` | `infrastructure/adapters/clients.adapter.spec.ts` | Lista vacía retorna array vacío sin error |
| `should_load_clients_and_update_signals` | `application/use-cases/list-clients.use-case.spec.ts` | Use case actualiza signals clients, loading, error |
| `should_filter_clients_by_name` | `application/use-cases/list-clients.use-case.spec.ts` | Filtro por nombre funciona en señal computada |
| `should_render_client_cards_with_indicators` | `presentation/pages/clients-dashboard/clients-dashboard.spec.ts` | Componente renderiza tarjetas con nombre, números, actividad |
| `should_show_empty_state_when_no_clients` | `presentation/pages/clients-dashboard/clients-dashboard.spec.ts` | Sin clientes muestra mensaje y CTA |
| `should_show_skeleton_while_loading` | `presentation/pages/clients-dashboard/clients-dashboard.spec.ts` | Loading muestra skeleton loader |
| `should_not_render_for_non_super_admin` | `presentation/pages/clients-dashboard/clients-dashboard.spec.ts` | Componente no se muestra si usuario no es super_admin |

### Tests Unitarios - Backend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `test_list_clients_with_whatsapp_returns_summary` | `tests/unit/controllers/test_clients_whatsapp_controller.py` | Endpoint retorna clientes con números WA activos |
| `test_list_clients_filters_by_organization` | `tests/unit/controllers/test_clients_whatsapp_controller.py` | Solo clientes de la org del header |
| `test_list_clients_requires_super_admin` | `tests/unit/controllers/test_clients_whatsapp_controller.py` | Retorna 403 si no es super_admin |
| `test_list_clients_includes_activity_indicators` | `tests/unit/services/test_client_whatsapp_service.py` | Incluye lastActivityAt, pendingCount, phoneNumbers |

### Tests de Integración

| Test | Tipo | Descripción |
|------|------|-------------|
| `should_load_and_display_clients_from_api` | Frontend | Componente carga clientes vía adapter mock y renderiza lista |
| `should_filter_clients_in_real_time` | Frontend | Escribir en buscador filtra lista sin nueva request |
| `test_clients_endpoint_with_real_db` | Backend | Endpoint con DynamoDB local retorna clientes correctamente |

### Cobertura Esperada

| Componente | Cobertura mínima |
|-----------|-----------------|
| `ClientsAdapter` | ≥ 98% |
| `ListClientsUseCase` | ≥ 98% |
| `ClientsDashboardComponent` | ≥ 98% |
| `ClientWhatsAppService` (backend) | ≥ 98% |

---

## 🔗 Dependencias

**Depende de:** HU-MFW-001, HU-MFW-002 (auth y roles).  
**Bloquea a:** HU-MFW-005 (navegación a conversaciones desde cliente).

---

## 📊 Estimación

**Complejidad:** Media  
**Puntos de Historia:** 3  
**Tiempo estimado:** 2–3 días  

---

## 📝 Notas Técnicas

- Reutilizar diseño de listas de otros MFs (mf-marketing, mf-ia) para consistencia.
- Considerar paginación si el número de clientes es grande.

---

## ⚠️ Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Endpoint de clientes con WhatsApp no existe en backend | Media | Alto | Verificar con equipo mipay_core; preparar endpoint stub si no existe; documentar contrato |
| Diseño no consistente con otros MFs del ecosistema | Baja | Medio | Reutilizar componentes de diseño existentes (css-design-system.mdc); revisar mf-marketing como referencia |

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

`user-story` `epic-2` `backend` `frontend` `priority:high` `size:M`
