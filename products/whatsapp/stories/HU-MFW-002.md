## 📖 Historia de Usuario

**Como** super administrador  
**Quiero** asignar roles específicos para mf-whatsapp  
**Para** controlar el acceso de usuarios a funcionalidades de WhatsApp  

---

## 🎯 Criterios de Aceptación

- [ ] **C1.** Existe un modelo de permisos/roles para mf-whatsapp (ej. `whatsapp:admin`, `whatsapp:viewer`, `whatsapp:super_admin`) documentado y alineado con el backend (mipay_core o sp_webhook) si los roles se persisten ahí.
- [ ] **C2.** El MF lee `permissions` y/o `roles` y `super_admin` desde SharedStateService (`covacha:user`) y decide qué vistas mostrar (ej. dashboard multi-cliente solo si `super_admin === true` o tiene permiso `whatsapp:super_admin`).
- [ ] **C3.** Usuarios sin permiso para WhatsApp ven mensaje claro (“No tienes acceso a este módulo”) o redirección a dashboard general, sin errores de consola.
- [ ] **C4.** Super administrador puede ver lista de clientes y acceder a cualquier cliente; administrador de cliente solo ve su cliente asignado (cuando se implemente HU-MFW-004/005).
- [ ] **C5.** La asignación de roles a usuarios se realiza desde el sistema existente (mf-settings o backend); mf-whatsapp no implementa pantalla de administración de roles (solo consume los roles ya asignados).
- [ ] **C6.** Tests automatizados verifican que componentes restringidos no se muestran cuando el usuario no tiene el rol/permiso correspondiente.

---

## ⚡ Requisitos No Funcionales

| Categoría | Requisito |
|-----------|-----------|
| **Performance** | Evaluación de permisos < 10ms (computed signal, sin llamadas async) |
| **Accesibilidad** | WCAG 2.1 AA; navegación por teclado; labels para screen readers |
| **Seguridad** | Permisos verificados en frontend Y backend; no confiar solo en ocultamiento de UI para seguridad |
| **Observabilidad** | Logs de error en consola con contexto; errores capturados por Sentry |
| **Compatibilidad** | Chrome 90+, Firefox 90+, Safari 15+, Edge 90+ |

---

## 📋 Tareas Técnicas

**Frontend (Hexagonal):**
- [ ] En `domain/models/user.model.ts` (o reutilizar tipos de shared-state): tipo para permisos/roles de WhatsApp.
- [ ] En `core/services/permission.service.ts`: servicio que exponga `canAccessWhatsApp()`, `canAccessMultiClientDashboard()`, `canManageAutomation()` basado en SharedStateService.
- [ ] En `presentation/`: usar PermissionService en guards o en componentes para mostrar/ocultar rutas o secciones; no duplicar lógica en cada página.
- [ ] Registrar PermissionService en `remote-entry/entry.component.ts` o en `app.config.ts` del MF.
- [ ] Documentar en CLAUDE.md la lista de permisos/roles usados por mf-whatsapp.

**Backend (si aplica):**
- [ ] Si los roles se guardan en backend: documentar endpoint o modelo existente; el MF solo consume lo que devuelve el login/profile (covacha:user).

**Tests:** Ver sección [Plan de Pruebas](#-plan-de-pruebas) para detalle completo.

---

## 🧪 Plan de Pruebas

### Tests Unitarios - Frontend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `should_return_true_for_super_admin_access` | `core/services/permission.service.spec.ts` | `canAccessWhatsApp()` retorna true cuando `super_admin === true` |
| `should_return_false_without_whatsapp_permission` | `core/services/permission.service.spec.ts` | `canAccessWhatsApp()` retorna false sin permiso `whatsapp:viewer` |
| `should_allow_multi_client_dashboard_for_super_admin` | `core/services/permission.service.spec.ts` | `canAccessMultiClientDashboard()` retorna true solo para super_admin |
| `should_deny_multi_client_dashboard_for_regular_user` | `core/services/permission.service.spec.ts` | `canAccessMultiClientDashboard()` retorna false para usuario normal |
| `should_react_to_user_changes_via_signal` | `core/services/permission.service.spec.ts` | Al cambiar covacha:user, permisos se recalculan automáticamente (computed signal) |
| `should_show_access_denied_message` | `presentation/components/access-denied.component.spec.ts` | Componente muestra mensaje "No tienes acceso" cuando sin permiso |
| `should_hide_restricted_content` | `presentation/pages/home/home.component.spec.ts` | Secciones restringidas no se renderizan sin permiso adecuado |

### Tests Unitarios - Backend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `test_endpoint_returns_403_without_whatsapp_permission` | `tests/unit/controllers/test_whatsapp_permissions.py` | Endpoint rechaza usuario sin permiso WhatsApp |
| `test_endpoint_allows_super_admin` | `tests/unit/controllers/test_whatsapp_permissions.py` | Endpoint permite acceso a super_admin |

### Tests de Integración

| Test | Tipo | Descripción |
|------|------|-------------|
| `should_show_full_dashboard_for_super_admin` | Frontend | Super admin ve dashboard multi-cliente completo |
| `should_show_limited_view_for_client_admin` | Frontend | Admin cliente ve solo su información |
| `should_show_access_denied_for_unauthorized` | Frontend | Usuario sin permiso ve mensaje de acceso denegado |

### Cobertura Esperada

| Componente | Cobertura mínima |
|-----------|-----------------|
| `PermissionService` | ≥ 98% |
| `AccessDeniedComponent` | ≥ 98% |
| Guards de ruta | ≥ 95% |

---

## 🔗 Dependencias

**Depende de:** HU-MFW-001 (auth y SharedState).  
**Bloquea a:** HU-MFW-004 (vista lista clientes por rol), HU-MFW-005 (navegación a conversaciones).

---

## 📊 Estimación

**Complejidad:** Media  
**Puntos de Historia:** 3  
**Tiempo estimado:** 2 días  

---

## 📝 Notas Técnicas

- Alinear nombres de permisos con mipay_core_frontend y mipay_core si ya existen (ej. `module:whatsapp`).
- Usar signals/computed en PermissionService para reacción a cambios de usuario.

---

## ⚠️ Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Modelo de permisos no alineado con backend (mipay_core) | Media | Alto | Documentar y validar mapping de roles con equipo backend antes de implementar |
| Cambio de roles en sesión activa no reflejado | Baja | Medio | Escuchar BroadcastChannel para cambios en covacha:user; revalidar en cada navegación |

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

`user-story` `epic-1` `frontend` `priority:high` `size:M`
