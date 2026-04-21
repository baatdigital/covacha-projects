# Marketing Autonomy — Flujo de Publicación E2E

**Actualizado:** 2026-04-21
**Contexto:** Sesión de fixes del flujo aprobar → publicar en Facebook/Instagram

---

## 1. Flujo completo

```
Pipeline mensual (cron dia 1 6am UTC)
  ↓
content_creator_agent genera 12 items con scheduled_at distribuido en el mes
  ↓
Items persistidos en modmarketing_content_plan con status=PENDING_APPROVAL
  ↓
photo_director (DALL-E 3) + video_generator (Sora 2) generan media en paralelo
  ↓
propagate_media_urls asocia visual_url a cada item
  ↓
┌──────────────────────────────────┬────────────────────────────────────┐
│ FULL_AUTO + auto_publish=True    │ SEMI_AUTO                          │
│                                   │                                    │
│ auto_approve_and_schedule:        │ Usuario ve items en UI             │
│   items → status=APPROVED         │   (client-approvals tab)           │
│                                   │ Click "Aprobar" → vote endpoint    │
│                                   │ ApprovalRecord → APPROVED          │
│                                   │ _advance → item status=APPROVED    │
│                                   │ (fallback: cron reconcile 5min)    │
└──────────────────────────────────┴────────────────────────────────────┘
  ↓
Cron superpago-publish-scheduled (cada 15 min)
  ↓
Query items WHERE status=APPROVED AND scheduled_at <= now()
  ↓
Resuelve token del social_account del cliente:
  - facebook → page_id + facebook_page_access_token
  - instagram → instagram_business_account_id + page_access_token
  ↓
Meta Graph API:
  - Facebook: POST /{page_id}/photos or /{page_id}/feed
  - Instagram: POST /{ig_user_id}/media + /{ig_user_id}/media_publish
  ↓
Item → status=PUBLISHED, meta_post_id guardado
```

---

## 2. Modos de autonomía (spec confirmada 2026-04-21)

| Modo | Comportamiento | Auto-publish content |
|------|----------------|----------------------|
| **FULL_AUTO** | Pipeline genera → auto-aprueba → scheduler publica en `scheduled_at`. 0 intervención humana. | `true` obligatorio |
| **SEMI_AUTO** | Pipeline genera → items en `PENDING_APPROVAL`. Usuario aprueba manualmente en UI. Solo lo aprobado se publica en su `scheduled_at`. | `false` |
| **MANUAL** | Todo requiere intervención humana. Sin pipeline automático. | `false` |

**Clientes activos (org 39c56b2b)**:
- Super Pago → FULL_AUTO + auto_publish=true
- BAATDigital → SEMI_AUTO
- Vivero Nativa → SEMI_AUTO
- POP Producciones → FULL_AUTO + auto_publish=true (normalizado el 2026-04-21)
- Otros 6 → FULL_AUTO + auto_publish=true (normalizados)

---

## 3. EventBridge Rules (superpago-*)

| Rule | Cron | Endpoint | Propósito |
|------|------|----------|-----------|
| `superpago-client-marketing-monthly` | `cron(0 6 1 * ? *)` | `/ai/marketing/process-monthly` | Pipeline mensual cross-org, día 1 cada mes |
| `superpago-client-marketing-daily-eval` | `cron(0 8 * * ? *)` | `/ai/marketing/process-daily-evaluation` | Evaluación FULL_AUTO diaria |
| `superpago-publish-scheduled` | `rate(15 minutes)` | `/posts/publish-scheduled` | Publica items APPROVED due |
| `superpago-reconcile-approvals` | `rate(5 minutes)` | `/agency/approvals/reconcile` | Fallback: avanza items cuyo ApprovalRecord está APPROVED pero item sigue PENDING_APPROVAL |
| `superpago-token-refresh-daily` | `cron(0 5 * * ? *)` | `/meta/tokens/refresh-all` | Refresh tokens Meta antes de expirar |
| `superpago-model-optimizer-weekly` | `rate(7 days)` | - | Optimización LLM |

---

## 4. Tablas DynamoDB involucradas

