# Portal de Clientes — Diseño Tecnico y de Producto

**Fecha:** 2026-04-30
**Estado:** Diseño aprobado — implementacion Phase 1 en curso
**Owner:** casp (BAATDIGITAL)
**Repos involucrados:** mf-whatsapp, mf-portal (nuevo), covacha-libs, covacha-core, covacha-payment

---

## 1. Resumen ejecutivo

Crear un portal web independiente donde los **clientes finales** del agency (POP Producciones, Vivero Nativa, BAATDIGITAL MTY, etc.) accedan a su WhatsApp Business como si fuera propio. El agency administra los accesos, planes de consumo, licencias y cobros recurrentes desde **mf-whatsapp**.

### Casos de uso

- **Vivero Nativa:** plan 200 conversaciones/mes, 5 usuarios. Cada usuario logea con `(numero personal, contraseña)`.
- **POP Producciones:** plan 500 conversaciones/mes, 5 usuarios. Uno de los usuarios tambien trabaja para BAATDIGITAL MTY y puede cambiar de cliente al vuelo.
- **BAATDIGITAL MTY:** cliente del agency que tambien opera como tenant.

### Objetivos

| # | Objetivo | Metrica de exito |
|---|----------|------------------|
| 1 | Portal accesible al cliente con UX premium | TTFB < 2s, login < 500ms |
| 2 | Aislamiento total de auth y data por cliente | 0 leaks cross-tenant |
| 3 | Multi-cliente fluido para usuarios con acceso multiple | Switch < 1s |
| 4 | Admin centralizado en mf-whatsapp | 1 sola UI para gestionar 100+ clientes |
| 5 | Cobro recurrente automatizado | 95%+ pagos exitosos sin intervencion |
| 6 | Enforcement de limites con avisos | 80/95/100% triggered correctamente |

---

## 2. Decisiones aprobadas (brainstorming sesion 2026-04-30)

| # | Decision | Aprobada |
|---|----------|----------|
| 1 | Auth: Cognito user pool **separado** `superpago-client-portal-users` | ✅ |
| 2 | URL: dominio unico `portal.superpago.com.mx` (subdomains como upgrade futuro) | ✅ |
| 3 | Capabilities: Tier 1 (chat) + Tier 2 (consumo propio) + Tier 3 (sub-admin del cliente) | ✅ |
| 4 | Conversacion = sesion 24h Meta. Enforcement hibrido: hard cap default + overage opt-in. Avisos 80/95/100% | ✅ |
| 5 | Multi-cliente UX: hibrido — selector grande primer login + dropdown header en sesiones siguientes | ✅ |
| 6 | Cobro: reutilizar `mf-payment-card` SDK + `covacha-payment/billpay_recurring` (NO Stripe) | ✅ |
| 7 | Admin module: hibrido — `/whatsapp/portal-admin` global + tabs en `/whatsapp/clients/:id` | ✅ |
| 8 | Diseño: command palette Cmd+K, dark/light/auto, theme branded por cliente, real-time feel via polling 15-30s | ✅ |

---

## 3. Arquitectura

### 3.1 Componentes

```
┌─────────────────────────────────────────────────────────────┐
│  CLOUDFRONT (mf.superpago.com.mx)                          │
│                                                              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐    │
│  │ mf-portal    │   │ mf-whatsapp  │   │  shell/core  │    │
│  │ (cliente     │   │ (agency:     │   │              │    │
│  │  final)      │   │  admin +     │   │              │    │
│  │              │   │  operacion)  │   │              │    │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘    │
└─────────┼───────────────────┼───────────────────┼───────────┘
          │                   │                   │
          ▼                   ▼                   ▼
   Cognito Pool 2      Cognito Pool 1      Cognito Pool 1
   (clientes)          (agency)            (agency)
          │                   │                   │
          └───────────────────┴───────────────────┘
                              │
                              ▼
              ┌──────────────────────────────┐
              │ API GW (api.superpago.com.mx)│
              └──────────────┬───────────────┘
                             │
        ┌────────────────────┼────────────────────────┐
        ▼                    ▼                        ▼
   covacha-core        covacha-botia           covacha-payment
   (whatsapp,          (chat sessions,         (subscriptions,
    organizations,      AI agents)              billpay,
    users,                                      recurring)
    licenses,                                   webhooks
    portal_users
    portal_grants)
```

### 3.2 Decisiones tecnicas clave

- **mf-portal** es un **MF nuevo** dedicado al cliente final. Reutiliza componentes del `mf-whatsapp` via Module Federation (chat, message-bubble, conversation-list) para no duplicar codigo. La UI es distinta (theme branded, layout simplificado, no expone admin/automation/analytics).
- **Cognito Pool 2** separado: usuarios cliente finales. Username = phone. Custom claim `client_grants: [{client_id, role}]` poblado desde `modIA_portal_grants` al login via Lambda trigger.
- **Datos de portal** en covacha-core (es el natural owner de organizations/users), no en covacha-botia (que es IA-specific).

