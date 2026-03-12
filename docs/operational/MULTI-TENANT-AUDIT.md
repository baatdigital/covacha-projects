# Multi-Tenant Data Isolation Audit - mf-marketing

**Fecha**: 2026-03-10
**Repo**: `baatdigital/mf-marketing`
**Branch**: `develop`
**Auditor**: Claude Code (automated)
**Issue**: #44

---

## Resumen Ejecutivo

| Categoria | Estado | Hallazgos |
|-----------|--------|-----------|
| API calls con org ID | PASS | Todos los adapters incluyen orgId en URLs |
| localStorage tenant prefixes | WARNING | 3 keys sin prefijo de org/tenant |
| Hardcoded org/tenant IDs | PASS | Solo en environments y bootstrap (dev) |
| SharedState tenant isolation | PASS | Lectura correcta de localStorage con keys `covacha:` |
| BroadcastChannel seguridad | PASS | Canal nombrado con prefijo `covacha:state-sync` |
| Cache clearing on org change | FAIL | In-memory caches NO se limpian al cambiar org |
| HTTP headers | WARNING | X-API-KEY hardcodeado, X-Tenant-Id presente |
| postMessage origin | FAIL | `window.opener.postMessage` usa `'*'` como target origin |
| Static/singleton data leakage | WARNING | BehaviorSubjects en servicios singleton persisten entre orgs |

**Risk Score: 5/10** (Medio)

---

## 1. API Calls con Organization ID

**Estado: PASS**

Todos los adapters HTTP incluyen el `orgId` como parte de la URL del endpoint, garantizando que las peticiones esten scoped a la organizacion correcta.

**Patron observado:**
```
/organization/{orgId}/agency/clients/{clientId}/...
/organization/{orgId}/clients/{clientId}/strategies/...
/organization/{orgId}/strategies/dashboard/executive
/social/organizations/{orgId}/...
```

**Archivos verificados:**
- `src/app/infrastructure/adapters/strategy/strategy-core.adapter.ts` (lineas 100-105)
- `src/app/infrastructure/adapters/strategy/strategy-dashboard.adapter.ts` (lineas 56-61)
- `src/app/core/services/permission-guard.service.ts` (lineas 131, 156, 182)

**Conclusion:** El backend es la barrera de aislamiento primaria y recibe el orgId en cada request. No se detectaron endpoints sin org scope.

---

## 2. localStorage Keys sin Tenant Prefix

**Estado: WARNING**

### Keys correctamente prefijadas

| Key Pattern | Ejemplo | Aislamiento |
|-------------|---------|-------------|
| `covacha:*` | `covacha:auth`, `covacha:user` | OK - compartido Shell |
| `mf-marketing:*` | `mf-marketing:campaign-builder-draft` | OK - modulo scope |
| `drive_account_{orgId}` | `drive_account_39c56b2b...` | OK - incluye orgId |
| `mf-marketing:client-{clientId}:tab` | Tab activo por cliente | OK - incluye clientId |

### Keys SIN aislamiento por org/tenant (PROBLEMA)

| Key | Archivo | Linea | Riesgo |
|-----|---------|-------|--------|
| `current_sp_client_id` | `client-settings.component.ts` | 109, 119 | Persiste clientId de org anterior al cambiar org |
| `mf-marketing:campaign-builder-draft` | `campaign-builder.component.ts` | 155 | Draft de campana puede pertenecer a otra org |
| `mf-marketing:active-strategy` | `strategy-state.service.ts` | 19 | Estrategia activa puede pertenecer a otra org |
| `mf-marketing:client-wizard-draft` | `client-wizard.component.ts` | 178 | Draft de wizard de otra org |
| `mf-marketing:current_sp_client_id` | `marketing-layout.component.ts` | 481, 516 | ClientId sin scope de org |
| `mf-marketing:current-page` | `marketing-layout.component.ts` | 487, 504 | Bajo riesgo pero sin org scope |
| `mf-marketing:view-mode` | `marketing-layout.component.ts` | 494, 521 | Bajo riesgo (preferencia UI) |
| `mf-marketing:clients-view` | `view-toggle.component.ts` | 29 (static) | Bajo riesgo (preferencia UI) |
| `drive_folder_{clientId}` | `client-media-library.component.ts` | 889, 917 | Folder ID sin org scope |

