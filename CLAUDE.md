# CLAUDE.md - covacha-projects (Cerebro Central)

## Que es este repo

Este repo es el **CEREBRO CENTRAL** del ecosistema BAAT Digital / SuperPago. Aqui se definen y coordinan TODOS los productos, repos, dependencias, epicas y reglas del ecosistema.

**Contiene:** YAML de configuracion, Markdown de planificacion, scripts de orquestacion, y el sistema de memoria compartida de Agent Teams.

---

## Estructura del Repo

```
covacha-projects/
├── infra/
│   └── create_agent_memory_table.py   # Crea tabla DynamoDB covacha-agent-memory
├── scripts/
│   ├── agent_memory/                  # Sistema de memoria compartida (NUEVO)
│   │   ├── config.py                  # Constantes AWS + GitHub + model mapping
│   │   ├── model_selector.py          # labels → modelo Claude (haiku/sonnet/opus)
│   │   ├── dynamo_client.py           # CRUD DynamoDB + locking atomico
│   │   ├── github_client.py           # GraphQL + gh CLI
│   │   ├── sync_github.py             # GitHub Project Board → DynamoDB
│   │   ├── bootstrap.py               # DynamoDB → CONTEXT.md (inicio de sesion)
│   │   ├── claim_task.py              # CLI: reclamar tarea + lock
│   │   ├── release_task.py            # CLI: liberar tarea + learnings
│   │   ├── team_status.py             # CLI: dashboard de equipos
│   │   └── tests/                     # pytest, 28 tests
│   ├── create-cross-story.sh          # Crea issues CROSS en multiples repos
│   ├── impact-analysis.sh             # Analiza impacto cross-repo
│   ├── priority-matrix.sh             # Matriz de prioridades
│   └── sync-rules.sh                  # Sincroniza rules/ a todos los repos
├── memory/
│   └── MEMORY.md                      # Patrones globales (cargado por Claude Code)
├── products/                          # Definicion de cada producto + epicas
│   ├── superpago/                     # Producto principal (pagos, SPEI, transacciones)
│   │   ├── superpago.yml              # Metadata del producto
│   │   ├── SPEI-PRODUCT-PLAN.md       # EP-SP-001 a EP-SP-010 (52 US)
│   │   ├── SPEI-FRONTEND-EPICS-MULTI-TIER.md # EP-SP-011 a EP-SP-013
│   │   ├── SPEI-EXPANSION-EPICS.md    # EP-SP-014 a EP-SP-020 (33 US)
│   │   ├── BILLPAY-ONBOARDING-EPICS.md # EP-SP-021 a EP-SP-028 (32 US)
│   │   ├── BILLPAY-PRODUCT-PLAN.md    # Plan detallado BillPay
│   │   ├── NOTIFICATIONS-EPICS.md     # EP-SP-029 a EP-SP-030 (14 US)
│   │   └── SUPERPAGO-AI-AGENTS-EPICS.md # EP-SP-031 a EP-SP-040 (55 US)
│   │
│   ├── marketing/                     # Agencia digital, social media, landings
│   │   ├── marketing.yml              # Metadata del producto
│   │   ├── MARKETING-EPICS.md         # EP-MK-006 a EP-MK-013 (38 US)
│   │   └── MARKETING-AI-AGENTS-EPICS.md # EP-MK-014 a EP-MK-023 (55 US)
│   │
│   ├── authentication/                # Autenticacion multi-tenant (P1 critico)
│   │   ├── authentication.yml         # Metadata del producto
│   │   └── AUTHENTICATION-EPICS.md    # EP-AU-001 a EP-AU-008 (45 US)
│   │
│   ├── dashboard/                     # Metricas y reportes
│   │   ├── dashboard.yml              # Metadata del producto
│   │   └── DASHBOARD-EPICS.md         # EP-DB-001 a EP-DB-008 (45 US)
│   │
│   ├── ia/                            # Plataforma IA, bots, agentes
│   │   ├── ia.yml                     # Metadata del producto
│   │   └── IA-BOTS-EPICS.md           # EP-IA-001 a EP-IA-010 (55 US)
│   │
│   ├── alerta-tribunal/               # Alertas judiciales automatizadas
│   │   ├── alerta-tribunal.yml        # Metadata del producto
│   │   └── ALERTA-TRIBUNAL-EPICS.md   # EP-AT-001 a EP-AT-008 (46 US)
│   │
│   ├── crm/                           # CRM independiente
│   │   ├── crm.yml                    # Metadata del producto
│   │   └── CRM-EPICS.md              # EP-CR-001 a EP-CR-008 (48 US)
│   │
│   ├── website/                       # Landing pages y portales publicos
│   │   ├── website.yml                # Metadata del producto
│   │   └── WEBSITE-EPICS.md           # EP-WB-001 a EP-WB-006 (36 US)
│   │
│   └── legacy-mipay/                  # Legacy en migracion
│       ├── legacy-mipay.yml           # Metadata del producto
│       └── LEGACY-MIPAY-MIGRATION-PLAN.md # EP-LM-001 a EP-LM-008 (42 US)
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

1. Lee `products/<producto>/<producto>.yml` para saber que repos involucra
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

### SuperPago (EP-SP-001 a EP-SP-040)

| Archivo | Epicas | User Stories | Estado |
|---------|--------|-------------|--------|
| superpago/SPEI-PRODUCT-PLAN.md | EP-SP-001 a EP-SP-010 | US-SP-001 a US-SP-051 | Planificacion |
| superpago/SPEI-FRONTEND-EPICS-MULTI-TIER.md | EP-SP-011 a EP-SP-013 | (incluidas arriba) | Planificacion |
| superpago/SPEI-EXPANSION-EPICS.md | EP-SP-014 a EP-SP-020 | US-SP-052 a US-SP-084 | Planificacion |
| superpago/BILLPAY-ONBOARDING-EPICS.md | EP-SP-021 a EP-SP-028 | US-SP-085 a US-SP-116 | Planificacion |
| superpago/NOTIFICATIONS-EPICS.md | EP-SP-029 a EP-SP-030 | US-SP-117 a US-SP-130 | Planificacion |
| superpago/SUPERPAGO-AI-AGENTS-EPICS.md | EP-SP-031 a EP-SP-040 | US-SP-131 a US-SP-185 | Planificacion |

**Total SuperPago**: 40 epicas, ~185 user stories

### Marketing (EP-MK-001 a EP-MK-025)

| Archivo | Epicas | User Stories | Estado |
|---------|--------|-------------|--------|
| (GitHub Issues #1-5, #8) | EP-MK-001 a EP-MK-005 | - | Completado |
| marketing/MARKETING-EPICS.md | EP-MK-006 a EP-MK-013 | US-MK-001 a US-MK-038 | Planificacion |
| marketing/MARKETING-AI-AGENTS-EPICS.md | EP-MK-014 a EP-MK-023 | US-MK-039 a US-MK-093 | Planificacion |
| marketing/MARKETING-SOCIAL-REPORTS-EPICS.md | EP-MK-024 | US-MK-094 a US-MK-100 | Planificacion |
| marketing/MARKETING-META-AI-EPICS.md | EP-MK-025 | US-MK-101 a US-MK-107 | Planificacion |

**Total Marketing**: 25 epicas (5 completadas, 20 pendientes), 107 user stories

### Authentication (EP-AU-001 a EP-AU-008)

| Archivo | Epicas | User Stories | Estado |
|---------|--------|-------------|--------|
| authentication/AUTHENTICATION-EPICS.md | EP-AU-001 a EP-AU-008 | US-AU-001 a US-AU-045 | Planificacion |

**Total Authentication**: 8 epicas, 45 user stories

### Dashboard (EP-DB-001 a EP-DB-008)

| Archivo | Epicas | User Stories | Estado |
|---------|--------|-------------|--------|
| dashboard/DASHBOARD-EPICS.md | EP-DB-001 a EP-DB-008 | US-DB-001 a US-DB-045 | Planificacion |

**Total Dashboard**: 8 epicas, 45 user stories

### IA/Bots (EP-IA-001 a EP-IA-010)

| Archivo | Epicas | User Stories | Estado |
|---------|--------|-------------|--------|
| ia/IA-BOTS-EPICS.md | EP-IA-001 a EP-IA-010 | US-IA-001 a US-IA-055 | Planificacion |

**Total IA/Bots**: 10 epicas, 55 user stories

### AlertaTribunal (EP-AT-001 a EP-AT-008)

| Archivo | Epicas | User Stories | Estado |
|---------|--------|-------------|--------|
| alerta-tribunal/ALERTA-TRIBUNAL-EPICS.md | EP-AT-001 a EP-AT-008 | US-AT-001 a US-AT-046 | Planificacion |

**Total AlertaTribunal**: 8 epicas, 46 user stories

### CRM (EP-CR-001 a EP-CR-008)

| Archivo | Epicas | User Stories | Estado |
|---------|--------|-------------|--------|
| crm/CRM-EPICS.md | EP-CR-001 a EP-CR-008 | US-CR-001 a US-CR-048 | Planificacion |

**Total CRM**: 8 epicas, 48 user stories

### Website (EP-WB-001 a EP-WB-006)

| Archivo | Epicas | User Stories | Estado |
|---------|--------|-------------|--------|
| website/WEBSITE-EPICS.md | EP-WB-001 a EP-WB-006 | US-WB-001 a US-WB-036 | Planificacion |

**Total Website**: 6 epicas, 36 user stories

### Legacy MiPay (EP-LM-001 a EP-LM-008)

| Archivo | Epicas | User Stories | Estado |
|---------|--------|-------------|--------|
| legacy-mipay/LEGACY-MIPAY-MIGRATION-PLAN.md | EP-LM-001 a EP-LM-008 | US-LM-001 a US-LM-042 | Migracion |

**Total Legacy MiPay**: 8 epicas, 42 user stories

### Totales del Ecosistema

| Producto | Epicas | User Stories | Prioridad |
|----------|--------|-------------|-----------|
| SuperPago | 40 | ~185 | P1 |
| Authentication | 8 | 45 | P1 |
| Marketing | 25 | 107 | P2 |
| Dashboard | 8 | 45 | P2 |
| IA/Bots | 10 | 55 | P2 |
| AlertaTribunal | 8 | 46 | P2 |
| CRM | 8 | 48 | P3 |
| Website | 6 | 36 | P3 |
| Legacy MiPay | 8 | 42 | P5 |
| **TOTAL** | **121** | **~609** | - |

---

## Convenciones

### IDs

| Tipo | Formato | Ejemplo |
|------|---------|---------|
| Epica SuperPago | EP-SP-XXX | EP-SP-031 |
| Epica Marketing | EP-MK-XXX | EP-MK-014 |
| Epica Authentication | EP-AU-XXX | EP-AU-001 |
| Epica Dashboard | EP-DB-XXX | EP-DB-001 |
| Epica IA/Bots | EP-IA-XXX | EP-IA-001 |
| Epica AlertaTribunal | EP-AT-XXX | EP-AT-001 |
| Epica CRM | EP-CR-XXX | EP-CR-001 |
| Epica Website | EP-WB-XXX | EP-WB-001 |
| Epica Legacy MiPay | EP-LM-XXX | EP-LM-001 |
| User Story SuperPago | US-SP-XXX | US-SP-131 |
| User Story Marketing | US-MK-XXX | US-MK-039 |
| User Story Authentication | US-AU-XXX | US-AU-001 |
| User Story Dashboard | US-DB-XXX | US-DB-001 |
| User Story IA/Bots | US-IA-XXX | US-IA-001 |
| User Story AlertaTribunal | US-AT-XXX | US-AT-001 |
| User Story CRM | US-CR-XXX | US-CR-001 |
| User Story Website | US-WB-XXX | US-WB-001 |
| User Story Legacy MiPay | US-LM-XXX | US-LM-001 |
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

## Sistema de Memoria Compartida (Agent Teams)

### Flujo obligatorio al iniciar una sesion

```bash
cd /Users/casp/sandboxes/superpago/covacha-projects