---

## 4. Modelo de datos (DynamoDB)

Tablas nuevas en covacha-libs (prefijo `modIA_*` segun convencion existente):

### 4.1 `modIA_portal_users_prod`

Usuarios del portal (cliente final). 1 fila por persona.

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `id` | String (PK) | UUID4 del usuario portal |
| `cognito_sub` | String (GSI1 PK) | sub de Cognito Pool 2 |
| `phone_number` | String (GSI2 PK) | Username = numero personal en E.164 |
| `email` | String | Email del usuario (opcional, para recover) |
| `name` | String | Nombre completo |
| `status` | String | active / suspended / pending_invite |
| `last_login_at` | String (ISO8601) | Para tracking |
| `created_at` | String (ISO8601) | |
| `updated_at` | String (ISO8601) | |

**GSIs:**
- `GSI1`: `cognito_sub` (login lookup)
- `GSI2`: `phone_number` (busqueda admin)

### 4.2 `modIA_portal_grants_prod`

Permisos de usuario sobre cliente. 1 fila por (user, client) tupla.

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `user_id` | String (PK) | id de portal_users |
| `client_id` | String (SK) | id del cliente IA (POP, BAAT, etc.) |
| `role` | String | `operator` / `client_admin` |
| `allowed_phone_ids` | List<String> | phones del cliente que puede operar (vacio = todos) |
| `created_at` | String | |
| `created_by` | String | user_id agency que otorgo el grant |
| `revoked_at` | String | null si activo |

**GSIs:**
- `GSI1`: `client_id` (listar usuarios de un cliente)

### 4.3 `modIA_client_plans_prod`

Plan vigente del cliente. 1 fila por cliente.

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `client_id` | String (PK) | |
| `plan_name` | String | "basic-200", "premium-500", "custom" |
| `monthly_conversation_limit` | Number | 200, 500, 1000, etc. |
| `seat_limit` | Number | 5, 10, etc. |
| `overage_enabled` | Boolean | si permite excederse |
| `overage_price_mxn` | Decimal | $X por conversacion extra |
| `monthly_price_mxn` | Decimal | precio mensual del plan |
| `status` | String | active / suspended / cancelled |
| `started_at` | String (ISO) | inicio del plan actual |
| `next_billing_at` | String (ISO) | proxima fecha de cargo |
| `recurring_payment_id` | String | FK a billpay_recurring |
| `created_at` | String | |
| `updated_at` | String | |

### 4.4 `modIA_client_usage_prod`

Tracking de consumo por cliente por ciclo. Una fila por (client, ciclo-mes).

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `client_id` | String (PK) | |
| `cycle` | String (SK) | `2026-04` |
| `conversations_count` | Number | sesiones 24h iniciadas en el ciclo |
| `overage_count` | Number | excedidas del limite |
| `tokens_consumed` | Number | tokens IA si aplica |
| `last_conversation_at` | String (ISO) | |
| `alerts_fired` | Map | `{80: timestamp, 95: timestamp, 100: timestamp}` |
| `updated_at` | String | |

Update via DynamoDB UpdateItem con `ADD conversations_count 1` cada vez que el chat-controller detecta una conversacion nueva en ventana 24h.

### 4.5 `modIA_client_invites_prod`

Magic links de invitacion. 1 fila por invitacion.

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `token` | String (PK) | UUID4 secret |
| `client_id` | String | |
| `phone_number` | String | username destinado |
| `name` | String | nombre destinado |
| `email` | String | opcional |
| `role` | String | `operator` / `client_admin` |
| `allowed_phone_ids` | List<String> | |
| `expires_at` | String (ISO) | TTL DynamoDB |
| `used_at` | String | null si no usado |
| `created_by` | String | agency user que invito |

TTL automatico: 24h.

---

## 5. Endpoints backend (covacha-core)

### 5.1 Admin endpoints (agency, requiere admin role)

| Verbo | Path | Proposito |
|-------|------|-----------|
| GET | `/organization/<org>/portal/clients/<client_id>/users` | Listar usuarios con grant en cliente |
| POST | `/organization/<org>/portal/clients/<client_id>/users/invite` | Crear magic link |
| PATCH | `/organization/<org>/portal/grants/<grant_id>` | Cambiar rol/phones de un grant |
| DELETE | `/organization/<org>/portal/grants/<grant_id>` | Revocar |
| GET | `/organization/<org>/portal/clients/<client_id>/plan` | Plan actual |
| PUT | `/organization/<org>/portal/clients/<client_id>/plan` | Cambiar plan/limites |
| GET | `/organization/<org>/portal/clients/<client_id>/usage?cycle=YYYY-MM` | Consumo |
| GET | `/organization/<org>/portal/dashboard` | KPIs globales (MRR, alerts, etc.) |
| GET | `/organization/<org>/portal/alerts` | Stream de alertas |
| POST | `/organization/<org>/portal/intent` | Command palette (NL → action) |