**Recomendacion:** Las keys que almacenan datos de negocio (drafts, client IDs, strategy IDs) deben incluir el orgId:
```
mf-marketing:{orgId}:campaign-builder-draft
mf-marketing:{orgId}:active-strategy
mf-marketing:{orgId}:current_sp_client_id
```

---

## 3. Hardcoded Organization/Tenant IDs

**Estado: PASS**

Los unicos hardcoded IDs encontrados estan en archivos de configuracion de desarrollo, lo cual es aceptable:

| Archivo | Contexto |
|---------|----------|
| `src/environments/environment.ts:39` | `spOrganizationId: '39c56b2b-...'` (solo dev) |
| `src/bootstrap.ts:61` | Tenant `superpago` mock (solo dev) |
| `src/app/presentation/pages/demos/bot-whatsapp-landing-demo.component.ts:321` | Demo component con IDs ficticios |

En produccion, todos los IDs provienen del estado compartido (`covacha:user`, `covacha:tenant`).

---

## 4. SharedStateService - Tenant Isolation

**Estado: PASS**

**Archivo:** `src/app/shared-state/shared-state.service.ts`

Aspectos positivos:
- Lee estado desde localStorage con keys prefijadas `covacha:`
- Soporta multi-org via `organization_ids[]` y `current_organization_id`
- `setCurrentOrganization()` valida que el orgId pertenezca al usuario (linea 570)
- Limpia `project_ids` y `current_project_id` al cambiar de org (lineas 578-579)
- Escucha cambios via `StorageEvent` y `BroadcastChannel` para sincronizar tabs
- `getCachedOrganizations()` filtra por `organization_ids` del usuario (linea 533)

Aspecto a mejorar:
- `setCurrentOrganization()` NO emite un evento para que otros servicios limpien sus caches in-memory

---

## 5. BroadcastChannel Messages

**Estado: PASS**

- Canal nombrado: `covacha:state-sync` (no generico)
- Mensajes tipados con `type` y `payload`
- Maneja correctamente `logout` y `clear` para resetear estado
- El evento `organization_cleared` limpia org y nav modules

**Archivo:** `src/app/shared-state/shared-state.service.ts` (lineas 368-476)

---

## 6. Cache Clearing on Organization Change

**Estado: FAIL**

### Problema critico

Cuando el usuario cambia de organizacion via `shared-header.component.ts:selectOrganization()`, el flujo es:

1. Actualiza `covacha:user.current_organization_id` en localStorage
2. Redirige a `/app` (full page reload)

Sin embargo, **los siguientes caches in-memory NO se limpian explicitamente**:

| Servicio | Cache | Tipo | Riesgo |
|----------|-------|------|--------|
| `PermissionGuardService` | `teamMembersCache`, `permissionsCache` | `Map<string, ...>` | **ALTO** - Permisos de org anterior persisten si no hay reload completo |
| `ClientManagementService` | `clientsSubject` | `BehaviorSubject` | **ALTO** - Lista de clientes de org anterior |
| `StrategyManagementService` | `strategiesSubject` | `BehaviorSubject` | **ALTO** - Estrategias de org anterior |
| `SocialMediaService` | `postsSubject`, `accountsSubject` | `BehaviorSubject` | **MEDIO** - Posts de org anterior |
| `AiContentService` | `historySubject` | `BehaviorSubject` | **BAJO** - Historial de contenido generado |
| `StrategyStateService` | `_activeStrategy`, `_strategies` | `signal` | **ALTO** - Estrategia activa de otra org (localStorage) |

**Mitigacion actual:** El `selectOrganization()` hace `globalThis.location.href = '/app'` que fuerza un full page reload, destruyendo los singletons en memoria. Esto funciona **siempre que** la navegacion no sea via Angular router (que mantendria los singletons).