# 1. Bootstrap: genera CONTEXT.md con contexto fresco de DynamoDB + GitHub
python scripts/agent_memory/bootstrap.py --team backend --machine mac-1 --module covacha-payment

# 2. Reclamar tarea (lock atomico + mueve board a In Progress)
python scripts/agent_memory/claim_task.py --task 043 --team backend --machine mac-1

# 3. Implementar (leer CONTEXT.md + MEMORY.md generados)

# 4. Liberar tarea + guardar learnings
python scripts/agent_memory/release_task.py \
  --task 043 --team backend --machine mac-1 \
  --status done --learning "usar decimal.Decimal para montos, no float"

# 5. Ver estado del equipo en cualquier momento
python scripts/agent_memory/team_status.py --label backend
```

### Seleccion de modelo por tipo de tarea

| Labels del issue | Modelo recomendado | Uso |
| --- | --- | --- |
| research, docs, sync, chore | **haiku** | ~40% de tareas |
| feature, bugfix, backend, frontend | **sonnet** | ~55% de tareas |
| architecture, epic, cross-repo | **opus** | ~5% de tareas |

El modelo recomendado aparece en el CONTEXT.md generado por bootstrap.py.

### Como usar en Agent Teams (Task tool)

```python
# El Lead lee CONTEXT.md para saber el modelo de cada teammate
Task(
    subagent_type="backend-architect",
    model="sonnet",   # leer de recommended_model en CONTEXT.md
    prompt="Implementa ISS-043. Lee CONTEXT.md en covacha-payment/ primero."
)

# Operaciones del sistema siempre usan haiku (barato)
Task(subagent_type="Explore", model="haiku", prompt="Busca archivos X")
```

### Setup y operaciones

- **Tabla DynamoDB:** `covacha-agent-memory` (us-east-1, PAY_PER_REQUEST)
- **Cron sync:** `.github/workflows/agent_memory_sync.yml` (cada 15min)
- **Setup inicial:** `python infra/create_agent_memory_table.py`
- **Tests:** `cd scripts/agent_memory && pytest tests/ -v` (28 tests)

---

## Boards

- [SuperPago Board](https://github.com/orgs/baatdigital/projects/1)
- [Master Board](https://github.com/orgs/baatdigital/projects/2)