### 5.2 Portal client endpoints (cliente final, autenticado en Cognito Pool 2)

| Verbo | Path | Proposito |
|-------|------|-----------|
| POST | `/portal/auth/redeem-invite` | Activar magic link → crear Cognito user |
| GET | `/portal/me` | Datos del usuario logueado |
| GET | `/portal/me/grants` | Clientes a los que tiene acceso |
| POST | `/portal/me/switch-client` | Cambiar cliente activo (refresh JWT) |
| GET | `/portal/clients/<client_id>/plan` | Plan visible para el cliente |
| GET | `/portal/clients/<client_id>/usage` | Su consumo |
| Reuse | `/whatsapp/conversations` | con clientId del JWT (no del body) |

### 5.3 Webhooks billpay (covacha-payment, ya existen)

- `recurring_payment_succeeded` → marcar cliente activo, reiniciar `usage`
- `recurring_payment_failed` → 1er fallo: warn email; 3er fallo: status=suspended, `client_admins` reciben email

---

## 6. Frontend

### 6.1 mf-portal (NUEVO)

Estructura:

```
mf-portal/
├── src/app/
│   ├── domain/models/         (PortalUser, ClientGrant, Plan, Usage)
│   ├── domain/ports/          (PortalAuthPort, PortalApiPort)
│   ├── infrastructure/adapters/
│   ├── application/           (state services, use cases)
│   ├── presentation/
│   │   ├── pages/
│   │   │   ├── login/
│   │   │   ├── invite-redeem/
│   │   │   ├── client-selector/  (post-login)
│   │   │   ├── chat/             (reusa de mf-whatsapp via federation)
│   │   │   ├── usage-dashboard/  (Tier 2)
│   │   │   ├── client-admin/     (Tier 3 - solo client_admin)
│   │   │   └── billing/          (ver propia tarjeta + pagos)
│   │   └── components/
│   │       ├── client-switcher/
│   │       ├── theme-provider/   (branded por cliente)
│   │       └── ...
│   └── shared/
└── federation.config.js (consume `chat`, `message-bubble`, `conversation-list` de mfWhatsapp)
```

### 6.2 mf-whatsapp — Admin module

```
src/app/presentation/pages/portal-admin/
├── command-center/        (dashboard global con KPIs + alerts feed)
├── command-palette/       (Cmd+K overlay)
├── components/
│   ├── kpi-card/
│   ├── client-row-sparkline/
│   ├── alert-feed/
│   └── usage-timeline/
```

Y en `client-detail` existing:

```
client-detail/
├── tabs/
│   ├── numeros/        (existe)
│   ├── conversaciones/ (existe)
│   ├── accesos/        (NUEVO - Tier 3)
│   ├── plan/           (NUEVO)
│   ├── uso/            (NUEVO)
│   └── billing/        (NUEVO - usa <sp-payment-card>)
```

### 6.3 Theme system

`mf-core` expone variables CSS extendidas:
- `--client-primary`, `--client-accent`, `--client-logo-url` set por TenantThemeService cuando se activa cliente
- Persiste en localStorage por usuario el theme dark/light/auto

---

## 7. Auth flow

### 7.1 Setup inicial (agency invita cliente)

1. Agency admin en `/whatsapp/clients/:id/accesos` click "Invitar usuario"
2. Modal: nombre, phone, email, rol, phones permitidos
3. Backend crea `client_invite` con token UUID4 + TTL 24h
4. Email enviado al cliente: `https://portal.superpago.com.mx/redeem?token=XXX`
5. Cliente abre link → form pide crear contraseña
6. Backend `POST /portal/auth/redeem-invite`:
   - Valida token y TTL
   - Crea Cognito user en pool 2 con username=phone
   - Crea registro `portal_users`
   - Crea `portal_grants` (user_id, client_id, role, phones)
   - Marca invite como usado
   - Devuelve JWT para auto-login

### 7.2 Login normal

1. Cliente va a `portal.superpago.com.mx/login`
2. Form: phone + password
3. Cognito `InitiateAuth` con USERNAME_AUTH
4. Lambda trigger `PreTokenGeneration` agrega claims:
   - `portal_user_id`
   - `client_grants: [{client_id, role, allowed_phone_ids}]`
5. Frontend recibe JWT, decodifica grants
6. **Si grants.length == 1**: entra directo al chat de ese cliente
7. **Si grants.length > 1**: muestra `client-selector` page
8. Al elegir cliente, llama `/portal/me/switch-client` que devuelve JWT con `active_client_id` agregado

### 7.3 Cambio de cliente (multi-tenant user)

