## 📖 Historia de Usuario

**Como** administrador de cliente  
**Quiero** acceder al historial completo de conversaciones  
**Para** revisar el contexto de interacciones anteriores  

---

## 🎯 Criterios de Aceptación

- [ ] **C1.** Al abrir una conversación se cargan los mensajes más recientes (ej. últimos 50); hay un control “Cargar más” o scroll hacia arriba que carga mensajes anteriores (paginación hacia atrás en el tiempo).
- [ ] **C2.** Los mensajes se muestran en orden cronológico (antiguos arriba, recientes abajo); la posición de scroll se mantiene de forma razonable al cargar más (no salta al final).
- [ ] **C3.** Cada mensaje muestra fecha/hora (formato legible); opcional agrupación por día (separador “Hoy”, “Ayer”, “15 ene”, etc.).
- [ ] **C4.** El historial incluye todos los tipos soportados (texto, imagen, audio, video, documento) con la misma representación que en tiempo real; enlaces a medios descargables si el backend los expone.
- [ ] **C5.** No hay límite práctico de mensajes a mostrar: paginación sigue cargando hasta que el backend indique que no hay más (o hasta un límite alto configurable).
- [ ] **C6.** Estados de mensaje (enviado/entregado/leído) se muestran en el historial igual que en mensajes recientes.
- [ ] **C7.** Performance: lista virtualizada o paginación eficiente para conversaciones con miles de mensajes; tiempo de primera carga < 2 s para 50 mensajes en condiciones normales.

---

## ⚡ Requisitos No Funcionales

| Categoría | Requisito |
|-----------|-----------|
| **Performance** | Carga inicial de 50 mensajes < 1s; 'cargar más' agrega 50 mensajes en < 500ms; scroll position mantenida sin salto visible |
| **Accesibilidad** | WCAG 2.1 AA; navegación por teclado; labels para screen readers |
| **Seguridad** | Cursor/token de paginación no manipulable; backend valida permisos por conversación |
| **Observabilidad** | Logs de error en consola con contexto; errores capturados por Sentry |
| **Compatibilidad** | Chrome 90+, Firefox 90+, Safari 15+, Edge 90+ |

---

## 📋 Tareas Técnicas

**Backend:**
- [ ] Endpoint de mensajes con paginación: query params `conversationId`, `before` (timestamp o cursor), `limit`; respuesta ordenada por fecha ascendente para “página anterior”; documentar.

**Frontend (Hexagonal):**
- [ ] `domain/ports/whatsapp.port.ts`: método `listMessages(conversationId, pagination?: { before?, limit })` ya puede existir; asegurar que soporte cursor/ before.
- [ ] Adapter: llamar endpoint con before/limit; mapear a Message[].
- [ ] `application/use-cases/get-messages.use-case.ts` (o extender existente): estado messages (array), hasMore, loadingMore; loadMore() que pida página anterior y concatene al inicio del array (o en orden correcto); evitar duplicados por id.
- [ ] Componente lista de mensajes: al hacer scroll hacia arriba (o botón “Cargar más” arriba) llamar loadMore(); mantener posición de scroll (scrollHeight/scrollTop) después de insertar mensajes antiguos.
- [ ] Agrupación por día: pipe o función que agrupe mensajes por fecha y renderice separadores “Hoy”, “Ayer”, “dd MMM”.
- [ ] Virtual scroll (CDK o similar) si la lista es muy larga; o paginación por bloques con “Cargar más” explícito.
- [ ] **Tests:** Ver sección [Plan de Pruebas](#-plan-de-pruebas) para detalle completo.

---

## 🧪 Plan de Pruebas

### Tests Unitarios - Frontend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `should_load_initial_messages` | `application/use-cases/get-messages.use-case.spec.ts` | Carga inicial retorna últimos 50 mensajes |
| `should_load_more_messages_on_request` | `application/use-cases/get-messages.use-case.spec.ts` | loadMore() agrega mensajes anteriores al inicio del array |
| `should_set_has_more_false_when_no_more` | `application/use-cases/get-messages.use-case.spec.ts` | Backend indica fin → hasMore signal false → botón oculto |
| `should_not_duplicate_messages` | `application/use-cases/get-messages.use-case.spec.ts` | Deduplicación por id al concatenar páginas |
| `should_maintain_scroll_position_on_load_more` | `presentation/pages/chat/message-list.component.spec.ts` | Scroll position estable al insertar mensajes arriba |
| `should_group_messages_by_day` | `presentation/pages/chat/message-list.component.spec.ts` | Separadores "Hoy", "Ayer", "15 ene" entre grupos |
| `should_show_load_more_button` | `presentation/pages/chat/message-list.component.spec.ts` | Botón "Cargar más" visible cuando hasMore === true |
| `should_format_timestamps_correctly` | `presentation/components/message-bubble/message-bubble.spec.ts` | Hora en formato legible (HH:mm) con timezone correcto |

### Tests Unitarios - Backend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `test_list_messages_with_cursor_pagination` | `tests/unit/controllers/test_messages_controller.py` | Paginación con before/limit retorna página correcta |
| `test_list_messages_ordered_ascending` | `tests/unit/controllers/test_messages_controller.py` | Mensajes en orden cronológico ascendente |
| `test_list_messages_includes_all_types` | `tests/unit/controllers/test_messages_controller.py` | Todos los tipos (text, image, audio, etc.) incluidos |
| `test_list_messages_indicates_has_more` | `tests/unit/controllers/test_messages_controller.py` | Respuesta incluye hasMore: true/false |
| `test_list_messages_with_media_urls` | `tests/unit/services/test_message_service.py` | Mensajes multimedia incluyen URLs de descarga válidas |

### Tests de Integración

| Test | Tipo | Descripción |
|------|------|-------------|
| `should_load_conversation_and_scroll_to_bottom` | Frontend | Abrir conversación → mensajes cargan → scroll al final |
| `should_load_more_and_maintain_position` | Frontend | Click "Cargar más" → mensajes previos aparecen → position estable |
| `test_pagination_with_real_db` | Backend | Múltiples páginas de mensajes navegan correctamente |

### Cobertura Esperada

| Componente | Cobertura mínima |
|-----------|-----------------|
| `GetMessagesUseCase` (paginación) | ≥ 98% |
| `MessageListComponent` | ≥ 98% |
| `MessagesController` (backend) | ≥ 95% |

---

## 🔗 Dependencias

**Depende de:** HU-MFW-007 (vista mensajes), HU-MFW-003 (API mensajes).  
**Bloquea a:** Ninguna crítica.

---

## 📊 Estimación

**Complejidad:** Media  
**Puntos de Historia:** 3  
**Tiempo estimado:** 2 días  

---

## 📝 Notas Técnicas

- Cursor-based pagination suele ser más estable que offset para mensajes.
- Mantener orden consistente (asc/desc) entre backend y frontend para no invertir mensajes.

---

## ⚠️ Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Scroll position pierde estabilidad al insertar mensajes arriba | Media | Alto | Guardar scrollHeight antes de insertar; restaurar scrollTop = newScrollHeight - oldScrollHeight; testar en varios browsers |
| Formato de fecha/hora inconsistente entre locales | Baja | Bajo | Usar DatePipe con locale configurado; agrupar por día con lógica timezone-aware (America/Mexico_City) |

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

`user-story` `epic-3` `backend` `frontend` `priority:medium` `size:M`