**Riesgo residual:** Si en el futuro se implementa cambio de org via SPA navigation (sin reload), habra data leakage entre organizaciones.

**Recomendacion:**
1. Implementar un metodo `onOrganizationChange()` en cada servicio con cache
2. Conectarlo al evento `current_organization` del BroadcastChannel
3. O crear un `CacheManagerService` que coordine la limpieza

### Logout clearing

La funcion `clearAllStorage()` en `shared-header.component.ts` (linea 365) solo limpia keys `covacha:*`, **no limpia** keys `mf-marketing:*`, `drive_account_*`, `drive_folder_*`, ni `current_sp_client_id`.

**Recomendacion:** Extender `clearAllStorage()` para limpiar todas las keys del MF:
```typescript
// Tambien limpiar keys del MF
for (let i = localStorage.length - 1; i >= 0; i--) {
  const key = localStorage.key(i);
  if (key?.startsWith('mf-marketing:') || key?.startsWith('drive_') || key === 'current_sp_client_id') {
    localStorage.removeItem(key);
  }
}
```

---

## 7. HTTP Interceptors / Headers

**Estado: WARNING**

**Archivo:** `src/app/core/http/http.service.ts`

### Headers enviados

| Header | Fuente | Estado |
|--------|--------|--------|
| `X-API-KEY` | Hardcodeado: `'MASTER-SuperSecretKey123456789'` | WARNING |
| `X-Tenant-Id` | `sharedState.tenantId()` (dinamico) | PASS |
| `Authorization` | NO incluido automaticamente | FAIL |
| `Content-Type` | `application/json` (excepto FormData) | PASS |

### Problemas detectados

1. **X-API-KEY hardcodeado** (linea 154): El valor `MASTER-SuperSecretKey123456789` esta hardcodeado en el servicio y tambien en `environment.ts` y `environment.prod.ts`. Deberia usar `environment.apiKey` para consistencia y facilitar rotacion.

2. **Authorization header ausente en HttpService**: El metodo `buildHeaders()` (lineas 149-175) **NO incluye el Bearer token**. El `getAuthHeaders()` de SharedState existe pero NO se usa en HttpService. Esto significa que las peticiones HTTP desde HttpService **no envian autenticacion**, a menos que el backend valide solo con X-API-KEY.

   - **Nota:** Algunos servicios como `shared-header.component.ts` y `organization-validator.service.ts` hacen fetch directo con Authorization header, bypasseando HttpService.

3. **X-Tenant-Id presente** (linea 170): Correcto, se envia en cada request.

**Archivos con hardcoded API key:**
- `src/app/core/http/http.service.ts:154`
- `src/app/core/services/organization-validator.service.ts:16`
- `src/environments/environment.ts:49`
- `src/environments/environment.prod.ts:45`

---

## 8. postMessage Origin Validation

**Estado: FAIL**

**Archivo:** `src/app/presentation/pages/oauth-callback/oauth-callback.component.ts`

```typescript
// Linea 223 - usa '*' como target origin
window.opener.postMessage({ type: 'google_drive_oauth_success', data }, '*');

// Linea 232 - usa '*' como target origin
window.opener.postMessage({ type: 'google_drive_oauth_error', error }, '*');
```

**Riesgo:** Usar `'*'` como target origin en `postMessage` permite que cualquier pagina que abra el callback reciba los datos del OAuth. En teoria, un atacante podria abrir la URL de callback OAuth y recibir tokens/datos del flujo.

**Recomendacion:** Reemplazar `'*'` con el origin esperado:
```typescript
const expectedOrigin = window.location.origin; // o environment-specific
window.opener.postMessage({ ... }, expectedOrigin);
```

---

## 9. Static/Singleton Data Persistence

**Estado: WARNING**

Solo se encontro 1 clase con `static readonly`:

| Archivo | Propiedad | Riesgo |
|---------|-----------|--------|
| `view-toggle.component.ts:29` | `private static readonly STORAGE_KEY = 'mf-marketing:clients-view'` | Ninguno - es una constante |