- Click en dropdown header → `client-switcher` overlay
- Selecciona cliente B → `/portal/me/switch-client { client_id: B }`
- Backend valida grant existe + activo → emite nuevo JWT con `active_client_id: B`
- Frontend recarga state, theme, conversations

---

## 8. Phases / MVP scope

### Phase 1 — Foundations (1 sprint, paralelo)

**Backend:**
- covacha-libs: 5 nuevos modelos + 5 repos
- covacha-core: endpoints admin (users, plans, usage)
- Cognito Pool 2 manual setup + Lambda PreTokenGeneration
- covacha-payment: extender billpay_recurring para ligar `client_id`

**Frontend mf-whatsapp:**
- `/whatsapp/portal-admin` Command Center (dashboard solo lectura, sin Cmd+K aun)
- Tab `Accesos` en client detail (CRUD usuarios)

**Tests:**
- Unit tests backend pytest
- Specs Angular Karma

### Phase 2 — Plan + billing en admin (1 sprint)

- Tab `Plan` en client detail (cambiar plan/limites)
- Tab `Uso` en client detail (consumo + forecast)
- Tab `Billing` en client detail (sp-payment-card + invoices)
- Webhooks recurring → suspender cliente
- Avisos 80/95/100%

### Phase 3 — mf-portal cliente final (2 sprints)

- mf-portal scaffold + Module Federation con mf-whatsapp
- Login + redeem-invite + client-selector
- Chat reusing mfWhatsapp components
- Theme branded por cliente
- Tier 2: dashboard de consumo propio
- Tier 3: pagina de admin del cliente

### Phase 4 — Innovations (1 sprint)

- Command palette Cmd+K
- Real-time alerts feed
- Theme dark/light/auto
- Mobile/PWA polish
- e2e tests cross-portal (Playwright)

---

## 9. Tests

### 9.1 Unit (Karma + pytest)

- Cobertura >= 90% en codigo nuevo
- Mocks de Cognito y DynamoDB en backend

### 9.2 e2e (Playwright)

Suite nueva `tests/e2e/ep-008-portal-clientes/`:

- **HU-PC-001**: Magic link redeem → crea cuenta + login auto
- **HU-PC-002**: Login normal con phone+password
- **HU-PC-003**: Usuario con 1 cliente entra directo
- **HU-PC-004**: Usuario con 2+ clientes ve selector + cambia cliente
- **HU-PC-005**: Operador ve solo conversaciones de phones permitidos
- **HU-PC-006**: client_admin invita usuario nuevo
- **HU-PC-007**: Aviso 80% se muestra al cliente
- **HU-PC-008**: Hard cap bloquea envio cuando llega a 100%
- **HU-PC-009**: Overage opt-in permite seguir + factura extra
- **HU-PC-010**: Pago fallido N veces → suspende cliente

Suite admin en mf-whatsapp:

- **HU-PA-001**: Dashboard global muestra KPIs
- **HU-PA-002**: Tab Accesos lista usuarios
- **HU-PA-003**: Invitar usuario genera link
- **HU-PA-004**: Tab Plan permite cambiar limite
- **HU-PA-005**: Tab Uso muestra forecast
- **HU-PA-006**: Tab Billing carga sp-payment-card

---

## 10. Riesgos y mitigaciones

| Riesgo | Severidad | Mitigacion |
|--------|-----------|------------|
| Leak cross-tenant via JWT manipulado | Alta | Validacion server-side de active_client_id en cada request, claims firmadas |
| Cognito Pool 2 setup error → todos los clientes lockeados | Alta | Terraform/IaC para pool, smoke test post-deploy |
| Billing recurring falla silenciosamente | Media | Alarmas CloudWatch en webhook errors, daily reconciliation job |
| mf-portal vs mf-whatsapp shared components rompen federation | Media | Contract tests en CI, version pinning |
| Usage counter se desincroniza | Media | DynamoDB Streams + reconciliation cron diario |

---

## 11. Out of scope (v1)

- Subdominios por cliente (Opcion A) — futuro upgrade premium
- White-label custom domain (Opcion C) — enterprise tier
- Mobile native apps (iOS/Android)
- Integraciones SSO con Google/Microsoft del cliente
- Reportes ejecutivos en PDF descargables
- Rotacion automatica de phones entre clientes
- Multi-currency (solo MXN en v1)

---

## 12. Issues / tracking

Crear en GitHub Project SuperPago (#1):

- **EP-PC-001** Foundations backend (Phase 1 backend)
- **EP-PC-002** Admin module mf-whatsapp (Phase 1 frontend + Phase 2)
- **EP-PC-003** mf-portal cliente final (Phase 3)
- **EP-PC-004** Innovations + e2e (Phase 4)

Owner inicial: casp. Cada epic se descompondra en HU-PC-XXX al arrancar.
