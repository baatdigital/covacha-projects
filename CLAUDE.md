# CLAUDE.md - covacha-projects (Cerebro Central)

## Que es este repo

Este repo es el **CEREBRO CENTRAL** del ecosistema BAAT Digital / SuperPago. Aqui se definen y coordinan TODOS los productos, repos, dependencias, epicas y reglas del ecosistema.

**NO contiene codigo ejecutable.** Solo YAML de configuracion, Markdown de planificacion, y scripts de orquestacion.

---

## Estructura del Repo

```
covacha-projects/
├── products/              # Definicion de cada producto + epicas
│   ├── superpago.yml      # Producto principal (pagos, SPEI, transacciones)
│   ├── marketing.yml      # Agencia digital, social media, landings
│   ├── dashboard.yml      # Metricas y reportes
│   ├── ia.yml             # Bots e inteligencia artificial
│   ├── crm.yml            # CRM independiente
│   ├── authentication.yml # Autenticacion multi-tenant
│   ├── website.yml        # Sitios web publicos
│   ├── alerta-tribunal.yml # Alertas legales
│   ├── legacy-mipay.yml   # Legacy en migracion
│   ├── SPEI-PRODUCT-PLAN.md           # EP-SP-001 a EP-SP-010 (52 US)
│   ├── SPEI-FRONTEND-EPICS-MULTI-TIER.md # EP-SP-011 a EP-SP-013
│   ├── SPEI-EXPANSION-EPICS.md        # EP-SP-014 a EP-SP-020 (33 US)
│   ├── BILLPAY-ONBOARDING-EPICS.md    # EP-SP-021 a EP-SP-028
│   ├── BILLPAY-PRODUCT-PLAN.md        # Plan detallado BillPay
│   ├── NOTIFICATIONS-EPICS.md         # EP-SP-029 a EP-SP-030
│   └── MARKETING-EPICS.md             # EP-MK-006 a EP-MK-013 (38 US)
│
├── repos/                 # Metadata de cada repositorio
│   ├── covacha-core.yml   # Backend principal
│   ├── covacha-payment.yml
│   ├── covacha-botia.yml
│   ├── covacha-transaction.yml
│   ├── covacha-notification.yml
│   ├── covacha-webhook.yml
│   ├── covacha-inventory.yml
│   ├── covacha-judicial.yml
│   ├── covacha-crm.yml
│   ├── covacha-libs.yml
│   ├── mf-core.yml        # Shell principal (Angular 21)
│   ├── mf-auth.yml
│   ├── mf-dashboard.yml
│   ├── mf-ia.yml
│   ├── mf-inventory.yml
│   ├── mf-marketing.yml
│   ├── mf-payment.yml
│   ├── mf-payment-card.yml
│   ├── mf-settings.yml
│   ├── mf-whatsapp.yml
│   └── mf-docs.yml
│
├── dependencies/          # Grafo de dependencias
│   ├── dependency-graph.yml    # Quien depende de quien
│   ├── breaking-changes.yml    # Cambios que rompen
│   └── shared-code-map.yml     # Codigo compartido
│
├── rules/                 # Reglas compartidas (fuente de verdad)
│   ├── testing-rules.yml       # Testing: pytest, Karma, Playwright
│   ├── branch-rules.yml        # Git: develop -> main (auto-promote)
│   ├── naming-conventions.yml  # Naming: repos, archivos, commits
│   └── story-template.yml      # Template de user stories
│
├── cross-repo/            # Features que tocan multiples repos
│   ├── active/            # Features en progreso
│   └── completed/         # Features completados
│
└── scripts/               # Automatizacion
    ├── sync-rules.sh           # Pushea rules/ a todos los repos
    ├── impact-analysis.sh      # Analiza impacto de un cambio
    ├── priority-matrix.sh      # Matriz de prioridades
    └── create-cross-story.sh   # Crea issue CROSS en multiples repos
```

---

## Ecosistema Completo

### Numeros Clave

- **31 repos** en la organizacion baatdigital
- **9 productos** activos
- **10 backends** (Python 3.9+, Flask, DynamoDB)
- **11 micro-frontends** (Angular 21, Native Federation)
- **1 Shell** (mf-core) que orquesta todos los MFs

### Productos y sus Repos