| Tabla | PK/SK | Propósito |
|-------|-------|-----------|
| `modmarketing_content_plan` | `ORG#{org}#CLIENT#{client}` / `ITEM#{id}` | Content items con status + scheduled_at |
| `modmarketing_autonomy_config` | `ORG#{org}#CLIENT#{client}` / `AUTONOMY_CONFIG` | Mode, auto_publish, agents_enabled, objective_mix |
| `modcore_agency_prod` | `CONTENT#{id}` / `APPROVAL#{rec_id}` (+ GSI1) | ApprovalRecords, promociones |
| `modcore_social_accounts_prod` | `id` (HASH) | Tokens Meta (FB page, IG business, ad account) |
| `modcore_social_posts_prod` | - | Posts históricos sincronizados desde Meta |
| `modIA_org_credentials_prod` | `sp_organization_id` | OpenAI / Anthropic keys master |
| `modIA_client_credentials_prod` | `sp_client_id` + `sp_organization_id` | Override per-client |

---

## 5. Fixes aplicados en esta sesión (2026-04-20/21)

### 5.1. Botones Aprobar/Editar/Rechazar no funcionaban

**Root cause**: `submitVote` en frontend sin error handler → fallos silenciosos.

**Fix** (mf-marketing #160):
- Error handler con `emitToastError`
- Toast success por tipo de voto
- `submitting` signal para bloquear doble-click
- Si error es "already completed" → cierra modal + recarga

### 5.2. Landing final no muestra logo del cliente

**Root cause**: `CovAgencyPromotion` model no declaraba `logo_url` / `client_logo_url` → Pydantic los descartaba.

**Fix** (covacha-libs #28 + covacha-core #105):
- Agregar `logo_url`, `client_logo_url`, `hero_image_url` al modelo
- `_inherit_client_branding`: heredar `sp_clients.logo_url` → `promotion.client_logo_url` en create/update
- `_ensure_default_landing_sections`: agregar hero/features/plans/form si landing vacío

### 5.3. Botón Editar Promoción

**Root cause**: `router.navigate('/marketing/promotions/:id/edit')` hacía match con ruta pública `/promotions/:slug` → cargaba `PublicLandingComponent` en vez del editor. Ademas rutas del editor estaban anidadas en `MarketingLayoutComponent` que usa render signal-based (sin router-outlet).

**Fix** (mf-marketing #161): eliminar router nav; usar `PromotionEditorComponent` en modo `modal` directamente.

### 5.4. Publicación no funcionaba (FB/IG 0 posts)

**Bug 1**: Approval no avanzaba item → publisher no tenía nada que publicar.
  - `_advance_content_after_approval` solo tocaba `strategy.content_plan` (legacy)
  - Fix: también actualizar `modmarketing_content_plan.status` = APPROVED

**Bug 2**: No había cron del publisher.
  - Fix: creado `superpago-publish-scheduled` cada 15 min

**Bug 3**: Tokens Meta invalidados (code 190).
  - `/tokens/refresh-all` funciona pero NO recupera tokens invalidados por password change.
  - Requiere re-login manual vía OAuth en UI.

**Bug 4**: 409 Conflict al reconectar misma página.
  - `connect_meta_account` rechazaba si `find_duplicate` encontraba existing.
  - Fix (covacha-core #107/#110): si existe, actualizar token en lugar de rechazar.

**Bug 5**: Cuentas reconectadas quedaban con `client_id=NULL`.
  - Workaround manual: asignar `client_id` post-reconexión.
  - TODO: frontend debería mandar `client_id` en el payload.

**Bug 6**: IG publisher usaba FB page_id (error "Object does not exist").
  - Fix (covacha-core #109): leer `instagram_business_account_id` para IG, `platform_account_id` solo para FB.

**Bug 7**: `_advance` usaba `scan(Limit=2)` → DynamoDB aplica Limit ANTES del filter → 0 resultados.
  - Fix (covacha-core #111): Query targeted por PK + SK conocido (pasando `sp_client_id`). Fallback scan con paginación real.

**Bug 8 (crítico)**: Bug silencioso en runtime — aun tras los fixes, items aprobados via UI no avanzan.
  - **Workaround**: cron `superpago-reconcile-approvals` cada 5 min captura items stuck.
  - Endpoint: `POST /agency/approvals/reconcile`
  - Garantiza consistencia eventual.

### 5.5. ApprovalRecords huérfanos

**Problema**: Pipelines anteriores dejaron ApprovalRecords apuntando a items ARCHIVED. Votar sobre ellos no hacía nada visible.

**Fix** (cleanup script ejecutado 2026-04-21):
- 9 records huérfanos de BAAT marcados `system_status=DELETED`
- 35 nuevos records creados para items PENDING actuales de BAAT
- 12 records creados para Vivero Nativa
- 12 records creados para POP Producciones

### 5.6. Objective Mix 80/10/10

**Feature** (covacha-libs + covacha-botia + mf-marketing):
- `AutonomyConfig.objective_mix = {sales, brand, other}` (suma 1.0)
- `AutonomyConfig.conversion_progression = {baseline_rate, monthly_growth_pct, horizon_months}`
- Pipeline lee mix → strategy_planner + content_creator generan posts distribuidos
- UI con 3 sliders + 3 presets (Agresivo/Balanceado/Marca primero)
- Seed aplicado: BAATDigital + Vivero Nativa + Super Pago = 80/10/10

### 5.7. DALL-E 3 + jerarquía visual +150%

**Feature**:
- `TEXT_OVERLAY_SCALE=1.5` (env var)
- Title 48→72pt, Subtitle 32→48pt, CTA 28→42pt
- Prompt DALL-E: focal subject grande + espacios negativos para overlay

### 5.8. Sora 2 en paralelo a DALL-E 3

**Feature** (covacha-botia):
- `OpenAIVideoClient` Sora 2 con misma API key que DALL-E
- `video_generator_agent` dedicado (split del photo_director)
- Orchestrator corre ambos en paralelo en fase `GENERATE_MEDIA`
- reel → Sora MP4, image/carousel/story → DALL-E PNG

---

## 6. Troubleshooting

### Problema: "Aprobar no hace nada"
**Diagnóstico**:
1. Verificar que el ApprovalRecord está avanzando: `scan modcore_agency_prod, filter Id=X` → `status=APPROVED` ✓
2. Verificar que el item avanza: `query modmarketing_content_plan PK=ORG#..#CLIENT#.. SK=ITEM#..` → `status=APPROVED`
3. Si item sigue PENDING_APPROVAL: esperar ≤5 min (cron reconcile) O llamar manual:
   ```
   POST /organization/{org}/agency/approvals/reconcile
   ```

### Problema: "No publica en FB/IG"
**Diagnóstico**:
1. Verificar item `status=APPROVED AND scheduled_at <= now`
2. Verificar token de la account:
   ```python
   curl "https://graph.facebook.com/v18.0/me?access_token={token}"
   # Si HTTP 400 code=190 → token invalidado
   ```
3. Si token roto → refresh-all NO resuelve invalidados, requiere OAuth manual
4. Disparar publisher manual:
   ```
   POST /organization/{org}/posts/publish-scheduled
   ```

### Problema: "Reconectar da 409"
**Ya arreglado en PRs #107 y #110**. Si persiste, verificar que el deploy incluye esos commits.

### Problema: "Token refresh no recupera cuenta"
Si Meta invalidó el token (password change, security revoke):
- Requiere re-login manual en UI (OAuth flow)
- El endpoint `connect_meta_account` ahora UPDATEA el token existente (no 409)
- Si el frontend no manda `client_id` → queda `client_id=NULL` → se debe asignar manualmente

---

## 7. IDs y constantes útiles

- **Org BAAT Digital master**: `39c56b2b-cbec-4645-b4b3-7b618e5a8888`
- **Clientes principales**:
  - Super Pago: `0b9c6051-1a8f-410e-93fb-653cb5a928bc`
  - BAATDigital: `4418d182-c391-4e1e-a011-c6f1bd7537fd`
  - Vivero Nativa: `c16b40c2-a3b3-407a-9ac9-12336c2e60aa`
  - POP Producciones: `dd86f618-94d8-4837-97c3-b4e4b24aab1f`
  - Alerta Tribunales: `a58bb241-9098-40d7-b047-01f87315f8cc`
- **API key EventBridge**: `API-537711982667073685643885` (en Secrets Manager `events!connection/superpago-api-connection/9f0fb6d0-b5ee-42f2-bd72-69e83a9e11de`)
- **Role EventBridge**: `arn:aws:iam::705262650738:role/EventBridge-ApiDestination-Marketing`
- **API base**: `https://api.superpago.com.mx/api/v1`

---

## 8. TODOs pendientes

1. **Frontend**: `connect_meta_account` debe mandar `client_id` en el payload para que la nueva cuenta reconectada quede asignada al cliente correcto (sin `client_id=NULL` requerir fix manual)
2. **Backend**: Investigar por qué `_advance_content_after_approval` falla silenciosamente en runtime (posible caching de bytecode en EC2). El cron reconcile cada 5 min es el workaround actual.
3. **Pipeline**: Al archivar items viejos, también archivar sus ApprovalRecords asociados (actualmente dejan huérfanos).
4. **Meta Ads desde promoción**: Feature planeada para integrar campañas Meta Ads dentro del promotion-editor (`TODO: US-MK-XXX`).
