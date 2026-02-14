## 📖 Historia de Usuario

**Como** super administrador  
**Quiero** buscar conversaciones entre todos los clientes  
**Para** encontrar rápidamente mensajes específicos o contactos  

---

## 🎯 Criterios de Aceptación

- [ ] **C1.** Existe un campo de búsqueda global (en dashboard de clientes o en barra superior) que permite buscar por: número de teléfono del contacto, nombre de contacto, o texto contenido en mensajes (si el backend lo soporta).
- [ ] **C2.** La búsqueda puede restringirse a un cliente o “todos los clientes” (solo super_admin); filtro por cliente opcional junto al campo de texto.
- [ ] **C3.** Los resultados se muestran como lista de conversaciones (o mensajes) que coinciden; cada ítem muestra cliente, número/nombre de contacto, preview del mensaje y permite abrir esa conversación.
- [ ] **C4.** Búsqueda con debounce (ej. 300–400 ms) para no disparar una petición por cada tecla; máximo una petición activa a la vez (cancelar anterior si hay nueva búsqueda).
- [ ] **C5.** Si el backend no soporta búsqueda por contenido de mensajes, al menos búsqueda por número de teléfono y/o nombre de contacto; documentar limitaciones.
- [ ] **C6.** Estado vacío: “Sin resultados” cuando la búsqueda no devuelve nada; estado de carga mientras se busca.
- [ ] **C7.** Opcional: persistir última búsqueda en sessionStorage o query params para no perderla al navegar.

---

## ⚡ Requisitos No Funcionales

| Categoría | Requisito |
|-----------|-----------|
| **Performance** | Búsqueda con debounce 300ms; resultados en < 1s; máximo 1 request activo (cancelar previo) |
| **Accesibilidad** | WCAG 2.1 AA; navegación por teclado; labels para screen readers |
| **Seguridad** | Sanitizar input de búsqueda contra XSS e inyección; limitar longitud de query a 200 chars |
| **Observabilidad** | Logs de error en consola con contexto; errores capturados por Sentry |
| **Compatibilidad** | Chrome 90+, Firefox 90+, Safari 15+, Edge 90+ |

---

## 📋 Tareas Técnicas

**Backend:**
- [ ] Endpoint de búsqueda global: query param `q`, opcional `clientId`; respuesta lista de conversaciones o mensajes que coinciden; documentar en CLAUDE.md.
- [ ] Si no hay endpoint: búsqueda en frontend sobre lista ya cargada (solo por nombre/número de contacto) y documentar limitación.

**Frontend (Hexagonal):**
- [ ] `domain/ports/search.port.ts` (o extender conversations port): `searchConversations(orgId, query, clientId?)`.
- [ ] `infrastructure/adapters/search.adapter.ts` o extender conversations adapter; llamar endpoint de búsqueda con debounce manejado en use case o en componente.
- [ ] `application/use-cases/search-conversations.use-case.ts`: estado results, loading, error; método search(query, clientId?) con debounce (rxjs debounceTime) y cancelación de petición anterior.
- [ ] Componente de búsqueda reutilizable: input + selector de cliente (opcional) + lista de resultados; emite “conversation selected” para navegar al chat.
- [ ] Integrar en página dashboard (super admin) o en layout; solo visible para super_admin.
- [ ] **Tests:** Ver sección [Plan de Pruebas](#-plan-de-pruebas) para detalle completo.

---

## 🧪 Plan de Pruebas

### Tests Unitarios - Frontend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `should_search_with_debounce` | `application/use-cases/search-conversations.use-case.spec.ts` | Búsqueda espera 300ms antes de ejecutar request |
| `should_cancel_previous_search_on_new_input` | `application/use-cases/search-conversations.use-case.spec.ts` | Nueva búsqueda cancela request anterior (switchMap) |
| `should_search_by_phone_and_name` | `infrastructure/adapters/search.adapter.spec.ts` | Adapter envía query param `q` correctamente |
| `should_filter_by_client_id` | `infrastructure/adapters/search.adapter.spec.ts` | Param clientId incluido cuando se especifica filtro |
| `should_show_empty_state_on_no_results` | `presentation/components/search/search.component.spec.ts` | "Sin resultados" cuando API retorna lista vacía |
| `should_show_loading_state_while_searching` | `presentation/components/search/search.component.spec.ts` | Spinner visible durante búsqueda |
| `should_navigate_to_conversation_on_result_click` | `presentation/components/search/search.component.spec.ts` | Click en resultado navega a la conversación |
| `should_sanitize_search_input` | `presentation/components/search/search.component.spec.ts` | Input con caracteres especiales se sanitiza antes de buscar |

### Tests Unitarios - Backend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `test_search_conversations_by_phone` | `tests/unit/services/test_conversation_search_service.py` | Búsqueda por teléfono retorna conversaciones matching |
| `test_search_conversations_by_name` | `tests/unit/services/test_conversation_search_service.py` | Búsqueda por nombre de contacto funciona |
| `test_search_with_client_filter` | `tests/unit/services/test_conversation_search_service.py` | Filtro por clientId limita resultados |
| `test_search_returns_empty_for_no_match` | `tests/unit/services/test_conversation_search_service.py` | Sin resultados retorna lista vacía, no error |
| `test_search_limits_results` | `tests/unit/services/test_conversation_search_service.py` | Máximo 50 resultados por búsqueda |

### Tests de Integración

| Test | Tipo | Descripción |
|------|------|-------------|
| `should_search_and_display_results_from_api` | Frontend | Escribir búsqueda -> debounce -> resultados renderizados |
| `should_navigate_from_search_to_conversation` | Frontend | Click en resultado -> chat con conversación seleccionada |
| `test_search_endpoint_with_db` | Backend | Endpoint search con DynamoDB local retorna resultados correctos |

### Cobertura Esperada

| Componente | Cobertura mínima |
|-----------|-----------------|
| `SearchConversationsUseCase` | ≥ 98% |
| `SearchAdapter` | ≥ 98% |
| `SearchComponent` | ≥ 98% |
| `ConversationSearchService` (backend) | ≥ 98% |

---

## 🔗 Dependencias

**Depende de:** HU-MFW-004 (lista clientes), HU-MFW-003 (conversaciones).  
**Bloquea a:** Ninguna crítica.

---

## 📊 Estimación

**Complejidad:** Media  
**Puntos de Historia:** 3  
**Tiempo estimado:** 2–3 días  

---

## 📝 Notas Técnicas

- Búsqueda full-text en mensajes puede requerir backend con índice (DynamoDB GSI, Elasticsearch, etc.); definir alcance con backend.

---

## ⚠️ Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Backend no soporta búsqueda de contenido de mensajes | Alta | Medio | Implementar búsqueda frontend por teléfono/nombre como MVP; documentar limitación; planear Elasticsearch en épica futura |
| Performance degradada con muchas conversaciones | Media | Medio | Paginación de resultados; limit en API; índice de búsqueda si volumen alto |

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

`user-story` `epic-2` `backend` `frontend` `priority:medium` `size:M`