| Producto | Backend(s) | Frontend(s) | Estado |
|----------|------------|-------------|--------|
| **SuperPago** | covacha-core, covacha-payment, covacha-transaction, covacha-notification, covacha-webhook | mf-core (shell), mf-payment, mf-payment-card, mf-settings | Activo |
| **Marketing** | covacha-core | mf-marketing | Activo |
| **Dashboard** | covacha-core, covacha-transaction | mf-dashboard | Activo |
| **IA/Bots** | covacha-botia | mf-ia, mf-whatsapp | Activo |
| **Inventario** | covacha-inventory | mf-inventory | Activo |
| **Auth** | covacha-core (Cognito) | mf-auth | Activo |
| **CRM** | covacha-crm | - | Activo |
| **AlertaTribunal** | covacha-judicial | - | Activo |
| **Legacy MiPay** | mipay_service, mipay_payment | mipay_web | Migracion |

### Infraestructura

| Servicio | Proveedor | Uso |
|----------|-----------|-----|
| Compute | EC2 (VPC privada) | Backends Flask |
| CDN | CloudFront + S3 | Micro-frontends |
| API Gateway | AWS API GW + WAF | Routing + seguridad |
| Auth | Cognito | Autenticacion multi-tenant |
| Database | DynamoDB | Single-table design |
| Queue | SQS | Eventos async |
| Storage | S3 + Google Drive | Media hibrido |
| CI/CD | GitHub Actions | Build + deploy |
| Monitoring | Grafana | grafana.superpago.com.mx |

### URLs de Produccion

| URL | Servicio |
|-----|----------|
| api.superpago.com.mx | Backend APIs (todos los servicios) |
| app.superpago.com.mx | Shell + micro-frontends |
| app.baatdigital.com.mx | Tenant BaatDigital |
| portal-api.superpago.com.mx | B2C payments API |
| webhook.superpago.com.mx | WhatsApp webhooks |
| mf.superpago.com.mx | CDN micro-frontends |
| grafana.superpago.com.mx | Monitoring |

---

## Como Usar Este Repo

### Antes de crear una historia de usuario

1. Lee `products/<producto>.yml` para saber que repos involucra
2. Lee `dependencies/dependency-graph.yml` para entender el impacto
3. Si el feature toca >1 repo, crea un issue CROSS aqui primero
4. Luego crea issues individuales en cada repo, referenciando el CROSS
5. Consulta `rules/story-template.yml` para el formato correcto

### Antes de modificar un repo

1. Busca el repo en `repos/<nombre>.yml`
2. Revisa `depends_on` y `consumed_by`
3. Si tocas un archivo en `breaking_patterns`, verifica consumidores
4. Ejecuta `scripts/impact-analysis.sh <repo> <archivo>` si hay duda

### Para sincronizar reglas

```bash
./scripts/sync-rules.sh  # Pushea rules/ a todos los repos
```

### Para analizar impacto

```bash
./scripts/impact-analysis.sh <repo> <archivo>  # Muestra que repos afecta
```

### Para crear feature cross-repo

```bash
./scripts/create-cross-story.sh  # Crea issue CROSS en multiples repos
```

---

## Mapa de Epicas por Producto

### SuperPago (EP-SP-001 a EP-SP-030)

| Archivo | Epicas | User Stories | Estado |
|---------|--------|-------------|--------|
| SPEI-PRODUCT-PLAN.md | EP-SP-001 a EP-SP-010 | US-SP-001 a US-SP-051 | Planificacion |
| SPEI-FRONTEND-EPICS-MULTI-TIER.md | EP-SP-011 a EP-SP-013 | (incluidas arriba) | Planificacion |
| SPEI-EXPANSION-EPICS.md | EP-SP-014 a EP-SP-020 | US-SP-052 a US-SP-084 | Planificacion |
| BILLPAY-ONBOARDING-EPICS.md | EP-SP-021 a EP-SP-028 | US-SP-085 a US-SP-116 | Planificacion |
| NOTIFICATIONS-EPICS.md | EP-SP-029 a EP-SP-030 | US-SP-117+ | Planificacion |

**Total SuperPago**: 30 epicas, ~130 user stories

### Marketing (EP-MK-001 a EP-MK-013)

