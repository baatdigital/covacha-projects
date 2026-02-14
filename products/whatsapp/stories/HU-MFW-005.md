## 📖 Historia de Usuario

**Como** super administrador  
**Quiero** hacer clic en un cliente específico  
**Para** acceder directamente a sus conversaciones de WhatsApp  

---

## 🎯 Criterios de Aceptación

- [ ] **C1.** Desde la lista de clientes (HU-MFW-004), al hacer clic en un cliente se navega a la vista de conversaciones de ese cliente (ruta ej. `/whatsapp/chat?clientId=xxx` o `/whatsapp/clients/:clientId/chat`).
- [ ] **C2.** La vista de conversaciones recibe el contexto del cliente (clientId o organizationId según modelo); carga solo las conversaciones/números de ese cliente.
- [ ] **C3.** Se muestra un encabezado o breadcrumb que indique el cliente seleccionado (nombre) y opción de volver al listado de clientes.
- [ ] **C4.** Si el cliente no tiene números de WhatsApp activos, se muestra mensaje informativo y opción “Configurar número” (enlace o botón) en lugar de lista vacía sin explicación.
- [ ] **C5.** El clientId (o identificador equivalente) se mantiene en la URL para permitir bookmarks y recarga; al recargar la página se vuelve a cargar el mismo cliente.
- [ ] **C6.** Solo usuarios con permiso (super_admin o admin de ese cliente) pueden acceder; en caso contrario mostrar “Sin acceso” o redirigir.

---

## ⚡ Requisitos No Funcionales

| Categoría | Requisito |
|-----------|-----------|
| **Performance** | Navegación de lista a chat < 500ms; carga de contexto cliente inmediata desde cache |
| **Accesibilidad** | WCAG 2.1 AA; navegación por teclado; labels para screen readers |
| **Seguridad** | clientId en URL no permite acceso a clientes no autorizados; backend valida permisos por org |
| **Observabilidad** | Logs de error en consola con contexto; errores capturados por Sentry |
| **Compatibilidad** | Chrome 90+, Firefox 90+, Safari 15+, Edge 90+ |

---

## 📋 Tareas Técnicas

**Frontend (Hexagonal):**
- [ ] Definir ruta en `entry.routes.ts`: ej. `clients/:clientId/chat` que cargue el componente de chat con `clientId` como parámetro.
- [ ] En el componente de lista de clientes: navegación con `Router.navigate(['/whatsapp/clients', client.id, 'chat'])` (o ruta relativa según configuración del Shell).
- [ ] En página/componente de chat: leer `clientId` desde `ActivatedRoute`; pasarlo al use case de conversaciones para filtrar por cliente (o por org si el modelo es 1 org = 1 cliente).
- [ ] Crear componente de encabezado o breadcrumb reutilizable: “Clientes > {nombre cliente} > Conversaciones”; enlace “Volver” al listado.
- [ ] Validar en guard o en componente: si clientId no tiene números activos, mostrar mensaje y CTA; reutilizar adapter/endpoint de números por cliente si existe.
- [ ] Ajustar `WhatsAppPort`/adapter para listar conversaciones por cliente (parámetro clientId o equivalente en API).

**Tests:** Ver sección [Plan de Pruebas](#-plan-de-pruebas) para detalle completo.

---

## 🧪 Plan de Pruebas

### Tests Unitarios - Frontend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `should_navigate_to_chat_with_client_id` | `presentation/pages/clients-dashboard/clients-dashboard.spec.ts` | Click en cliente navega a `/whatsapp/clients/:clientId/chat` |
| `should_read_client_id_from_route` | `presentation/pages/chat/chat.component.spec.ts` | Componente lee clientId de ActivatedRoute.params |
| `should_load_conversations_for_client` | `presentation/pages/chat/chat.component.spec.ts` | Use case se invoca con clientId correcto |
| `should_show_breadcrumb_with_client_name` | `presentation/components/breadcrumb/breadcrumb.spec.ts` | Breadcrumb muestra "Clientes > {nombre} > Conversaciones" |
| `should_show_no_numbers_message` | `presentation/pages/chat/chat.component.spec.ts` | Sin números activos muestra mensaje informativo y CTA |
| `should_handle_invalid_client_id` | `presentation/pages/chat/chat.component.spec.ts` | clientId inexistente redirige a lista con toast de error |

### Tests Unitarios - Backend

Reutiliza endpoints de HU-MFW-003/004 - no requiere tests backend adicionales.

### Tests de Integración

| Test | Tipo | Descripción |
|------|------|-------------|
| `should_navigate_from_list_to_chat_and_load_conversations` | Frontend | Flujo completo: lista -> click -> chat con conversaciones del cliente |
| `should_persist_client_context_on_reload` | Frontend | Recargar página con clientId en URL mantiene contexto |
| `should_redirect_on_unauthorized_client_access` | Frontend | Acceder a clientId sin permiso redirige con error |

### Cobertura Esperada

| Componente | Cobertura mínima |
|-----------|-----------------|
| `ChatComponent` (navegación) | ≥ 98% |
| `BreadcrumbComponent` | ≥ 98% |
| Routing/Guards | ≥ 95% |

---

## 🔗 Dependencias

**Depende de:** HU-MFW-004 (lista de clientes), HU-MFW-003 (API conversaciones).  
**Bloquea a:** HU-MFW-007 (vista conversaciones en tiempo real puede reutilizar la misma ruta).

---

## 📊 Estimación

**Complejidad:** Baja  
**Puntos de Historia:** 2  
**Tiempo estimado:** 1 día  

---

## 📝 Notas Técnicas

- Decidir si "cliente" en el modelo es organization (multi-tenant) o una entidad cliente dentro de una org; alinear con mipay_core.

---

## ⚠️ Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Modelo de 'cliente' inconsistente entre MFs | Media | Medio | Alinear con modcore_clients de mipay_core; documentar mapping |
| Deep link con clientId inválido causa error no manejado | Baja | Medio | Validar clientId al cargar; redirigir a lista con toast de error si no encontrado |

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

`user-story` `epic-2` `frontend` `priority:high` `size:S`