Sin embargo, los servicios `providedIn: 'root'` (singletons) mantienen estado en memoria que no se limpia al cambiar de organizacion:

- `PermissionGuardService` - Maps de permisos/equipo
- `ClientManagementService` - BehaviorSubject de clientes
- `StrategyManagementService` - BehaviorSubject de estrategias
- `SocialMediaService` - BehaviorSubjects de posts/cuentas
- `StrategyStateService` - Signal de estrategia activa

Ver seccion 6 para detalles y mitigacion.

---

## Hallazgos Adicionales

### Google Drive Adapter - localStorage con orgId

**Estado: PASS**

El `google-drive.adapter.ts` usa keys con orgId incluido: `drive_account_{orgId}` (linea 264). Esto es correcto para aislamiento multi-tenant.

### client-media-library - localStorage sin orgId

**Estado: WARNING**

`client-media-library.component.ts` usa `drive_folder_{clientId}` (linea 889) sin incluir orgId. Si dos orgs tienen clientes con el mismo ID (improbable pero posible con UUIDs), habria collision.

---

## Matriz de Riesgos

| # | Riesgo | Severidad | Probabilidad | Impacto | Mitigacion Actual |
|---|--------|-----------|--------------|---------|-------------------|
| 1 | In-memory caches persisten entre orgs | Alta | Baja (redirect fuerza reload) | Data leak cross-org | Full page reload en org switch |
| 2 | localStorage keys sin org scope | Media | Media | Draft/estado de otra org visible | Ninguna |
| 3 | postMessage con origin `'*'` | Media | Baja | OAuth data leak | Ninguna |
| 4 | Authorization header no enviado via HttpService | Alta | Alta | Requests sin auth | Backend valida con X-API-KEY |
| 5 | X-API-KEY hardcodeado en codigo | Media | Baja | Dificil rotar key | Environment files |
| 6 | Logout no limpia keys `mf-marketing:*` | Baja | Media | Datos residuales post-logout | Ninguna |
| 7 | `current_sp_client_id` sin prefijo ni org scope | Baja | Baja | Referencia a cliente incorrecto | Solo usado para debugging |

---

## Recomendaciones Priorizadas

### P0 - Critico (resolver antes de produccion multi-tenant real)

1. **Agregar orgId a localStorage keys de negocio**: `mf-marketing:active-strategy`, `mf-marketing:campaign-builder-draft`, `mf-marketing:current_sp_client_id`
2. **Agregar Authorization header en HttpService.buildHeaders()**: Usar `sharedState.accessToken()` para incluir Bearer token
3. **Implementar cache clearing on org change**: Crear hook `onOrganizationChange()` que limpie BehaviorSubjects y Maps

### P1 - Importante

4. **Corregir postMessage origin**: Reemplazar `'*'` con origin especifico en `oauth-callback.component.ts`
5. **Usar `environment.apiKey`** en HttpService en lugar de string hardcodeado
6. **Extender logout para limpiar keys `mf-marketing:*`**: En `clearAllStorage()`

### P2 - Mejora

7. **Agregar orgId a `drive_folder_{clientId}`**: Prevenir colision teorica
8. **Eliminar key `current_sp_client_id`** sin prefijo (usar solo la version con prefijo `mf-marketing:`)
9. **Documentar patron de aislamiento**: Agregar guia en CLAUDE.md sobre como manejar localStorage y caches en contexto multi-tenant

---

## Risk Score: 5/10

**Justificacion:** La arquitectura actual tiene buena aislamiento a nivel de API (orgId en URLs) y estado compartido (localStorage con prefijos). Sin embargo, hay riesgos medios en caches in-memory, localStorage keys sin org scope, y ausencia de Authorization header. La mitigacion principal (full page reload al cambiar org) funciona pero es fragil ante futuros cambios de navegacion SPA. Para un sistema multi-tenant en produccion real, se recomienda resolver los items P0 antes de habilitar cambio de organizacion dinamico.