| Archivo | Epicas | User Stories | Estado |
|---------|--------|-------------|--------|
| (GitHub Issues #1-5, #8) | EP-MK-001 a EP-MK-005 | - | Completado |
| MARKETING-EPICS.md | EP-MK-006 a EP-MK-013 | US-MK-001 a US-MK-038 | Planificacion |

**Total Marketing**: 13 epicas (5 completadas, 8 pendientes), 38 user stories pendientes

---

## Convenciones

### IDs

| Tipo | Formato | Ejemplo |
|------|---------|---------|
| Epica SuperPago | EP-SP-XXX | EP-SP-014 |
| Epica Marketing | EP-MK-XXX | EP-MK-006 |
| User Story SuperPago | US-SP-XXX | US-SP-052 |
| User Story Marketing | US-MK-XXX | US-MK-001 |
| Feature cross-repo | CROSS-XXX | CROSS-001 |
| Issue individual | ISS-XXX | ISS-042 |

### Repos

- Backend: `covacha-<servicio>` (ej: covacha-core, covacha-payment)
- Frontend MF: `mf-<modulo>` (ej: mf-marketing, mf-core)
- Shared: `covacha-libs`

### Git

- Branches: `feature/<desc>`, `bugfix/<desc>`, `hotfix/<desc>`
- Commits: `tipo: descripcion en espanol`
- Tipos: feat, fix, refactor, test, docs, ci, chore
- Flow: feature/* -> develop -> main (auto-promote via GitHub Actions)
- **NUNCA push directo a main**

### Testing

| Stack | Framework | Coverage Min | E2E |
|-------|-----------|-------------|-----|
| Backend (Python) | pytest | 80% | N/A |
| Frontend (Angular) | Karma + Jasmine | 80% | Playwright |
| Excepciones | mf-payment*: Jest | 80% | Playwright |

### Naming

- Python: snake_case (archivos, funciones, variables)
- TypeScript: kebab-case (archivos), PascalCase (clases), camelCase (variables)
- Angular: standalone components, OnPush, Signals
- Tests: `test_debe_<accion>_cuando_<condicion>` (Python), `should <action> when <condition>` (TS)

---

## Multi-Tenancy

El ecosistema soporta multiples marcas/dominios:

| Tenant | Dominio | Descripcion |
|--------|---------|-------------|
| SuperPago | superpago.com.mx, app.superpago.com.mx | Plataforma principal de pagos |
| BaatDigital | baatdigital.com.mx, app.baatdigital.com.mx | Agencia digital |
| AlertaTribunal | alertatribunal.com, app.alertatribunal.com | Alertas legales |
| Development | localhost | Desarrollo local |

Jerarquia: **Tenant > Organization > Project > Recursos**

Estado compartido via localStorage con prefijo `covacha:` + BroadcastChannel para sync entre pestanas.

---

## Deploy

### Frontend

```
GitHub push (develop) -> GitHub Actions -> build Angular -> S3 -> CloudFront
```

- Cache: assets hasheados 1 ano immutable, remoteEntry.json 5 min, index.html no-cache
- Cada MF tiene su distribution de CloudFront

### Backend

```
GitHub push (develop) -> GitHub Actions -> build -> CodeDeploy -> EC2
```

- EC2 en VPC privada detras de ALBs internos
- API Gateway + WAF como entry point (limite ~8KB body)
- Variables de entorno en Parameter Store

### Flujo CI/CD

```
feature/* -> push -> CI (tests + coverage)
  -> PR automatico si coverage >= 98%
    -> merge a develop
      -> Action promote.yml auto-promueve a main
        -> deploy a AWS
```

---

## Coordinacion de Agentes IA

### Herramientas

| Agente | Uso | Cuando |
|--------|-----|--------|
| **Claude Code** | Terminal, multi-archivo, cross-repo | 3+ archivos, terminal, orquestacion |
| **Cursor Agent** | Editor inline, autocompletado | 1-2 archivos, contexto visual |
| **Copilot** | Review de PRs, sugerencias | Code review automatizado |

### Regla de Oro

> **1-2 archivos sin terminal** -> Cursor Agent
> **3+ archivos, terminal, o cross-repo** -> Claude Code
> **Ambiguo** -> Claude Code planifica, Cursor ejecuta lo puntual

### Maquinas

- **Mac-1**: frontend-heavy
- **Mac-2**: backend-heavy
- Labels en issues: `mac-1`, `mac-2` para evitar colisiones

---

## Boards

- [SuperPago Board](https://github.com/orgs/baatdigital/projects/1)
- [Master Board](https://github.com/orgs/baatdigital/projects/2)
