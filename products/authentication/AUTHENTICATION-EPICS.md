# Authentication - Epicas de Autenticacion y Autorizacion (EP-AU-001 a EP-AU-008)

**Fecha**: 2026-02-16
**Product Owner**: SuperPago / BaatDigital
**Estado**: Planificacion
**Prefijo Epicas**: EP-AU
**Prefijo User Stories**: US-AU

---

## Tabla de Contenidos

1. [Contexto y Motivacion](#contexto-y-motivacion)
2. [Arquitectura de Autenticacion](#arquitectura-de-autenticacion)
3. [Mapa de Epicas](#mapa-de-epicas)
4. [Epicas Detalladas](#epicas-detalladas)
5. [User Stories Detalladas](#user-stories-detalladas)
6. [Roadmap](#roadmap)
7. [Grafo de Dependencias](#grafo-de-dependencias)
8. [Riesgos y Mitigaciones](#riesgos-y-mitigaciones)

---

## Contexto y Motivacion

El modulo de Authentication es **P1 CRITICO** porque controla el acceso a todos los micro-frontends y APIs del ecosistema SuperPago/BaatDigital. Actualmente existe una implementacion basica (login, registro, JWT, roles simples). Las epicas aqui definidas extienden esa base hacia un sistema enterprise-grade.

### Repositorios Involucrados

| Repositorio | Funcion | Puerto Dev |
|-------------|---------|------------|
| `covacha-core` | Backend auth (Flask, Cognito, DynamoDB) | 5000 |
| `mf-auth` | Micro-frontend Angular 21 | 4201 |
| `covacha-libs` | Modelos y utilidades compartidas | N/A |
| `mf-core` | Shell - guards, interceptors, shared state | N/A |

### Capacidades Actuales vs Requeridas

| Capacidad | Estado Actual | Problema |
|-----------|--------------|----------|
| Login/Logout | Basico funcional | Sin MFA, sin device tracking |
| Roles y permisos | RBAC simple (3 roles) | Sin granularidad por recurso, sin herencia tenant>org |
| SSO empresarial | No existe | Clientes empresa no pueden usar su IdP corporativo |
| Gestion de sesiones | Token JWT sin tracking | Sin limite de sesiones, sin deteccion de anomalias |
| Onboarding multi-tenant | Manual | Sin flujo self-service, sin invitaciones |
| API Keys | No existe | Integraciones B2B dependen de JWT de usuario |
| Frontend mf-auth | Login/registro basico | Sin MFA wizard, sin profile, sin security settings |
| Compliance y auditoria | Logs basicos | Sin audit trail, sin politicas configurables |

---

## Arquitectura de Autenticacion

### Flujo General

```
Usuario (Browser/App)
    |
    v
mf-core (Shell) ──> mf-auth (Login/Register/MFA)
    |
    +── Guards: AuthGuard, RoleGuard, TenantGuard, MfaGuard
    +── Interceptor: TokenInterceptor (JWT attach + refresh)
    +── Shared State: covacha:auth, covacha:user, covacha:tenant
    |
    v
API Gateway (WAF) ──> api.superpago.com.mx
    |
    v
covacha-core (Flask)
    |
    +── /api/v1/auth/*         (login, register, mfa, tokens)
    +── /api/v1/users/*        (profile, sessions, security)
    +── /api/v1/roles/*        (RBAC management)
    +── /api/v1/permissions/*  (permission CRUD)
    +── /api/v1/sso/*          (SAML, OIDC config)
    +── /api/v1/api-keys/*     (API key management)
    +── /api/v1/audit/*        (audit logs)
    |
    v
AWS Cognito (User Pool por Tenant)
    |
    +── MFA: TOTP, SMS
    +── OAuth2: Authorization Code Flow
    +── Tokens: ID Token, Access Token, Refresh Token
    +── Triggers: Pre-Auth, Post-Auth, Pre-Token-Gen
    |
    v
DynamoDB (Single Table)
    |
    +── USER#{user_id}          ── Perfil extendido, preferencias
    +── ROLE#{role_id}          ── Definicion de roles
    +── PERM#{permission_id}    ── Permisos individuales
    +── SESSION#{session_id}    ── Sesiones activas + device info
    +── TENANT#{tenant_id}      ── Configuracion del tenant
    +── ORG#{org_id}            ── Organizacion + config auth
    +── APIKEY#{key_id}         ── API keys + scopes
    +── AUDIT#{timestamp}       ── Audit trail de auth
```

### Flujo MFA

```
Login (email + password)
    |
    v
Cognito: Verifica credenciales
    |
    +── MFA NO requerido ──> JWT emitido ──> Acceso completo
    |
    +── MFA requerido (TOTP/SMS/Email)
        |
        v
    mf-auth: Pantalla MFA Challenge
        |
        v
    Usuario ingresa codigo
        |
        v
    Cognito: Verifica TOTP/SMS/Email
        |
        +── Valido ──> JWT con claim mfa_verified=true ──> Acceso completo
        +── Invalido ──> Retry (max 3) ──> Lockout temporal
```

### Multi-Tenant Auth Flow

```
Usuario visita app.superpago.com.mx
    |
    v
mf-core detecta dominio ──> Resuelve tenant_id
    |
    v
mf-auth carga branding del tenant (logo, colores, textos)
    |
    v
Login ──> Cognito User Pool (compartido, con custom attribute tenant_id)
    |
    v
Post-Auth Lambda Trigger:
    +── Verifica que usuario pertenece al tenant del dominio
    +── Inyecta claims: tenant_id, org_id, roles[], permissions[]
    |
    v
JWT emitido con claims multi-tenant
    |
    v
covacha-core valida JWT + verifica tenant_id en cada request
```

### Modelo de Datos DynamoDB

```
# Perfil extendido de usuario
PK: USER#{user_id}
SK: PROFILE
Campos: email, name, phone, avatar_url, mfa_enabled, mfa_methods[],
        preferred_locale, last_login, login_count, status

# Membresia usuario-organizacion
PK: USER#{user_id}
SK: ORG#{org_id}
Campos: role_id, permissions_override[], joined_at, invited_by, status
GSI-1: PK=ORG#{org_id}#MEMBERS, SK=USER#{user_id}

# Definicion de roles
PK: ROLE#{role_id}
SK: DEFINITION
Campos: name, description, permissions[], tenant_id, org_id, is_system, created_by
GSI-2: PK=TENANT#{tenant_id}#ROLES, SK=ROLE#{role_id}

# Permisos
PK: PERM#{permission_id}
SK: DEFINITION
Campos: resource, action, scope, description

# Sesiones activas
PK: SESSION#{session_id}
SK: DETAIL
Campos: user_id, device_fingerprint, ip, geo_location, user_agent,
        created_at, last_activity, expires_at, is_active
GSI-3: PK=USER#{user_id}#SESSIONS, SK={created_at}

# Configuracion auth por tenant
PK: TENANT#{tenant_id}
SK: AUTH_CONFIG
Campos: mfa_policy, password_policy, session_policy, sso_config,
        branding, allowed_domains, max_sessions_per_user

# Configuracion auth por organizacion
PK: ORG#{org_id}
SK: AUTH_CONFIG
Campos: mfa_required, password_policy_override, session_limit,
        ip_whitelist, sso_provider_id, auto_provision

# API Keys
PK: APIKEY#{key_prefix}
SK: DETAIL
Campos: org_id, name, scopes[], rate_limit, created_by, created_at,
        last_used, expires_at, is_active, hashed_key
GSI-4: PK=ORG#{org_id}#APIKEYS, SK=APIKEY#{key_prefix}

# Audit trail
PK: AUDIT#AUTH#{org_id}
SK: {timestamp}#{event_id}
Campos: user_id, action, resource, ip, device, result, details
GSI-5: PK=AUDIT#USER#{user_id}, SK={timestamp}
TTL: 365 dias

# SSO Provider Config
PK: ORG#{org_id}
SK: SSO_PROVIDER#{provider_id}
Campos: type (SAML|OIDC), metadata_url, client_id, client_secret_ref,
        role_mapping, auto_provision, enabled
```

---

## Mapa de Epicas

| ID | Epica | Complejidad | Sprint | Dependencias |
|----|-------|-------------|--------|--------------|
| EP-AU-001 | Autenticacion Multi-Factor (MFA) | L | 1-2 | Ninguna |
| EP-AU-002 | Gestion Avanzada de Roles y Permisos (RBAC) | XL | 1-3 | Ninguna (paralela) |
| EP-AU-003 | Single Sign-On (SSO) Empresarial | L | 3-4 | EP-AU-002 |
| EP-AU-004 | Gestion de Sesiones y Seguridad | L | 2-3 | EP-AU-001 |
| EP-AU-005 | Onboarding Multi-Tenant | M | 3-4 | EP-AU-002, EP-AU-004 |
| EP-AU-006 | API Keys y Service Accounts | M | 4-5 | EP-AU-002 |
| EP-AU-007 | Frontend mf-auth Completo | XL | 2-5 | EP-AU-001, EP-AU-002, EP-AU-004 |
| EP-AU-008 | Compliance y Auditoria de Acceso | L | 4-5 | EP-AU-004, EP-AU-002 |

**Totales:**
- 8 epicas
- 45 user stories (US-AU-001 a US-AU-045)
- Estimacion total: ~110-140 dev-days

---

## Epicas Detalladas

---

### EP-AU-001: Autenticacion Multi-Factor (MFA)

**Objetivo**: Implementar MFA con TOTP, SMS y Email como segundo factor, con enrollment guiado, recovery codes y remember device. Obligatorio para operaciones financieras.

**User Stories:** US-AU-001 a US-AU-006

**Criterios de Aceptacion de la Epica:**
- [ ] TOTP enrollment con QR code (Google Authenticator, Authy)
- [ ] SMS como segundo factor via Cognito + SNS
- [ ] Email como segundo factor via Cognito + SES
- [ ] Recovery codes (10 codigos de un solo uso) generados al enrollar
- [ ] Remember device por 30 dias (configurable por tenant)
- [ ] MFA obligatorio para operaciones financieras (SPEI, BillPay)
- [ ] Politica MFA configurable por tenant y por organizacion
- [ ] Bypass de emergencia por SuperAdmin con audit trail
- [ ] Tests >= 98% coverage

**Dependencias:** Ninguna
**Complejidad:** L
**Repositorios:** covacha-core, mf-auth, covacha-libs

---

### EP-AU-002: Gestion Avanzada de Roles y Permisos (RBAC)

**Objetivo**: Sistema granular de roles con herencia tenant > org > project. Permisos por recurso y accion. UI de gestion completa.

**User Stories:** US-AU-007 a US-AU-012

**Criterios de Aceptacion de la Epica:**
- [ ] 6 roles del sistema: SuperAdmin, TenantAdmin, OrgAdmin, OrgManager, OrgUser, ReadOnly
- [ ] Roles custom creables por TenantAdmin y OrgAdmin
- [ ] Permisos granulares: resource:action (ej: accounts:read, transactions:write)
- [ ] Herencia: permisos del tenant aplican a todas sus orgs, permisos de org aplican a sus usuarios
- [ ] Override: una org puede restringir (no expandir) permisos heredados del tenant
- [ ] API CRUD completa para roles y permisos
- [ ] Middleware de autorizacion en cada endpoint: `@requires_permission('resource:action')`
- [ ] UI de gestion de roles en mf-auth
- [ ] Tests >= 98% coverage

**Dependencias:** Ninguna (puede empezar en paralelo con EP-AU-001)
**Complejidad:** XL
**Repositorios:** covacha-core, mf-auth, covacha-libs

---

### EP-AU-003: Single Sign-On (SSO) Empresarial

**Objetivo**: Soporte SAML 2.0 y OpenID Connect para clientes empresa. Configuracion por organizacion con mapeo de roles y auto-provisioning.

**User Stories:** US-AU-013 a US-AU-017

**Criterios de Aceptacion de la Epica:**
- [ ] SAML 2.0 SP-initiated flow funcional
- [ ] OpenID Connect Authorization Code flow funcional
- [ ] Configuracion SSO por organizacion (no por tenant global)
- [ ] Mapeo de atributos/claims externos a roles internos
- [ ] Auto-provisioning: crear usuario automaticamente en primer login SSO
- [ ] Just-in-time provisioning con asignacion de rol default
- [ ] Desactivacion de password login cuando SSO esta activo para una org
- [ ] UI de configuracion SSO para OrgAdmin
- [ ] Tests >= 98% coverage

**Dependencias:** EP-AU-002 (necesita roles para mapeo)
**Complejidad:** L
**Repositorios:** covacha-core, mf-auth

---

### EP-AU-004: Gestion de Sesiones y Seguridad

**Objetivo**: Control avanzado de sesiones con device fingerprinting, geo-location, deteccion de anomalias y cierre remoto.

**User Stories:** US-AU-018 a US-AU-023

**Criterios de Aceptacion de la Epica:**
- [ ] Sesiones activas rastreadas en DynamoDB con device info
- [ ] Limite configurable de sesiones concurrentes por usuario (default: 5)
- [ ] Device fingerprinting (browser, OS, screen, timezone)
- [ ] Geo-location por IP (pais, ciudad)
- [ ] Deteccion de login desde ubicacion inusual
- [ ] Cierre remoto de sesiones desde UI y API
- [ ] Notificacion al usuario en login desde nuevo dispositivo
- [ ] Audit log de todas las operaciones de autenticacion
- [ ] Tests >= 98% coverage

**Dependencias:** EP-AU-001 (MFA para challenge en login sospechoso)
**Complejidad:** L
**Repositorios:** covacha-core, mf-auth, covacha-libs

---

### EP-AU-005: Onboarding Multi-Tenant

**Objetivo**: Flujo de registro diferenciado por tenant con invitaciones, self-service y aprobacion por admin.

**User Stories:** US-AU-024 a US-AU-028

**Criterios de Aceptacion de la Epica:**
- [ ] Flujo de registro adaptado al tenant (branding, campos, validaciones)
- [ ] Invitaciones por email con link de registro pre-aprobado
- [ ] Self-service registration con aprobacion pendiente por OrgAdmin
- [ ] Welcome wizard personalizado por tenant (pasos configurables)
- [ ] Activacion de cuenta por email (verificacion obligatoria)
- [ ] Asignacion automatica de rol default al registrar
- [ ] Dashboard de invitaciones pendientes para OrgAdmin
- [ ] Tests >= 98% coverage

**Dependencias:** EP-AU-002 (roles para asignacion), EP-AU-004 (sesiones)
**Complejidad:** M
**Repositorios:** covacha-core, mf-auth

---

### EP-AU-006: API Keys y Service Accounts

**Objetivo**: API keys para integraciones B2B con scopes granulares, rate limiting, rotacion y dashboard de uso.

**User Stories:** US-AU-029 a US-AU-033

**Criterios de Aceptacion de la Epica:**
- [ ] Generacion de API keys con prefijo identificable (sk_live_, sk_test_)
- [ ] Scopes granulares alineados con permisos RBAC
- [ ] Rate limiting por key (configurable, default 1000 req/min)
- [ ] Rotacion de keys sin downtime (periodo de gracia de 24h para key vieja)
- [ ] Dashboard de uso: requests/dia, endpoints mas usados, errores
- [ ] Service accounts para comunicacion inter-microservicio
- [ ] Expiracion configurable (30, 90, 365 dias, sin expiracion)
- [ ] Revocacion inmediata con propagacion en < 1 minuto
- [ ] Tests >= 98% coverage

**Dependencias:** EP-AU-002 (scopes basados en permisos RBAC)
**Complejidad:** M
**Repositorios:** covacha-core, mf-auth, covacha-libs

---

### EP-AU-007: Frontend mf-auth Completo

**Objetivo**: UI completa de autenticacion: login multi-tenant, MFA wizard, profile, security settings, session manager, role viewer.

**User Stories:** US-AU-034 a US-AU-040

**Criterios de Aceptacion de la Epica:**
- [ ] Login page con branding dinamico por tenant (logo, colores, textos)
- [ ] MFA enrollment wizard paso a paso (TOTP, SMS, Email)
- [ ] Pagina de perfil de usuario con edicion
- [ ] Security settings: cambio de password, MFA config, sesiones activas
- [ ] Session manager: lista de sesiones con cierre remoto
- [ ] Role viewer: ver roles y permisos asignados
- [ ] Password policies UI: indicador de fortaleza, reglas visibles
- [ ] Responsive mobile-first
- [ ] Shared state sync via BroadcastChannel (covacha:auth, covacha:user)
- [ ] Tests >= 98% coverage

**Dependencias:** EP-AU-001 (MFA), EP-AU-002 (roles), EP-AU-004 (sesiones)
**Complejidad:** XL
**Repositorios:** mf-auth, mf-core

---

### EP-AU-008: Compliance y Auditoria de Acceso

**Objetivo**: Audit trail completo, reportes de acceso, politicas configurables y compliance GDPR.

**User Stories:** US-AU-041 a US-AU-045

**Criterios de Aceptacion de la Epica:**
- [ ] Audit trail completo de login, logout, MFA, cambio de roles, acceso a recursos
- [ ] Reportes de acceso por usuario, por organizacion, por rango de fechas
- [ ] Politicas de contrasenas configurables por org (longitud, complejidad, rotacion)
- [ ] Account lockout configurable (intentos fallidos, duracion del lockout)
- [ ] GDPR: derecho al olvido (anonimizacion de datos de usuario)
- [ ] GDPR: exportacion de datos personales en formato portable
- [ ] Retencion configurable de logs de auditoria (default 365 dias)
- [ ] Dashboard de compliance para TenantAdmin
- [ ] Tests >= 98% coverage

**Dependencias:** EP-AU-004 (sesiones), EP-AU-002 (roles)
**Complejidad:** L
**Repositorios:** covacha-core, mf-auth

---

## User Stories Detalladas

---

### EP-AU-001: Autenticacion Multi-Factor (MFA)

---

#### US-AU-001: Enrollment TOTP (Google Authenticator)

**ID:** US-AU-001
**Epica:** EP-AU-001
**Prioridad:** P0
**Story Points:** 5

**Como** Usuario del ecosistema
**Quiero** enrollar mi cuenta con TOTP usando Google Authenticator o Authy
**Para** tener un segundo factor de autenticacion que proteja mi cuenta contra accesos no autorizados

**Criterios de Aceptacion:**
- [ ] Endpoint `POST /api/v1/auth/mfa/totp/setup` genera secret + QR code URI
- [ ] El secret se registra en Cognito via `associate_software_token`
- [ ] QR code incluye issuer="SuperPago" y account=email del usuario
- [ ] Endpoint `POST /api/v1/auth/mfa/totp/verify` valida codigo TOTP y confirma enrollment
- [ ] Al confirmar, se generan 10 recovery codes de 8 caracteres alfanumericos
- [ ] Recovery codes se almacenan hasheados (bcrypt) en DynamoDB `USER#{id}/MFA_RECOVERY`
- [ ] Se actualiza `USER#{id}/PROFILE` con `mfa_enabled=true, mfa_methods=['TOTP']`
- [ ] Si ya tiene MFA activo, requiere verificacion MFA actual antes de cambiar

**Notas Tecnicas:**
- Usar `pyotp` para generacion de secret y verificacion
- Cognito `AssociateSoftwareToken` + `VerifySoftwareTokenCommand`
- QR code como data URI (base64 PNG) generado server-side con `qrcode` lib

**Dependencias:** Ninguna

---

#### US-AU-002: MFA via SMS y Email

**ID:** US-AU-002
**Epica:** EP-AU-001
**Prioridad:** P0
**Story Points:** 5

**Como** Usuario del ecosistema
**Quiero** usar SMS o email como segundo factor de autenticacion
**Para** tener alternativas a TOTP si no tengo acceso a una app de autenticacion

**Criterios de Aceptacion:**
- [ ] Endpoint `POST /api/v1/auth/mfa/sms/setup` registra numero de telefono para MFA SMS
- [ ] Verificacion del numero via OTP de 6 digitos enviado por SNS
- [ ] Endpoint `POST /api/v1/auth/mfa/email/setup` registra email alternativo para MFA email
- [ ] Verificacion del email via OTP de 6 digitos enviado por SES
- [ ] OTP expira en 5 minutos, maximo 3 intentos
- [ ] Cognito configurado con `SMS_MFA` y custom challenge para email
- [ ] Rate limit: maximo 5 OTPs por hora por usuario
- [ ] Se actualiza `mfa_methods[]` con el metodo enrollado

**Notas Tecnicas:**
- SMS via Cognito native (SNS backend)
- Email MFA via Cognito Custom Auth Challenge (Lambda triggers)
- Numero en formato E.164

**Dependencias:** Ninguna

---

#### US-AU-003: MFA Challenge en Login

**ID:** US-AU-003
**Epica:** EP-AU-001
**Prioridad:** P0
**Story Points:** 5

**Como** Sistema
**Quiero** solicitar el segundo factor despues de verificar credenciales cuando MFA esta activo
**Para** asegurar que solo el dueno de la cuenta pueda acceder incluso si la contrasena se compromete

**Criterios de Aceptacion:**
- [ ] Login flow: `POST /api/v1/auth/login` retorna `{ challenge: 'MFA_REQUIRED', session: '...', methods: ['TOTP','SMS'] }` si MFA activo
- [ ] Endpoint `POST /api/v1/auth/mfa/challenge` acepta `{ session, method, code }`
- [ ] Si metodo es TOTP: verifica codigo con Cognito `respond_to_auth_challenge`
- [ ] Si metodo es SMS: Cognito envia OTP automaticamente, usuario responde con codigo
- [ ] Si metodo es Email: se envia OTP via SES, usuario responde con codigo
- [ ] Maximo 3 intentos por challenge session antes de expirar
- [ ] Challenge session expira en 3 minutos
- [ ] Despues de 5 challenges fallidos consecutivos: lockout de 15 minutos
- [ ] JWT emitido post-MFA incluye claim `mfa_verified: true`

**Notas Tecnicas:**
- Cognito `InitiateAuth` → `RespondToAuthChallenge` flow
- Session token temporal entre step 1 y step 2

**Dependencias:** US-AU-001, US-AU-002

---

#### US-AU-004: Recovery Codes

**ID:** US-AU-004
**Epica:** EP-AU-001
**Prioridad:** P1
**Story Points:** 3

**Como** Usuario del ecosistema
**Quiero** tener codigos de recuperacion de un solo uso para acceder si pierdo mi dispositivo MFA
**Para** no quedarme bloqueado de mi cuenta permanentemente

**Criterios de Aceptacion:**
- [ ] 10 recovery codes generados al enrollar MFA (US-AU-001)
- [ ] Cada codigo: 8 caracteres alfanumericos, formato XXXX-XXXX
- [ ] Codigos almacenados como hash bcrypt en DynamoDB
- [ ] Endpoint `POST /api/v1/auth/mfa/recovery` acepta recovery code como alternativa a TOTP/SMS
- [ ] Cada codigo es de un solo uso, se marca como usado al verificar
- [ ] Endpoint `POST /api/v1/auth/mfa/recovery/regenerate` genera nuevos 10 codigos (invalida anteriores)
- [ ] Requiere autenticacion completa (password + MFA activo) para regenerar
- [ ] Cuando quedan <= 2 codigos sin usar, mostrar alerta en UI

**Notas Tecnicas:**
- Almacenar en `PK: USER#{id}, SK: MFA_RECOVERY#{code_index}`
- Hash con bcrypt, comparar con `bcrypt.checkpw()`

**Dependencias:** US-AU-001

---

#### US-AU-005: Remember Device

**ID:** US-AU-005
**Epica:** EP-AU-001
**Prioridad:** P1
**Story Points:** 3

**Como** Usuario del ecosistema
**Quiero** marcar un dispositivo como "recordado" para no tener que ingresar MFA cada vez
**Para** tener conveniencia sin sacrificar seguridad en dispositivos de confianza

**Criterios de Aceptacion:**
- [ ] Checkbox "Recordar este dispositivo" en pantalla MFA challenge
- [ ] Si marcado: se genera cookie segura `sp_device_token` (HttpOnly, Secure, SameSite=Strict)
- [ ] Device token almacenado en DynamoDB `SESSION#{device_token}/DEVICE_TRUST`
- [ ] Duracion configurable por tenant (default 30 dias)
- [ ] En login subsecuente: si device token valido, skip MFA challenge
- [ ] Endpoint `DELETE /api/v1/auth/devices/{device_id}/trust` revoca confianza
- [ ] Maximo 5 dispositivos de confianza por usuario
- [ ] SuperAdmin puede revocar todos los dispositivos de un usuario

**Notas Tecnicas:**
- Cognito `ConfirmDevice` + `UpdateDeviceStatus` para device tracking
- Device fingerprint = hash(user_agent + screen_res + timezone + platform)

**Dependencias:** US-AU-003

---

#### US-AU-006: MFA Obligatorio para Operaciones Financieras

**ID:** US-AU-006
**Epica:** EP-AU-001
**Prioridad:** P0
**Story Points:** 5

**Como** Sistema
**Quiero** requerir verificacion MFA antes de ejecutar operaciones financieras criticas
**Para** prevenir transferencias no autorizadas incluso si un atacante obtiene el JWT

**Criterios de Aceptacion:**
- [ ] Decorator `@requires_mfa_step_up` en endpoints criticos (SPEI out, BillPay, cambio de beneficiarios)
- [ ] Si JWT tiene `mfa_verified=true` pero `mfa_verified_at` > 15 minutos: solicitar re-verificacion
- [ ] Endpoint `POST /api/v1/auth/mfa/step-up` emite token de corta vida (5 min) para la operacion
- [ ] Step-up token vinculado a la operacion especifica (no reutilizable)
- [ ] Si usuario no tiene MFA enrollado y la operacion lo requiere: forzar enrollment primero
- [ ] Politica configurable por tenant: lista de endpoints que requieren MFA step-up
- [ ] Audit log de cada step-up: usuario, operacion, resultado, timestamp

**Notas Tecnicas:**
- Step-up token como JWT adicional de corta vida con claim `step_up_for: 'spei_out'`
- Almacenar en DynamoDB con TTL de 5 minutos para invalidacion

**Dependencias:** US-AU-003

---

### EP-AU-002: Gestion Avanzada de Roles y Permisos (RBAC)

---

#### US-AU-007: Modelo de Roles del Sistema

**ID:** US-AU-007
**Epica:** EP-AU-002
**Prioridad:** P0
**Story Points:** 5

**Como** Sistema
**Quiero** definir una jerarquia de roles con permisos predeterminados
**Para** controlar el acceso granular a recursos segun la responsabilidad de cada usuario

**Criterios de Aceptacion:**
- [ ] 6 roles del sistema (no editables, no eliminables):
  - `SuperAdmin`: acceso total a todos los tenants y orgs
  - `TenantAdmin`: acceso total dentro de su tenant, gestiona orgs
  - `OrgAdmin`: acceso total dentro de su org, gestiona usuarios y roles
  - `OrgManager`: lectura/escritura en su org, sin gestion de usuarios
  - `OrgUser`: lectura/escritura limitada a recursos asignados
  - `ReadOnly`: solo lectura en recursos de su org
- [ ] Cada rol tiene lista de permissions predeterminadas
- [ ] Roles almacenados en DynamoDB `ROLE#{role_id}/DEFINITION` con `is_system=true`
- [ ] Endpoint `GET /api/v1/roles` lista roles disponibles segun contexto (tenant/org)
- [ ] Endpoint `GET /api/v1/roles/{role_id}` detalle con permisos incluidos
- [ ] Seed automatico: roles del sistema se crean al inicializar la DB

**Notas Tecnicas:**
- Roles del sistema con IDs fijos: `role_superadmin`, `role_tenant_admin`, etc.
- Permisos como strings: `resource:action` (ej: `accounts:read`, `transactions:write`)

**Dependencias:** Ninguna

---

#### US-AU-008: Permisos Granulares por Recurso

**ID:** US-AU-008
**Epica:** EP-AU-002
**Prioridad:** P0
**Story Points:** 5

**Como** TenantAdmin
**Quiero** definir permisos granulares por recurso y accion
**Para** controlar exactamente que puede hacer cada rol en cada parte del sistema

**Criterios de Aceptacion:**
- [ ] Catalogo de recursos: `accounts`, `transactions`, `reports`, `settings`, `users`, `roles`, `api_keys`, `audit`, `billing`, `notifications`
- [ ] Acciones por recurso: `read`, `write`, `delete`, `admin`
- [ ] Formato permiso: `{resource}:{action}` (ej: `accounts:read`, `users:admin`)
- [ ] Permiso wildcard: `accounts:*` (todas las acciones en accounts)
- [ ] Permisos almacenados en DynamoDB `PERM#{permission_id}/DEFINITION`
- [ ] Endpoint `GET /api/v1/permissions` lista todo el catalogo de permisos
- [ ] Endpoint `GET /api/v1/permissions/resources` lista recursos disponibles
- [ ] Middleware Flask `@requires_permission('resource:action')` valida en cada request
- [ ] Middleware verifica permisos del JWT claims o consulta DynamoDB si no estan en claims

**Notas Tecnicas:**
- Permisos inyectados en JWT via Cognito Pre-Token-Generation Lambda trigger
- Si la lista de permisos excede el limite de claims JWT (5KB), usar lookup a DynamoDB

**Dependencias:** US-AU-007

---

#### US-AU-009: Herencia de Permisos Tenant > Org

**ID:** US-AU-009
**Epica:** EP-AU-002
**Prioridad:** P0
**Story Points:** 5

**Como** Sistema
**Quiero** implementar herencia de permisos desde tenant hacia organizaciones
**Para** que los permisos definidos a nivel tenant apliquen automaticamente a todas sus orgs sin configuracion manual

**Criterios de Aceptacion:**
- [ ] Cada tenant tiene un "permission set" que define el maximo de permisos disponibles
- [ ] Cada org dentro del tenant hereda esos permisos por default
- [ ] OrgAdmin puede RESTRINGIR (no expandir) permisos heredados del tenant
- [ ] Resolucion de permisos: `effective_permissions = tenant_permissions INTERSECT org_permissions INTERSECT role_permissions`
- [ ] Endpoint `GET /api/v1/organizations/{org_id}/effective-permissions` retorna permisos efectivos
- [ ] Si tenant remueve un permiso, se propaga automaticamente a todas las orgs
- [ ] Cache de permisos efectivos con invalidacion en cambios (TTL 5 min)
- [ ] Endpoint `PUT /api/v1/organizations/{org_id}/permission-overrides` para restricciones de org

**Notas Tecnicas:**
- Resolucion lazy: calcular en cada request y cachear resultado
- Invalidar cache via SQS event cuando cambian permisos de tenant u org

**Dependencias:** US-AU-007, US-AU-008

---

#### US-AU-010: Roles Custom por Organizacion

**ID:** US-AU-010
**Epica:** EP-AU-002
**Prioridad:** P1
**Story Points:** 3

**Como** OrgAdmin
**Quiero** crear roles personalizados con combinaciones especificas de permisos
**Para** adaptar el control de acceso a la estructura y necesidades de mi organizacion

**Criterios de Aceptacion:**
- [ ] Endpoint `POST /api/v1/organizations/{org_id}/roles` crea rol custom
- [ ] Campos requeridos: name, description, permissions[]
- [ ] Solo puede incluir permisos que la org tiene efectivos (no puede escalar privilegios)
- [ ] Endpoint `PUT /api/v1/organizations/{org_id}/roles/{role_id}` edita rol custom
- [ ] Endpoint `DELETE /api/v1/organizations/{org_id}/roles/{role_id}` elimina (solo si no tiene usuarios asignados)
- [ ] Maximo 20 roles custom por organizacion
- [ ] Nombre de rol unico dentro de la organizacion
- [ ] Roles custom almacenados con `is_system=false` y `org_id` en DynamoDB

**Notas Tecnicas:**
- Validar que permissions[] es subconjunto de org effective permissions
- Al eliminar, ofrecer reasignar usuarios a otro rol

**Dependencias:** US-AU-009

---

#### US-AU-011: Asignacion de Roles a Usuarios

**ID:** US-AU-011
**Epica:** EP-AU-002
**Prioridad:** P0
**Story Points:** 3

**Como** OrgAdmin
**Quiero** asignar y cambiar roles de usuarios dentro de mi organizacion
**Para** controlar el nivel de acceso de cada miembro del equipo

**Criterios de Aceptacion:**
- [ ] Endpoint `PUT /api/v1/organizations/{org_id}/users/{user_id}/role` asigna rol
- [ ] Solo OrgAdmin o superior puede asignar roles
- [ ] No puede asignar rol superior al propio (OrgAdmin no puede crear otro OrgAdmin sin TenantAdmin)
- [ ] Cambio de rol toma efecto inmediato (invalidar cache de permisos)
- [ ] Endpoint `GET /api/v1/organizations/{org_id}/users` lista usuarios con sus roles
- [ ] Endpoint `GET /api/v1/organizations/{org_id}/users/{user_id}/permissions` lista permisos efectivos del usuario
- [ ] Audit log del cambio de rol: who, from_role, to_role, timestamp
- [ ] Notificacion por email al usuario cuando su rol cambia

**Notas Tecnicas:**
- Actualizar `PK: USER#{id}, SK: ORG#{org_id}` con nuevo `role_id`
- Invalidar JWT: agregar a blacklist o esperar expiracion (configurable)

**Dependencias:** US-AU-007, US-AU-010

---

#### US-AU-012: Middleware de Autorizacion

**ID:** US-AU-012
**Epica:** EP-AU-002
**Prioridad:** P0
**Story Points:** 5

**Como** Sistema
**Quiero** un middleware que valide permisos automaticamente en cada endpoint
**Para** garantizar que ningun endpoint sea accesible sin la autorizacion correspondiente

**Criterios de Aceptacion:**
- [ ] Decorator `@requires_permission('resource:action')` para Flask endpoints
- [ ] Decorator `@requires_role('OrgAdmin')` para validar rol minimo
- [ ] Decorator `@requires_any_permission(['perm1', 'perm2'])` para OR de permisos
- [ ] Decorator `@requires_all_permissions(['perm1', 'perm2'])` para AND de permisos
- [ ] Middleware extrae user_id, org_id, tenant_id del JWT
- [ ] Resuelve permisos efectivos (cache primero, DynamoDB fallback)
- [ ] Respuesta 403 estandarizada: `{ error: 'FORBIDDEN', message: 'Permission required: accounts:write', required: 'accounts:write' }`
- [ ] Log de acceso denegado para auditoria
- [ ] Performance: resolucion de permisos < 10ms (con cache activo)
- [ ] Todos los endpoints existentes migrados a usar decorators

**Notas Tecnicas:**
- Implementar en covacha-libs para compartir entre todos los backends
- Cache en memoria (dict) con TTL de 5 min, invalidacion por SQS

**Dependencias:** US-AU-008, US-AU-009

---

### EP-AU-003: Single Sign-On (SSO) Empresarial

---

#### US-AU-013: Configuracion SAML 2.0

**ID:** US-AU-013
**Epica:** EP-AU-003
**Prioridad:** P1
**Story Points:** 5

**Como** OrgAdmin de empresa
**Quiero** configurar SAML 2.0 como proveedor de identidad para mi organizacion
**Para** que mis empleados usen sus credenciales corporativas (Azure AD, Okta, etc.) para acceder a SuperPago

**Criterios de Aceptacion:**
- [ ] Endpoint `POST /api/v1/organizations/{org_id}/sso/saml` configura SAML SP
- [ ] Acepta metadata XML del IdP (URL o upload)
- [ ] Genera SP metadata XML para que el cliente configure en su IdP
- [ ] Almacena configuracion en DynamoDB `ORG#{org_id}/SSO_PROVIDER#{id}`
- [ ] Cognito configurado como SAML SP via User Pool Identity Provider
- [ ] Endpoint `GET /api/v1/organizations/{org_id}/sso/saml/metadata` retorna SP metadata
- [ ] Test de conectividad: `POST /api/v1/organizations/{org_id}/sso/saml/test`
- [ ] Soporte para multiples atributos SAML: email, name, groups, roles

**Notas Tecnicas:**
- Cognito soporta SAML 2.0 nativamente via Identity Providers
- Usar `python3-saml` o `pysaml2` para parsing de metadata
- Almacenar certificados encriptados via KMS

**Dependencias:** US-AU-007 (roles para mapeo)

---

#### US-AU-014: Configuracion OpenID Connect

**ID:** US-AU-014
**Epica:** EP-AU-003
**Prioridad:** P1
**Story Points:** 5

**Como** OrgAdmin de empresa
**Quiero** configurar OpenID Connect como proveedor de identidad
**Para** integrar con IdPs modernos que soporten OIDC (Google Workspace, Azure AD, Auth0)

**Criterios de Aceptacion:**
- [ ] Endpoint `POST /api/v1/organizations/{org_id}/sso/oidc` configura OIDC
- [ ] Campos: issuer_url, client_id, client_secret, scopes, redirect_uri
- [ ] Auto-discovery via `.well-known/openid-configuration`
- [ ] Cognito configurado como OIDC relying party
- [ ] Authorization Code Flow con PKCE
- [ ] Almacena client_secret encriptado en DynamoDB (ref a KMS)
- [ ] Test de conectividad: `POST /api/v1/organizations/{org_id}/sso/oidc/test`
- [ ] Soporte para claims estandar: sub, email, name, groups

**Notas Tecnicas:**
- Cognito soporta OIDC nativamente via Identity Providers
- client_secret almacenado como referencia a AWS Secrets Manager

**Dependencias:** US-AU-007 (roles para mapeo)

---

#### US-AU-015: Mapeo de Roles Externos a Internos

**ID:** US-AU-015
**Epica:** EP-AU-003
**Prioridad:** P1
**Story Points:** 3

**Como** OrgAdmin
**Quiero** mapear grupos/roles de mi IdP corporativo a roles de SuperPago
**Para** que al autenticarse via SSO, los usuarios reciban automaticamente el rol correcto

**Criterios de Aceptacion:**
- [ ] Endpoint `PUT /api/v1/organizations/{org_id}/sso/role-mapping` configura mapeo
- [ ] Formato: `{ mappings: [{ external_group: "Finance-Team", internal_role: "OrgManager" }] }`
- [ ] Mapeo evaluado en Cognito Post-Authentication Lambda trigger
- [ ] Si grupo externo no tiene mapeo: asignar rol default de la org
- [ ] Soporte para multiples grupos → 1 rol (OR): si usuario tiene cualquiera, recibe el rol
- [ ] Prioridad de mapeo configurable (si usuario tiene multiples grupos mapeados, gana el de mayor prioridad)
- [ ] Mapeo actualizado en cada login SSO (no solo en provisioning)

**Notas Tecnicas:**
- SAML: atributo `groups` o `memberOf`
- OIDC: claim `groups` o custom claim
- Cognito Post-Auth trigger evalua claims y actualiza custom attributes

**Dependencias:** US-AU-013 o US-AU-014, US-AU-011

---

#### US-AU-016: Auto-Provisioning de Usuarios SSO

**ID:** US-AU-016
**Epica:** EP-AU-003
**Prioridad:** P1
**Story Points:** 3

**Como** Sistema
**Quiero** crear automaticamente usuarios en SuperPago la primera vez que se autentican via SSO
**Para** eliminar la necesidad de pre-registrar usuarios manualmente cuando una empresa activa SSO

**Criterios de Aceptacion:**
- [ ] Cognito Pre-Sign-Up Lambda trigger detecta primer login SSO
- [ ] Crea usuario en DynamoDB `USER#{id}/PROFILE` con datos del IdP
- [ ] Asigna a organizacion correspondiente `USER#{id}/ORG#{org_id}`
- [ ] Aplica role mapping (US-AU-015) para asignar rol inicial
- [ ] Email de bienvenida automatico al usuario provisionado
- [ ] Configurable por org: auto-provision ON/OFF
- [ ] Si OFF: el usuario ve mensaje "Contacta a tu administrador para obtener acceso"
- [ ] Audit log: `USER_AUTO_PROVISIONED` con datos del IdP

**Notas Tecnicas:**
- Cognito `PreSignUp` trigger con `autoConfirmUser=true` para SSO
- Crear registros DynamoDB en post-confirmation trigger

**Dependencias:** US-AU-015

---

#### US-AU-017: Desactivacion de Password Login con SSO Activo

**ID:** US-AU-017
**Epica:** EP-AU-003
**Prioridad:** P2
**Story Points:** 2

**Como** OrgAdmin
**Quiero** desactivar el login por contrasena cuando SSO esta configurado
**Para** forzar que todos los usuarios de mi organizacion usen exclusivamente el IdP corporativo

**Criterios de Aceptacion:**
- [ ] Endpoint `PUT /api/v1/organizations/{org_id}/sso/settings` con `{ disable_password_login: true }`
- [ ] Cuando activo: login con email+password retorna error `SSO_REQUIRED` para usuarios de esa org
- [ ] SuperAdmin y TenantAdmin siempre pueden hacer login con password (bypass de emergencia)
- [ ] Si SSO se desactiva, password login se reactiva automaticamente
- [ ] UI muestra "Inicia sesion con tu cuenta corporativa" en vez del form de password
- [ ] Boton "Iniciar sesion con SSO" redirige al IdP configurado

**Notas Tecnicas:**
- Validar en `POST /api/v1/auth/login`: si usuario pertenece a org con SSO-only, rechazar
- Mantener password en Cognito (no eliminar) para recovery

**Dependencias:** US-AU-013 o US-AU-014

---

### EP-AU-004: Gestion de Sesiones y Seguridad

---

#### US-AU-018: Tracking de Sesiones Activas

**ID:** US-AU-018
**Epica:** EP-AU-004
**Prioridad:** P0
**Story Points:** 5

**Como** Sistema
**Quiero** rastrear todas las sesiones activas de cada usuario con informacion del dispositivo
**Para** dar visibilidad al usuario y administradores sobre donde esta activa la cuenta

**Criterios de Aceptacion:**
- [ ] Al login exitoso, crear registro `SESSION#{session_id}/DETAIL` en DynamoDB
- [ ] Campos: user_id, ip, user_agent, device_type (desktop/mobile/tablet), browser, OS, created_at, last_activity, expires_at
- [ ] GSI: `USER#{user_id}#SESSIONS` para listar sesiones de un usuario
- [ ] Endpoint `GET /api/v1/auth/sessions` lista sesiones activas del usuario autenticado
- [ ] Endpoint `GET /api/v1/users/{user_id}/sessions` (OrgAdmin+) lista sesiones de otro usuario
- [ ] Update `last_activity` en cada request autenticado (debounce 5 min para no sobrecargar DB)
- [ ] TTL automatico: sesiones inactivas por > 24h se eliminan
- [ ] Sesion marcada con `is_current=true` para la sesion actual del request

**Notas Tecnicas:**
- Session ID = UUID generado al login, almacenado en JWT custom claim
- Debounce de last_activity via middleware con timestamp en memoria

**Dependencias:** Ninguna

---

#### US-AU-019: Limite de Sesiones Concurrentes

**ID:** US-AU-019
**Epica:** EP-AU-004
**Prioridad:** P0
**Story Points:** 3

**Como** TenantAdmin
**Quiero** configurar un limite maximo de sesiones concurrentes por usuario
**Para** prevenir el uso compartido de cuentas y reducir riesgos de seguridad

**Criterios de Aceptacion:**
- [ ] Configuracion en `TENANT#{id}/AUTH_CONFIG` campo `max_sessions_per_user` (default: 5)
- [ ] Override por organizacion en `ORG#{id}/AUTH_CONFIG`
- [ ] Al login: si sesiones activas >= limite, rechazar con `MAX_SESSIONS_REACHED`
- [ ] Opcion configurable: en vez de rechazar, cerrar la sesion mas antigua automaticamente
- [ ] Endpoint `PUT /api/v1/tenants/{id}/auth-config` para configurar limite
- [ ] Endpoint `PUT /api/v1/organizations/{id}/auth-config` para override
- [ ] SuperAdmin exento del limite

**Notas Tecnicas:**
- Contar sesiones con query a GSI `USER#{id}#SESSIONS` filtrado por `is_active=true`
- Atomic counter para evitar race conditions

**Dependencias:** US-AU-018

---

#### US-AU-020: Device Fingerprinting y Geo-Location

**ID:** US-AU-020
**Epica:** EP-AU-004
**Prioridad:** P1
**Story Points:** 5

**Como** Sistema
**Quiero** capturar device fingerprint y geo-location en cada login
**Para** detectar accesos desde dispositivos o ubicaciones inusuales

**Criterios de Aceptacion:**
- [ ] Frontend (mf-auth) genera device fingerprint: hash(user_agent + screen + timezone + language + platform)
- [ ] Fingerprint enviado en header `X-Device-Fingerprint` en cada request
- [ ] Backend resuelve geo-location por IP via MaxMind GeoLite2 (offline DB)
- [ ] Almacena en sesion: fingerprint, country, city, latitude, longitude
- [ ] Tabla de dispositivos conocidos: `USER#{id}/KNOWN_DEVICES`
- [ ] Si device fingerprint es nuevo Y geo-location es nueva: marcar login como `suspicious`
- [ ] Si login sospechoso y MFA no activo: forzar verificacion por email OTP
- [ ] Si login sospechoso y MFA activo: proceder normal pero registrar alerta
- [ ] Endpoint `GET /api/v1/auth/devices` lista dispositivos conocidos del usuario

**Notas Tecnicas:**
- MaxMind GeoLite2 DB actualizada mensualmente via cron
- FingerprintJS o custom fingerprint en frontend
- No usar servicio externo para geo-location (privacy + latencia)

**Dependencias:** US-AU-018

---

#### US-AU-021: Cierre Remoto de Sesiones

**ID:** US-AU-021
**Epica:** EP-AU-004
**Prioridad:** P0
**Story Points:** 3

**Como** Usuario del ecosistema
**Quiero** cerrar sesiones activas en otros dispositivos de forma remota
**Para** proteger mi cuenta si pierdo un dispositivo o sospecho de acceso no autorizado

**Criterios de Aceptacion:**
- [ ] Endpoint `DELETE /api/v1/auth/sessions/{session_id}` cierra sesion especifica
- [ ] Endpoint `DELETE /api/v1/auth/sessions?all_except_current=true` cierra todas excepto la actual
- [ ] OrgAdmin+ puede cerrar sesiones de usuarios de su org: `DELETE /api/v1/users/{user_id}/sessions/{session_id}`
- [ ] Al cerrar sesion: marcar como `is_active=false` en DynamoDB
- [ ] Agregar session_id a blacklist de tokens (Redis o DynamoDB con TTL)
- [ ] Propagacion: dentro de 1 minuto, el token asociado deja de ser valido
- [ ] Notificacion al usuario (email) cuando una sesion es cerrada remotamente
- [ ] Audit log: quien cerro que sesion, desde donde

**Notas Tecnicas:**
- Token blacklist en DynamoDB con TTL = remaining token life
- Middleware verifica blacklist en cada request (cache 1 min)

**Dependencias:** US-AU-018

---

#### US-AU-022: Deteccion de Sesiones Anomalas

**ID:** US-AU-022
**Epica:** EP-AU-004
**Prioridad:** P1
**Story Points:** 5

**Como** Sistema
**Quiero** detectar patrones de acceso anomalos y alertar al usuario y administradores
**Para** identificar cuentas comprometidas antes de que ocurra un dano financiero

**Criterios de Aceptacion:**
- [ ] Reglas de deteccion:
  - Login desde pais diferente al habitual
  - Login desde IP en lista negra (TOR exit nodes, VPNs conocidas)
  - Multiples logins fallidos seguidos de login exitoso (brute force con exito)
  - Login simultaneo desde 2 geolocaciones distantes (> 500km) en < 1 hora
  - Cambio de password seguido de creacion de API key en < 5 minutos
- [ ] Cada regla tiene severidad: LOW, MEDIUM, HIGH, CRITICAL
- [ ] Acciones por severidad:
  - LOW: log en audit trail
  - MEDIUM: notificacion email al usuario
  - HIGH: forzar MFA step-up + notificar admin
  - CRITICAL: bloquear sesion + notificar admin + email al usuario
- [ ] Endpoint `GET /api/v1/admin/security/anomalies` lista anomalias recientes
- [ ] Endpoint `PUT /api/v1/admin/security/anomalies/{id}/resolve` marca como resuelta

**Notas Tecnicas:**
- Evaluar reglas en Post-Authentication Lambda trigger
- Historial de logins para comparacion en GSI `AUDIT#USER#{id}`
- Lista de TOR exit nodes actualizada diariamente

**Dependencias:** US-AU-020, US-AU-018

---

#### US-AU-023: Audit Log de Autenticacion

**ID:** US-AU-023
**Epica:** EP-AU-004
**Prioridad:** P0
**Story Points:** 3

**Como** Sistema
**Quiero** registrar todas las operaciones de autenticacion en un audit trail inmutable
**Para** tener trazabilidad completa de accesos para seguridad y compliance

**Criterios de Aceptacion:**
- [ ] Eventos registrados: LOGIN_SUCCESS, LOGIN_FAILED, LOGOUT, MFA_ENROLLED, MFA_VERIFIED, MFA_FAILED, PASSWORD_CHANGED, SESSION_CLOSED, ROLE_CHANGED, PERMISSION_CHANGED, API_KEY_CREATED, API_KEY_REVOKED, SSO_LOGIN, ACCOUNT_LOCKED, ACCOUNT_UNLOCKED
- [ ] Cada evento: user_id, timestamp, action, ip, device, result (success/failure), details
- [ ] Almacenado en DynamoDB `AUDIT#AUTH#{org_id}/{timestamp}#{event_id}`
- [ ] GSI: `AUDIT#USER#{user_id}` para historial por usuario
- [ ] Immutable: no se puede editar ni eliminar (append-only)
- [ ] TTL: 365 dias configurable por tenant
- [ ] Endpoint `GET /api/v1/audit/auth?user_id=X&action=Y&from=&to=` con paginacion
- [ ] Solo accesible por OrgAdmin+ (usuarios ven solo su propio historial)

**Notas Tecnicas:**
- Write en background via SQS para no afectar latencia de login
- Batch write para eficiencia

**Dependencias:** US-AU-018

---

### EP-AU-005: Onboarding Multi-Tenant

---

#### US-AU-024: Registro Diferenciado por Tenant

**ID:** US-AU-024
**Epica:** EP-AU-005
**Prioridad:** P0
**Story Points:** 5

**Como** Nuevo usuario
**Quiero** ver un flujo de registro adaptado al tenant del dominio que estoy visitando
**Para** tener una experiencia coherente con la marca (SuperPago, BaatDigital, AlertaTribunal)

**Criterios de Aceptacion:**
- [ ] mf-auth detecta tenant por dominio: superpago.com.mx, baatdigital.com.mx, alertatribunal.com
- [ ] Endpoint `GET /api/v1/tenants/resolve?domain={domain}` retorna tenant_id + config publica
- [ ] Config publica incluye: logo_url, primary_color, app_name, registration_fields, terms_url
- [ ] Formulario de registro muestra campos configurados por tenant
- [ ] Campos base (todos): email, password, nombre, apellido
- [ ] Campos opcionales por tenant: telefono, empresa, RFC, puesto
- [ ] Validaciones de password segun politica del tenant
- [ ] Email de verificacion con branding del tenant
- [ ] Cognito signup con custom attribute `tenant_id`

**Notas Tecnicas:**
- Config publica cacheada en mf-auth (localStorage, TTL 1h)
- No requiere autenticacion para resolver tenant

**Dependencias:** Ninguna

---

#### US-AU-025: Invitaciones por Email

**ID:** US-AU-025
**Epica:** EP-AU-005
**Prioridad:** P0
**Story Points:** 5

**Como** OrgAdmin
**Quiero** invitar usuarios a mi organizacion via email con un link de registro pre-aprobado
**Para** facilitar el onboarding de nuevos miembros sin que pasen por un proceso de aprobacion

**Criterios de Aceptacion:**
- [ ] Endpoint `POST /api/v1/organizations/{org_id}/invitations` crea invitacion
- [ ] Campos: email, role_id, message (opcional), expires_in_days (default 7)
- [ ] Genera token de invitacion unico (UUID) almacenado en DynamoDB
- [ ] Email enviado via SES con branding del tenant: "Has sido invitado a [OrgName] en [TenantName]"
- [ ] Link de registro: `https://app.{tenant}.com.mx/auth/register?invitation={token}`
- [ ] Al registrarse con invitacion: skip aprobacion, asignar rol indicado, asignar a org
- [ ] Endpoint `GET /api/v1/organizations/{org_id}/invitations` lista invitaciones pendientes
- [ ] Endpoint `DELETE /api/v1/organizations/{org_id}/invitations/{id}` revoca invitacion
- [ ] Invitacion expira segun configuracion, token de un solo uso
- [ ] Re-envio: `POST /api/v1/organizations/{org_id}/invitations/{id}/resend`

**Notas Tecnicas:**
- Token almacenado en `PK: INVITATION#{token}, SK: DETAIL` con TTL
- Validar que email no este ya registrado en la org

**Dependencias:** US-AU-011 (asignacion de roles)

---

#### US-AU-026: Self-Service Registration con Aprobacion

**ID:** US-AU-026
**Epica:** EP-AU-005
**Prioridad:** P1
**Story Points:** 3

**Como** Nuevo usuario
**Quiero** registrarme sin invitacion y esperar aprobacion del administrador
**Para** poder solicitar acceso a una organizacion aunque nadie me haya invitado explicitamente

**Criterios de Aceptacion:**
- [ ] Configurable por org: self-registration ON/OFF (default OFF)
- [ ] Si ON: formulario de registro incluye selector de organizacion (solo orgs con self-reg activo)
- [ ] Al registrarse: usuario creado en estado `PENDING_APPROVAL`
- [ ] Cognito user creado pero con `enabled=false` hasta aprobacion
- [ ] Notificacion email al OrgAdmin: "Nuevo usuario pendiente de aprobacion"
- [ ] OrgAdmin aprueba/rechaza: `PUT /api/v1/organizations/{org_id}/users/{user_id}/approve`
- [ ] Al aprobar: Cognito `admin_enable_user`, asignar rol default, email de bienvenida
- [ ] Al rechazar: Cognito `admin_delete_user`, email de rechazo
- [ ] Endpoint `GET /api/v1/organizations/{org_id}/users?status=PENDING_APPROVAL` lista pendientes

**Notas Tecnicas:**
- Estado `PENDING_APPROVAL` en `USER#{id}/ORG#{org_id}` campo `status`

**Dependencias:** US-AU-024

---

#### US-AU-027: Welcome Wizard Personalizado

**ID:** US-AU-027
**Epica:** EP-AU-005
**Prioridad:** P2
**Story Points:** 3

**Como** Nuevo usuario recien registrado
**Quiero** ver un wizard de bienvenida que me guie por las funciones principales
**Para** entender rapidamente como usar la plataforma segun mi rol y organizacion

**Criterios de Aceptacion:**
- [ ] Wizard mostrado al primer login post-registro (flag `onboarding_completed` en perfil)
- [ ] Pasos configurables por tenant en `TENANT#{id}/ONBOARDING_CONFIG`
- [ ] Pasos base: Bienvenida → Completar perfil → Configurar MFA → Tour de funciones → Listo
- [ ] Cada paso puede ser obligatorio u opcional
- [ ] Step "Configurar MFA" puede ser obligatorio si la politica del tenant lo requiere
- [ ] Endpoint `GET /api/v1/auth/onboarding/steps` retorna pasos pendientes
- [ ] Endpoint `PUT /api/v1/auth/onboarding/steps/{step_id}/complete` marca paso completado
- [ ] Boton "Saltar" (solo en pasos opcionales) y "Completar despues"
- [ ] Al completar todos los pasos: `onboarding_completed=true`, no se muestra de nuevo

**Notas Tecnicas:**
- Estado de onboarding en `USER#{id}/PROFILE` campo `onboarding_progress`
- Frontend: componente wizard reutilizable con steps dinamicos

**Dependencias:** US-AU-024, US-AU-001 (MFA step)

---

#### US-AU-028: Dashboard de Invitaciones para OrgAdmin

**ID:** US-AU-028
**Epica:** EP-AU-005
**Prioridad:** P1
**Story Points:** 3

**Como** OrgAdmin
**Quiero** ver un dashboard con todas las invitaciones y solicitudes pendientes
**Para** gestionar eficientemente el acceso a mi organizacion

**Criterios de Aceptacion:**
- [ ] Pagina en mf-auth `/auth/admin/invitations` con 3 tabs:
  - Invitaciones enviadas (pendientes, aceptadas, expiradas, revocadas)
  - Solicitudes pendientes de aprobacion (self-registration)
  - Miembros activos con rol y fecha de ingreso
- [ ] Acciones rapidas: aprobar, rechazar, reenviar invitacion, revocar
- [ ] Filtros: por estado, por rol, por fecha
- [ ] Bulk actions: invitar multiples emails (CSV upload o textarea)
- [ ] Metricas: total miembros, invitaciones pendientes, conversion rate
- [ ] Componentes standalone OnPush
- [ ] data-cy attributes, tests >= 98%

**Notas Tecnicas:**
- Componente compartido entre mf-auth admin pages
- Paginacion server-side para orgs con muchos miembros

**Dependencias:** US-AU-025, US-AU-026

---

### EP-AU-006: API Keys y Service Accounts

---

#### US-AU-029: Generacion y Gestion de API Keys

**ID:** US-AU-029
**Epica:** EP-AU-006
**Prioridad:** P0
**Story Points:** 5

**Como** OrgAdmin
**Quiero** generar API keys para que mis sistemas se integren con SuperPago via API
**Para** automatizar operaciones sin depender de tokens JWT de usuario

**Criterios de Aceptacion:**
- [ ] Endpoint `POST /api/v1/organizations/{org_id}/api-keys` genera nueva key
- [ ] Campos: name, scopes[], expires_in_days (30/90/365/null), description
- [ ] Key generada: `sk_live_{32_chars_random}` (produccion) o `sk_test_{32_chars_random}` (sandbox)
- [ ] Key retornada EN TEXTO PLANO una sola vez en el response (no se almacena en plano)
- [ ] Almacenada como SHA-256 hash en DynamoDB `APIKEY#{prefix}/DETAIL`
- [ ] prefix = primeros 8 chars de la key (para identificacion visual)
- [ ] Endpoint `GET /api/v1/organizations/{org_id}/api-keys` lista keys (solo prefijo, nunca key completa)
- [ ] Endpoint `DELETE /api/v1/organizations/{org_id}/api-keys/{key_prefix}` revoca key
- [ ] Maximo 10 API keys activas por organizacion
- [ ] Audit log: creacion, uso, revocacion de cada key

**Notas Tecnicas:**
- Generar key con `secrets.token_urlsafe(32)`
- Hash con SHA-256 para storage, verificar en cada request con hash comparison

**Dependencias:** US-AU-008 (permisos para scopes)

---

#### US-AU-030: Autenticacion por API Key

**ID:** US-AU-030
**Epica:** EP-AU-006
**Prioridad:** P0
**Story Points:** 5

**Como** Sistema externo (B2B)
**Quiero** autenticarme con una API key en lugar de JWT
**Para** realizar operaciones programaticas sin flujo OAuth interactivo

**Criterios de Aceptacion:**
- [ ] Header: `Authorization: Bearer sk_live_...` o `X-API-Key: sk_live_...`
- [ ] Middleware detecta API key por prefijo `sk_` y rutea a validacion de API key
- [ ] Validacion: hash(key) == stored hash, is_active=true, not expired
- [ ] Si valida: inyectar org_id y scopes en request context (como si fuera JWT)
- [ ] Rate limiting por key: default 1000 req/min, configurable
- [ ] Rate limit header: `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- [ ] Si rate limit excedido: 429 con `Retry-After` header
- [ ] Update `last_used` timestamp en cada uso (debounce 1 min)
- [ ] Si key expirada: 401 con mensaje claro `API_KEY_EXPIRED`
- [ ] Si key revocada: 401 con `API_KEY_REVOKED`

**Notas Tecnicas:**
- Rate limiting via DynamoDB atomic counter con TTL de 1 minuto
- Cache de API key validation en memoria (TTL 1 min) para performance

**Dependencias:** US-AU-029

---

#### US-AU-031: Scopes Granulares para API Keys

**ID:** US-AU-031
**Epica:** EP-AU-006
**Prioridad:** P0
**Story Points:** 3

**Como** OrgAdmin
**Quiero** asignar scopes especificos a cada API key
**Para** limitar el acceso de cada integracion solo a los recursos que necesita (principio de minimo privilegio)

**Criterios de Aceptacion:**
- [ ] Scopes alineados con permisos RBAC: `accounts:read`, `transactions:write`, etc.
- [ ] Al crear API key, se seleccionan scopes de los permisos efectivos de la org
- [ ] No se puede asignar un scope que la org no tenga como permiso efectivo
- [ ] Middleware valida scopes de la API key contra el endpoint solicitado
- [ ] Si scope insuficiente: 403 con `{ error: 'INSUFFICIENT_SCOPE', required: 'transactions:write' }`
- [ ] Endpoint `GET /api/v1/organizations/{org_id}/api-keys/{prefix}/scopes` lista scopes de una key
- [ ] Endpoint `PUT /api/v1/organizations/{org_id}/api-keys/{prefix}/scopes` actualiza scopes (sin regenerar key)

**Notas Tecnicas:**
- Scopes almacenados como lista en DynamoDB con la API key
- Validacion en el mismo middleware de autorizacion (US-AU-012)

**Dependencias:** US-AU-029, US-AU-012

---

#### US-AU-032: Rotacion de API Keys

**ID:** US-AU-032
**Epica:** EP-AU-006
**Prioridad:** P1
**Story Points:** 3

**Como** OrgAdmin
**Quiero** rotar una API key generando una nueva sin invalidar la anterior inmediatamente
**Para** actualizar credenciales en mis sistemas sin tiempo de inactividad

**Criterios de Aceptacion:**
- [ ] Endpoint `POST /api/v1/organizations/{org_id}/api-keys/{prefix}/rotate` genera nueva key
- [ ] La key anterior permanece activa por periodo de gracia (default 24h, configurable)
- [ ] Nueva key retornada en response (unica vez)
- [ ] Despues del periodo de gracia: key anterior se revoca automaticamente
- [ ] Si se necesita rotacion inmediata: `POST .../rotate?immediate=true` revoca la anterior ya
- [ ] La nueva key hereda scopes, rate limits y configuracion de la anterior
- [ ] Notificacion al OrgAdmin 24h antes de expirar la key vieja
- [ ] Audit log: rotacion con timestamps de ambas keys

**Notas Tecnicas:**
- Periodo de gracia via campo `deprecated_at` + `grace_period_hours` en DynamoDB
- Job programado (EventBridge) revoca keys cuyo grace period expiro

**Dependencias:** US-AU-029

---

#### US-AU-033: Service Accounts Inter-Microservicio

**ID:** US-AU-033
**Epica:** EP-AU-006
**Prioridad:** P1
**Story Points:** 3

**Como** Sistema (microservicio)
**Quiero** un mecanismo de autenticacion entre microservicios internos
**Para** que covacha-payment pueda llamar a covacha-core de forma autenticada y autorizada

**Criterios de Aceptacion:**
- [ ] Service accounts: API keys especiales con `type=SERVICE` y `scope=internal`
- [ ] Creados por SuperAdmin: `POST /api/v1/service-accounts`
- [ ] Campos: name (ej: "covacha-payment"), allowed_services[] (endpoints permitidos)
- [ ] Sin rate limit (o limite alto: 10000 req/min)
- [ ] Sin expiracion (pero rotacion obligatoria cada 90 dias con alerta)
- [ ] Header: `X-Service-Account: sa_...` (prefijo diferente a API keys de usuario)
- [ ] Mutual TLS opcional para verificacion adicional en produccion
- [ ] Audit log: cada llamada inter-servicio con service account

**Notas Tecnicas:**
- Service accounts almacenados como `APIKEY#{prefix}/DETAIL` con `type=SERVICE`
- En VPC privada, el TLS mutuo es opcional pero recomendado

**Dependencias:** US-AU-029, US-AU-030

---

### EP-AU-007: Frontend mf-auth Completo

---

#### US-AU-034: Login Page Multi-Tenant con Branding

**ID:** US-AU-034
**Epica:** EP-AU-007
**Prioridad:** P0
**Story Points:** 5

**Como** Usuario visitante
**Quiero** ver una pagina de login con el branding del tenant correspondiente al dominio
**Para** saber que estoy en la plataforma correcta y tener confianza en la autenticidad

**Criterios de Aceptacion:**
- [ ] Pagina `/auth/login` carga branding del tenant resuelto por dominio
- [ ] Elementos personalizados: logo, color primario, titulo, subtitulo, fondo
- [ ] Form: email, password, checkbox "Recordarme", link "Olvide mi contrasena"
- [ ] Si org tiene SSO: boton "Iniciar sesion con [IdP Name]" debajo del form
- [ ] Si org tiene SSO-only: ocultar form de password, mostrar solo boton SSO
- [ ] Validacion inline: email format, password required
- [ ] Mensaje de error descriptivo pero seguro (no revelar si email existe)
- [ ] Redirect post-login a URL original o dashboard default
- [ ] Shared state: al login exitoso, guardar `covacha:auth` y `covacha:user` en localStorage
- [ ] BroadcastChannel: notificar a otras pestanas del login
- [ ] Componente standalone OnPush, responsive mobile-first
- [ ] data-cy attributes, tests >= 98%

**Notas Tecnicas:**
- Resolver tenant en `APP_INITIALIZER` de Angular
- Cachear branding en localStorage con TTL de 1h

**Dependencias:** US-AU-024 (resolve tenant API)

---

#### US-AU-035: MFA Enrollment Wizard

**ID:** US-AU-035
**Epica:** EP-AU-007
**Prioridad:** P0
**Story Points:** 5

**Como** Usuario del ecosistema
**Quiero** un wizard paso a paso para configurar MFA en mi cuenta
**Para** activar la proteccion de segundo factor de forma guiada y sin confusion

**Criterios de Aceptacion:**
- [ ] Pagina `/auth/mfa/setup` con wizard de 4 pasos:
  1. Seleccionar metodo: TOTP (recomendado), SMS, Email
  2. Configurar: QR code para TOTP, numero para SMS, email para Email
  3. Verificar: ingresar codigo del metodo seleccionado
  4. Recovery codes: mostrar 10 codigos, boton "Descargar" y "Copiar", checkbox "Los he guardado"
- [ ] Step indicators visuales (1/4, 2/4, etc.)
- [ ] Boton "Atras" en cada paso (excepto paso 1)
- [ ] Si TOTP: mostrar QR code grande + campo manual del secret para copy-paste
- [ ] Si SMS: input de telefono con country code selector (default +52 Mexico)
- [ ] Si Email: input de email con validacion
- [ ] Recovery codes: mostrar en grid 2x5, boton descarga como TXT
- [ ] Al completar: redirigir a pagina de security settings con mensaje de exito
- [ ] Componente standalone OnPush, responsive
- [ ] data-cy attributes, tests >= 98%

**Notas Tecnicas:**
- Usar adapter `auth-mfa.adapter.ts` para calls al backend
- QR code renderizado client-side con `qrcode` npm package

**Dependencias:** US-AU-001, US-AU-002, US-AU-004

---

#### US-AU-036: MFA Challenge Page

**ID:** US-AU-036
**Epica:** EP-AU-007
**Prioridad:** P0
**Story Points:** 3

**Como** Usuario con MFA activo
**Quiero** una pagina clara para ingresar mi codigo de segundo factor durante el login
**Para** completar la autenticacion de forma rapida y sin fricciones

**Criterios de Aceptacion:**
- [ ] Pagina `/auth/mfa/challenge` mostrada despues de login exitoso si MFA requerido
- [ ] Muestra metodos disponibles con tabs/radio: TOTP, SMS, Email, Recovery Code
- [ ] Input de 6 digitos con auto-focus y auto-submit al completar
- [ ] Si SMS/Email: boton "Reenviar codigo" con cooldown de 60 segundos
- [ ] Timer de expiracion visible (3 minutos)
- [ ] Mensaje de error inline si codigo invalido con intentos restantes
- [ ] Despues de 3 intentos fallidos: redirigir a login con mensaje
- [ ] Link "Usar recovery code" como opcion de emergencia
- [ ] Branding del tenant mantenido
- [ ] Componente standalone OnPush, responsive
- [ ] data-cy attributes, tests >= 98%

**Notas Tecnicas:**
- Auto-submit: detectar 6 caracteres y enviar automaticamente
- Timer con `interval()` de RxJS, unsubscribe on destroy

**Dependencias:** US-AU-003

---

#### US-AU-037: Profile Management Page

**ID:** US-AU-037
**Epica:** EP-AU-007
**Prioridad:** P1
**Story Points:** 3

**Como** Usuario autenticado
**Quiero** ver y editar mi perfil personal desde mf-auth
**Para** mantener mi informacion actualizada y personalizar mi experiencia

**Criterios de Aceptacion:**
- [ ] Pagina `/auth/profile` con secciones:
  - Info personal: nombre, apellido, email (read-only), telefono, avatar
  - Organizacion: nombre org, rol, fecha de ingreso (read-only)
  - Preferencias: idioma, zona horaria, formato de fecha
- [ ] Avatar: upload de imagen con crop circular (max 1MB, JPG/PNG)
- [ ] Edicion inline con boton "Guardar" por seccion
- [ ] Validaciones: telefono E.164, nombre max 100 chars
- [ ] Endpoint `GET /api/v1/users/me/profile` y `PUT /api/v1/users/me/profile`
- [ ] Componente standalone OnPush, responsive
- [ ] data-cy attributes, tests >= 98%

**Notas Tecnicas:**
- Avatar upload a S3 via presigned URL
- Actualizar `covacha:user` en localStorage al guardar

**Dependencias:** Ninguna

---

#### US-AU-038: Security Settings Page

**ID:** US-AU-038
**Epica:** EP-AU-007
**Prioridad:** P0
**Story Points:** 5

**Como** Usuario autenticado
**Quiero** una pagina para gestionar la seguridad de mi cuenta
**Para** cambiar contrasena, configurar MFA y revisar mis sesiones activas en un solo lugar

**Criterios de Aceptacion:**
- [ ] Pagina `/auth/security` con tabs:
  1. **Password**: cambiar contrasena (current + new + confirm), indicador de fortaleza, reglas visibles
  2. **MFA**: estado actual (activo/inactivo), metodos enrollados, botones configurar/desactivar, recovery codes restantes
  3. **Sesiones**: lista de sesiones activas con device, IP, ubicacion, last activity, boton "Cerrar"
  4. **Dispositivos**: dispositivos de confianza (remembered), boton "Revocar confianza"
- [ ] Tab Password: validacion en tiempo real de reglas (min 8 chars, mayuscula, minuscula, numero, especial)
- [ ] Tab MFA: badge verde "Activo" o rojo "Inactivo", link a wizard de setup
- [ ] Tab Sesiones: sesion actual resaltada, boton "Cerrar todas las demas"
- [ ] Tab Dispositivos: icono por device type (desktop/mobile/tablet)
- [ ] Componentes standalone OnPush, responsive
- [ ] data-cy attributes, tests >= 98%

**Notas Tecnicas:**
- Reutilizar componentes de session list y device list
- Tab por defecto segun query param: `/auth/security?tab=mfa`

**Dependencias:** US-AU-001 (MFA), US-AU-018 (sesiones), US-AU-021 (cierre remoto)

---

#### US-AU-039: Role Viewer para Usuarios

**ID:** US-AU-039
**Epica:** EP-AU-007
**Prioridad:** P2
**Story Points:** 2

**Como** Usuario autenticado
**Quiero** ver que rol y permisos tengo asignados en mi organizacion
**Para** entender que puedo y que no puedo hacer en la plataforma

**Criterios de Aceptacion:**
- [ ] Pagina `/auth/permissions` con:
  - Nombre del rol actual con descripcion
  - Lista de permisos agrupados por recurso
  - Indicador visual: check verde (permitido), X roja (no permitido) por cada permiso
  - Si rol custom: indicar "Rol personalizado por [OrgName]"
- [ ] Solo lectura (no puede editarse desde esta pagina)
- [ ] Link a contactar OrgAdmin si necesita permisos adicionales
- [ ] Componente standalone OnPush, responsive
- [ ] data-cy attributes, tests >= 98%

**Notas Tecnicas:**
- Endpoint `GET /api/v1/users/me/permissions` retorna permisos efectivos
- Agrupar por recurso en frontend con `groupBy()`

**Dependencias:** US-AU-008, US-AU-012

---

#### US-AU-040: Gestion de Roles y Usuarios (Admin Pages)

**ID:** US-AU-040
**Epica:** EP-AU-007
**Prioridad:** P1
**Story Points:** 5

**Como** OrgAdmin
**Quiero** paginas de administracion para gestionar roles y usuarios de mi organizacion
**Para** controlar el acceso sin tener que usar la API directamente

**Criterios de Aceptacion:**
- [ ] Pagina `/auth/admin/users` con:
  - Tabla de usuarios: nombre, email, rol, estado, ultimo login, acciones
  - Filtros: por rol, por estado, busqueda por nombre/email
  - Acciones: cambiar rol, desactivar, reactivar, ver sesiones, reset password
  - Paginacion server-side
- [ ] Pagina `/auth/admin/roles` con:
  - Lista de roles (sistema + custom) con conteo de usuarios asignados
  - Crear rol custom: nombre, descripcion, selector de permisos con checkboxes
  - Editar rol custom: misma interfaz que creacion
  - Eliminar rol custom: confirmacion + reasignar usuarios a otro rol
- [ ] Componentes standalone OnPush, responsive
- [ ] Acceso restringido: solo OrgAdmin+ puede ver estas paginas (guard)
- [ ] data-cy attributes, tests >= 98%

**Notas Tecnicas:**
- Guard `OrgAdminGuard` verifica rol en shared state
- Reutilizar tabla de usuarios entre invitations y user management

**Dependencias:** US-AU-011, US-AU-010

---

### EP-AU-008: Compliance y Auditoria de Acceso

---

#### US-AU-041: Politicas de Contrasenas Configurables

**ID:** US-AU-041
**Epica:** EP-AU-008
**Prioridad:** P0
**Story Points:** 3

**Como** TenantAdmin
**Quiero** configurar las politicas de contrasenas para mi tenant
**Para** cumplir con los requisitos de seguridad de mi organizacion

**Criterios de Aceptacion:**
- [ ] Endpoint `PUT /api/v1/tenants/{id}/password-policy` configura politica
- [ ] Campos configurables:
  - `min_length`: 8-128 (default 8)
  - `require_uppercase`: bool (default true)
  - `require_lowercase`: bool (default true)
  - `require_numbers`: bool (default true)
  - `require_special_chars`: bool (default true)
  - `max_age_days`: 0-365 (default 90, 0=sin expiracion)
  - `history_count`: 0-24 (default 5, ultimas N passwords no reutilizables)
  - `min_age_days`: 0-7 (default 1, dias minimos antes de poder cambiar otra vez)
- [ ] Override por organizacion: `PUT /api/v1/organizations/{id}/password-policy` (solo puede ser mas estricto)
- [ ] Cognito User Pool policy actualizada via API al cambiar configuracion
- [ ] Validacion en registro y cambio de password contra la politica activa
- [ ] Endpoint `GET /api/v1/auth/password-policy` retorna politica aplicable (publica, para UI)

**Notas Tecnicas:**
- Cognito soporta password policies nativamente via User Pool settings
- Historial de passwords almacenado como hashes en `USER#{id}/PASSWORD_HISTORY`

**Dependencias:** Ninguna

---

#### US-AU-042: Account Lockout Policies

**ID:** US-AU-042
**Epica:** EP-AU-008
**Prioridad:** P0
**Story Points:** 3

**Como** TenantAdmin
**Quiero** configurar politicas de bloqueo de cuenta por intentos fallidos
**Para** proteger las cuentas contra ataques de fuerza bruta

**Criterios de Aceptacion:**
- [ ] Configuracion en `TENANT#{id}/AUTH_CONFIG`:
  - `max_failed_attempts`: 3-10 (default 5)
  - `lockout_duration_minutes`: 5-1440 (default 15)
  - `lockout_type`: TEMPORARY (auto-unlock despues de duracion) | PERMANENT (requiere admin unlock)
  - `failed_attempt_window_minutes`: 5-60 (default 15, ventana para contar intentos)
- [ ] Cognito: usar Advanced Security features para bloqueo automatico
- [ ] Contador de intentos fallidos en DynamoDB `USER#{id}/LOGIN_ATTEMPTS` con TTL
- [ ] Al bloquear: status del usuario cambia a `LOCKED`, audit event `ACCOUNT_LOCKED`
- [ ] Endpoint `POST /api/v1/users/{user_id}/unlock` (OrgAdmin+) desbloquea manualmente
- [ ] Email al usuario cuando su cuenta se bloquea
- [ ] Email al OrgAdmin cuando lockout PERMANENT ocurre

**Notas Tecnicas:**
- Cognito Advanced Security mode activado para risk-based auth
- Contador con atomic increment y TTL para auto-reset

**Dependencias:** US-AU-023 (audit log)

---

#### US-AU-043: Reportes de Acceso

**ID:** US-AU-043
**Epica:** EP-AU-008
**Prioridad:** P1
**Story Points:** 5

**Como** TenantAdmin
**Quiero** generar reportes de acceso por usuario, organizacion y periodo
**Para** auditar quien accedio a que y cuando, cumpliendo requisitos de compliance

**Criterios de Aceptacion:**
- [ ] Endpoint `GET /api/v1/audit/reports/access?org_id=X&from=&to=&format=json` genera reporte
- [ ] Formatos: JSON (API), CSV (descarga)
- [ ] Contenido del reporte:
  - Logins exitosos/fallidos por usuario
  - Horarios de acceso (distribucion por hora del dia)
  - Dispositivos y ubicaciones por usuario
  - Cambios de roles y permisos
  - API keys creadas/revocadas
  - Sesiones anomalas detectadas
- [ ] Pagina en mf-auth `/auth/admin/reports` con:
  - Selector de periodo (ultimo dia, semana, mes, custom)
  - Selector de organizacion (TenantAdmin ve todas sus orgs)
  - Graficas: logins por dia, top usuarios activos, distribucion por dispositivo
  - Tabla detallada con paginacion y export CSV
- [ ] Reporte programado: email semanal al TenantAdmin con resumen (opcional)
- [ ] Componentes standalone OnPush, responsive
- [ ] data-cy attributes, tests >= 98%

**Notas Tecnicas:**
- Queries a GSI de audit trail, agregaciones en backend
- Graficas con Chart.js o ngx-charts
- CSV generado server-side para datasets grandes

**Dependencias:** US-AU-023 (audit trail)

---

#### US-AU-044: GDPR - Derecho al Olvido y Exportacion

**ID:** US-AU-044
**Epica:** EP-AU-008
**Prioridad:** P1
**Story Points:** 5

**Como** Usuario del ecosistema
**Quiero** solicitar la eliminacion o exportacion de mis datos personales
**Para** ejercer mis derechos de privacidad segun normativas de proteccion de datos

**Criterios de Aceptacion:**
- [ ] Endpoint `POST /api/v1/users/me/data-export` solicita exportacion de datos
- [ ] Genera archivo ZIP con todos los datos del usuario:
  - Perfil personal (JSON)
  - Historial de acceso (CSV)
  - Sesiones historicas (CSV)
  - Roles y permisos asignados (JSON)
  - API keys creadas (JSON, sin secrets)
  - Invitaciones enviadas/recibidas (JSON)
- [ ] Archivo disponible para descarga por 24h, notificacion por email cuando listo
- [ ] Endpoint `POST /api/v1/users/me/data-deletion` solicita eliminacion
- [ ] Eliminacion = anonimizacion (no borrar, reemplazar PII con placeholders):
  - nombre → "Usuario eliminado"
  - email → hash irreversible
  - telefono → null
  - IP addresses en audit → anonimizados
- [ ] Periodo de gracia: 30 dias antes de ejecutar (cancelable)
- [ ] Requiere confirmacion por email + MFA (si activo)
- [ ] Solo el usuario puede solicitar (no OrgAdmin, por privacidad)
- [ ] Audit log de la solicitud (el audit log mismo NO se anonimiza durante 365 dias por compliance)

**Notas Tecnicas:**
- Exportacion asincrona: SQS job que genera ZIP y sube a S3 con presigned URL
- Anonimizacion batch: Lambda programada para ejecutar eliminaciones pendientes

**Dependencias:** US-AU-023

---

#### US-AU-045: Dashboard de Compliance

**ID:** US-AU-045
**Epica:** EP-AU-008
**Prioridad:** P2
**Story Points:** 3

**Como** TenantAdmin
**Quiero** ver un dashboard de compliance que muestre el estado de seguridad del tenant
**Para** identificar riesgos y demostrar cumplimiento a auditores

**Criterios de Aceptacion:**
- [ ] Pagina en mf-auth `/auth/admin/compliance` con:
  - **Metricas de seguridad**:
    - % de usuarios con MFA activo
    - % de usuarios con password expirado
    - Cuentas bloqueadas actualmente
    - Sesiones anomalas (ultimos 30 dias)
    - API keys proximas a expirar (30 dias)
  - **Checklist de compliance**:
    - Password policy configurada: check/warn
    - MFA policy activa: check/warn
    - Lockout policy configurada: check/warn
    - Audit trail activo: check
    - Retencion de logs >= 365 dias: check/warn
  - **Alertas activas**: lista de issues de seguridad pendientes
  - **Score de seguridad**: 0-100 basado en las metricas anteriores
- [ ] Endpoint `GET /api/v1/admin/compliance/score` retorna score y desglose
- [ ] Endpoint `GET /api/v1/admin/compliance/alerts` retorna alertas pendientes
- [ ] Componentes standalone OnPush, responsive
- [ ] data-cy attributes, tests >= 98%

**Notas Tecnicas:**
- Score calculado server-side con pesos configurables por metrica
- Cache del score con TTL de 1h (recalcular on-demand con boton "Refresh")

**Dependencias:** US-AU-041, US-AU-042, US-AU-043

---

## Roadmap

### Fase 1: Fundamentos (Sprint 1-2)

| Sprint | Epica | User Stories | Dev-Days |
|--------|-------|-------------|----------|
| 1 | EP-AU-001 | US-AU-001 (TOTP), US-AU-002 (SMS/Email), US-AU-003 (Challenge) | 15 |
| 1 | EP-AU-002 | US-AU-007 (Roles sistema), US-AU-008 (Permisos granulares) | 10 |
| 2 | EP-AU-001 | US-AU-004 (Recovery), US-AU-005 (Remember), US-AU-006 (Step-up) | 11 |
| 2 | EP-AU-002 | US-AU-009 (Herencia), US-AU-010 (Custom), US-AU-011 (Asignacion), US-AU-012 (Middleware) | 16 |

### Fase 2: Sesiones y Frontend Base (Sprint 2-3)

| Sprint | Epica | User Stories | Dev-Days |
|--------|-------|-------------|----------|
| 2-3 | EP-AU-004 | US-AU-018 (Tracking), US-AU-019 (Limite), US-AU-020 (Fingerprint) | 13 |
| 3 | EP-AU-004 | US-AU-021 (Cierre remoto), US-AU-022 (Anomalias), US-AU-023 (Audit) | 11 |
| 2-3 | EP-AU-007 | US-AU-034 (Login), US-AU-035 (MFA Wizard), US-AU-036 (MFA Challenge) | 13 |

### Fase 3: SSO y Onboarding (Sprint 3-4)

| Sprint | Epica | User Stories | Dev-Days |
|--------|-------|-------------|----------|
| 3-4 | EP-AU-003 | US-AU-013 (SAML), US-AU-014 (OIDC), US-AU-015 (Role mapping) | 13 |
| 4 | EP-AU-003 | US-AU-016 (Auto-provision), US-AU-017 (Disable password) | 5 |
| 3-4 | EP-AU-005 | US-AU-024 (Registro tenant), US-AU-025 (Invitaciones), US-AU-026 (Self-reg) | 13 |
| 4 | EP-AU-005 | US-AU-027 (Wizard), US-AU-028 (Dashboard invitations) | 6 |

### Fase 4: API Keys, Frontend y Compliance (Sprint 4-5)

| Sprint | Epica | User Stories | Dev-Days |
|--------|-------|-------------|----------|
| 4-5 | EP-AU-006 | US-AU-029 a US-AU-033 (API Keys completo) | 19 |
| 4-5 | EP-AU-007 | US-AU-037 (Profile), US-AU-038 (Security), US-AU-039 (Role viewer), US-AU-040 (Admin) | 15 |
| 4-5 | EP-AU-008 | US-AU-041 a US-AU-045 (Compliance completo) | 19 |

### Resumen de Estimaciones

| Epica | User Stories | Dev-Days | Sprint |
|-------|-------------|----------|--------|
| EP-AU-001 | 6 (US-AU-001 a 006) | 26 | 1-2 |
| EP-AU-002 | 6 (US-AU-007 a 012) | 26 | 1-3 |
| EP-AU-003 | 5 (US-AU-013 a 017) | 18 | 3-4 |
| EP-AU-004 | 6 (US-AU-018 a 023) | 24 | 2-3 |
| EP-AU-005 | 5 (US-AU-024 a 028) | 19 | 3-4 |
| EP-AU-006 | 5 (US-AU-029 a 033) | 19 | 4-5 |
| EP-AU-007 | 7 (US-AU-034 a 040) | 28 | 2-5 |
| EP-AU-008 | 5 (US-AU-041 a 045) | 19 | 4-5 |
| **TOTAL** | **45** | **179** | **1-5** |

### Paralelismo Sugerido (2 equipos)

```
Sprint 1: [Equipo A: EP-AU-001 MFA setup]          [Equipo B: EP-AU-002 Roles+Permisos]
Sprint 2: [Equipo A: EP-AU-001 cont. + EP-AU-004]  [Equipo B: EP-AU-002 cont. + EP-AU-007 Login/MFA UI]
Sprint 3: [Equipo A: EP-AU-004 cont. + EP-AU-003]  [Equipo B: EP-AU-005 Onboarding + EP-AU-007 cont.]
Sprint 4: [Equipo A: EP-AU-003 cont. + EP-AU-006]  [Equipo B: EP-AU-005 cont. + EP-AU-007 Admin UI]
Sprint 5: [Equipo A: EP-AU-006 cont. + EP-AU-008]  [Equipo B: EP-AU-008 UI + QA + Integration testing]
```

---

## Grafo de Dependencias

```
BACKEND CORE:
EP-AU-001 (MFA) ─────────────────────+
    |                                 |
    v                                 v
US-AU-001 (TOTP) ──+                 EP-AU-004 (Sesiones)
US-AU-002 (SMS)  ──+──> US-AU-003    |
                        (Challenge)   +──> US-AU-018 (Tracking)
                            |         |         |
                            v         |         v
                     US-AU-004        |    US-AU-019 (Limite)
                     (Recovery)       |    US-AU-020 (Fingerprint)
                            |         |         |
                            v         |         v
                     US-AU-005        |    US-AU-021 (Cierre)
                     (Remember)       |    US-AU-022 (Anomalias)
                            |         |    US-AU-023 (Audit)
                            v         |
                     US-AU-006        |
                     (Step-up)        |
                                      |
EP-AU-002 (RBAC) ────────────────────+
    |                                 |
    v                                 v
US-AU-007 (Roles) ──> US-AU-008   EP-AU-005 (Onboarding)
                      (Permisos)     |
                          |          +──> US-AU-024 (Registro)
                          v          |    US-AU-025 (Invitaciones)
                     US-AU-009       |    US-AU-026 (Self-reg)
                     (Herencia)      |    US-AU-027 (Wizard)
                          |          |    US-AU-028 (Dashboard)
                          v          |
                     US-AU-010       v
                     (Custom)     EP-AU-003 (SSO)
                          |          |
                          v          +──> US-AU-013 (SAML)
                     US-AU-011       |    US-AU-014 (OIDC)
                     (Asignacion)    |    US-AU-015 (Role mapping)
                          |          |    US-AU-016 (Auto-provision)
                          v          |    US-AU-017 (Disable password)
                     US-AU-012       |
                     (Middleware)     v
                          |       EP-AU-006 (API Keys)
                          |          |
                          |          +──> US-AU-029 (Generacion)
                          |          |    US-AU-030 (Auth by key)
                          +──────────+    US-AU-031 (Scopes)
                                     |    US-AU-032 (Rotacion)
                                     |    US-AU-033 (Service accounts)
                                     |
                                     v
                               EP-AU-008 (Compliance)
                                     |
                                     +──> US-AU-041 (Password policy)
                                     |    US-AU-042 (Lockout)
                                     |    US-AU-043 (Reportes)
                                     |    US-AU-044 (GDPR)
                                     |    US-AU-045 (Dashboard)

FRONTEND:
EP-AU-007 (mf-auth UI) ──────────────────────────
    |
    +──> US-AU-034 (Login page)        ── depende de: US-AU-024
    +──> US-AU-035 (MFA Wizard)        ── depende de: US-AU-001, 002
    +──> US-AU-036 (MFA Challenge)     ── depende de: US-AU-003
    +──> US-AU-037 (Profile)           ── independiente
    +──> US-AU-038 (Security settings) ── depende de: US-AU-001, 018, 021
    +──> US-AU-039 (Role viewer)       ── depende de: US-AU-008, 012
    +──> US-AU-040 (Admin pages)       ── depende de: US-AU-010, 011
```

---

## Riesgos y Mitigaciones

| # | Riesgo | Probabilidad | Impacto | Mitigacion |
|---|--------|-------------|---------|------------|
| R1 | Cognito tiene limitaciones en MFA custom (email MFA no es nativo) | Alta | Medio | Usar Custom Auth Challenge Lambda triggers para email MFA. Documentar limitaciones. |
| R2 | SAML/OIDC configuracion compleja para clientes empresa | Alta | Medio | Wizard guiado paso a paso. Documentacion detallada. Soporte para metadata URL auto-discovery. Testing con Azure AD, Okta, Google Workspace. |
| R3 | Performance de resolucion de permisos en cada request | Media | Alto | Cache agresivo en memoria (TTL 5 min). Permisos en JWT claims cuando sea posible. Benchmark: < 10ms con cache. |
| R4 | JWT claim size limit (5KB en Cognito) insuficiente para permisos complejos | Media | Medio | Si excede limite: almacenar solo role_id en JWT, resolver permisos via DynamoDB lookup + cache. |
| R5 | Migracion de usuarios existentes a nuevo sistema RBAC | Alta | Alto | Script de migracion que mapea roles actuales a nuevos. Periodo de compatibilidad donde ambos sistemas funcionan en paralelo. Rollback plan. |
| R6 | Device fingerprinting inconsistente entre browsers/updates | Media | Bajo | Fingerprint como factor adicional, no como factor unico. Tolerancia: si 80% de parametros coinciden, se considera mismo device. |
| R7 | SSO provider del cliente tiene downtime → usuarios no pueden acceder | Baja | Alto | Fallback: permitir login con password si SSO-only falla por > 5 minutos (configurable). Notificar admin. |
| R8 | API keys comprometidas por cliente | Media | Alto | Rotacion facil con grace period. Alerta por uso anomalo (spike en requests). Revocacion inmediata disponible. Rate limiting como primera linea de defensa. |
| R9 | GDPR data deletion conflicta con audit trail requerido | Media | Medio | Anonimizar PII pero mantener registro de acciones con IDs hasheados. Documentar que el audit trail se retiene 365 dias por compliance antes de anonimizar. |
| R10 | Cognito cold starts en Lambda triggers aumentan latencia de login | Media | Medio | Provisioned concurrency en Lambdas criticas (Pre-Auth, Post-Auth). Warmer Lambda cada 5 minutos. Target: login < 2 segundos end-to-end. |
