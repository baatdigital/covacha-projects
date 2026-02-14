## 📖 Historia de Usuario

**Como** super administrador del sistema sp-agents  
**Quiero** autenticarme una sola vez  
**Para** acceder tanto a sp-agents como a mf-whatsapp sin múltiples logins  

---

## 🎯 Criterios de Aceptación

- [ ] **C1.** El usuario autenticado en el Shell (mipay_core_frontend) accede a la ruta `/whatsapp` sin ser redirigido a login cuando existe sesión válida en `covacha:auth`.
- [ ] **C2.** Los tokens (access_token, refresh_token, expires_at) se leen desde SharedStateService (localStorage `covacha:auth`); no se implementa login propio dentro de mf-whatsapp.
- [ ] **C3.** Si no hay sesión válida, el Shell redirige a `/auth` (mf-auth); mf-whatsapp no muestra pantalla de login propia.
- [ ] **C4.** Los roles y permisos del usuario (`covacha:user`: roles, permissions, super_admin) están disponibles en el MF y se usan para mostrar/ocultar funcionalidades (ej. dashboard multi-cliente solo para super_admin).
- [ ] **C5.** La organización actual (`current_organization_id`) y tenant (`covacha:tenant`) se obtienen del SharedState; las llamadas HTTP del MF incluyen `X-SP-Organization-Id` y `X-Tenant-Id` en headers.
- [ ] **C6.** Al cerrar sesión en el Shell, al navegar a `/whatsapp` se redirige a auth (comportamiento consistente con otros MFs).

---

## ⚡ Requisitos No Funcionales

| Categoría | Requisito |
|-----------|-----------|
| **Performance** | Carga de ruta `/whatsapp` < 1s cuando sesión válida; inyección de headers < 5ms |
| **Accesibilidad** | WCAG 2.1 AA; navegación por teclado; labels para screen readers |
| **Seguridad** | Tokens nunca expuestos en logs ni DOM; headers solo en HTTPS; refresh token no incluido en requests API |
| **Observabilidad** | Logs de error en consola con contexto; errores capturados por Sentry |
| **Compatibilidad** | Chrome 90+, Firefox 90+, Safari 15+, Edge 90+ |

---

## 📋 Tareas Técnicas

**Frontend (Arquitectura hexagonal):**
- [ ] En `remote-entry/entry.component.ts`: llamar `SharedStateService.rehydrate()` en `ngOnInit`; no implementar lógica de login.
- [ ] En `core/http/http.service.ts`: construir headers con `Authorization: Bearer {accessToken}`, `X-API-KEY`, `X-SP-Organization-Id`, `X-Tenant-Id` desde SharedStateService.
- [ ] En `shared-state/shared-state.service.ts`: mantener compatibilidad con keys `covacha:auth`, `covacha:user`, `covacha:tenant`; solo lectura desde localStorage.
- [ ] Crear `core/guards/auth.guard.ts` (opcional) que verifique `isAuthenticated` del SharedState y redirija a `/auth` si no hay sesión; registrar en rutas del MF si se requiere protección adicional a la del Shell.
- [ ] Documentar en CLAUDE.md que la autenticación es responsabilidad del Shell y mf-auth.

**Tests:** Ver sección [Plan de Pruebas](#-plan-de-pruebas) para detalle completo.

**Documentación:**
- [ ] Actualizar CLAUDE.md sección de autenticación y flujo SSO.

---

## 🧪 Plan de Pruebas

### Tests Unitarios - Frontend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `should_include_authorization_header_when_token_exists` | `core/http/http.service.spec.ts` | Verifica que HttpService agrega `Authorization: Bearer {token}` cuando existe token en SharedState |
| `should_include_organization_and_tenant_headers` | `core/http/http.service.spec.ts` | Verifica que HttpService agrega `X-SP-Organization-Id` y `X-Tenant-Id` desde SharedState |
| `should_include_api_key_header` | `core/http/http.service.spec.ts` | Verifica que HttpService agrega `X-API-KEY` en todas las peticiones |
| `should_not_include_auth_header_when_no_token` | `core/http/http.service.spec.ts` | Verifica que no se agrega header Authorization cuando no hay token |
| `should_call_rehydrate_on_init` | `remote-entry/entry.component.spec.ts` | Verifica que `SharedStateService.rehydrate()` se llama en `ngOnInit` |
| `should_not_render_login_form` | `remote-entry/entry.component.spec.ts` | Verifica que entry component no contiene formulario de login |
| `should_validate_organization_on_init` | `remote-entry/entry.component.spec.ts` | Verifica que se valida `current_sp_organization_id` al iniciar |
| `should_read_shared_state_keys_correctly` | `shared-state/shared-state.service.spec.ts` | Verifica lectura de `covacha:auth`, `covacha:user`, `covacha:tenant` |

### Tests Unitarios - Backend

No aplica - esta historia es solo frontend.

### Tests de Integración

| Test | Tipo | Descripción |
|------|------|-------------|
| `should_access_whatsapp_route_with_valid_session` | E2E | Usuario autenticado en Shell navega a `/whatsapp` sin redirect |
| `should_redirect_to_auth_without_session` | E2E | Sin sesión válida, acceso a `/whatsapp` redirige a `/auth` |
| `should_propagate_logout_to_mf` | E2E | Al cerrar sesión en Shell, `/whatsapp` redirige a auth |

### Cobertura Esperada

| Componente | Cobertura mínima |
|-----------|-----------------|
| `HttpService` | ≥ 98% |
| `EntryComponent` | ≥ 98% |
| `SharedStateService` | ≥ 95% |

---

## 🔗 Dependencias

**Depende de:** Ninguna (primera historia de la épica).  
**Bloquea a:** HU-MFW-002, HU-MFW-004 (sin auth no se puede restringir por roles).

---

## 📊 Estimación

**Complejidad:** Baja  
**Puntos de Historia:** 2  
**Tiempo estimado:** 1 día  

---

## 📝 Notas Técnicas

- El Shell ya carga mf-whatsapp bajo una ruta protegida por auth guard; validar en tenant.config.ts que la ruta `/whatsapp` exige autenticación.
- Usar path aliases: `@shared-state`, `@core/*`, `@env`.

---

## ⚠️ Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| SharedState no rehidratado al cargar MF | Media | Alto | Verificar rehydrate() en ngOnInit con retry; test E2E de carga |
| Cambios en keys de localStorage por otro MF | Baja | Alto | Usar constantes compartidas de covacha_libs; no hardcodear strings |

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

`user-story` `epic-1` `frontend` `priority:high` `size:S`
